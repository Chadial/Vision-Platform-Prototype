from pathlib import Path
import unittest

from tests import _path_setup
from vision_platform.models import (
    ApplyConfigurationRequest,
    IntervalCaptureRequest,
    SaveSnapshotRequest,
    SetSaveDirectoryRequest,
    StartIntervalCaptureRequest,
    StartRecordingRequest,
)


class RequestModelTests(unittest.TestCase):
    def test_apply_configuration_request_maps_to_camera_configuration(self) -> None:
        request = ApplyConfigurationRequest(
            exposure_time_us=2500.0,
            gain=1.5,
            pixel_format="Mono8",
            acquisition_frame_rate=15.0,
            roi_offset_x=10,
            roi_offset_y=20,
            roi_width=640,
            roi_height=480,
        )

        configuration = request.to_camera_configuration()

        self.assertEqual(configuration.exposure_time_us, 2500.0)
        self.assertEqual(configuration.gain, 1.5)
        self.assertEqual(configuration.pixel_format, "Mono8")
        self.assertEqual(configuration.acquisition_frame_rate, 15.0)
        self.assertEqual(configuration.roi_offset_x, 10)
        self.assertEqual(configuration.roi_offset_y, 20)
        self.assertEqual(configuration.roi_width, 640)
        self.assertEqual(configuration.roi_height, 480)

    def test_set_save_directory_request_resolves_append_mode(self) -> None:
        request = SetSaveDirectoryRequest(base_directory=Path("captures"), mode="append")

        self.assertEqual(request.resolve_directory(), Path("captures"))

    def test_set_save_directory_request_resolves_new_subdirectory_mode(self) -> None:
        request = SetSaveDirectoryRequest(
            base_directory=Path("captures"),
            mode="new_subdirectory",
            subdirectory_name="run_001",
        )

        self.assertEqual(request.resolve_directory(), Path("captures/run_001"))

    def test_set_save_directory_request_requires_subdirectory_name_for_new_subdirectory_mode(self) -> None:
        request = SetSaveDirectoryRequest(base_directory=Path("captures"), mode="new_subdirectory")

        with self.assertRaisesRegex(ValueError, "subdirectory_name"):
            request.resolve_directory()

    def test_set_save_directory_request_rejects_path_like_subdirectory_name(self) -> None:
        request = SetSaveDirectoryRequest(
            base_directory=Path("captures"),
            mode="new_subdirectory",
            subdirectory_name="run/001",
        )

        with self.assertRaisesRegex(ValueError, "path separators"):
            request.resolve_directory()

    def test_save_snapshot_request_maps_to_snapshot_request(self) -> None:
        request = SaveSnapshotRequest(
            file_stem="snapshot_001",
            file_extension=".png",
            save_directory=Path("captures"),
            camera_id="cam2",
        )

        snapshot_request = request.to_snapshot_request()

        self.assertEqual(snapshot_request.file_stem, "snapshot_001")
        self.assertEqual(snapshot_request.file_extension, ".png")
        self.assertEqual(snapshot_request.save_directory, Path("captures"))
        self.assertEqual(snapshot_request.camera_id, "cam2")

    def test_start_recording_request_maps_to_recording_request(self) -> None:
        request = StartRecordingRequest(
            file_stem="series_001",
            file_extension=".raw",
            save_directory=Path("captures"),
            max_frame_count=25,
            duration_seconds=5.0,
            target_frame_rate=12.5,
            queue_size=16,
            camera_id="cam2",
        )

        recording_request = request.to_recording_request()

        self.assertEqual(recording_request.file_stem, "series_001")
        self.assertEqual(recording_request.file_extension, ".raw")
        self.assertEqual(recording_request.save_directory, Path("captures"))
        self.assertEqual(recording_request.frame_limit, 25)
        self.assertEqual(recording_request.duration_seconds, 5.0)
        self.assertEqual(recording_request.target_frame_rate, 12.5)
        self.assertEqual(recording_request.queue_size, 16)
        self.assertEqual(recording_request.camera_id, "cam2")

    def test_interval_capture_request_stores_expected_fields(self) -> None:
        request = IntervalCaptureRequest(
            save_directory=Path("captures"),
            file_stem="interval_001",
            file_extension=".png",
            interval_seconds=1.0,
            max_frame_count=5,
            duration_seconds=10.0,
            camera_id="cam2",
        )

        self.assertEqual(request.save_directory, Path("captures"))
        self.assertEqual(request.file_stem, "interval_001")
        self.assertEqual(request.file_extension, ".png")
        self.assertEqual(request.interval_seconds, 1.0)
        self.assertEqual(request.max_frame_count, 5)
        self.assertEqual(request.duration_seconds, 10.0)
        self.assertEqual(request.camera_id, "cam2")

    def test_start_interval_capture_request_maps_to_interval_capture_request(self) -> None:
        request = StartIntervalCaptureRequest(
            file_stem="interval_001",
            interval_seconds=1.0,
            file_extension=".png",
            save_directory=Path("captures"),
            max_frame_count=5,
            duration_seconds=10.0,
            camera_id="cam2",
        )

        interval_capture_request = request.to_interval_capture_request()

        self.assertEqual(interval_capture_request.save_directory, Path("captures"))
        self.assertEqual(interval_capture_request.file_stem, "interval_001")
        self.assertEqual(interval_capture_request.file_extension, ".png")
        self.assertEqual(interval_capture_request.interval_seconds, 1.0)
        self.assertEqual(interval_capture_request.max_frame_count, 5)
        self.assertEqual(interval_capture_request.duration_seconds, 10.0)
        self.assertEqual(interval_capture_request.camera_id, "cam2")


if __name__ == "__main__":
    unittest.main()
