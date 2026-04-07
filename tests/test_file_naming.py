from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tests import _path_setup
from camera_app.storage import (
    build_interval_capture_frame_path as legacy_build_interval_capture_frame_path,
    build_recording_frame_path as legacy_build_recording_frame_path,
    build_recording_log_path as legacy_build_recording_log_path,
    build_snapshot_path as legacy_build_snapshot_path,
)
from vision_platform.models import IntervalCaptureRequest, RecordingRequest, SnapshotRequest
from vision_platform.services.recording_service import (
    build_next_snapshot_path,
    build_interval_capture_frame_path,
    build_recording_frame_path,
    build_recording_log_path,
    build_recording_log_path_for_run,
    build_snapshot_path,
    resolve_next_recording_frame_index,
    resolve_next_snapshot_index,
)


class FileNamingTests(unittest.TestCase):
    def test_legacy_camera_app_storage_package_reexports_platform_file_naming(self) -> None:
        self.assertIs(legacy_build_snapshot_path, build_snapshot_path)
        self.assertIs(legacy_build_recording_frame_path, build_recording_frame_path)
        self.assertIs(legacy_build_recording_log_path, build_recording_log_path)
        self.assertIs(legacy_build_interval_capture_frame_path, build_interval_capture_frame_path)

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

    def test_build_recording_log_path_for_run_adds_start_index_suffix_for_continuation(self) -> None:
        request = RecordingRequest(
            save_directory=Path("captures"),
            file_stem="series",
            file_extension="raw",
            frame_limit=3,
        )
        self.assertEqual(
            build_recording_log_path_for_run(request, start_frame_index=12),
            Path("captures/series_recording_log_000012.csv"),
        )

    def test_resolve_next_recording_frame_index_uses_existing_files(self) -> None:
        with TemporaryDirectory() as temp_dir:
            save_directory = Path(temp_dir)
            (save_directory / "series_000000.raw").write_bytes(b"a")
            (save_directory / "series_000001.raw").write_bytes(b"b")
            next_index = resolve_next_recording_frame_index(
                save_directory=save_directory,
                file_stem="series",
                file_extension=".raw",
            )
            self.assertEqual(next_index, 2)

    def test_build_next_snapshot_path_adds_suffix_when_base_file_exists(self) -> None:
        with TemporaryDirectory() as temp_dir:
            save_directory = Path(temp_dir)
            (save_directory / "snapshot.bmp").write_bytes(b"first")
            request = SnapshotRequest(
                save_directory=save_directory,
                file_stem="snapshot",
                file_extension=".bmp",
            )
            self.assertEqual(
                build_next_snapshot_path(request),
                save_directory / "snapshot_000001.bmp",
            )

    def test_resolve_next_snapshot_index_uses_existing_trace_rows(self) -> None:
        with TemporaryDirectory() as temp_dir:
            save_directory = Path(temp_dir)
            trace_path = save_directory / "saved_artifact_traceability.csv"
            trace_path.write_text(
                "\n".join(
                    [
                        "# context.record_kind: saved_artifact_folder_log",
                        "artifact_kind,run_id,image_name,frame_id,camera_timestamp,system_timestamp_utc,analysis_roi_id,analysis_roi_type,analysis_roi_data,focus_method,focus_score_frame_interval,focus_value_mean,focus_value_stddev,focus_roi_type,focus_roi_data",
                        "snapshot,run_a,snapshot.bmp,0,,2026-04-07T00:00:00+00:00,,,,,,,,,",
                        "snapshot,run_b,snapshot_000001.bmp,1,,2026-04-07T00:00:01+00:00,,,,,,,,,",
                    ]
                ),
                encoding="utf-8",
            )
            self.assertEqual(
                resolve_next_snapshot_index(
                    save_directory=save_directory,
                    file_stem="snapshot",
                    file_extension=".bmp",
                ),
                2,
            )

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
