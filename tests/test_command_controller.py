from pathlib import Path
import unittest
from unittest.mock import MagicMock

from tests import _path_setup
from camera_app.control.command_controller import CommandController
from camera_app.models.apply_configuration_request import ApplyConfigurationRequest
from camera_app.models.camera_configuration import CameraConfiguration
from camera_app.models.camera_status import CameraStatus
from camera_app.models.recording_request import RecordingRequest
from camera_app.models.recording_status import RecordingStatus
from camera_app.models.save_snapshot_request import SaveSnapshotRequest
from camera_app.models.set_save_directory_request import SetSaveDirectoryRequest
from camera_app.models.snapshot_request import SnapshotRequest
from camera_app.models.start_recording_request import StartRecordingRequest
from camera_app.models.subsystem_status import SubsystemStatus


class CommandControllerTests(unittest.TestCase):
    def test_save_snapshot_uses_default_save_directory_when_request_has_none(self) -> None:
        camera_service = MagicMock()
        snapshot_service = MagicMock()
        recording_service = MagicMock()
        controller = CommandController(camera_service, snapshot_service, recording_service)
        controller.set_save_directory(Path("captures/default"))

        request = SnapshotRequest(save_directory=None, file_stem="image_001", file_extension=".png")
        controller.save_snapshot(request)

        resolved_request = snapshot_service.save_snapshot.call_args.args[0]
        self.assertEqual(resolved_request.save_directory, Path("captures/default"))
        self.assertEqual(resolved_request.file_stem, "image_001")

    def test_start_recording_uses_default_save_directory_when_request_has_none(self) -> None:
        camera_service = MagicMock()
        snapshot_service = MagicMock()
        recording_service = MagicMock()
        controller = CommandController(camera_service, snapshot_service, recording_service)
        controller.set_save_directory(Path("captures/default"))

        request = RecordingRequest(save_directory=None, file_stem="series", file_extension=".raw", frame_limit=3)
        controller.start_recording(request)

        resolved_request = recording_service.start_recording.call_args.args[0]
        self.assertEqual(resolved_request.save_directory, Path("captures/default"))
        self.assertEqual(resolved_request.file_stem, "series")

    def test_set_save_directory_request_can_resolve_new_subdirectory(self) -> None:
        controller = CommandController(MagicMock(), MagicMock(), MagicMock())

        controller.set_save_directory(
            SetSaveDirectoryRequest(
                base_directory=Path("captures"),
                mode="new_subdirectory",
                subdirectory_name="run_001",
            )
        )

        status = controller.get_status()

        self.assertEqual(status.default_save_directory, Path("captures/run_001"))

    def test_apply_configuration_request_maps_roi_and_exposure(self) -> None:
        camera_service = MagicMock()
        controller = CommandController(camera_service, MagicMock(), MagicMock())

        controller.apply_configuration(
            ApplyConfigurationRequest(
                exposure_time_us=2000.0,
                roi_offset_x=10,
                roi_offset_y=20,
                roi_width=300,
                roi_height=200,
            )
        )

        forwarded_config = camera_service.apply_configuration.call_args.args[0]
        self.assertEqual(forwarded_config.exposure_time_us, 2000.0)
        self.assertEqual(forwarded_config.roi_offset_x, 10)
        self.assertEqual(forwarded_config.roi_offset_y, 20)
        self.assertEqual(forwarded_config.roi_width, 300)
        self.assertEqual(forwarded_config.roi_height, 200)

    def test_save_snapshot_request_maps_to_snapshot_request(self) -> None:
        snapshot_service = MagicMock()
        controller = CommandController(MagicMock(), snapshot_service, MagicMock())
        controller.set_save_directory(Path("captures/default"))

        controller.save_snapshot(SaveSnapshotRequest(file_stem="image_001"))

        resolved_request = snapshot_service.save_snapshot.call_args.args[0]
        self.assertEqual(resolved_request.save_directory, Path("captures/default"))
        self.assertEqual(resolved_request.file_stem, "image_001")

    def test_start_recording_request_maps_target_frame_rate(self) -> None:
        recording_service = MagicMock()
        controller = CommandController(MagicMock(), MagicMock(), recording_service)
        controller.set_save_directory(Path("captures/default"))

        controller.start_recording(
            StartRecordingRequest(
                file_stem="series",
                max_frame_count=5,
                duration_seconds=2.0,
                target_frame_rate=12.5,
            )
        )

        resolved_request = recording_service.start_recording.call_args.args[0]
        self.assertEqual(resolved_request.save_directory, Path("captures/default"))
        self.assertEqual(resolved_request.frame_limit, 5)
        self.assertEqual(resolved_request.duration_seconds, 2.0)
        self.assertEqual(resolved_request.target_frame_rate, 12.5)

    def test_save_snapshot_raises_when_no_request_or_default_save_directory_exists(self) -> None:
        controller = CommandController(MagicMock(), MagicMock(), MagicMock())

        with self.assertRaisesRegex(ValueError, "no default save directory"):
            controller.save_snapshot(SnapshotRequest(save_directory=None, file_stem="image_001"))

    def test_get_status_returns_explicit_subsystem_status_model(self) -> None:
        camera_service = MagicMock()
        snapshot_service = MagicMock()
        recording_service = MagicMock()
        controller = CommandController(camera_service, snapshot_service, recording_service)
        controller.set_save_directory(Path("captures/default"))

        camera_service.get_status.return_value = CameraStatus(
            is_initialized=True,
            camera_id="cam2",
            source_kind="simulation",
            driver_name="SimulatedCameraDriver",
        )
        camera_service.get_last_configuration.return_value = CameraConfiguration(pixel_format="Mono8")
        recording_service.get_status.return_value = RecordingStatus(is_recording=True, frames_written=4)

        status = controller.get_status()

        self.assertIsInstance(status, SubsystemStatus)
        self.assertEqual(status.default_save_directory, Path("captures/default"))
        self.assertEqual(status.camera.camera_id, "cam2")
        self.assertEqual(status.camera.source_kind, "simulation")
        self.assertEqual(status.camera.driver_name, "SimulatedCameraDriver")
        self.assertEqual(status.configuration.pixel_format, "Mono8")
        self.assertEqual(status.recording.frames_written, 4)
        self.assertTrue(status.can_apply_configuration)
        self.assertFalse(status.can_start_recording)
        self.assertTrue(status.can_stop_recording)

    def test_get_status_reports_command_readiness_for_idle_initialized_camera(self) -> None:
        camera_service = MagicMock()
        snapshot_service = MagicMock()
        recording_service = MagicMock()
        controller = CommandController(camera_service, snapshot_service, recording_service)
        controller.set_save_directory(Path("captures/default"))

        camera_service.get_status.return_value = CameraStatus(is_initialized=True, camera_id="cam2")
        camera_service.get_last_configuration.return_value = None
        recording_service.get_status.return_value = RecordingStatus(is_recording=False, frames_written=0)

        status = controller.get_status()

        self.assertTrue(status.can_apply_configuration)
        self.assertTrue(status.can_save_snapshot)
        self.assertTrue(status.can_start_recording)
        self.assertFalse(status.can_stop_recording)

    def test_set_save_directory_allows_clearing_default_path(self) -> None:
        camera_service = MagicMock()
        snapshot_service = MagicMock()
        recording_service = MagicMock()
        controller = CommandController(camera_service, snapshot_service, recording_service)
        controller.set_save_directory(Path("captures/default"))
        controller.set_save_directory(None)

        camera_service.get_status.return_value = CameraStatus(is_initialized=True)
        camera_service.get_last_configuration.return_value = None
        recording_service.get_status.return_value = RecordingStatus()

        status = controller.get_status()

        self.assertIsNone(status.default_save_directory)
        self.assertFalse(status.can_save_snapshot)
        self.assertFalse(status.can_start_recording)

    def test_apply_configuration_rejects_invalid_roi(self) -> None:
        controller = CommandController(MagicMock(), MagicMock(), MagicMock())

        with self.assertRaisesRegex(ValueError, "roi_width"):
            controller.apply_configuration(ApplyConfigurationRequest(roi_width=0))


if __name__ == "__main__":
    unittest.main()
