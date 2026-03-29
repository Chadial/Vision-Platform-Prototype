from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from pathlib import Path
import subprocess
from time import monotonic
from typing import Callable

from vision_platform.imaging.opencv_adapter import OpenCvFrameAdapter
from vision_platform.libraries.common_models import FocusPreviewState
from vision_platform.libraries.common_models import RoiDefinition
from vision_platform.libraries.roi_core import roi_bounds
from vision_platform.services.display_service import CoordinateExportService
from vision_platform.services.stream_service.preview_service import PreviewService
from vision_platform.services.stream_service.roi_state_service import RoiStateService


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
        roi_state_service: RoiStateService | None = None,
        snapshot_callback: Callable[[], Path] | None = None,
        clipboard_copy_callback: Callable[[str], None] | None = None,
        coordinate_export_service: CoordinateExportService | None = None,
        zoom_step: float = 1.5,
        min_zoom_scale: float = 0.05,
        max_zoom_scale: float = 8.0,
        time_provider: Callable[[], float] | None = None,
    ) -> None:
        self._preview_service = preview_service
        self._window_name = window_name
        self._frame_adapter = frame_adapter or OpenCvFrameAdapter()
        self._status_warning_provider = status_warning_provider
        self._focus_state_provider = focus_state_provider
        self._roi_state_service = roi_state_service
        self._snapshot_callback = snapshot_callback
        self._clipboard_copy_callback = clipboard_copy_callback or self._copy_text_to_clipboard
        self._coordinate_export_service = coordinate_export_service or CoordinateExportService()
        self._zoom_step = zoom_step
        self._min_zoom_scale = min_zoom_scale
        self._max_zoom_scale = max_zoom_scale
        self._time_provider = time_provider or monotonic
        self._fit_to_window = True
        self._manual_zoom_scale: float | None = None
        self._last_display_scale = 1.0
        self._last_viewport_mapping: _ViewportMapping | None = None
        self._selected_point: tuple[int, int] | None = None
        self._last_status_message: str | None = None
        self._frame_render_timestamps: deque[float] = deque(maxlen=30)
        self._crosshair_visible = True
        self._focus_status_visible = True
        self._roi_mode: str | None = None
        self._fallback_active_roi: RoiDefinition | None = None
        self._roi_anchor_point: tuple[int, int] | None = None
        self._roi_preview_point: tuple[int, int] | None = None
        self._last_cursor_viewport_point: tuple[int, int] | None = None
        self._viewport_origin_scaled: tuple[int, int] = (0, 0)
        self._pan_anchor_viewport_point: tuple[int, int] | None = None
        self._pan_anchor_origin_scaled: tuple[int, int] | None = None
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
        self._record_render_timestamp()
        status_lines = self._build_status_lines()
        status_band_height = self._calculate_status_band_height(status_lines)
        viewport_width = window_size[0]
        viewport_height = max(1, window_size[1] - status_band_height)
        display_scale = self._resolve_display_scale(frame.width, frame.height, viewport_width, viewport_height)
        self._last_display_scale = display_scale
        viewport_origin = self._resolve_viewport_origin(
            frame_width=frame.width,
            frame_height=frame.height,
            viewport_width=viewport_width,
            viewport_height=viewport_height,
            display_scale=display_scale,
        )
        self._last_viewport_mapping = self._build_viewport_mapping(
            frame_width=frame.width,
            frame_height=frame.height,
            viewport_width=viewport_width,
            viewport_height=viewport_height,
            display_scale=display_scale,
            src_x=viewport_origin[0],
            src_y=viewport_origin[1],
        )
        display_image = self._frame_adapter.render_into_viewport(
            image,
            viewport_width=viewport_width,
            viewport_height=viewport_height,
            scale=display_scale,
            source_offset_x=viewport_origin[0],
            source_offset_y=viewport_origin[1],
        )
        self._draw_viewport_outline_if_needed(display_image)
        crosshair_position = self._map_source_point_to_viewport(self._selected_point)
        if crosshair_position is not None and self._crosshair_visible:
            self._frame_adapter.draw_crosshair(display_image, crosshair_position[0], crosshair_position[1])
        self._draw_roi(display_image)
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
        new_scale = min(base_scale * self._zoom_step, self._max_zoom_scale)
        self._update_zoom_state(new_scale, previous_scale=base_scale)
        self._fit_to_window = False

    def zoom_out(self) -> None:
        base_scale = self._last_display_scale if self._fit_to_window or self._manual_zoom_scale is None else self._manual_zoom_scale
        new_scale = max(base_scale / self._zoom_step, self._min_zoom_scale)
        self._update_zoom_state(new_scale, previous_scale=base_scale)
        self._fit_to_window = False

    def enable_fit_to_window(self) -> None:
        self._fit_to_window = True
        self._manual_zoom_scale = None
        self._viewport_origin_scaled = (0, 0)
        self._pan_anchor_viewport_point = None
        self._pan_anchor_origin_scaled = None

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

    def _resolve_viewport_origin(
        self,
        frame_width: int,
        frame_height: int,
        viewport_width: int,
        viewport_height: int,
        display_scale: float,
    ) -> tuple[int, int]:
        if self._fit_to_window:
            self._viewport_origin_scaled = (0, 0)
            return self._viewport_origin_scaled

        scaled_width = max(1, int(round(frame_width * display_scale)))
        scaled_height = max(1, int(round(frame_height * display_scale)))
        max_src_x = max(0, scaled_width - viewport_width)
        max_src_y = max(0, scaled_height - viewport_height)
        origin_x = min(max(0, self._viewport_origin_scaled[0]), max_src_x)
        origin_y = min(max(0, self._viewport_origin_scaled[1]), max_src_y)
        self._viewport_origin_scaled = (origin_x, origin_y)
        return self._viewport_origin_scaled

    def _update_zoom_state(self, new_scale: float, previous_scale: float) -> None:
        self._manual_zoom_scale = new_scale
        if self._last_viewport_mapping is None:
            return

        anchored_origin = self._build_cursor_anchored_origin(new_scale)
        if anchored_origin is not None:
            self._viewport_origin_scaled = anchored_origin
            return

        top_left_source_x = self._last_viewport_mapping.src_x / max(previous_scale, 1e-9)
        top_left_source_y = self._last_viewport_mapping.src_y / max(previous_scale, 1e-9)
        self._viewport_origin_scaled = (
            int(round(top_left_source_x * new_scale)),
            int(round(top_left_source_y * new_scale)),
        )

    def _build_cursor_anchored_origin(self, new_scale: float) -> tuple[int, int] | None:
        if self._last_viewport_mapping is None or self._last_cursor_viewport_point is None:
            return None

        cursor_source_point = self._map_viewport_point_to_source(
            self._last_cursor_viewport_point[0],
            self._last_cursor_viewport_point[1],
        )
        if cursor_source_point is None:
            return None

        return (
            int(round(cursor_source_point[0] * new_scale - self._last_cursor_viewport_point[0])),
            int(round(cursor_source_point[1] * new_scale - self._last_cursor_viewport_point[1])),
        )

    def _build_status_lines(self) -> list[str]:
        mode = "FIT" if self._fit_to_window else "ZOOM"
        primary_parts = [f"{mode} {self._last_display_scale:.2f}x"]
        viewport_text = self._build_viewport_status_text()
        if viewport_text:
            primary_parts.append(viewport_text)
        fps_text = self._build_fps_text()
        if fps_text:
            primary_parts.append(fps_text)
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
        roi_line = self._build_roi_status_line()
        if roi_line:
            status_lines.append(roi_line)
        focus_line = self._build_focus_status_line()
        if focus_line:
            status_lines.append(focus_line)
        shortcut_line = self.build_shortcut_hint(
            has_snapshot_shortcut=self._snapshot_callback is not None,
            has_focus_toggle=self._focus_state_provider is not None,
        )
        status_lines.append(shortcut_line)
        return status_lines

    @staticmethod
    def build_shortcut_hint(
        *,
        has_snapshot_shortcut: bool,
        has_focus_toggle: bool,
    ) -> str:
        shortcut_parts = ["i=in", "o=out", "f=fit"]
        if has_snapshot_shortcut:
            shortcut_parts.append("+=snapshot")
        shortcut_parts.append("x=crosshair")
        if has_focus_toggle:
            shortcut_parts.append("y=focus")
        shortcut_parts.extend(["r=rect", "e=ellipse", "wheel=zoom", "mdrag=pan", "c=copy", "q=quit"])
        return " ".join(shortcut_parts)

    def _calculate_status_band_height(self, status_lines: list[str]) -> int:
        visible_lines = [line for line in status_lines if line]
        if not visible_lines:
            return 0
        return self._STATUS_PADDING * 2 + self._STATUS_LINE_HEIGHT * len(visible_lines)

    def _record_render_timestamp(self) -> None:
        self._frame_render_timestamps.append(self._time_provider())

    def _build_fps_text(self) -> str | None:
        if len(self._frame_render_timestamps) < 2:
            return None

        elapsed = self._frame_render_timestamps[-1] - self._frame_render_timestamps[0]
        if elapsed <= 0:
            return None

        fps = (len(self._frame_render_timestamps) - 1) / elapsed
        return f"FPS {fps:.1f}"

    def _build_viewport_status_text(self) -> str | None:
        if self._fit_to_window:
            return None
        return f"view={self._viewport_origin_scaled[0]},{self._viewport_origin_scaled[1]}"

    def _build_focus_status_line(self) -> str | None:
        if not self._focus_status_visible or self._focus_state_provider is None:
            return None

        focus_state = self._focus_state_provider()
        if focus_state is None:
            return "Focus: waiting"
        if not focus_state.result.is_valid:
            return f"Focus: invalid ({focus_state.result.metric_name})"
        return f"Focus: {focus_state.result.metric_name}={focus_state.result.score:.2f}"

    def _build_roi_status_line(self) -> str | None:
        if self._roi_anchor_point is not None and self._roi_mode is not None:
            base_line = f"ROI mode: {self._roi_mode} anchor={self._coordinate_export_service.format_point(*self._roi_anchor_point)}"
            if self._roi_preview_point is not None:
                preview_text = self._coordinate_export_service.format_point(*self._roi_preview_point)
                return f"{base_line} preview={preview_text}"
            return base_line
        active_roi = self._get_active_roi()
        if active_roi is not None:
            return f"ROI active: {active_roi.shape}"
        if self._roi_mode is None:
            return None
        if self._roi_mode == "rectangle":
            return "ROI mode: rectangle (entry point active)"
        if self._roi_mode == "ellipse":
            return "ROI mode: ellipse (entry point active)"
        return f"ROI mode: {self._roi_mode}"

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
            if self._focus_state_provider is None:
                self._last_status_message = "Focus display unavailable"
                return
            self._focus_status_visible = not self._focus_status_visible
            self._last_status_message = "Focus shown" if self._focus_status_visible else "Focus hidden"
        elif normalized_key in (ord("r"), ord("R")):
            self._toggle_roi_mode("rectangle")
        elif normalized_key in (ord("e"), ord("E")):
            self._toggle_roi_mode("ellipse")
        elif normalized_key in (ord("+"), ord("=")):
            self._save_preview_snapshot()
        elif normalized_key in (ord("c"), ord("C")):
            self._copy_selected_point()

    def _toggle_roi_mode(self, roi_mode: str) -> None:
        if self._roi_mode == roi_mode:
            self._roi_mode = None
            self._roi_anchor_point = None
            self._roi_preview_point = None
            self._last_status_message = "ROI mode cleared"
            return
        self._roi_mode = roi_mode
        self._roi_anchor_point = None
        self._roi_preview_point = None
        self._last_status_message = f"ROI mode set to {roi_mode}"

    def _handle_mouse_event(self, event: int, x: int, y: int, flags: int | None = None, param=None) -> None:
        left_button_down = self._frame_adapter.get_left_button_down_event()
        middle_button_down = self._frame_adapter.get_middle_button_down_event()
        middle_button_up = self._frame_adapter.get_middle_button_up_event()
        mouse_move = self._frame_adapter.get_mouse_move_event()
        mouse_wheel = self._frame_adapter.get_mouse_wheel_event()
        self._last_cursor_viewport_point = (x, y)
        selected_point = self._map_viewport_point_to_source(x, y)
        if middle_button_down is not None and event == middle_button_down:
            self._start_pan((x, y))
            return
        if middle_button_up is not None and event == middle_button_up:
            self._stop_pan()
            return
        if mouse_wheel is not None and event == mouse_wheel:
            self._handle_mouse_wheel(flags, selected_point)
            return
        if mouse_move is not None and event == mouse_move:
            if self._update_pan((x, y)):
                return
            self._handle_roi_mouse_move(selected_point)
            return

        if left_button_down is None or event != left_button_down:
            return

        if selected_point is None:
            return

        if self._roi_mode is not None:
            self._handle_roi_click(selected_point)
            return

        self._selected_point = selected_point
        self._last_status_message = f"Selected {self._coordinate_export_service.format_point(*selected_point)}"

    def _handle_mouse_wheel(self, flags: int | None, selected_point: tuple[int, int] | None) -> None:
        delta = self._frame_adapter.get_mouse_wheel_delta(flags)
        if delta == 0:
            return
        if selected_point is None:
            self._last_status_message = "Wheel zoom ignored outside image"
            return
        if delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def _start_pan(self, viewport_point: tuple[int, int]) -> None:
        if self._fit_to_window:
            self._last_status_message = "Pan unavailable in fit mode"
            self._pan_anchor_viewport_point = None
            self._pan_anchor_origin_scaled = None
            return
        self._pan_anchor_viewport_point = viewport_point
        self._pan_anchor_origin_scaled = self._viewport_origin_scaled
        self._last_status_message = "Panning"

    def _stop_pan(self) -> None:
        if self._pan_anchor_viewport_point is None:
            return
        self._pan_anchor_viewport_point = None
        self._pan_anchor_origin_scaled = None
        self._last_status_message = "Pan complete"

    def _update_pan(self, viewport_point: tuple[int, int]) -> bool:
        if self._pan_anchor_viewport_point is None or self._pan_anchor_origin_scaled is None:
            return False

        delta_x = viewport_point[0] - self._pan_anchor_viewport_point[0]
        delta_y = viewport_point[1] - self._pan_anchor_viewport_point[1]
        self._viewport_origin_scaled = (
            self._pan_anchor_origin_scaled[0] - delta_x,
            self._pan_anchor_origin_scaled[1] - delta_y,
        )
        self._last_status_message = "Panning"
        return True

    def _handle_roi_click(self, selected_point: tuple[int, int]) -> None:
        if self._roi_anchor_point is None:
            self._roi_anchor_point = selected_point
            self._roi_preview_point = None
            self._last_status_message = f"ROI anchor set to {self._coordinate_export_service.format_point(*selected_point)}"
            return

        roi = self._build_roi_definition(self._roi_mode, self._roi_anchor_point, selected_point)
        self._set_active_roi(roi)
        self._roi_anchor_point = None
        self._roi_preview_point = None
        self._last_status_message = f"ROI saved as {roi.shape}"

    def _handle_roi_mouse_move(self, selected_point: tuple[int, int] | None) -> None:
        if self._roi_anchor_point is None:
            return
        self._roi_preview_point = selected_point

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
            return RoiDefinition(roi_id="preview-roi", shape="ellipse", points=points)

        points = (anchor_point, selected_point)
        return RoiDefinition(roi_id="preview-roi", shape="rectangle", points=points)

    def _draw_roi(self, display_image) -> None:
        draft_roi = self._build_draft_roi()
        if draft_roi is not None:
            self._draw_roi_definition(display_image, draft_roi)
        active_roi = self._get_active_roi()
        if active_roi is not None:
            self._draw_roi_definition(display_image, active_roi)

    def _draw_viewport_outline_if_needed(self, display_image) -> None:
        mapping = self._last_viewport_mapping
        if mapping is None:
            return
        if mapping.copy_width >= mapping.viewport_width and mapping.copy_height >= mapping.viewport_height:
            return

        right = max(0, mapping.copy_width - 1)
        bottom = max(0, mapping.copy_height - 1)
        self._frame_adapter.draw_viewport_outline(display_image, 0, 0, right, bottom)

    def _build_draft_roi(self) -> RoiDefinition | None:
        if self._roi_mode is None or self._roi_anchor_point is None or self._roi_preview_point is None:
            return None
        return self._build_roi_definition(self._roi_mode, self._roi_anchor_point, self._roi_preview_point)

    def _draw_roi_definition(self, display_image, roi: RoiDefinition) -> None:
        bounds = roi_bounds(roi)
        if bounds is None:
            return

        top_left = self._map_source_point_to_viewport((int(round(bounds[0])), int(round(bounds[1]))))
        bottom_right = self._map_source_point_to_viewport((int(round(bounds[2])), int(round(bounds[3]))))
        if top_left is None or bottom_right is None:
            return

        left = min(top_left[0], bottom_right[0])
        top = min(top_left[1], bottom_right[1])
        right = max(top_left[0], bottom_right[0])
        bottom = max(top_left[1], bottom_right[1])
        if roi.shape == "ellipse":
            center_x = left + (right - left) // 2
            center_y = top + (bottom - top) // 2
            radius_x = max(1, (right - left) // 2)
            radius_y = max(1, (bottom - top) // 2)
            self._frame_adapter.draw_ellipse_outline(display_image, center_x, center_y, radius_x, radius_y)
            return

        self._frame_adapter.draw_rectangle_outline(display_image, left, top, right, bottom)

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

    def _save_preview_snapshot(self) -> None:
        if self._snapshot_callback is None:
            self._last_status_message = "Snapshot shortcut unavailable"
            return

        try:
            saved_path = self._snapshot_callback()
        except Exception as exc:
            self._last_status_message = f"Snapshot failed: {exc}"
            return

        self._last_status_message = f"Snapshot saved: {saved_path.name}"

    def _get_active_roi(self) -> RoiDefinition | None:
        if self._roi_state_service is not None:
            return self._roi_state_service.get_active_roi()
        return self._fallback_active_roi

    def _set_active_roi(self, roi: RoiDefinition) -> None:
        if self._roi_state_service is not None:
            self._roi_state_service.set_active_roi(roi)
            return
        self._fallback_active_roi = roi

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
        src_x: int = 0,
        src_y: int = 0,
    ) -> _ViewportMapping:
        scaled_width = max(1, int(round(frame_width * display_scale)))
        scaled_height = max(1, int(round(frame_height * display_scale)))
        max_src_x = max(0, scaled_width - viewport_width)
        max_src_y = max(0, scaled_height - viewport_height)
        src_x = min(max(0, src_x), max_src_x)
        src_y = min(max(0, src_y), max_src_y)
        dst_x = 0
        dst_y = 0
        copy_width = min(scaled_width - src_x, viewport_width)
        copy_height = min(scaled_height - src_y, viewport_height)
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
