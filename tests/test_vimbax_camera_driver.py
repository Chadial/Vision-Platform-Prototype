import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from tests import _path_setup
from camera_app.models.camera_configuration import CameraConfiguration
from camera_app.drivers.vimbax_camera_driver import VimbaXCameraDriver


class VimbaXCameraDriverTests(unittest.TestCase):
    @patch("camera_app.drivers.vimbax_camera_driver.VmbSystem")
    def test_initialize_uses_first_camera_when_no_id_is_given(self, vmb_system_type: MagicMock) -> None:
        fake_camera = MagicMock()
        fake_camera.get_id.return_value = "CAM-001"
        fake_camera.get_name.return_value = "TestCam"
        fake_camera.get_model.return_value = "ModelA"
        fake_camera.get_serial.return_value = "SER-001"
        fake_camera.get_interface_id.return_value = "IF-001"

        fake_vmb_system = MagicMock()
        fake_vmb_system.get_all_cameras.return_value = [fake_camera]
        vmb_system_type.get_instance.return_value = fake_vmb_system

        driver = VimbaXCameraDriver()

        status = driver.initialize()

        self.assertTrue(status.is_initialized)
        self.assertEqual(status.camera_id, "CAM-001")
        self.assertEqual(status.camera_name, "TestCam")
        self.assertEqual(status.camera_model, "ModelA")
        self.assertEqual(status.camera_serial, "SER-001")
        self.assertEqual(status.interface_id, "IF-001")
        fake_vmb_system.__enter__.assert_called_once()
        fake_camera.__enter__.assert_called_once()

    @patch("camera_app.drivers.vimbax_camera_driver.VmbSystem")
    def test_initialize_uses_explicit_camera_id(self, vmb_system_type: MagicMock) -> None:
        fake_camera = MagicMock()
        fake_camera.get_id.return_value = "CAM-123"
        fake_camera.get_name.return_value = "NamedCam"
        fake_camera.get_model.return_value = "ModelB"
        fake_camera.get_serial.return_value = "SER-123"
        fake_camera.get_interface_id.return_value = "IF-123"

        fake_vmb_system = MagicMock()
        fake_vmb_system.get_camera_by_id.return_value = fake_camera
        vmb_system_type.get_instance.return_value = fake_vmb_system

        driver = VimbaXCameraDriver()

        status = driver.initialize(camera_id="CAM-123")

        self.assertEqual(status.camera_id, "CAM-123")
        fake_vmb_system.get_camera_by_id.assert_called_once_with("CAM-123")

    @patch("camera_app.drivers.vimbax_camera_driver.VmbSystem")
    def test_shutdown_closes_camera_and_system(self, vmb_system_type: MagicMock) -> None:
        fake_camera = MagicMock()
        fake_camera.get_id.return_value = "CAM-001"
        fake_camera.get_name.return_value = "TestCam"
        fake_camera.get_model.return_value = "ModelA"
        fake_camera.get_serial.return_value = "SER-001"
        fake_camera.get_interface_id.return_value = "IF-001"

        fake_vmb_system = MagicMock()
        fake_vmb_system.get_all_cameras.return_value = [fake_camera]
        vmb_system_type.get_instance.return_value = fake_vmb_system

        driver = VimbaXCameraDriver()
        driver.initialize()

        driver.shutdown()

        fake_camera.__exit__.assert_called()
        fake_vmb_system.__exit__.assert_called()

    def test_apply_configuration_sets_only_provided_features(self) -> None:
        exposure_feature = MagicMock()
        exposure_feature.is_writeable.return_value = True
        pixel_format_feature = MagicMock()
        pixel_format_feature.is_writeable.return_value = True

        fake_camera = MagicMock()
        fake_camera.get_feature_by_name.side_effect = lambda name: {
            "ExposureTime": exposure_feature,
            "PixelFormat": pixel_format_feature,
        }[name]

        driver = VimbaXCameraDriver()
        driver._camera = fake_camera

        driver.apply_configuration(
            CameraConfiguration(
                exposure_time_us=1500.0,
                pixel_format="Mono8",
            )
        )

        fake_camera.get_feature_by_name.assert_any_call("ExposureTime")
        fake_camera.get_feature_by_name.assert_any_call("PixelFormat")
        exposure_feature.set.assert_called_once_with(1500.0)
        pixel_format_feature.set.assert_called_once_with("Mono8")

    def test_apply_configuration_requires_initialized_camera(self) -> None:
        driver = VimbaXCameraDriver()

        with self.assertRaisesRegex(RuntimeError, "not initialized"):
            driver.apply_configuration(CameraConfiguration(exposure_time_us=1000.0))

    def test_apply_configuration_raises_when_feature_is_missing(self) -> None:
        fake_camera = MagicMock()
        fake_camera.get_feature_by_name.side_effect = Exception("missing")

        driver = VimbaXCameraDriver()
        driver._camera = fake_camera

        with self.assertRaisesRegex(RuntimeError, "Gain"):
            driver.apply_configuration(CameraConfiguration(gain=1.0))

    def test_apply_configuration_raises_when_feature_is_not_writeable(self) -> None:
        read_only_feature = MagicMock()
        read_only_feature.is_writeable.return_value = False

        fake_camera = MagicMock()
        fake_camera.get_feature_by_name.return_value = read_only_feature

        driver = VimbaXCameraDriver()
        driver._camera = fake_camera

        with self.assertRaisesRegex(RuntimeError, "not writeable"):
            driver.apply_configuration(CameraConfiguration(exposure_time_us=1000.0))

    def test_capture_snapshot_returns_frame_metadata_and_updates_latest_frame(self) -> None:
        fake_frame = MagicMock()
        fake_frame.get_id.return_value = 42
        fake_frame.get_timestamp.return_value = 123456789
        fake_frame.get_width.return_value = 1920
        fake_frame.get_height.return_value = 1080
        fake_frame.get_pixel_format.return_value = "Mono8"

        fake_camera = MagicMock()
        fake_camera.get_frame.return_value = fake_frame

        driver = VimbaXCameraDriver(snapshot_timeout_ms=1500)
        driver._camera = fake_camera

        captured_frame = driver.capture_snapshot()

        fake_camera.get_frame.assert_called_once_with(timeout_ms=1500)
        self.assertIs(captured_frame.raw_frame, fake_frame)
        self.assertEqual(captured_frame.frame_id, 42)
        self.assertEqual(captured_frame.camera_timestamp, 123456789)
        self.assertEqual(captured_frame.width, 1920)
        self.assertEqual(captured_frame.height, 1080)
        self.assertEqual(captured_frame.pixel_format, "Mono8")
        self.assertIs(driver.get_latest_frame(), captured_frame)
        self.assertIsInstance(captured_frame.timestamp_utc, datetime)
        self.assertEqual(captured_frame.timestamp_utc.tzinfo, timezone.utc)

    def test_capture_snapshot_requires_initialized_camera(self) -> None:
        driver = VimbaXCameraDriver()

        with self.assertRaisesRegex(RuntimeError, "not initialized"):
            driver.capture_snapshot()

    def test_capture_snapshot_raises_timeout_error(self) -> None:
        fake_camera = MagicMock()
        fake_camera.get_frame.side_effect = Exception("Frame timeout")

        driver = VimbaXCameraDriver()
        driver._camera = fake_camera

        with self.assertRaisesRegex(RuntimeError, "Timed out"):
            driver.capture_snapshot()

    def test_capture_snapshot_raises_disconnect_error(self) -> None:
        fake_camera = MagicMock()
        fake_camera.get_frame.side_effect = Exception("Camera disconnected")

        driver = VimbaXCameraDriver()
        driver._camera = fake_camera

        with self.assertRaisesRegex(RuntimeError, "disconnected"):
            driver.capture_snapshot()


if __name__ == "__main__":
    unittest.main()
