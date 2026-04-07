from __future__ import annotations

import argparse
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
import sys
from time import monotonic
from typing import Sequence

from camera_app.logging.log_service import configure_logging
from vision_platform.libraries.roi_core import roi_bounds
from vision_platform.models import ApplyConfigurationRequest, SaveSnapshotRequest, SetSaveDirectoryRequest
from vision_platform.models import StartRecordingRequest, StopRecordingRequest
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
from vision_platform.apps.local_shell.preview_shell_state import PreviewShellPresenter, PreviewShellViewModel
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
        self._publish_live_status_snapshot(status, focus_summary=focus_summary, recording_summary=recording_summary)

    def _on_timer(self, event) -> None:
        self._poll_live_commands()
        self.request_refresh()

    def _on_snapshot(self, event) -> None:
        try:
            result = self._subsystem.command_controller.save_snapshot(
                SaveSnapshotRequest(file_stem="wx_shell_snapshot", file_extension=".bmp")
            )
        except Exception as exc:
            self._set_transient_status_message(f"Snapshot failed: {exc}")
            self.request_refresh()
            return
        self._cached_status = None
        self._set_transient_status_message(f"Snapshot saved: {result.saved_path.name}")
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
                self._set_transient_status_message("Recording failed: no save directory configured")
                self.request_refresh()
                return
            result = self._session.subsystem.command_controller.start_recording(
                StartRecordingRequest(
                    file_stem=self._recording_file_stem,
                    file_extension=self._recording_file_extension,
                    save_directory=save_directory,
                    max_frame_count=frame_limit,
                    target_frame_rate=target_frame_rate,
                    camera_id=self._session.resolved_camera_id,
                    configuration_profile_id=self._session.configuration_profile_id,
                    configuration_profile_camera_class=self._session.configuration_profile_camera_class,
                )
            )
        except Exception as exc:
            self._set_transient_status_message(f"Recording failed: {exc}")
            self.request_refresh()
            return
        self._recording_active_frame_limit = frame_limit
        self._recording_target_frame_rate_value = target_frame_rate
        self._recording_last_summary = None
        self._cached_status = None
        self._last_status_refresh_time = 0.0
        self._set_transient_status_message(
            f"Recording started: {result.status.active_file_stem or self._recording_file_stem}"
        )
        self.request_refresh()

    def _on_stop_recording(self, event) -> None:
        try:
            result = self._session.subsystem.command_controller.stop_recording(
                StopRecordingRequest(reason="wx_shell_button")
            )
        except Exception as exc:
            self._set_transient_status_message(f"Recording stop failed: {exc}")
            self.request_refresh()
            return
        self._recording_last_summary = self._format_recording_summary(
            frames_written=result.status.frames_written,
            frame_limit=self._recording_active_frame_limit,
        )
        self._recording_active_frame_limit = None
        self._set_transient_status_message(
            f"Recording stopped: {result.status.frames_written} frames"
        )
        self.request_refresh()

    def _on_close(self, event) -> None:
        self._shutdown_subsystem()
        event.Skip()

    def _on_char_hook(self, event) -> None:
        if _is_copy_shortcut(event):
            self._copy_selected_point()
            self.request_refresh()
            return
        if event.GetKeyCode() == wx.WXK_ESCAPE and self._presenter.cancel_active_drag():
            self.request_refresh()
            return
        event.Skip()

    def _build_menu_bar(self) -> wx.MenuBar:
        menu_bar = wx.MenuBar()

        file_menu = wx.Menu()
        self._menu_set_save_directory = file_menu.Append(
            wx.ID_ANY,
            "Set Save Directory...\tCtrl+Shift+S",
            "Choose the base directory for snapshots and recordings.",
        )
        self.Bind(wx.EVT_MENU, self._on_menu_set_save_directory, self._menu_set_save_directory)
        file_menu.AppendSeparator()
        exit_item = file_menu.Append(wx.ID_EXIT, "Exit\tCtrl+Q", "Close the local shell.")
        self.Bind(wx.EVT_MENU, lambda _event: self.Close(), exit_item)
        menu_bar.Append(file_menu, "&File")

        settings_menu = wx.Menu()
        self._menu_recording_settings = settings_menu.Append(
            wx.ID_ANY,
            "Recording Settings...\tCtrl+R",
            "Edit bounded recording settings used by Start Recording.",
        )
        self.Bind(wx.EVT_MENU, self._on_menu_recording_settings, self._menu_recording_settings)
        menu_bar.Append(settings_menu, "&Settings")

        return menu_bar

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
            self._set_transient_status_message(f"Save directory: {result.selected_directory}")
            self.request_refresh()
        except Exception as exc:
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
        if self._focus_preview_service is None:
            return None
        if not self._presenter.state.interaction_state.focus_status_visible:
            return "hidden"
        if focus_state is None:
            return "waiting"
        if not focus_state.result.is_valid:
            return "invalid"
        return format_focus_score(focus_state.result.score)

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
        if status.default_save_directory is not None:
            prefix.append(f"save={status.default_save_directory}")
        if self._session.configuration_profile_id is not None:
            prefix.append(f"profile={self._session.configuration_profile_id}")
        return prefix

    def _build_recording_summary(self, status) -> str | None:
        if status.recording.is_recording:
            return self._format_recording_summary(
                frames_written=status.recording.frames_written,
                frame_limit=self._recording_active_frame_limit,
            )
        if (
            self._recording_active_frame_limit is not None
            and status.recording.frames_written > 0
            and self._recording_last_summary is None
        ):
            summary = self._format_recording_summary(
                frames_written=status.recording.frames_written,
                frame_limit=self._recording_active_frame_limit,
            )
            self._recording_last_summary = summary
            self._recording_active_frame_limit = None
            return summary
        if self._recording_last_summary is not None:
            return self._recording_last_summary
        return None

    @staticmethod
    def _format_recording_summary(*, frames_written: int, frame_limit: int | None) -> str:
        if frame_limit is None:
            return f"{frames_written}/n"
        return f"{frames_written}/{frame_limit}"

    def _update_recording_controls(self, status) -> None:
        if hasattr(self, "_start_recording_button"):
            self._start_recording_button.Enable(status.can_start_recording)
        if hasattr(self, "_stop_recording_button"):
            self._stop_recording_button.Enable(status.can_stop_recording)

    def _get_recording_save_directory(self) -> Path | None:
        status = self._get_status()
        if status.default_save_directory is not None:
            return status.default_save_directory
        return self._session.selected_save_directory

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
                write_live_command_result(
                    live_sync_session,
                    command_id=command.command_id,
                    success=False,
                    error=str(exc),
                )
                self._set_transient_status_message(f"External command failed: {command.command_name}")
                continue
            write_live_command_result(
                live_sync_session,
                command_id=command.command_id,
                success=True,
                result=result,
            )

    def _execute_live_command(self, command: LocalShellLiveCommand) -> dict:
        controller = self._session.subsystem.command_controller
        payload = command.payload

        if command.command_name == "apply_configuration":
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
            self._cached_focus_state = None
            self._set_transient_status_message("External configuration applied")
        elif command.command_name == "set_save_directory":
            result = controller.set_save_directory(
                SetSaveDirectoryRequest(
                    base_directory=Path(payload["base_directory"]),
                    mode=payload.get("mode", "append"),
                    subdirectory_name=payload.get("subdirectory_name"),
                )
            )
            self._session.selected_save_directory = result.selected_directory
            self._set_transient_status_message(f"External save directory: {result.selected_directory}")
        elif command.command_name == "save_snapshot":
            result = controller.save_snapshot(
                SaveSnapshotRequest(
                    file_stem=payload.get("file_stem", "wx_shell_snapshot"),
                    file_extension=payload.get("file_extension", ".bmp"),
                    camera_id=self._session.resolved_camera_id,
                    configuration_profile_id=self._session.configuration_profile_id,
                    configuration_profile_camera_class=self._session.configuration_profile_camera_class,
                )
            )
            self._set_transient_status_message(f"External snapshot saved: {result.saved_path.name}")
        elif command.command_name == "start_recording":
            result = controller.start_recording(
                StartRecordingRequest(
                    file_stem=payload.get("file_stem", "wx_recording"),
                    file_extension=payload.get("file_extension", ".bmp"),
                    save_directory=self._get_recording_save_directory(),
                    max_frame_count=payload.get("max_frame_count"),
                    target_frame_rate=payload.get("target_frame_rate"),
                    camera_id=self._session.resolved_camera_id,
                    configuration_profile_id=self._session.configuration_profile_id,
                    configuration_profile_camera_class=self._session.configuration_profile_camera_class,
                )
            )
            self._recording_active_frame_limit = payload.get("max_frame_count")
            self._recording_target_frame_rate_value = payload.get("target_frame_rate")
            self._recording_last_summary = None
            self._set_transient_status_message(
                f"External recording started: {result.status.active_file_stem or payload.get('file_stem', 'wx_recording')}"
            )
        elif command.command_name == "stop_recording":
            result = controller.stop_recording(
                StopRecordingRequest(reason=payload.get("reason", "external_cli"))
            )
            self._recording_last_summary = self._format_recording_summary(
                frames_written=result.status.frames_written,
                frame_limit=self._recording_active_frame_limit,
            )
            self._recording_active_frame_limit = None
            self._set_transient_status_message(f"External recording stopped: {result.status.frames_written} frames")
        else:
            raise RuntimeError(f"Unsupported live command '{command.command_name}'.")

        self._cached_status = None
        self._last_status_refresh_time = 0.0
        return {"command": command.command_name, "result": to_serializable(result)}

    def _publish_live_status_snapshot(self, status, *, focus_summary: str | None, recording_summary: str | None) -> None:
        live_sync_session = self._session.live_sync_session
        if live_sync_session is None:
            return
        write_live_status_snapshot(
            live_sync_session,
            {
                "session_id": live_sync_session.session_id,
                "source": self._session.source,
                "camera_id": self._session.resolved_camera_id,
                "configuration_profile_id": self._session.configuration_profile_id,
                "focus_summary": focus_summary,
                "recording_summary": recording_summary,
                "status_lines": self._status_lines,
                "status": to_serializable(status),
            },
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
