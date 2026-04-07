import unittest

from tests import _path_setup
from vision_platform.apps.local_shell import PreviewShellPresenter
from vision_platform.apps.local_shell.preview_shell_state import render_viewport_image
from vision_platform.models import CapturedFrame
from vision_platform.services.display_service import PreviewInteractionCommand


class WxPreviewShellTests(unittest.TestCase):
    def test_render_viewport_image_converts_mono8_to_rgb_bytes_for_wx(self) -> None:
        presenter = PreviewShellPresenter()
        frame = CapturedFrame(
            raw_frame=bytes(range(16)),
            width=4,
            height=4,
            pixel_format="Mono8",
        )
        view = presenter.build_view(frame, viewport_width=4, viewport_height=4)

        self.assertEqual(view.image.mime_family, "pgm")
        self.assertEqual(len(view.image.payload), 16)
        self.assertEqual(len(view.image.to_rgb_bytes()), 48)

    def test_presenter_reuses_shared_interaction_state_for_zoom_and_roi(self) -> None:
        presenter = PreviewShellPresenter()
        frame = CapturedFrame(
            raw_frame=bytes((x + y) % 256 for y in range(8) for x in range(8)),
            width=8,
            height=8,
            pixel_format="Mono8",
        )

        presenter.build_view(frame, viewport_width=4, viewport_height=4)
        presenter.apply_command(PreviewInteractionCommand(action="zoom_in"))
        presenter.apply_command(PreviewInteractionCommand(action="toggle_roi_mode", roi_mode="rectangle"))
        presenter.handle_canvas_click(1, 1)
        presenter.handle_pointer_move(3, 3)
        presenter.handle_canvas_click(3, 3)
        view = presenter.build_view(frame, viewport_width=4, viewport_height=4)

        self.assertFalse(presenter.state.geometry_state.fit_to_window)
        self.assertIn("ZOOM", view.status_lines[0])
        self.assertIn("ROI active: rectangle", view.status_lines[1])

    def test_wx_shell_module_import_path_stays_available(self) -> None:
        from vision_platform.apps.local_shell import run_wx_preview_shell

        self.assertTrue(callable(run_wx_preview_shell))


if __name__ == "__main__":
    unittest.main()
