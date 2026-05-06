from copy import deepcopy
from dataclasses import fields

from camera_app.drivers.camera_driver import CameraDriver
from camera_app.models.camera_capability_profile import CameraCapabilityProfile
from camera_app.models.camera_configuration import CameraConfiguration
from camera_app.models.camera_status import CameraStatus
from vision_platform.integrations.camera.capability_probe import DEFAULT_FEATURE_NAMES
from vision_platform.services.camera_capability_service import CameraCapabilityService
from vision_platform.services.hardware_audit_service import HardwareAuditService


class CameraService:
    def __init__(
        self,
        driver: CameraDriver,
        capability_service: CameraCapabilityService | None = None,
        hardware_audit_service: HardwareAuditService | None = None,
    ) -> None:
        self._driver = driver
        self._capability_service = capability_service or CameraCapabilityService()
        self._hardware_audit_service = hardware_audit_service
        self._last_configuration: CameraConfiguration | None = None
        self._capability_profile: CameraCapabilityProfile | None = None
        self._camera_status = CameraStatus()

    def initialize(self, camera_id: str | None = None) -> CameraStatus:
        try:
            self._camera_status = self._driver.initialize(camera_id=camera_id)
        except Exception as exc:
            self._camera_status.last_error = str(exc)
            self._record_hardware_audit_incident(
                stage="camera.initialize",
                severity="error",
                event="initialize_failed",
                message="camera initialization failed",
                exception=exc,
            )
            raise
        self._refresh_capability_profile_best_effort()
        self._record_hardware_audit_status("camera.initialize")
        return deepcopy(self._camera_status)

    def apply_configuration(self, config: CameraConfiguration) -> None:
        if not self._camera_status.is_initialized:
            raise RuntimeError("Camera is not initialized.")
        try:
            self._driver.apply_configuration(config)
        except Exception as exc:
            self._record_hardware_audit_incident(
                stage="camera.apply_configuration",
                severity="error",
                event="configuration_failed",
                message="camera configuration failed",
                exception=exc,
                details={"configuration": repr(config)},
            )
            raise
        self._last_configuration = self._merge_with_last_configuration(config)

    def shutdown(self) -> None:
        self._driver.shutdown()
        self._capability_profile = None
        self._camera_status = CameraStatus()

    def get_last_configuration(self) -> CameraConfiguration | None:
        if self._last_configuration is None:
            return None
        return deepcopy(self._last_configuration)

    def _merge_with_last_configuration(self, config: CameraConfiguration) -> CameraConfiguration:
        if self._last_configuration is None:
            return deepcopy(config)

        values = {}
        for field in fields(CameraConfiguration):
            value = getattr(config, field.name)
            values[field.name] = value if value is not None else getattr(self._last_configuration, field.name)
        return CameraConfiguration(**values)

    def get_capability_profile(self) -> CameraCapabilityProfile | None:
        if self._capability_profile is None:
            return None
        return deepcopy(self._capability_profile)

    def get_status(self) -> CameraStatus:
        driver_status = self._driver.get_status()
        driver_status.capabilities_available = self._camera_status.capabilities_available
        driver_status.capability_probe_error = self._camera_status.capability_probe_error
        self._camera_status = driver_status
        self._record_hardware_audit_status("camera.get_status")
        return deepcopy(self._camera_status)

    def _refresh_capability_profile_best_effort(self) -> None:
        self._capability_profile = None
        self._camera_status.capabilities_available = False
        self._camera_status.capability_probe_error = None

        if not self._camera_status.is_initialized or self._camera_status.source_kind != "hardware":
            return

        try:
            probe_capabilities = getattr(self._driver, "probe_capabilities", None)
            if callable(probe_capabilities):
                payload = probe_capabilities(feature_names=DEFAULT_FEATURE_NAMES)
                self._capability_profile = self._capability_service.from_probe_payload(payload)
            else:
                self._capability_profile = self._capability_service.probe_live(camera_id=self._camera_status.camera_id)
        except Exception as exc:
            self._camera_status.capability_probe_error = self._classify_capability_probe_issue(exc)
            return

        self._camera_status.capabilities_available = True

    def _record_hardware_audit_status(self, stage: str) -> None:
        if self._hardware_audit_service is None:
            return
        self._hardware_audit_service.record_camera_status(stage=stage, status=self._camera_status)

    def _record_hardware_audit_incident(
        self,
        *,
        stage: str,
        severity: str,
        event: str,
        message: str,
        exception: Exception | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        if self._hardware_audit_service is None:
            return
        if exception is not None:
            self._hardware_audit_service.record_exception(
                stage=stage,
                exc=exception,
                severity=severity,
                event=event,
                status=self._camera_status,
                details=details,
            )
            return
        self._hardware_audit_service.record_incident(
            stage=stage,
            severity=severity,
            event=event,
            message=message,
            status=self._camera_status,
            details=details,
        )

    @staticmethod
    def _classify_capability_probe_issue(exc: Exception) -> str:
        raw_message = str(exc).strip() or exc.__class__.__name__
        normalized = raw_message.lower()

        if "notavailable" in normalized or "not available" in normalized:
            return (
                "Non-blocking hardware startup warning during capability probe "
                f"(likely SDK / transport noise, camera startup still succeeded): {raw_message}"
            )

        if "already in use" in normalized or "accessed camera" in normalized:
            return (
                "Hardware capability probe could not complete because the camera was already in use: "
                f"{raw_message}"
            )

        return raw_message
