import unittest

from tests import _path_setup
from vision_platform.services.display_service import (
    DisplayGeometryService,
    PreviewInteractionCommand,
    PreviewInteractionService,
    PreviewInteractionState,
    ZoomPanState,
)


class PreviewInteractionServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.geometry_service = DisplayGeometryService()
        self.service = PreviewInteractionService(self.geometry_service)
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

        self.assertFalse(self.interaction_state.crosshair_visible)
        self.assertEqual(self.interaction_state.last_status_message, "Crosshair hidden")

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
