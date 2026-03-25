from camera_app.drivers.camera_driver import CameraDriver
from camera_app.models.camera_configuration import CameraConfiguration
from camera_app.models.camera_status import CameraStatus


class CameraService:
    def __init__(self, driver: CameraDriver) -> None:
        self._driver = driver

    def initialize(self, camera_id: str | None = None) -> CameraStatus:
        return self._driver.initialize(camera_id=camera_id)

    def apply_configuration(self, config: CameraConfiguration) -> None:
        self._driver.apply_configuration(config)

    def shutdown(self) -> None:
        self._driver.shutdown()

