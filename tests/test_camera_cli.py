from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import contextlib
import json
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

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
        self.assertIsNone(payload["status"]["active_run"])
        self.assertIsNone(payload["error"])

    def test_status_command_accepts_camera_alias(self) -> None:
        result = run_cli(
            [
                "status",
                "--camera-alias",
                "tested_camera",
            ]
        )

        self.assertEqual(result.operation, "status")
        self.assertEqual(result.status.camera.camera_id, "DEV_1AB22C046D81")

    def test_status_command_applies_named_configuration_profile(self) -> None:
        result = run_cli(
            [
                "status",
                "--camera-id",
                "sim-cli",
                "--configuration-profile",
                "default",
                "--profile-camera-class",
                "alvium_1800_u_1240m",
            ]
        )

        self.assertEqual(result.status.configuration.pixel_format, "Mono8")
        self.assertEqual(result.status.configuration.exposure_time_us, 10031.291)
        self.assertEqual(result.status.configuration.gain, 3.0)
        self.assertEqual(result.status.configuration.roi_width, 2000)
        self.assertEqual(result.status.configuration.roi_height, 1500)

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

    def test_snapshot_command_prints_confirmed_result_subset(self) -> None:
        with TemporaryDirectory() as temp_dir:
            stdout = StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    [
                        "snapshot",
                        "--base-directory",
                        temp_dir,
                        "--file-stem",
                        "capture",
                        "--file-extension",
                        ".bmp",
                        "--camera-id",
                        "sim-confirm",
                        "--pixel-format",
                        "Mono8",
                        "--exposure-time-us",
                        "1500",
                    ]
                )

            payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["success"])
            self.assertEqual(payload["result"]["run_id"], "capture")
            self.assertEqual(payload["result"]["confirmed_settings"]["camera_id"], "sim-confirm")
            self.assertEqual(payload["result"]["confirmed_settings"]["run_id"], "capture")
            self.assertEqual(payload["result"]["confirmed_settings"]["pixel_format"], "Mono8")
            self.assertEqual(payload["result"]["confirmed_settings"]["exposure_time_us"], 1500.0)
            self.assertEqual(payload["result"]["confirmed_settings"]["resolved_save_directory"], temp_dir)
            self.assertEqual(payload["result"]["confirmed_settings"]["resolved_file_stem"], "capture")
            self.assertEqual(payload["result"]["confirmed_settings"]["resolved_file_extension"], ".bmp")

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
            self.assertEqual(result.result["selected_save_directory"], Path(temp_dir))
            self.assertEqual(result.result["frames_written"], 2)
            self.assertEqual(result.result["stop_reason"], "bounded_completion")
            self.assertEqual(result.result["capture_bounds"]["frame_limit"], 2)
            self.assertIsNone(result.result["capture_bounds"]["duration_seconds"])
            self.assertEqual(result.result["capture_bounds"]["interval_seconds"], 0.01)
            self.assertEqual(result.result["confirmed_settings"]["camera_id"], "simulated-camera")
            self.assertEqual(result.result["confirmed_settings"]["resolved_save_directory"], Path(temp_dir))
            self.assertEqual(result.result["confirmed_settings"]["resolved_file_stem"], "interval")
            self.assertEqual(result.result["confirmed_settings"]["resolved_file_extension"], ".raw")
            self.assertEqual(result.result["confirmed_settings"]["accepted_frame_limit"], 2)
            self.assertIsNone(result.result["confirmed_settings"]["accepted_duration_seconds"])
            self.assertEqual(result.result["confirmed_settings"]["accepted_interval_seconds"], 0.01)
            self.assertTrue((Path(temp_dir) / "interval_000000.raw").exists())
            self.assertTrue((Path(temp_dir) / "interval_000001.raw").exists())

    def test_interval_capture_command_prints_json_summary(self) -> None:
        with TemporaryDirectory() as temp_dir:
            stdout = StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(
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

            payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["success"])
            self.assertEqual(payload["command"], "interval-capture")
            self.assertEqual(payload["source"], "simulated")
            self.assertEqual(payload["result"]["selected_save_directory"], temp_dir)
            self.assertEqual(payload["result"]["frames_written"], 2)
            self.assertEqual(payload["result"]["stop_reason"], "bounded_completion")
            self.assertEqual(payload["result"]["capture_bounds"]["frame_limit"], 2)
            self.assertIsNone(payload["result"]["capture_bounds"]["duration_seconds"])
            self.assertEqual(payload["result"]["capture_bounds"]["interval_seconds"], 0.01)
            self.assertEqual(payload["result"]["confirmed_settings"]["camera_id"], "simulated-camera")
            self.assertEqual(payload["result"]["confirmed_settings"]["resolved_save_directory"], temp_dir)
            self.assertEqual(payload["result"]["confirmed_settings"]["resolved_file_stem"], "interval")
            self.assertEqual(payload["result"]["confirmed_settings"]["resolved_file_extension"], ".raw")
            self.assertEqual(payload["result"]["confirmed_settings"]["accepted_frame_limit"], 2)
            self.assertIsNone(payload["result"]["confirmed_settings"]["accepted_duration_seconds"])
            self.assertEqual(payload["result"]["confirmed_settings"]["accepted_interval_seconds"], 0.01)
            self.assertEqual(payload["status"]["interval_capture"]["frames_written"], 2)
            self.assertFalse(payload["status"]["interval_capture"]["is_capturing"])

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
            self.assertTrue(payload["result"]["run_id"].startswith("recording@"))
            self.assertEqual(payload["result"]["stop_reason"], "bounded_completion")
            self.assertEqual(payload["result"]["selected_save_directory"], temp_dir)
            self.assertEqual(payload["result"]["recording_bounds"]["frame_limit"], 2)
            self.assertIsNone(payload["result"]["recording_bounds"]["duration_seconds"])
            self.assertEqual(payload["result"]["recording_bounds"]["target_frame_rate"], 8.0)
            self.assertEqual(payload["result"]["confirmed_settings"]["camera_id"], "simulated-camera")
            self.assertEqual(payload["result"]["confirmed_settings"]["run_id"], payload["result"]["run_id"])
            self.assertEqual(payload["result"]["confirmed_settings"]["resolved_save_directory"], temp_dir)
            self.assertEqual(payload["result"]["confirmed_settings"]["resolved_file_stem"], "recording")
            self.assertEqual(payload["result"]["confirmed_settings"]["resolved_file_extension"], ".raw")
            self.assertEqual(payload["result"]["confirmed_settings"]["accepted_frame_limit"], 2)
            self.assertIsNone(payload["result"]["confirmed_settings"]["accepted_duration_seconds"])
            self.assertEqual(payload["result"]["confirmed_settings"]["accepted_target_frame_rate"], 8.0)
            self.assertIsNone(payload["status"]["recording"]["run_id"])
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

    def test_main_prints_camera_selection_error_for_unknown_camera_alias(self) -> None:
        stdout = StringIO()
        stderr = StringIO()

        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = main(
                [
                    "status",
                    "--camera-alias",
                    "missing_camera",
                ]
            )

        payload = json.loads(stderr.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertFalse(payload["success"])
        self.assertEqual(payload["error"]["code"], "camera_selection_error")
        self.assertEqual(payload["error"]["details"]["camera_alias"], "missing_camera")

    def test_main_prints_camera_selection_error_for_combined_camera_id_and_alias(self) -> None:
        stdout = StringIO()
        stderr = StringIO()

        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = main(
                [
                    "status",
                    "--camera-id",
                    "DEV_DIRECT",
                    "--camera-alias",
                    "tested_camera",
                ]
            )

        payload = json.loads(stderr.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertFalse(payload["success"])
        self.assertEqual(payload["error"]["code"], "camera_selection_error")
        self.assertEqual(payload["error"]["details"]["camera_id"], "DEV_DIRECT")
        self.assertEqual(payload["error"]["details"]["camera_alias"], "tested_camera")

    @patch("vision_platform.apps.camera_cli.camera_cli._build_subsystem_for_args")
    def test_main_prints_configuration_error_envelope_for_invalid_roi_configuration(
        self,
        build_subsystem_mock,
    ) -> None:
        camera_service = MagicMock()
        command_controller = MagicMock()
        command_controller.apply_configuration.side_effect = ValueError(
            "CameraConfiguration.roi_width=2001 is invalid for camera feature 'Width': "
            "value must align to increment 8 from base 8; allowed range 8..4024; nearest valid values: 2000, 2008."
        )
        build_subsystem_mock.return_value = SimpleNamespace(
            camera_service=camera_service,
            command_controller=command_controller,
        )

        stdout = StringIO()
        stderr = StringIO()

        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = main(
                [
                    "status",
                    "--source",
                    "hardware",
                    "--camera-id",
                    "CAM-001",
                    "--roi-width",
                    "2001",
                ]
            )

        payload = json.loads(stderr.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertFalse(payload["success"])
        self.assertEqual(payload["error"]["code"], "configuration_error")
        self.assertEqual(payload["error"]["details"]["stage"], "apply_configuration")
        self.assertIn("roi_width=2001", payload["error"]["message"])
        camera_service.initialize.assert_called_once_with(camera_id="CAM-001")
        camera_service.shutdown.assert_called_once_with()

    @patch("vision_platform.apps.camera_cli.camera_cli._build_subsystem_for_args")
    def test_snapshot_command_merges_named_profile_and_passes_profile_identity(
        self,
        build_subsystem_mock,
    ) -> None:
        camera_service = MagicMock()
        camera_service.initialize.return_value = SimpleNamespace(
            is_initialized=True,
            camera_id="CAM-001",
            camera_model="Alvium 1800 U-1240m",
        )
        command_controller = MagicMock()
        command_controller.set_save_directory.return_value = SimpleNamespace(selected_directory=Path("captures/profile"))
        command_controller.save_snapshot.return_value = SimpleNamespace(saved_path=Path("captures/profile/image.bmp"))
        command_controller.get_status.return_value = SimpleNamespace(
            camera=SimpleNamespace(camera_id="CAM-001"),
            configuration=SimpleNamespace(pixel_format="Mono8", exposure_time_us=10031.291),
        )
        build_subsystem_mock.return_value = SimpleNamespace(
            camera_service=camera_service,
            command_controller=command_controller,
        )

        run_cli(
            [
                "snapshot",
                "--source",
                "hardware",
                "--camera-id",
                "CAM-001",
                "--base-directory",
                "captures",
                "--file-extension",
                ".bmp",
                "--configuration-profile",
                "default",
                "--gain",
                "5.0",
            ]
        )

        applied_request = command_controller.apply_configuration.call_args.args[0]
        snapshot_request = command_controller.save_snapshot.call_args.args[0]
        self.assertEqual(applied_request.pixel_format, "Mono8")
        self.assertEqual(applied_request.exposure_time_us, 10031.291)
        self.assertEqual(applied_request.gain, 5.0)
        self.assertEqual(applied_request.roi_width, 2000)
        self.assertEqual(snapshot_request.configuration_profile_id, "default")
        self.assertEqual(snapshot_request.configuration_profile_camera_class, "alvium_1800_u_1240m")

    @patch("vision_platform.apps.camera_cli.camera_cli._build_subsystem_for_args")
    def test_main_prints_configuration_error_for_unknown_configuration_profile_class(
        self,
        build_subsystem_mock,
    ) -> None:
        camera_service = MagicMock()
        camera_service.initialize.return_value = SimpleNamespace(
            is_initialized=True,
            camera_id="CAM-001",
            camera_model="Unknown Camera",
        )
        command_controller = MagicMock()
        build_subsystem_mock.return_value = SimpleNamespace(
            camera_service=camera_service,
            command_controller=command_controller,
        )

        stdout = StringIO()
        stderr = StringIO()

        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = main(
                [
                    "status",
                    "--source",
                    "hardware",
                    "--camera-id",
                    "CAM-001",
                    "--configuration-profile",
                    "default",
                    "--profile-camera-class",
                    "missing_class",
                ]
            )

        payload = json.loads(stderr.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertFalse(payload["success"])
        self.assertEqual(payload["error"]["code"], "configuration_error")
        self.assertEqual(payload["error"]["details"]["stage"], "load_configuration_profile")
        self.assertEqual(payload["error"]["details"]["camera_class"], "missing_class")
        camera_service.shutdown.assert_called_once_with()


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
