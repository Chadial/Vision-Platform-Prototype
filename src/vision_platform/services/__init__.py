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

__all__ = [
    "CameraHealthService",
    "CameraCapabilityService",
    "CameraConfigurationValidationService",
    "HardwareAuditService",
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
]
