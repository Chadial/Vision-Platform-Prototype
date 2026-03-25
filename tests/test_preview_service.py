from datetime import datetime, timezone
import unittest
from unittest.mock import MagicMock

from tests import _path_setup
from camera_app.models.captured_frame import CapturedFrame
from camera_app.services.preview_service import PreviewService


class PreviewServiceTests(unittest.TestCase):
    def test_refresh_once_updates_latest_frame_and_frame_info(self) -> None:
        fake_frame = CapturedFrame(
            raw_frame=b"",
            width=640,
            height=480,
            frame_id=11,
            pixel_format="Mono8",
            timestamp_utc=datetime.now(timezone.utc),
        )
        fake_driver = MagicMock()
        fake_driver.get_latest_frame.return_value = fake_frame

        service = PreviewService(fake_driver)

        frame_info = service.refresh_once()

        self.assertEqual(frame_info.frame_id, 11)
        self.assertEqual(frame_info.width, 640)
        self.assertEqual(frame_info.height, 480)
        self.assertEqual(frame_info.pixel_format, "Mono8")
        self.assertIs(service.get_latest_frame(), fake_frame)
        self.assertIs(service.get_latest_frame_info(), frame_info)

    def test_refresh_once_returns_none_when_driver_has_no_frame(self) -> None:
        fake_driver = MagicMock()
        fake_driver.get_latest_frame.return_value = None

        service = PreviewService(fake_driver)

        self.assertIsNone(service.refresh_once())
        self.assertIsNone(service.get_latest_frame())
        self.assertIsNone(service.get_latest_frame_info())

    def test_start_and_stop_toggle_driver_acquisition(self) -> None:
        fake_driver = MagicMock()
        fake_driver.get_latest_frame.return_value = None

        service = PreviewService(fake_driver, poll_interval_seconds=0.01)

        service.start()
        service.stop()

        fake_driver.start_acquisition.assert_called_once_with()
        fake_driver.stop_acquisition.assert_called_once_with()
        self.assertFalse(service.is_running)

    def test_preview_loop_logs_errors_and_continues(self) -> None:
        fake_frame = CapturedFrame(
            raw_frame=b"",
            width=320,
            height=240,
            frame_id=3,
            pixel_format="Mono8",
            timestamp_utc=datetime.now(timezone.utc),
        )
        fake_driver = MagicMock()
        fake_driver.get_latest_frame.side_effect = [RuntimeError("temporary"), fake_frame, None, None]

        service = PreviewService(fake_driver, poll_interval_seconds=0.01)

        with self.assertLogs("camera_app.services.preview_service", level="ERROR") as logs:
            service.start()
            try:
                for _ in range(20):
                    if service.get_latest_frame_info() is not None:
                        break
                    from time import sleep

                    sleep(0.01)
            finally:
                service.stop()

        self.assertTrue(any("Preview polling failed" in message for message in logs.output))
        self.assertIsNotNone(service.get_latest_frame_info())

    def test_stop_is_idempotent_when_preview_never_started(self) -> None:
        fake_driver = MagicMock()
        service = PreviewService(fake_driver)

        service.stop()
        service.stop()

        fake_driver.stop_acquisition.assert_not_called()

    def test_start_does_not_double_start_acquisition_when_already_running(self) -> None:
        fake_driver = MagicMock()
        fake_driver.get_latest_frame.return_value = None
        service = PreviewService(fake_driver, poll_interval_seconds=0.01)

        service.start()
        try:
            service.start()
        finally:
            service.stop()

        fake_driver.start_acquisition.assert_called_once_with()

    def test_start_stops_acquisition_if_worker_creation_fails(self) -> None:
        fake_driver = MagicMock()
        service = PreviewService(fake_driver)

        original_thread_class = service.__class__.__dict__["start"].__globals__["Thread"]

        class _BrokenThread:
            def __init__(self, *args, **kwargs) -> None:
                raise RuntimeError("thread setup failed")

        service.__class__.__dict__["start"].__globals__["Thread"] = _BrokenThread
        try:
            with self.assertRaisesRegex(RuntimeError, "thread setup failed"):
                service.start()
        finally:
            service.__class__.__dict__["start"].__globals__["Thread"] = original_thread_class

        fake_driver.start_acquisition.assert_called_once_with()
        fake_driver.stop_acquisition.assert_called_once_with()
        self.assertFalse(service.is_running)


if __name__ == "__main__":
    unittest.main()
