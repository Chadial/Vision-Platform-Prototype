import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from tests import _path_setup
from vision_platform.models import CameraConfiguration
from vision_platform.integrations.camera import VimbaXCameraDriver


class VimbaXCameraDriverTests(unittest.TestCase):
    @patch("vision_platform.integrations.camera.vimbax_camera_driver.VmbSystem")
    def test_initialize_uses_first_camera_when_no_id_is_given(self, vmb_system_type: MagicMock) -> None:
        fake_camera = MagicMock()
        fake_camera.get_id.return_value = "CAM-001"
        fake_camera.get_name.return_value = "TestCam"
        fake_camera.get_model.return_value = "ModelA"
        fake_camera.get_serial.return_value = "SER-001"
        fake_camera.get_interface_id.return_value = "IF-001"
        fake_rate_feature = MagicMock()
        fake_rate_feature.is_readable.return_value = True
        fake_rate_feature.get.return_value = 8.0
        fake_rate_enable_feature = MagicMock()
        fake_rate_enable_feature.is_readable.return_value = True
        fake_rate_enable_feature.get.return_value = False
        fake_camera.get_feature_by_name.side_effect = lambda name: {
            "AcquisitionFrameRate": fake_rate_feature,
            "AcquisitionFrameRateEnable": fake_rate_enable_feature,
        }[name]

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
        self.assertEqual(status.reported_acquisition_frame_rate, 8.0)
        self.assertFalse(status.acquisition_frame_rate_enabled)
        fake_vmb_system.__enter__.assert_called_once()
        fake_camera.__enter__.assert_called_once()

    @patch("vision_platform.integrations.camera.vimbax_camera_driver.VmbSystem")
    def test_initialize_uses_explicit_camera_id(self, vmb_system_type: MagicMock) -> None:
        fake_camera = MagicMock()
        fake_camera.get_id.return_value = "CAM-123"
        fake_camera.get_name.return_value = "NamedCam"
        fake_camera.get_model.return_value = "ModelB"
        fake_camera.get_serial.return_value = "SER-123"
        fake_camera.get_interface_id.return_value = "IF-123"
        fake_rate_feature = MagicMock()
        fake_rate_feature.is_readable.return_value = True
        fake_rate_feature.get.return_value = 8.0
        fake_rate_enable_feature = MagicMock()
        fake_rate_enable_feature.is_readable.return_value = True
        fake_rate_enable_feature.get.return_value = False
        fake_camera.get_feature_by_name.side_effect = lambda name: {
            "AcquisitionFrameRate": fake_rate_feature,
            "AcquisitionFrameRateEnable": fake_rate_enable_feature,
        }[name]

        fake_vmb_system = MagicMock()
        fake_vmb_system.get_camera_by_id.return_value = fake_camera
        vmb_system_type.get_instance.return_value = fake_vmb_system

        driver = VimbaXCameraDriver()

        status = driver.initialize(camera_id="CAM-123")

        self.assertEqual(status.camera_id, "CAM-123")
        fake_vmb_system.get_camera_by_id.assert_called_once_with("CAM-123")

    @patch("vision_platform.integrations.camera.vimbax_camera_driver.VmbSystem")
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

    def test_apply_configuration_enables_and_sets_acquisition_frame_rate(self) -> None:
        frame_rate_enable_feature = MagicMock()
        frame_rate_enable_feature.is_writeable.return_value = True
        frame_rate_enable_feature.is_readable.return_value = True
        frame_rate_enable_feature.get.return_value = True
        frame_rate_feature = MagicMock()
        frame_rate_feature.is_writeable.return_value = True
        frame_rate_feature.is_readable.return_value = True
        frame_rate_feature.get.return_value = 4.999

        fake_camera = MagicMock()
        fake_camera.get_id.return_value = "CAM-001"
        fake_camera.get_name.return_value = "TestCam"
        fake_camera.get_model.return_value = "ModelA"
        fake_camera.get_serial.return_value = "SER-001"
        fake_camera.get_interface_id.return_value = "IF-001"
        fake_camera.get_feature_by_name.side_effect = lambda name: {
            "AcquisitionFrameRateEnable": frame_rate_enable_feature,
            "AcquisitionFrameRate": frame_rate_feature,
        }[name]

        driver = VimbaXCameraDriver()
        driver._camera = fake_camera
        driver._status.is_initialized = True

        driver.apply_configuration(CameraConfiguration(acquisition_frame_rate=5.0))

        frame_rate_enable_feature.set.assert_called_once_with(True)
        frame_rate_feature.set.assert_called_once_with(5.0)
        self.assertEqual(driver.get_status().reported_acquisition_frame_rate, 4.999)
        self.assertTrue(driver.get_status().acquisition_frame_rate_enabled)

    def test_apply_configuration_sets_roi_features_when_provided(self) -> None:
        offset_x_feature = MagicMock()
        offset_x_feature.is_writeable.return_value = True
        offset_y_feature = MagicMock()
        offset_y_feature.is_writeable.return_value = True
        width_feature = MagicMock()
        width_feature.is_writeable.return_value = True
        height_feature = MagicMock()
        height_feature.is_writeable.return_value = True

        fake_camera = MagicMock()
        fake_camera.get_feature_by_name.side_effect = lambda name: {
            "OffsetX": offset_x_feature,
            "OffsetY": offset_y_feature,
            "Width": width_feature,
            "Height": height_feature,
        }[name]

        driver = VimbaXCameraDriver()
        driver._camera = fake_camera

        driver.apply_configuration(
            CameraConfiguration(
                roi_offset_x=10,
                roi_offset_y=20,
                roi_width=300,
                roi_height=200,
            )
        )

        offset_x_feature.set.assert_called_once_with(10)
        offset_y_feature.set.assert_called_once_with(20)
        width_feature.set.assert_called_once_with(300)
        height_feature.set.assert_called_once_with(200)

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
