from pathlib import Path
import unittest
from unittest.mock import MagicMock

from tests import _path_setup
from camera_app.control.command_controller import CommandController
from camera_app.models.camera_configuration import CameraConfiguration
from camera_app.models.camera_status import CameraStatus
from camera_app.models.recording_request import RecordingRequest
from camera_app.models.recording_status import RecordingStatus
from camera_app.models.snapshot_request import SnapshotRequest


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

    def test_save_snapshot_raises_when_no_request_or_default_save_directory_exists(self) -> None:
        controller = CommandController(MagicMock(), MagicMock(), MagicMock())

        with self.assertRaisesRegex(ValueError, "no default save directory"):
            controller.save_snapshot(SnapshotRequest(save_directory=None, file_stem="image_001"))

    def test_get_status_returns_camera_configuration_and_recording_state(self) -> None:
        camera_service = MagicMock()
        snapshot_service = MagicMock()
        recording_service = MagicMock()
        controller = CommandController(camera_service, snapshot_service, recording_service)
        controller.set_save_directory(Path("captures/default"))

        camera_service.get_status.return_value = CameraStatus(is_initialized=True, camera_id="cam2")
        camera_service.get_last_configuration.return_value = CameraConfiguration(pixel_format="Mono8")
        recording_service.get_status.return_value = RecordingStatus(is_recording=True, frames_written=4)

        status = controller.get_status()

        self.assertEqual(status["default_save_directory"], Path("captures/default"))
        self.assertEqual(status["camera"].camera_id, "cam2")
        self.assertEqual(status["configuration"].pixel_format, "Mono8")
        self.assertEqual(status["recording"].frames_written, 4)


if __name__ == "__main__":
    unittest.main()
