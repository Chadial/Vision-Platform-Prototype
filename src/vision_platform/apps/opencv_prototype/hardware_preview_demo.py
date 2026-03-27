from __future__ import annotations

import argparse
from time import sleep

from camera_app.logging.log_service import configure_logging
from camera_app.smoke.demo_result import DemoRunResult
from vision_platform.imaging.opencv_preview import OpenCvPreviewWindow
from vision_platform.integrations.camera import VimbaXCameraDriver
from vision_platform.services.recording_service import CameraService
from vision_platform.services.stream_service import CameraStreamService


def run_hardware_preview_demo(
    camera_id: str | None = None,
    poll_interval_seconds: float = 0.03,
    frame_limit: int | None = None,
) -> DemoRunResult:
    driver = VimbaXCameraDriver()
    camera_service = CameraService(driver)
    camera_service.initialize(camera_id=camera_id)
    stream_service = CameraStreamService(
        driver,
        preview_poll_interval_seconds=poll_interval_seconds,
        shared_poll_interval_seconds=poll_interval_seconds,
    )
    preview_window = OpenCvPreviewWindow(
        stream_service._preview_service,
        window_name="Hardware Camera Preview",
        status_warning_provider=lambda: camera_service.get_status().capability_probe_error,
    )

    rendered_frames = 0
    stream_service.start_preview()
    try:
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
    return parser


def main() -> int:
    configure_logging()
    parser = _build_argument_parser()
    args = parser.parse_args()
    print(
        "Preview controls: left click=select point, x=crosshair on/off, y=focus status on/off, "
        "c=copy coordinates, q/Esc or window close=quit, i=zoom in, o=zoom out, f=fit-to-window"
    )

    result = run_hardware_preview_demo(
        camera_id=args.camera_id,
        poll_interval_seconds=args.poll_interval_seconds,
        frame_limit=args.frame_limit,
    )
    print(f"Rendered {result.rendered_frames} frames.")
    if result.preview_frame_info is not None:
        print(
            f"Last frame: id={result.preview_frame_info.frame_id}, "
            f"size={result.preview_frame_info.width}x{result.preview_frame_info.height}, "
            f"pixel_format={result.preview_frame_info.pixel_format}"
        )
    return 0


__all__ = ["main", "run_hardware_preview_demo"]
