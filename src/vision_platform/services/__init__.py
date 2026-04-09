"""Service-layer namespaces for acquisition, recording, and later APIs."""

from vision_platform.services.camera_capability_service import CameraCapabilityService
from vision_platform.services.camera_configuration_validation_service import CameraConfigurationValidationService
from vision_platform.services.companion_contract_service import (
    build_companion_command_result,
    build_companion_status_snapshot,
    build_failed_companion_command_result,
)
from vision_platform.services.hardware_audit_service import HardwareAuditService

__all__ = [
    "CameraCapabilityService",
    "CameraConfigurationValidationService",
    "HardwareAuditService",
    "build_companion_command_result",
    "build_companion_status_snapshot",
    "build_failed_companion_command_result",
]
