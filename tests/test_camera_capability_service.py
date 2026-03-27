from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest
from unittest.mock import patch

from tests import _path_setup
from vision_platform.services import CameraCapabilityService


class CameraCapabilityServiceTests(unittest.TestCase):
    def test_from_probe_payload_normalizes_numeric_and_enum_features(self) -> None:
        service = CameraCapabilityService()
        profile = service.from_probe_payload(
            {
                "probe_utc": "2026-03-27T14:47:00+00:00",
                "camera": {
                    "camera_id": "CAM-001",
                    "name": "TestCam",
                    "model": "ModelA",
                    "serial": "SER-001",
                    "interface_id": "IF-001",
                },
                "software": {"vmbpy_version": "1.2.1"},
                "feature_count": 2,
                "features": {
                    "ExposureTime": {
                        "type": "FloatFeature",
                        "is_readable": True,
                        "is_writeable": True,
                        "value": 1000.0,
                        "range": [10.0, 2000.0],
                        "increment": 5.0,
                    },
                    "PixelFormat": {
                        "type": "EnumFeature",
                        "is_readable": True,
                        "is_writeable": True,
                        "value": "Mono8",
                        "entries": ["Mono8", "Mono10"],
                    },
                },
            }
        )

        self.assertEqual(profile.camera_id, "CAM-001")
        self.assertEqual(profile.software["vmbpy_version"], "1.2.1")
        exposure = profile.require_feature("ExposureTime")
        self.assertTrue(exposure.is_numeric)
        self.assertEqual(exposure.minimum, 10.0)
        self.assertEqual(exposure.maximum, 2000.0)
        pixel_format = profile.require_feature("PixelFormat")
        self.assertTrue(pixel_format.is_enum)
        self.assertEqual(pixel_format.entries, ("Mono8", "Mono10"))

    def test_load_json_reads_profile_from_disk(self) -> None:
        service = CameraCapabilityService()
        payload = {
            "probe_utc": "2026-03-27T14:47:00+00:00",
            "camera": {
                "camera_id": "CAM-001",
                "name": "TestCam",
                "model": "ModelA",
                "serial": "SER-001",
                "interface_id": "IF-001",
            },
            "feature_count": 1,
            "features": {
                "Gain": {
                    "type": "FloatFeature",
                    "is_readable": True,
                    "is_writeable": True,
                    "value": 3.0,
                    "range": [0.0, 27.0],
                }
            },
        }

        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "camera.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            profile = service.load_json(path)

        self.assertEqual(profile.camera_model, "ModelA")
        self.assertEqual(profile.require_feature("Gain").maximum, 27.0)

    @patch("vision_platform.services.camera_capability_service.probe_camera_capabilities")
    def test_probe_live_uses_probe_function(self, probe_camera_capabilities_mock) -> None:
        probe_camera_capabilities_mock.return_value = {
            "probe_utc": None,
            "camera": {
                "camera_id": "CAM-002",
                "name": "LiveCam",
                "model": "ModelB",
                "serial": "SER-002",
                "interface_id": "IF-002",
            },
            "feature_count": 0,
            "features": {},
        }

        service = CameraCapabilityService()
        profile = service.probe_live(camera_id="CAM-002", feature_names=("ExposureTime",))

        probe_camera_capabilities_mock.assert_called_once_with(camera_id="CAM-002", feature_names=("ExposureTime",))
        self.assertEqual(profile.camera_name, "LiveCam")


if __name__ == "__main__":
    unittest.main()
