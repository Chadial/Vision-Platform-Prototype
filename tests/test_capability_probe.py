from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest
from unittest.mock import MagicMock, patch

from tests import _path_setup
from vision_platform.integrations.camera.capability_probe import (
    probe_camera_capabilities,
    probe_open_camera_capabilities,
    select_camera_from_system,
    write_camera_capabilities_json,
)


class CapabilityProbeTests(unittest.TestCase):
    def test_probe_open_camera_capabilities_serializes_selected_features_without_system_open(self) -> None:
        exposure_feature = MagicMock()
        exposure_feature.is_readable.return_value = True
        exposure_feature.is_writeable.return_value = True
        exposure_feature.get.return_value = 1000.0

        fake_camera = MagicMock()
        fake_camera.get_id.return_value = "CAM-001"
        fake_camera.get_name.return_value = "TestCam"
        fake_camera.get_model.return_value = "ModelA"
        fake_camera.get_serial.return_value = "SER-001"
        fake_camera.get_interface_id.return_value = "IF-001"
        fake_camera.get_all_features.return_value = [object()]
        fake_camera.get_feature_by_name.return_value = exposure_feature

        payload = probe_open_camera_capabilities(fake_camera, feature_names=("ExposureTime",))

        self.assertEqual(payload["camera"]["camera_id"], "CAM-001")
        self.assertEqual(payload["feature_count"], 1)
        self.assertEqual(payload["features"]["ExposureTime"]["value"], 1000.0)

    @patch("vision_platform.integrations.camera.capability_probe.VmbSystem")
    def test_probe_camera_capabilities_serializes_selected_features(self, vmb_system_type: MagicMock) -> None:
        exposure_feature = MagicMock()
        exposure_feature.is_readable.return_value = True
        exposure_feature.is_writeable.return_value = True
        exposure_feature.get.return_value = 1000.0
        exposure_feature.get_range.return_value = (10.0, 2000.0)
        exposure_feature.get_increment.return_value = 5.0

        pixel_format_feature = MagicMock()
        pixel_format_feature.is_readable.return_value = True
        pixel_format_feature.is_writeable.return_value = True
        pixel_format_feature.get.return_value = "Mono8"
        pixel_format_feature.get_available_entries.return_value = ["Mono8", "Mono10"]

        fake_camera = MagicMock()
        fake_camera.get_id.return_value = "CAM-001"
        fake_camera.get_name.return_value = "TestCam"
        fake_camera.get_model.return_value = "ModelA"
        fake_camera.get_serial.return_value = "SER-001"
        fake_camera.get_interface_id.return_value = "IF-001"
        fake_camera.get_all_features.return_value = [object(), object(), object()]
        fake_camera.get_feature_by_name.side_effect = lambda name: {
            "ExposureTime": exposure_feature,
            "PixelFormat": pixel_format_feature,
        }[name]
        fake_camera.__enter__.return_value = fake_camera

        fake_vmb_system = MagicMock()
        fake_vmb_system.get_all_cameras.return_value = [fake_camera]
        fake_vmb_system.__enter__.return_value = fake_vmb_system
        vmb_system_type.get_instance.return_value = fake_vmb_system

        payload = probe_camera_capabilities(feature_names=("ExposureTime", "PixelFormat"))

        self.assertEqual(payload["camera"]["camera_id"], "CAM-001")
        self.assertEqual(payload["feature_count"], 3)
        self.assertEqual(payload["features"]["ExposureTime"]["value"], 1000.0)
        self.assertEqual(payload["features"]["ExposureTime"]["range"], [10.0, 2000.0])
        self.assertEqual(payload["features"]["PixelFormat"]["entries"], ["Mono8", "Mono10"])

    @patch("vision_platform.integrations.camera.capability_probe.VmbSystem")
    def test_write_camera_capabilities_json_writes_file(self, vmb_system_type: MagicMock) -> None:
        feature = MagicMock()
        feature.is_readable.return_value = True
        feature.is_writeable.return_value = False
        feature.get.return_value = "Allied Vision"

        fake_camera = MagicMock()
        fake_camera.get_id.return_value = "CAM-001"
        fake_camera.get_name.return_value = "TestCam"
        fake_camera.get_model.return_value = "ModelA"
        fake_camera.get_serial.return_value = "SER-001"
        fake_camera.get_interface_id.return_value = "IF-001"
        fake_camera.get_all_features.return_value = [object()]
        fake_camera.get_feature_by_name.return_value = feature
        fake_camera.__enter__.return_value = fake_camera

        fake_vmb_system = MagicMock()
        fake_vmb_system.get_all_cameras.return_value = [fake_camera]
        fake_vmb_system.__enter__.return_value = fake_vmb_system
        vmb_system_type.get_instance.return_value = fake_vmb_system

        with TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "camera.json"
            result_path = write_camera_capabilities_json(target, feature_names=("DeviceVendorName",))

            self.assertEqual(result_path, target)
            payload = json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(payload["camera"]["model"], "ModelA")
            self.assertEqual(payload["features"]["DeviceVendorName"]["value"], "Allied Vision")

    def test_select_camera_from_system_prefers_richer_duplicate_identity(self) -> None:
        richer_camera = MagicMock()
        richer_camera.get_id.return_value = "CAM-123"
        richer_camera.get_serial.return_value = "SER-123"
        richer_camera.get_name.return_value = "NamedCam"
        richer_camera.get_model.return_value = "ModelB"
        richer_camera.get_interface_id.return_value = "IF-123"

        duplicate_camera = MagicMock()
        duplicate_camera.get_id.return_value = "CAM-123"
        duplicate_camera.get_serial.return_value = "N/A"
        duplicate_camera.get_name.return_value = "NamedCam"
        duplicate_camera.get_model.return_value = "ModelB"
        duplicate_camera.get_interface_id.return_value = "IF-123"

        fake_vmb_system = MagicMock()
        fake_vmb_system.get_all_cameras.return_value = [duplicate_camera, richer_camera]

        selected_camera = select_camera_from_system(fake_vmb_system, camera_id="CAM-123")

        self.assertIs(selected_camera, richer_camera)
        fake_vmb_system.get_camera_by_id.assert_not_called()


if __name__ == "__main__":
    unittest.main()
