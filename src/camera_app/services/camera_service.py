from copy import deepcopy

from camera_app.drivers.camera_driver import CameraDriver
from camera_app.models.camera_configuration import CameraConfiguration
from camera_app.models.camera_status import CameraStatus


class CameraService:
    def __init__(self, driver: CameraDriver) -> None:
        self._driver = driver
        self._last_configuration: CameraConfiguration | None = None
        self._camera_status = CameraStatus()

    def initialize(self, camera_id: str | None = None) -> CameraStatus:
        self._camera_status = self._driver.initialize(camera_id=camera_id)
        return self._camera_status

    def apply_configuration(self, config: CameraConfiguration) -> None:
        self._driver.apply_configuration(config)
        self._last_configuration = deepcopy(config)

    def shutdown(self) -> None:
        self._driver.shutdown()
        self._camera_status = CameraStatus()

    def get_last_configuration(self) -> CameraConfiguration | None:
        if self._last_configuration is None:
            return None
        return deepcopy(self._last_configuration)

    def get_status(self) -> CameraStatus:
        return deepcopy(self._camera_status)
