from __future__ import annotations

import argparse
from pathlib import Path
from time import sleep

from camera_app.logging.log_service import configure_logging
from camera_app.smoke.demo_result import DemoRunResult
from vision_platform.apps.opencv_prototype.preview_snapshot import PreviewSnapshotSaver
from vision_platform.imaging.opencv_preview import OpenCvPreviewWindow
from vision_platform.integrations.camera import VimbaXCameraDriver
from vision_platform.models import CameraConfiguration
from vision_platform.services.recording_service import CameraService
from vision_platform.services.stream_service import CameraStreamService


def _format_operator_error(exc: Exception) -> str:
    message = str(exc).strip()
    if message:
        return message
    return exc.__class__.__name__


def run_hardware_preview_demo(
    camera_id: str | None = None,
    poll_interval_seconds: float = 0.03,
    frame_limit: int | None = None,
    exposure_time_us: float | None = None,
    snapshot_save_directory: Path | None = None,
    snapshot_file_stem: str = "preview_snapshot",
    snapshot_file_extension: str = ".png",
) -> DemoRunResult:
    driver = VimbaXCameraDriver()
    camera_service = CameraService(driver)
    camera_service.initialize(camera_id=camera_id)
    if exposure_time_us is not None:
        camera_service.apply_configuration(CameraConfiguration(exposure_time_us=exposure_time_us))
    stream_service = CameraStreamService(
        driver,
        preview_poll_interval_seconds=poll_interval_seconds,
        shared_poll_interval_seconds=poll_interval_seconds,
    )
    snapshot_saver = None
    if snapshot_save_directory is not None:
        snapshot_saver = PreviewSnapshotSaver(
            stream_service._preview_service,
            save_directory=snapshot_save_directory,
            file_stem=snapshot_file_stem,
            file_extension=snapshot_file_extension,
        )
    preview_window = OpenCvPreviewWindow(
        stream_service._preview_service,
        window_name="Hardware Camera Preview",
        status_warning_provider=lambda: camera_service.get_status().capability_probe_error,
        roi_state_service=stream_service.get_roi_state_service(),
        snapshot_callback=snapshot_saver.save_latest_frame if snapshot_saver is not None else None,
    )

    rendered_frames = 0
    preview_started = False
    try:
        stream_service.start_preview()
        preview_started = True
        while frame_limit is None or rendered_frames < frame_limit:
            pressed_key = preview_window.render_latest_frame_and_get_key(delay_ms=1)
            if pressed_key is None:
                sleep(poll_interval_seconds)
                continue

            if pressed_key in (27, ord("q"), ord("Q")):
                break

            rendered_frames += 1
            sleep(poll_interval_seconds)
    finally:
        preview_window.close()
        if preview_started:
            stream_service.stop_preview()
        camera_service.shutdown()

    return DemoRunResult(
        success=True,
        rendered_frames=rendered_frames,
        preview_frame_info=stream_service.get_latest_frame_info(),
    )


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the optional OpenCV preview demo with a real Vimba X camera.")
    parser.add_argument(
        "--camera-id",
        default=None,
        help="Optional explicit camera id. If omitted, the first available hardware camera is used.",
    )
    parser.add_argument(
        "--poll-interval-seconds",
        type=float,
        default=0.03,
        help="Preview polling interval in seconds.",
    )
    parser.add_argument(
        "--frame-limit",
        type=int,
        default=None,
        help="Optional number of rendered frames before the demo exits.",
    )
    parser.add_argument(
        "--exposure-time-us",
        type=float,
        default=None,
        help="Optional exposure time in microseconds to apply before preview starts.",
    )
    parser.add_argument(
        "--snapshot-save-directory",
        type=Path,
        default=None,
        help="Optional directory that enables the '+' snapshot shortcut for saving the latest preview frame.",
    )
    parser.add_argument(
        "--snapshot-file-stem",
        default="preview_snapshot",
        help="Base file stem used by the '+' snapshot shortcut when a snapshot save directory is configured.",
    )
    parser.add_argument(
        "--snapshot-file-extension",
        default=".png",
        help="File extension used by the '+' snapshot shortcut when a snapshot save directory is configured.",
    )
    return parser


def main() -> int:
    configure_logging()
    parser = _build_argument_parser()
    args = parser.parse_args()
    print(
        "Preview controls: left click=select point, +=save preview frame, x=crosshair on/off, y=focus status on/off, "
        "wheel=zoom, middle-drag=pan, c=copy coordinates, q/Esc or window close=quit, i=zoom in, o=zoom out, f=fit-to-window"
    )

    try:
        result = run_hardware_preview_demo(
            camera_id=args.camera_id,
            poll_interval_seconds=args.poll_interval_seconds,
            frame_limit=args.frame_limit,
            exposure_time_us=args.exposure_time_us,
            snapshot_save_directory=args.snapshot_save_directory,
            snapshot_file_stem=args.snapshot_file_stem,
            snapshot_file_extension=args.snapshot_file_extension,
        )
    except Exception as exc:
        print(f"ERROR: Hardware preview failed: {_format_operator_error(exc)}")
        return 1
    print(f"Rendered {result.rendered_frames} frames.")
    if result.preview_frame_info is not None:
        print(
            f"Last frame: id={result.preview_frame_info.frame_id}, "
            f"size={result.preview_frame_info.width}x{result.preview_frame_info.height}, "
            f"pixel_format={result.preview_frame_info.pixel_format}"
        )
    return 0


__all__ = ["main", "run_hardware_preview_demo"]


if __name__ == "__main__":
    raise SystemExit(main())
