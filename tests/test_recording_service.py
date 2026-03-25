from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Lock
from time import sleep
import csv
import unittest

from tests import _path_setup
from camera_app.models.camera_configuration import CameraConfiguration
from camera_app.models.captured_frame import CapturedFrame
from camera_app.models.recording_request import RecordingRequest
from camera_app.services.recording_service import RecordingService


class _FakeRecordingDriver:
    def __init__(self, frames: list[CapturedFrame]) -> None:
        self._frames = list(frames)
        self._lock = Lock()
        self.start_calls = 0
        self.stop_calls = 0

    def start_acquisition(self) -> None:
        self.start_calls += 1

    def stop_acquisition(self) -> None:
        self.stop_calls += 1

    def get_latest_frame(self) -> CapturedFrame | None:
        with self._lock:
            if not self._frames:
                return None
            return self._frames.pop(0)


class _StreamingRecordingDriver:
    def __init__(self) -> None:
        self._next_frame_id = 0
        self._lock = Lock()
        self.start_calls = 0
        self.stop_calls = 0

    def start_acquisition(self) -> None:
        self.start_calls += 1

    def stop_acquisition(self) -> None:
        self.stop_calls += 1

    def get_latest_frame(self) -> CapturedFrame:
        with self._lock:
            frame = CapturedFrame(
                raw_frame=bytes([self._next_frame_id % 256]),
                width=1,
                height=1,
                frame_id=self._next_frame_id,
                camera_timestamp=5000 + self._next_frame_id,
            )
            self._next_frame_id += 1
            return frame


class _FailingStartDriver(_FakeRecordingDriver):
    def start_acquisition(self) -> None:
        self.start_calls += 1
        raise RuntimeError("camera start failed")


class RecordingServiceTests(unittest.TestCase):
    def test_start_recording_writes_raw_sequence_until_frame_limit(self) -> None:
        frames = [
            CapturedFrame(
                raw_frame=bytes([index]),
                width=1,
                height=1,
                frame_id=index,
                camera_timestamp=1000 + index,
            )
            for index in range(3)
        ]
        driver = _FakeRecordingDriver(frames)
        service = RecordingService(
            driver,
            poll_interval_seconds=0.001,
            configuration_provider=lambda: CameraConfiguration(
                exposure_time_us=2500.0,
                gain=1.5,
                pixel_format="Mono8",
                acquisition_frame_rate=12.0,
            ),
        )

        with TemporaryDirectory() as temp_dir:
            request = RecordingRequest(
                save_directory=Path(temp_dir),
                file_stem="series",
                file_extension=".raw",
                frame_limit=3,
                queue_size=4,
            )

            status = service.start_recording(request)
            self.assertTrue(status.is_recording)

            for _ in range(200):
                status = service.get_status()
                if not status.is_recording and status.frames_written == 3:
                    break
                sleep(0.01)

            self.assertEqual(service.get_status().frames_written, 3)
            self.assertFalse(service.get_status().is_recording)
            self.assertEqual(driver.start_calls, 1)
            self.assertEqual(driver.stop_calls, 1)
            self.assertEqual((Path(temp_dir) / "series_000000.raw").read_bytes(), b"\x00")
            self.assertEqual((Path(temp_dir) / "series_000001.raw").read_bytes(), b"\x01")
            self.assertEqual((Path(temp_dir) / "series_000002.raw").read_bytes(), b"\x02")
            log_path = Path(temp_dir) / "series_recording_log.csv"
            log_lines = log_path.read_text(encoding="utf-8").splitlines()
            self.assertIn(f"# save_directory: {temp_dir}", log_lines)
            self.assertIn("# frame_limit: 3", log_lines)
            self.assertIn("# target_frame_rate: ", log_lines)
            self.assertIn("# continues_previous_series: false", log_lines)
            self.assertIn("# exposure_time_us: 2500.0", log_lines)
            self.assertIn("# gain: 1.5", log_lines)
            self.assertIn("# pixel_format: Mono8", log_lines)
            self.assertIn("# acquisition_frame_rate: 12.0", log_lines)
            self.assertIn("# roi_x: ", log_lines)
            self.assertIn("# roi_y: ", log_lines)
            self.assertIn("# roi_width: ", log_lines)
            self.assertIn("# roi_height: ", log_lines)
            data_rows = list(csv.reader(line for line in log_lines if not line.startswith("# ")))
            self.assertEqual(data_rows[0], ["image_name", "frame_id", "camera_timestamp", "system_timestamp_utc"])
            self.assertEqual(data_rows[1][0], "series_000000.raw")
            self.assertEqual(data_rows[1][1], "0")
            self.assertEqual(data_rows[1][2], "1000")
            self.assertTrue(data_rows[1][3])
            self.assertEqual(data_rows[3][0], "series_000002.raw")

    def test_stop_recording_stops_active_recording(self) -> None:
        frames = [
            CapturedFrame(raw_frame=bytes([index]), width=1, height=1, frame_id=index)
            for index in range(10)
        ]
        driver = _FakeRecordingDriver(frames)
        service = RecordingService(driver, poll_interval_seconds=0.001)

        with TemporaryDirectory() as temp_dir:
            request = RecordingRequest(
                save_directory=Path(temp_dir),
                file_stem="series",
                file_extension=".raw",
                frame_limit=10,
                queue_size=2,
            )

            service.start_recording(request)
            sleep(0.02)
            status = service.stop_recording()

            self.assertFalse(status.is_recording)
            self.assertGreaterEqual(driver.stop_calls, 1)

    def test_start_recording_rejects_missing_frame_limit(self) -> None:
        driver = _FakeRecordingDriver([])
        service = RecordingService(driver)

        with TemporaryDirectory() as temp_dir:
            request = RecordingRequest(
                save_directory=Path(temp_dir),
                file_stem="series",
                file_extension=".raw",
                frame_limit=None,
            )

            with self.assertRaisesRegex(ValueError, "requires frame_limit or duration_seconds"):
                service.start_recording(request)

    def test_start_recording_stops_after_duration_seconds(self) -> None:
        driver = _StreamingRecordingDriver()
        service = RecordingService(driver, poll_interval_seconds=0.001)

        with TemporaryDirectory() as temp_dir:
            request = RecordingRequest(
                save_directory=Path(temp_dir),
                file_stem="timed",
                file_extension=".raw",
                frame_limit=None,
                duration_seconds=0.03,
                queue_size=8,
            )

            status = service.start_recording(request)
            self.assertTrue(status.is_recording)

            for _ in range(200):
                status = service.get_status()
                if not status.is_recording:
                    break
                sleep(0.01)

            final_status = service.get_status()
            self.assertFalse(final_status.is_recording)
            self.assertGreater(final_status.frames_written, 0)
            self.assertEqual(driver.start_calls, 1)
            self.assertEqual(driver.stop_calls, 1)

    def test_start_recording_rejects_non_positive_duration(self) -> None:
        driver = _FakeRecordingDriver([])
        service = RecordingService(driver)

        with TemporaryDirectory() as temp_dir:
            request = RecordingRequest(
                save_directory=Path(temp_dir),
                file_stem="series",
                file_extension=".raw",
                duration_seconds=0,
            )

            with self.assertRaisesRegex(ValueError, "duration_seconds must be greater than zero"):
                service.start_recording(request)

    def test_start_recording_rejects_non_positive_target_frame_rate(self) -> None:
        driver = _FakeRecordingDriver([])
        service = RecordingService(driver)

        with TemporaryDirectory() as temp_dir:
            request = RecordingRequest(
                save_directory=Path(temp_dir),
                file_stem="series",
                file_extension=".raw",
                frame_limit=3,
                target_frame_rate=0,
            )

            with self.assertRaisesRegex(ValueError, "target_frame_rate must be greater than zero"):
                service.start_recording(request)

    def test_start_recording_rejects_invalid_file_extension(self) -> None:
        driver = _FakeRecordingDriver([])
        service = RecordingService(driver)

        with TemporaryDirectory() as temp_dir:
            request = RecordingRequest(
                save_directory=Path(temp_dir),
                file_stem="series",
                file_extension=".tar.gz",
                frame_limit=3,
            )

            with self.assertRaisesRegex(ValueError, "single extension segment"):
                service.start_recording(request)

    def test_start_recording_rejects_path_like_file_stem(self) -> None:
        driver = _FakeRecordingDriver([])
        service = RecordingService(driver)

        with TemporaryDirectory() as temp_dir:
            request = RecordingRequest(
                save_directory=Path(temp_dir),
                file_stem="nested/series",
                file_extension=".raw",
                frame_limit=3,
            )

            with self.assertRaisesRegex(ValueError, "file_stem"):
                service.start_recording(request)

    def test_recording_log_includes_target_frame_rate_and_roi(self) -> None:
        frames = [
            CapturedFrame(
                raw_frame=bytes([index]),
                width=1,
                height=1,
                frame_id=index,
                camera_timestamp=1000 + index,
            )
            for index in range(2)
        ]
        driver = _FakeRecordingDriver(frames)
        service = RecordingService(
            driver,
            poll_interval_seconds=0.001,
            configuration_provider=lambda: CameraConfiguration(
                exposure_time_us=2500.0,
                acquisition_frame_rate=25.0,
                roi_offset_x=11,
                roi_offset_y=22,
                roi_width=333,
                roi_height=222,
            ),
        )

        with TemporaryDirectory() as temp_dir:
            service.start_recording(
                RecordingRequest(
                    save_directory=Path(temp_dir),
                    file_stem="series",
                    file_extension=".raw",
                    frame_limit=2,
                    target_frame_rate=8.0,
                )
            )

            for _ in range(100):
                status = service.get_status()
                if not status.is_recording and status.frames_written == 2:
                    break
                sleep(0.01)

            log_lines = (Path(temp_dir) / "series_recording_log.csv").read_text(encoding="utf-8").splitlines()
            self.assertIn("# target_frame_rate: 8.0", log_lines)
            self.assertIn("# roi_x: 11", log_lines)
            self.assertIn("# roi_y: 22", log_lines)
            self.assertIn("# roi_width: 333", log_lines)
            self.assertIn("# roi_height: 222", log_lines)

    def test_stop_recording_is_idempotent_when_idle(self) -> None:
        driver = _FakeRecordingDriver([])
        service = RecordingService(driver)

        first_status = service.stop_recording()
        second_status = service.stop_recording()

        self.assertFalse(first_status.is_recording)
        self.assertFalse(second_status.is_recording)
        self.assertEqual(driver.stop_calls, 0)

    def test_start_recording_cleans_up_if_camera_start_fails(self) -> None:
        driver = _FailingStartDriver([])
        service = RecordingService(driver, poll_interval_seconds=0.001)

        with TemporaryDirectory() as temp_dir:
            request = RecordingRequest(
                save_directory=Path(temp_dir),
                file_stem="series",
                file_extension=".raw",
                frame_limit=3,
            )

            with self.assertRaisesRegex(RuntimeError, "camera start failed"):
                service.start_recording(request)

            status = service.get_status()
            self.assertFalse(status.is_recording)
            self.assertIsNone(status.save_directory)
            self.assertIsNone(status.active_file_stem)
            self.assertEqual(driver.start_calls, 1)
            self.assertEqual(driver.stop_calls, 0)

    def test_start_recording_cleans_up_if_log_open_fails(self) -> None:
        driver = _FakeRecordingDriver([])
        service = RecordingService(driver, poll_interval_seconds=0.001)

        original_open_recording_log = service._open_recording_log

        def failing_open_recording_log(request: RecordingRequest) -> None:
            raise RuntimeError("log setup failed")

        service._open_recording_log = failing_open_recording_log
        try:
            with TemporaryDirectory() as temp_dir:
                request = RecordingRequest(
                    save_directory=Path(temp_dir),
                    file_stem="series",
                    file_extension=".raw",
                    frame_limit=3,
                )

                with self.assertRaisesRegex(RuntimeError, "log setup failed"):
                    service.start_recording(request)
        finally:
            service._open_recording_log = original_open_recording_log

        status = service.get_status()
        self.assertFalse(status.is_recording)
        self.assertIsNone(status.save_directory)
        self.assertIsNone(status.active_file_stem)
        self.assertEqual(driver.start_calls, 0)
        self.assertEqual(driver.stop_calls, 0)


if __name__ == "__main__":
    unittest.main()
