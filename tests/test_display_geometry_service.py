import unittest

from tests import _path_setup
from vision_platform.services.display_service import DisplayGeometryService, ZoomPanState


class DisplayGeometryServiceTests(unittest.TestCase):
    def test_resolve_display_scale_uses_fit_mode_until_manual_zoom_is_active(self) -> None:
        service = DisplayGeometryService()
        state = ZoomPanState()

        fit_scale = service.resolve_display_scale(200, 100, 100, 100, state, min_zoom_scale=0.05)

        self.assertEqual(fit_scale, 0.5)

        state.fit_to_window = False
        state.manual_zoom_scale = 2.0

        manual_scale = service.resolve_display_scale(200, 100, 100, 100, state, min_zoom_scale=0.05)

        self.assertEqual(manual_scale, 2.0)

    def test_resolve_viewport_origin_clamps_zoomed_origin_to_scaled_bounds(self) -> None:
        service = DisplayGeometryService()
        state = ZoomPanState(fit_to_window=False, manual_zoom_scale=2.0, viewport_origin_scaled=(350, 20))

        origin = service.resolve_viewport_origin(200, 100, 100, 100, 2.0, state)

        self.assertEqual(origin, (300, 20))
        self.assertEqual(state.viewport_origin_scaled, (300, 20))

    def test_map_viewport_point_to_source_and_back_round_trips_visible_point(self) -> None:
        service = DisplayGeometryService()
        mapping = service.build_viewport_mapping(
            frame_width=200,
            frame_height=200,
            viewport_width=100,
            viewport_height=100,
            display_scale=2.0,
            src_x=40,
            src_y=60,
        )

        source_point = service.map_viewport_point_to_source(mapping, 20, 30)
        viewport_point = service.map_source_point_to_viewport(mapping, source_point)

        self.assertEqual(source_point, (30, 45))
        self.assertEqual(viewport_point, (20, 30))

    def test_build_cursor_anchored_origin_keeps_cursor_target_stable(self) -> None:
        service = DisplayGeometryService()
        mapping = service.build_viewport_mapping(
            frame_width=200,
            frame_height=200,
            viewport_width=100,
            viewport_height=100,
            display_scale=1.0,
            src_x=0,
            src_y=0,
        )

        origin = service.build_cursor_anchored_origin(mapping, (20, 30), 1.5)

        self.assertEqual(origin, (10, 15))


if __name__ == "__main__":
    unittest.main()
