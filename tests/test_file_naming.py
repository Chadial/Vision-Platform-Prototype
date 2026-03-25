from pathlib import Path
import unittest

from tests import _path_setup
from camera_app.models.recording_request import RecordingRequest
from camera_app.models.snapshot_request import SnapshotRequest
from camera_app.storage.file_naming import build_recording_frame_path, build_recording_log_path, build_snapshot_path


class FileNamingTests(unittest.TestCase):
    def test_build_snapshot_path_appends_extension(self) -> None:
        request = SnapshotRequest(save_directory=Path("captures"), file_stem="image_001", file_extension="png")
        self.assertEqual(build_snapshot_path(request), Path("captures/image_001.png"))

    def test_build_recording_frame_path_uses_zero_padded_index(self) -> None:
        request = RecordingRequest(
            save_directory=Path("captures"),
            file_stem="series",
            file_extension="raw",
            frame_limit=3,
        )
        self.assertEqual(build_recording_frame_path(request, 12), Path("captures/series_000012.raw"))

    def test_build_recording_log_path_uses_deterministic_name(self) -> None:
        request = RecordingRequest(
            save_directory=Path("captures"),
            file_stem="series",
            file_extension="raw",
            frame_limit=3,
        )
        self.assertEqual(build_recording_log_path(request), Path("captures/series_recording_log.csv"))


if __name__ == "__main__":
    unittest.main()
