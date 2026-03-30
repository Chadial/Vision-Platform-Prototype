from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep
import unittest

from camera_app.bootstrap import build_simulated_camera_subsystem as build_legacy_simulated_camera_subsystem
from tests import _path_setup
from vision_platform import build_camera_subsystem, build_simulated_camera_subsystem
from vision_platform.integrations.camera import SimulatedCameraDriver
from vision_platform.models import (
    ApplyConfigurationCommandResult,
    ApplyConfigurationRequest,
    RecordingCommandResult,
    SaveSnapshotRequest,
    SetSaveDirectoryRequest,
    StartRecordingRequest,
    StopRecordingRequest,
    StartIntervalCaptureRequest,
)
from vision_platform.services.recording_service import FrameWriter


class _FailingOnceFrameWriter:
    def __init__(self) -> None:
        self._has_failed = False

    def write_frame(self, frame, target_path: Path, create_directories: bool = True) -> None:
        if not self._has_failed:
            self._has_failed = True
            raise RuntimeError("frame write failed")

        FrameWriter().write_frame(frame, target_path, create_directories=create_directories)


class BootstrapTests(unittest.TestCase):
    def test_legacy_camera_app_bootstrap_shim_reuses_platform_bootstrap(self) -> None:
        legacy_subsystem = build_legacy_simulated_camera_subsystem()
        platform_subsystem = build_simulated_camera_subsystem()

        self.assertEqual(type(legacy_subsystem), type(platform_subsystem))
        self.assertEqual(type(legacy_subsystem.command_controller), type(platform_subsystem.command_controller))

    def test_build_camera_subsystem_wires_shared_services_consistently(self) -> None:
        subsystem = build_camera_subsystem(SimulatedCameraDriver())

        self.assertIs(subsystem.camera_service._driver, subsystem.driver)
        self.assertIs(subsystem.snapshot_service._driver, subsystem.driver)
        self.assertIs(subsystem.stream_service._driver, subsystem.driver)
        self.assertIs(subsystem.recording_service._driver, subsystem.driver)
        self.assertIs(subsystem.interval_capture_service._driver, subsystem.driver)
        self.assertIs(subsystem.command_controller._camera_service, subsystem.camera_service)
        self.assertIs(subsystem.command_controller._snapshot_service, subsystem.snapshot_service)
        self.assertIs(subsystem.command_controller._recording_service, subsystem.recording_service)
        self.assertIs(subsystem.command_controller._interval_capture_service, subsystem.interval_capture_service)

    def test_build_camera_subsystem_can_wire_focus_metadata_producers(self) -> None:
        subsystem = build_camera_subsystem(
            SimulatedCameraDriver(),
            artifact_focus_method="laplace",
            focus_score_frame_interval=5,
        )

        self.assertIsNotNone(subsystem.snapshot_service._artifact_focus_metadata_producer)
        self.assertIsNotNone(subsystem.recording_service._artifact_focus_metadata_producer)

    def test_build_simulated_camera_subsystem_supports_command_controller_interval_flow(self) -> None:
        subsystem = build_simulated_camera_subsystem()

        with TemporaryDirectory() as temp_dir:
            subsystem.camera_service.initialize(camera_id="sim-bootstrap")
            try:
                configuration_result = subsystem.command_controller.apply_configuration(
                    ApplyConfigurationRequest(pixel_format="Mono8")
                )
                self.assertIsInstance(configuration_result, ApplyConfigurationCommandResult)
                self.assertEqual(configuration_result.applied_configuration.pixel_format, "Mono8")
                subsystem.command_controller.set_save_directory(
                    SetSaveDirectoryRequest(
                        base_directory=Path(temp_dir),
                        mode="new_subdirectory",
                        subdirectory_name="run_001",
                    )
                )

                snapshot_result = subsystem.command_controller.save_snapshot(
                    SaveSnapshotRequest(file_stem="snapshot")
                )
                self.assertTrue(snapshot_result.saved_path.exists())

                subsystem.stream_service.start_preview()
                try:
                    interval_result = subsystem.command_controller.start_interval_capture(
                        StartIntervalCaptureRequest(
                            file_stem="interval",
                            interval_seconds=0.02,
                            max_frame_count=2,
                            file_extension=".raw",
                        )
                    )
                    self.assertTrue(interval_result.status.is_capturing)

                    for _ in range(200):
                        status = subsystem.command_controller.get_status()
                        if not status.interval_capture.is_capturing and status.interval_capture.frames_written == 2:
                            break
                        from time import sleep

                        sleep(0.01)

                    final_status = subsystem.command_controller.get_status()
                    self.assertEqual(final_status.interval_capture.frames_written, 2)
                    self.assertTrue(final_status.can_start_interval_capture)
                    self.assertFalse(final_status.can_stop_interval_capture)
                    self.assertTrue((Path(temp_dir) / "run_001" / "interval_000000.raw").exists())
                finally:
                    subsystem.stream_service.stop_preview()
            finally:
                subsystem.camera_service.shutdown()

    def test_build_simulated_camera_subsystem_recovers_after_recording_write_failure(self) -> None:
        subsystem = build_simulated_camera_subsystem()
        subsystem.recording_service._frame_writer = _FailingOnceFrameWriter()

        with TemporaryDirectory() as temp_dir:
            subsystem.camera_service.initialize(camera_id="sim-bootstrap")
            try:
                subsystem.command_controller.set_save_directory(
                    SetSaveDirectoryRequest(
                        base_directory=Path(temp_dir),
                        mode="append",
                    )
                )

                start_result = subsystem.command_controller.start_recording(
                    StartRecordingRequest(
                        file_stem="broken",
                        file_extension=".raw",
                        max_frame_count=2,
                    )
                )
                self.assertIsInstance(start_result, RecordingCommandResult)
                self.assertTrue(start_result.status.is_recording)

                for _ in range(200):
                    failed_status = subsystem.command_controller.get_status()
                    if not failed_status.recording.is_recording and failed_status.recording.last_error is not None:
                        break
                    sleep(0.01)

                failed_status = subsystem.command_controller.get_status()
                self.assertFalse(failed_status.recording.is_recording)
                self.assertIn("Recording write failed", failed_status.recording.last_error or "")
                self.assertTrue(failed_status.can_start_recording)
                self.assertFalse(failed_status.can_stop_recording)

                stop_after_failure = subsystem.command_controller.stop_recording(
                    StopRecordingRequest(reason="post_failure_cleanup")
                )
                second_stop_after_failure = subsystem.command_controller.stop_recording(
                    StopRecordingRequest(reason="duplicate_cleanup")
                )
                self.assertEqual(stop_after_failure.stop_reason, "post_failure_cleanup")
                self.assertEqual(second_stop_after_failure.stop_reason, "duplicate_cleanup")
                self.assertFalse(stop_after_failure.status.is_recording)
                self.assertFalse(second_stop_after_failure.status.is_recording)

                retry_result = subsystem.command_controller.start_recording(
                    StartRecordingRequest(
                        file_stem="recovered",
                        file_extension=".raw",
                        max_frame_count=2,
                    )
                )
                self.assertTrue(retry_result.status.is_recording)

                for _ in range(200):
                    status = subsystem.command_controller.get_status()
                    if not status.recording.is_recording and status.recording.frames_written == 2:
                        break
                    sleep(0.01)

                stop_after_recovery = subsystem.command_controller.stop_recording(
                    StopRecordingRequest(reason="bounded_completion")
                )
                final_status = subsystem.command_controller.get_status()

                self.assertFalse(stop_after_recovery.status.is_recording)
                self.assertIsNotNone(stop_after_recovery.status.run_id)
                self.assertEqual(stop_after_recovery.stop_reason, "bounded_completion")
                self.assertFalse(final_status.recording.is_recording)
                self.assertEqual(final_status.recording.frames_written, 2)
                self.assertIsNone(final_status.recording.last_error)
                self.assertTrue(final_status.can_start_recording)
                self.assertFalse(final_status.can_stop_recording)
                self.assertTrue((Path(temp_dir) / "recovered_000000.raw").exists())
            finally:
                subsystem.camera_service.shutdown()


if __name__ == "__main__":
    unittest.main()
