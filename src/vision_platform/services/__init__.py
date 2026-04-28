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
from vision_platform.services.local_shell_command_polling_service import poll_local_shell_live_commands
from vision_platform.services.local_shell_failure_reflection_state_service import (
    FailureReflectionPayload,
    LocalShellFailureReflectionState,
)
from vision_platform.services.local_shell_projection_input_builder_service import (
    build_local_shell_recording_projection_input,
    build_local_shell_setup_projection_input,
    build_local_shell_snapshot_projection_input,
    build_local_shell_status_projection_input,
)
from vision_platform.services.local_shell_runtime_tick_coordinator import LocalShellRuntimeTickCoordinator
from vision_platform.services.local_shell_status_publication_service import publish_local_shell_status_snapshot
from vision_platform.services.local_shell_status_projection_service import (
    LocalShellRecordingProjectionInput,
    LocalShellSetupProjectionInput,
    LocalShellSnapshotProjectionInput,
    LocalShellStatusProjectionInput,
    build_local_shell_live_command_result,
    build_local_shell_recording_reflection,
    build_local_shell_save_directory_reflection,
    build_local_shell_setup_reflection,
    build_local_shell_snapshot_reflection,
    build_local_shell_status_snapshot,
    categorize_local_shell_recording_stop_reason,
    get_local_shell_recording_stop_category,
    get_local_shell_snapshot_phase,
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
    "FailureReflectionPayload",
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
    "LocalShellFailureReflectionState",
    "LocalShellRecordingDefaults",
    "LocalShellRecordingProjectionInput",
    "LocalShellRuntimeTickCoordinator",
    "LocalShellSessionMetadata",
    "LocalShellSetupProjectionInput",
    "LocalShellSnapshotProjectionInput",
    "LocalShellStatusProjectionInput",
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
    "build_local_shell_live_command_result",
    "build_local_shell_recording_reflection",
    "build_local_shell_recording_projection_input",
    "build_local_shell_setup_projection_input",
    "build_local_shell_save_directory_reflection",
    "build_local_shell_setup_reflection",
    "build_local_shell_snapshot_projection_input",
    "build_local_shell_snapshot_reflection",
    "build_local_shell_status_snapshot",
    "build_local_shell_status_projection_input",
    "build_recording_started_event",
    "build_recording_stopped_event",
    "build_snapshot_saved_event",
    "categorize_local_shell_recording_stop_reason",
    "close_live_sync_session",
    "execute_local_shell_companion_command",
    "create_live_sync_session",
    "get_local_shell_recording_stop_category",
    "get_local_shell_snapshot_phase",
    "poll_local_shell_live_commands",
    "publish_local_shell_status_snapshot",
    "read_live_status_snapshot",
    "read_pending_live_commands",
    "resolve_active_live_sync_session",
    "wait_for_live_command_result",
    "write_live_command_result",
    "write_live_status_snapshot",
]
