from __future__ import annotations

import argparse
from pathlib import Path
from time import sleep

from camera_app.logging.log_service import configure_logging
from vision_platform.apps.opencv_prototype.demo_result import DemoRunResult
from vision_platform.integrations.camera import SimulatedCameraDriver
from vision_platform.libraries.common_models import RoiDefinition
from vision_platform.services.stream_service import CameraStreamService


def run_focus_preview_demo(
    sample_dir: Path | None = None,
    poll_interval_seconds: float = 0.01,
    roi: RoiDefinition | None = None,
) -> DemoRunResult:
    sample_paths = []
    if sample_dir is not None:
        sample_paths = sorted(
            path for path in sample_dir.iterdir() if path.is_file() and path.suffix.lower() in {".pgm", ".ppm"}
        )

    driver = SimulatedCameraDriver(sample_image_paths=sample_paths)
    driver.initialize(camera_id="sim-focus-preview")
    stream_service = CameraStreamService(
        driver,
        preview_poll_interval_seconds=poll_interval_seconds,
        shared_poll_interval_seconds=poll_interval_seconds,
    )
    focus_preview_service = stream_service.create_focus_preview_service()

    stream_service.start_preview()
    try:
        focus_state = None
        preview_frame_info = None
        for _ in range(100):
            stream_service.refresh_preview_once()
            preview_frame_info = stream_service.get_latest_frame_info()
            focus_state = focus_preview_service.refresh_once(roi=roi)
            if focus_state is not None and focus_state.result.is_valid:
                if preview_frame_info is None:
                    preview_frame_info = stream_service.get_latest_frame_info()
                break
            sleep(poll_interval_seconds)

        return DemoRunResult(
            success=focus_state is not None and focus_state.result.is_valid,
            preview_frame_info=preview_frame_info,
            focus_preview_state=focus_state,
        )
    finally:
        stream_service.stop_preview()
        driver.shutdown()


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a simulated preview-to-focus smoke demo.")
    parser.add_argument(
        "--sample-dir",
        type=Path,
        default=None,
        help="Optional directory containing .pgm or .ppm sample images.",
    )
    parser.add_argument(
        "--poll-interval-seconds",
        type=float,
        default=0.01,
        help="Preview and shared-stream polling interval in seconds.",
    )
    return parser


def main() -> int:
    configure_logging()
    parser = _build_argument_parser()
    args = parser.parse_args()
    result = run_focus_preview_demo(
        sample_dir=args.sample_dir,
        poll_interval_seconds=args.poll_interval_seconds,
    )
    if result.focus_preview_state is not None:
        print(result.focus_preview_state.result.score)
    return 0 if result.success else 1


__all__ = ["main", "run_focus_preview_demo"]
