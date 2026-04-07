from __future__ import annotations

from collections import deque
from pathlib import Path
import subprocess
from time import monotonic
from typing import Callable

from vision_platform.imaging.opencv_adapter import OpenCvFrameAdapter
from vision_platform.libraries.common_models import FocusPreviewState
from vision_platform.libraries.common_models import RoiDefinition
from vision_platform.libraries.roi_core import roi_bounds
from vision_platform.services.display_service import (
    CoordinateExportService,
    DisplayGeometryService,
    PreviewFocusStatusModel,
    PreviewInteractionCommand,
    PreviewInteractionOutcome,
    PreviewInteractionService,
    PreviewInteractionState,
    PreviewOverlayModel,
    PreviewRoiStatusModel,
    PreviewShortcutHint,
    PreviewStatusLineModel,
    PreviewStatusModel,
    PreviewStatusModelService,
    ZoomPanState,
    format_focus_score,
)
from vision_platform.services.stream_service.preview_service import PreviewService
from vision_platform.services.stream_service.roi_state_service import RoiStateService


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
        geometry_service: DisplayGeometryService | None = None,
        interaction_service: PreviewInteractionService | None = None,
        status_model_service: PreviewStatusModelService | None = None,
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
        self._geometry_service = geometry_service or DisplayGeometryService()
        self._interaction_service = interaction_service or PreviewInteractionService(self._geometry_service)
        self._status_model_service = status_model_service or PreviewStatusModelService()
        self._zoom_step = zoom_step
        self._min_zoom_scale = min_zoom_scale
        self._max_zoom_scale = max_zoom_scale
        self._time_provider = time_provider or monotonic
        self._geometry_state = ZoomPanState()
        self._last_display_scale = 1.0
        self._last_viewport_mapping = None
        self._interaction_state = PreviewInteractionState()
        self._frame_render_timestamps: deque[float] = deque(maxlen=30)
        self._fallback_active_roi: RoiDefinition | None = None
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
        status_model = self._build_status_model()
        status_lines = self._format_status_lines(status_model)
        status_band_height = self._calculate_status_band_height(status_lines)
        viewport_width = window_size[0]
        viewport_height = max(1, window_size[1] - status_band_height)
        display_scale = self._geometry_service.resolve_display_scale(
            frame.width,
            frame.height,
            viewport_width,
            viewport_height,
            self._geometry_state,
            min_zoom_scale=self._min_zoom_scale,
        )
        self._last_display_scale = display_scale
        viewport_origin = self._geometry_service.resolve_viewport_origin(
            frame.width,
            frame.height,
            viewport_width,
            viewport_height,
            display_scale,
            self._geometry_state,
        )
        self._last_viewport_mapping = self._geometry_service.build_viewport_mapping(
            frame.width,
            frame.height,
            viewport_width,
            viewport_height,
            display_scale,
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
        self._render_overlay_model(display_image, self._build_overlay_model())
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
        return self._geometry_state.fit_to_window

    @property
    def _fit_to_window(self) -> bool:
        return self._geometry_state.fit_to_window

    @_fit_to_window.setter
    def _fit_to_window(self, value: bool) -> None:
        self._geometry_state.fit_to_window = value

    @property
    def _selected_point(self) -> tuple[int, int] | None:
        return self._interaction_state.selected_point

    @_selected_point.setter
    def _selected_point(self, value: tuple[int, int] | None) -> None:
        self._interaction_state.selected_point = value

    @property
    def _last_status_message(self) -> str | None:
        return self._interaction_state.last_status_message

    @_last_status_message.setter
    def _last_status_message(self, value: str | None) -> None:
        self._interaction_state.last_status_message = value

    @property
    def _crosshair_visible(self) -> bool:
        return self._interaction_state.crosshair_visible

    @_crosshair_visible.setter
    def _crosshair_visible(self, value: bool) -> None:
        self._interaction_state.crosshair_visible = value

    @property
    def _focus_status_visible(self) -> bool:
        return self._interaction_state.focus_status_visible

    @_focus_status_visible.setter
    def _focus_status_visible(self, value: bool) -> None:
        self._interaction_state.focus_status_visible = value

    @property
    def _roi_mode(self) -> str | None:
        return self._interaction_state.roi_mode

    @_roi_mode.setter
    def _roi_mode(self, value: str | None) -> None:
        self._interaction_state.roi_mode = value

    @property
    def _roi_anchor_point(self) -> tuple[int, int] | None:
        return self._interaction_state.roi_anchor_point

    @_roi_anchor_point.setter
    def _roi_anchor_point(self, value: tuple[int, int] | None) -> None:
        self._interaction_state.roi_anchor_point = value

    @property
    def _roi_preview_point(self) -> tuple[int, int] | None:
        return self._interaction_state.roi_preview_point

    @_roi_preview_point.setter
    def _roi_preview_point(self, value: tuple[int, int] | None) -> None:
        self._interaction_state.roi_preview_point = value

    @property
    def _last_cursor_viewport_point(self) -> tuple[int, int] | None:
        return self._interaction_state.last_cursor_viewport_point

    @_last_cursor_viewport_point.setter
    def _last_cursor_viewport_point(self, value: tuple[int, int] | None) -> None:
        self._interaction_state.last_cursor_viewport_point = value

    @property
    def manual_zoom_scale(self) -> float | None:
        return self._geometry_state.manual_zoom_scale

    def zoom_in(self) -> None:
        self._apply_interaction_command(PreviewInteractionCommand(action="zoom_in"))

    def zoom_out(self) -> None:
        self._apply_interaction_command(PreviewInteractionCommand(action="zoom_out"))

    def enable_fit_to_window(self) -> None:
        self._apply_interaction_command(PreviewInteractionCommand(action="enable_fit"))

    @property
    def _manual_zoom_scale(self) -> float | None:
        return self._geometry_state.manual_zoom_scale

    @_manual_zoom_scale.setter
    def _manual_zoom_scale(self, value: float | None) -> None:
        self._geometry_state.manual_zoom_scale = value

    @property
    def _viewport_origin_scaled(self) -> tuple[int, int]:
        return self._geometry_state.viewport_origin_scaled

    @_viewport_origin_scaled.setter
    def _viewport_origin_scaled(self, value: tuple[int, int]) -> None:
        self._geometry_state.viewport_origin_scaled = value

    @property
    def _pan_anchor_viewport_point(self) -> tuple[int, int] | None:
        return self._geometry_state.pan_anchor_viewport_point

    @_pan_anchor_viewport_point.setter
    def _pan_anchor_viewport_point(self, value: tuple[int, int] | None) -> None:
        self._geometry_state.pan_anchor_viewport_point = value

    @property
    def _pan_anchor_origin_scaled(self) -> tuple[int, int] | None:
        return self._geometry_state.pan_anchor_origin_scaled

    @_pan_anchor_origin_scaled.setter
    def _pan_anchor_origin_scaled(self, value: tuple[int, int] | None) -> None:
        self._geometry_state.pan_anchor_origin_scaled = value

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

    def _build_status_lines(self) -> list[str]:
        return self._format_status_lines(self._build_status_model())

    @staticmethod
    def build_shortcut_hint(
        *,
        has_snapshot_shortcut: bool,
        has_focus_toggle: bool,
    ) -> str:
        shortcut_hints = PreviewStatusModelService.build_shortcut_hints(
            has_snapshot_shortcut=has_snapshot_shortcut,
            has_focus_toggle=has_focus_toggle,
        )
        return OpenCvPreviewWindow._format_shortcut_hints(shortcut_hints)

    def _calculate_status_band_height(self, status_lines: list[str]) -> int:
        visible_lines = [line for line in status_lines if line]
        if not visible_lines:
            return 0
        return self._STATUS_PADDING * 2 + self._STATUS_LINE_HEIGHT * len(visible_lines)

    def _record_render_timestamp(self) -> None:
        self._frame_render_timestamps.append(self._time_provider())

    def _calculate_fps(self) -> float | None:
        if len(self._frame_render_timestamps) < 2:
            return None

        elapsed = self._frame_render_timestamps[-1] - self._frame_render_timestamps[0]
        if elapsed <= 0:
            return None

        return (len(self._frame_render_timestamps) - 1) / elapsed

    def _build_status_model(self) -> PreviewStatusModel:
        focus_state = self._focus_state_provider() if self._focus_state_provider is not None else None
        selected_point_text = None
        if self._selected_point is not None:
            selected_point_text = self._coordinate_export_service.format_point(*self._selected_point)
        warning = self._status_warning_provider() if self._status_warning_provider is not None else None
        return self._status_model_service.build_status_model(
            fit_to_window=self._geometry_state.fit_to_window,
            display_scale=self._last_display_scale,
            viewport_origin_scaled=self._geometry_state.viewport_origin_scaled,
            fps=self._calculate_fps(),
            selected_point=self._selected_point,
            selected_point_text=selected_point_text,
            warning=warning,
            transient_message=self._last_status_message,
            has_focus_provider=self._focus_state_provider is not None,
            focus_status_visible=self._focus_status_visible,
            focus_state=focus_state,
            roi_mode=self._roi_mode,
            roi_anchor_point=self._roi_anchor_point,
            roi_preview_point=self._roi_preview_point,
            active_roi=self._get_active_roi(),
            has_snapshot_shortcut=self._snapshot_callback is not None,
            has_focus_toggle=self._focus_state_provider is not None,
        )

    def _build_overlay_model(self) -> PreviewOverlayModel:
        return self._status_model_service.build_overlay_model(
            crosshair_visible=self._crosshair_visible,
            selected_point=self._selected_point,
            draft_roi=self._build_draft_roi(),
            active_roi=self._get_active_roi(),
            focus_status_visible=self._focus_status_visible,
            focus_state=self._focus_state_provider() if self._focus_state_provider is not None else None,
            focus_anchor_point=None,
            show_viewport_outline=self._should_draw_viewport_outline(),
        )

    def _handle_shortcuts(self, pressed_key: int) -> None:
        normalized_key = pressed_key & 0xFF
        if normalized_key in (ord("i"), ord("I")):
            self._apply_interaction_command(PreviewInteractionCommand(action="zoom_in"))
        elif normalized_key in (ord("o"), ord("O")):
            self._apply_interaction_command(PreviewInteractionCommand(action="zoom_out"))
        elif normalized_key in (ord("f"), ord("F")):
            self._apply_interaction_command(PreviewInteractionCommand(action="enable_fit"))
        elif normalized_key in (ord("x"), ord("X")):
            self._apply_interaction_command(PreviewInteractionCommand(action="toggle_crosshair"))
        elif normalized_key in (ord("y"), ord("Y")):
            self._apply_interaction_command(PreviewInteractionCommand(action="toggle_focus"))
        elif normalized_key in (ord("r"), ord("R")):
            self._apply_interaction_command(PreviewInteractionCommand(action="toggle_roi_mode", roi_mode="rectangle"))
        elif normalized_key in (ord("e"), ord("E")):
            self._apply_interaction_command(PreviewInteractionCommand(action="toggle_roi_mode", roi_mode="ellipse"))
        elif normalized_key in (ord("+"), ord("=")):
            self._apply_interaction_command(PreviewInteractionCommand(action="request_snapshot"))
        elif normalized_key in (ord("c"), ord("C")):
            self._apply_interaction_command(PreviewInteractionCommand(action="request_copy"))

    def _handle_mouse_event(self, event: int, x: int, y: int, flags: int | None = None, param=None) -> None:
        left_button_down = self._frame_adapter.get_left_button_down_event()
        middle_button_down = self._frame_adapter.get_middle_button_down_event()
        middle_button_up = self._frame_adapter.get_middle_button_up_event()
        mouse_move = self._frame_adapter.get_mouse_move_event()
        mouse_wheel = self._frame_adapter.get_mouse_wheel_event()
        self._apply_interaction_command(
            PreviewInteractionCommand(action="cursor_moved", viewport_point=(x, y)),
            apply_outcome=False,
        )
        selected_point = self._map_viewport_point_to_source(x, y)
        if middle_button_down is not None and event == middle_button_down:
            self._apply_interaction_command(PreviewInteractionCommand(action="start_pan", viewport_point=(x, y)))
            return
        if middle_button_up is not None and event == middle_button_up:
            self._apply_interaction_command(PreviewInteractionCommand(action="stop_pan"))
            return
        if mouse_wheel is not None and event == mouse_wheel:
            self._handle_mouse_wheel(flags, selected_point)
            return
        if mouse_move is not None and event == mouse_move:
            outcome = self._apply_interaction_command(
                PreviewInteractionCommand(action="update_pan", viewport_point=(x, y)),
                apply_outcome=False,
            )
            if outcome.handled:
                return
            self._handle_roi_mouse_move(selected_point)
            return

        if left_button_down is None or event != left_button_down:
            return

        if selected_point is None:
            return

        self._apply_interaction_command(
            PreviewInteractionCommand(action="select_source_point", source_point=selected_point)
        )

    def _handle_mouse_wheel(self, flags: int | None, selected_point: tuple[int, int] | None) -> None:
        delta = self._frame_adapter.get_mouse_wheel_delta(flags)
        self._apply_interaction_command(
            PreviewInteractionCommand(action="wheel_zoom", source_point=selected_point, wheel_delta=delta)
        )

    def _handle_roi_mouse_move(self, selected_point: tuple[int, int] | None) -> None:
        if self._roi_anchor_point is None:
            return
        self._roi_preview_point = selected_point

    def _update_pan(self, viewport_point: tuple[int, int]) -> bool:
        outcome = self._apply_interaction_command(
            PreviewInteractionCommand(action="update_pan", viewport_point=viewport_point),
            apply_outcome=False,
        )
        return outcome.handled

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

    def _render_overlay_model(self, display_image, overlay_model: PreviewOverlayModel) -> None:
        if overlay_model.show_viewport_outline:
            self._draw_viewport_outline(display_image)
        crosshair_position = self._map_source_point_to_viewport(overlay_model.crosshair_point)
        if crosshair_position is not None:
            self._frame_adapter.draw_crosshair(display_image, crosshair_position[0], crosshair_position[1])
        if overlay_model.draft_roi is not None:
            self._draw_roi_definition(display_image, overlay_model.draft_roi)
        if overlay_model.active_roi is not None:
            self._draw_roi_definition(display_image, overlay_model.active_roi)

    def _draw_roi(self, display_image) -> None:
        self._render_overlay_model(display_image, self._build_overlay_model())

    def _should_draw_viewport_outline(self) -> bool:
        mapping = self._last_viewport_mapping
        if mapping is None:
            return False
        if mapping.copy_width >= mapping.viewport_width and mapping.copy_height >= mapping.viewport_height:
            return False
        return True

    def _draw_viewport_outline(self, display_image) -> None:
        mapping = self._last_viewport_mapping
        if mapping is None:
            return
        right = max(0, mapping.copy_width - 1)
        bottom = max(0, mapping.copy_height - 1)
        self._frame_adapter.draw_viewport_outline(display_image, 0, 0, right, bottom)

    def _draw_viewport_outline_if_needed(self, display_image) -> None:
        if self._should_draw_viewport_outline():
            self._draw_viewport_outline(display_image)

    def _format_status_lines(self, status_model: PreviewStatusModel) -> list[str]:
        status_lines = [self._format_status_line_model(status_model.primary_line)]
        roi_line = self._format_roi_status(status_model.roi_status)
        if roi_line:
            status_lines.append(roi_line)
        focus_line = self._format_focus_status(status_model.focus_status)
        if focus_line:
            status_lines.append(focus_line)
        status_lines.append(self._format_shortcut_hints(status_model.shortcuts))
        return status_lines

    @staticmethod
    def _format_status_line_model(line_model: PreviewStatusLineModel) -> str:
        return " | ".join(entry.value for entry in line_model.entries)

    def _format_roi_status(self, roi_status: PreviewRoiStatusModel | None) -> str | None:
        if roi_status is None:
            return None
        if roi_status.state == "active":
            return f"ROI active: {roi_status.active_shape}"
        if roi_status.state == "mode_active":
            if roi_status.roi_mode == "rectangle":
                return "ROI mode: rectangle (entry point active)"
            if roi_status.roi_mode == "ellipse":
                return "ROI mode: ellipse (entry point active)"
            return f"ROI mode: {roi_status.roi_mode}"
        if roi_status.state == "anchor_pending":
            assert roi_status.roi_mode is not None
            assert roi_status.anchor_point is not None
            anchor_text = self._coordinate_export_service.format_point(*roi_status.anchor_point)
            base_line = f"ROI mode: {roi_status.roi_mode} anchor={anchor_text}"
            if roi_status.preview_point is None:
                return base_line
            preview_text = self._coordinate_export_service.format_point(*roi_status.preview_point)
            return f"{base_line} preview={preview_text}"
        return None

    @staticmethod
    def _format_focus_status(focus_status: PreviewFocusStatusModel | None) -> str | None:
        if focus_status is None or focus_status.state == "hidden":
            return None
        if focus_status.state == "waiting":
            return "Focus: waiting"
        if focus_status.state == "invalid":
            return f"Focus: invalid ({focus_status.metric_name})"
        return f"Focus: {focus_status.metric_name}={format_focus_score(focus_status.score)}"

    @staticmethod
    def _format_shortcut_hints(shortcut_hints: tuple[PreviewShortcutHint, ...]) -> str:
        return " ".join(f"{shortcut.key}={shortcut.action}" for shortcut in shortcut_hints)

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

    def _apply_interaction_command(
        self,
        command: PreviewInteractionCommand,
        *,
        apply_outcome: bool = True,
    ):
        outcome = self._interaction_service.apply_command(
            command,
            self._interaction_state,
            self._geometry_state,
            last_display_scale=self._last_display_scale,
            last_viewport_mapping=self._last_viewport_mapping,
            zoom_step=self._zoom_step,
            min_zoom_scale=self._min_zoom_scale,
            max_zoom_scale=self._max_zoom_scale,
            has_focus_provider=self._focus_state_provider is not None,
            has_snapshot_callback=self._snapshot_callback is not None,
            coordinate_formatter=self._coordinate_export_service.format_point,
            roi_builder=self._build_roi_definition,
        )
        if apply_outcome:
            self._apply_interaction_outcome(outcome)
        return outcome

    def _apply_interaction_outcome(self, outcome: PreviewInteractionOutcome) -> None:
        if outcome.committed_roi is not None:
            self._set_active_roi(outcome.committed_roi)

        if outcome.snapshot_requested:
            self._save_preview_snapshot()

        if outcome.copy_text is not None:
            try:
                self._clipboard_copy_callback(outcome.copy_text)
            except Exception as exc:
                self._last_status_message = f"Copy failed: {exc}"
            else:
                self._last_status_message = outcome.copy_success_message

    def _build_viewport_mapping(
        self,
        frame_width: int,
        frame_height: int,
        viewport_width: int,
        viewport_height: int,
        display_scale: float,
        src_x: int = 0,
        src_y: int = 0,
    ):
        return self._geometry_service.build_viewport_mapping(
            frame_width,
            frame_height,
            viewport_width,
            viewport_height,
            display_scale,
            src_x=src_x,
            src_y=src_y,
        )

    def _map_viewport_point_to_source(self, x: int, y: int) -> tuple[int, int] | None:
        return self._geometry_service.map_viewport_point_to_source(self._last_viewport_mapping, x, y)

    def _map_source_point_to_viewport(self, point: tuple[int, int] | None) -> tuple[int, int] | None:
        return self._geometry_service.map_source_point_to_viewport(self._last_viewport_mapping, point)


__all__ = ["OpenCvPreviewWindow"]
