from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tests import _path_setup
from vision_platform.apps.opencv_prototype.focus_preview_demo import run_focus_preview_demo
from vision_platform.libraries.common_models import RoiDefinition


class FocusPreviewDemoTests(unittest.TestCase):
    def test_run_focus_preview_demo_returns_focus_state_without_roi(self) -> None:
        result = run_focus_preview_demo(poll_interval_seconds=0.001)

        self.assertTrue(result.success)
        self.assertIsNotNone(result.preview_frame_info)
        self.assertIsNotNone(result.focus_preview_state)
        self.assertTrue(result.focus_preview_state.result.is_valid)
        self.assertGreaterEqual(result.focus_preview_state.result.score, 0.0)

    def test_run_focus_preview_demo_returns_roi_anchored_overlay(self) -> None:
        roi = RoiDefinition(
            roi_id="roi-demo",
            shape="rectangle",
            points=((1.0, 1.0), (5.0, 1.0), (5.0, 5.0), (1.0, 5.0)),
        )

        result = run_focus_preview_demo(poll_interval_seconds=0.001, roi=roi)

        self.assertTrue(result.success)
        self.assertEqual(result.focus_preview_state.overlay.roi_id, "roi-demo")
        self.assertEqual(result.focus_preview_state.overlay.region_bounds, (1.0, 1.0, 5.0, 5.0))
        self.assertEqual(result.focus_preview_state.overlay.anchor_x, 3.0)
        self.assertEqual(result.focus_preview_state.overlay.anchor_y, 3.0)

    def test_run_focus_preview_demo_accepts_sample_images(self) -> None:
        with TemporaryDirectory() as temp_dir:
            sample_path = Path(temp_dir) / "sample_001.pgm"
            sample_path.write_bytes(b"P5\n3 3\n255\n\x00\x40\x80\x40\x80\xc0\x80\xc0\xff")

            result = run_focus_preview_demo(sample_dir=Path(temp_dir), poll_interval_seconds=0.001)

            self.assertTrue(result.success)
            self.assertIsNotNone(result.focus_preview_state)


if __name__ == "__main__":
    unittest.main()
