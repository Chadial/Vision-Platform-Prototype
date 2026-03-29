from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep
import unittest

from tests import _path_setup
from vision_platform.integrations.camera import SimulatedCameraDriver
from vision_platform.libraries.common_models import RoiDefinition
from vision_platform.models import CameraConfiguration, IntervalCaptureRequest, RecordingRequest
from vision_platform.services.recording_service import CameraService
from vision_platform.services.stream_service import CameraStreamService


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

    def test_stream_service_can_produce_focus_state_from_simulated_preview(self) -> None:
        driver = SimulatedCameraDriver(width=6, height=6, pixel_format="Mono8")
        camera_service = CameraService(driver)
        camera_service.initialize(camera_id="sim-focus")
        camera_service.apply_configuration(CameraConfiguration(pixel_format="Mono8"))
        stream_service = CameraStreamService(
            driver,
            preview_poll_interval_seconds=0.001,
            shared_poll_interval_seconds=0.001,
        )
        focus_preview_service = stream_service.create_focus_preview_service()
        roi = RoiDefinition(
            roi_id="focus-zone",
            shape="rectangle",
            points=((1.0, 1.0), (5.0, 1.0), (5.0, 5.0), (1.0, 5.0)),
        )

        stream_service.start_preview()
        try:
            focus_state = None
            for _ in range(100):
                focus_state = focus_preview_service.refresh_once(roi=roi)
                if focus_state is not None and focus_state.result.is_valid:
                    break
                sleep(0.01)

            self.assertIsNotNone(focus_state)
            self.assertTrue(focus_state.result.is_valid)
            self.assertEqual(focus_state.result.method, "laplace")
            self.assertEqual(focus_state.overlay.roi_id, "focus-zone")
            self.assertEqual(focus_state.overlay.region_bounds, (1.0, 1.0, 5.0, 5.0))
            self.assertEqual(focus_state.overlay.anchor_x, 3.0)
            self.assertEqual(focus_state.overlay.anchor_y, 3.0)
            self.assertEqual(
                focus_preview_service.get_latest_focus_state().result.source_frame_id,
                focus_state.result.source_frame_id,
            )
        finally:
            stream_service.stop_preview()
            camera_service.shutdown()

    def test_stream_service_exposes_shared_roi_state_for_focus_preview_consumers(self) -> None:
        driver = SimulatedCameraDriver(width=6, height=6, pixel_format="Mono8")
        camera_service = CameraService(driver)
        camera_service.initialize(camera_id="sim-focus-state")
        camera_service.apply_configuration(CameraConfiguration(pixel_format="Mono8"))
        stream_service = CameraStreamService(
            driver,
            preview_poll_interval_seconds=0.001,
            shared_poll_interval_seconds=0.001,
        )
        roi_state_service = stream_service.get_roi_state_service()
        roi_state_service.set_active_roi(
            RoiDefinition(
                roi_id="focus-zone",
                shape="rectangle",
                points=((1.0, 1.0), (5.0, 1.0), (5.0, 5.0), (1.0, 5.0)),
            )
        )
        focus_preview_service = stream_service.create_focus_preview_service()

        stream_service.start_preview()
        try:
            focus_state = None
            for _ in range(100):
                focus_state = focus_preview_service.refresh_once()
                if focus_state is not None and focus_state.result.is_valid:
                    break
                sleep(0.01)

            self.assertIsNotNone(focus_state)
            self.assertTrue(focus_state.result.is_valid)
            self.assertEqual(focus_state.result.roi_id, "focus-zone")
            self.assertEqual(focus_state.overlay.roi_id, "focus-zone")
            self.assertEqual(focus_state.overlay.region_bounds, (1.0, 1.0, 5.0, 5.0))
        finally:
            stream_service.stop_preview()
            camera_service.shutdown()

    def test_stream_service_can_create_tenengrad_focus_preview_consumer(self) -> None:
        driver = SimulatedCameraDriver(width=6, height=6, pixel_format="Mono8")
        camera_service = CameraService(driver)
        camera_service.initialize(camera_id="sim-focus-tenengrad")
        camera_service.apply_configuration(CameraConfiguration(pixel_format="Mono8"))
        stream_service = CameraStreamService(
            driver,
            preview_poll_interval_seconds=0.001,
            shared_poll_interval_seconds=0.001,
        )
        focus_preview_service = stream_service.create_focus_preview_service(focus_method="tenengrad")

        stream_service.start_preview()
        try:
            focus_state = None
            for _ in range(100):
                focus_state = focus_preview_service.refresh_once()
                if focus_state is not None and focus_state.result.is_valid:
                    break
                sleep(0.01)

            self.assertIsNotNone(focus_state)
            self.assertTrue(focus_state.result.is_valid)
            self.assertEqual(focus_state.result.method, "tenengrad")
            self.assertEqual(focus_state.result.metric_name, "tenengrad_mean_gradient_energy")
        finally:
            stream_service.stop_preview()
            camera_service.shutdown()


if __name__ == "__main__":
    unittest.main()
