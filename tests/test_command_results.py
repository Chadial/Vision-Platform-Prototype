from pathlib import Path
import unittest

from tests import _path_setup
from vision_platform.models import (
    ApplyConfigurationCommandResult,
    CameraConfiguration,
    IntervalCaptureCommandResult,
    IntervalCaptureStatus,
    RecordingCommandResult,
    RecordingStatus,
    SaveDirectoryCommandResult,
    SnapshotCommandResult,
)


class CommandResultFactoryTests(unittest.TestCase):
    def test_apply_configuration_result_can_be_built_from_configuration(self) -> None:
        configuration = CameraConfiguration(pixel_format="Mono8", roi_width=320)

        result = ApplyConfigurationCommandResult.from_applied_configuration(configuration)

        self.assertEqual(result.applied_configuration, configuration)

    def test_save_directory_result_can_represent_selection_or_clearing(self) -> None:
        selected = SaveDirectoryCommandResult.selected(Path("captures"))
        cleared = SaveDirectoryCommandResult.cleared()

        self.assertEqual(selected.selected_directory, Path("captures"))
        self.assertFalse(selected.was_cleared)
        self.assertIsNone(cleared.selected_directory)
        self.assertTrue(cleared.was_cleared)

    def test_snapshot_result_can_be_built_from_saved_path(self) -> None:
        result = SnapshotCommandResult.from_saved_path(Path("captures/image.png"))

        self.assertEqual(result.saved_path, Path("captures/image.png"))

    def test_recording_result_can_be_built_from_status(self) -> None:
        status = RecordingStatus(is_recording=False, frames_written=7)

        result = RecordingCommandResult.from_status(status, stop_reason="operator_cancelled")

        self.assertEqual(result.status, status)
        self.assertEqual(result.stop_reason, "operator_cancelled")

    def test_interval_capture_result_can_be_built_from_status(self) -> None:
        status = IntervalCaptureStatus(is_capturing=False, frames_written=4)

        result = IntervalCaptureCommandResult.from_status(status, stop_reason="host_shutdown")

        self.assertEqual(result.status, status)
        self.assertEqual(result.stop_reason, "host_shutdown")


if __name__ == "__main__":
    unittest.main()
