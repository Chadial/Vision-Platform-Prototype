"""API-adapter-facing DTO mapping kept above the shared command surface."""

from vision_platform.services.api_service.command_payloads import (
    ApiCommandEnvelopePayload,
    ApiCommandErrorPayload,
    build_error_command_payload,
    build_success_command_payload,
)
from vision_platform.services.api_service.status_payloads import (
    ApiActiveRunStatusPayload,
    ApiCameraCapabilitiesPayload,
    ApiCameraConfigurationPayload,
    ApiCameraHealthPayload,
    ApiCameraStatusPayload,
    ApiCapabilityStatePayload,
    ApiIntervalCaptureStatusPayload,
    ApiRecordingStatusPayload,
    ApiSubsystemStatusPayload,
    map_camera_capabilities_to_api_payload,
    map_camera_health_to_api_payload,
    map_subsystem_status_to_api_payload,
)

__all__ = [
    "ApiCommandEnvelopePayload",
    "ApiCommandErrorPayload",
    "ApiActiveRunStatusPayload",
    "ApiCameraCapabilitiesPayload",
    "ApiCameraConfigurationPayload",
    "ApiCameraHealthPayload",
    "ApiCameraStatusPayload",
    "ApiCapabilityStatePayload",
    "ApiIntervalCaptureStatusPayload",
    "ApiRecordingStatusPayload",
    "ApiSubsystemStatusPayload",
    "build_error_command_payload",
    "build_success_command_payload",
    "map_camera_capabilities_to_api_payload",
    "map_camera_health_to_api_payload",
    "map_subsystem_status_to_api_payload",
]
