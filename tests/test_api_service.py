from dataclasses import asdict
from pathlib import Path
import unittest

from tests import _path_setup
from vision_platform.models import CameraConfiguration, CameraStatus, IntervalCaptureStatus, RecordingStatus, SubsystemStatus
from vision_platform.services.api_service import (
    ApiSubsystemStatusPayload,
    map_subsystem_status_to_api_payload,
)


class ApiServiceTests(unittest.TestCase):
    def test_map_subsystem_status_to_api_payload_converts_paths_and_nested_models(self) -> None:
        status = SubsystemStatus(
            camera=CameraStatus(
                is_initialized=True,
                is_acquiring=False,
                source_kind="simulation",
                driver_name="SimulatedCameraDriver",
                camera_id="sim-api",
                capabilities_available=True,
            ),
            configuration=CameraConfiguration(
                exposure_time_us=2500.0,
                pixel_format="Mono8",
                roi_width=320,
                roi_height=240,
            ),
            recording=RecordingStatus(
                is_recording=True,
                frames_written=12,
                dropped_frames=1,
                save_directory=Path("C:/captures/recording"),
                active_file_stem="recording",
            ),
            interval_capture=IntervalCaptureStatus(
                is_capturing=False,
                frames_written=3,
                skipped_intervals=0,
                save_directory=Path("C:/captures/interval"),
                active_file_stem="interval",
            ),
            default_save_directory=Path("C:/captures"),
            is_save_directory_configured=True,
            has_interval_capture_service=True,
            can_apply_configuration=True,
            can_save_snapshot=True,
            can_start_recording=False,
            can_stop_recording=True,
            can_start_interval_capture=True,
            can_stop_interval_capture=False,
        )

        payload = map_subsystem_status_to_api_payload(status)

        self.assertIsInstance(payload, ApiSubsystemStatusPayload)
        self.assertEqual(payload.camera.camera_id, "sim-api")
        self.assertEqual(payload.configuration.pixel_format, "Mono8")
        self.assertEqual(payload.recording.save_directory, str(Path("C:/captures/recording")))
        self.assertEqual(payload.interval_capture.save_directory, str(Path("C:/captures/interval")))
        self.assertEqual(payload.default_save_directory, str(Path("C:/captures")))
        self.assertTrue(payload.can_save_snapshot)

    def test_api_payload_is_dataclass_serializable(self) -> None:
        status = SubsystemStatus(
            camera=CameraStatus(),
            configuration=None,
            recording=RecordingStatus(),
            interval_capture=IntervalCaptureStatus(),
        )

        payload_dict = asdict(map_subsystem_status_to_api_payload(status))

        self.assertIn("camera", payload_dict)
        self.assertIn("recording", payload_dict)
        self.assertIsNone(payload_dict["default_save_directory"])
        self.assertFalse(payload_dict["can_save_snapshot"])


if __name__ == "__main__":
    unittest.main()
