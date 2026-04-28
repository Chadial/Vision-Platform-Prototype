from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from vision_platform.libraries.roi_core import roi_bounds
from vision_platform.services.companion_contract_service import (
    build_companion_command_result,
    build_companion_status_snapshot,
)
from vision_platform.services.local_shell_session_service import to_serializable


@dataclass(slots=True)
class LocalShellSetupProjectionInput:
    focus_visibility: str
    focus_summary: str | None
    active_roi: Any | None
    configuration_summary: str | None


@dataclass(slots=True)
class LocalShellSnapshotProjectionInput:
    last_saved_path: Path | None
    last_error: str | None


@dataclass(slots=True)
class LocalShellRecordingProjectionInput:
    is_recording: bool
    frames_written: int
    active_file_stem: str | None
    active_save_directory: Path | None
    last_file_stem: str | None
    last_save_directory: Path | None
    last_stop_reason: str | None
    last_error: str | None
    recording_summary: str | None


@dataclass(slots=True)
class LocalShellStatusProjectionInput:
    session_id: str
    source: str
    camera_id: str | None
    configuration_profile_id: str | None
    focus_summary: str | None
    setup: LocalShellSetupProjectionInput
    failure_reflection: dict[str, object | None] | None
    snapshot: LocalShellSnapshotProjectionInput
    recording: LocalShellRecordingProjectionInput
    status_lines: list[str]
    status: Any


def build_local_shell_setup_reflection(
    projection: LocalShellSetupProjectionInput,
) -> dict[str, object | None]:
    active_roi_bounds = roi_bounds(projection.active_roi) if projection.active_roi is not None else None
    return {
        "phase": "ready",
        "focus_visibility": projection.focus_visibility,
        "focus_summary": projection.focus_summary,
        "roi_active": projection.active_roi is not None,
        "roi_shape": getattr(projection.active_roi, "shape", None) if projection.active_roi is not None else None,
        "roi_bounds": None if active_roi_bounds is None else [int(round(value)) for value in active_roi_bounds],
        "configuration_summary": projection.configuration_summary,
    }


def build_local_shell_snapshot_reflection(
    projection: LocalShellSnapshotProjectionInput,
) -> dict[str, object | None]:
    return {
        "phase": get_local_shell_snapshot_phase(projection),
        "file_name": None if projection.last_saved_path is None else projection.last_saved_path.name,
        "file_stem": None if projection.last_saved_path is None else projection.last_saved_path.stem,
        "save_directory": None if projection.last_saved_path is None else str(projection.last_saved_path.parent),
        "last_error": projection.last_error,
    }


def get_local_shell_snapshot_phase(projection: LocalShellSnapshotProjectionInput) -> str:
    if projection.last_error is not None:
        return "failed"
    if projection.last_saved_path is not None:
        return "saved"
    return "idle"


def build_local_shell_save_directory_reflection(selected_directory: Path | None) -> dict[str, object | None]:
    return {
        "phase": "selected" if selected_directory is not None else "unset",
        "selected_directory": None if selected_directory is None else str(selected_directory),
    }


def build_local_shell_recording_reflection(
    projection: LocalShellRecordingProjectionInput,
) -> dict[str, object | None]:
    stop_reason = None if projection.is_recording else projection.last_stop_reason
    stop_category = categorize_local_shell_recording_stop_reason(stop_reason)
    if stop_category is None and projection.last_error is not None:
        stop_category = "failure_termination"
    file_stem = projection.active_file_stem or projection.last_file_stem
    save_directory = projection.active_save_directory or projection.last_save_directory
    return {
        "phase": "running" if projection.is_recording else ("failed" if projection.last_error is not None else "idle"),
        "summary": projection.recording_summary,
        "file_stem": file_stem,
        "save_directory": None if save_directory is None else str(save_directory),
        "stop_reason": stop_reason,
        "stop_category": stop_category,
        "frames_written": projection.frames_written,
        "last_error": projection.last_error,
    }


def get_local_shell_recording_stop_category(
    projection: LocalShellRecordingProjectionInput,
) -> str | None:
    if projection.is_recording:
        return None
    stop_category = categorize_local_shell_recording_stop_reason(projection.last_stop_reason)
    if stop_category is None and projection.last_error is not None:
        return "failure_termination"
    return stop_category


def categorize_local_shell_recording_stop_reason(stop_reason: str | None) -> str | None:
    if stop_reason is None:
        return None
    if stop_reason in {"bounded_completion", "max_frames_reached"}:
        return "max_frames_reached"
    if stop_reason in {"post_failure_cleanup", "duplicate_cleanup"}:
        return "failure_termination"
    if stop_reason in {"wx_shell_button", "external_cli", "external_request", "operator_cancelled", "host_shutdown"}:
        return "host_stop"
    return stop_reason


def build_local_shell_live_command_result(
    *,
    command_name: str,
    result: Any,
    status_projection: LocalShellStatusProjectionInput,
    selected_save_directory: Path | None,
) -> dict[str, Any]:
    reflection_kind: str | None = None
    reflection: dict[str, object | None] | None = None
    if command_name == "apply_configuration":
        reflection_kind = "setup"
        reflection = build_local_shell_setup_reflection(status_projection.setup)
    elif command_name == "set_save_directory":
        reflection_kind = "save_directory"
        reflection = build_local_shell_save_directory_reflection(selected_save_directory)
    elif command_name == "save_snapshot":
        reflection_kind = "snapshot"
        reflection = build_local_shell_snapshot_reflection(status_projection.snapshot)
    elif command_name in {"start_recording", "stop_recording"}:
        reflection_kind = "recording"
        reflection = build_local_shell_recording_reflection(status_projection.recording)
    return build_companion_command_result(
        command_name=command_name,
        reflection_kind=reflection_kind,
        reflection=reflection,
        failure_reflection=status_projection.failure_reflection,
        result=to_serializable(result),
    )


def build_local_shell_status_snapshot(
    projection: LocalShellStatusProjectionInput,
) -> dict[str, Any]:
    return build_companion_status_snapshot(
        session_id=projection.session_id,
        source=projection.source,
        camera_id=projection.camera_id,
        configuration_profile_id=projection.configuration_profile_id,
        focus_summary=projection.focus_summary,
        setup_reflection=build_local_shell_setup_reflection(projection.setup),
        failure_reflection=projection.failure_reflection,
        snapshot_reflection=build_local_shell_snapshot_reflection(projection.snapshot),
        recording_summary=projection.recording.recording_summary,
        recording_reflection=build_local_shell_recording_reflection(projection.recording),
        status_lines=projection.status_lines,
        status=to_serializable(projection.status),
    )


__all__ = [
    "LocalShellRecordingProjectionInput",
    "LocalShellSetupProjectionInput",
    "LocalShellSnapshotProjectionInput",
    "LocalShellStatusProjectionInput",
    "build_local_shell_live_command_result",
    "build_local_shell_recording_reflection",
    "build_local_shell_save_directory_reflection",
    "build_local_shell_setup_reflection",
    "build_local_shell_snapshot_reflection",
    "build_local_shell_status_snapshot",
    "categorize_local_shell_recording_stop_reason",
    "get_local_shell_recording_stop_category",
    "get_local_shell_snapshot_phase",
]
