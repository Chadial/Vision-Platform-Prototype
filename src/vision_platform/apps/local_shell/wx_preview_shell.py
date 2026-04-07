from __future__ import annotations

import argparse
from pathlib import Path

from camera_app.logging.log_service import configure_logging
from vision_platform.libraries.roi_core import roi_bounds
from vision_platform.models import SaveSnapshotRequest
from vision_platform.services.display_service import PreviewInteractionCommand

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


class PreviewCanvas(wx.Panel):
    def __init__(self, parent: wx.Window, presenter: PreviewShellPresenter, refresh_callback) -> None:
        super().__init__(parent, size=(640, 480))
        self._presenter = presenter
        self._refresh_callback = refresh_callback
        self._view_model: PreviewShellViewModel | None = None
        self._bitmap: wx.Bitmap | None = None
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        self.Bind(wx.EVT_MIDDLE_DOWN, self._on_middle_down)
        self.Bind(wx.EVT_MIDDLE_UP, self._on_middle_up)
        self.Bind(wx.EVT_MOTION, self._on_motion)
        self.Bind(wx.EVT_MOUSEWHEEL, self._on_mouse_wheel)

    def update_view(self, view_model: PreviewShellViewModel) -> None:
        self._view_model = view_model
        image = wx.Image(view_model.image.width, view_model.image.height)
        image.SetData(view_model.image.to_rgb_bytes())
        self._bitmap = wx.Bitmap(image)
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

        for roi, colour in (
            (view_model.overlay_model.draft_roi, wx.Colour(0, 200, 255)),
            (view_model.overlay_model.active_roi, wx.Colour(0, 255, 0)),
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

    def _on_left_down(self, event) -> None:
        self._presenter.handle_canvas_click(event.GetX(), event.GetY())
        self._refresh_callback()

    def _on_middle_down(self, event) -> None:
        self._presenter.handle_pan_start(event.GetX(), event.GetY())
        self._refresh_callback()

    def _on_middle_up(self, event) -> None:
        self._presenter.handle_pan_stop()
        self._refresh_callback()

    def _on_motion(self, event) -> None:
        self._presenter.handle_pointer_move(event.GetX(), event.GetY())
        if event.MiddleIsDown():
            self._presenter.handle_pan_move(event.GetX(), event.GetY())
        self._refresh_callback()

    def _on_mouse_wheel(self, event) -> None:
        self._presenter.handle_mouse_wheel(event.GetX(), event.GetY(), event.GetWheelRotation())
        self._refresh_callback()


class WxLocalPreviewShell(wx.Frame):
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
        self._last_snapshot_name: str | None = None
        self._is_closed = False

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
        root_sizer.Add(self._canvas, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        root_sizer.Add(self._status, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        panel.SetSizer(root_sizer)

        self.Bind(wx.EVT_TIMER, self._on_timer, self._timer)
        self.Bind(wx.EVT_CLOSE, self._on_close)
        self._timer.Start(max(15, int(poll_interval_seconds * 1000)))
        self.request_refresh()

    def request_refresh(self) -> None:
        frame = self._subsystem.stream_service.get_latest_frame()
        if frame is None:
            return
        focus_state = None
        if self._focus_preview_service is not None:
            focus_state = self._focus_preview_service.refresh_once(
                roi=self._subsystem.stream_service.get_roi_state_service().get_active_roi()
            )
        canvas_size = self._canvas.GetClientSize()
        view_model = self._presenter.build_view(
            frame,
            viewport_width=max(1, canvas_size.GetWidth()),
            viewport_height=max(1, canvas_size.GetHeight()),
            focus_state=focus_state,
            has_focus_toggle=self._focus_preview_service is not None,
        )
        self._canvas.update_view(view_model)
        status = self._subsystem.command_controller.get_status()
        prefix = [
            f"source={self._session.source}",
            f"camera={'ready' if status.camera.is_initialized else 'offline'}",
            f"preview={'running' if self._subsystem.stream_service.is_preview_running else 'stopped'}",
        ]
        if self._session.resolved_camera_id is not None:
            prefix.append(f"camera_id={self._session.resolved_camera_id}")
        if status.default_save_directory is not None:
            prefix.append(f"save={status.default_save_directory}")
        if self._session.configuration_profile_id is not None:
            prefix.append(f"profile={self._session.configuration_profile_id}")
        if self._last_snapshot_name is not None:
            prefix.append(f"last_snapshot={self._last_snapshot_name}")
        self._status_lines = [" | ".join(prefix)] + view_model.status_lines
        self._status.SetValue("\n".join(self._status_lines))

    def _on_timer(self, event) -> None:
        self.request_refresh()

    def _on_snapshot(self, event) -> None:
        try:
            result = self._subsystem.command_controller.save_snapshot(
                SaveSnapshotRequest(file_stem="wx_shell_snapshot", file_extension=".bmp")
            )
        except Exception as exc:
            self._presenter.state.interaction_state.last_status_message = f"Snapshot failed: {exc}"
            self.request_refresh()
            return
        self._last_snapshot_name = result.saved_path.name
        self._presenter.state.interaction_state.last_status_message = f"Snapshot saved: {result.saved_path.name}"
        self.request_refresh()

    def _run_action(self, action: str) -> None:
        self._presenter.apply_command(
            PreviewInteractionCommand(action=action),
            has_focus_provider=self._focus_preview_service is not None,
        )
        self.request_refresh()

    def _run_roi_toggle(self, roi_mode: str) -> None:
        self._presenter.apply_command(PreviewInteractionCommand(action="toggle_roi_mode", roi_mode=roi_mode))
        self.request_refresh()

    def _on_close(self, event) -> None:
        self._shutdown_subsystem()
        event.Skip()

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
            self._subsystem.driver.shutdown()


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
        "--poll-interval-seconds",
        type=float,
        default=0.03,
        help="Preview polling interval in seconds.",
    )
    return parser


def main() -> int:
    configure_logging()
    parser = _build_argument_parser()
    args = parser.parse_args()
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


__all__ = ["WxLocalPreviewShell", "main", "run_wx_preview_shell"]
