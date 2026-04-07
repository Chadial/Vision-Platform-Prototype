from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from vision_platform.apps.local_shell.live_command_sync import (
    LocalShellLiveSyncError,
    append_live_command,
    read_live_status_snapshot,
    resolve_active_live_sync_session,
    to_serializable,
    wait_for_live_command_result,
)

_DEFAULT_SESSION_ROOT = Path("captures/wx_shell_sessions")


class LocalShellControlArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise LocalShellLiveSyncError(message)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = LocalShellControlArgumentParser(
        description="Send bounded external commands to an already open wx shell session.",
    )
    parser.add_argument(
        "--session-root",
        type=Path,
        default=_DEFAULT_SESSION_ROOT,
        help="Root directory containing the active wx shell session registry.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    status_parser = subparsers.add_parser("status", help="Read the latest published shell status snapshot.")
    status_parser.set_defaults(command_handler=_handle_status_command)

    save_dir_parser = subparsers.add_parser(
        "set-save-directory",
        help="Change the save directory of the currently open wx shell.",
    )
    save_dir_parser.add_argument("--base-directory", type=Path, required=True, help="Base directory for saved output.")
    save_dir_parser.add_argument(
        "--save-mode",
        choices=("append", "new_subdirectory"),
        default="append",
        help="Append into the base directory or create a named run subdirectory.",
    )
    save_dir_parser.add_argument("--run-name", default=None, help="Required for --save-mode new_subdirectory.")
    save_dir_parser.set_defaults(command_handler=_handle_set_save_directory_command)

    apply_parser = subparsers.add_parser(
        "apply-configuration",
        help="Apply bounded configuration changes through the open wx shell core.",
    )
    apply_parser.add_argument("--exposure-time-us", type=float, default=None)
    apply_parser.add_argument("--gain", type=float, default=None)
    apply_parser.add_argument("--pixel-format", default=None)
    apply_parser.add_argument("--acquisition-frame-rate", type=float, default=None)
    apply_parser.add_argument("--roi-offset-x", type=int, default=None)
    apply_parser.add_argument("--roi-offset-y", type=int, default=None)
    apply_parser.add_argument("--roi-width", type=int, default=None)
    apply_parser.add_argument("--roi-height", type=int, default=None)
    apply_parser.set_defaults(command_handler=_handle_apply_configuration_command)

    snapshot_parser = subparsers.add_parser(
        "snapshot",
        help="Trigger a snapshot through the open wx shell core.",
    )
    snapshot_parser.add_argument("--file-stem", default="wx_shell_snapshot")
    snapshot_parser.add_argument("--file-extension", default=".bmp")
    snapshot_parser.set_defaults(command_handler=_handle_snapshot_command)

    start_recording_parser = subparsers.add_parser(
        "start-recording",
        help="Start recording through the open wx shell core.",
    )
    start_recording_parser.add_argument("--file-stem", default="wx_recording")
    start_recording_parser.add_argument("--file-extension", default=".raw")
    start_recording_parser.add_argument(
        "--max-frames",
        type=int,
        default=0,
        help="0 means unbounded recording.",
    )
    start_recording_parser.add_argument("--recording-fps", type=float, default=None)
    start_recording_parser.set_defaults(command_handler=_handle_start_recording_command)

    stop_recording_parser = subparsers.add_parser(
        "stop-recording",
        help="Stop the current recording in the open wx shell.",
    )
    stop_recording_parser.add_argument("--reason", default="external_cli")
    stop_recording_parser.set_defaults(command_handler=_handle_stop_recording_command)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_argument_parser()
    try:
        args = parser.parse_args(list(argv) if argv is not None else None)
        if getattr(args, "save_mode", None) == "new_subdirectory" and not getattr(args, "run_name", None):
            parser.error("--run-name is required when --save-mode is new_subdirectory.")
        result = args.command_handler(args)
    except LocalShellLiveSyncError as exc:
        _emit({"success": False, "error": str(exc)})
        return 1
    _emit({"success": True, "result": result})
    return 0


def _handle_status_command(args: argparse.Namespace) -> dict:
    session = resolve_active_live_sync_session(args.session_root)
    return read_live_status_snapshot(session)


def _handle_set_save_directory_command(args: argparse.Namespace) -> dict:
    return _send_command(
        args.session_root,
        command_name="set_save_directory",
        payload={
            "base_directory": args.base_directory,
            "mode": args.save_mode,
            "subdirectory_name": args.run_name,
        },
    )


def _handle_apply_configuration_command(args: argparse.Namespace) -> dict:
    return _send_command(
        args.session_root,
        command_name="apply_configuration",
        payload={
            "exposure_time_us": args.exposure_time_us,
            "gain": args.gain,
            "pixel_format": args.pixel_format,
            "acquisition_frame_rate": args.acquisition_frame_rate,
            "roi_offset_x": args.roi_offset_x,
            "roi_offset_y": args.roi_offset_y,
            "roi_width": args.roi_width,
            "roi_height": args.roi_height,
        },
    )


def _handle_snapshot_command(args: argparse.Namespace) -> dict:
    return _send_command(
        args.session_root,
        command_name="save_snapshot",
        payload={
            "file_stem": args.file_stem,
            "file_extension": args.file_extension,
        },
    )


def _handle_start_recording_command(args: argparse.Namespace) -> dict:
    max_frames = None if args.max_frames == 0 else args.max_frames
    if args.max_frames < 0:
        raise LocalShellLiveSyncError("--max-frames must be zero or greater.")
    return _send_command(
        args.session_root,
        command_name="start_recording",
        payload={
            "file_stem": args.file_stem,
            "file_extension": args.file_extension,
            "max_frame_count": max_frames,
            "target_frame_rate": args.recording_fps,
        },
    )


def _handle_stop_recording_command(args: argparse.Namespace) -> dict:
    return _send_command(
        args.session_root,
        command_name="stop_recording",
        payload={"reason": args.reason},
    )


def _send_command(session_root: Path, *, command_name: str, payload: dict) -> dict:
    session = resolve_active_live_sync_session(session_root)
    command = append_live_command(session, command_name=command_name, payload=payload)
    result = wait_for_live_command_result(session, command_id=command.command_id)
    if not result.get("success", False):
        raise LocalShellLiveSyncError(result.get("error") or f"wx shell command '{command_name}' failed")
    return result


def _emit(payload: dict) -> None:
    print(json.dumps(to_serializable(payload), indent=2, sort_keys=True), file=sys.stdout)


__all__ = ["build_argument_parser", "main"]
