from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tests import _path_setup
from camera_app.smoke.opencv_preview_demo import run_opencv_preview_demo
from camera_app.smoke.opencv_save_demo import run_opencv_save_demo


class OpenCvSmokeDemoTests(unittest.TestCase):
    def test_run_opencv_preview_demo_returns_typed_result(self) -> None:
        result = run_opencv_preview_demo(frame_limit=3, poll_interval_seconds=0.001)

        self.assertTrue(result.success)
        self.assertEqual(result.rendered_frames, 3)
        self.assertIsNone(result.snapshot_path)
        self.assertIsNone(result.saved_path)

    def test_run_opencv_save_demo_returns_saved_path_for_mono8_png(self) -> None:
        with TemporaryDirectory() as temp_dir:
            result = run_opencv_save_demo(
                save_directory=Path(temp_dir),
                file_stem="opencv_demo",
                pixel_format="Mono8",
                file_extension=".png",
            )

            self.assertTrue(result.success)
            self.assertIsNotNone(result.saved_path)
            self.assertTrue(result.saved_path.exists())
            self.assertEqual(result.saved_path.name, "opencv_demo.png")

    def test_run_opencv_save_demo_returns_saved_path_for_mono16_tiff(self) -> None:
        with TemporaryDirectory() as temp_dir:
            result = run_opencv_save_demo(
                save_directory=Path(temp_dir),
                file_stem="opencv_demo",
                pixel_format="Mono16",
                file_extension=".tiff",
            )

            self.assertTrue(result.success)
            self.assertIsNotNone(result.saved_path)
            self.assertTrue(result.saved_path.exists())
            self.assertEqual(result.saved_path.name, "opencv_demo.tiff")


if __name__ == "__main__":
    unittest.main()
