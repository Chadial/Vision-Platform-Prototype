from __future__ import annotations

from dataclasses import dataclass
import subprocess
from typing import Callable

from vision_platform.imaging.opencv_adapter import OpenCvFrameAdapter
from vision_platform.libraries.common_models import FocusPreviewState
from vision_platform.services.display_service import CoordinateExportService
from vision_platform.services.stream_service.preview_service import PreviewService


@dataclass(frozen=True, slots=True)
class _ViewportMapping:
    source_width: int
    source_height: int
    viewport_width: int
    viewport_height: int
    display_scale: float
    scaled_width: int
    scaled_height: int
    src_x: int
    src_y: int
    dst_x: int
    dst_y: int
    copy_width: int
    copy_height: int


class OpenCvPreviewWindow:
    """Optional OpenCV-backed preview window on top of PreviewService."""

    _STATUS_LINE_HEIGHT = 24
    _STATUS_PADDING = 8

    def __init__(
        self,
        preview_service: PreviewService,
        window_name: str = "Camera Preview",
        frame_adapter: OpenCvFrameAdapter | None = None,
        status_warning_provider: Callable[[], str | None] | None = None,
        focus_state_provider: Callable[[], FocusPreviewState | None] | None = None,
        clipboard_copy_callback: Callable[[str], None] | None = None,
        coordinate_export_service: CoordinateExportService | None = None,
        zoom_step: float = 1.5,
        min_zoom_scale: float = 0.05,
        max_zoom_scale: float = 8.0,
    ) -> None:
        self._preview_service = preview_service
        self._window_name = window_name
        self._frame_adapter = frame_adapter or OpenCvFrameAdapter()
        self._status_warning_provider = status_warning_provider
        self._focus_state_provider = focus_state_provider
        self._clipboard_copy_callback = clipboard_copy_callback or self._copy_text_to_clipboard
        self._coordinate_export_service = coordinate_export_service or CoordinateExportService()
        self._zoom_step = zoom_step
        self._min_zoom_scale = min_zoom_scale
        self._max_zoom_scale = max_zoom_scale
        self._fit_to_window = True
        self._manual_zoom_scale: float | None = None
        self._last_display_scale = 1.0
        self._last_viewport_mapping: _ViewportMapping | None = None
        self._selected_point: tuple[int, int] | None = None
        self._last_status_message: str | None = None
        self._crosshair_visible = True
        self._focus_status_visible = True
        self._window_created = False

    def render_latest_frame(self, delay_ms: int = 1) -> bool:
        return self.render_latest_frame_and_get_key(delay_ms=delay_ms) is not None

    def render_latest_frame_and_get_key(self, delay_ms: int = 1) -> int | None:
        frame = self._preview_service.get_latest_frame()
        if frame is None:
            return None

        self._ensure_window()
        if not self.is_open():
            return 27

        image = self._frame_adapter.to_image(frame)
        window_size = self._frame_adapter.get_window_image_size(self._window_name) or (frame.width, frame.height)
        status_lines = self._build_status_lines()
        status_band_height = self._calculate_status_band_height(status_lines)
        viewport_width = window_size[0]
        viewport_height = max(1, window_size[1] - status_band_height)
        display_scale = self._resolve_display_scale(frame.width, frame.height, viewport_width, viewport_height)
        self._last_display_scale = display_scale
        self._last_viewport_mapping = self._build_viewport_mapping(
            frame_width=frame.width,
            frame_height=frame.height,
            viewport_width=viewport_width,
            viewport_height=viewport_height,
            display_scale=display_scale,
        )
        display_image = self._frame_adapter.render_into_viewport(
            image,
            viewport_width=viewport_width,
            viewport_height=viewport_height,
            scale=display_scale,
        )
        crosshair_position = self._map_source_point_to_viewport(self._selected_point)
        if crosshair_position is not None and self._crosshair_visible:
            self._frame_adapter.draw_crosshair(display_image, crosshair_position[0], crosshair_position[1])
        display_image = self._frame_adapter.append_status_band(
            display_image,
            status_lines,
            line_height=self._STATUS_LINE_HEIGHT,
            padding=self._STATUS_PADDING,
        )
        pressed_key = self._frame_adapter.show_image(self._window_name, display_image, delay_ms=delay_ms)
        self._handle_shortcuts(pressed_key)
        if not self.is_open():
            return 27
        return pressed_key

    @property
    def is_fit_to_window_enabled(self) -> bool:
        return self._fit_to_window

    @property
    def manual_zoom_scale(self) -> float | None:
        return self._manual_zoom_scale

    def zoom_in(self) -> None:
        base_scale = self._last_display_scale if self._fit_to_window or self._manual_zoom_scale is None else self._manual_zoom_scale
        self._manual_zoom_scale = min(base_scale * self._zoom_step, self._max_zoom_scale)
        self._fit_to_window = False

    def zoom_out(self) -> None:
        base_scale = self._last_display_scale if self._fit_to_window or self._manual_zoom_scale is None else self._manual_zoom_scale
        self._manual_zoom_scale = max(base_scale / self._zoom_step, self._min_zoom_scale)
        self._fit_to_window = False

    def enable_fit_to_window(self) -> None:
        self._fit_to_window = True
        self._manual_zoom_scale = None

    def close(self) -> None:
        if self._window_created:
            self._frame_adapter.destroy_window(self._window_name)
            self._window_created = False

    def is_open(self) -> bool:
        if not self._window_created:
            return False
        return self._frame_adapter.is_window_visible(self._window_name)

    def _ensure_window(self) -> None:
        if self._window_created:
            return
        self._frame_adapter.create_window(self._window_name)
        self._frame_adapter.set_mouse_callback(self._window_name, self._handle_mouse_event)
        self._window_created = True

    def _resolve_display_scale(self, frame_width: int, frame_height: int, viewport_width: int, viewport_height: int) -> float:
        if self._fit_to_window:
            return max(min(viewport_width / frame_width, viewport_height / frame_height), self._min_zoom_scale)

        assert self._manual_zoom_scale is not None
        return self._manual_zoom_scale

    def _build_status_lines(self) -> list[str]:
        mode = "FIT" if self._fit_to_window else "ZOOM"
        primary_parts = [f"{mode} {self._last_display_scale:.2f}x"]
        if self._selected_point is not None:
            coordinate_text = self._coordinate_export_service.format_point(*self._selected_point)
            primary_parts.append(coordinate_text)
        if self._status_warning_provider is not None:
            warning = self._status_warning_provider()
            if warning:
                primary_parts.append(f"WARN: {warning}")
        if self._last_status_message:
            primary_parts.append(self._last_status_message)
        status_lines = [" | ".join(primary_parts)]
        focus_line = self._build_focus_status_line()
        if focus_line:
            status_lines.append(focus_line)
        status_lines.append("i=in o=out f=fit x=crosshair y=focus c=copy q=quit")
        return status_lines

    def _calculate_status_band_height(self, status_lines: list[str]) -> int:
        visible_lines = [line for line in status_lines if line]
        if not visible_lines:
            return 0
        return self._STATUS_PADDING * 2 + self._STATUS_LINE_HEIGHT * len(visible_lines)

    def _build_focus_status_line(self) -> str | None:
        if not self._focus_status_visible or self._focus_state_provider is None:
            return None

        focus_state = self._focus_state_provider()
        if focus_state is None:
            return "Focus: waiting"
        if not focus_state.result.is_valid:
            return f"Focus: invalid ({focus_state.result.metric_name})"
        return f"Focus: {focus_state.result.metric_name}={focus_state.result.score:.2f}"

    def _handle_shortcuts(self, pressed_key: int) -> None:
        normalized_key = pressed_key & 0xFF
        if normalized_key in (ord("i"), ord("I")):
            self.zoom_in()
        elif normalized_key in (ord("o"), ord("O")):
            self.zoom_out()
        elif normalized_key in (ord("f"), ord("F")):
            self.enable_fit_to_window()
        elif normalized_key in (ord("x"), ord("X")):
            self._crosshair_visible = not self._crosshair_visible
            self._last_status_message = "Crosshair shown" if self._crosshair_visible else "Crosshair hidden"
        elif normalized_key in (ord("y"), ord("Y")):
            self._focus_status_visible = not self._focus_status_visible
            self._last_status_message = "Focus shown" if self._focus_status_visible else "Focus hidden"
        elif normalized_key in (ord("c"), ord("C")):
            self._copy_selected_point()

    def _handle_mouse_event(self, event: int, x: int, y: int, flags: int | None = None, param=None) -> None:
        left_button_down = self._frame_adapter.get_left_button_down_event()
        if left_button_down is None or event != left_button_down:
            return

        selected_point = self._map_viewport_point_to_source(x, y)
        if selected_point is None:
            return

        self._selected_point = selected_point
        self._last_status_message = f"Selected {self._coordinate_export_service.format_point(*selected_point)}"

    def _copy_selected_point(self) -> None:
        if self._selected_point is None:
            self._last_status_message = "No point selected"
            return

        coordinate_text = self._coordinate_export_service.format_point(*self._selected_point)
        try:
            self._clipboard_copy_callback(coordinate_text)
        except Exception as exc:
            self._last_status_message = f"Copy failed: {exc}"
            return

        self._last_status_message = f"Copied {coordinate_text}"

    @staticmethod
    def _copy_text_to_clipboard(text: str) -> None:
        completed = subprocess.run(
            ["clip"],
            input=text,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            error_text = completed.stderr.strip() or completed.stdout.strip() or "clipboard command failed"
            raise RuntimeError(error_text)

    def _build_viewport_mapping(
        self,
        frame_width: int,
        frame_height: int,
        viewport_width: int,
        viewport_height: int,
        display_scale: float,
    ) -> _ViewportMapping:
        scaled_width = max(1, int(round(frame_width * display_scale)))
        scaled_height = max(1, int(round(frame_height * display_scale)))
        src_x = max(0, (scaled_width - viewport_width) // 2)
        src_y = max(0, (scaled_height - viewport_height) // 2)
        dst_x = max(0, (viewport_width - scaled_width) // 2)
        dst_y = max(0, (viewport_height - scaled_height) // 2)
        copy_width = min(scaled_width, viewport_width)
        copy_height = min(scaled_height, viewport_height)
        return _ViewportMapping(
            source_width=frame_width,
            source_height=frame_height,
            viewport_width=viewport_width,
            viewport_height=viewport_height,
            display_scale=display_scale,
            scaled_width=scaled_width,
            scaled_height=scaled_height,
            src_x=src_x,
            src_y=src_y,
            dst_x=dst_x,
            dst_y=dst_y,
            copy_width=copy_width,
            copy_height=copy_height,
        )

    def _map_viewport_point_to_source(self, x: int, y: int) -> tuple[int, int] | None:
        mapping = self._last_viewport_mapping
        if mapping is None:
            return None
        if not (
            mapping.dst_x <= x < mapping.dst_x + mapping.copy_width
            and mapping.dst_y <= y < mapping.dst_y + mapping.copy_height
        ):
            return None

        scaled_x = mapping.src_x + (x - mapping.dst_x)
        scaled_y = mapping.src_y + (y - mapping.dst_y)
        source_x = int(scaled_x / mapping.display_scale)
        source_y = int(scaled_y / mapping.display_scale)
        source_x = min(max(source_x, 0), mapping.source_width - 1)
        source_y = min(max(source_y, 0), mapping.source_height - 1)
        return source_x, source_y

    def _map_source_point_to_viewport(self, point: tuple[int, int] | None) -> tuple[int, int] | None:
        mapping = self._last_viewport_mapping
        if mapping is None or point is None:
            return None

        scaled_x = int(round(point[0] * mapping.display_scale))
        scaled_y = int(round(point[1] * mapping.display_scale))
        viewport_x = mapping.dst_x + scaled_x - mapping.src_x
        viewport_y = mapping.dst_y + scaled_y - mapping.src_y
        if not (
            mapping.dst_x <= viewport_x < mapping.dst_x + mapping.copy_width
            and mapping.dst_y <= viewport_y < mapping.dst_y + mapping.copy_height
        ):
            return None
        return viewport_x, viewport_y


__all__ = ["OpenCvPreviewWindow"]
