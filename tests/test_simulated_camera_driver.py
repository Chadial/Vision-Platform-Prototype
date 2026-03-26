from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep
import unittest

from tests import _path_setup
from camera_app.drivers.simulated_camera_driver import SimulatedCameraDriver
from camera_app.models.camera_configuration import CameraConfiguration
from camera_app.models.snapshot_request import SnapshotRequest
from camera_app.models.recording_request import RecordingRequest
from camera_app.services.preview_service import PreviewService
from camera_app.services.recording_service import RecordingService
from camera_app.services.shared_frame_source import SharedFrameSource
from camera_app.services.snapshot_service import SnapshotService


class SimulatedCameraDriverTests(unittest.TestCase):
    def test_initialize_and_capture_snapshot_with_generated_frame(self) -> None:
        driver = SimulatedCameraDriver(width=4, height=3, pixel_format="Mono8")

        status = driver.initialize(camera_id="sim-cam")
        frame = driver.capture_snapshot()

        self.assertTrue(status.is_initialized)
        self.assertEqual(status.camera_id, "sim-cam")
        self.assertEqual(frame.width, 4)
        self.assertEqual(frame.height, 3)
        self.assertEqual(frame.pixel_format, "Mono8")
        self.assertEqual(frame.frame_id, 0)
        self.assertEqual(len(frame.raw_frame), 12)

    def test_apply_configuration_changes_generated_pixel_format(self) -> None:
        driver = SimulatedCameraDriver(width=2, height=2, pixel_format="Mono8")
        driver.initialize()
        driver.apply_configuration(CameraConfiguration(pixel_format="Rgb8"))

        frame = driver.capture_snapshot()

        self.assertEqual(frame.pixel_format, "Rgb8")
        self.assertEqual(len(frame.raw_frame), 12)

    def test_simulated_driver_supports_mono16_generated_frames(self) -> None:
        driver = SimulatedCameraDriver(width=2, height=2, pixel_format="Mono16")
        driver.initialize()

        frame = driver.capture_snapshot()

        self.assertEqual(frame.pixel_format, "Mono16")
        self.assertEqual(len(frame.raw_frame), 8)

    def test_preview_service_reads_frames_from_simulated_driver(self) -> None:
        driver = SimulatedCameraDriver(width=3, height=2, pixel_format="Mono8")
        driver.initialize()
        preview_service = PreviewService(driver, poll_interval_seconds=0.001)

        preview_service.start()
        try:
            for _ in range(50):
                frame_info = preview_service.get_latest_frame_info()
                if frame_info is not None:
                    break
                sleep(0.01)
            self.assertIsNotNone(preview_service.get_latest_frame_info())
            self.assertEqual(preview_service.get_latest_frame_info().width, 3)
            self.assertEqual(preview_service.get_latest_frame_info().height, 2)
        finally:
            preview_service.stop()

    def test_snapshot_service_saves_png_from_simulated_driver(self) -> None:
        driver = SimulatedCameraDriver(width=2, height=2, pixel_format="Mono8")
        driver.initialize()
        snapshot_service = SnapshotService(driver)

        with TemporaryDirectory() as temp_dir:
            saved_path = snapshot_service.save_snapshot(
                SnapshotRequest(
                    save_directory=Path(temp_dir),
                    file_stem="sim_snapshot",
                    file_extension=".png",
                )
            )

            self.assertTrue(saved_path.exists())
            self.assertEqual(saved_path.name, "sim_snapshot.png")

    def test_recording_service_writes_sequence_from_simulated_driver(self) -> None:
        driver = SimulatedCameraDriver(width=2, height=2, pixel_format="Mono8")
        driver.initialize()
        recording_service = RecordingService(driver, poll_interval_seconds=0.001)

        with TemporaryDirectory() as temp_dir:
            recording_service.start_recording(
                RecordingRequest(
                    save_directory=Path(temp_dir),
                    file_stem="sim_recording",
                    file_extension=".raw",
                    frame_limit=3,
                    queue_size=4,
                )
            )

            for _ in range(100):
                status = recording_service.get_status()
                if not status.is_recording and status.frames_written == 3:
                    break
                sleep(0.01)

            self.assertEqual(recording_service.get_status().frames_written, 3)
            self.assertTrue((Path(temp_dir) / "sim_recording_000000.raw").exists())
            self.assertTrue((Path(temp_dir) / "sim_recording_recording_log.csv").exists())

    def test_preview_and_recording_can_share_one_acquisition_loop(self) -> None:
        driver = SimulatedCameraDriver(width=2, height=2, pixel_format="Mono8")
        driver.initialize()
        shared_frame_source = SharedFrameSource(driver, poll_interval_seconds=0.001)
        preview_service = PreviewService(
            driver,
            poll_interval_seconds=0.001,
            shared_frame_source=shared_frame_source,
        )
        recording_service = RecordingService(
            driver,
            poll_interval_seconds=0.001,
            shared_frame_source=shared_frame_source,
        )

        with TemporaryDirectory() as temp_dir:
            preview_service.start()
            try:
                for _ in range(100):
                    if preview_service.get_latest_frame_info() is not None:
                        break
                    sleep(0.01)

                recording_service.start_recording(
                    RecordingRequest(
                        save_directory=Path(temp_dir),
                        file_stem="shared_recording",
                        file_extension=".raw",
                        frame_limit=3,
                        queue_size=4,
                        target_frame_rate=1.0,
                    )
                )

                preview_frame_id_before = preview_service.get_latest_frame_info().frame_id

                for _ in range(400):
                    status = recording_service.get_status()
                    preview_info = preview_service.get_latest_frame_info()
                    if not status.is_recording and status.frames_written == 3 and preview_info is not None:
                        break
                    sleep(0.01)

                final_status = recording_service.get_status()
                self.assertFalse(final_status.is_recording)
                self.assertEqual(final_status.frames_written, 3)
                self.assertIsNotNone(preview_service.get_latest_frame_info())
                self.assertGreater(preview_service.get_latest_frame_info().frame_id, preview_frame_id_before)
                self.assertTrue((Path(temp_dir) / "shared_recording_000000.raw").exists())
                self.assertTrue((Path(temp_dir) / "shared_recording_recording_log.csv").exists())

                preview_frame_during_idle = preview_service.get_latest_frame_info().frame_id
                for _ in range(100):
                    latest_info = preview_service.get_latest_frame_info()
                    if latest_info is not None and latest_info.frame_id > preview_frame_during_idle:
                        break
                    sleep(0.01)

                self.assertGreater(preview_service.get_latest_frame_info().frame_id, preview_frame_during_idle)
            finally:
                preview_service.stop()

    def test_simulated_driver_uses_sample_pgm_sequence(self) -> None:
        with TemporaryDirectory() as temp_dir:
            sample_path = Path(temp_dir) / "sample_001.pgm"
            sample_path.write_bytes(b"P5\n2 2\n255\n\x00\x40\x80\xff")

            driver = SimulatedCameraDriver(sample_image_paths=[sample_path], loop_samples=False)
            driver.initialize()

            frame = driver.capture_snapshot()

            self.assertEqual(frame.width, 2)
            self.assertEqual(frame.height, 2)
            self.assertEqual(frame.pixel_format, "Mono8")
            self.assertEqual(frame.raw_frame, b"\x00\x40\x80\xff")


if __name__ == "__main__":
    unittest.main()
