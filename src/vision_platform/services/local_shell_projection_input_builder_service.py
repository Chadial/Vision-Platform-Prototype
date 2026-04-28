from __future__ import annotations

from pathlib import Path
from typing import Any

from vision_platform.services.local_shell_status_projection_service import (
    LocalShellRecordingProjectionInput,
    LocalShellSetupProjectionInput,
    LocalShellSnapshotProjectionInput,
    LocalShellStatusProjectionInput,
)


def build_local_shell_setup_projection_input(
    *,
    focus_visibility: str,
    focus_summary: str | None,
    active_roi: Any | None,
    configuration_summary: str | None,
) -> LocalShellSetupProjectionInput:
    return LocalShellSetupProjectionInput(
        focus_visibility=focus_visibility,
        focus_summary=focus_summary,
        active_roi=active_roi,
        configuration_summary=configuration_summary,
    )


def build_local_shell_snapshot_projection_input(
    *,
    last_saved_path: Path | None,
    last_error: str | None,
) -> LocalShellSnapshotProjectionInput:
    return LocalShellSnapshotProjectionInput(
        last_saved_path=last_saved_path,
        last_error=last_error,
    )


def build_local_shell_recording_projection_input(
    *,
    is_recording: bool,
    frames_written: int,
    active_file_stem: str | None,
    active_save_directory: Path | None,
    last_file_stem: str | None,
    last_save_directory: Path | None,
    last_stop_reason: str | None,
    last_error: str | None,
    recording_summary: str | None,
) -> LocalShellRecordingProjectionInput:
    return LocalShellRecordingProjectionInput(
        is_recording=is_recording,
        frames_written=frames_written,
        active_file_stem=active_file_stem,
        active_save_directory=active_save_directory,
        last_file_stem=last_file_stem,
        last_save_directory=last_save_directory,
        last_stop_reason=last_stop_reason,
        last_error=last_error,
        recording_summary=recording_summary,
    )


def build_local_shell_status_projection_input(
    *,
    session_id: str,
    source: str,
    camera_id: str | None,
    configuration_profile_id: str | None,
    focus_summary: str | None,
    setup_focus_visibility: str,
    active_roi: Any | None,
    configuration_summary: str | None,
    failure_reflection: dict[str, object | None] | None,
    snapshot_last_saved_path: Path | None,
    snapshot_last_error: str | None,
    is_recording: bool,
    frames_written: int,
    active_file_stem: str | None,
    active_save_directory: Path | None,
    last_file_stem: str | None,
    last_save_directory: Path | None,
    last_stop_reason: str | None,
    last_error: str | None,
    recording_summary: str | None,
    status_lines: list[str],
    status: Any,
) -> LocalShellStatusProjectionInput:
    return LocalShellStatusProjectionInput(
        session_id=session_id,
        source=source,
        camera_id=camera_id,
        configuration_profile_id=configuration_profile_id,
        focus_summary=focus_summary,
        setup=build_local_shell_setup_projection_input(
            focus_visibility=setup_focus_visibility,
            focus_summary=focus_summary,
            active_roi=active_roi,
            configuration_summary=configuration_summary,
        ),
        failure_reflection=failure_reflection,
        snapshot=build_local_shell_snapshot_projection_input(
            last_saved_path=snapshot_last_saved_path,
            last_error=snapshot_last_error,
        ),
        recording=build_local_shell_recording_projection_input(
            is_recording=is_recording,
            frames_written=frames_written,
            active_file_stem=active_file_stem,
            active_save_directory=active_save_directory,
            last_file_stem=last_file_stem,
            last_save_directory=last_save_directory,
            last_stop_reason=last_stop_reason,
            last_error=last_error,
            recording_summary=recording_summary,
        ),
        status_lines=list(status_lines),
        status=status,
    )


__all__ = [
    "build_local_shell_recording_projection_input",
    "build_local_shell_setup_projection_input",
    "build_local_shell_snapshot_projection_input",
    "build_local_shell_status_projection_input",
]
