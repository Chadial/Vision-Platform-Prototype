from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tests import _path_setup
from vision_platform.apps.camera_cli import CameraCliError, run_cli


class HardwareCliSmokeTests(unittest.TestCase):
    def test_hardware_status_smoke_for_tested_camera(self) -> None:
        try:
            result = run_cli(
                [
                    "status",
                    "--source",
                    "hardware",
                    "--camera-alias",
                    "tested_camera",
                ]
            )
        except (CameraCliError, RuntimeError) as exc:
            _skip_if_tested_hardware_is_unavailable(exc)
            raise

        self.assertEqual(result.operation, "status")
        self.assertEqual(result.source, "hardware")
        self.assertTrue(result.status.camera.is_initialized)
        self.assertEqual(result.status.camera.camera_id, "DEV_1AB22C046D81")

    def test_hardware_snapshot_smoke_for_tested_camera(self) -> None:
        with TemporaryDirectory() as temp_dir:
            try:
                result = run_cli(
                    [
                        "snapshot",
                        "--source",
                        "hardware",
                        "--camera-alias",
                        "tested_camera",
                        "--configuration-profile",
                        "default",
                        "--base-directory",
                        temp_dir,
                        "--file-stem",
                        "hardware_smoke_snapshot",
                        "--file-extension",
                        ".bmp",
                    ]
                )
            except (CameraCliError, RuntimeError) as exc:
                _skip_if_tested_hardware_is_unavailable(exc)
                raise

        self.assertEqual(result.operation, "snapshot")
        self.assertEqual(result.source, "hardware")
        self.assertTrue(result.snapshot_path.exists())
        self.assertEqual(result.snapshot_path.suffix, ".bmp")
        self.assertEqual(result.status.camera.camera_id, "DEV_1AB22C046D81")
        self.assertEqual(result.selected_save_directory, Path(temp_dir))


def _skip_if_tested_hardware_is_unavailable(exc: Exception) -> None:
    message = str(exc)
    if (
        "No Camera with Id 'DEV_1AB22C046D81' available." in message
        or "Failed to initialize camera driver" in message
    ):
        raise unittest.SkipTest("Tested real camera path is not available locally.")


if __name__ == "__main__":
    unittest.main()
