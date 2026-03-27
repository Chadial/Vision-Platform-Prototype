from __future__ import annotations

import argparse
from pathlib import Path
from time import monotonic, sleep

from camera_app.logging.log_service import configure_logging
from camera_app.smoke.demo_result import DemoRunResult
from vision_platform.bootstrap import CameraSubsystem, build_camera_subsystem
from vision_platform.integrations.camera import VimbaXCameraDriver
from vision_platform.models import (
    ApplyConfigurationRequest,
    CameraConfiguration,
    SaveSnapshotRequest,
    SetSaveDirectoryRequest,
    StartIntervalCaptureRequest,
    StartRecordingRequest,
    StopIntervalCaptureRequest,
    StopRecordingRequest,
)


def run_hardware_command_flow(
    base_directory: Path,
    run_name: str,
    camera_id: str | None = None,
    snapshot_stem: str = "snapshot",
    snapshot_extension: str = ".png",
    interval_stem: str = "interval",
    interval_extension: str = ".raw",
    interval_seconds: float = 0.25,
    interval_frame_count: int = 3,
    recording_stem: str = "recording",
    recording_extension: str = ".raw",
    frame_limit: int | None = 3,
    duration_seconds: float | None = None,
    target_frame_rate: float | None = None,
    preview_poll_interval_seconds: float = 0.03,
    shared_poll_interval_seconds: float = 0.01,
    recording_poll_interval_seconds: float = 0.01,
    interval_capture_poll_interval_seconds: float = 0.01,
    preview_warmup_timeout_seconds: float = 2.0,
    configuration: CameraConfiguration | None = None,
    subsystem: CameraSubsystem | None = None,
) -> DemoRunResult:
    subsystem = subsystem or build_camera_subsystem(
        VimbaXCameraDriver(),
        preview_poll_interval_seconds=preview_poll_interval_seconds,
        shared_poll_interval_seconds=shared_poll_interval_seconds,
        recording_poll_interval_seconds=recording_poll_interval_seconds,
        interval_capture_poll_interval_seconds=interval_capture_poll_interval_seconds,
    )
    camera_service = subsystem.camera_service
    controller = subsystem.command_controller

    try:
        camera_service.initialize(camera_id=camera_id)
        if configuration is not None:
            controller.apply_configuration(_to_apply_configuration_request(configuration))

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
                file_extension=snapshot_extension,
            )
        )

        subsystem.stream_service.start_preview()
        try:
            preview_frame_info = _wait_for_preview_frame(subsystem, preview_warmup_timeout_seconds)
            initial_interval_capture_status = controller.start_interval_capture(
                StartIntervalCaptureRequest(
                    file_stem=interval_stem,
                    file_extension=interval_extension,
                    interval_seconds=interval_seconds,
                    max_frame_count=interval_frame_count,
                )
            )

            while controller.get_status().interval_capture.is_capturing:
                sleep(0.01)

            interval_capture_status = controller.get_status().interval_capture
            stop_interval_capture_status = controller.stop_interval_capture(StopIntervalCaptureRequest())
        finally:
            subsystem.stream_service.stop_preview()

        initial_recording_status = controller.start_recording(
            StartRecordingRequest(
                file_stem=recording_stem,
                file_extension=recording_extension,
                max_frame_count=frame_limit,
                duration_seconds=duration_seconds,
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
            preview_frame_info=preview_frame_info,
            initial_interval_capture_status=initial_interval_capture_status,
            interval_capture_status=interval_capture_status,
            initial_recording_status=initial_recording_status,
            final_status=final_status,
            stop_status={
                "recording": stop_status,
                "interval_capture": stop_interval_capture_status,
            },
        )
    finally:
        camera_service.shutdown()


def _wait_for_preview_frame(
    subsystem: CameraSubsystem,
    preview_warmup_timeout_seconds: float,
):
    deadline = monotonic() + preview_warmup_timeout_seconds
    while monotonic() < deadline:
        preview_frame_info = subsystem.stream_service.get_latest_frame_info()
        if preview_frame_info is not None:
            return preview_frame_info
        sleep(0.01)
    raise RuntimeError("Preview did not produce a frame within the configured warmup timeout.")


def _to_apply_configuration_request(configuration: CameraConfiguration) -> ApplyConfigurationRequest:
    return ApplyConfigurationRequest(
        exposure_time_us=configuration.exposure_time_us,
        gain=configuration.gain,
        pixel_format=configuration.pixel_format,
        acquisition_frame_rate=configuration.acquisition_frame_rate,
        roi_offset_x=configuration.roi_offset_x,
        roi_offset_y=configuration.roi_offset_y,
        roi_width=configuration.roi_width,
        roi_height=configuration.roi_height,
    )


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a hardware-backed command flow for Phase 9 validation.")
    parser.add_argument("--base-directory", type=Path, required=True, help="Base output directory for the run.")
    parser.add_argument("--run-name", default="run_001", help="Subdirectory name for this hardware validation run.")
    parser.add_argument(
        "--camera-id",
        default=None,
        help="Optional explicit camera id. If omitted, the first available hardware camera is used.",
    )
    parser.add_argument("--snapshot-stem", default="snapshot", help="Snapshot file stem.")
    parser.add_argument("--snapshot-extension", default=".png", help="Snapshot file extension.")
    parser.add_argument("--interval-stem", default="interval", help="Interval-capture file stem.")
    parser.add_argument("--interval-extension", default=".raw", help="Interval-capture file extension.")
    parser.add_argument(
        "--interval-seconds",
        type=float,
        default=0.25,
        help="Capture one interval frame at this cadence while preview is running.",
    )
    parser.add_argument(
        "--interval-frame-count",
        type=int,
        default=3,
        help="Number of interval-capture frames to save from the shared preview stream.",
    )
    parser.add_argument("--recording-stem", default="recording", help="Recording file stem.")
    parser.add_argument("--recording-extension", default=".raw", help="Recording file extension.")
    parser.add_argument("--frame-limit", type=int, default=None, help="Optional number of frames to record.")
    parser.add_argument(
        "--duration-seconds",
        type=float,
        default=None,
        help="Optional duration-based recording stop condition.",
    )
    parser.add_argument(
        "--target-frame-rate",
        type=float,
        default=None,
        help="Optional recording pacing rate in frames per second.",
    )
    parser.add_argument("--exposure-time-us", type=float, default=None, help="Optional exposure time to apply.")
    parser.add_argument("--gain", type=float, default=None, help="Optional gain to apply.")
    parser.add_argument("--pixel-format", default=None, help="Optional pixel format to apply, for example Mono8.")
    parser.add_argument(
        "--acquisition-frame-rate",
        type=float,
        default=None,
        help="Optional acquisition frame rate to apply.",
    )
    parser.add_argument("--roi-offset-x", type=int, default=None, help="Optional ROI offset X to apply.")
    parser.add_argument("--roi-offset-y", type=int, default=None, help="Optional ROI offset Y to apply.")
    parser.add_argument("--roi-width", type=int, default=None, help="Optional ROI width to apply.")
    parser.add_argument("--roi-height", type=int, default=None, help="Optional ROI height to apply.")
    parser.add_argument(
        "--preview-warmup-timeout-seconds",
        type=float,
        default=2.0,
        help="Fail the run if preview does not produce a frame within this time.",
    )
    return parser


def main() -> int:
    configure_logging()
    parser = _build_argument_parser()
    args = parser.parse_args()

    configuration = CameraConfiguration(
        exposure_time_us=args.exposure_time_us,
        gain=args.gain,
        pixel_format=args.pixel_format,
        acquisition_frame_rate=args.acquisition_frame_rate,
        roi_offset_x=args.roi_offset_x,
        roi_offset_y=args.roi_offset_y,
        roi_width=args.roi_width,
        roi_height=args.roi_height,
    )
    if configuration == CameraConfiguration():
        configuration = None

    frame_limit = args.frame_limit
    if frame_limit is None and args.duration_seconds is None:
        frame_limit = 3

    result = run_hardware_command_flow(
        base_directory=args.base_directory,
        run_name=args.run_name,
        camera_id=args.camera_id,
        snapshot_stem=args.snapshot_stem,
        snapshot_extension=args.snapshot_extension,
        interval_stem=args.interval_stem,
        interval_extension=args.interval_extension,
        interval_seconds=args.interval_seconds,
        interval_frame_count=args.interval_frame_count,
        recording_stem=args.recording_stem,
        recording_extension=args.recording_extension,
        frame_limit=frame_limit,
        duration_seconds=args.duration_seconds,
        target_frame_rate=args.target_frame_rate,
        preview_warmup_timeout_seconds=args.preview_warmup_timeout_seconds,
        configuration=configuration,
    )
    print(result.snapshot_path)
    return 0


__all__ = ["main", "run_hardware_command_flow"]
