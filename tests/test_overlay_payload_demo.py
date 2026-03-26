from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tests import _path_setup
from vision_platform.apps.opencv_prototype.overlay_payload_demo import (
    run_overlay_payload_demo,
    summarize_overlay_payload,
)
from vision_platform.libraries.common_models import RoiDefinition


class OverlayPayloadDemoTests(unittest.TestCase):
    def test_run_overlay_payload_demo_returns_composed_payload(self) -> None:
        roi = RoiDefinition(
            roi_id="roi-demo",
            shape="rectangle",
            points=((1.0, 1.0), (5.0, 1.0), (5.0, 5.0), (1.0, 5.0)),
        )

        result = run_overlay_payload_demo(poll_interval_seconds=0.001, roi=roi)

        self.assertTrue(result.success)
        self.assertIsNotNone(result.preview_frame_info)
        self.assertIsNotNone(result.focus_preview_state)
        self.assertIsNotNone(result.snapshot_focus_capture)
        self.assertIsNotNone(result.display_overlay_payload)
        self.assertEqual(result.display_overlay_payload.active_roi.roi_id, "roi-demo")
        self.assertEqual(result.display_overlay_payload.preview_focus.roi_id, "roi-demo")
        self.assertEqual(result.display_overlay_payload.snapshot_focus.roi_id, "roi-demo")

    def test_run_overlay_payload_demo_accepts_sample_images(self) -> None:
        with TemporaryDirectory() as temp_dir:
            sample_path = Path(temp_dir) / "sample_001.pgm"
            sample_path.write_bytes(b"P5\n3 3\n255\n\x00\x40\x80\x40\x80\xc0\x80\xc0\xff")

            result = run_overlay_payload_demo(sample_dir=Path(temp_dir), poll_interval_seconds=0.001)

            self.assertTrue(result.success)
            self.assertIsNotNone(result.display_overlay_payload)

    def test_summarize_overlay_payload_returns_console_friendly_text(self) -> None:
        roi = RoiDefinition(
            roi_id="roi-demo",
            shape="rectangle",
            points=((1.0, 1.0), (5.0, 1.0), (5.0, 5.0), (1.0, 5.0)),
        )
        result = run_overlay_payload_demo(poll_interval_seconds=0.001, roi=roi)

        summary = summarize_overlay_payload(result.display_overlay_payload)

        self.assertIn("active_roi=roi-demo", summary)
        self.assertIn("preview_focus=", summary)
        self.assertIn("snapshot_focus=", summary)


if __name__ == "__main__":
    unittest.main()
