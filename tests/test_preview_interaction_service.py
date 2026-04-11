import unittest

from tests import _path_setup
from vision_platform.libraries.common_models import RoiDefinition
from vision_platform.services.display_service import (
    DisplayGeometryService,
    PreviewInteractionCommand,
    PreviewInteractionService,
    PreviewInteractionState,
    ZoomPanState,
)
from vision_platform.services.stream_service import RoiStateService


class PreviewInteractionServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.geometry_service = DisplayGeometryService()
        self.roi_state_service = RoiStateService()
        self.service = PreviewInteractionService(
            self.geometry_service,
            self.roi_state_service,
        )
        self.interaction_state = PreviewInteractionState()
        self.geometry_state = ZoomPanState()

    def _apply(self, command: PreviewInteractionCommand, **kwargs):
        defaults = {
            "last_display_scale": 1.0,
            "last_viewport_mapping": None,
            "zoom_step": 1.5,
            "min_zoom_scale": 0.05,
            "max_zoom_scale": 8.0,
            "has_focus_provider": False,
            "has_snapshot_callback": False,
            "coordinate_formatter": lambda x, y: f"x={x}, y={y}",
            "roi_builder": lambda roi_mode, anchor, point: type(
                "Roi",
                (),
                {"shape": roi_mode or "rectangle", "points": (anchor, point)},
            )(),
        }
        defaults.update(kwargs)
        return self.service.apply_command(command, self.interaction_state, self.geometry_state, **defaults)

    def test_toggle_crosshair_updates_shared_interaction_state(self) -> None:
        self._apply(PreviewInteractionCommand(action="toggle_crosshair"))

        self.assertTrue(self.interaction_state.crosshair_visible)
        self.assertEqual(self.interaction_state.last_status_message, "Crosshair shown")

    def test_toggle_focus_without_provider_reports_unavailable(self) -> None:
        self._apply(PreviewInteractionCommand(action="toggle_focus"))

        self.assertEqual(self.interaction_state.last_status_message, "Focus display unavailable")

    def test_toggle_focus_with_provider_toggles_visibility(self) -> None:
        self._apply(PreviewInteractionCommand(action="toggle_focus"), has_focus_provider=True)

        self.assertFalse(self.interaction_state.focus_status_visible)
        self.assertEqual(self.interaction_state.last_status_message, "Focus hidden")

    def test_select_source_point_sets_selected_point_when_roi_mode_is_inactive(self) -> None:
        self._apply(PreviewInteractionCommand(action="select_source_point", source_point=(12, 34)))

        self.assertEqual(self.interaction_state.selected_point, (12, 34))
        self.assertEqual(self.interaction_state.last_status_message, "Point selected")

    def test_select_source_point_commits_roi_when_roi_mode_is_active(self) -> None:
        self.interaction_state.roi_mode = "rectangle"
        self.interaction_state.roi_anchor_point = (10, 20)

        outcome = self._apply(PreviewInteractionCommand(action="select_source_point", source_point=(40, 60)))

        self.assertIsNotNone(outcome.committed_roi)
        self.assertEqual(outcome.committed_roi.points, ((10, 20), (40, 60)))
        self.assertIsNone(self.interaction_state.roi_anchor_point)
        self.assertEqual(self.interaction_state.last_status_message, "ROI saved as rectangle")

    def test_select_source_point_prefers_crosshair_over_roi_entry_when_crosshair_is_visible(self) -> None:
        self.interaction_state.roi_mode = "rectangle"
        self.interaction_state.roi_anchor_point = (10, 20)
        self.interaction_state.crosshair_visible = True

        outcome = self._apply(PreviewInteractionCommand(action="select_source_point", source_point=(40, 60)))

        self.assertIsNone(outcome.committed_roi)
        self.assertEqual(self.interaction_state.selected_point, (40, 60))
        self.assertIsNone(self.interaction_state.roi_anchor_point)
        self.assertEqual(self.interaction_state.last_status_message, "Point selected")

    def test_toggle_crosshair_on_aborts_active_roi_draft(self) -> None:
        self.interaction_state.roi_mode = "rectangle"
        self.interaction_state.roi_anchor_point = (10, 20)

        self._apply(PreviewInteractionCommand(action="toggle_crosshair"))

        self.assertTrue(self.interaction_state.crosshair_visible)
        self.assertIsNone(self.interaction_state.roi_anchor_point)
        self.assertIsNone(self.interaction_state.roi_preview_point)
        self.assertEqual(self.interaction_state.last_status_message, "Crosshair shown")

    def test_toggle_roi_mode_off_clears_visible_roi(self) -> None:
        self.roi_state_service.set_active_roi(
            RoiDefinition(roi_id="roi-1", shape="rectangle", points=((1, 2), (3, 4)))
        )
        self.interaction_state.roi_mode = "rectangle"

        self._apply(PreviewInteractionCommand(action="toggle_roi_mode", roi_mode="rectangle"))

        self.assertIsNone(self.interaction_state.roi_mode)
        self.assertIsNone(self.roi_state_service.get_active_roi())
        self.assertIsNotNone(self.roi_state_service.get_roi("rectangle"))
        self.assertFalse(self.roi_state_service.get_roi("rectangle").enabled)
        self.assertEqual(self.interaction_state.last_status_message, "rectangle ROI hidden")

    def test_toggle_roi_mode_switches_shapes_exclusively(self) -> None:
        rectangle_roi = RoiDefinition(roi_id="roi-rect", shape="rectangle", points=((1, 2), (3, 4)))
        ellipse_roi = RoiDefinition(roi_id="roi-ellipse", shape="ellipse", points=((5, 6), (7, 8)))
        self.roi_state_service.set_active_roi(rectangle_roi)
        self.roi_state_service.set_active_roi(ellipse_roi)

        self._apply(PreviewInteractionCommand(action="toggle_roi_mode", roi_mode="rectangle"))

        active_roi = self.roi_state_service.get_active_roi()
        self.assertIsNotNone(active_roi)
        self.assertEqual(active_roi.shape, "rectangle")
        self.assertTrue(active_roi.enabled)
        self.assertFalse(self.roi_state_service.get_roi("ellipse").enabled)
        self.assertEqual(self.interaction_state.last_status_message, "rectangle ROI shown")

    def test_update_pan_returns_unhandled_without_active_pan_anchor(self) -> None:
        outcome = self._apply(PreviewInteractionCommand(action="update_pan", viewport_point=(20, 25)))

        self.assertFalse(outcome.handled)

    def test_wheel_zoom_outside_image_sets_status_message(self) -> None:
        self._apply(PreviewInteractionCommand(action="wheel_zoom", wheel_delta=120, source_point=None))

        self.assertEqual(self.interaction_state.last_status_message, "Wheel zoom ignored outside image")

    def test_zoom_command_uses_cursor_anchor_when_mapping_exists(self) -> None:
        mapping = self.geometry_service.build_viewport_mapping(
            frame_width=200,
            frame_height=200,
            viewport_width=100,
            viewport_height=100,
            display_scale=1.0,
        )
        self.interaction_state.last_cursor_viewport_point = (20, 30)

        self._apply(
            PreviewInteractionCommand(action="zoom_in"),
            last_viewport_mapping=mapping,
        )

        self.assertFalse(self.geometry_state.fit_to_window)
        self.assertEqual(self.geometry_state.manual_zoom_scale, 1.5)
        self.assertEqual(self.geometry_state.viewport_origin_scaled, (10, 15))


if __name__ == "__main__":
    unittest.main()
