from camera_app.drivers.camera_driver import CameraDriver


class PreviewService:
    def __init__(self, driver: CameraDriver) -> None:
        self._driver = driver

    def start(self) -> None:
        self._driver.start_acquisition()

    def stop(self) -> None:
        self._driver.stop_acquisition()

    def get_latest_frame(self):
        return self._driver.get_latest_frame()

