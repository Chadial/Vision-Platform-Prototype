from __future__ import annotations

import argparse
from pathlib import Path
from time import sleep

from camera_app.logging.log_service import configure_logging
from vision_platform.apps.opencv_prototype.demo_result import DemoRunResult
from vision_platform.bootstrap import build_simulated_camera_subsystem
from vision_platform.models import (
    ApplyConfigurationRequest,
    SaveSnapshotRequest,
    SetSaveDirectoryRequest,
    StartIntervalCaptureRequest,
    StartRecordingRequest,
    StopIntervalCaptureRequest,
    StopRecordingRequest,
)


def run_simulated_command_flow(
    base_directory: Path,
    run_name: str,
    snapshot_stem: str = "snapshot",
    interval_stem: str = "interval",
    interval_seconds: float = 0.05,
    interval_frame_count: int = 3,
    recording_stem: str = "recording",
    frame_limit: int = 3,
    target_frame_rate: float | None = None,
) -> DemoRunResult:
    subsystem = build_simulated_camera_subsystem()
    camera_service = subsystem.camera_service
    controller = subsystem.command_controller

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

        snapshot_result = controller.save_snapshot(
            SaveSnapshotRequest(
                file_stem=snapshot_stem,
                file_extension=".png",
            )
        )

        subsystem.stream_service.start_preview()
        try:
            initial_interval_capture_result = controller.start_interval_capture(
                StartIntervalCaptureRequest(
                    file_stem=interval_stem,
                    file_extension=".raw",
                    interval_seconds=interval_seconds,
                    max_frame_count=interval_frame_count,
                )
            )

            while controller.get_status().interval_capture.is_capturing:
                sleep(0.01)

            interval_capture_status = controller.get_status().interval_capture
            stop_interval_capture_result = controller.stop_interval_capture(StopIntervalCaptureRequest())
        finally:
            subsystem.stream_service.stop_preview()

        initial_recording_result = controller.start_recording(
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
        stop_recording_result = controller.stop_recording(StopRecordingRequest())
        return DemoRunResult(
            success=True,
            snapshot_path=snapshot_result.saved_path,
            initial_interval_capture_status=initial_interval_capture_result.status,
            interval_capture_status=interval_capture_status,
            initial_recording_status=initial_recording_result.status,
            final_status=final_status,
            stop_status={
                "recording": stop_recording_result.status,
                "interval_capture": stop_interval_capture_result.status,
            },
        )
    finally:
        camera_service.shutdown()


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a simulated host-style command flow without real hardware.")
    parser.add_argument("--base-directory", type=Path, required=True, help="Base output directory for the run.")
    parser.add_argument("--run-name", default="command_run_001", help="Subdirectory name for this command-driven run.")
    parser.add_argument("--snapshot-stem", default="snapshot", help="Snapshot file stem.")
    parser.add_argument("--interval-stem", default="interval", help="Interval-capture file stem.")
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
        interval_stem=args.interval_stem,
        interval_seconds=args.interval_seconds,
        interval_frame_count=args.interval_frame_count,
        recording_stem=args.recording_stem,
        frame_limit=args.frame_limit,
        target_frame_rate=args.target_frame_rate,
    )
    print(result.snapshot_path)
    return 0


__all__ = ["main", "run_simulated_command_flow"]
