from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import contextlib
import json
import unittest

from tests import _path_setup
from vision_platform.apps.camera_cli import main, run_cli


class CameraCliTests(unittest.TestCase):
    def test_status_command_reports_simulated_camera_and_configuration(self) -> None:
        result = run_cli(
            [
                "status",
                "--camera-id",
                "sim-cli",
                "--pixel-format",
                "Mono8",
                "--exposure-time-us",
                "2500",
            ]
        )

        self.assertEqual(result.operation, "status")
        self.assertEqual(result.source, "simulated")
        self.assertTrue(result.status.camera.is_initialized)
        self.assertEqual(result.status.camera.source_kind, "simulation")
        self.assertEqual(result.status.camera.camera_id, "sim-cli")
        self.assertIsNotNone(result.status.configuration)
        self.assertEqual(result.status.configuration.pixel_format, "Mono8")
        self.assertEqual(result.status.configuration.exposure_time_us, 2500.0)

    def test_snapshot_command_uses_new_subdirectory_save_mode(self) -> None:
        with TemporaryDirectory() as temp_dir:
            result = run_cli(
                [
                    "snapshot",
                    "--base-directory",
                    temp_dir,
                    "--save-mode",
                    "new_subdirectory",
                    "--run-name",
                    "cli_run_001",
                    "--file-stem",
                    "capture",
                ]
            )

            target_directory = Path(temp_dir) / "cli_run_001"
            self.assertEqual(result.selected_save_directory, target_directory)
            self.assertEqual(result.snapshot_path, target_directory / "capture.png")
            self.assertTrue(result.snapshot_path.exists())
            self.assertEqual(result.status.default_save_directory, target_directory)
            self.assertTrue(result.status.can_save_snapshot)

    def test_interval_capture_command_writes_bounded_frames(self) -> None:
        with TemporaryDirectory() as temp_dir:
            result = run_cli(
                [
                    "interval-capture",
                    "--base-directory",
                    temp_dir,
                    "--file-stem",
                    "interval",
                    "--interval-seconds",
                    "0.01",
                    "--frame-limit",
                    "2",
                ]
            )

            self.assertEqual(result.operation, "interval-capture")
            self.assertEqual(result.status.interval_capture.frames_written, 2)
            self.assertFalse(result.status.interval_capture.is_capturing)
            self.assertTrue((Path(temp_dir) / "interval_000000.raw").exists())
            self.assertTrue((Path(temp_dir) / "interval_000001.raw").exists())

    def test_recording_command_prints_json_summary(self) -> None:
        with TemporaryDirectory() as temp_dir:
            stdout = StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    [
                        "recording",
                        "--base-directory",
                        temp_dir,
                        "--file-stem",
                        "recording",
                        "--frame-limit",
                        "2",
                        "--target-frame-rate",
                        "8",
                    ]
                )

            payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["operation"], "recording")
            self.assertEqual(payload["source"], "simulated")
            self.assertEqual(payload["status"]["recording"]["frames_written"], 2)
            self.assertFalse(payload["status"]["recording"]["is_recording"])
            self.assertTrue((Path(temp_dir) / "recording_000000.raw").exists())
            self.assertTrue((Path(temp_dir) / "recording_000001.raw").exists())
            self.assertTrue((Path(temp_dir) / "recording_recording_log.csv").exists())

    def test_recording_command_requires_bounding_argument(self) -> None:
        with contextlib.redirect_stderr(StringIO()):
            with self.assertRaises(SystemExit):
                run_cli(
                    [
                        "recording",
                        "--base-directory",
                        "C:\\temp",
                    ]
                )


if __name__ == "__main__":
    unittest.main()
