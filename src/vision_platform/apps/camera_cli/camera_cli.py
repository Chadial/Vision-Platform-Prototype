from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, is_dataclass
from pathlib import Path
from time import sleep
from typing import Any, Sequence

from camera_app.logging.log_service import configure_logging
from vision_platform.bootstrap import build_camera_subsystem, build_simulated_camera_subsystem
from vision_platform.models import (
    ApplyConfigurationRequest,
    SaveSnapshotRequest,
    SetSaveDirectoryRequest,
    StartIntervalCaptureRequest,
    StartRecordingRequest,
    StopIntervalCaptureRequest,
    StopRecordingRequest,
    SubsystemStatus,
)


@dataclass(slots=True)
class CameraCliResult:
    operation: str
    source: str
    status: SubsystemStatus
    snapshot_path: Path | None = None
    selected_save_directory: Path | None = None


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run camera-oriented platform commands from one consistent CLI surface.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    common_parser = argparse.ArgumentParser(add_help=False)
    _add_common_camera_arguments(common_parser)
    _add_common_configuration_arguments(common_parser)

    status_parser = subparsers.add_parser(
        "status",
        parents=[common_parser],
        help="Initialize the selected camera source and print consolidated status.",
    )
    status_parser.set_defaults(command_handler=_handle_status_command)

    snapshot_parser = subparsers.add_parser(
        "snapshot",
        parents=[common_parser],
        help="Save one snapshot through the command-controller path.",
    )
    _add_common_storage_arguments(snapshot_parser)
    _add_snapshot_arguments(snapshot_parser)
    snapshot_parser.set_defaults(command_handler=_handle_snapshot_command)

    interval_parser = subparsers.add_parser(
        "interval-capture",
        parents=[common_parser],
        help="Run bounded interval capture through the shared stream path.",
    )
    _add_common_storage_arguments(interval_parser)
    _add_interval_capture_arguments(interval_parser)
    interval_parser.set_defaults(command_handler=_handle_interval_capture_command)

    recording_parser = subparsers.add_parser(
        "recording",
        parents=[common_parser],
        help="Run bounded recording through the command-controller path.",
    )
    _add_common_storage_arguments(recording_parser)
    _add_recording_arguments(recording_parser)
    recording_parser.set_defaults(command_handler=_handle_recording_command)

    return parser


def run_cli(argv: Sequence[str] | None = None) -> CameraCliResult:
    parser = build_argument_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    _validate_argument_combinations(parser, args)
    subsystem = _build_subsystem_for_args(args)
    controller = subsystem.command_controller
    camera_service = subsystem.camera_service

    try:
        camera_service.initialize(camera_id=args.camera_id)
        _apply_configuration_if_requested(controller, args)
        return args.command_handler(args, parser, subsystem)
    finally:
        camera_service.shutdown()


def main(argv: Sequence[str] | None = None) -> int:
    configure_logging()
    result = run_cli(argv)
    print(json.dumps(_to_serializable(result), indent=2, sort_keys=True))
    return 0


def _handle_status_command(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
    subsystem,
) -> CameraCliResult:
    del parser
    status = subsystem.command_controller.get_status()
    return CameraCliResult(
        operation="status",
        source=args.source,
        status=status,
    )


def _handle_snapshot_command(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
    subsystem,
) -> CameraCliResult:
    controller = subsystem.command_controller
    selected_save_directory = _set_default_save_directory(parser, controller, args)
    snapshot_result = controller.save_snapshot(
        SaveSnapshotRequest(
            file_stem=args.file_stem,
            file_extension=args.file_extension,
        )
    )
    return CameraCliResult(
        operation="snapshot",
        source=args.source,
        status=controller.get_status(),
        snapshot_path=snapshot_result.saved_path,
        selected_save_directory=selected_save_directory,
    )


def _handle_interval_capture_command(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
    subsystem,
) -> CameraCliResult:
    controller = subsystem.command_controller
    selected_save_directory = _set_default_save_directory(parser, controller, args)
    controller.start_interval_capture(
        StartIntervalCaptureRequest(
            file_stem=args.file_stem,
            file_extension=args.file_extension,
            interval_seconds=args.interval_seconds,
            max_frame_count=args.frame_limit,
            duration_seconds=args.duration_seconds,
        )
    )
    _wait_for_interval_capture_completion(controller)
    controller.stop_interval_capture(StopIntervalCaptureRequest())
    return CameraCliResult(
        operation="interval-capture",
        source=args.source,
        status=controller.get_status(),
        selected_save_directory=selected_save_directory,
    )


def _handle_recording_command(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
    subsystem,
) -> CameraCliResult:
    controller = subsystem.command_controller
    selected_save_directory = _set_default_save_directory(parser, controller, args)
    controller.start_recording(
        StartRecordingRequest(
            file_stem=args.file_stem,
            file_extension=args.file_extension,
            max_frame_count=args.frame_limit,
            duration_seconds=args.duration_seconds,
            target_frame_rate=args.target_frame_rate,
            queue_size=args.queue_size,
        )
    )
    _wait_for_recording_completion(controller)
    controller.stop_recording(StopRecordingRequest())
    return CameraCliResult(
        operation="recording",
        source=args.source,
        status=controller.get_status(),
        selected_save_directory=selected_save_directory,
    )


def _build_subsystem_for_args(args: argparse.Namespace):
    if args.source == "simulated":
        sample_paths = _collect_sample_paths(args.sample_dir)
        return build_simulated_camera_subsystem(sample_image_paths=sample_paths)

    from vision_platform.integrations.camera.vimbax_camera_driver import VimbaXCameraDriver

    return build_camera_subsystem(VimbaXCameraDriver())


def _collect_sample_paths(sample_dir: Path | None) -> list[Path] | None:
    if sample_dir is None:
        return None
    return sorted([*sample_dir.glob("*.pgm"), *sample_dir.glob("*.ppm")])


def _apply_configuration_if_requested(controller, args: argparse.Namespace) -> None:
    if not _has_configuration_overrides(args):
        return

    controller.apply_configuration(
        ApplyConfigurationRequest(
            exposure_time_us=args.exposure_time_us,
            gain=args.gain,
            pixel_format=args.pixel_format,
            acquisition_frame_rate=args.acquisition_frame_rate,
            roi_offset_x=args.roi_offset_x,
            roi_offset_y=args.roi_offset_y,
            roi_width=args.roi_width,
            roi_height=args.roi_height,
        )
    )


def _has_configuration_overrides(args: argparse.Namespace) -> bool:
    return any(
        value is not None
        for value in (
            args.exposure_time_us,
            args.gain,
            args.pixel_format,
            args.acquisition_frame_rate,
            args.roi_offset_x,
            args.roi_offset_y,
            args.roi_width,
            args.roi_height,
        )
    )


def _set_default_save_directory(parser: argparse.ArgumentParser, controller, args: argparse.Namespace) -> Path:
    if args.base_directory is None:
        parser.error("--base-directory is required for this command.")
    if args.save_mode == "new_subdirectory" and not args.run_name:
        parser.error("--run-name is required when --save-mode is 'new_subdirectory'.")

    request = SetSaveDirectoryRequest(
        base_directory=args.base_directory,
        mode=args.save_mode,
        subdirectory_name=args.run_name,
    )
    return controller.set_save_directory(request).selected_directory


def _wait_for_recording_completion(controller) -> None:
    while controller.get_status().recording.is_recording:
        sleep(0.01)


def _wait_for_interval_capture_completion(controller) -> None:
    while controller.get_status().interval_capture.is_capturing:
        sleep(0.01)


def _validate_argument_combinations(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if getattr(args, "source", None) == "hardware" and args.sample_dir is not None:
        parser.error("--sample-dir is only valid for --source simulated.")

    if getattr(args, "command", None) == "interval-capture":
        if args.interval_seconds is None:
            parser.error("--interval-seconds is required for interval-capture.")
        if args.frame_limit is None and args.duration_seconds is None:
            parser.error("interval-capture requires --frame-limit or --duration-seconds.")

    if getattr(args, "command", None) == "recording":
        if args.frame_limit is None and args.duration_seconds is None:
            parser.error("recording requires --frame-limit or --duration-seconds.")


def _add_common_camera_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--source",
        choices=("simulated", "hardware"),
        default="simulated",
        help="Choose the simulator-backed or hardware-backed camera path.",
    )
    parser.add_argument("--camera-id", default=None, help="Explicit camera id to initialize.")
    parser.add_argument(
        "--sample-dir",
        type=Path,
        default=None,
        help="Optional directory containing .pgm or .ppm sample frames for simulator runs.",
    )


def _add_common_configuration_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--exposure-time-us", type=float, default=None, help="Exposure time in microseconds.")
    parser.add_argument("--gain", type=float, default=None, help="Gain value to apply before the command runs.")
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


def _add_common_storage_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--base-directory", type=Path, default=None, help="Base directory for saved output.")
    parser.add_argument(
        "--save-mode",
        choices=("append", "new_subdirectory"),
        default="append",
        help="Append into the base directory or create a named run subdirectory.",
    )
    parser.add_argument(
        "--run-name",
        default=None,
        help="Subdirectory name used only when --save-mode is new_subdirectory.",
    )


def _add_snapshot_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--file-stem", default="snapshot", help="Snapshot file stem.")
    parser.add_argument("--file-extension", default=".png", help="Snapshot file extension.")


def _add_interval_capture_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--file-stem", default="interval", help="Interval-capture file stem.")
    parser.add_argument("--file-extension", default=".raw", help="Interval-capture file extension.")
    parser.add_argument(
        "--interval-seconds",
        type=float,
        default=None,
        help="Time between saved frames in seconds.",
    )
    parser.add_argument(
        "--frame-limit",
        type=int,
        default=None,
        help="Maximum number of frames to save. Required unless --duration-seconds is provided.",
    )
    parser.add_argument(
        "--duration-seconds",
        type=float,
        default=None,
        help="Maximum capture duration in seconds. Required unless --frame-limit is provided.",
    )


def _add_recording_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--file-stem", default="recording", help="Recording file stem.")
    parser.add_argument("--file-extension", default=".raw", help="Recording file extension.")
    parser.add_argument(
        "--frame-limit",
        type=int,
        default=None,
        help="Maximum number of frames to record. Required unless --duration-seconds is provided.",
    )
    parser.add_argument(
        "--duration-seconds",
        type=float,
        default=None,
        help="Maximum recording duration in seconds. Required unless --frame-limit is provided.",
    )
    parser.add_argument(
        "--target-frame-rate",
        type=float,
        default=None,
        help="Optional producer pacing rate in frames per second.",
    )
    parser.add_argument("--queue-size", type=int, default=128, help="Recording queue size.")


def _to_serializable(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if is_dataclass(value):
        return {key: _to_serializable(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): _to_serializable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_serializable(item) for item in value]
    return value


__all__ = [
    "CameraCliResult",
    "build_argument_parser",
    "main",
    "run_cli",
]
