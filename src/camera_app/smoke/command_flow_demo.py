from __future__ import annotations

import argparse
from pathlib import Path
from time import sleep

from camera_app.control.command_controller import CommandController
from camera_app.drivers.simulated_camera_driver import SimulatedCameraDriver
from camera_app.logging.log_service import configure_logging
from camera_app.models.apply_configuration_request import ApplyConfigurationRequest
from camera_app.models.save_snapshot_request import SaveSnapshotRequest
from camera_app.models.set_save_directory_request import SetSaveDirectoryRequest
from camera_app.models.start_recording_request import StartRecordingRequest
from camera_app.models.stop_recording_request import StopRecordingRequest
from camera_app.smoke.demo_result import DemoRunResult
from camera_app.services.camera_service import CameraService
from camera_app.services.recording_service import RecordingService
from camera_app.services.snapshot_service import SnapshotService


def run_simulated_command_flow(
    base_directory: Path,
    run_name: str,
    snapshot_stem: str = "snapshot",
    recording_stem: str = "recording",
    frame_limit: int = 3,
    target_frame_rate: float | None = None,
) -> DemoRunResult:
    driver = SimulatedCameraDriver()
    camera_service = CameraService(driver)
    snapshot_service = SnapshotService(driver)
    recording_service = RecordingService(
        driver,
        configuration_provider=camera_service.get_last_configuration,
    )
    controller = CommandController(camera_service, snapshot_service, recording_service)

    try:
        camera_service.initialize(camera_id="sim-command-flow")
        controller.apply_configuration(
            ApplyConfigurationRequest(
                exposure_time_us=1500.0,
                pixel_format="Mono8",
                roi_offset_x=0,
                roi_offset_y=0,
                roi_width=320,
                roi_height=240,
            )
        )
        controller.set_save_directory(
            SetSaveDirectoryRequest(
                base_directory=base_directory,
                mode="new_subdirectory",
                subdirectory_name=run_name,
            )
        )

        snapshot_path = controller.save_snapshot(
            SaveSnapshotRequest(
                file_stem=snapshot_stem,
                file_extension=".png",
            )
        )

        initial_recording_status = controller.start_recording(
            StartRecordingRequest(
                file_stem=recording_stem,
                file_extension=".raw",
                max_frame_count=frame_limit,
                target_frame_rate=target_frame_rate,
            )
        )

        while controller.get_status().recording.is_recording:
            sleep(0.01)

        final_status = controller.get_status()
        stop_status = controller.stop_recording(StopRecordingRequest())
        return DemoRunResult(
            success=True,
            snapshot_path=snapshot_path,
            initial_recording_status=initial_recording_status,
            final_status=final_status,
            stop_status=stop_status,
        )
    finally:
        camera_service.shutdown()


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a simulated host-style command flow without real hardware.")
    parser.add_argument("--base-directory", type=Path, required=True, help="Base output directory for the run.")
    parser.add_argument("--run-name", default="command_run_001", help="Subdirectory name for this command-driven run.")
    parser.add_argument("--snapshot-stem", default="snapshot", help="Snapshot file stem.")
    parser.add_argument("--recording-stem", default="recording", help="Recording file stem.")
    parser.add_argument("--frame-limit", type=int, default=3, help="Number of frames to record.")
    parser.add_argument(
        "--target-frame-rate",
        type=float,
        default=None,
        help="Optional recording pacing rate in frames per second.",
    )
    return parser


def main() -> int:
    configure_logging()
    parser = _build_argument_parser()
    args = parser.parse_args()
    result = run_simulated_command_flow(
        base_directory=args.base_directory,
        run_name=args.run_name,
        snapshot_stem=args.snapshot_stem,
        recording_stem=args.recording_stem,
        frame_limit=args.frame_limit,
        target_frame_rate=args.target_frame_rate,
    )
    print(result.snapshot_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
