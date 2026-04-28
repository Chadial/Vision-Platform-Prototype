from __future__ import annotations

import argparse
from concurrent.futures import Future, ThreadPoolExecutor
import logging
from pathlib import Path
import sys
from time import monotonic
from types import SimpleNamespace
from typing import Sequence

from vision_platform.libraries.roi_core import roi_bounds
from vision_platform.models import ApplyConfigurationRequest, SaveSnapshotRequest, SetSaveDirectoryRequest
from vision_platform.models import StartRecordingRequest, StopRecordingRequest
from vision_platform.services.companion_contract_service import (
    build_companion_command_result,
    build_companion_status_snapshot,
    build_failed_companion_command_result,
)
from vision_platform.services.display_service import PreviewInteractionCommand, format_focus_score

from vision_platform.apps.local_shell.control_cli import main as run_local_shell_control_cli
from vision_platform.apps.local_shell.live_command_sync import (
    LocalShellLiveCommand,
    close_live_sync_session,
    read_pending_live_commands,
    to_serializable,
    write_live_command_result,
    write_live_status_snapshot,
)
from vision_platform.apps.local_shell.output_format_policy import choose_snapshot_file_extension
from vision_platform.apps.local_shell.preview_shell_state import PreviewShellPresenter, PreviewShellViewModel
from vision_platform.apps.local_shell.camera_settings_service import CameraSettingsService
from vision_platform.apps.camera_cli.camera_configuration_profiles import normalize_camera_class_name
from vision_platform.apps.local_shell.startup import (
    LocalShellLaunchOptions,
    LocalShellSession,
    build_local_shell_session,
)

try:
    import wx
except ImportError as exc:  # pragma: no cover - installation is validated separately
    raise RuntimeError("wxPython is not installed in the project environment.") from exc


_WX_RECORDING_FILE_EXTENSIONS = (".bmp", ".png", ".tiff", ".raw")
_WX_CAMERA_PIXEL_FORMATS = ("<unchanged>", "Mono8", "Mono10", "Mono12", "Mono16", "Rgb8", "Rgb16")


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


class PreviewCanvas(wx.Panel):
    def __init__(self, parent: wx.Window, presenter: PreviewShellPresenter, refresh_callback) -> None:
        super().__init__(parent, size=(640, 480))
        self._presenter = presenter
        self._refresh_callback = refresh_callback
        self._view_model: PreviewShellViewModel | None = None
        self._bitmap: wx.Bitmap | None = None
        self._bitmap_rgb_buffer: bytearray | None = None
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self._on_left_up)
        self.Bind(wx.EVT_MIDDLE_DOWN, self._on_middle_down)
        self.Bind(wx.EVT_MIDDLE_UP, self._on_middle_up)
        self.Bind(wx.EVT_MOTION, self._on_motion)
        self.Bind(wx.EVT_MOUSEWHEEL, self._on_mouse_wheel)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave_window)

    def update_view(self, view_model: PreviewShellViewModel) -> None:
        self._view_model = view_model
        rgb_buffer = view_model.image.to_rgb_buffer()
        if (
            self._bitmap is None
            or self._bitmap.GetWidth() != view_model.image.width
            or self._bitmap.GetHeight() != view_model.image.height
        ):
            self._bitmap_rgb_buffer = rgb_buffer
            self._bitmap = wx.Bitmap.FromBuffer(
                view_model.image.width,
                view_model.image.height,
                self._bitmap_rgb_buffer,
            )
        else:
            assert self._bitmap is not None
            self._bitmap_rgb_buffer = rgb_buffer
            self._bitmap.CopyFromBuffer(self._bitmap_rgb_buffer)
        self.Refresh(False)

    def _on_paint(self, event) -> None:
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBackground(wx.Brush(wx.Colour(20, 20, 20)))
        dc.Clear()
        if self._bitmap is None or self._view_model is None:
            return
        dc.DrawBitmap(self._bitmap, 0, 0)
        self._draw_overlays(dc, self._view_model)

    def _draw_overlays(self, dc: wx.DC, view_model: PreviewShellViewModel) -> None:
        mapping = view_model.viewport_mapping
        if view_model.overlay_model.show_viewport_outline:
            dc.SetPen(wx.Pen(wx.Colour(180, 180, 180), width=1))
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.DrawRectangle(0, 0, max(1, mapping.copy_width), max(1, mapping.copy_height))

        crosshair_point = view_model.overlay_model.crosshair_point
        if crosshair_point is not None:
            viewport_point = _map_source_point_to_viewport(mapping, crosshair_point)
            if viewport_point is not None:
                dc.SetPen(wx.Pen(wx.Colour(255, 255, 0), width=1))
                dc.DrawLine(viewport_point[0] - 8, viewport_point[1], viewport_point[0] + 8, viewport_point[1])
                dc.DrawLine(viewport_point[0], viewport_point[1] - 8, viewport_point[0], viewport_point[1] + 8)

        focus_anchor_point = view_model.overlay_model.focus_anchor_point
        focus_label = view_model.overlay_model.focus_label
        if focus_anchor_point is not None and focus_label:
            viewport_point = _map_source_point_to_viewport(mapping, focus_anchor_point)
            if viewport_point is not None:
                self._draw_focus_overlay(dc, viewport_point, focus_label)

        for roi, colour in (
            (view_model.overlay_model.draft_roi, wx.Colour(0, 200, 255)),
            (view_model.overlay_model.active_roi, _resolve_active_roi_colour(view_model.overlay_model.active_roi_emphasis)),
        ):
            if roi is None:
                continue
            bounds = roi_bounds(roi)
            if bounds is None:
                continue
            top_left = _map_source_point_to_viewport(mapping, (int(round(bounds[0])), int(round(bounds[1]))))
            bottom_right = _map_source_point_to_viewport(mapping, (int(round(bounds[2])), int(round(bounds[3]))))
            if top_left is None or bottom_right is None:
                continue
            left = min(top_left[0], bottom_right[0])
            top = min(top_left[1], bottom_right[1])
            right = max(top_left[0], bottom_right[0])
            bottom = max(top_left[1], bottom_right[1])
            dc.SetPen(wx.Pen(colour, width=2))
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            if roi.shape == "ellipse":
                dc.DrawEllipse(left, top, max(1, right - left), max(1, bottom - top))
            else:
                dc.DrawRectangle(left, top, max(1, right - left), max(1, bottom - top))
        self._draw_anchor_handles(dc, view_model)

    @staticmethod
    def _draw_anchor_handles(dc: wx.DC, view_model: PreviewShellViewModel) -> None:
        for handle in view_model.overlay_model.anchor_handles:
            viewport_point = _map_source_point_to_viewport(view_model.viewport_mapping, handle.point)
            if viewport_point is None:
                continue
            if handle.is_active:
                colour = wx.Colour(255, 140, 0)
            elif handle.is_hovered:
                colour = wx.Colour(255, 255, 255)
            else:
                colour = wx.Colour(0, 255, 0)
            dc.SetPen(wx.Pen(colour, width=2))
            dc.SetBrush(wx.Brush(colour))
            dc.DrawRectangle(viewport_point[0] - 4, viewport_point[1] - 4, 8, 8)

    @staticmethod
    def _draw_focus_overlay(dc: wx.DC, viewport_point: tuple[int, int], label: str) -> None:
        dc.SetPen(wx.Pen(wx.Colour(255, 128, 0), width=1))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawCircle(viewport_point[0], viewport_point[1], 6)
        dc.DrawLine(viewport_point[0] - 10, viewport_point[1], viewport_point[0] + 10, viewport_point[1])
        dc.DrawLine(viewport_point[0], viewport_point[1] - 10, viewport_point[0], viewport_point[1] + 10)
        text_width, text_height = dc.GetTextExtent(label)
        left = viewport_point[0] + 12
        top = max(0, viewport_point[1] - text_height - 8)
        dc.SetPen(wx.Pen(wx.Colour(255, 128, 0), width=1))
        dc.SetBrush(wx.Brush(wx.Colour(30, 30, 30)))
        dc.DrawRectangle(left, top, text_width + 10, text_height + 6)
        dc.SetTextForeground(wx.Colour(255, 220, 160))
        dc.DrawText(label, left + 5, top + 3)

    def _on_left_down(self, event) -> None:
        self._presenter.handle_canvas_click(event.GetX(), event.GetY())
        self._refresh_callback(interactive=True)

    def _on_left_up(self, event) -> None:
        self._presenter.handle_left_release(event.GetX(), event.GetY(), shift_down=event.ShiftDown())
        self._refresh_callback(interactive=True)

    def _on_middle_down(self, event) -> None:
        self._presenter.handle_pan_start(event.GetX(), event.GetY())
        self._refresh_callback(interactive=True)

    def _on_middle_up(self, event) -> None:
        self._presenter.handle_pan_stop()
        self._refresh_callback(interactive=True)

    def _on_motion(self, event) -> None:
        self._presenter.handle_pointer_move(
            event.GetX(),
            event.GetY(),
            left_button_down=event.LeftIsDown(),
            shift_down=event.ShiftDown(),
        )
        if event.MiddleIsDown():
            self._presenter.handle_pan_move(event.GetX(), event.GetY())
        self._refresh_callback(interactive=True)

    def _on_mouse_wheel(self, event) -> None:
        self._presenter.handle_mouse_wheel(event.GetX(), event.GetY(), event.GetWheelRotation())
        self._refresh_callback(interactive=True)

    def _on_leave_window(self, event) -> None:
        self._presenter.clear_hovered_anchor()
        self._refresh_callback(interactive=True)
        event.Skip()


class WxLocalPreviewShell(wx.Frame):
    _STATUS_REFRESH_INTERVAL_SECONDS = 0.5
    _FOCUS_REFRESH_INTERVAL_SECONDS = 0.5
    _INTERACTIVE_RENDER_INTERVAL_SECONDS = 1.0 / 30.0
    _TRANSIENT_STATUS_TTL_SECONDS = 2.5

    def __init__(
        self,
        *,
        session: LocalShellSession,
        poll_interval_seconds: float,
    ) -> None:
        super().__init__(None, title="Vision Platform wx Shell", size=(920, 720))
        self._session = session
        self._subsystem = session.subsystem
        self._focus_preview_service = session.focus_preview_service
        self._camera_settings_service = CameraSettingsService()
        self._subsystem.stream_service.start_preview()
        self._presenter = PreviewShellPresenter(roi_state_service=self._subsystem.stream_service.get_roi_state_service())
        self._timer = wx.Timer(self)
        self._status_lines: list[str] = []
        self._is_closed = False
        self._transient_status_message: str | None = None
        self._transient_status_deadline = 0.0
        self._cached_status = None
        self._last_status_refresh_time = 0.0
        self._cached_focus_state = None
        self._last_focus_refresh_time = 0.0
        self._focus_refresh_future: Future | None = None
        self._focus_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="WxShellFocus")
        self._last_render_time = 0.0
        self._last_ui_refresh_sample_time: float | None = None
        self._ui_refresh_fps: float | None = None
        self._refresh_scheduled = False
        self._recording_active_frame_limit: int | None = None
        self._recording_target_frame_rate_value: float | None = None
        self._recording_last_summary: str | None = None
        self._recording_last_file_stem: str | None = None
        self._recording_last_save_directory: Path | None = None
        self._recording_last_stop_reason: str | None = None
        self._recording_last_error: str | None = None
        self._snapshot_last_saved_path: Path | None = None
        self._snapshot_last_error: str | None = None
        self._failure_reflection: dict[str, object | None] | None = None
        self._recording_file_stem = "wx_recording"
        self._recording_file_extension = ".bmp"
        self._live_sync_processed_count = 0
        # Focus starts hidden to avoid heavy per-frame computation by default.
        self._presenter.state.interaction_state.focus_status_visible = False

        panel = wx.Panel(self)
        root_sizer = wx.BoxSizer(wx.VERTICAL)
        controls = wx.BoxSizer(wx.HORIZONTAL)
        self._canvas = PreviewCanvas(panel, self._presenter, self.request_refresh)
        self._status = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_NONE)

        self._add_button(panel, controls, "Snapshot", self._on_snapshot)
        self._add_button(panel, controls, "Zoom In", lambda event: self._run_action("zoom_in"))
        self._add_button(panel, controls, "Zoom Out", lambda event: self._run_action("zoom_out"))
        self._add_button(panel, controls, "Fit", lambda event: self._run_action("enable_fit"))
        self._add_button(panel, controls, "Crosshair", lambda event: self._run_action("toggle_crosshair"))
        self._add_button(panel, controls, "Focus", lambda event: self._run_action("toggle_focus"))
        self._add_button(panel, controls, "Rect ROI", lambda event: self._run_roi_toggle("rectangle"))
        self._add_button(panel, controls, "Ellipse ROI", lambda event: self._run_roi_toggle("ellipse"))

        root_sizer.Add(controls, 0, wx.EXPAND | wx.ALL, 8)
        recording_controls = wx.BoxSizer(wx.HORIZONTAL)
        self._add_label(panel, recording_controls, "Max Frames")
        self._recording_max_frames = wx.TextCtrl(panel, value="0", size=(72, -1))
        recording_controls.Add(self._recording_max_frames, 0, wx.RIGHT, 8)
        self._add_label(panel, recording_controls, "Recording FPS")
        self._recording_target_frame_rate_input = wx.TextCtrl(panel, value="", size=(72, -1))
        recording_controls.Add(self._recording_target_frame_rate_input, 0, wx.RIGHT, 8)
        self._start_recording_button = wx.Button(panel, label="Start Recording")
        self._start_recording_button.Bind(wx.EVT_BUTTON, self._on_start_recording)
        recording_controls.Add(self._start_recording_button, 0, wx.RIGHT, 6)
        self._stop_recording_button = wx.Button(panel, label="Stop Recording")
        self._stop_recording_button.Bind(wx.EVT_BUTTON, self._on_stop_recording)
        recording_controls.Add(self._stop_recording_button, 0, wx.RIGHT, 6)
        root_sizer.Add(recording_controls, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        root_sizer.Add(self._canvas, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        root_sizer.Add(self._status, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        panel.SetSizer(root_sizer)
        self.SetMenuBar(self._build_menu_bar())
        self.SetAcceleratorTable(self._build_accelerator_table())

        self.Bind(wx.EVT_TIMER, self._on_timer, self._timer)
        self.Bind(wx.EVT_CLOSE, self._on_close)
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)
        self._timer.Start(max(33, int(poll_interval_seconds * 1000)))
        self.request_refresh()

    def request_refresh(self, *, interactive: bool = False) -> None:
        now = monotonic()
        if interactive and now - self._last_render_time < self._INTERACTIVE_RENDER_INTERVAL_SECONDS:
            if not self._refresh_scheduled:
                self._refresh_scheduled = True
                wx.CallLater(
                    max(1, int(self._INTERACTIVE_RENDER_INTERVAL_SECONDS * 1000)),
                    self._run_scheduled_refresh,
                )
            return
        frame = self._subsystem.stream_service.get_latest_frame()
        if frame is None:
            return
        self._refresh_scheduled = False
        self._last_render_time = now
        self._update_ui_refresh_rate(now)
        self._consume_interaction_status_message()
        self._sync_transient_status_message(now)
        focus_state = self._get_focus_state()
        canvas_size = self._canvas.GetClientSize()
        view_model = self._presenter.build_view(
            frame,
            viewport_width=max(1, canvas_size.GetWidth()),
            viewport_height=max(1, canvas_size.GetHeight()),
            fps=self._ui_refresh_fps,
            focus_state=focus_state,
            has_focus_toggle=self._focus_preview_service is not None,
        )
        self._canvas.update_view(view_model)
        status = self._get_status()
        prefix = self._build_status_prefix(status)
        focus_summary = self._build_focus_summary(focus_state)
        if focus_summary is not None:
            prefix.append(f"focus={focus_summary}")
        recording_summary = self._build_recording_summary(status)
        if recording_summary is not None:
            prefix.append(f"recording={recording_summary}")
        self._status_lines = [" | ".join(prefix)] + view_model.status_lines
        status_text = "\n".join(self._status_lines)
        if self._status.GetValue() != status_text:
            self._status.ChangeValue(status_text)
        self._update_recording_controls(status)
        self._update_menu_state(status)
        self._publish_live_status_snapshot(status, focus_summary=focus_summary, recording_summary=recording_summary)

    def _on_timer(self, event) -> None:
        self._poll_live_commands()
        self.request_refresh()

    def _on_snapshot(self, event) -> None:
        try:
            result = self._subsystem.command_controller.save_snapshot(
                SaveSnapshotRequest(
                    file_stem="wx_shell_snapshot",
                    file_extension=choose_snapshot_file_extension(
                        pixel_format=self._get_current_pixel_format(),
                    ),
                )
            )
        except Exception as exc:
            self._snapshot_last_error = str(exc)
            self._set_failure_reflection(
                source="snapshot",
                action="save_snapshot",
                message=self._snapshot_last_error,
                external=False,
            )
            self._set_transient_status_message(self._format_snapshot_failure_message(self._snapshot_last_error))
            self.request_refresh()
            return
        self._cached_status = None
        self._snapshot_last_saved_path = result.saved_path
        self._snapshot_last_error = None
        self._clear_failure_reflection_for_source("snapshot")
        self._set_transient_status_message(
            self._format_snapshot_saved_message(result.saved_path)
        )
        self.request_refresh()

    def _run_action(self, action: str) -> None:
        self._presenter.apply_command(
            PreviewInteractionCommand(action=action),
            has_focus_provider=self._focus_preview_service is not None,
        )
        if action == "toggle_focus":
            self._cached_focus_state = None
            self._last_focus_refresh_time = 0.0
        self.request_refresh()

    def _run_roi_toggle(self, roi_mode: str) -> None:
        self._presenter.apply_command(PreviewInteractionCommand(action="toggle_roi_mode", roi_mode=roi_mode))
        self.request_refresh()

    def _on_start_recording(self, event) -> None:
        try:
            frame_limit = self._parse_optional_positive_int(self._recording_max_frames.GetValue())
            target_frame_rate = self._parse_optional_positive_float(self._recording_target_frame_rate_input.GetValue())
            save_directory = self._get_recording_save_directory()
            if save_directory is None:
                self._recording_last_error = "no save directory configured"
                self._set_failure_reflection(
                    source="recording",
                    action="start_recording",
                    message=self._recording_last_error,
                    external=False,
                )
                self._set_transient_status_message(self._format_recording_failure_message("start", self._recording_last_error))
                self.request_refresh()
                return
            result = self._session.subsystem.command_controller.start_recording(
                StartRecordingRequest(
                    file_stem=self._recording_file_stem,
                    file_extension=choose_snapshot_file_extension(
                        pixel_format=self._get_current_pixel_format(),
                        requested_extension=self._recording_file_extension,
                    ),
                    save_directory=save_directory,
                    max_frame_count=frame_limit,
                    target_frame_rate=target_frame_rate,
                    camera_id=self._session.resolved_camera_id,
                    configuration_profile_id=self._session.configuration_profile_id,
                    configuration_profile_camera_class=self._session.configuration_profile_camera_class,
                )
            )
        except Exception as exc:
            self._recording_last_error = str(exc)
            self._set_failure_reflection(
                source="recording",
                action="start_recording",
                message=self._recording_last_error,
                external=False,
            )
            self._set_transient_status_message(self._format_recording_failure_message("start", self._recording_last_error))
            self.request_refresh()
            return
        self._recording_active_frame_limit = frame_limit
        self._recording_target_frame_rate_value = target_frame_rate
        self._recording_last_summary = None
        self._recording_last_file_stem = result.status.active_file_stem or self._recording_file_stem
        self._recording_last_save_directory = save_directory
        self._recording_last_stop_reason = None
        self._recording_last_error = None
        self._clear_failure_reflection_for_source("recording")
        self._cached_status = None
        self._last_status_refresh_time = 0.0
        self._set_transient_status_message(self._format_recording_started_message(file_stem=self._recording_last_file_stem, save_directory=save_directory))
        self.request_refresh()

    def _on_stop_recording(self, event) -> None:
        try:
            result = self._session.subsystem.command_controller.stop_recording(
                StopRecordingRequest(reason="wx_shell_button")
            )
        except Exception as exc:
            self._recording_last_error = str(exc)
            self._set_failure_reflection(
                source="recording",
                action="stop_recording",
                message=self._recording_last_error,
                external=False,
            )
            self._set_transient_status_message(self._format_recording_failure_message("stop", self._recording_last_error))
            self.request_refresh()
            return
        self._recording_last_summary = self._format_recording_summary(
            frames_written=result.status.frames_written,
            frame_limit=self._recording_active_frame_limit,
        )
        self._recording_last_stop_reason = result.stop_reason
        self._recording_last_error = None
        self._recording_active_frame_limit = None
        self._clear_failure_reflection_for_source("recording")
        self._set_transient_status_message(
            self._format_recording_stopped_message(
                frames_written=result.status.frames_written,
                recording_summary=self._recording_last_summary,
                stop_reason=result.stop_reason,
                save_directory=self._recording_last_save_directory,
            )
        )
        self.request_refresh()

    def _on_close(self, event) -> None:
        self._shutdown_subsystem()
        event.Skip()

    def _on_char_hook(self, event) -> None:
        if not self._should_process_global_shortcuts():
            event.Skip()
            return
        if _is_copy_shortcut(event):
            self._copy_selected_point()
            self.request_refresh()
            return
        key_code = event.GetKeyCode()
        if key_code in (ord("i"), ord("I")):
            self._run_action("zoom_in")
            return
        if key_code in (ord("o"), ord("O")):
            self._run_action("zoom_out")
            return
        if key_code in (ord("f"), ord("F")):
            self._run_action("enable_fit")
            return
        if key_code in (ord("x"), ord("X")):
            self._run_action("toggle_crosshair")
            return
        if key_code in (ord("y"), ord("Y")):
            self._run_action("toggle_focus")
            return
        if key_code in (ord("r"), ord("R")):
            self._run_roi_toggle("rectangle")
            return
        if key_code in (ord("e"), ord("E")):
            self._run_roi_toggle("ellipse")
            return
        if key_code in (ord("+"), ord("=")):
            self._on_snapshot(event)
            return
        if key_code == wx.WXK_ESCAPE and self._presenter.cancel_active_drag():
            self.request_refresh()
            return
        event.Skip()

    def _should_process_global_shortcuts(self) -> bool:
        focused_window = wx.Window.FindFocus()
        if focused_window is None:
            return True
        if focused_window is self._canvas:
            return True
        if isinstance(focused_window, (wx.TextCtrl, wx.Choice)):
            return False
        return True

    def _build_menu_bar(self) -> wx.MenuBar:
        menu_bar = wx.MenuBar()

        file_menu = wx.Menu()
        self._menu_snapshot = file_menu.Append(
            wx.ID_ANY,
            "Snapshot\tCtrl+P",
            "Save the current preview frame.",
        )
        self.Bind(wx.EVT_MENU, self._on_snapshot, self._menu_snapshot)
        self._menu_set_save_directory = file_menu.Append(
            wx.ID_ANY,
            "Set Save Directory...\tCtrl+Shift+S",
            "Choose the base directory for snapshots and recordings.",
        )
        self.Bind(wx.EVT_MENU, self._on_menu_set_save_directory, self._menu_set_save_directory)
        file_menu.AppendSeparator()
        self._menu_exit = file_menu.Append(wx.ID_ANY, "Exit\tCtrl+Q", "Close the local shell.")
        self.Bind(wx.EVT_MENU, lambda _event: self.Close(), self._menu_exit)
        menu_bar.Append(file_menu, "&File")

        camera_menu = wx.Menu()
        self._menu_camera_settings = camera_menu.Append(
            wx.ID_ANY,
            "Camera Settings...\tCtrl+Shift+C",
            "Edit the camera configuration properties through the shared configuration request path.",
        )
        self.Bind(wx.EVT_MENU, self._on_menu_camera_settings, self._menu_camera_settings)
        menu_bar.Append(camera_menu, "&Camera")

        view_menu = wx.Menu()
        self._menu_zoom_in = view_menu.Append(wx.ID_ANY, "Zoom In\tI", "Zoom in on the preview.")
        self.Bind(wx.EVT_MENU, lambda _event: self._run_action("zoom_in"), self._menu_zoom_in)
        self._menu_zoom_out = view_menu.Append(wx.ID_ANY, "Zoom Out\tO", "Zoom out on the preview.")
        self.Bind(wx.EVT_MENU, lambda _event: self._run_action("zoom_out"), self._menu_zoom_out)
        self._menu_fit = view_menu.Append(wx.ID_ANY, "Fit\tF", "Return the preview to fit-to-window mode.")
        self.Bind(wx.EVT_MENU, lambda _event: self._run_action("enable_fit"), self._menu_fit)
        view_menu.AppendSeparator()
        self._menu_crosshair = view_menu.Append(wx.ID_ANY, "Crosshair\tX", "Toggle the crosshair overlay.")
        self.Bind(wx.EVT_MENU, lambda _event: self._run_action("toggle_crosshair"), self._menu_crosshair)
        self._menu_focus = view_menu.Append(wx.ID_ANY, "Focus\tY", "Toggle the focus overlay and status.")
        self.Bind(wx.EVT_MENU, lambda _event: self._run_action("toggle_focus"), self._menu_focus)
        menu_bar.Append(view_menu, "&View")

        roi_menu = wx.Menu()
        self._menu_rect_roi = roi_menu.Append(wx.ID_ANY, "Rectangle ROI\tR", "Toggle rectangle ROI entry.")
        self.Bind(wx.EVT_MENU, lambda _event: self._run_roi_toggle("rectangle"), self._menu_rect_roi)
        self._menu_ellipse_roi = roi_menu.Append(wx.ID_ANY, "Ellipse ROI\tE", "Toggle ellipse ROI entry.")
        self.Bind(wx.EVT_MENU, lambda _event: self._run_roi_toggle("ellipse"), self._menu_ellipse_roi)
        roi_menu.AppendSeparator()
        self._menu_copy_point = roi_menu.Append(
            wx.ID_ANY,
            "Copy Selected Point\tCtrl+C",
            "Copy the current selected point to the clipboard.",
        )
        self.Bind(wx.EVT_MENU, lambda _event: self._copy_selected_point(), self._menu_copy_point)
        self._menu_cancel_drag = roi_menu.Append(
            wx.ID_ANY,
            "Cancel Active Drag\tEsc",
            "Cancel the current point or ROI drag.",
        )
        self.Bind(wx.EVT_MENU, lambda _event: self._cancel_active_drag(), self._menu_cancel_drag)
        menu_bar.Append(roi_menu, "&ROI")

        settings_menu = wx.Menu()
        self._menu_recording_settings = settings_menu.Append(
            wx.ID_ANY,
            "Recording Settings...\tCtrl+R",
            "Edit bounded recording settings used by Start Recording.",
        )
        self.Bind(wx.EVT_MENU, self._on_menu_recording_settings, self._menu_recording_settings)
        self._menu_start_recording = settings_menu.Append(
            wx.ID_ANY,
            "Start Recording\tCtrl+Enter",
            "Start bounded recording with the current settings.",
        )
        self.Bind(wx.EVT_MENU, self._on_start_recording, self._menu_start_recording)
        self._menu_stop_recording = settings_menu.Append(
            wx.ID_ANY,
            "Stop Recording\tCtrl+Shift+Enter",
            "Stop the current recording run.",
        )
        self.Bind(wx.EVT_MENU, self._on_stop_recording, self._menu_stop_recording)
        menu_bar.Append(settings_menu, "&Recording")

        help_menu = wx.Menu()
        self._menu_shortcuts = help_menu.Append(
            wx.ID_ANY,
            "Keyboard Shortcuts...\tF1",
            "Show the current keyboard shortcut map.",
        )
        self.Bind(wx.EVT_MENU, self._on_menu_shortcut_reference, self._menu_shortcuts)
        menu_bar.Append(help_menu, "&Help")

        return menu_bar

    def _build_accelerator_table(self) -> wx.AcceleratorTable:
        entries = [
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord("1"), self._menu_zoom_in.GetId()),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord("2"), self._menu_zoom_out.GetId()),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord("3"), self._menu_fit.GetId()),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord("P"), self._menu_snapshot.GetId()),
            wx.AcceleratorEntry(wx.ACCEL_CTRL | wx.ACCEL_SHIFT, ord("S"), self._menu_set_save_directory.GetId()),
            wx.AcceleratorEntry(wx.ACCEL_CTRL | wx.ACCEL_SHIFT, ord("C"), self._menu_camera_settings.GetId()),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord("R"), self._menu_recording_settings.GetId()),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, wx.WXK_RETURN, self._menu_start_recording.GetId()),
            wx.AcceleratorEntry(wx.ACCEL_CTRL | wx.ACCEL_SHIFT, wx.WXK_RETURN, self._menu_stop_recording.GetId()),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord("Q"), self._menu_exit.GetId()),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F1, self._menu_shortcuts.GetId()),
        ]
        return wx.AcceleratorTable(entries)

    def _on_menu_camera_settings(self, event) -> None:
        status = self._get_status()
        capability_profile = self._subsystem.camera_service.get_capability_profile()
        camera_class = getattr(self._session, "configuration_profile_camera_class", None)
        status_camera = getattr(status, "camera", None)
        if camera_class is None and status_camera is not None and getattr(status_camera, "camera_model", None):
            camera_class = normalize_camera_class_name(status_camera.camera_model)
        defaults = self._camera_settings_service.build_initial_request(
            current_configuration=status.configuration,
            profile_id=getattr(self._session, "configuration_profile_id", None),
            camera_class=camera_class,
            capability_profile=capability_profile,
        )
        field_hints = self._camera_settings_service.build_field_hints(capability_profile)
        dialog = _CameraSettingsDialog(
            self,
            exposure_time_us=self._format_optional_value(defaults.exposure_time_us),
            gain=self._format_optional_value(defaults.gain),
            pixel_format=defaults.pixel_format or "",
            acquisition_frame_rate=self._format_optional_value(defaults.acquisition_frame_rate),
            roi_offset_x=self._format_optional_value(defaults.roi_offset_x),
            roi_offset_y=self._format_optional_value(defaults.roi_offset_y),
            roi_width=self._format_optional_value(defaults.roi_width),
            roi_height=self._format_optional_value(defaults.roi_height),
            field_hints={field_name: hint.tooltip for field_name, hint in field_hints.items() if hint.tooltip},
        )
        try:
            if dialog.ShowModal() != wx.ID_OK:
                return
            request = self._build_camera_settings_request(**dialog.get_values())
            request = self._camera_settings_service.normalize_request(request, capability_profile)
            self._session.subsystem.command_controller.apply_configuration(request)
            self._cached_status = None
            self._last_status_refresh_time = 0.0
            self._cached_focus_state = None
            self._last_focus_refresh_time = 0.0
            self._clear_failure_reflection_for_source("setup")
            self._set_transient_status_message("Camera settings updated")
            self.request_refresh()
        except Exception as exc:
            self._set_failure_reflection(
                source="setup",
                action="apply_configuration",
                message=str(exc),
                external=False,
            )
            self._set_transient_status_message(f"Camera settings failed: {exc}")
            self.request_refresh()
        finally:
            dialog.Destroy()

    def _on_menu_shortcut_reference(self, event) -> None:
        wx.MessageBox(
            self._build_shortcut_reference_text(),
            "Keyboard Shortcuts",
            wx.OK | wx.ICON_INFORMATION,
            self,
        )

    def _cancel_active_drag(self) -> None:
        if self._presenter.cancel_active_drag():
            self.request_refresh()

    def _on_menu_set_save_directory(self, event) -> None:
        current_directory = self._get_recording_save_directory()
        default_path = str(current_directory) if current_directory is not None else str(Path.cwd())
        dialog = wx.DirDialog(
            self,
            "Select save directory",
            defaultPath=default_path,
            style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST,
        )
        try:
            if dialog.ShowModal() != wx.ID_OK:
                return
            selected_path = Path(dialog.GetPath())
            result = self._session.subsystem.command_controller.set_save_directory(
                SetSaveDirectoryRequest(
                    base_directory=selected_path,
                    mode="append",
                )
            )
            self._session.selected_save_directory = result.selected_directory
            self._cached_status = None
            self._last_status_refresh_time = 0.0
            self._clear_failure_reflection_for_source("setup")
            self._set_transient_status_message(f"Save directory: {result.selected_directory}")
            self.request_refresh()
        except Exception as exc:
            self._set_failure_reflection(
                source="setup",
                action="set_save_directory",
                message=str(exc),
                external=False,
            )
            self._set_transient_status_message(f"Save directory failed: {exc}")
            self.request_refresh()
        finally:
            dialog.Destroy()

    def _on_menu_recording_settings(self, event) -> None:
        dialog = _RecordingSettingsDialog(
            self,
            file_stem=self._recording_file_stem,
            file_extension=self._recording_file_extension,
            max_frames=self._recording_max_frames.GetValue(),
            recording_fps=self._recording_target_frame_rate_input.GetValue(),
        )
        try:
            if dialog.ShowModal() != wx.ID_OK:
                return
            values = dialog.get_values()
            self._apply_recording_settings_values(
                file_stem=values["file_stem"],
                file_extension=values["file_extension"],
                max_frames=values["max_frames"],
                recording_fps=values["recording_fps"],
            )
            self._set_transient_status_message("Recording settings updated")
            self.request_refresh()
        except Exception as exc:
            self._set_transient_status_message(f"Recording settings failed: {exc}")
            self.request_refresh()
        finally:
            dialog.Destroy()

    @staticmethod
    def _add_button(parent: wx.Window, sizer: wx.BoxSizer, label: str, handler) -> None:
        button = wx.Button(parent, label=label)
        button.Bind(wx.EVT_BUTTON, handler)
        sizer.Add(button, 0, wx.RIGHT, 6)

    def _shutdown_subsystem(self) -> None:
        if self._is_closed:
            return
        self._is_closed = True
        self._timer.Stop()
        try:
            if self._subsystem.stream_service.is_preview_running:
                self._subsystem.stream_service.stop_preview()
        finally:
            self._focus_executor.shutdown(wait=False, cancel_futures=True)
            self._subsystem.driver.shutdown()
            if self._session.live_sync_session is not None:
                close_live_sync_session(self._session.live_sync_session)

    def _get_status(self):
        now = monotonic()
        if self._cached_status is None or now - self._last_status_refresh_time >= self._STATUS_REFRESH_INTERVAL_SECONDS:
            self._cached_status = self._subsystem.command_controller.get_status()
            self._last_status_refresh_time = now
        return self._cached_status

    def _get_current_pixel_format(self) -> str | None:
        try:
            status = self._get_status()
        except AttributeError:
            return None
        configuration = getattr(status, "configuration", None)
        return getattr(configuration, "pixel_format", None)

    def _get_command_controller(self):
        session = getattr(self, "_session", None)
        subsystem = getattr(session, "subsystem", None)
        if subsystem is not None and getattr(subsystem, "command_controller", None) is not None:
            return subsystem.command_controller
        shell_subsystem = getattr(self, "_subsystem", None)
        if shell_subsystem is not None and getattr(shell_subsystem, "command_controller", None) is not None:
            return shell_subsystem.command_controller
        raise AttributeError("No command controller is available on the current wx shell instance.")

    @staticmethod
    def _add_label(parent: wx.Window, sizer: wx.BoxSizer, text: str) -> None:
        sizer.Add(wx.StaticText(parent, label=text), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)

    def _update_ui_refresh_rate(self, now: float) -> None:
        if self._last_ui_refresh_sample_time is None:
            self._last_ui_refresh_sample_time = now
            return
        delta = now - self._last_ui_refresh_sample_time
        self._last_ui_refresh_sample_time = now
        if delta <= 0:
            return
        sample_fps = 1.0 / delta
        if self._ui_refresh_fps is None:
            self._ui_refresh_fps = sample_fps
            return
        self._ui_refresh_fps = (self._ui_refresh_fps * 0.8) + (sample_fps * 0.2)

    def _get_focus_state(self):
        if self._focus_preview_service is None:
            return None
        if not self._presenter.state.interaction_state.focus_status_visible:
            self._cached_focus_state = None
            return None
        now = monotonic()
        if self._focus_refresh_future is not None and self._focus_refresh_future.done():
            try:
                self._cached_focus_state = self._focus_refresh_future.result()
            except Exception as exc:
                self._set_transient_status_message(f"Focus failed: {exc}")
                self._cached_focus_state = None
            finally:
                self._focus_refresh_future = None
        if now - self._last_focus_refresh_time < self._FOCUS_REFRESH_INTERVAL_SECONDS:
            return self._cached_focus_state
        self._last_focus_refresh_time = now
        if self._focus_refresh_future is None:
            roi = self._subsystem.stream_service.get_roi_state_service().get_active_roi()
            self._focus_refresh_future = self._focus_executor.submit(self._focus_preview_service.refresh_once, roi)
        return self._cached_focus_state

    def _copy_selected_point(self) -> None:
        outcome = self._presenter.apply_command(
            PreviewInteractionCommand(action="request_copy"),
            has_focus_provider=self._focus_preview_service is not None,
        )
        if outcome.copy_text is None:
            return
        try:
            _copy_text_to_clipboard(outcome.copy_text)
        except Exception as exc:
            self._set_transient_status_message(f"Copy failed: {exc}")
            return
        self._set_transient_status_message(outcome.copy_success_message or "Point copied")

    def _run_scheduled_refresh(self) -> None:
        self.request_refresh(interactive=False)

    def _set_transient_status_message(self, message: str) -> None:
        self._transient_status_message = message
        self._transient_status_deadline = monotonic() + self._TRANSIENT_STATUS_TTL_SECONDS
        self._presenter.state.interaction_state.last_status_message = message

    def _consume_interaction_status_message(self) -> None:
        message = self._presenter.state.interaction_state.last_status_message
        if not message:
            return
        self._transient_status_message = message
        self._transient_status_deadline = monotonic() + self._TRANSIENT_STATUS_TTL_SECONDS
        self._presenter.state.interaction_state.last_status_message = None

    def _sync_transient_status_message(self, now: float) -> None:
        if self._transient_status_message is None:
            self._presenter.state.interaction_state.last_status_message = None
            return
        if now >= self._transient_status_deadline:
            self._transient_status_message = None
            self._presenter.state.interaction_state.last_status_message = None
            return
        self._presenter.state.interaction_state.last_status_message = self._transient_status_message

    def _build_focus_summary(self, focus_state) -> str | None:
        if getattr(self, "_focus_preview_service", None) is None:
            return None
        if not self._presenter.state.interaction_state.focus_status_visible:
            return "hidden"
        if focus_state is None:
            return "waiting"
        if not focus_state.result.is_valid:
            return "invalid"
        return format_focus_score(focus_state.result.score)

    def _get_setup_focus_visibility(self) -> str:
        focus_service = getattr(self, "_focus_preview_service", None)
        if focus_service is None:
            return "unavailable"
        presenter = getattr(self, "_presenter", None)
        interaction_state = getattr(getattr(presenter, "state", None), "interaction_state", None)
        if interaction_state is None:
            return "hidden"
        return "visible" if bool(getattr(interaction_state, "focus_status_visible", False)) else "hidden"

    def _get_active_setup_roi(self):
        subsystem = getattr(self, "_subsystem", None)
        stream_service = getattr(subsystem, "stream_service", None)
        if stream_service is None:
            return None
        roi_state_service = getattr(stream_service, "get_roi_state_service", None)
        if roi_state_service is None:
            return None
        service = roi_state_service()
        if service is None:
            return None
        get_active_roi = getattr(service, "get_active_roi", None)
        if get_active_roi is None:
            return None
        return get_active_roi()

    def _get_active_setup_roi_shape(self) -> str | None:
        active_roi = self._get_active_setup_roi()
        if active_roi is None:
            return None
        return getattr(active_roi, "shape", None)

    def _build_setup_reflection(self, *, focus_summary: str | None, status) -> dict[str, object | None]:
        active_roi = self._get_active_setup_roi()
        active_roi_bounds = roi_bounds(active_roi) if active_roi is not None else None
        configuration_summary = self._format_camera_configuration_summary(getattr(status, "configuration", None))
        return {
            "phase": "ready",
            "focus_visibility": self._get_setup_focus_visibility(),
            "focus_summary": focus_summary,
            "roi_active": active_roi is not None,
            "roi_shape": getattr(active_roi, "shape", None) if active_roi is not None else None,
            "roi_bounds": None if active_roi_bounds is None else [int(round(value)) for value in active_roi_bounds],
            "configuration_summary": configuration_summary,
        }

    def _set_failure_reflection(self, *, source: str, action: str, message: str, external: bool) -> None:
        self._failure_reflection = {
            "phase": "failed",
            "source": source,
            "action": action,
            "message": message,
            "external": external,
        }

    def _clear_failure_reflection_for_source(self, source: str) -> None:
        current = getattr(self, "_failure_reflection", None)
        if current is not None and current.get("source") == source:
            self._failure_reflection = None

    def _build_failure_reflection(self) -> dict[str, object | None] | None:
        failure_reflection = getattr(self, "_failure_reflection", None)
        if failure_reflection is None:
            return None
        return dict(failure_reflection)

    def _build_status_prefix(self, status) -> list[str]:
        prefix = [
            f"source={self._session.source}",
            f"camera={'ready' if status.camera.is_initialized else 'offline'}",
            f"preview={'running' if self._subsystem.stream_service.is_preview_running else 'stopped'}",
        ]
        if self._session.resolved_camera_id is not None:
            prefix.append(f"camera_id={self._session.resolved_camera_id}")
        if status.camera.reported_acquisition_frame_rate is not None:
            prefix.append(f"camera_fps={status.camera.reported_acquisition_frame_rate:.1f}")
        else:
            prefix.append("camera_fps=n/a")
        if self._ui_refresh_fps is not None:
            prefix.append(f"ui_fps={self._ui_refresh_fps:.1f}")
        else:
            prefix.append("ui_fps=waiting")
        recording_target_frame_rate = getattr(self, "_recording_target_frame_rate_value", None)
        if isinstance(recording_target_frame_rate, (int, float)):
            prefix.append(f"recording_fps={float(recording_target_frame_rate):.1f}")
        elif recording_target_frame_rate is not None:
            prefix.append("recording_fps=cfg")
        elif getattr(status, "recording", None) is not None and status.recording.is_recording:
            prefix.append("recording_fps=auto")
        camera_configuration_summary = self._format_camera_configuration_summary(getattr(status, "configuration", None))
        if camera_configuration_summary is not None:
            prefix.append(f"config={camera_configuration_summary}")
        if status.default_save_directory is not None:
            prefix.append(f"save={status.default_save_directory}")
        setup_focus_visibility = self._get_setup_focus_visibility()
        if setup_focus_visibility != "unavailable":
            prefix.append(f"setup_focus={setup_focus_visibility}")
        setup_roi_shape = self._get_active_setup_roi_shape()
        if setup_roi_shape is not None:
            prefix.append(f"setup_roi={setup_roi_shape}")
        snapshot_file_name = self._get_snapshot_reflection_file_name()
        if snapshot_file_name is not None:
            prefix.append(f"snapshot_file={snapshot_file_name}")
        snapshot_save_directory = self._get_snapshot_reflection_save_directory()
        if snapshot_save_directory is not None:
            prefix.append(f"snapshot_save={snapshot_save_directory}")
        snapshot_phase = self._get_snapshot_reflection_phase()
        if snapshot_phase == "failed":
            prefix.append("snapshot_state=failed")
        recording_file_stem = self._get_recording_reflection_file_stem(status)
        if recording_file_stem is not None:
            prefix.append(f"recording_file={recording_file_stem}")
        recording_save_directory = self._get_recording_reflection_save_directory(status)
        if recording_save_directory is not None:
            prefix.append(f"recording_save={recording_save_directory}")
        recording_stop_category = self._get_recording_stop_category(status)
        if recording_stop_category is not None:
            prefix.append(f"recording_stop={recording_stop_category}")
        failure_reflection = self._build_failure_reflection()
        if failure_reflection is not None:
            prefix.append(f"failure={failure_reflection['source']}")
        if self._session.configuration_profile_id is not None:
            prefix.append(f"profile={self._session.configuration_profile_id}")
        return prefix

    def _build_recording_summary(self, status) -> str | None:
        if status.recording.is_recording:
            return self._format_recording_summary(
                frames_written=status.recording.frames_written,
                frame_limit=getattr(self, "_recording_active_frame_limit", None),
            )
        if (
            getattr(self, "_recording_active_frame_limit", None) is not None
            and status.recording.frames_written > 0
            and getattr(self, "_recording_last_summary", None) is None
        ):
            summary = self._format_recording_summary(
                frames_written=status.recording.frames_written,
                frame_limit=getattr(self, "_recording_active_frame_limit", None),
            )
            self._recording_last_summary = summary
            if getattr(self, "_recording_last_stop_reason", None) is None:
                self._recording_last_stop_reason = "max_frames_reached"
            self._recording_last_error = None
            if hasattr(self, "_presenter"):
                self._set_transient_status_message(
                    self._format_recording_stopped_message(
                        frames_written=status.recording.frames_written,
                        recording_summary=summary,
                        stop_reason=self._recording_last_stop_reason,
                        save_directory=getattr(self, "_recording_last_save_directory", None),
                    )
                )
            self._recording_active_frame_limit = None
            return summary
        if getattr(self, "_recording_last_summary", None) is not None:
            return self._recording_last_summary
        return None

    @staticmethod
    def _format_recording_summary(*, frames_written: int, frame_limit: int | None) -> str:
        if frame_limit is None:
            return f"{frames_written}/n"
        return f"{frames_written}/{frame_limit}"

    def _get_recording_reflection_file_stem(self, status) -> str | None:
        recording_status = getattr(status, "recording", None)
        active_file_stem = getattr(recording_status, "active_file_stem", None)
        if active_file_stem:
            return active_file_stem
        return getattr(self, "_recording_last_file_stem", None)

    def _get_recording_reflection_save_directory(self, status) -> str | None:
        recording_status = getattr(status, "recording", None)
        save_directory = getattr(recording_status, "save_directory", None)
        if save_directory is None:
            save_directory = getattr(self, "_recording_last_save_directory", None)
        if save_directory is None:
            return None
        return str(save_directory)

    def _get_recording_stop_category(self, status) -> str | None:
        recording_status = getattr(status, "recording", None)
        if bool(getattr(recording_status, "is_recording", False)):
            return None
        stop_reason = getattr(self, "_recording_last_stop_reason", None)
        last_error = self._get_recording_last_error(status)
        categorized = self._categorize_recording_stop_reason(stop_reason)
        if categorized is None and last_error is not None:
            return "failure_termination"
        return categorized

    @staticmethod
    def _categorize_recording_stop_reason(stop_reason: str | None) -> str | None:
        if stop_reason is None:
            return None
        if stop_reason in {"bounded_completion", "max_frames_reached"}:
            return "max_frames_reached"
        if stop_reason in {"post_failure_cleanup", "duplicate_cleanup"}:
            return "failure_termination"
        if stop_reason in {"wx_shell_button", "external_cli", "external_request", "operator_cancelled", "host_shutdown"}:
            return "host_stop"
        return stop_reason

    def _get_recording_last_error(self, status) -> str | None:
        recording_status = getattr(status, "recording", None)
        status_error = getattr(recording_status, "last_error", None)
        if status_error:
            return status_error
        return getattr(self, "_recording_last_error", None)

    @staticmethod
    def _format_snapshot_saved_message(saved_path: Path, *, external: bool = False) -> str:
        prefix = "External geometry snapshot saved" if external else "Geometry snapshot saved"
        return f"{prefix}: {saved_path.name} -> {saved_path.parent}"

    @staticmethod
    def _format_snapshot_failure_message(error: str, *, external: bool = False) -> str:
        prefix = "External geometry snapshot" if external else "Geometry snapshot"
        return f"{prefix} failed: {error}"

    def _get_snapshot_reflection_file_name(self) -> str | None:
        saved_path = getattr(self, "_snapshot_last_saved_path", None)
        if saved_path is None:
            return None
        return saved_path.name

    def _get_snapshot_reflection_save_directory(self) -> str | None:
        saved_path = getattr(self, "_snapshot_last_saved_path", None)
        if saved_path is None:
            return None
        return str(saved_path.parent)

    def _get_snapshot_reflection_phase(self) -> str:
        if getattr(self, "_snapshot_last_error", None) is not None:
            return "failed"
        if getattr(self, "_snapshot_last_saved_path", None) is not None:
            return "saved"
        return "idle"

    def _build_snapshot_reflection(self) -> dict[str, object | None]:
        return {
            "phase": self._get_snapshot_reflection_phase(),
            "file_name": self._get_snapshot_reflection_file_name(),
            "file_stem": None if getattr(self, "_snapshot_last_saved_path", None) is None else self._snapshot_last_saved_path.stem,
            "save_directory": self._get_snapshot_reflection_save_directory(),
            "last_error": getattr(self, "_snapshot_last_error", None),
        }

    @staticmethod
    def _build_save_directory_reflection(selected_directory: Path | None) -> dict[str, object | None]:
        return {
            "phase": "selected" if selected_directory is not None else "unset",
            "selected_directory": None if selected_directory is None else str(selected_directory),
        }

    def _build_live_command_reflection(
        self,
        *,
        command_name: str,
        status,
        focus_summary: str | None,
        recording_summary: str | None,
    ) -> tuple[str | None, dict[str, object | None] | None]:
        if command_name == "apply_configuration":
            return "setup", self._build_setup_reflection(focus_summary=focus_summary, status=status)
        if command_name == "set_save_directory":
            selected_directory = getattr(self._session, "selected_save_directory", None)
            return "save_directory", self._build_save_directory_reflection(selected_directory)
        if command_name == "save_snapshot":
            return "snapshot", self._build_snapshot_reflection()
        if command_name in {"start_recording", "stop_recording"}:
            return "recording", self._build_recording_reflection(status, recording_summary=recording_summary)
        return None, None

    def _build_live_command_result(
        self,
        *,
        command_name: str,
        result,
    ) -> dict:
        self._cached_status = None
        self._last_status_refresh_time = 0.0
        controller = self._get_command_controller()
        if hasattr(controller, "get_status"):
            status = controller.get_status()
        else:
            status = SimpleNamespace(
                camera=SimpleNamespace(is_initialized=False, reported_acquisition_frame_rate=None),
                default_save_directory=getattr(self._session, "selected_save_directory", None),
                configuration=None,
                recording=SimpleNamespace(
                    is_recording=command_name == "start_recording",
                    frames_written=0,
                    active_file_stem=getattr(self, "_recording_last_file_stem", None),
                    save_directory=getattr(self, "_recording_last_save_directory", None),
                    last_error=getattr(self, "_recording_last_error", None),
                ),
            )
        focus_summary = self._build_focus_summary(getattr(self, "_cached_focus_state", None))
        recording_summary = self._build_recording_summary(status)
        reflection_kind, reflection = self._build_live_command_reflection(
            command_name=command_name,
            status=status,
            focus_summary=focus_summary,
            recording_summary=recording_summary,
        )
        return build_companion_command_result(
            command_name=command_name,
            reflection_kind=reflection_kind,
            reflection=reflection,
            failure_reflection=self._build_failure_reflection(),
            result=to_serializable(result),
        )

    @staticmethod
    def _format_recording_started_message(*, file_stem: str | None, save_directory: Path | None, external: bool = False) -> str:
        prefix = "External recording run started" if external else "Recording run started"
        file_part = file_stem or "recording"
        if save_directory is None:
            return f"{prefix}: {file_part}"
        return f"{prefix}: {file_part} -> {save_directory}"

    def _format_recording_stopped_message(
        self,
        *,
        frames_written: int,
        recording_summary: str | None,
        stop_reason: str | None,
        save_directory: Path | None,
        external: bool = False,
    ) -> str:
        stop_category = self._categorize_recording_stop_reason(stop_reason)
        prefix = "External recording run" if external else "Recording run"
        if stop_category == "max_frames_reached":
            detail = f"completed (max frames): {recording_summary or frames_written}"
        elif stop_category == "failure_termination":
            detail = f"terminated after failure: {frames_written} frames"
        elif stop_category == "host_stop":
            detail = f"stopped (host stop): {frames_written} frames"
        else:
            detail = f"stopped: {frames_written} frames"
        if save_directory is None:
            return f"{prefix} {detail}"
        return f"{prefix} {detail} -> {save_directory}"

    @staticmethod
    def _format_recording_failure_message(action: str, error: str, *, external: bool = False) -> str:
        prefix = "External recording run" if external else "Recording run"
        return f"{prefix} {action} failed: {error}"

    def _build_recording_reflection(self, status, *, recording_summary: str | None) -> dict[str, object | None]:
        recording_status = getattr(status, "recording", None)
        save_directory = self._get_recording_reflection_save_directory(status)
        stop_reason = getattr(self, "_recording_last_stop_reason", None)
        is_recording = bool(getattr(recording_status, "is_recording", False))
        last_error = self._get_recording_last_error(status)
        if is_recording:
            stop_reason = None
        stop_category = self._categorize_recording_stop_reason(stop_reason)
        if stop_category is None and last_error is not None:
            stop_category = "failure_termination"
        return {
            "phase": "running" if is_recording else ("failed" if last_error is not None else "idle"),
            "summary": recording_summary,
            "file_stem": self._get_recording_reflection_file_stem(status),
            "save_directory": save_directory,
            "stop_reason": stop_reason,
            "stop_category": stop_category,
            "frames_written": getattr(recording_status, "frames_written", 0),
            "last_error": last_error,
        }

    def _update_recording_controls(self, status) -> None:
        if hasattr(self, "_start_recording_button"):
            self._start_recording_button.Enable(status.can_start_recording)
        if hasattr(self, "_stop_recording_button"):
            self._stop_recording_button.Enable(status.can_stop_recording)

    def _update_menu_state(self, status) -> None:
        menu_state = (
            ("_menu_snapshot", status.can_save_snapshot),
            ("_menu_camera_settings", True),
            ("_menu_start_recording", status.can_start_recording),
            ("_menu_stop_recording", status.can_stop_recording),
            ("_menu_recording_settings", True),
            ("_menu_set_save_directory", True),
            ("_menu_zoom_in", True),
            ("_menu_zoom_out", True),
            ("_menu_fit", True),
            ("_menu_crosshair", True),
            ("_menu_focus", True),
            ("_menu_rect_roi", True),
            ("_menu_ellipse_roi", True),
            ("_menu_copy_point", True),
            ("_menu_cancel_drag", True),
            ("_menu_shortcuts", True),
        )
        for attr_name, enabled in menu_state:
            menu_item = getattr(self, attr_name, None)
            if menu_item is not None:
                menu_item.Enable(enabled)

    @staticmethod
    def _format_camera_configuration_summary(configuration) -> str | None:
        if configuration is None:
            return None
        parts: list[str] = []
        if configuration.exposure_time_us is not None:
            parts.append(f"exp={configuration.exposure_time_us:g}us")
        if configuration.gain is not None:
            parts.append(f"gain={configuration.gain:g}")
        if configuration.pixel_format is not None:
            parts.append(f"fmt={configuration.pixel_format}")
        if configuration.acquisition_frame_rate is not None:
            parts.append(f"fps={configuration.acquisition_frame_rate:g}")
        roi_parts: list[str] = []
        if configuration.roi_offset_x is not None:
            roi_parts.append(f"x={configuration.roi_offset_x}")
        if configuration.roi_offset_y is not None:
            roi_parts.append(f"y={configuration.roi_offset_y}")
        if configuration.roi_width is not None:
            roi_parts.append(f"w={configuration.roi_width}")
        if configuration.roi_height is not None:
            roi_parts.append(f"h={configuration.roi_height}")
        if roi_parts:
            parts.append("roi=" + ",".join(roi_parts))
        if not parts:
            return None
        return " ".join(parts)

    @staticmethod
    def _build_shortcut_reference_text() -> str:
        return "\n".join(
            [
                "Preview:",
                "  Ctrl+1=zoom in  Ctrl+2=zoom out  Ctrl+3=fit",
                "  i=zoom in  o=zoom out  f=fit  x=crosshair  y=focus",
                "  r=rectangle ROI  e=ellipse ROI  Ctrl+C=copy point  Esc=cancel drag",
                "Menu:",
                "  Ctrl+P=snapshot  Ctrl+Shift+S=set save directory  Ctrl+Shift+C=camera settings",
                "  Ctrl+R=recording settings  Ctrl+Enter=start recording  Ctrl+Shift+Enter=stop recording  Ctrl+Q=exit",
            ]
        )

    def _build_camera_settings_request(
        self,
        *,
        exposure_time_us: str,
        gain: str,
        pixel_format: str,
        acquisition_frame_rate: str,
        roi_offset_x: str,
        roi_offset_y: str,
        roi_width: str,
        roi_height: str,
    ) -> ApplyConfigurationRequest:
        normalized_pixel_format = _normalize_wx_camera_pixel_format(pixel_format)
        return ApplyConfigurationRequest(
            exposure_time_us=self._parse_optional_float(exposure_time_us),
            gain=self._parse_optional_float(gain),
            pixel_format=normalized_pixel_format,
            acquisition_frame_rate=self._parse_optional_float(acquisition_frame_rate),
            roi_offset_x=self._parse_optional_int(roi_offset_x),
            roi_offset_y=self._parse_optional_int(roi_offset_y),
            roi_width=self._parse_optional_int(roi_width),
            roi_height=self._parse_optional_int(roi_height),
        )

    def _get_recording_save_directory(self) -> Path | None:
        status = self._get_status()
        if status.default_save_directory is not None:
            return status.default_save_directory
        return self._session.selected_save_directory

    @staticmethod
    def _parse_optional_int(value: str) -> int | None:
        stripped = value.strip()
        if not stripped:
            return None
        return int(stripped)

    @staticmethod
    def _parse_optional_float(value: str) -> float | None:
        stripped = value.strip()
        if not stripped:
            return None
        return float(stripped)

    @staticmethod
    def _format_optional_value(value) -> str:
        if value is None:
            return ""
        return f"{value:g}" if isinstance(value, float) else str(value)

    @staticmethod
    def _parse_optional_positive_int(value: str) -> int | None:
        stripped = value.strip()
        if not stripped:
            return None
        parsed = int(stripped)
        if parsed < 0:
            raise ValueError("value must be zero or greater")
        return None if parsed == 0 else parsed

    @staticmethod
    def _parse_optional_positive_float(value: str) -> float | None:
        stripped = value.strip()
        if not stripped:
            return None
        parsed = float(stripped)
        if parsed <= 0:
            raise ValueError("value must be positive")
        return parsed

    def _apply_recording_settings_values(
        self,
        *,
        file_stem: str,
        file_extension: str,
        max_frames: str,
        recording_fps: str,
    ) -> None:
        normalized_stem = file_stem.strip()
        if not normalized_stem:
            raise ValueError("file stem must not be empty")
        normalized_extension = _normalize_wx_recording_file_extension(file_extension)
        self._parse_optional_positive_int(max_frames)
        parsed_recording_fps = self._parse_optional_positive_float(recording_fps)
        self._recording_file_stem = normalized_stem
        self._recording_file_extension = normalized_extension
        self._recording_max_frames.ChangeValue(max_frames.strip())
        self._recording_target_frame_rate_input.ChangeValue(recording_fps.strip())
        self._recording_target_frame_rate_value = parsed_recording_fps

    def _poll_live_commands(self) -> None:
        live_sync_session = self._session.live_sync_session
        if live_sync_session is None:
            return
        commands, processed_count = read_pending_live_commands(
            live_sync_session,
            processed_count=self._live_sync_processed_count,
        )
        self._live_sync_processed_count = processed_count
        for command in commands:
            try:
                result = self._execute_live_command(command)
            except Exception as exc:
                self._cached_status = None
                self._last_status_refresh_time = 0.0
                write_live_command_result(
                    live_sync_session,
                    command_id=command.command_id,
                    success=False,
                    command_name=command.command_name,
                    result=build_failed_companion_command_result(
                        command_name=command.command_name,
                        failure_reflection=self._build_failure_reflection(),
                    ),
                    error=str(exc),
                )
                self._set_transient_status_message(f"External command failed: {command.command_name}")
                continue
            write_live_command_result(
                live_sync_session,
                command_id=command.command_id,
                success=True,
                command_name=command.command_name,
                result=result,
            )

    def _execute_live_command(self, command: LocalShellLiveCommand) -> dict:
        controller = self._session.subsystem.command_controller
        payload = command.payload

        if command.command_name == "apply_configuration":
            try:
                result = controller.apply_configuration(
                    ApplyConfigurationRequest(
                        exposure_time_us=payload.get("exposure_time_us"),
                        gain=payload.get("gain"),
                        pixel_format=payload.get("pixel_format"),
                        acquisition_frame_rate=payload.get("acquisition_frame_rate"),
                        roi_offset_x=payload.get("roi_offset_x"),
                        roi_offset_y=payload.get("roi_offset_y"),
                        roi_width=payload.get("roi_width"),
                        roi_height=payload.get("roi_height"),
                    )
                )
            except Exception as exc:
                self._set_failure_reflection(
                    source="setup",
                    action="apply_configuration",
                    message=str(exc),
                    external=True,
                )
                self._set_transient_status_message(f"External setup configuration failed: {exc}")
                raise
            self._cached_focus_state = None
            self._clear_failure_reflection_for_source("setup")
            self._set_transient_status_message("External setup configuration applied")
        elif command.command_name == "set_save_directory":
            try:
                result = controller.set_save_directory(
                    SetSaveDirectoryRequest(
                        base_directory=Path(payload["base_directory"]),
                        mode=payload.get("mode", "append"),
                        subdirectory_name=payload.get("subdirectory_name"),
                    )
                )
            except Exception as exc:
                self._set_failure_reflection(
                    source="setup",
                    action="set_save_directory",
                    message=str(exc),
                    external=True,
                )
                self._set_transient_status_message(f"External save directory failed: {exc}")
                raise
            self._session.selected_save_directory = result.selected_directory
            self._clear_failure_reflection_for_source("setup")
            self._set_transient_status_message(f"External save directory: {result.selected_directory}")
        elif command.command_name == "save_snapshot":
            try:
                result = controller.save_snapshot(
                    SaveSnapshotRequest(
                        file_stem=payload.get("file_stem", "wx_shell_snapshot"),
                        file_extension=choose_snapshot_file_extension(
                            pixel_format=self._get_current_pixel_format(),
                            requested_extension=payload.get("file_extension"),
                        ),
                        camera_id=self._session.resolved_camera_id,
                        configuration_profile_id=self._session.configuration_profile_id,
                        configuration_profile_camera_class=self._session.configuration_profile_camera_class,
                    )
                )
            except Exception as exc:
                self._snapshot_last_error = str(exc)
                self._set_failure_reflection(
                    source="snapshot",
                    action="save_snapshot",
                    message=self._snapshot_last_error,
                    external=True,
                )
                self._set_transient_status_message(
                    self._format_snapshot_failure_message(self._snapshot_last_error, external=True)
                )
                raise
            self._snapshot_last_saved_path = result.saved_path
            self._snapshot_last_error = None
            self._clear_failure_reflection_for_source("snapshot")
            self._set_transient_status_message(
                self._format_snapshot_saved_message(result.saved_path, external=True)
            )
        elif command.command_name == "start_recording":
            file_stem = payload["file_stem"] if "file_stem" in payload else self._recording_file_stem
            file_extension = choose_snapshot_file_extension(
                pixel_format=self._get_current_pixel_format(),
                requested_extension=payload["file_extension"] if "file_extension" in payload else self._recording_file_extension,
            )
            frame_limit = (
                payload["max_frame_count"]
                if "max_frame_count" in payload
                else self._parse_optional_positive_int(self._recording_max_frames.GetValue())
            )
            target_frame_rate = (
                payload["target_frame_rate"]
                if "target_frame_rate" in payload
                else self._parse_optional_positive_float(self._recording_target_frame_rate_input.GetValue())
            )
            save_directory = self._get_recording_save_directory()
            try:
                result = controller.start_recording(
                    StartRecordingRequest(
                        file_stem=file_stem,
                        file_extension=file_extension,
                        save_directory=save_directory,
                        max_frame_count=frame_limit,
                        target_frame_rate=target_frame_rate,
                        camera_id=self._session.resolved_camera_id,
                        configuration_profile_id=self._session.configuration_profile_id,
                        configuration_profile_camera_class=self._session.configuration_profile_camera_class,
                    )
                )
            except Exception as exc:
                self._recording_last_error = str(exc)
                self._recording_last_stop_reason = None
                self._set_failure_reflection(
                    source="recording",
                    action="start_recording",
                    message=self._recording_last_error,
                    external=True,
                )
                self._set_transient_status_message(
                    self._format_recording_failure_message("start", self._recording_last_error, external=True)
                )
                raise
            self._recording_active_frame_limit = frame_limit
            self._recording_target_frame_rate_value = target_frame_rate
            self._recording_last_summary = None
            self._recording_last_file_stem = result.status.active_file_stem or file_stem
            self._recording_last_save_directory = save_directory
            self._recording_last_stop_reason = None
            self._recording_last_error = None
            self._clear_failure_reflection_for_source("recording")
            self._set_transient_status_message(
                self._format_recording_started_message(
                    file_stem=result.status.active_file_stem or file_stem,
                    save_directory=save_directory,
                    external=True,
                )
            )
        elif command.command_name == "stop_recording":
            try:
                result = controller.stop_recording(
                    StopRecordingRequest(reason=payload.get("reason", "external_cli"))
                )
            except Exception as exc:
                self._recording_last_error = str(exc)
                self._set_failure_reflection(
                    source="recording",
                    action="stop_recording",
                    message=self._recording_last_error,
                    external=True,
                )
                self._set_transient_status_message(
                    self._format_recording_failure_message("stop", self._recording_last_error, external=True)
                )
                raise
            self._recording_last_summary = self._format_recording_summary(
                frames_written=result.status.frames_written,
                frame_limit=self._recording_active_frame_limit,
            )
            self._recording_last_stop_reason = result.stop_reason
            self._recording_last_error = None
            self._recording_active_frame_limit = None
            self._clear_failure_reflection_for_source("recording")
            self._set_transient_status_message(
                self._format_recording_stopped_message(
                    frames_written=result.status.frames_written,
                    recording_summary=self._recording_last_summary,
                    stop_reason=result.stop_reason,
                    save_directory=getattr(self, "_recording_last_save_directory", None),
                    external=True,
                )
            )
        else:
            raise RuntimeError(f"Unsupported live command '{command.command_name}'.")

        return self._build_live_command_result(command_name=command.command_name, result=result)

    def _publish_live_status_snapshot(self, status, *, focus_summary: str | None, recording_summary: str | None) -> None:
        live_sync_session = self._session.live_sync_session
        if live_sync_session is None:
            return
        setup_reflection = self._build_setup_reflection(focus_summary=focus_summary, status=status)
        recording_reflection = self._build_recording_reflection(status, recording_summary=recording_summary)
        snapshot_reflection = self._build_snapshot_reflection()
        write_live_status_snapshot(
            live_sync_session,
            build_companion_status_snapshot(
                session_id=live_sync_session.session_id,
                source=self._session.source,
                camera_id=self._session.resolved_camera_id,
                configuration_profile_id=self._session.configuration_profile_id,
                focus_summary=focus_summary,
                setup_reflection=setup_reflection,
                failure_reflection=self._build_failure_reflection(),
                snapshot_reflection=snapshot_reflection,
                recording_summary=recording_summary,
                recording_reflection=recording_reflection,
                status_lines=self._status_lines,
                status=to_serializable(status),
            ),
        )


def run_wx_preview_shell(
    *,
    source: str = "simulated",
    camera_id: str | None = None,
    camera_alias: str | None = None,
    sample_dir: Path | None = None,
    configuration_profile: str | None = None,
    profile_camera_class: str | None = None,
    exposure_time_us: float | None = None,
    gain: float | None = None,
    pixel_format: str | None = None,
    acquisition_frame_rate: float | None = None,
    roi_offset_x: int | None = None,
    roi_offset_y: int | None = None,
    roi_width: int | None = None,
    roi_height: int | None = None,
    snapshot_directory: Path = Path("captures/wx_shell_snapshot"),
    live_sync_directory: Path = Path("captures/wx_shell_sessions"),
    poll_interval_seconds: float = 0.03,
) -> int:
    session = build_local_shell_session(
        LocalShellLaunchOptions(
            source=source,
            camera_id=camera_id,
            camera_alias=camera_alias,
            sample_dir=sample_dir,
            configuration_profile=configuration_profile,
            profile_camera_class=profile_camera_class,
            exposure_time_us=exposure_time_us,
            gain=gain,
            pixel_format=pixel_format,
            acquisition_frame_rate=acquisition_frame_rate,
            roi_offset_x=roi_offset_x,
            roi_offset_y=roi_offset_y,
            roi_width=roi_width,
            roi_height=roi_height,
            snapshot_directory=snapshot_directory,
            live_sync_directory=live_sync_directory,
            poll_interval_seconds=poll_interval_seconds,
        )
    )
    app = wx.App(False)
    try:
        frame = WxLocalPreviewShell(
            session=session,
            poll_interval_seconds=poll_interval_seconds,
        )
        frame.Show()
        app.MainLoop()
        return 0
    finally:
        if "frame" in locals():
            frame._shutdown_subsystem()
        else:
            session.subsystem.driver.shutdown()


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the bounded wxPython local preview shell.")
    parser.add_argument(
        "--source",
        choices=("simulated", "hardware"),
        default="simulated",
        help="Choose the simulator-backed or hardware-backed camera path.",
    )
    parser.add_argument("--camera-id", default=None, help="Explicit camera id to initialize.")
    parser.add_argument(
        "--camera-alias",
        default=None,
        help="Repo-local camera alias resolved through configs/camera_aliases.json.",
    )
    parser.add_argument(
        "--sample-dir",
        type=Path,
        default=None,
        help="Optional directory containing .pgm or .ppm sample images.",
    )
    parser.add_argument(
        "--configuration-profile",
        default=None,
        help="Named camera-class configuration profile from configs/camera_configuration_profiles.json.",
    )
    parser.add_argument(
        "--profile-camera-class",
        default=None,
        help="Optional explicit camera-class key for profile resolution; defaults to a normalized camera model.",
    )
    parser.add_argument("--exposure-time-us", type=float, default=None, help="Exposure time in microseconds.")
    parser.add_argument("--gain", type=float, default=None, help="Gain value to apply before preview starts.")
    parser.add_argument("--pixel-format", default=None, help="Pixel format such as Mono8 or Mono10.")
    parser.add_argument(
        "--acquisition-frame-rate",
        type=float,
        default=None,
        help="Requested acquisition frame rate in frames per second.",
    )
    parser.add_argument("--roi-offset-x", type=int, default=None, help="ROI X offset.")
    parser.add_argument("--roi-offset-y", type=int, default=None, help="ROI Y offset.")
    parser.add_argument("--roi-width", type=int, default=None, help="ROI width.")
    parser.add_argument("--roi-height", type=int, default=None, help="ROI height.")
    parser.add_argument(
        "--snapshot-directory",
        type=Path,
        default=Path("captures/wx_shell_snapshot"),
        help="Repo-local directory used by the snapshot button.",
    )
    parser.add_argument(
        "--live-sync-directory",
        type=Path,
        default=Path("captures/wx_shell_sessions"),
        help="Repo-local directory used for the bounded open-shell command sync session.",
    )
    parser.add_argument(
        "--poll-interval-seconds",
        type=float,
        default=0.03,
        help="Preview polling interval in seconds.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    configure_logging()
    args_list = list(argv) if argv is not None else sys.argv[1:]
    if args_list and args_list[0] == "control":
        return run_local_shell_control_cli(args_list[1:])
    parser = _build_argument_parser()
    args = parser.parse_args(args_list)
    if args.source == "hardware" and args.sample_dir is not None:
        parser.error("--sample-dir is only valid for --source simulated.")
    return run_wx_preview_shell(
        source=args.source,
        camera_id=args.camera_id,
        camera_alias=args.camera_alias,
        sample_dir=args.sample_dir,
        configuration_profile=args.configuration_profile,
        profile_camera_class=args.profile_camera_class,
        exposure_time_us=args.exposure_time_us,
        gain=args.gain,
        pixel_format=args.pixel_format,
        acquisition_frame_rate=args.acquisition_frame_rate,
        roi_offset_x=args.roi_offset_x,
        roi_offset_y=args.roi_offset_y,
        roi_width=args.roi_width,
        roi_height=args.roi_height,
        snapshot_directory=args.snapshot_directory,
        live_sync_directory=args.live_sync_directory,
        poll_interval_seconds=args.poll_interval_seconds,
    )


def _map_source_point_to_viewport(
    mapping,
    point: tuple[int, int] | None,
) -> tuple[int, int] | None:
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


def _resolve_active_roi_colour(emphasis: str) -> wx.Colour:
    if emphasis == "drag":
        return wx.Colour(220, 60, 60)
    if emphasis == "hover":
        return wx.Colour(60, 120, 255)
    return wx.Colour(0, 255, 0)


class _RecordingSettingsDialog(wx.Dialog):
    def __init__(
        self,
        parent: wx.Window,
        *,
        file_stem: str,
        file_extension: str,
        max_frames: str,
        recording_fps: str,
    ) -> None:
        super().__init__(parent, title="Recording Settings", style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        panel = wx.Panel(self)
        panel_sizer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.FlexGridSizer(cols=2, vgap=8, hgap=8)
        grid.AddGrowableCol(1, 1)

        grid.Add(wx.StaticText(panel, label="File Stem"), 0, wx.ALIGN_CENTER_VERTICAL)
        self._file_stem = wx.TextCtrl(panel, value=file_stem)
        grid.Add(self._file_stem, 1, wx.EXPAND)

        grid.Add(wx.StaticText(panel, label="File Extension"), 0, wx.ALIGN_CENTER_VERTICAL)
        self._file_extension = wx.Choice(panel, choices=list(_WX_RECORDING_FILE_EXTENSIONS))
        self._file_extension.SetStringSelection(_normalize_wx_recording_file_extension(file_extension))
        grid.Add(self._file_extension, 1, wx.EXPAND)

        grid.Add(wx.StaticText(panel, label="Max Frames (0=unbounded)"), 0, wx.ALIGN_CENTER_VERTICAL)
        self._max_frames = wx.TextCtrl(panel, value=max_frames)
        grid.Add(self._max_frames, 1, wx.EXPAND)

        grid.Add(wx.StaticText(panel, label="Recording FPS (blank=auto)"), 0, wx.ALIGN_CENTER_VERTICAL)
        self._recording_fps = wx.TextCtrl(panel, value=recording_fps)
        grid.Add(self._recording_fps, 1, wx.EXPAND)

        panel_sizer.Add(grid, 1, wx.EXPAND | wx.ALL, 10)
        panel.SetSizer(panel_sizer)
        buttons = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(panel, 1, wx.EXPAND)
        if buttons is not None:
            root.Add(buttons, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        self.SetSizerAndFit(root)

    def get_values(self) -> dict[str, str]:
        return {
            "file_stem": self._file_stem.GetValue(),
            "file_extension": self._file_extension.GetStringSelection(),
            "max_frames": self._max_frames.GetValue(),
            "recording_fps": self._recording_fps.GetValue(),
        }


class _CameraSettingsDialog(wx.Dialog):
    def __init__(
        self,
        parent: wx.Window,
        *,
        exposure_time_us: str,
        gain: str,
        pixel_format: str,
        acquisition_frame_rate: str,
        roi_offset_x: str,
        roi_offset_y: str,
        roi_width: str,
        roi_height: str,
        field_hints: dict[str, str] | None = None,
    ) -> None:
        super().__init__(parent, title="Camera Settings", style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        panel = wx.Panel(self)
        panel_sizer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.FlexGridSizer(cols=2, vgap=8, hgap=8)
        grid.AddGrowableCol(1, 1)
        field_hints = field_hints or {}

        grid.Add(wx.StaticText(panel, label="Exposure Time (us, blank=unchanged)"), 0, wx.ALIGN_CENTER_VERTICAL)
        self._exposure_time_us = wx.TextCtrl(panel, value=exposure_time_us)
        self._set_tooltip(self._exposure_time_us, field_hints.get("exposure_time_us"))
        grid.Add(self._exposure_time_us, 1, wx.EXPAND)

        grid.Add(wx.StaticText(panel, label="Gain (blank=unchanged)"), 0, wx.ALIGN_CENTER_VERTICAL)
        self._gain = wx.TextCtrl(panel, value=gain)
        self._set_tooltip(self._gain, field_hints.get("gain"))
        grid.Add(self._gain, 1, wx.EXPAND)

        pixel_format_choices = list(_WX_CAMERA_PIXEL_FORMATS)
        if pixel_format and pixel_format not in pixel_format_choices:
            pixel_format_choices.insert(1, pixel_format)
        self._pixel_format_choices = tuple(pixel_format_choices)
        grid.Add(wx.StaticText(panel, label="Pixel Format"), 0, wx.ALIGN_CENTER_VERTICAL)
        self._pixel_format = wx.Choice(panel, choices=pixel_format_choices)
        if pixel_format and not self._pixel_format.SetStringSelection(pixel_format):
            self._pixel_format.SetSelection(0)
        elif not pixel_format:
            self._pixel_format.SetSelection(0)
        self._set_tooltip(self._pixel_format, field_hints.get("pixel_format"))
        grid.Add(self._pixel_format, 1, wx.EXPAND)

        grid.Add(wx.StaticText(panel, label="Acquisition FPS (blank=unchanged)"), 0, wx.ALIGN_CENTER_VERTICAL)
        self._acquisition_frame_rate = wx.TextCtrl(panel, value=acquisition_frame_rate)
        self._set_tooltip(self._acquisition_frame_rate, field_hints.get("acquisition_frame_rate"))
        grid.Add(self._acquisition_frame_rate, 1, wx.EXPAND)

        grid.Add(wx.StaticText(panel, label="ROI Offset X (blank=unchanged)"), 0, wx.ALIGN_CENTER_VERTICAL)
        self._roi_offset_x = wx.TextCtrl(panel, value=roi_offset_x)
        self._set_tooltip(self._roi_offset_x, field_hints.get("roi_offset_x"))
        grid.Add(self._roi_offset_x, 1, wx.EXPAND)

        grid.Add(wx.StaticText(panel, label="ROI Offset Y (blank=unchanged)"), 0, wx.ALIGN_CENTER_VERTICAL)
        self._roi_offset_y = wx.TextCtrl(panel, value=roi_offset_y)
        self._set_tooltip(self._roi_offset_y, field_hints.get("roi_offset_y"))
        grid.Add(self._roi_offset_y, 1, wx.EXPAND)

        grid.Add(wx.StaticText(panel, label="ROI Width (blank=unchanged)"), 0, wx.ALIGN_CENTER_VERTICAL)
        self._roi_width = wx.TextCtrl(panel, value=roi_width)
        self._set_tooltip(self._roi_width, field_hints.get("roi_width"))
        grid.Add(self._roi_width, 1, wx.EXPAND)

        grid.Add(wx.StaticText(panel, label="ROI Height (blank=unchanged)"), 0, wx.ALIGN_CENTER_VERTICAL)
        self._roi_height = wx.TextCtrl(panel, value=roi_height)
        self._set_tooltip(self._roi_height, field_hints.get("roi_height"))
        grid.Add(self._roi_height, 1, wx.EXPAND)

        panel_sizer.Add(grid, 1, wx.EXPAND | wx.ALL, 10)
        panel.SetSizer(panel_sizer)
        buttons = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(panel, 1, wx.EXPAND)
        if buttons is not None:
            root.Add(buttons, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        self.SetSizerAndFit(root)

    @staticmethod
    def _set_tooltip(control, tooltip: str | None) -> None:
        if tooltip:
            control.SetToolTip(tooltip)

    def get_values(self) -> dict[str, str]:
        return {
            "exposure_time_us": self._exposure_time_us.GetValue(),
            "gain": self._gain.GetValue(),
            "pixel_format": _normalize_wx_camera_pixel_format(
                self._pixel_format.GetStringSelection(),
                allowed_formats=self._pixel_format_choices,
            )
            or "",
            "acquisition_frame_rate": self._acquisition_frame_rate.GetValue(),
            "roi_offset_x": self._roi_offset_x.GetValue(),
            "roi_offset_y": self._roi_offset_y.GetValue(),
            "roi_width": self._roi_width.GetValue(),
            "roi_height": self._roi_height.GetValue(),
        }


__all__ = ["WxLocalPreviewShell", "main", "run_wx_preview_shell"]


def _is_copy_shortcut(event) -> bool:
    key_code = event.GetKeyCode()
    return bool((event.ControlDown() or event.CmdDown()) and key_code in (3, ord("C"), ord("c")))


def _copy_text_to_clipboard(text: str) -> None:
    if not wx.TheClipboard.Open():
        raise RuntimeError("clipboard unavailable")
    try:
        if not wx.TheClipboard.SetData(wx.TextDataObject(text)):
            raise RuntimeError("clipboard write failed")
    finally:
        wx.TheClipboard.Close()


def _normalize_wx_recording_file_extension(file_extension: str) -> str:
    normalized_extension = file_extension.strip().lower()
    if normalized_extension not in _WX_RECORDING_FILE_EXTENSIONS:
        allowed_extensions = ", ".join(_WX_RECORDING_FILE_EXTENSIONS)
        raise ValueError(f"file extension must be one of: {allowed_extensions}")
    return normalized_extension


def _normalize_wx_camera_pixel_format(
    pixel_format: str,
    *,
    allowed_formats: tuple[str, ...] | list[str] | None = None,
) -> str | None:
    normalized_pixel_format = pixel_format.strip()
    if not normalized_pixel_format or normalized_pixel_format == "<unchanged>":
        return None
    allowed_formats = allowed_formats or _WX_CAMERA_PIXEL_FORMATS
    allowed_format_set = {format_name for format_name in allowed_formats if format_name != "<unchanged>"}
    if normalized_pixel_format not in allowed_format_set:
        allowed_text = ", ".join(allowed_formats)
        raise ValueError(f"pixel format must be one of: {allowed_text}")
    return normalized_pixel_format
