"""Service-layer namespaces for acquisition, recording, and later APIs."""

from vision_platform.services.artifact_reference_service import (
    build_artifact_reference,
    build_artifact_reference_from_trace_row,
    build_time_context_from_captured_frame,
)
from vision_platform.services.camera_capability_service import CameraCapabilityService
from vision_platform.services.camera_configuration_validation_service import CameraConfigurationValidationService
from vision_platform.services.camera_health_service import CameraHealthService
from vision_platform.services.camera_runtime_event_service import (
    build_configuration_applied_event,
    build_faulted_event,
    build_health_changed_event,
    build_recording_started_event,
    build_recording_stopped_event,
    build_snapshot_saved_event,
)
from vision_platform.services.companion_contract_service import (
    build_companion_command_result,
    build_companion_status_snapshot,
    build_failed_companion_command_result,
)
from vision_platform.services.hardware_audit_service import HardwareAuditService
from vision_platform.services.local_shell_session_protocol import (
    LocalShellActiveSessionMetadata,
    LocalShellLiveCommandResult,
    LocalShellLiveStatusSnapshot,
    LocalShellSessionMetadata,
)
from vision_platform.services.local_shell_command_execution_service import (
    FailureReflectionUpdate,
    LocalShellCompanionCommandExecutionContext,
    LocalShellCompanionCommandExecutionError,
    LocalShellCompanionCommandExecutionOutcome,
    LocalShellRecordingDefaults,
    execute_local_shell_companion_command,
)
from vision_platform.services.local_shell_session_service import (
    LocalShellLiveCommand,
    LocalShellLiveSyncError,
    LocalShellLiveSyncSession,
    append_live_command,
    close_live_sync_session,
    create_live_sync_session,
    read_live_status_snapshot,
    read_pending_live_commands,
    resolve_active_live_sync_session,
    wait_for_live_command_result,
    write_live_command_result,
    write_live_status_snapshot,
)

__all__ = [
    "CameraHealthService",
    "CameraCapabilityService",
    "CameraConfigurationValidationService",
    "HardwareAuditService",
    "FailureReflectionUpdate",
    "LocalShellActiveSessionMetadata",
    "LocalShellCompanionCommandExecutionContext",
    "LocalShellCompanionCommandExecutionError",
    "LocalShellCompanionCommandExecutionOutcome",
    "LocalShellLiveCommand",
    "LocalShellLiveCommandResult",
    "LocalShellLiveSyncError",
    "LocalShellLiveSyncSession",
    "LocalShellLiveStatusSnapshot",
    "LocalShellRecordingDefaults",
    "LocalShellSessionMetadata",
    "append_live_command",
    "build_artifact_reference",
    "build_artifact_reference_from_trace_row",
    "build_time_context_from_captured_frame",
    "build_configuration_applied_event",
    "build_companion_command_result",
    "build_companion_status_snapshot",
    "build_faulted_event",
    "build_failed_companion_command_result",
    "build_health_changed_event",
    "build_recording_started_event",
    "build_recording_stopped_event",
    "build_snapshot_saved_event",
    "close_live_sync_session",
    "execute_local_shell_companion_command",
    "create_live_sync_session",
    "read_live_status_snapshot",
    "read_pending_live_commands",
    "resolve_active_live_sync_session",
    "wait_for_live_command_result",
    "write_live_command_result",
    "write_live_status_snapshot",
]
