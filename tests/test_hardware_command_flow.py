from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tests import _path_setup
from vision_platform.apps.opencv_prototype.hardware_command_flow import run_hardware_command_flow
from vision_platform.bootstrap import build_simulated_camera_subsystem
from vision_platform.models import CameraConfiguration


class HardwareCommandFlowTests(unittest.TestCase):
    def test_run_hardware_command_flow_can_be_exercised_through_injected_subsystem(self) -> None:
        with TemporaryDirectory() as temp_dir:
            subsystem = build_simulated_camera_subsystem(
                preview_poll_interval_seconds=0.001,
                shared_poll_interval_seconds=0.001,
                recording_poll_interval_seconds=0.001,
                interval_capture_poll_interval_seconds=0.001,
            )

            result = run_hardware_command_flow(
                base_directory=Path(temp_dir),
                run_name="run_001",
                camera_id="sim-hardware-flow",
                snapshot_stem="snapshot",
                snapshot_extension=".png",
                interval_stem="interval",
                interval_extension=".raw",
                interval_seconds=0.02,
                interval_frame_count=2,
                recording_stem="recording",
                recording_extension=".raw",
                frame_limit=2,
                target_frame_rate=10.0,
                preview_warmup_timeout_seconds=1.0,
                configuration=CameraConfiguration(
                    exposure_time_us=1500.0,
                    pixel_format="Mono8",
                    roi_offset_x=0,
                    roi_offset_y=0,
                    roi_width=320,
                    roi_height=240,
                ),
                subsystem=subsystem,
            )

            run_directory = Path(temp_dir) / "run_001"
            self.assertTrue(result.success)
            self.assertEqual(result.snapshot_path, run_directory / "snapshot.png")
            self.assertTrue(result.snapshot_path.exists())
            self.assertIsNotNone(result.preview_frame_info)
            self.assertTrue((run_directory / "interval_000000.raw").exists())
            self.assertTrue((run_directory / "interval_000001.raw").exists())
            self.assertTrue((run_directory / "recording_000000.raw").exists())
            self.assertTrue((run_directory / "recording_000001.raw").exists())
            self.assertTrue((run_directory / "recording_recording_log.csv").exists())
            self.assertEqual(result.interval_capture_status.frames_written, 2)
            self.assertEqual(result.final_status.recording.frames_written, 2)
            self.assertFalse(result.final_status.recording.is_recording)
            self.assertTrue(result.final_status.can_start_recording)
            self.assertFalse(result.stop_status["recording"].is_recording)
            self.assertFalse(result.stop_status["interval_capture"].is_capturing)


if __name__ == "__main__":
    unittest.main()
