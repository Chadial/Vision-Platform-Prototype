from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tests import _path_setup
from camera_app.smoke.simulated_demo import run_simulated_demo


class SimulatedDemoTests(unittest.TestCase):
    def test_run_simulated_demo_creates_snapshot_and_recording_outputs(self) -> None:
        with TemporaryDirectory() as temp_dir:
            result = run_simulated_demo(
                save_directory=Path(temp_dir),
                file_stem="demo",
                frame_limit=2,
            )

            self.assertTrue(result["snapshot_path"].exists())
            self.assertTrue((Path(temp_dir) / "demo_recording_000000.raw").exists())
            self.assertTrue((Path(temp_dir) / "demo_recording_recording_log.csv").exists())
            self.assertEqual(result["recording_status"].frames_written, 2)
            self.assertIsNotNone(result["preview_frame_info"])


if __name__ == "__main__":
    unittest.main()
