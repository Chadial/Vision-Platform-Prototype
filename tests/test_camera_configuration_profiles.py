from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from tests import _path_setup
from vision_platform.apps.camera_cli.camera_configuration_profiles import (
    CameraConfigurationProfileResolutionError,
    has_configuration_values,
    merge_configuration_requests,
    normalize_camera_class_name,
    resolve_camera_configuration_profile,
)
from vision_platform.models import ApplyConfigurationRequest


class CameraConfigurationProfileTests(unittest.TestCase):
    def test_normalize_camera_class_name_normalizes_hardware_model(self) -> None:
        self.assertEqual(normalize_camera_class_name("Alvium 1800 U-1240m"), "alvium_1800_u_1240m")

    def test_resolve_camera_configuration_profile_loads_default_profile(self) -> None:
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "camera_configuration_profiles.json"
            config_path.write_text(
                json.dumps(
                    {
                        "camera_classes": {
                            "alvium_1800_u_1240m": {
                                "default": {
                                    "pixel_format": "Mono8",
                                    "gain": 3.0,
                                }
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )

            resolved = resolve_camera_configuration_profile(
                profile_id="default",
                camera_class="alvium_1800_u_1240m",
                config_path=config_path,
            )

        self.assertEqual(resolved.profile_id, "default")
        self.assertEqual(resolved.camera_class, "alvium_1800_u_1240m")
        self.assertEqual(resolved.configuration.pixel_format, "Mono8")
        self.assertEqual(resolved.configuration.gain, 3.0)

    def test_resolve_camera_configuration_profile_raises_for_missing_class(self) -> None:
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "camera_configuration_profiles.json"
            config_path.write_text(json.dumps({"camera_classes": {}}), encoding="utf-8")

            with self.assertRaises(CameraConfigurationProfileResolutionError) as exc_info:
                resolve_camera_configuration_profile(
                    profile_id="default",
                    camera_class="missing_class",
                    config_path=config_path,
                )

        self.assertEqual(exc_info.exception.details["camera_class"], "missing_class")

    def test_merge_configuration_requests_prefers_explicit_overrides(self) -> None:
        merged = merge_configuration_requests(
            ApplyConfigurationRequest(pixel_format="Mono8", gain=3.0, roi_width=2000),
            ApplyConfigurationRequest(gain=5.0, roi_height=1500),
        )

        self.assertEqual(merged.pixel_format, "Mono8")
        self.assertEqual(merged.gain, 5.0)
        self.assertEqual(merged.roi_width, 2000)
        self.assertEqual(merged.roi_height, 1500)

    def test_has_configuration_values_reports_empty_request(self) -> None:
        self.assertFalse(has_configuration_values(ApplyConfigurationRequest()))
        self.assertTrue(has_configuration_values(ApplyConfigurationRequest(pixel_format="Mono8")))


if __name__ == "__main__":
    unittest.main()
