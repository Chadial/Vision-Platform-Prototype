from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Lock
from time import sleep
import csv
import unittest

from tests import _path_setup
from vision_platform.models import CameraConfiguration, CapturedFrame, RecordingRequest
from vision_platform.services.recording_service import FrameWriter
from vision_platform.services.recording_service import RecordingService


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


class _FailingStopDriver(_FakeRecordingDriver):
    def stop_acquisition(self) -> None:
        self.stop_calls += 1
        raise RuntimeError("camera stop failed")


class _IdleFailingStopDriver(_FailingStopDriver):
    def __init__(self) -> None:
        super().__init__([])
        self.start_calls = 0

    def start_acquisition(self) -> None:
        self.start_calls += 1

    def get_latest_frame(self) -> CapturedFrame | None:
        return None


class _FailingFrameWriter:
    def write_frame(self, frame: CapturedFrame, target_path: Path, create_directories: bool = True) -> None:
        del frame, target_path, create_directories
        raise RuntimeError("frame write failed")


class _FailingOnceFrameWriter:
    def __init__(self) -> None:
        self._has_failed = False

    def write_frame(self, frame: CapturedFrame, target_path: Path, create_directories: bool = True) -> None:
        if not self._has_failed:
            self._has_failed = True
            raise RuntimeError("frame write failed")

        FrameWriter().write_frame(frame, target_path, create_directories=create_directories)


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
            trace_lines = (Path(temp_dir) / "saved_artifact_traceability.csv").read_text(encoding="utf-8").splitlines()
            self.assertIn(f"# context.save_directory: {temp_dir}", trace_lines)
            self.assertIn("# context.record_kind: saved_artifact_folder_log", trace_lines)
            self.assertIn("# context.pixel_format: Mono8", trace_lines)
            self.assertIn("# context.exposure_time_us: 2500.0", trace_lines)
            self.assertIn("# context.gain: 1.5", trace_lines)
            self.assertIn("# run.start", trace_lines)
            self.assertIn("# run.artifact_kind: bounded_recording", trace_lines)
            self.assertIn("# run.file_stem: series", trace_lines)
            self.assertIn("# run.frame_limit: 3", trace_lines)
            self.assertIn("# run.end", trace_lines)
            self.assertIn("# run.end_state: completed", trace_lines)
            trace_rows = list(csv.reader(line for line in trace_lines if line and not line.startswith("# ")))
            self.assertEqual(
                trace_rows[0],
                [
                    "artifact_kind",
                    "run_id",
                    "image_name",
                    "frame_id",
                    "camera_timestamp",
                    "system_timestamp_utc",
                    "analysis_roi_id",
                    "analysis_roi_type",
                    "analysis_roi_data",
                    "focus_method",
                    "focus_value_mean",
                    "focus_value_stddev",
                    "focus_roi_type",
                    "focus_roi_data",
                ],
            )
            self.assertEqual(trace_rows[1][0], "bounded_recording")
            self.assertEqual(trace_rows[1][2], "series_000000.raw")
            self.assertEqual(trace_rows[3][2], "series_000002.raw")
            self.assertEqual(trace_rows[1][6:], ["", "", "", "", "", "", "", ""])

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

    def test_stop_recording_clears_state_even_if_camera_stop_fails(self) -> None:
        driver = _IdleFailingStopDriver()
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
            try:
                service.stop_recording()
            except RuntimeError as exc:
                self.assertIn("camera stop failed", str(exc))

        status = service.get_status()
        self.assertFalse(status.is_recording)
        self.assertIsNone(status.save_directory)
        self.assertIsNone(status.active_file_stem)
        self.assertEqual(driver.start_calls, 1)
        self.assertGreaterEqual(driver.stop_calls, 1)

    def test_start_recording_preserves_original_error_if_cleanup_stop_fails(self) -> None:
        driver = _FailingStopDriver([])
        service = RecordingService(driver, poll_interval_seconds=0.001)

        original_open_recording_log = service._open_recording_log

        def failing_open_recording_log(request: RecordingRequest) -> None:
            service._acquisition_started = True
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

                with self.assertLogs("camera_app.services.recording_service", level="ERROR") as logs:
                    with self.assertRaisesRegex(RuntimeError, "log setup failed"):
                        service.start_recording(request)
        finally:
            service._open_recording_log = original_open_recording_log

        status = service.get_status()
        self.assertFalse(status.is_recording)
        self.assertIsNone(status.save_directory)
        self.assertIsNone(status.active_file_stem)
        self.assertTrue(any("Recording acquisition stop failed during cleanup." in message for message in logs.output))
        self.assertEqual(driver.stop_calls, 1)

    def test_bounded_recording_can_be_started_again_after_successful_completion(self) -> None:
        driver = _StreamingRecordingDriver()
        service = RecordingService(driver, poll_interval_seconds=0.001)

        with TemporaryDirectory() as temp_dir:
            first_request = RecordingRequest(
                save_directory=Path(temp_dir),
                file_stem="first",
                file_extension=".raw",
                frame_limit=2,
                queue_size=4,
            )
            second_request = RecordingRequest(
                save_directory=Path(temp_dir),
                file_stem="second",
                file_extension=".raw",
                frame_limit=2,
                queue_size=4,
            )

            service.start_recording(first_request)
            for _ in range(200):
                status = service.get_status()
                if not status.is_recording and status.frames_written == 2:
                    break
                sleep(0.01)

            first_status = service.get_status()
            self.assertFalse(first_status.is_recording)
            self.assertEqual(first_status.frames_written, 2)

            service.start_recording(second_request)
            for _ in range(200):
                status = service.get_status()
                if not status.is_recording and status.frames_written == 2:
                    break
                sleep(0.01)

            second_status = service.get_status()
            self.assertFalse(second_status.is_recording)
            self.assertEqual(second_status.frames_written, 2)
            self.assertGreaterEqual(driver.start_calls, 2)
            self.assertGreaterEqual(driver.stop_calls, 2)
            self.assertTrue((Path(temp_dir) / "first_000000.raw").exists())
            self.assertTrue((Path(temp_dir) / "second_000000.raw").exists())

    def test_recording_can_be_started_again_on_same_service_after_write_failure(self) -> None:
        driver = _StreamingRecordingDriver()
        service = RecordingService(driver, frame_writer=_FailingOnceFrameWriter(), poll_interval_seconds=0.001)

        with TemporaryDirectory() as temp_dir:
            failing_request = RecordingRequest(
                save_directory=Path(temp_dir),
                file_stem="broken",
                file_extension=".raw",
                frame_limit=2,
                queue_size=4,
            )

            service.start_recording(failing_request)
            for _ in range(200):
                status = service.get_status()
                if not status.is_recording and status.last_error is not None:
                    break
                sleep(0.01)

            failed_status = service.get_status()
            self.assertFalse(failed_status.is_recording)
            self.assertIn("Recording write failed", failed_status.last_error or "")
            self.assertIsNone(failed_status.save_directory)
            self.assertIsNone(failed_status.active_file_stem)
            trace_lines = (Path(temp_dir) / "saved_artifact_traceability.csv").read_text(encoding="utf-8").splitlines()
            self.assertIn("# run.artifact_kind: bounded_recording", trace_lines)
            self.assertIn("# run.file_stem: broken", trace_lines)
            self.assertIn("# run.end_state: failed", trace_lines)
            self.assertTrue(any("Recording write failed" in line for line in trace_lines))

            recovery_request = RecordingRequest(
                save_directory=Path(temp_dir),
                file_stem="recovered",
                file_extension=".raw",
                frame_limit=2,
                queue_size=4,
            )
            service.start_recording(recovery_request)
            for _ in range(200):
                status = service.get_status()
                if not status.is_recording and status.frames_written == 2:
                    break
                sleep(0.01)

            recovered_status = service.get_status()
            self.assertFalse(recovered_status.is_recording)
            self.assertEqual(recovered_status.frames_written, 2)
            self.assertIsNone(recovered_status.last_error)
            self.assertTrue((Path(temp_dir) / "recovered_000000.raw").exists())

    def test_recording_traceability_reuses_log_when_context_matches(self) -> None:
        driver = _StreamingRecordingDriver()
        service = RecordingService(
            driver,
            poll_interval_seconds=0.001,
            configuration_provider=lambda: CameraConfiguration(
                exposure_time_us=2500.0,
                gain=1.5,
                pixel_format="Mono8",
            ),
        )

        with TemporaryDirectory() as temp_dir:
            first_request = RecordingRequest(
                save_directory=Path(temp_dir),
                file_stem="first",
                file_extension=".raw",
                frame_limit=2,
                queue_size=4,
            )
            second_request = RecordingRequest(
                save_directory=Path(temp_dir),
                file_stem="second",
                file_extension=".raw",
                frame_limit=3,
                queue_size=4,
                duration_seconds=0.05,
            )

            for request in (first_request, second_request):
                service.start_recording(request)
                for _ in range(200):
                    status = service.get_status()
                    if not status.is_recording:
                        break
                    sleep(0.01)

            trace_path = Path(temp_dir) / "saved_artifact_traceability.csv"
            self.assertTrue(trace_path.exists())
            self.assertFalse((Path(temp_dir) / "saved_artifact_traceability_001.csv").exists())
            trace_lines = trace_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(trace_lines.count("# run.start"), 2)
            self.assertEqual(trace_lines.count("# run.artifact_kind: bounded_recording"), 4)
            self.assertIn("# run.file_stem: first", trace_lines)
            self.assertIn("# run.file_stem: second", trace_lines)
            self.assertIn("# run.frame_limit: 2", trace_lines)
            self.assertIn("# run.frame_limit: 3", trace_lines)
            self.assertIn("# run.duration_seconds: 0.05", trace_lines)

    def test_recording_traceability_creates_new_log_when_context_changes(self) -> None:
        driver = _StreamingRecordingDriver()
        current_configuration = CameraConfiguration(
            exposure_time_us=2500.0,
            gain=1.5,
            pixel_format="Mono8",
        )
        service = RecordingService(
            driver,
            poll_interval_seconds=0.001,
            configuration_provider=lambda: current_configuration,
        )

        with TemporaryDirectory() as temp_dir:
            first_request = RecordingRequest(
                save_directory=Path(temp_dir),
                file_stem="first",
                file_extension=".raw",
                frame_limit=2,
                queue_size=4,
            )
            second_request = RecordingRequest(
                save_directory=Path(temp_dir),
                file_stem="second",
                file_extension=".raw",
                frame_limit=2,
                queue_size=4,
            )

            service.start_recording(first_request)
            for _ in range(200):
                status = service.get_status()
                if not status.is_recording:
                    break
                sleep(0.01)

            current_configuration = CameraConfiguration(
                exposure_time_us=3000.0,
                gain=1.5,
                pixel_format="Mono8",
            )

            service.start_recording(second_request)
            for _ in range(200):
                status = service.get_status()
                if not status.is_recording:
                    break
                sleep(0.01)

            first_trace = Path(temp_dir) / "saved_artifact_traceability.csv"
            second_trace = Path(temp_dir) / "saved_artifact_traceability_001.csv"
            self.assertTrue(first_trace.exists())
            self.assertTrue(second_trace.exists())
            self.assertIn("# context.exposure_time_us: 2500.0", first_trace.read_text(encoding="utf-8").splitlines())
            self.assertIn("# context.exposure_time_us: 3000.0", second_trace.read_text(encoding="utf-8").splitlines())


if __name__ == "__main__":
    unittest.main()
