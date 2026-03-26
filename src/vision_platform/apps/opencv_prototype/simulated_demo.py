from __future__ import annotations

import argparse
from pathlib import Path
from time import sleep

from camera_app.logging.log_service import configure_logging
from camera_app.smoke.demo_result import DemoRunResult
from vision_platform.integrations.camera import SimulatedCameraDriver
from vision_platform.models import CameraConfiguration, IntervalCaptureRequest, RecordingRequest, SnapshotRequest
from vision_platform.services.recording_service import CameraService, SnapshotService
from vision_platform.services.stream_service import CameraStreamService


def run_simulated_demo(
    save_directory: Path,
    file_stem: str,
    sample_image_paths: list[Path] | None = None,
    interval_seconds: float = 0.05,
    interval_frame_count: int = 3,
    frame_limit: int = 3,
) -> DemoRunResult:
    driver = SimulatedCameraDriver(sample_image_paths=sample_image_paths or [])
    camera_service = CameraService(driver)
    snapshot_service = SnapshotService(driver)
    stream_service = CameraStreamService(
        driver,
        preview_poll_interval_seconds=0.001,
        shared_poll_interval_seconds=0.001,
    )
    recording_service = stream_service.create_recording_service(
        configuration_provider=camera_service.get_last_configuration,
    )
    interval_capture_service = stream_service.create_interval_capture_service()

    try:
        camera_service.initialize(camera_id="sim-demo")
        camera_service.apply_configuration(CameraConfiguration(pixel_format="Mono8"))

        snapshot_path = snapshot_service.save_snapshot(
            SnapshotRequest(save_directory=save_directory, file_stem=f"{file_stem}_snapshot", file_extension=".png")
        )

        stream_service.start_preview()
        try:
            preview_info = None
            for _ in range(100):
                stream_service.refresh_preview_once()
                preview_info = stream_service.get_latest_frame_info()
                if preview_info is not None:
                    break
                sleep(0.01)

            interval_capture_status = interval_capture_service.start_capture(
                IntervalCaptureRequest(
                    save_directory=save_directory,
                    file_stem=f"{file_stem}_interval",
                    file_extension=".raw",
                    interval_seconds=interval_seconds,
                    max_frame_count=interval_frame_count,
                )
            )

            for _ in range(300):
                current_interval_status = interval_capture_service.get_status()
                if (
                    not current_interval_status.is_capturing
                    and current_interval_status.frames_written == interval_frame_count
                ):
                    break
                sleep(0.01)

            final_interval_capture_status = interval_capture_service.get_status()
        finally:
            stream_service.stop_preview()

        recording_status = recording_service.start_recording(
            RecordingRequest(
                save_directory=save_directory,
                file_stem=f"{file_stem}_recording",
                file_extension=".raw",
                frame_limit=frame_limit,
                queue_size=max(4, frame_limit),
            )
        )

        while recording_service.get_status().is_recording:
            sleep(0.01)

        return DemoRunResult(
            success=True,
            snapshot_path=snapshot_path,
            preview_frame_info=preview_info,
            initial_interval_capture_status=interval_capture_status,
            interval_capture_status=final_interval_capture_status,
            recording_status=recording_service.get_status(),
            initial_recording_status=recording_status,
        )
    finally:
        camera_service.shutdown()


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a simulated camera demo without real hardware.")
    parser.add_argument("--save-directory", type=Path, required=True, help="Output directory for demo files.")
    parser.add_argument("--file-stem", default="demo", help="Base file stem for snapshot and recording output.")
    parser.add_argument(
        "--sample-dir",
        type=Path,
        default=None,
        help="Optional directory containing .pgm or .ppm sample images for the simulation source.",
    )
    parser.add_argument(
        "--interval-seconds",
        type=float,
        default=0.05,
        help="Capture one frame at this interval from the shared preview stream.",
    )
    parser.add_argument(
        "--interval-frame-count",
        type=int,
        default=3,
        help="Number of interval-capture frames to save from the shared preview stream.",
    )
    parser.add_argument("--frame-limit", type=int, default=3, help="Number of frames to record in demo mode.")
    return parser


def main() -> int:
    configure_logging()
    parser = _build_argument_parser()
    args = parser.parse_args()

    sample_paths = None
    if args.sample_dir is not None:
        sample_paths = sorted(
            [
                *args.sample_dir.glob("*.pgm"),
                *args.sample_dir.glob("*.ppm"),
            ]
        )

    result = run_simulated_demo(
        save_directory=args.save_directory,
        file_stem=args.file_stem,
        sample_image_paths=sample_paths,
        interval_seconds=args.interval_seconds,
        interval_frame_count=args.interval_frame_count,
        frame_limit=args.frame_limit,
    )
    print(result.snapshot_path)
    return 0


__all__ = ["main", "run_simulated_demo"]
