from __future__ import annotations

from dataclasses import dataclass, field
from importlib import import_module
from importlib.util import find_spec

from vision_platform.libraries.roi_core import roi_bounds
from vision_platform.libraries.common_models import FocusPreviewState, RoiDefinition
from vision_platform.models import CapturedFrame
from vision_platform.services.display_service import (
    CoordinateExportService,
    DisplayGeometryService,
    PreviewInteractionCommand,
    PreviewInteractionOutcome,
    PreviewInteractionService,
    PreviewInteractionState,
    PreviewOverlayModel,
    PreviewStatusModelService,
    ViewportMapping,
    ZoomPanState,
)
from vision_platform.services.stream_service import RoiStateService


@dataclass(frozen=True, slots=True)
class RenderedViewportImage:
    width: int
    height: int
    mime_family: str
    payload: bytes

    def to_pnm_bytes(self) -> bytes:
        magic = b"P5" if self.mime_family == "pgm" else b"P6"
        header = magic + b"\n" + f"{self.width} {self.height}\n255\n".encode("ascii")
        return header + self.payload

    def to_rgb_bytes(self) -> bytes:
        if self.mime_family == "ppm":
            return self.payload
        return bytes(self.to_rgb_buffer())

    def to_rgb_buffer(self) -> bytearray:
        if self.mime_family == "ppm":
            return bytearray(self.payload)
        if _is_numpy_available():
            numpy_module = _require_numpy()
            values = numpy_module.frombuffer(self.payload, dtype=numpy_module.uint8)
            return bytearray(numpy_module.repeat(values, 3).tobytes())
        rgb_payload = bytearray(self.width * self.height * 3)
        target_index = 0
        for value in self.payload:
            rgb_payload[target_index : target_index + 3] = bytes((value, value, value))
            target_index += 3
        return rgb_payload


@dataclass(frozen=True, slots=True)
class PreviewShellViewModel:
    image: RenderedViewportImage
    overlay_model: PreviewOverlayModel
    status_lines: list[str]
    viewport_mapping: ViewportMapping


@dataclass(slots=True)
class PreviewShellState:
    geometry_state: ZoomPanState = field(default_factory=ZoomPanState)
    interaction_state: PreviewInteractionState = field(default_factory=PreviewInteractionState)
    last_display_scale: float = 1.0
    last_viewport_mapping: ViewportMapping | None = None


class PreviewShellPresenter:
    """UI-agnostic preview-shell adapter over shared geometry, interaction, and status services."""

    def __init__(
        self,
        *,
        coordinate_export_service: CoordinateExportService | None = None,
        geometry_service: DisplayGeometryService | None = None,
        interaction_service: PreviewInteractionService | None = None,
        status_model_service: PreviewStatusModelService | None = None,
        roi_state_service: RoiStateService | None = None,
        zoom_step: float = 2.0,
        min_zoom_scale: float = 0.25,
        max_zoom_scale: float = 4.0,
    ) -> None:
        self._coordinate_export_service = coordinate_export_service or CoordinateExportService()
        self._geometry_service = geometry_service or DisplayGeometryService()
        self._interaction_service = interaction_service or PreviewInteractionService(self._geometry_service)
        self._status_model_service = status_model_service or PreviewStatusModelService()
        self._roi_state_service = roi_state_service or RoiStateService()
        self._zoom_step = zoom_step
        self._min_zoom_scale = min_zoom_scale
        self._max_zoom_scale = max_zoom_scale
        self._state = PreviewShellState()

    @property
    def state(self) -> PreviewShellState:
        return self._state

    def build_view(
        self,
        frame: CapturedFrame,
        *,
        viewport_width: int,
        viewport_height: int,
        focus_state: FocusPreviewState | None = None,
        warning: str | None = None,
        has_focus_toggle: bool = False,
    ) -> PreviewShellViewModel:
        display_scale = self._geometry_service.resolve_display_scale(
            frame.width,
            frame.height,
            viewport_width,
            viewport_height,
            self._state.geometry_state,
            min_zoom_scale=self._min_zoom_scale,
        )
        self._state.last_display_scale = display_scale
        viewport_origin = self._geometry_service.resolve_viewport_origin(
            frame.width,
            frame.height,
            viewport_width,
            viewport_height,
            display_scale,
            self._state.geometry_state,
        )
        mapping = self._geometry_service.build_viewport_mapping(
            frame.width,
            frame.height,
            viewport_width,
            viewport_height,
            display_scale,
            src_x=viewport_origin[0],
            src_y=viewport_origin[1],
        )
        self._state.last_viewport_mapping = mapping
        selected_point = self._state.interaction_state.selected_point
        crosshair_point = selected_point or self._state.interaction_state.last_cursor_source_point
        selected_point_text = None
        if selected_point is not None:
            selected_point_text = self._coordinate_export_service.format_point(*selected_point)
        active_roi = self._roi_state_service.get_active_roi()
        focus_anchor_point = self._resolve_focus_anchor_point(
            frame=frame,
            active_roi=active_roi,
            focus_state=focus_state,
        )
        status_model = self._status_model_service.build_status_model(
            fit_to_window=self._state.geometry_state.fit_to_window,
            display_scale=display_scale,
            viewport_origin_scaled=self._state.geometry_state.viewport_origin_scaled,
            fps=None,
            selected_point=selected_point,
            selected_point_text=selected_point_text,
            warning=warning,
            transient_message=self._state.interaction_state.last_status_message,
            has_focus_provider=has_focus_toggle,
            focus_status_visible=self._state.interaction_state.focus_status_visible,
            focus_state=focus_state,
            roi_mode=self._state.interaction_state.roi_mode,
            roi_anchor_point=self._state.interaction_state.roi_anchor_point,
            roi_preview_point=self._state.interaction_state.roi_preview_point,
            active_roi=active_roi,
            has_snapshot_shortcut=False,
            has_focus_toggle=has_focus_toggle,
        )
        overlay_model = self._status_model_service.build_overlay_model(
            crosshair_visible=self._state.interaction_state.crosshair_visible,
            selected_point=crosshair_point,
            draft_roi=self._build_draft_roi(),
            active_roi=active_roi,
            focus_status_visible=self._state.interaction_state.focus_status_visible,
            focus_state=focus_state,
            focus_anchor_point=focus_anchor_point,
            show_viewport_outline=self._should_draw_viewport_outline(mapping),
        )
        return PreviewShellViewModel(
            image=render_viewport_image(frame, mapping),
            overlay_model=overlay_model,
            status_lines=self._format_status_lines(status_model),
            viewport_mapping=mapping,
        )

    def apply_command(
        self,
        command: PreviewInteractionCommand,
        *,
        has_focus_provider: bool = False,
    ) -> PreviewInteractionOutcome:
        outcome = self._interaction_service.apply_command(
            command,
            self._state.interaction_state,
            self._state.geometry_state,
            last_display_scale=self._state.last_display_scale,
            last_viewport_mapping=self._state.last_viewport_mapping,
            zoom_step=self._zoom_step,
            min_zoom_scale=self._min_zoom_scale,
            max_zoom_scale=self._max_zoom_scale,
            has_focus_provider=has_focus_provider,
            has_snapshot_callback=False,
            coordinate_formatter=self._coordinate_export_service.format_point,
            roi_builder=self._build_roi_definition,
        )
        if outcome.committed_roi is not None:
            self._roi_state_service.set_active_roi(outcome.committed_roi)
        return outcome

    def handle_canvas_click(self, x: int, y: int) -> PreviewInteractionOutcome:
        self.apply_command(
            PreviewInteractionCommand(action="cursor_moved", viewport_point=(x, y)),
        )
        source_point = self._geometry_service.map_viewport_point_to_source(self._state.last_viewport_mapping, x, y)
        return self.apply_command(
            PreviewInteractionCommand(action="select_source_point", source_point=source_point),
        )

    def handle_mouse_wheel(self, x: int, y: int, wheel_delta: int) -> PreviewInteractionOutcome:
        self.apply_command(
            PreviewInteractionCommand(action="cursor_moved", viewport_point=(x, y)),
        )
        source_point = self._geometry_service.map_viewport_point_to_source(self._state.last_viewport_mapping, x, y)
        return self.apply_command(
            PreviewInteractionCommand(action="wheel_zoom", source_point=source_point, wheel_delta=wheel_delta),
        )

    def handle_pan_start(self, x: int, y: int) -> PreviewInteractionOutcome:
        return self.apply_command(PreviewInteractionCommand(action="start_pan", viewport_point=(x, y)))

    def handle_pan_move(self, x: int, y: int) -> PreviewInteractionOutcome:
        self.apply_command(
            PreviewInteractionCommand(action="cursor_moved", viewport_point=(x, y)),
        )
        return self.apply_command(PreviewInteractionCommand(action="update_pan", viewport_point=(x, y)))

    def handle_pan_stop(self) -> PreviewInteractionOutcome:
        return self.apply_command(PreviewInteractionCommand(action="stop_pan"))

    def handle_pointer_move(self, x: int, y: int) -> None:
        source_point = self._geometry_service.map_viewport_point_to_source(self._state.last_viewport_mapping, x, y)
        self.apply_command(
            PreviewInteractionCommand(action="cursor_moved", viewport_point=(x, y), source_point=source_point),
        )
        if self._state.interaction_state.roi_anchor_point is None:
            return
        self._state.interaction_state.roi_preview_point = source_point

    def _build_draft_roi(self) -> RoiDefinition | None:
        roi_mode = self._state.interaction_state.roi_mode
        anchor = self._state.interaction_state.roi_anchor_point
        preview = self._state.interaction_state.roi_preview_point
        if roi_mode is None or anchor is None or preview is None:
            return None
        return self._build_roi_definition(roi_mode, anchor, preview)

    @staticmethod
    def _resolve_focus_anchor_point(
        *,
        frame: CapturedFrame,
        active_roi: RoiDefinition | None,
        focus_state: FocusPreviewState | None,
    ) -> tuple[int, int] | None:
        if focus_state is not None:
            return (
                int(round(focus_state.overlay.anchor_x)),
                int(round(focus_state.overlay.anchor_y)),
            )
        if active_roi is not None:
            bounds = roi_bounds(active_roi)
            if bounds is not None:
                return (
                    int(round((bounds[0] + bounds[2]) / 2.0)),
                    int(round((bounds[1] + bounds[3]) / 2.0)),
                )
        return (frame.width // 2, frame.height // 2)

    @staticmethod
    def _should_draw_viewport_outline(mapping: ViewportMapping) -> bool:
        return not (mapping.copy_width >= mapping.viewport_width and mapping.copy_height >= mapping.viewport_height)

    def _build_roi_definition(
        self,
        roi_mode: str | None,
        anchor_point: tuple[int, int],
        selected_point: tuple[int, int],
    ) -> RoiDefinition:
        if roi_mode == "ellipse":
            radius_x = abs(selected_point[0] - anchor_point[0])
            radius_y = abs(selected_point[1] - anchor_point[1])
            points = (
                (anchor_point[0] - radius_x, anchor_point[1] - radius_y),
                (anchor_point[0] + radius_x, anchor_point[1] + radius_y),
            )
            return RoiDefinition(roi_id="shell-roi", shape="ellipse", points=points)
        return RoiDefinition(roi_id="shell-roi", shape="rectangle", points=(anchor_point, selected_point))

    def _format_status_lines(self, status_model) -> list[str]:
        lines = [" | ".join(entry.value for entry in status_model.primary_line.entries)]
        if status_model.roi_status is not None:
            lines.append(self._format_roi_status(status_model.roi_status))
        if status_model.focus_status is not None and status_model.focus_status.state != "hidden":
            lines.append(self._format_focus_status(status_model.focus_status))
        lines.append(" ".join(f"{item.key}={item.action}" for item in status_model.shortcuts))
        return [line for line in lines if line]

    def _format_roi_status(self, roi_status) -> str:
        if roi_status.state == "active":
            return f"ROI active: {roi_status.active_shape}"
        if roi_status.state == "mode_active":
            if roi_status.roi_mode == "rectangle":
                return "ROI mode: rectangle (entry point active)"
            if roi_status.roi_mode == "ellipse":
                return "ROI mode: ellipse (entry point active)"
            return f"ROI mode: {roi_status.roi_mode}"
        anchor_text = self._coordinate_export_service.format_point(*roi_status.anchor_point)
        base = f"ROI mode: {roi_status.roi_mode} anchor={anchor_text}"
        if roi_status.preview_point is None:
            return base
        preview_text = self._coordinate_export_service.format_point(*roi_status.preview_point)
        return f"{base} preview={preview_text}"

    @staticmethod
    def _format_focus_status(focus_status) -> str:
        if focus_status.state == "waiting":
            return "Focus: waiting"
        if focus_status.state == "invalid":
            return f"Focus: invalid ({focus_status.metric_name})"
        return f"Focus: {focus_status.metric_name}={focus_status.score:.2f}"


def render_viewport_image(frame: CapturedFrame, mapping: ViewportMapping) -> RenderedViewportImage:
    pixel_format = (frame.pixel_format or "Mono8").lower()
    source_bytes = frame.get_buffer_bytes()
    if pixel_format == "mono8":
        return RenderedViewportImage(
            width=mapping.viewport_width,
            height=mapping.viewport_height,
            mime_family="pgm",
            payload=_render_mono8_payload(
                source_bytes,
                source_width=frame.width,
                source_height=frame.height,
                mapping=mapping,
            ),
        )
    if pixel_format == "mono16":
        mono8_bytes = _convert_mono16_to_mono8(source_bytes, frame.width, frame.height)
        return RenderedViewportImage(
            width=mapping.viewport_width,
            height=mapping.viewport_height,
            mime_family="pgm",
            payload=_render_mono8_payload(
                mono8_bytes,
                source_width=frame.width,
                source_height=frame.height,
                mapping=mapping,
            ),
        )
    if pixel_format in {"rgb8", "bgr8"}:
        return RenderedViewportImage(
            width=mapping.viewport_width,
            height=mapping.viewport_height,
            mime_family="ppm",
            payload=_render_rgb_payload(
                source_bytes,
                source_width=frame.width,
                source_height=frame.height,
                mapping=mapping,
                source_format=pixel_format,
            ),
        )
    raise RuntimeError(f"Unsupported pixel format '{frame.pixel_format}' for local shell rendering.")


def _render_mono8_payload(
    source_bytes: bytes,
    *,
    source_width: int,
    source_height: int,
    mapping: ViewportMapping,
) -> bytes:
    if _is_numpy_available():
        return _render_mono8_payload_numpy(
            source_bytes,
            source_width=source_width,
            source_height=source_height,
            mapping=mapping,
        )
    payload = bytearray(mapping.viewport_width * mapping.viewport_height)
    for viewport_y in range(mapping.copy_height):
        for viewport_x in range(mapping.copy_width):
            scaled_x = mapping.src_x + viewport_x
            scaled_y = mapping.src_y + viewport_y
            source_x = min(max(int(scaled_x / mapping.display_scale), 0), source_width - 1)
            source_y = min(max(int(scaled_y / mapping.display_scale), 0), source_height - 1)
            payload[(mapping.dst_y + viewport_y) * mapping.viewport_width + mapping.dst_x + viewport_x] = source_bytes[
                source_y * source_width + source_x
            ]
    return bytes(payload)


def _render_rgb_payload(
    source_bytes: bytes,
    *,
    source_width: int,
    source_height: int,
    mapping: ViewportMapping,
    source_format: str,
) -> bytes:
    if _is_numpy_available():
        return _render_rgb_payload_numpy(
            source_bytes,
            source_width=source_width,
            source_height=source_height,
            mapping=mapping,
            source_format=source_format,
        )
    payload = bytearray(mapping.viewport_width * mapping.viewport_height * 3)
    for viewport_y in range(mapping.copy_height):
        for viewport_x in range(mapping.copy_width):
            scaled_x = mapping.src_x + viewport_x
            scaled_y = mapping.src_y + viewport_y
            source_x = min(max(int(scaled_x / mapping.display_scale), 0), source_width - 1)
            source_y = min(max(int(scaled_y / mapping.display_scale), 0), source_height - 1)
            source_index = (source_y * source_width + source_x) * 3
            target_index = ((mapping.dst_y + viewport_y) * mapping.viewport_width + mapping.dst_x + viewport_x) * 3
            pixel = source_bytes[source_index : source_index + 3]
            if source_format == "bgr8":
                payload[target_index : target_index + 3] = bytes((pixel[2], pixel[1], pixel[0]))
            else:
                payload[target_index : target_index + 3] = pixel
    return bytes(payload)


def _render_mono8_payload_numpy(
    source_bytes: bytes,
    *,
    source_width: int,
    source_height: int,
    mapping: ViewportMapping,
) -> bytes:
    numpy_module = _require_numpy()
    expected_size = source_width * source_height
    if len(source_bytes) < expected_size:
        raise RuntimeError("Frame buffer is too small for Mono8 viewport rendering.")

    source_image = numpy_module.frombuffer(source_bytes, dtype=numpy_module.uint8, count=expected_size).reshape(
        (source_height, source_width)
    )
    source_x, source_y = _build_source_indices_numpy(mapping, source_width, source_height, numpy_module)
    sampled = source_image[source_y[:, None], source_x[None, :]]

    viewport = numpy_module.zeros((mapping.viewport_height, mapping.viewport_width), dtype=numpy_module.uint8)
    viewport[
        mapping.dst_y : mapping.dst_y + mapping.copy_height,
        mapping.dst_x : mapping.dst_x + mapping.copy_width,
    ] = sampled
    return viewport.tobytes()


def _render_rgb_payload_numpy(
    source_bytes: bytes,
    *,
    source_width: int,
    source_height: int,
    mapping: ViewportMapping,
    source_format: str,
) -> bytes:
    numpy_module = _require_numpy()
    expected_size = source_width * source_height * 3
    if len(source_bytes) < expected_size:
        raise RuntimeError("Frame buffer is too small for RGB viewport rendering.")

    source_image = numpy_module.frombuffer(source_bytes, dtype=numpy_module.uint8, count=expected_size).reshape(
        (source_height, source_width, 3)
    )
    source_x, source_y = _build_source_indices_numpy(mapping, source_width, source_height, numpy_module)
    sampled = source_image[source_y[:, None], source_x[None, :]]
    if source_format == "bgr8":
        sampled = sampled[:, :, ::-1]

    viewport = numpy_module.zeros((mapping.viewport_height, mapping.viewport_width, 3), dtype=numpy_module.uint8)
    viewport[
        mapping.dst_y : mapping.dst_y + mapping.copy_height,
        mapping.dst_x : mapping.dst_x + mapping.copy_width,
        :,
    ] = sampled
    return viewport.tobytes()


def _build_source_indices_numpy(mapping: ViewportMapping, source_width: int, source_height: int, numpy_module):
    x_scaled = mapping.src_x + numpy_module.arange(mapping.copy_width)
    y_scaled = mapping.src_y + numpy_module.arange(mapping.copy_height)
    x_source = numpy_module.clip((x_scaled / mapping.display_scale).astype(numpy_module.int32), 0, source_width - 1)
    y_source = numpy_module.clip((y_scaled / mapping.display_scale).astype(numpy_module.int32), 0, source_height - 1)
    return x_source, y_source


_NUMPY_MODULE = None
_HAS_NUMPY = find_spec("numpy") is not None


def _is_numpy_available() -> bool:
    return _HAS_NUMPY


def _require_numpy():
    global _NUMPY_MODULE
    if _NUMPY_MODULE is None:
        _NUMPY_MODULE = import_module("numpy")
    return _NUMPY_MODULE


def _convert_mono16_to_mono8(source_bytes: bytes, width: int, height: int) -> bytes:
    expected_size = width * height * 2
    if len(source_bytes) < expected_size:
        raise RuntimeError("Frame buffer is too small for Mono16 viewport rendering.")
    if _is_numpy_available():
        numpy_module = _require_numpy()
        values = numpy_module.frombuffer(source_bytes, dtype=numpy_module.uint16, count=width * height)
        return (values >> 8).astype(numpy_module.uint8).tobytes()
    return source_bytes[1:expected_size:2]


__all__ = [
    "PreviewShellPresenter",
    "PreviewShellState",
    "PreviewShellViewModel",
    "RenderedViewportImage",
    "render_viewport_image",
]
