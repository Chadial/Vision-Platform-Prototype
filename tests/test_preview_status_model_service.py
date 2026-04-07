import unittest

from tests import _path_setup
from vision_platform.services.display_service import PreviewStatusModelService


class PreviewStatusModelServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = PreviewStatusModelService()

    def test_build_status_model_captures_descriptive_state_without_renderer_strings(self) -> None:
        model = self.service.build_status_model(
            fit_to_window=False,
            display_scale=2.0,
            viewport_origin_scaled=(40, 50),
            fps=10.0,
            selected_point=(20, 10),
            selected_point_text="x=20, y=10",
            warning="Capability probe unavailable",
            transient_message="Copied x=20, y=10",
            has_focus_provider=True,
            focus_status_visible=True,
            focus_state=None,
            roi_mode="rectangle",
            roi_anchor_point=(10, 20),
            roi_preview_point=(40, 60),
            active_roi=None,
            has_snapshot_shortcut=True,
            has_focus_toggle=True,
        )

        self.assertEqual(
            [entry.value for entry in model.primary_line.entries],
            [
                "ZOOM 2.00x",
                "view=40,50",
                "FPS 10.0",
                "Selected x=20, y=10",
                "WARN: Capability probe unavailable",
                "Copied x=20, y=10",
            ],
        )
        self.assertEqual(model.roi_status.state, "anchor_pending")
        self.assertEqual(model.roi_status.roi_mode, "rectangle")
        self.assertEqual(model.roi_status.anchor_point, (10, 20))
        self.assertEqual(model.roi_status.preview_point, (40, 60))
        self.assertEqual(model.focus_status.state, "waiting")
        self.assertEqual(model.shortcuts[3].action, "snapshot")

    def test_build_overlay_model_exposes_crosshair_and_roi_layers(self) -> None:
        roi = type("Roi", (), {"shape": "rectangle", "points": ((10, 20), (40, 60))})()

        overlay_model = self.service.build_overlay_model(
            crosshair_visible=True,
            selected_point=(12, 34),
            draft_roi=roi,
            active_roi=roi,
            focus_status_visible=True,
            focus_state=None,
            focus_anchor_point=(25, 30),
            show_viewport_outline=True,
        )

        self.assertEqual(overlay_model.crosshair_point, (12, 34))
        self.assertIs(overlay_model.draft_roi, roi)
        self.assertIs(overlay_model.active_roi, roi)
        self.assertEqual(overlay_model.focus_anchor_point, (25, 30))
        self.assertEqual(overlay_model.focus_label, "Focus...")
        self.assertTrue(overlay_model.show_viewport_outline)


if __name__ == "__main__":
    unittest.main()
