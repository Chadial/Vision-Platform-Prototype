from pathlib import Path
import unittest

from tests import _path_setup
from vision_platform.models import IntervalCaptureRequest, RecordingRequest, SnapshotRequest
from vision_platform.services.recording_service import (
    build_interval_capture_frame_path,
    build_recording_frame_path,
    build_recording_log_path,
    build_snapshot_path,
)


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

    def test_build_snapshot_path_rejects_path_like_file_stem(self) -> None:
        request = SnapshotRequest(save_directory=Path("captures"), file_stem="nested/image", file_extension=".png")

        with self.assertRaisesRegex(ValueError, "file_stem"):
            build_snapshot_path(request)

    def test_build_recording_frame_path_rejects_multi_segment_extension(self) -> None:
        request = RecordingRequest(
            save_directory=Path("captures"),
            file_stem="series",
            file_extension=".tar.gz",
            frame_limit=3,
        )

        with self.assertRaisesRegex(ValueError, "single extension segment"):
            build_recording_frame_path(request, 0)

    def test_build_interval_capture_frame_path_uses_zero_padded_index(self) -> None:
        request = IntervalCaptureRequest(
            save_directory=Path("captures"),
            file_stem="interval",
            interval_seconds=1.0,
            file_extension="png",
            max_frame_count=3,
        )

        self.assertEqual(build_interval_capture_frame_path(request, 2), Path("captures/interval_000002.png"))


if __name__ == "__main__":
    unittest.main()
