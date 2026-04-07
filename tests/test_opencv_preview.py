import unittest
from unittest.mock import MagicMock

from tests import _path_setup
from camera_app.imaging import OpenCvPreviewWindow as LegacyOpenCvPreviewWindow
from vision_platform.imaging import OpenCvPreviewWindow
from vision_platform.services.stream_service.roi_state_service import RoiStateService


class OpenCvPreviewWindowTests(unittest.TestCase):
    def test_legacy_camera_app_imaging_package_reexports_platform_preview_window(self) -> None:
        self.assertIs(LegacyOpenCvPreviewWindow, OpenCvPreviewWindow)

    def test_render_latest_frame_uses_adapter_when_frame_exists(self) -> None:
        preview_service = MagicMock()
        preview_service.get_latest_frame.return_value = MagicMock(width=320, height=240)
        adapter = MagicMock()
        adapter.to_image.return_value = "image"
        adapter.get_window_image_size.return_value = (640, 480)
        adapter.render_into_viewport.return_value = "viewport-image"
        adapter.append_status_band.return_value = "framed-image"
        adapter.is_window_visible.return_value = True

        window = OpenCvPreviewWindow(preview_service, window_name="Preview", frame_adapter=adapter)

        rendered = window.render_latest_frame(delay_ms=7)

        self.assertTrue(rendered)
        adapter.create_window.assert_called_once_with("Preview")
        adapter.set_mouse_callback.assert_called_once()
        adapter.render_into_viewport.assert_called_once()
        adapter.append_status_band.assert_called_once()
        adapter.show_image.assert_called_once_with("Preview", "framed-image", delay_ms=7)

    def test_render_latest_frame_returns_false_without_frame(self) -> None:
        preview_service = MagicMock()
        preview_service.get_latest_frame.return_value = None
        adapter = MagicMock()

        window = OpenCvPreviewWindow(preview_service, frame_adapter=adapter)

        rendered = window.render_latest_frame()

        self.assertFalse(rendered)
        adapter.show_image.assert_not_called()

    def test_letter_shortcuts_change_zoom_mode(self) -> None:
        preview_service = MagicMock()
        preview_service.get_latest_frame.return_value = MagicMock(width=100, height=100)
        adapter = MagicMock()
        adapter.to_image.return_value = "image"
        adapter.get_window_image_size.return_value = (100, 100)
        adapter.render_into_viewport.return_value = "viewport-image"
        adapter.append_status_band.return_value = "framed-image"
        adapter.is_window_visible.return_value = True
        adapter.show_image.side_effect = [ord("i"), ord("o"), ord("f")]

        window = OpenCvPreviewWindow(preview_service, frame_adapter=adapter)

        window.render_latest_frame(delay_ms=1)
        zoomed_in = window.manual_zoom_scale
        self.assertFalse(window.is_fit_to_window_enabled)

        window.render_latest_frame(delay_ms=1)
        zoomed_out = window.manual_zoom_scale
        self.assertFalse(window.is_fit_to_window_enabled)

        window.render_latest_frame(delay_ms=1)

        self.assertIsNotNone(zoomed_in)
        self.assertIsNotNone(zoomed_out)
        self.assertGreater(zoomed_in, zoomed_out)
        self.assertTrue(window.is_fit_to_window_enabled)

    def test_render_returns_escape_when_window_was_closed(self) -> None:
        preview_service = MagicMock()
        preview_service.get_latest_frame.return_value = MagicMock(width=100, height=100)
        adapter = MagicMock()
        adapter.is_window_visible.side_effect = [True, False]
        adapter.to_image.return_value = "image"
        adapter.get_window_image_size.return_value = (100, 100)
        adapter.render_into_viewport.return_value = "viewport-image"
        adapter.append_status_band.return_value = "framed-image"
        adapter.show_image.return_value = -1

        window = OpenCvPreviewWindow(preview_service, frame_adapter=adapter)

        pressed_key = window.render_latest_frame_and_get_key(delay_ms=1)

        self.assertEqual(pressed_key, 27)

    def test_status_lines_include_warning_only_when_provider_returns_text(self) -> None:
        preview_service = MagicMock()
        window = OpenCvPreviewWindow(
            preview_service,
            status_warning_provider=lambda: "Capability probe unavailable",
        )
        window._last_display_scale = 1.25

        status_lines = window._build_status_lines()

        self.assertEqual(len(status_lines), 2)
        self.assertIn("FIT 1.25x", status_lines[0])
        self.assertIn("WARN: Capability probe unavailable", status_lines[0])
        self.assertEqual(status_lines[1], "i=in o=out f=fit x=crosshair r=rect e=ellipse wheel=zoom mdrag=pan c=copy q=quit")

    def test_status_lines_stay_clean_when_warning_provider_returns_none(self) -> None:
        preview_service = MagicMock()
        window = OpenCvPreviewWindow(
            preview_service,
            status_warning_provider=lambda: None,
        )
        window._last_display_scale = 1.25

        status_lines = window._build_status_lines()

        self.assertEqual(status_lines, ["FIT 1.25x", "i=in o=out f=fit x=crosshair r=rect e=ellipse wheel=zoom mdrag=pan c=copy q=quit"])

    def test_status_lines_include_fps_when_multiple_renders_were_recorded(self) -> None:
        preview_service = MagicMock()
        time_values = iter([10.0, 10.1, 10.2])
        window = OpenCvPreviewWindow(
            preview_service,
            time_provider=lambda: next(time_values),
        )
        window._last_display_scale = 1.0

        window._record_render_timestamp()
        window._record_render_timestamp()
        window._record_render_timestamp()
        status_lines = window._build_status_lines()

        self.assertIn("FIT 1.00x", status_lines[0])
        self.assertIn("FPS 10.0", status_lines[0])

    def test_status_lines_include_viewport_origin_in_zoom_mode(self) -> None:
        preview_service = MagicMock()
        window = OpenCvPreviewWindow(preview_service)
        window._fit_to_window = False
        window._manual_zoom_scale = 2.0
        window._last_display_scale = 2.0
        window._viewport_origin_scaled = (40, 50)

        status_lines = window._build_status_lines()

        self.assertIn("ZOOM 2.00x", status_lines[0])
        self.assertIn("view=40,50", status_lines[0])

    def test_build_status_model_exposes_overlay_and_focus_state_before_formatting(self) -> None:
        preview_service = MagicMock()
        focus_state = MagicMock()
        focus_state.result.is_valid = True
        focus_state.result.metric_name = "laplace"
        focus_state.result.score = 12.34
        window = OpenCvPreviewWindow(
            preview_service,
            focus_state_provider=lambda: focus_state,
        )
        window._fit_to_window = False
        window._manual_zoom_scale = 2.0
        window._last_display_scale = 2.0
        window._viewport_origin_scaled = (40, 50)
        window._selected_point = (20, 10)
        window._last_status_message = "Copied x=20, y=10"
        window._roi_mode = "rectangle"
        window._roi_anchor_point = (10, 20)
        window._roi_preview_point = (40, 60)

        status_model = window._build_status_model()

        self.assertEqual([entry.value for entry in status_model.primary_line.entries[:4]], ["ZOOM 2.00x", "view=40,50", "x=20, y=10", "Copied x=20, y=10"])
        self.assertEqual(status_model.roi_status.state, "anchor_pending")
        self.assertEqual(status_model.focus_status.state, "valid")
        self.assertEqual(status_model.focus_status.metric_name, "laplace")

    def test_render_uses_window_height_minus_status_band_for_image_viewport(self) -> None:
        preview_service = MagicMock()
        preview_service.get_latest_frame.return_value = MagicMock(width=320, height=240)
        adapter = MagicMock()
        adapter.to_image.return_value = "image"
        adapter.get_window_image_size.return_value = (640, 480)
        adapter.render_into_viewport.return_value = "viewport-image"
        adapter.append_status_band.return_value = "framed-image"
        adapter.is_window_visible.return_value = True
        window = OpenCvPreviewWindow(preview_service, frame_adapter=adapter)
        window._last_status_message = "Copied x=20, y=10"

        window.render_latest_frame(delay_ms=1)

        _, kwargs = adapter.render_into_viewport.call_args
        self.assertEqual(kwargs["viewport_width"], 640)
        self.assertEqual(kwargs["viewport_height"], 416)
        self.assertEqual(kwargs["source_offset_x"], 0)
        self.assertEqual(kwargs["source_offset_y"], 0)

    def test_viewport_outline_is_drawn_when_padding_is_visible(self) -> None:
        preview_service = MagicMock()
        adapter = MagicMock()
        window = OpenCvPreviewWindow(preview_service, frame_adapter=adapter)
        window._last_viewport_mapping = window._build_viewport_mapping(
            frame_width=100,
            frame_height=50,
            viewport_width=200,
            viewport_height=100,
            display_scale=1.0,
        )

        window._draw_viewport_outline_if_needed("viewport-image")

        adapter.draw_viewport_outline.assert_called_once_with("viewport-image", 0, 0, 99, 49)

    def test_viewport_outline_is_not_drawn_when_image_fills_viewport(self) -> None:
        preview_service = MagicMock()
        adapter = MagicMock()
        window = OpenCvPreviewWindow(preview_service, frame_adapter=adapter)
        window._last_viewport_mapping = window._build_viewport_mapping(
            frame_width=100,
            frame_height=100,
            viewport_width=100,
            viewport_height=100,
            display_scale=1.0,
        )

        window._draw_viewport_outline_if_needed("viewport-image")

        adapter.draw_viewport_outline.assert_not_called()

    def test_x_shortcut_toggles_crosshair_visibility(self) -> None:
        preview_service = MagicMock()
        preview_service.get_latest_frame.return_value = MagicMock(width=100, height=100)
        adapter = MagicMock()
        adapter.to_image.return_value = "image"
        adapter.get_window_image_size.return_value = (100, 100)
        adapter.render_into_viewport.return_value = "viewport-image"
        adapter.append_status_band.return_value = "framed-image"
        adapter.is_window_visible.return_value = True
        adapter.show_image.side_effect = [ord("x"), -1]

        window = OpenCvPreviewWindow(preview_service, frame_adapter=adapter)
        window._selected_point = (10, 10)

        window.render_latest_frame(delay_ms=1)
        window.render_latest_frame(delay_ms=1)

        adapter.draw_crosshair.assert_called_once_with("viewport-image", 4, 4)
        self.assertEqual(window._last_status_message, "Crosshair hidden")

    def test_zoom_in_anchors_to_last_cursor_position(self) -> None:
        preview_service = MagicMock()
        window = OpenCvPreviewWindow(preview_service)
        window._last_display_scale = 1.0
        window._last_viewport_mapping = window._build_viewport_mapping(
            frame_width=200,
            frame_height=200,
            viewport_width=100,
            viewport_height=100,
            display_scale=1.0,
        )
        window._last_cursor_viewport_point = (20, 30)

        window.zoom_in()

        self.assertEqual(window.manual_zoom_scale, 1.5)
        self.assertEqual(window._viewport_origin_scaled, (10, 15))

    def test_y_shortcut_hides_focus_status_line(self) -> None:
        preview_service = MagicMock()
        focus_state = MagicMock()
        focus_state.result.is_valid = True
        focus_state.result.metric_name = "laplace"
        focus_state.result.score = 12.34
        window = OpenCvPreviewWindow(
            preview_service,
            focus_state_provider=lambda: focus_state,
        )
        window._last_display_scale = 1.0

        visible_lines = window._build_status_lines()
        window._handle_shortcuts(ord("y"))
        hidden_lines = window._build_status_lines()

        self.assertIn("Focus: laplace=12.34", visible_lines)
        self.assertEqual(hidden_lines, ["FIT 1.00x | Focus hidden", "i=in o=out f=fit x=crosshair y=focus r=rect e=ellipse wheel=zoom mdrag=pan c=copy q=quit"])

    def test_r_and_e_shortcuts_toggle_roi_entry_modes(self) -> None:
        preview_service = MagicMock()
        window = OpenCvPreviewWindow(preview_service)
        window._last_display_scale = 1.0

        window._handle_shortcuts(ord("r"))
        rectangle_lines = window._build_status_lines()
        window._handle_shortcuts(ord("e"))
        ellipse_lines = window._build_status_lines()
        window._handle_shortcuts(ord("e"))
        cleared_lines = window._build_status_lines()

        self.assertIn("ROI mode set to rectangle", rectangle_lines[0])
        self.assertIn("ROI mode: rectangle", rectangle_lines[1])
        self.assertIn("ROI mode set to ellipse", ellipse_lines[0])
        self.assertIn("ROI mode: ellipse", ellipse_lines[1])
        self.assertEqual(cleared_lines, ["FIT 1.00x | ROI mode cleared", "i=in o=out f=fit x=crosshair r=rect e=ellipse wheel=zoom mdrag=pan c=copy q=quit"])

    def test_status_lines_include_snapshot_shortcut_only_when_snapshot_callback_exists(self) -> None:
        preview_service = MagicMock()
        window = OpenCvPreviewWindow(preview_service, snapshot_callback=MagicMock())
        window._last_display_scale = 1.0

        status_lines = window._build_status_lines()

        self.assertIn("+=snapshot", status_lines[1])

    def test_rectangle_roi_is_created_on_second_click_and_pushed_to_roi_state_service(self) -> None:
        preview_service = MagicMock()
        adapter = MagicMock()
        adapter.get_left_button_down_event.return_value = 1
        adapter.get_mouse_move_event.return_value = 0
        roi_state_service = RoiStateService()
        window = OpenCvPreviewWindow(
            preview_service,
            frame_adapter=adapter,
            roi_state_service=roi_state_service,
        )
        window._roi_mode = "rectangle"
        window._last_viewport_mapping = window._build_viewport_mapping(
            frame_width=100,
            frame_height=100,
            viewport_width=100,
            viewport_height=100,
            display_scale=1.0,
        )

        window._handle_mouse_event(event=1, x=10, y=20)
        window._handle_mouse_event(event=1, x=40, y=60)

        active_roi = roi_state_service.get_active_roi()
        self.assertIsNotNone(active_roi)
        self.assertEqual(active_roi.shape, "rectangle")
        self.assertEqual(active_roi.points, ((10, 20), (40, 60)))
        self.assertEqual(window._last_status_message, "ROI saved as rectangle")

    def test_roi_mouse_move_updates_preview_point_after_anchor(self) -> None:
        preview_service = MagicMock()
        adapter = MagicMock()
        adapter.get_left_button_down_event.return_value = 1
        adapter.get_mouse_move_event.return_value = 0
        window = OpenCvPreviewWindow(preview_service, frame_adapter=adapter)
        window._roi_mode = "rectangle"
        window._last_viewport_mapping = window._build_viewport_mapping(
            frame_width=100,
            frame_height=100,
            viewport_width=100,
            viewport_height=100,
            display_scale=1.0,
        )

        window._handle_mouse_event(event=1, x=10, y=20)
        window._handle_mouse_event(event=0, x=40, y=60)

        self.assertEqual(window._roi_preview_point, (40, 60))
        self.assertIn("preview=x=40, y=60", window._build_status_lines()[1])

    def test_active_rectangle_roi_is_drawn_in_viewport(self) -> None:
        preview_service = MagicMock()
        adapter = MagicMock()
        window = OpenCvPreviewWindow(preview_service, frame_adapter=adapter)
        window._fallback_active_roi = type("Roi", (), {"shape": "rectangle", "points": ((10, 20), (40, 60))})()
        window._last_viewport_mapping = window._build_viewport_mapping(
            frame_width=100,
            frame_height=100,
            viewport_width=100,
            viewport_height=100,
            display_scale=1.0,
        )

        window._draw_roi("viewport-image")

        adapter.draw_rectangle_outline.assert_called_once_with("viewport-image", 10, 20, 40, 60)

    def test_status_lines_reflect_committed_roi_from_state_service(self) -> None:
        preview_service = MagicMock()
        roi_state_service = RoiStateService()
        roi_state_service.set_active_roi(
            type("Roi", (), {"shape": "ellipse", "points": ((10, 20), (40, 60))})()
        )
        window = OpenCvPreviewWindow(preview_service, roi_state_service=roi_state_service)
        window._last_display_scale = 1.0

        status_lines = window._build_status_lines()

        self.assertEqual(status_lines[1], "ROI active: ellipse")

    def test_active_roi_from_state_service_is_drawn_in_viewport(self) -> None:
        preview_service = MagicMock()
        adapter = MagicMock()
        roi_state_service = RoiStateService()
        roi_state_service.set_active_roi(
            type("Roi", (), {"shape": "rectangle", "points": ((10, 20), (40, 60))})()
        )
        window = OpenCvPreviewWindow(
            preview_service,
            frame_adapter=adapter,
            roi_state_service=roi_state_service,
        )
        window._last_viewport_mapping = window._build_viewport_mapping(
            frame_width=100,
            frame_height=100,
            viewport_width=100,
            viewport_height=100,
            display_scale=1.0,
        )

        window._draw_roi("viewport-image")

        adapter.draw_rectangle_outline.assert_called_once_with("viewport-image", 10, 20, 40, 60)

    def test_draft_ellipse_roi_is_drawn_in_viewport(self) -> None:
        preview_service = MagicMock()
        adapter = MagicMock()
        window = OpenCvPreviewWindow(preview_service, frame_adapter=adapter)
        window._roi_mode = "ellipse"
        window._roi_anchor_point = (50, 50)
        window._roi_preview_point = (70, 80)
        window._last_viewport_mapping = window._build_viewport_mapping(
            frame_width=100,
            frame_height=100,
            viewport_width=100,
            viewport_height=100,
            display_scale=1.0,
        )

        window._draw_roi("viewport-image")

        adapter.draw_ellipse_outline.assert_called_once_with("viewport-image", 50, 50, 20, 30)

    def test_mouse_click_selects_source_point_and_copy_uses_formatted_coordinates(self) -> None:
        preview_service = MagicMock()
        copy_callback = MagicMock()
        adapter = MagicMock()
        adapter.get_left_button_down_event.return_value = 1
        window = OpenCvPreviewWindow(
            preview_service,
            frame_adapter=adapter,
            clipboard_copy_callback=copy_callback,
        )
        window._last_viewport_mapping = window._build_viewport_mapping(
            frame_width=100,
            frame_height=50,
            viewport_width=200,
            viewport_height=100,
            display_scale=2.0,
        )

        window._handle_mouse_event(event=1, x=40, y=20)
        window._handle_shortcuts(ord("c"))

        copy_callback.assert_called_once_with("x=20, y=10")
        self.assertEqual(window._selected_point, (20, 10))
        self.assertEqual(window._last_status_message, "Copied x=20, y=10")

    def test_copy_without_selection_sets_status_message(self) -> None:
        preview_service = MagicMock()
        window = OpenCvPreviewWindow(preview_service, clipboard_copy_callback=MagicMock())

        window._handle_shortcuts(ord("c"))

        self.assertEqual(window._last_status_message, "No point selected")

    def test_plus_shortcut_uses_snapshot_callback(self) -> None:
        preview_service = MagicMock()
        snapshot_callback = MagicMock()
        snapshot_callback.return_value = type("SavedPath", (), {"name": "preview_snapshot_000000.png"})()
        window = OpenCvPreviewWindow(preview_service, snapshot_callback=snapshot_callback)

        window._handle_shortcuts(ord("+"))

        snapshot_callback.assert_called_once_with()
        self.assertEqual(window._last_status_message, "Snapshot saved: preview_snapshot_000000.png")

    def test_y_shortcut_reports_unavailable_without_focus_provider(self) -> None:
        preview_service = MagicMock()
        window = OpenCvPreviewWindow(preview_service)

        window._handle_shortcuts(ord("y"))

        self.assertEqual(window._last_status_message, "Focus display unavailable")

    def test_mouse_wheel_zoom_in_anchors_to_cursor_position(self) -> None:
        preview_service = MagicMock()
        adapter = MagicMock()
        adapter.get_left_button_down_event.return_value = 1
        adapter.get_mouse_move_event.return_value = 0
        adapter.get_mouse_wheel_event.return_value = 10
        adapter.get_mouse_wheel_delta.return_value = 120
        window = OpenCvPreviewWindow(preview_service, frame_adapter=adapter)
        window._last_display_scale = 1.0
        window._last_viewport_mapping = window._build_viewport_mapping(
            frame_width=200,
            frame_height=200,
            viewport_width=100,
            viewport_height=100,
            display_scale=1.0,
        )

        window._handle_mouse_event(event=10, x=20, y=30, flags=120)

        self.assertEqual(window.manual_zoom_scale, 1.5)
        self.assertEqual(window._viewport_origin_scaled, (10, 15))

    def test_mouse_wheel_zoom_outside_image_sets_status_message(self) -> None:
        preview_service = MagicMock()
        adapter = MagicMock()
        adapter.get_left_button_down_event.return_value = 1
        adapter.get_mouse_move_event.return_value = 0
        adapter.get_mouse_wheel_event.return_value = 10
        adapter.get_mouse_wheel_delta.return_value = 120
        window = OpenCvPreviewWindow(preview_service, frame_adapter=adapter)
        window._last_display_scale = 1.0
        window._last_viewport_mapping = window._build_viewport_mapping(
            frame_width=100,
            frame_height=50,
            viewport_width=200,
            viewport_height=100,
            display_scale=1.0,
        )

        window._handle_mouse_event(event=10, x=150, y=20, flags=120)

        self.assertEqual(window._last_status_message, "Wheel zoom ignored outside image")

    def test_middle_drag_updates_viewport_origin_in_zoom_mode(self) -> None:
        preview_service = MagicMock()
        adapter = MagicMock()
        adapter.get_left_button_down_event.return_value = 1
        adapter.get_middle_button_down_event.return_value = 2
        adapter.get_middle_button_up_event.return_value = 3
        adapter.get_mouse_move_event.return_value = 0
        adapter.get_mouse_wheel_event.return_value = 10
        window = OpenCvPreviewWindow(preview_service, frame_adapter=adapter)
        window._fit_to_window = False
        window._manual_zoom_scale = 2.0
        window._viewport_origin_scaled = (40, 50)

        window._handle_mouse_event(event=2, x=30, y=40)
        window._handle_mouse_event(event=0, x=20, y=25)
        window._handle_mouse_event(event=3, x=20, y=25)

        self.assertEqual(window._viewport_origin_scaled, (50, 65))
        self.assertEqual(window._last_status_message, "Pan complete")

    def test_middle_drag_in_fit_mode_reports_unavailable(self) -> None:
        preview_service = MagicMock()
        adapter = MagicMock()
        adapter.get_left_button_down_event.return_value = 1
        adapter.get_middle_button_down_event.return_value = 2
        adapter.get_middle_button_up_event.return_value = 3
        adapter.get_mouse_move_event.return_value = 0
        adapter.get_mouse_wheel_event.return_value = 10
        window = OpenCvPreviewWindow(preview_service, frame_adapter=adapter)

        window._handle_mouse_event(event=2, x=30, y=40)

        self.assertEqual(window._last_status_message, "Pan unavailable in fit mode")

    def test_enable_fit_to_window_clears_active_pan_state(self) -> None:
        preview_service = MagicMock()
        window = OpenCvPreviewWindow(preview_service)
        window._fit_to_window = False
        window._manual_zoom_scale = 2.0
        window._viewport_origin_scaled = (40, 50)
        window._pan_anchor_viewport_point = (30, 40)
        window._pan_anchor_origin_scaled = (40, 50)

        window.enable_fit_to_window()
        pan_updated = window._update_pan((20, 25))

        self.assertTrue(window.is_fit_to_window_enabled)
        self.assertIsNone(window.manual_zoom_scale)
        self.assertEqual(window._viewport_origin_scaled, (0, 0))
        self.assertIsNone(window._pan_anchor_viewport_point)
        self.assertIsNone(window._pan_anchor_origin_scaled)
        self.assertFalse(pan_updated)


if __name__ == "__main__":
    unittest.main()
