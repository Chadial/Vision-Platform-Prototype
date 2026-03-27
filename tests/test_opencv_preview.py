import unittest
from unittest.mock import MagicMock

from tests import _path_setup
from vision_platform.imaging import OpenCvPreviewWindow
from vision_platform.services.stream_service.roi_state_service import RoiStateService


class OpenCvPreviewWindowTests(unittest.TestCase):
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
        self.assertEqual(status_lines[1], "i=in o=out f=fit x=crosshair y=focus r=rect e=ellipse c=copy q=quit")

    def test_status_lines_stay_clean_when_warning_provider_returns_none(self) -> None:
        preview_service = MagicMock()
        window = OpenCvPreviewWindow(
            preview_service,
            status_warning_provider=lambda: None,
        )
        window._last_display_scale = 1.25

        status_lines = window._build_status_lines()

        self.assertEqual(status_lines, ["FIT 1.25x", "i=in o=out f=fit x=crosshair y=focus r=rect e=ellipse c=copy q=quit"])

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

        adapter.draw_crosshair.assert_called_once_with("viewport-image", 36, 4)
        self.assertEqual(window._last_status_message, "Crosshair hidden")

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
        self.assertEqual(hidden_lines, ["FIT 1.00x | Focus hidden", "i=in o=out f=fit x=crosshair y=focus r=rect e=ellipse c=copy q=quit"])

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
        self.assertEqual(cleared_lines, ["FIT 1.00x | ROI mode cleared", "i=in o=out f=fit x=crosshair y=focus r=rect e=ellipse c=copy q=quit"])

    def test_rectangle_roi_is_created_on_second_click_and_pushed_to_roi_state_service(self) -> None:
        preview_service = MagicMock()
        adapter = MagicMock()
        adapter.get_left_button_down_event.return_value = 1
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

    def test_active_rectangle_roi_is_drawn_in_viewport(self) -> None:
        preview_service = MagicMock()
        adapter = MagicMock()
        window = OpenCvPreviewWindow(preview_service, frame_adapter=adapter)
        window._active_roi = type("Roi", (), {"shape": "rectangle", "points": ((10, 20), (40, 60))})()
        window._last_viewport_mapping = window._build_viewport_mapping(
            frame_width=100,
            frame_height=100,
            viewport_width=100,
            viewport_height=100,
            display_scale=1.0,
        )

        window._draw_active_roi("viewport-image")

        adapter.draw_rectangle_outline.assert_called_once_with("viewport-image", 10, 20, 40, 60)

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


if __name__ == "__main__":
    unittest.main()
