from copy import deepcopy

from camera_app.drivers.camera_driver import CameraDriver
from camera_app.models.camera_capability_profile import CameraCapabilityProfile
from camera_app.models.camera_configuration import CameraConfiguration
from camera_app.models.camera_status import CameraStatus
from vision_platform.integrations.camera.capability_probe import DEFAULT_FEATURE_NAMES
from vision_platform.services.camera_capability_service import CameraCapabilityService


class CameraService:
    def __init__(
        self,
        driver: CameraDriver,
        capability_service: CameraCapabilityService | None = None,
    ) -> None:
        self._driver = driver
        self._capability_service = capability_service or CameraCapabilityService()
        self._last_configuration: CameraConfiguration | None = None
        self._capability_profile: CameraCapabilityProfile | None = None
        self._camera_status = CameraStatus()

    def initialize(self, camera_id: str | None = None) -> CameraStatus:
        self._camera_status = self._driver.initialize(camera_id=camera_id)
        self._refresh_capability_profile_best_effort()
        return deepcopy(self._camera_status)

    def apply_configuration(self, config: CameraConfiguration) -> None:
        if not self._camera_status.is_initialized:
            raise RuntimeError("Camera is not initialized.")
        self._driver.apply_configuration(config)
        self._last_configuration = deepcopy(config)

    def shutdown(self) -> None:
        self._driver.shutdown()
        self._capability_profile = None
        self._camera_status = CameraStatus()

    def get_last_configuration(self) -> CameraConfiguration | None:
        if self._last_configuration is None:
            return None
        return deepcopy(self._last_configuration)

    def get_capability_profile(self) -> CameraCapabilityProfile | None:
        if self._capability_profile is None:
            return None
        return deepcopy(self._capability_profile)

    def get_status(self) -> CameraStatus:
        driver_status = self._driver.get_status()
        driver_status.capabilities_available = self._camera_status.capabilities_available
        driver_status.capability_probe_error = self._camera_status.capability_probe_error
        self._camera_status = driver_status
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
            self._camera_status.capability_probe_error = str(exc)
            return

        self._camera_status.capabilities_available = True
