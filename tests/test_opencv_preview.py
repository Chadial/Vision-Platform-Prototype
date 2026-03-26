import unittest
from unittest.mock import MagicMock

from tests import _path_setup
from vision_platform.imaging import OpenCvPreviewWindow


class OpenCvPreviewWindowTests(unittest.TestCase):
    def test_render_latest_frame_uses_adapter_when_frame_exists(self) -> None:
        preview_service = MagicMock()
        preview_service.get_latest_frame.return_value = object()
        adapter = MagicMock()

        window = OpenCvPreviewWindow(preview_service, window_name="Preview", frame_adapter=adapter)

        rendered = window.render_latest_frame(delay_ms=7)

        self.assertTrue(rendered)
        adapter.show_frame.assert_called_once_with("Preview", preview_service.get_latest_frame.return_value, delay_ms=7)

    def test_render_latest_frame_returns_false_without_frame(self) -> None:
        preview_service = MagicMock()
        preview_service.get_latest_frame.return_value = None
        adapter = MagicMock()

        window = OpenCvPreviewWindow(preview_service, frame_adapter=adapter)

        rendered = window.render_latest_frame()

        self.assertFalse(rendered)
        adapter.show_frame.assert_not_called()


if __name__ == "__main__":
    unittest.main()
