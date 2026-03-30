from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep
import unittest

from tests import _path_setup
from vision_platform.models import CapturedFrame, IntervalCaptureRequest
from vision_platform.services.recording_service import IntervalCaptureService
from vision_platform.services.stream_service import SharedFrameSource


class _StreamingIntervalDriver:
    def __init__(self) -> None:
        self._next_frame_id = 0
        self.start_calls = 0
        self.stop_calls = 0

    def start_acquisition(self) -> None:
        self.start_calls += 1

    def stop_acquisition(self) -> None:
        self.stop_calls += 1

    def get_latest_frame(self) -> CapturedFrame:
        frame = CapturedFrame(
            raw_frame=bytes([self._next_frame_id % 256]),
            width=1,
            height=1,
            frame_id=self._next_frame_id,
            camera_timestamp=1000 + self._next_frame_id,
            pixel_format="Mono8",
        )
        self._next_frame_id += 1
        return frame


class _StaticIntervalDriver:
    def __init__(self) -> None:
        self.start_calls = 0
        self.stop_calls = 0
        self._frame = CapturedFrame(
            raw_frame=b"x",
            width=1,
            height=1,
            frame_id=0,
            camera_timestamp=1000,
            pixel_format="Mono8",
        )

    def start_acquisition(self) -> None:
        self.start_calls += 1

    def stop_acquisition(self) -> None:
        self.stop_calls += 1

    def get_latest_frame(self) -> CapturedFrame:
        return self._frame


class IntervalCaptureServiceTests(unittest.TestCase):
    def test_interval_capture_writes_sequence_until_frame_limit(self) -> None:
        driver = _StreamingIntervalDriver()
        service = IntervalCaptureService(driver, poll_interval_seconds=0.001)

        with TemporaryDirectory() as temp_dir:
            status = service.start_capture(
                IntervalCaptureRequest(
                    save_directory=Path(temp_dir),
                    file_stem="interval",
                    file_extension=".raw",
                    interval_seconds=0.01,
                    max_frame_count=3,
                )
            )

            self.assertTrue(status.is_capturing)
            for _ in range(200):
                status = service.get_status()
                if not status.is_capturing and status.frames_written == 3:
                    break
                sleep(0.01)

            final_status = service.get_status()
            self.assertFalse(final_status.is_capturing)
            self.assertEqual(final_status.frames_written, 3)
            self.assertTrue((Path(temp_dir) / "interval_000000.raw").exists())
            self.assertTrue((Path(temp_dir) / "interval_000001.raw").exists())
            self.assertTrue((Path(temp_dir) / "interval_000002.raw").exists())
            self.assertEqual(driver.start_calls, 1)
            self.assertEqual(driver.stop_calls, 1)

    def test_interval_capture_rejects_missing_stop_condition(self) -> None:
        driver = _StreamingIntervalDriver()
        service = IntervalCaptureService(driver)

        with TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(ValueError, "requires max_frame_count or duration_seconds"):
                service.start_capture(
                    IntervalCaptureRequest(
                        save_directory=Path(temp_dir),
                        file_stem="interval",
                        interval_seconds=1.0,
                    )
                )

    def test_interval_capture_rejects_non_positive_interval(self) -> None:
        driver = _StreamingIntervalDriver()
        service = IntervalCaptureService(driver)

        with TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(ValueError, "interval_seconds must be greater than zero"):
                service.start_capture(
                    IntervalCaptureRequest(
                        save_directory=Path(temp_dir),
                        file_stem="interval",
                        interval_seconds=0,
                        max_frame_count=1,
                    )
                )

    def test_interval_capture_can_use_shared_frame_source(self) -> None:
        driver = _StreamingIntervalDriver()
        shared_frame_source = SharedFrameSource(driver, poll_interval_seconds=0.001)
        service = IntervalCaptureService(
            driver,
            poll_interval_seconds=0.001,
            shared_frame_source=shared_frame_source,
        )

        with TemporaryDirectory() as temp_dir:
            shared_frame_source.acquire()
            try:
                sleep(0.02)
                service.start_capture(
                    IntervalCaptureRequest(
                        save_directory=Path(temp_dir),
                        file_stem="shared_interval",
                        file_extension=".raw",
                        interval_seconds=0.01,
                        max_frame_count=2,
                    )
                )

                for _ in range(200):
                    status = service.get_status()
                    if not status.is_capturing and status.frames_written == 2:
                        break
                    sleep(0.01)
            finally:
                shared_frame_source.release()

            self.assertEqual(service.get_status().frames_written, 2)
            self.assertEqual(driver.start_calls, 1)
            self.assertEqual(driver.stop_calls, 1)

    def test_interval_capture_reports_timing_warning_and_completion_summary_when_intervals_are_skipped(self) -> None:
        driver = _StaticIntervalDriver()
        service = IntervalCaptureService(driver, poll_interval_seconds=0.001)

        with TemporaryDirectory() as temp_dir:
            status = service.start_capture(
                IntervalCaptureRequest(
                    save_directory=Path(temp_dir),
                    file_stem="interval",
                    file_extension=".raw",
                    interval_seconds=0.005,
                    duration_seconds=0.03,
                )
            )

            self.assertTrue(status.is_capturing)
            saw_active_warning = False
            for _ in range(200):
                status = service.get_status()
                if status.last_error and status.last_error.startswith("Interval timing warning:"):
                    saw_active_warning = True
                if not status.is_capturing:
                    break
                sleep(0.005)

            final_status = service.get_status()
            self.assertTrue(saw_active_warning)
            self.assertFalse(final_status.is_capturing)
            self.assertEqual(final_status.frames_written, 1)
            self.assertGreater(final_status.skipped_intervals, 0)
            self.assertEqual(
                final_status.last_error,
                f"Interval capture completed with skipped_intervals={final_status.skipped_intervals}",
            )
            self.assertEqual(driver.start_calls, 1)
            self.assertEqual(driver.stop_calls, 1)


if __name__ == "__main__":
    unittest.main()
