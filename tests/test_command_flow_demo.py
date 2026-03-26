from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tests import _path_setup
from camera_app.smoke.command_flow_demo import run_simulated_command_flow


class CommandFlowDemoTests(unittest.TestCase):
    def test_run_simulated_command_flow_creates_subdirectory_snapshot_and_recording_outputs(self) -> None:
        with TemporaryDirectory() as temp_dir:
            result = run_simulated_command_flow(
                base_directory=Path(temp_dir),
                run_name="run_001",
                snapshot_stem="snapshot",
                interval_stem="interval",
                interval_seconds=0.02,
                interval_frame_count=2,
                recording_stem="recording",
                frame_limit=2,
                target_frame_rate=8.0,
            )

            run_directory = Path(temp_dir) / "run_001"
            self.assertTrue(result.success)
            self.assertTrue(result.snapshot_path.exists())
            self.assertEqual(result.snapshot_path, run_directory / "snapshot.png")
            self.assertTrue((run_directory / "interval_000000.raw").exists())
            self.assertTrue((run_directory / "interval_000001.raw").exists())
            self.assertTrue((run_directory / "recording_000000.raw").exists())
            self.assertTrue((run_directory / "recording_000001.raw").exists())
            self.assertTrue((run_directory / "recording_recording_log.csv").exists())
            self.assertEqual(result.interval_capture_status.frames_written, 2)
            self.assertEqual(result.initial_recording_status.save_directory, run_directory)
            self.assertEqual(result.final_status.default_save_directory, run_directory)
            self.assertEqual(result.final_status.recording.frames_written, 2)
            self.assertEqual(result.final_status.interval_capture.frames_written, 2)
            self.assertFalse(result.final_status.recording.is_recording)
            self.assertTrue(result.final_status.can_save_snapshot)
            self.assertTrue(result.final_status.can_start_recording)
            self.assertFalse(result.final_status.can_stop_recording)
            self.assertFalse(result.stop_status["recording"].is_recording)
            self.assertFalse(result.stop_status["interval_capture"].is_capturing)


if __name__ == "__main__":
    unittest.main()
