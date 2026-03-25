from __future__ import annotations

import argparse
from pathlib import Path
from time import sleep

from camera_app.drivers.simulated_camera_driver import SimulatedCameraDriver
from camera_app.logging.log_service import configure_logging
from camera_app.models.camera_configuration import CameraConfiguration
from camera_app.models.recording_request import RecordingRequest
from camera_app.models.snapshot_request import SnapshotRequest
from camera_app.smoke.demo_result import DemoRunResult
from camera_app.services.camera_service import CameraService
from camera_app.services.preview_service import PreviewService
from camera_app.services.recording_service import RecordingService
from camera_app.services.snapshot_service import SnapshotService


def run_simulated_demo(
    save_directory: Path,
    file_stem: str,
    sample_image_paths: list[Path] | None = None,
    frame_limit: int = 3,
) -> DemoRunResult:
    driver = SimulatedCameraDriver(sample_image_paths=sample_image_paths or [])
    camera_service = CameraService(driver)
    snapshot_service = SnapshotService(driver)
    recording_service = RecordingService(
        driver,
        configuration_provider=camera_service.get_last_configuration,
    )
    preview_service = PreviewService(driver, poll_interval_seconds=0.001)

    try:
        camera_service.initialize(camera_id="sim-demo")
        camera_service.apply_configuration(CameraConfiguration(pixel_format="Mono8"))

        snapshot_path = snapshot_service.save_snapshot(
            SnapshotRequest(save_directory=save_directory, file_stem=f"{file_stem}_snapshot", file_extension=".png")
        )

        preview_service.start()
        try:
            preview_service.refresh_once()
            preview_info = preview_service.get_latest_frame_info()
        finally:
            preview_service.stop()

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
        frame_limit=args.frame_limit,
    )
    print(result.snapshot_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
