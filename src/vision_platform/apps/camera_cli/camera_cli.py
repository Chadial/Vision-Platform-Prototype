from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, is_dataclass
from pathlib import Path
import sys
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
from vision_platform.services.api_service import map_subsystem_status_to_api_payload
from vision_platform.services.recording_service.traceability import build_snapshot_run_id


@dataclass(slots=True)
class CameraCliResult:
    operation: str
    source: str
    status: SubsystemStatus
    result: Any = None
    snapshot_path: Path | None = None
    selected_save_directory: Path | None = None


@dataclass(slots=True)
class CameraCliError(Exception):
    error_type: str
    message: str
    exit_code: int = 1
    details: dict[str, Any] | None = None

    def __str__(self) -> str:
        return self.message


class CameraCliArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise CameraCliError(
            error_type="argument_error",
            message=message,
            exit_code=2,
        )


def build_argument_parser() -> argparse.ArgumentParser:
    parser = CameraCliArgumentParser(
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
        try:
            _apply_configuration_if_requested(controller, args)
        except ValueError as exc:
            raise CameraCliError(
                error_type="configuration_error",
                message=str(exc),
                details={"stage": "apply_configuration"},
            ) from exc
        return args.command_handler(args, parser, subsystem)
    finally:
        camera_service.shutdown()


def main(argv: Sequence[str] | None = None) -> int:
    configure_logging()
    try:
        result = run_cli(argv)
    except CameraCliError as exc:
        _emit_envelope(_build_error_envelope(exc), stream=sys.stderr)
        return exc.exit_code
    except Exception as exc:
        _emit_envelope(
            _build_error_envelope(
                CameraCliError(
                    error_type="command_error",
                    message=str(exc),
                    exit_code=1,
                )
            ),
            stream=sys.stderr,
        )
        return 1

    _emit_envelope(_build_success_envelope(result), stream=sys.stdout)
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
        result={
            "status_source": "poll",
            "confirmed_settings": _build_status_confirmed_settings(status),
        },
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
    status = controller.get_status()
    return CameraCliResult(
        operation="snapshot",
        source=args.source,
        status=status,
        result={
            "saved_path": snapshot_result.saved_path,
            "run_id": build_snapshot_run_id(snapshot_result.saved_path),
            "selected_save_directory": selected_save_directory,
            "confirmed_settings": _build_snapshot_confirmed_settings(
                status,
                args,
                selected_save_directory,
                run_id=build_snapshot_run_id(snapshot_result.saved_path),
            ),
        },
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
    recording_result = controller.stop_recording(StopRecordingRequest(reason="bounded_completion"))
    status = controller.get_status()
    return CameraCliResult(
        operation="recording",
        source=args.source,
        status=status,
        result={
            "run_id": recording_result.status.run_id,
            "selected_save_directory": selected_save_directory,
            "frames_written": status.recording.frames_written,
            "stop_reason": recording_result.stop_reason,
            "recording_bounds": {
                "frame_limit": args.frame_limit,
                "duration_seconds": args.duration_seconds,
                "target_frame_rate": args.target_frame_rate,
            },
            "confirmed_settings": _build_recording_confirmed_settings(
                status,
                args,
                selected_save_directory,
                run_id=recording_result.status.run_id,
            ),
        },
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


def _build_success_envelope(result: CameraCliResult) -> dict[str, Any]:
    return {
        "success": True,
        "command": result.operation,
        "source": result.source,
        "result": _to_serializable(result.result),
        "status": _to_serializable(map_subsystem_status_to_api_payload(result.status)),
        "error": None,
    }


def _build_error_envelope(error: CameraCliError) -> dict[str, Any]:
    return {
        "success": False,
        "command": None,
        "source": None,
        "result": None,
        "status": None,
        "error": {
            "code": error.error_type,
            "message": error.message,
            "details": _to_serializable(error.details),
        },
    }


def _emit_envelope(payload: dict[str, Any], stream) -> None:
    print(json.dumps(_to_serializable(payload), indent=2, sort_keys=True), file=stream)


def _build_status_confirmed_settings(status: SubsystemStatus) -> dict[str, Any]:
    configuration = status.configuration
    return {
        "camera_id": status.camera.camera_id,
        "pixel_format": configuration.pixel_format if configuration is not None else None,
        "exposure_time_us": configuration.exposure_time_us if configuration is not None else None,
    }


def _build_snapshot_confirmed_settings(
    status: SubsystemStatus,
    args: argparse.Namespace,
    selected_save_directory: Path,
    *,
    run_id: str | None,
) -> dict[str, Any]:
    confirmed_settings = _build_status_confirmed_settings(status)
    confirmed_settings.update(
        {
            "run_id": run_id,
            "resolved_save_directory": selected_save_directory,
            "resolved_file_stem": args.file_stem,
            "resolved_file_extension": args.file_extension,
        }
    )
    return confirmed_settings


def _build_recording_confirmed_settings(
    status: SubsystemStatus,
    args: argparse.Namespace,
    selected_save_directory: Path,
    *,
    run_id: str | None,
) -> dict[str, Any]:
    confirmed_settings = _build_snapshot_confirmed_settings(
        status,
        args,
        selected_save_directory,
        run_id=run_id,
    )
    confirmed_settings.update(
        {
            "accepted_frame_limit": args.frame_limit,
            "accepted_duration_seconds": args.duration_seconds,
            "accepted_target_frame_rate": args.target_frame_rate,
        }
    )
    return confirmed_settings


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
