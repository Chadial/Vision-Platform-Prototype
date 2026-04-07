from pathlib import Path
import unittest

from tests import _path_setup
from vision_platform.models import (
    ApplyConfigurationRequest,
    CameraConfiguration,
    IntervalCaptureRequest,
    RecordingRequest,
    SaveSnapshotRequest,
    SnapshotRequest,
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

    def test_apply_configuration_request_can_be_created_from_camera_configuration(self) -> None:
        configuration = CameraConfiguration(
            exposure_time_us=1250.0,
            gain=2.5,
            pixel_format="Mono10",
            acquisition_frame_rate=8.0,
            roi_offset_x=4,
            roi_offset_y=6,
            roi_width=800,
            roi_height=600,
        )

        request = ApplyConfigurationRequest.from_camera_configuration(configuration)

        self.assertEqual(request.exposure_time_us, 1250.0)
        self.assertEqual(request.gain, 2.5)
        self.assertEqual(request.pixel_format, "Mono10")
        self.assertEqual(request.acquisition_frame_rate, 8.0)
        self.assertEqual(request.roi_offset_x, 4)
        self.assertEqual(request.roi_offset_y, 6)
        self.assertEqual(request.roi_width, 800)
        self.assertEqual(request.roi_height, 600)

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
            camera_alias="alias_cam2",
            configuration_profile_id="default",
            configuration_profile_camera_class="alvium_1800_u_1240m",
        )

        snapshot_request = request.to_snapshot_request()

        self.assertEqual(snapshot_request.file_stem, "snapshot_001")
        self.assertEqual(snapshot_request.file_extension, ".png")
        self.assertEqual(snapshot_request.save_directory, Path("captures"))
        self.assertEqual(snapshot_request.camera_id, "cam2")
        self.assertEqual(snapshot_request.camera_alias, "alias_cam2")
        self.assertEqual(snapshot_request.configuration_profile_id, "default")
        self.assertEqual(snapshot_request.configuration_profile_camera_class, "alvium_1800_u_1240m")

    def test_save_snapshot_request_can_be_created_from_snapshot_request(self) -> None:
        snapshot_request = SnapshotRequest(
            save_directory=Path("captures"),
            file_stem="snapshot_002",
            file_extension=".raw",
            create_directories=False,
            camera_id="cam3",
            camera_alias="alias_cam3",
            configuration_profile_id="fast_preview",
            configuration_profile_camera_class="alvium_1800_u_1240m",
        )

        request = SaveSnapshotRequest.from_snapshot_request(snapshot_request)

        self.assertEqual(request.file_stem, "snapshot_002")
        self.assertEqual(request.file_extension, ".raw")
        self.assertEqual(request.save_directory, Path("captures"))
        self.assertFalse(request.create_directories)
        self.assertEqual(request.camera_id, "cam3")
        self.assertEqual(request.camera_alias, "alias_cam3")
        self.assertEqual(request.configuration_profile_id, "fast_preview")
        self.assertEqual(request.configuration_profile_camera_class, "alvium_1800_u_1240m")

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
            camera_alias="alias_cam2",
            configuration_profile_id="default",
            configuration_profile_camera_class="alvium_1800_u_1240m",
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
        self.assertEqual(recording_request.camera_alias, "alias_cam2")
        self.assertEqual(recording_request.configuration_profile_id, "default")
        self.assertEqual(recording_request.configuration_profile_camera_class, "alvium_1800_u_1240m")

    def test_start_recording_request_can_be_created_from_recording_request(self) -> None:
        recording_request = RecordingRequest(
            save_directory=Path("captures"),
            file_stem="series_002",
            file_extension=".raw",
            frame_limit=30,
            duration_seconds=3.0,
            target_frame_rate=10.0,
            queue_size=32,
            create_directories=False,
            camera_id="cam4",
            camera_alias="alias_cam4",
            configuration_profile_id="inspection",
            configuration_profile_camera_class="alvium_1800_u_1240m",
        )

        request = StartRecordingRequest.from_recording_request(recording_request)

        self.assertEqual(request.file_stem, "series_002")
        self.assertEqual(request.file_extension, ".raw")
        self.assertEqual(request.save_directory, Path("captures"))
        self.assertEqual(request.max_frame_count, 30)
        self.assertEqual(request.duration_seconds, 3.0)
        self.assertEqual(request.target_frame_rate, 10.0)
        self.assertEqual(request.queue_size, 32)
        self.assertFalse(request.create_directories)
        self.assertEqual(request.camera_id, "cam4")
        self.assertEqual(request.camera_alias, "alias_cam4")
        self.assertEqual(request.configuration_profile_id, "inspection")
        self.assertEqual(request.configuration_profile_camera_class, "alvium_1800_u_1240m")

    def test_recording_request_default_file_extension_is_bmp(self) -> None:
        request = RecordingRequest(save_directory=Path("captures"), file_stem="series_default")

        self.assertEqual(request.file_extension, ".bmp")

    def test_start_recording_request_default_file_extension_is_bmp(self) -> None:
        request = StartRecordingRequest(file_stem="series_default")

        self.assertEqual(request.file_extension, ".bmp")

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

    def test_start_interval_capture_request_can_be_created_from_interval_capture_request(self) -> None:
        interval_capture_request = IntervalCaptureRequest(
            save_directory=Path("captures"),
            file_stem="interval_002",
            interval_seconds=0.5,
            file_extension=".raw",
            max_frame_count=9,
            duration_seconds=4.0,
            create_directories=False,
            camera_id="cam5",
        )

        request = StartIntervalCaptureRequest.from_interval_capture_request(interval_capture_request)

        self.assertEqual(request.file_stem, "interval_002")
        self.assertEqual(request.interval_seconds, 0.5)
        self.assertEqual(request.file_extension, ".raw")
        self.assertEqual(request.save_directory, Path("captures"))
        self.assertEqual(request.max_frame_count, 9)
        self.assertEqual(request.duration_seconds, 4.0)
        self.assertFalse(request.create_directories)
        self.assertEqual(request.camera_id, "cam5")


if __name__ == "__main__":
    unittest.main()
