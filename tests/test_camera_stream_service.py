from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep
import unittest

from tests import _path_setup
from camera_app.drivers.simulated_camera_driver import SimulatedCameraDriver
from camera_app.models.camera_configuration import CameraConfiguration
from camera_app.models.interval_capture_request import IntervalCaptureRequest
from camera_app.models.recording_request import RecordingRequest
from camera_app.services.camera_service import CameraService
from camera_app.services.camera_stream_service import CameraStreamService


class CameraStreamServiceTests(unittest.TestCase):
    def test_stream_service_provides_preview_and_recording_from_shared_stream(self) -> None:
        driver = SimulatedCameraDriver(width=2, height=2, pixel_format="Mono8")
        camera_service = CameraService(driver)
        camera_service.initialize(camera_id="sim-stream")
        camera_service.apply_configuration(CameraConfiguration(pixel_format="Mono8"))
        stream_service = CameraStreamService(
            driver,
            preview_poll_interval_seconds=0.001,
            shared_poll_interval_seconds=0.001,
        )
        recording_service = stream_service.create_recording_service(
            poll_interval_seconds=0.001,
            configuration_provider=camera_service.get_last_configuration,
        )

        with TemporaryDirectory() as temp_dir:
            stream_service.start_preview()
            try:
                for _ in range(100):
                    preview_info = stream_service.get_latest_frame_info()
                    if preview_info is not None:
                        break
                    sleep(0.01)

                self.assertTrue(stream_service.is_preview_running)
                self.assertIsNotNone(stream_service.get_latest_frame())
                self.assertIsNotNone(stream_service.get_latest_frame_info())

                recording_service.start_recording(
                    RecordingRequest(
                        save_directory=Path(temp_dir),
                        file_stem="stream_recording",
                        file_extension=".raw",
                        frame_limit=2,
                        queue_size=4,
                        target_frame_rate=1.0,
                    )
                )

                for _ in range(300):
                    status = recording_service.get_status()
                    if not status.is_recording and status.frames_written == 2:
                        break
                    sleep(0.01)

                self.assertEqual(recording_service.get_status().frames_written, 2)
                self.assertTrue((Path(temp_dir) / "stream_recording_000000.raw").exists())
                self.assertTrue((Path(temp_dir) / "stream_recording_recording_log.csv").exists())
                self.assertTrue(stream_service.is_preview_running)
                self.assertIsNotNone(stream_service.get_latest_frame_info())
            finally:
                stream_service.stop_preview()
                camera_service.shutdown()

        self.assertFalse(stream_service.is_preview_running)

    def test_stream_service_supports_preview_with_interval_capture(self) -> None:
        driver = SimulatedCameraDriver(width=2, height=2, pixel_format="Mono8")
        camera_service = CameraService(driver)
        camera_service.initialize(camera_id="sim-stream")
        camera_service.apply_configuration(CameraConfiguration(pixel_format="Mono8"))
        stream_service = CameraStreamService(
            driver,
            preview_poll_interval_seconds=0.001,
            shared_poll_interval_seconds=0.001,
        )
        interval_capture_service = stream_service.create_interval_capture_service(poll_interval_seconds=0.001)

        with TemporaryDirectory() as temp_dir:
            stream_service.start_preview()
            try:
                for _ in range(100):
                    if stream_service.get_latest_frame_info() is not None:
                        break
                    sleep(0.01)

                starting_frame_id = stream_service.get_latest_frame_info().frame_id
                interval_capture_service.start_capture(
                    IntervalCaptureRequest(
                        save_directory=Path(temp_dir),
                        file_stem="interval",
                        file_extension=".raw",
                        interval_seconds=0.02,
                        max_frame_count=3,
                    )
                )

                for _ in range(300):
                    status = interval_capture_service.get_status()
                    if not status.is_capturing and status.frames_written == 3:
                        break
                    sleep(0.01)

                final_status = interval_capture_service.get_status()
                self.assertFalse(final_status.is_capturing)
                self.assertEqual(final_status.frames_written, 3)
                self.assertTrue((Path(temp_dir) / "interval_000000.raw").exists())
                self.assertTrue(stream_service.is_preview_running)
                self.assertGreater(stream_service.get_latest_frame_info().frame_id, starting_frame_id)
            finally:
                stream_service.stop_preview()
                camera_service.shutdown()


if __name__ == "__main__":
    unittest.main()
