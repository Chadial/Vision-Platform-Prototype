from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import contextlib
import json
import unittest

from tests import _path_setup
from vision_platform.apps.camera_cli import CameraCliError, main, run_cli
from vision_platform.services.api_service import map_subsystem_status_to_api_payload


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

    def test_main_status_command_prints_host_envelope_with_api_status_payload(self) -> None:
        stdout = StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "status",
                    "--camera-id",
                    "sim-cli",
                    "--pixel-format",
                    "Mono8",
                ]
            )

        payload = json.loads(stdout.getvalue())
        run_result = run_cli(
            [
                "status",
                "--camera-id",
                "sim-cli",
                "--pixel-format",
                "Mono8",
            ]
        )

        self.assertEqual(exit_code, 0)
        self.assertTrue(payload["success"])
        self.assertEqual(payload["command"], "status")
        self.assertEqual(payload["source"], "simulated")
        self.assertEqual(payload["result"]["status_source"], "poll")
        self.assertEqual(payload["result"]["confirmed_settings"]["camera_id"], "sim-cli")
        self.assertEqual(payload["result"]["confirmed_settings"]["pixel_format"], "Mono8")
        self.assertEqual(payload["status"], json.loads(json.dumps(_as_serializable_api_status(run_result.status))))
        self.assertIsNone(payload["error"])

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
            self.assertTrue(payload["success"])
            self.assertEqual(payload["command"], "recording")
            self.assertEqual(payload["source"], "simulated")
            self.assertEqual(payload["result"]["stop_reason"], "bounded_completion")
            self.assertEqual(payload["result"]["selected_save_directory"], temp_dir)
            self.assertEqual(payload["result"]["recording_bounds"]["frame_limit"], 2)
            self.assertIsNone(payload["result"]["recording_bounds"]["duration_seconds"])
            self.assertEqual(payload["result"]["recording_bounds"]["target_frame_rate"], 8.0)
            self.assertEqual(payload["result"]["confirmed_settings"]["camera_id"], "simulated-camera")
            self.assertEqual(payload["status"]["recording"]["frames_written"], 2)
            self.assertFalse(payload["status"]["recording"]["is_recording"])
            self.assertTrue((Path(temp_dir) / "recording_000000.raw").exists())
            self.assertTrue((Path(temp_dir) / "recording_000001.raw").exists())
            self.assertTrue((Path(temp_dir) / "recording_recording_log.csv").exists())

    def test_run_cli_raises_camera_cli_error_for_invalid_recording_arguments(self) -> None:
        with self.assertRaises(CameraCliError) as exc_info:
            run_cli(
                [
                    "recording",
                    "--base-directory",
                    "C:\\temp",
                ]
            )

        self.assertEqual(exc_info.exception.error_type, "argument_error")

    def test_main_prints_machine_readable_error_envelope_for_invalid_recording_arguments(self) -> None:
        stdout = StringIO()
        stderr = StringIO()

        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = main(
                [
                    "recording",
                    "--base-directory",
                    "C:\\temp",
                ]
            )

        payload = json.loads(stderr.getvalue())
        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertFalse(payload["success"])
        self.assertIsNone(payload["status"])
        self.assertEqual(payload["error"]["code"], "argument_error")
        self.assertIn("--frame-limit", payload["error"]["message"])


def _as_serializable_api_status(status):
    return json.loads(json.dumps(_to_json_ready(map_subsystem_status_to_api_payload(status))))


def _to_json_ready(value):
    if isinstance(value, dict):
        return {str(key): _to_json_ready(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_json_ready(item) for item in value]
    if hasattr(value, "__dataclass_fields__"):
        return {key: _to_json_ready(getattr(value, key)) for key in value.__dataclass_fields__}
    return value


if __name__ == "__main__":
    unittest.main()
