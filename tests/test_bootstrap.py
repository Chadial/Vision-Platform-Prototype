from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tests import _path_setup
from vision_platform import build_camera_subsystem, build_simulated_camera_subsystem
from vision_platform.integrations.camera import SimulatedCameraDriver
from vision_platform.models import (
    ApplyConfigurationRequest,
    SaveSnapshotRequest,
    SetSaveDirectoryRequest,
    StartIntervalCaptureRequest,
)


class BootstrapTests(unittest.TestCase):
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

    def test_build_simulated_camera_subsystem_supports_command_controller_interval_flow(self) -> None:
        subsystem = build_simulated_camera_subsystem()

        with TemporaryDirectory() as temp_dir:
            subsystem.camera_service.initialize(camera_id="sim-bootstrap")
            try:
                subsystem.command_controller.apply_configuration(
                    ApplyConfigurationRequest(pixel_format="Mono8")
                )
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
                    interval_status = subsystem.command_controller.start_interval_capture(
                        StartIntervalCaptureRequest(
                            file_stem="interval",
                            interval_seconds=0.02,
                            max_frame_count=2,
                            file_extension=".raw",
                        )
                    )
                    self.assertTrue(interval_status.is_capturing)

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


if __name__ == "__main__":
    unittest.main()
