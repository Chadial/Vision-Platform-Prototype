from __future__ import annotations

import unittest

from tests import _path_setup
from vision_platform.apps.local_shell.camera_settings_service import CameraSettingsService
from vision_platform.models import ApplyConfigurationRequest
from vision_platform.services import CameraCapabilityService


class CameraSettingsServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = CameraSettingsService()

    def test_build_initial_request_uses_default_profile_when_no_current_configuration_exists(self) -> None:
        request = self.service.build_initial_request(
            current_configuration=None,
            profile_id=None,
            camera_class="1800_u_1240m",
            capability_profile=None,
        )

        self.assertEqual(request.pixel_format, "Mono10")
        self.assertIsNone(request.exposure_time_us)
        self.assertEqual(request.gain, 3.0)
        self.assertEqual(request.roi_width, 2000)
        self.assertEqual(request.roi_height, 1500)

    def test_normalize_request_clamps_values_to_capability_profile_steps_and_ranges(self) -> None:
        capability_service = CameraCapabilityService()
        capability_profile = capability_service.from_probe_payload(
            {
                "probe_utc": "2026-04-10T00:00:00+00:00",
                "camera": {
                    "camera_id": "DEV_1AB22C046D81",
                    "name": "Allied Vision 1800 U-1240m",
                    "model": "1800 U-1240m",
                    "serial": "067WH",
                    "interface_id": "VimbaUSBInterface_0x0",
                },
                "feature_count": 4,
                "features": {
                    "PixelFormat": {
                        "type": "EnumFeature",
                        "is_readable": True,
                        "is_writeable": True,
                        "value": "Mono10",
                        "entries": ["Mono8", "Mono10"],
                    },
                    "Gain": {
                        "type": "FloatFeature",
                        "is_readable": True,
                        "is_writeable": True,
                        "value": 3.0,
                        "range": [0.0, 27.0],
                        "increment": 0.1,
                    },
                    "Width": {
                        "type": "IntFeature",
                        "is_readable": True,
                        "is_writeable": True,
                        "value": 2000,
                        "range": [8, 4024],
                        "increment": 8,
                    },
                    "OffsetX": {
                        "type": "IntFeature",
                        "is_readable": True,
                        "is_writeable": True,
                        "value": 0,
                        "range": [0, 2024],
                        "increment": 2,
                    },
                },
            }
        )

        normalized = self.service.normalize_request(
            ApplyConfigurationRequest(
                pixel_format="Mono10",
                gain=3.04,
                roi_width=2001,
                roi_offset_x=17,
            ),
            capability_profile,
        )

        self.assertEqual(normalized.pixel_format, "Mono10")
        self.assertEqual(normalized.gain, 3.0)
        self.assertEqual(normalized.roi_width, 2000)
        self.assertEqual(normalized.roi_offset_x, 18)


if __name__ == "__main__":
    unittest.main()
