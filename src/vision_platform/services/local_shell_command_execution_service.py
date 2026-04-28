from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from vision_platform.models import (
    ApplyConfigurationRequest,
    SaveSnapshotRequest,
    SetSaveDirectoryRequest,
    StartRecordingRequest,
    StopRecordingRequest,
)
from vision_platform.services.local_shell_session_protocol import LocalShellLiveCommand
from vision_platform.apps.local_shell.output_format_policy import choose_snapshot_file_extension

_UNSET = object()


@dataclass(slots=True)
class FailureReflectionUpdate:
    source: str
    action: str
    message: str
    external: bool = True


@dataclass(slots=True)
class LocalShellRecordingDefaults:
    file_stem: str
    file_extension: str
    max_frame_count: int | None
    target_frame_rate: float | None
    save_directory: Path | None


@dataclass(slots=True)
class LocalShellCompanionCommandExecutionContext:
    command_controller: Any
    resolved_camera_id: str | None
    configuration_profile_id: str | None
    configuration_profile_camera_class: str | None
    current_pixel_format: str | None
    recording_defaults: LocalShellRecordingDefaults
    format_snapshot_saved_message: Callable[[Path], str]
    format_snapshot_failure_message: Callable[[str], str]
    format_recording_started_message: Callable[[str | None, Path | None], str]
    format_recording_stopped_message: Callable[[int, str | None, str | None, Path | None], str]
    format_recording_failure_message: Callable[[str, str], str]


@dataclass(slots=True)
class LocalShellCompanionCommandExecutionOutcome:
    result: Any
    transient_status_message: str | None = None
    failure_reflection_to_set: FailureReflectionUpdate | None = None
    failure_reflection_source_to_clear: str | None = None
    clear_cached_focus_state: bool = False
    selected_save_directory: Any = _UNSET
    snapshot_saved_path: Any = _UNSET
    snapshot_last_error: Any = _UNSET
    recording_active_frame_limit: Any = _UNSET
    recording_target_frame_rate_value: Any = _UNSET
    recording_last_summary: Any = _UNSET
    recording_last_file_stem: Any = _UNSET
    recording_last_save_directory: Any = _UNSET
    recording_last_stop_reason: Any = _UNSET
    recording_last_error: Any = _UNSET


def execute_local_shell_companion_command(
    command: LocalShellLiveCommand,
    *,
    context: LocalShellCompanionCommandExecutionContext,
) -> LocalShellCompanionCommandExecutionOutcome:
    controller = context.command_controller
    payload = command.payload

    if command.command_name == "apply_configuration":
        try:
            result = controller.apply_configuration(
                ApplyConfigurationRequest(
                    exposure_time_us=payload.get("exposure_time_us"),
                    gain=payload.get("gain"),
                    pixel_format=payload.get("pixel_format"),
                    acquisition_frame_rate=payload.get("acquisition_frame_rate"),
                    roi_offset_x=payload.get("roi_offset_x"),
                    roi_offset_y=payload.get("roi_offset_y"),
                    roi_width=payload.get("roi_width"),
                    roi_height=payload.get("roi_height"),
                )
            )
        except Exception as exc:
            raise LocalShellCompanionCommandExecutionError(
                str(exc),
                outcome=LocalShellCompanionCommandExecutionOutcome(
                    result=None,
                    transient_status_message=f"External setup configuration failed: {exc}",
                    failure_reflection_to_set=FailureReflectionUpdate(
                        source="setup",
                        action="apply_configuration",
                        message=str(exc),
                    ),
                ),
            ) from exc
        return LocalShellCompanionCommandExecutionOutcome(
            result=result,
            transient_status_message="External setup configuration applied",
            failure_reflection_source_to_clear="setup",
            clear_cached_focus_state=True,
        )

    if command.command_name == "set_save_directory":
        try:
            result = controller.set_save_directory(
                SetSaveDirectoryRequest(
                    base_directory=Path(payload["base_directory"]),
                    mode=payload.get("mode", "append"),
                    subdirectory_name=payload.get("subdirectory_name"),
                )
            )
        except Exception as exc:
            raise LocalShellCompanionCommandExecutionError(
                str(exc),
                outcome=LocalShellCompanionCommandExecutionOutcome(
                    result=None,
                    transient_status_message=f"External save directory failed: {exc}",
                    failure_reflection_to_set=FailureReflectionUpdate(
                        source="setup",
                        action="set_save_directory",
                        message=str(exc),
                    ),
                ),
            ) from exc
        return LocalShellCompanionCommandExecutionOutcome(
            result=result,
            transient_status_message=f"External save directory: {result.selected_directory}",
            failure_reflection_source_to_clear="setup",
            selected_save_directory=result.selected_directory,
        )

    if command.command_name == "save_snapshot":
        try:
            result = controller.save_snapshot(
                SaveSnapshotRequest(
                    file_stem=payload.get("file_stem", "wx_shell_snapshot"),
                    file_extension=choose_snapshot_file_extension(
                        pixel_format=context.current_pixel_format,
                        requested_extension=payload.get("file_extension"),
                    ),
                    camera_id=context.resolved_camera_id,
                    configuration_profile_id=context.configuration_profile_id,
                    configuration_profile_camera_class=context.configuration_profile_camera_class,
                )
            )
        except Exception as exc:
            raise LocalShellCompanionCommandExecutionError(
                str(exc),
                outcome=LocalShellCompanionCommandExecutionOutcome(
                    result=None,
                    transient_status_message=context.format_snapshot_failure_message(str(exc)),
                    failure_reflection_to_set=FailureReflectionUpdate(
                        source="snapshot",
                        action="save_snapshot",
                        message=str(exc),
                    ),
                    snapshot_last_error=str(exc),
                ),
            ) from exc
        return LocalShellCompanionCommandExecutionOutcome(
            result=result,
            transient_status_message=context.format_snapshot_saved_message(result.saved_path),
            failure_reflection_source_to_clear="snapshot",
            snapshot_saved_path=result.saved_path,
            snapshot_last_error=None,
        )

    if command.command_name == "start_recording":
        file_stem = payload["file_stem"] if "file_stem" in payload else context.recording_defaults.file_stem
        file_extension = choose_snapshot_file_extension(
            pixel_format=context.current_pixel_format,
            requested_extension=(
                payload["file_extension"] if "file_extension" in payload else context.recording_defaults.file_extension
            ),
        )
        frame_limit = (
            payload["max_frame_count"] if "max_frame_count" in payload else context.recording_defaults.max_frame_count
        )
        target_frame_rate = (
            payload["target_frame_rate"]
            if "target_frame_rate" in payload
            else context.recording_defaults.target_frame_rate
        )
        save_directory = context.recording_defaults.save_directory
        try:
            result = controller.start_recording(
                StartRecordingRequest(
                    file_stem=file_stem,
                    file_extension=file_extension,
                    save_directory=save_directory,
                    max_frame_count=frame_limit,
                    target_frame_rate=target_frame_rate,
                    camera_id=context.resolved_camera_id,
                    configuration_profile_id=context.configuration_profile_id,
                    configuration_profile_camera_class=context.configuration_profile_camera_class,
                )
            )
        except Exception as exc:
            raise LocalShellCompanionCommandExecutionError(
                str(exc),
                outcome=LocalShellCompanionCommandExecutionOutcome(
                    result=None,
                    transient_status_message=context.format_recording_failure_message("start", str(exc)),
                    failure_reflection_to_set=FailureReflectionUpdate(
                        source="recording",
                        action="start_recording",
                        message=str(exc),
                    ),
                    recording_last_error=str(exc),
                    recording_last_stop_reason=None,
                ),
            ) from exc
        active_file_stem = result.status.active_file_stem or file_stem
        return LocalShellCompanionCommandExecutionOutcome(
            result=result,
            transient_status_message=context.format_recording_started_message(active_file_stem, save_directory),
            failure_reflection_source_to_clear="recording",
            recording_active_frame_limit=frame_limit,
            recording_target_frame_rate_value=target_frame_rate,
            recording_last_summary=None,
            recording_last_file_stem=active_file_stem,
            recording_last_save_directory=save_directory,
            recording_last_stop_reason=None,
            recording_last_error=None,
        )

    if command.command_name == "stop_recording":
        try:
            result = controller.stop_recording(
                StopRecordingRequest(reason=payload.get("reason", "external_cli"))
            )
        except Exception as exc:
            raise LocalShellCompanionCommandExecutionError(
                str(exc),
                outcome=LocalShellCompanionCommandExecutionOutcome(
                    result=None,
                    transient_status_message=context.format_recording_failure_message("stop", str(exc)),
                    failure_reflection_to_set=FailureReflectionUpdate(
                        source="recording",
                        action="stop_recording",
                        message=str(exc),
                    ),
                    recording_last_error=str(exc),
                ),
            ) from exc
        recording_summary = _format_recording_summary(
            frames_written=result.status.frames_written,
            frame_limit=context.recording_defaults.max_frame_count,
        )
        return LocalShellCompanionCommandExecutionOutcome(
            result=result,
            transient_status_message=context.format_recording_stopped_message(
                result.status.frames_written,
                recording_summary,
                result.stop_reason,
                context.recording_defaults.save_directory,
            ),
            failure_reflection_source_to_clear="recording",
            recording_last_summary=recording_summary,
            recording_last_stop_reason=result.stop_reason,
            recording_last_error=None,
            recording_active_frame_limit=None,
        )

    raise RuntimeError(f"Unsupported live command '{command.command_name}'.")


class LocalShellCompanionCommandExecutionError(RuntimeError):
    def __init__(self, message: str, *, outcome: LocalShellCompanionCommandExecutionOutcome) -> None:
        super().__init__(message)
        self.outcome = outcome


def _format_recording_summary(*, frames_written: int, frame_limit: int | None) -> str:
    if frame_limit is None:
        return f"{frames_written}/n"
    return f"{frames_written}/{frame_limit}"


__all__ = [
    "FailureReflectionUpdate",
    "LocalShellCompanionCommandExecutionContext",
    "LocalShellCompanionCommandExecutionError",
    "LocalShellCompanionCommandExecutionOutcome",
    "LocalShellRecordingDefaults",
    "execute_local_shell_companion_command",
]
