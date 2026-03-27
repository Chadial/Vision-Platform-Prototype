import unittest
from unittest.mock import MagicMock

from tests import _path_setup
from vision_platform.imaging import OpenCvPreviewWindow


class OpenCvPreviewWindowTests(unittest.TestCase):
    def test_render_latest_frame_uses_adapter_when_frame_exists(self) -> None:
        preview_service = MagicMock()
        preview_service.get_latest_frame.return_value = MagicMock(width=320, height=240)
        adapter = MagicMock()
        adapter.to_image.return_value = "image"
        adapter.get_window_image_size.return_value = (640, 480)
        adapter.render_into_viewport.return_value = "viewport-image"
        adapter.is_window_visible.return_value = True

        window = OpenCvPreviewWindow(preview_service, window_name="Preview", frame_adapter=adapter)

        rendered = window.render_latest_frame(delay_ms=7)

        self.assertTrue(rendered)
        adapter.create_window.assert_called_once_with("Preview")
        adapter.render_into_viewport.assert_called_once()
        adapter.show_image.assert_called_once_with("Preview", "viewport-image", delay_ms=7)

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
        adapter.show_image.return_value = -1

        window = OpenCvPreviewWindow(preview_service, frame_adapter=adapter)

        pressed_key = window.render_latest_frame_and_get_key(delay_ms=1)

        self.assertEqual(pressed_key, 27)

    def test_overlay_text_appends_warning_only_when_provider_returns_text(self) -> None:
        preview_service = MagicMock()
        window = OpenCvPreviewWindow(
            preview_service,
            status_warning_provider=lambda: "Capability probe unavailable",
        )
        window._last_display_scale = 1.25

        overlay_text = window._build_overlay_text()

        self.assertIn("FIT 1.25x", overlay_text)
        self.assertIn("WARN: Capability probe unavailable", overlay_text)

    def test_overlay_text_stays_clean_when_warning_provider_returns_none(self) -> None:
        preview_service = MagicMock()
        window = OpenCvPreviewWindow(
            preview_service,
            status_warning_provider=lambda: None,
        )
        window._last_display_scale = 1.25

        overlay_text = window._build_overlay_text()

        self.assertEqual(overlay_text, "FIT 1.25x | i=in o=out f=fit q=quit")


if __name__ == "__main__":
    unittest.main()
