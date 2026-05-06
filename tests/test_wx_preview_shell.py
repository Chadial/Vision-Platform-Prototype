import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from types import SimpleNamespace

from tests import _path_setup
from vision_platform.apps.local_shell import wx_preview_shell as wx_preview_shell_module
from vision_platform.apps.local_shell import PreviewShellPresenter
from vision_platform.apps.local_shell.wx_preview_shell import (
    WxLocalPreviewShell,
    _is_copy_shortcut,
    _normalize_wx_camera_pixel_format,
    _normalize_wx_recording_file_extension,
)
from vision_platform.apps.local_shell.startup import (
    LocalShellLaunchOptions,
    LocalShellStartupError,
    build_local_shell_session,
)
from vision_platform.integrations.camera import SimulatedCameraDriver
from vision_platform.libraries.common_models import FocusOverlayData, FocusPreviewState, FocusResult, RoiDefinition
from vision_platform.models import CapturedFrame
from vision_platform.services.display_service import PreviewInteractionCommand
from vision_platform.services.display_service import render_viewport_image


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

    def test_render_viewport_image_converts_mono10_to_rgb_bytes_for_wx(self) -> None:
        presenter = PreviewShellPresenter()
        values = (0, 256, 512, 1023)
        frame = CapturedFrame(
            raw_frame=b"".join(value.to_bytes(2, "little") for value in values),
            width=2,
            height=2,
            pixel_format="Mono10",
        )
        view = presenter.build_view(frame, viewport_width=2, viewport_height=2)

        self.assertEqual(view.image.mime_family, "pgm")
        self.assertEqual(list(view.image.payload), [0, 64, 128, 255])
        self.assertEqual(len(view.image.to_rgb_bytes()), 12)

    def test_render_viewport_image_converts_mono16_to_rgb_bytes_for_wx(self) -> None:
        presenter = PreviewShellPresenter()
        values = (0, 16384, 32768, 65535)
        frame = CapturedFrame(
            raw_frame=b"".join(value.to_bytes(2, "little") for value in values),
            width=4,
            height=1,
            pixel_format="Mono16",
        )
        view = presenter.build_view(frame, viewport_width=4, viewport_height=1)

        self.assertEqual(view.image.mime_family, "pgm")
        self.assertEqual(list(view.image.payload), [0, 64, 128, 255])
        self.assertEqual(len(view.image.to_rgb_bytes()), 12)

    def test_render_viewport_image_stretches_low_contrast_mono10_for_preview_visibility(self) -> None:
        presenter = PreviewShellPresenter()
        values = (40, 80, 160, 320)
        frame = CapturedFrame(
            raw_frame=b"".join(value.to_bytes(2, "little") for value in values),
            width=2,
            height=2,
            pixel_format="Mono10",
        )

        view = presenter.build_view(frame, viewport_width=2, viewport_height=2)

        self.assertEqual(list(view.image.payload), [0, 36, 109, 255])

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

    def test_presenter_includes_render_fps_in_primary_status_line(self) -> None:
        presenter = PreviewShellPresenter()
        frame = CapturedFrame(
            raw_frame=bytes(range(16)),
            width=4,
            height=4,
            pixel_format="Mono8",
        )

        view = presenter.build_view(frame, viewport_width=4, viewport_height=4, fps=24.0)

        self.assertIn("FPS 24.0", view.status_lines[0])

    def test_presenter_formats_focus_status_and_shortcut_hint_when_focus_state_is_available(self) -> None:
        presenter = PreviewShellPresenter()
        frame = CapturedFrame(
            raw_frame=bytes(range(16)),
            width=4,
            height=4,
            pixel_format="Mono8",
        )
        focus_state = FocusPreviewState(
            result=FocusResult(method="laplace", score=12.5, is_valid=True),
            overlay=FocusOverlayData(
                score=12.5,
                metric_name="laplace",
                anchor_x=1.0,
                anchor_y=1.0,
                is_valid=True,
            ),
        )

        view = presenter.build_view(
            frame,
            viewport_width=4,
            viewport_height=4,
            focus_state=focus_state,
            has_focus_toggle=True,
        )

        self.assertIn("Focus: laplace=1.250e+01", view.status_lines)
        self.assertEqual(view.overlay_model.focus_anchor_point, (1, 1))
        self.assertEqual(view.overlay_model.focus_label, "Focus 1.250e+01")
        self.assertIn("y=focus", view.status_lines[-1])

    def test_presenter_builds_waiting_focus_overlay_at_image_center_when_no_focus_state_exists(self) -> None:
        presenter = PreviewShellPresenter()
        frame = CapturedFrame(
            raw_frame=bytes(range(64)),
            width=8,
            height=8,
            pixel_format="Mono8",
        )

        view = presenter.build_view(
            frame,
            viewport_width=8,
            viewport_height=8,
            focus_state=None,
            has_focus_toggle=True,
        )

        self.assertEqual(view.overlay_model.focus_anchor_point, (4, 4))
        self.assertEqual(view.overlay_model.focus_label, "Focus...")

    def test_presenter_uses_cursor_position_for_crosshair_before_point_selection(self) -> None:
        presenter = PreviewShellPresenter()
        frame = CapturedFrame(
            raw_frame=bytes(range(64)),
            width=8,
            height=8,
            pixel_format="Mono8",
        )

        presenter.build_view(frame, viewport_width=8, viewport_height=8)
        presenter.apply_command(PreviewInteractionCommand(action="toggle_crosshair"))
        presenter.handle_pointer_move(4, 5)
        view = presenter.build_view(frame, viewport_width=8, viewport_height=8)

        self.assertEqual(view.overlay_model.crosshair_point, (4, 5))

    def test_presenter_builds_visible_roi_anchor_handles_when_cursor_is_over_active_roi(self) -> None:
        presenter = PreviewShellPresenter()
        frame = CapturedFrame(
            raw_frame=bytes(range(64)),
            width=8,
            height=8,
            pixel_format="Mono8",
        )

        presenter.build_view(frame, viewport_width=8, viewport_height=8)
        presenter.handle_canvas_click(2, 3)
        presenter.apply_command(PreviewInteractionCommand(action="toggle_roi_mode", roi_mode="rectangle"))
        presenter.handle_canvas_click(1, 1)
        presenter.handle_pointer_move(6, 6)
        presenter.handle_canvas_click(6, 6)
        presenter.handle_pointer_move(3, 3)
        view = presenter.build_view(frame, viewport_width=8, viewport_height=8)

        anchor_ids = {handle.anchor_id for handle in view.overlay_model.anchor_handles}
        self.assertSetEqual(
            anchor_ids,
            {
                "roi_top_left",
                "roi_top_right",
                "roi_bottom_left",
                "roi_bottom_right",
                "roi_mid_top",
                "roi_mid_right",
                "roi_mid_bottom",
                "roi_mid_left",
            },
        )
        self.assertEqual(view.overlay_model.active_roi_emphasis, "hover")

    def test_presenter_hides_roi_anchor_handles_while_cursor_is_away_from_roi(self) -> None:
        presenter = PreviewShellPresenter()
        frame = CapturedFrame(
            raw_frame=bytes((index % 256 for index in range(32 * 32))),
            width=32,
            height=32,
            pixel_format="Mono8",
        )

        presenter.build_view(frame, viewport_width=32, viewport_height=32)
        presenter.apply_command(PreviewInteractionCommand(action="toggle_roi_mode", roi_mode="rectangle"))
        presenter.handle_canvas_click(4, 4)
        presenter.handle_pointer_move(20, 20)
        presenter.handle_canvas_click(20, 20)
        presenter.handle_pointer_move(31, 0)
        view = presenter.build_view(frame, viewport_width=32, viewport_height=32)

        self.assertEqual(view.overlay_model.anchor_handles, ())
        self.assertEqual(view.overlay_model.active_roi_emphasis, "normal")

    def test_presenter_drags_selected_point_without_visible_anchor_handle(self) -> None:
        presenter = PreviewShellPresenter()
        frame = CapturedFrame(
            raw_frame=bytes(range(64)),
            width=8,
            height=8,
            pixel_format="Mono8",
        )

        presenter.build_view(frame, viewport_width=8, viewport_height=8)
        presenter.handle_canvas_click(2, 3)
        presenter.handle_canvas_click(2, 3)
        presenter.handle_pointer_move(5, 6, left_button_down=True)
        presenter.handle_left_release(5, 6)

        self.assertEqual(presenter.state.interaction_state.selected_point, (5, 6))
        self.assertEqual(presenter.state.interaction_state.last_status_message, "Point moved")
        view = presenter.build_view(frame, viewport_width=8, viewport_height=8)
        self.assertEqual(view.overlay_model.anchor_handles, ())

    def test_presenter_locks_selected_point_drag_on_click_release_and_releases_on_second_click(self) -> None:
        presenter = PreviewShellPresenter()
        frame = CapturedFrame(
            raw_frame=bytes(range(64)),
            width=8,
            height=8,
            pixel_format="Mono8",
        )

        presenter.build_view(frame, viewport_width=8, viewport_height=8)
        presenter.handle_canvas_click(2, 3)
        presenter.handle_canvas_click(2, 3)
        presenter.handle_left_release(2, 3)

        self.assertEqual(presenter.state.interaction_state.active_anchor_drag_id, "selected_point")
        self.assertEqual(presenter.state.interaction_state.active_anchor_drag_mode, "locked")
        self.assertEqual(presenter.state.interaction_state.last_status_message, "Point drag locked")

        presenter.handle_pointer_move(6, 6)
        presenter.handle_canvas_click(6, 6)

        self.assertEqual(presenter.state.interaction_state.selected_point, (6, 6))
        self.assertIsNone(presenter.state.interaction_state.active_anchor_drag_id)
        self.assertIsNone(presenter.state.interaction_state.active_anchor_drag_mode)
        self.assertEqual(presenter.state.interaction_state.last_status_message, "Point moved")

    def test_presenter_drags_active_roi_corner(self) -> None:
        presenter = PreviewShellPresenter()
        frame = CapturedFrame(
            raw_frame=bytes(range(64)),
            width=8,
            height=8,
            pixel_format="Mono8",
        )

        presenter.build_view(frame, viewport_width=8, viewport_height=8)
        presenter.apply_command(PreviewInteractionCommand(action="toggle_roi_mode", roi_mode="rectangle"))
        presenter.handle_canvas_click(1, 1)
        presenter.handle_pointer_move(4, 4)
        presenter.handle_canvas_click(4, 4)
        presenter.handle_canvas_click(4, 4)
        presenter.handle_pointer_move(6, 7, left_button_down=True)
        presenter.handle_left_release(6, 7)
        view = presenter.build_view(frame, viewport_width=8, viewport_height=8)

        self.assertEqual(view.overlay_model.active_roi.points, ((1, 1), (6, 7)))
        self.assertEqual(presenter.state.interaction_state.last_status_message, "ROI updated")
        self.assertEqual(view.overlay_model.active_roi_emphasis, "hover")

    def test_presenter_drags_active_ellipse_corner_using_bounding_box_semantics(self) -> None:
        presenter = PreviewShellPresenter()
        frame = CapturedFrame(
            raw_frame=bytes(range(64)),
            width=8,
            height=8,
            pixel_format="Mono8",
        )

        presenter.build_view(frame, viewport_width=8, viewport_height=8)
        presenter.apply_command(PreviewInteractionCommand(action="toggle_roi_mode", roi_mode="ellipse"))
        presenter.handle_canvas_click(4, 4)
        presenter.handle_pointer_move(6, 5)
        presenter.handle_canvas_click(6, 5)
        presenter.handle_pointer_move(5, 4)
        presenter.handle_canvas_click(6, 5)
        presenter.handle_pointer_move(7, 6, left_button_down=True)
        presenter.handle_left_release(7, 6)
        view = presenter.build_view(frame, viewport_width=8, viewport_height=8)

        self.assertEqual(view.overlay_model.active_roi.shape, "ellipse")
        self.assertEqual(view.overlay_model.active_roi.points, ((2, 3), (7, 6)))

    def test_presenter_locks_roi_drag_on_click_release_and_releases_on_second_click(self) -> None:
        presenter = PreviewShellPresenter()
        frame = CapturedFrame(
            raw_frame=bytes(range(64)),
            width=8,
            height=8,
            pixel_format="Mono8",
        )

        presenter.build_view(frame, viewport_width=8, viewport_height=8)
        presenter.apply_command(PreviewInteractionCommand(action="toggle_roi_mode", roi_mode="rectangle"))
        presenter.handle_canvas_click(1, 1)
        presenter.handle_pointer_move(4, 4)
        presenter.handle_canvas_click(4, 4)
        presenter.handle_pointer_move(4, 4)
        presenter.handle_canvas_click(4, 4)
        presenter.handle_left_release(4, 4)

        self.assertEqual(presenter.state.interaction_state.active_anchor_drag_id, "roi_bottom_right")
        self.assertEqual(presenter.state.interaction_state.active_anchor_drag_mode, "locked")
        self.assertEqual(presenter.state.interaction_state.last_status_message, "ROI drag locked")

        presenter.handle_pointer_move(6, 7)
        presenter.handle_canvas_click(6, 7)

        view = presenter.build_view(frame, viewport_width=8, viewport_height=8)
        self.assertEqual(view.overlay_model.active_roi.points, ((1, 1), (6, 7)))
        self.assertIsNone(presenter.state.interaction_state.active_anchor_drag_id)
        self.assertIsNone(presenter.state.interaction_state.active_anchor_drag_mode)
        self.assertEqual(presenter.state.interaction_state.last_status_message, "ROI updated")

    def test_presenter_pans_roi_body_without_distortion(self) -> None:
        presenter = PreviewShellPresenter()
        frame = CapturedFrame(
            raw_frame=bytes((index % 256 for index in range(32 * 32))),
            width=32,
            height=32,
            pixel_format="Mono8",
        )

        presenter.build_view(frame, viewport_width=32, viewport_height=32)
        presenter.apply_command(PreviewInteractionCommand(action="toggle_roi_mode", roi_mode="rectangle"))
        presenter.handle_canvas_click(4, 4)
        presenter.handle_pointer_move(20, 20)
        presenter.handle_canvas_click(20, 20)

        presenter.handle_canvas_click(12, 12)
        presenter.handle_pointer_move(14, 15, left_button_down=True)
        presenter.handle_left_release(14, 15)

        view = presenter.build_view(frame, viewport_width=32, viewport_height=32)
        self.assertEqual(view.overlay_model.active_roi.points, ((6, 7), (22, 23)))
        self.assertEqual(presenter.state.interaction_state.last_status_message, "ROI updated")
        self.assertEqual(view.overlay_model.active_roi_emphasis, "hover")

    def test_presenter_pans_roi_body_with_shift_axis_lock(self) -> None:
        presenter = PreviewShellPresenter()
        frame = CapturedFrame(
            raw_frame=bytes((index % 256 for index in range(32 * 32))),
            width=32,
            height=32,
            pixel_format="Mono8",
        )

        presenter.build_view(frame, viewport_width=32, viewport_height=32)
        presenter.apply_command(PreviewInteractionCommand(action="toggle_roi_mode", roi_mode="rectangle"))
        presenter.handle_canvas_click(4, 4)
        presenter.handle_pointer_move(20, 20)
        presenter.handle_canvas_click(20, 20)

        presenter.handle_canvas_click(12, 12)
        presenter.handle_pointer_move(16, 13, left_button_down=True, shift_down=True)
        presenter.handle_left_release(16, 13, shift_down=True)

        view = presenter.build_view(frame, viewport_width=32, viewport_height=32)
        self.assertEqual(view.overlay_model.active_roi.points, ((8, 4), (24, 20)))

    def test_presenter_releases_shift_during_roi_body_drag_back_to_actual_position(self) -> None:
        presenter = PreviewShellPresenter()
        frame = CapturedFrame(
            raw_frame=bytes((index % 256 for index in range(32 * 32))),
            width=32,
            height=32,
            pixel_format="Mono8",
        )

        presenter.build_view(frame, viewport_width=32, viewport_height=32)
        presenter.apply_command(PreviewInteractionCommand(action="toggle_roi_mode", roi_mode="rectangle"))
        presenter.handle_canvas_click(4, 4)
        presenter.handle_pointer_move(20, 20)
        presenter.handle_canvas_click(20, 20)

        presenter.handle_canvas_click(12, 12)
        presenter.handle_pointer_move(14, 15, left_button_down=True)
        presenter.handle_pointer_move(16, 16, left_button_down=True, shift_down=True)
        presenter.handle_pointer_move(16, 16, left_button_down=True, shift_down=False)
        view = presenter.build_view(frame, viewport_width=32, viewport_height=32)

        self.assertEqual(view.overlay_model.active_roi.points, ((8, 8), (24, 24)))
        self.assertEqual(view.overlay_model.active_roi_emphasis, "drag")

    def test_presenter_locks_roi_body_drag_and_releases_on_second_click(self) -> None:
        presenter = PreviewShellPresenter()
        frame = CapturedFrame(
            raw_frame=bytes((index % 256 for index in range(32 * 32))),
            width=32,
            height=32,
            pixel_format="Mono8",
        )

        presenter.build_view(frame, viewport_width=32, viewport_height=32)
        presenter.apply_command(PreviewInteractionCommand(action="toggle_roi_mode", roi_mode="rectangle"))
        presenter.handle_canvas_click(4, 4)
        presenter.handle_pointer_move(20, 20)
        presenter.handle_canvas_click(20, 20)

        presenter.handle_canvas_click(12, 12)
        presenter.handle_left_release(12, 12)

        self.assertEqual(presenter.state.interaction_state.active_anchor_drag_id, "roi_body")
        self.assertEqual(presenter.state.interaction_state.active_anchor_drag_mode, "locked")
        self.assertEqual(presenter.state.interaction_state.last_status_message, "ROI drag locked")

        presenter.handle_pointer_move(14, 15)
        presenter.handle_canvas_click(14, 15)

        view = presenter.build_view(frame, viewport_width=32, viewport_height=32)
        self.assertEqual(view.overlay_model.active_roi.points, ((6, 7), (22, 23)))
        self.assertIsNone(presenter.state.interaction_state.active_anchor_drag_id)
        self.assertIsNone(presenter.state.interaction_state.active_anchor_drag_mode)

    def test_presenter_uses_effective_drag_bounds_for_small_roi_body_hover(self) -> None:
        presenter = PreviewShellPresenter()
        frame = CapturedFrame(
            raw_frame=bytes((index % 256 for index in range(32 * 32))),
            width=32,
            height=32,
            pixel_format="Mono8",
        )

        presenter.build_view(frame, viewport_width=32, viewport_height=32)
        presenter.apply_command(PreviewInteractionCommand(action="toggle_roi_mode", roi_mode="rectangle"))
        presenter.handle_canvas_click(10, 10)
        presenter.handle_pointer_move(12, 12)
        presenter.handle_canvas_click(12, 12)
        presenter.handle_pointer_move(14, 14)
        view = presenter.build_view(frame, viewport_width=32, viewport_height=32)

        self.assertEqual(view.overlay_model.active_roi.points, ((10, 10), (12, 12)))
        self.assertEqual(view.overlay_model.active_roi_emphasis, "hover")
        self.assertEqual(view.overlay_model.anchor_handles, ())

    def test_presenter_drags_rectangle_mid_side_handle_on_single_axis(self) -> None:
        presenter = PreviewShellPresenter()
        frame = CapturedFrame(
            raw_frame=bytes((index % 256 for index in range(32 * 32))),
            width=32,
            height=32,
            pixel_format="Mono8",
        )

        presenter.build_view(frame, viewport_width=32, viewport_height=32)
        presenter.apply_command(PreviewInteractionCommand(action="toggle_roi_mode", roi_mode="rectangle"))
        presenter.handle_canvas_click(4, 4)
        presenter.handle_pointer_move(20, 20)
        presenter.handle_canvas_click(20, 20)
        presenter.handle_pointer_move(12, 4)
        presenter.handle_canvas_click(12, 4)
        presenter.handle_pointer_move(12, 2, left_button_down=True)
        presenter.handle_left_release(12, 2)

        view = presenter.build_view(frame, viewport_width=32, viewport_height=32)
        self.assertEqual(view.overlay_model.active_roi.points, ((4, 2), (20, 20)))

    def test_presenter_cancel_active_roi_drag_restores_drag_start_geometry(self) -> None:
        presenter = PreviewShellPresenter()
        frame = CapturedFrame(
            raw_frame=bytes((index % 256 for index in range(32 * 32))),
            width=32,
            height=32,
            pixel_format="Mono8",
        )

        presenter.build_view(frame, viewport_width=32, viewport_height=32)
        presenter.apply_command(PreviewInteractionCommand(action="toggle_roi_mode", roi_mode="rectangle"))
        presenter.handle_canvas_click(4, 4)
        presenter.handle_pointer_move(20, 20)
        presenter.handle_canvas_click(20, 20)

        presenter.handle_canvas_click(12, 12)
        presenter.handle_pointer_move(14, 15, left_button_down=True)
        self.assertTrue(presenter.cancel_active_drag())

        view = presenter.build_view(frame, viewport_width=32, viewport_height=32)
        self.assertEqual(view.overlay_model.active_roi.points, ((4, 4), (20, 20)))
        self.assertEqual(presenter.state.interaction_state.last_status_message, "ROI drag canceled")

    def test_presenter_cancel_active_point_drag_restores_drag_start_point(self) -> None:
        presenter = PreviewShellPresenter()
        frame = CapturedFrame(
            raw_frame=bytes(range(64)),
            width=8,
            height=8,
            pixel_format="Mono8",
        )

        presenter.build_view(frame, viewport_width=8, viewport_height=8)
        presenter.handle_canvas_click(2, 3)
        presenter.handle_canvas_click(2, 3)
        presenter.handle_pointer_move(5, 6, left_button_down=True)

        self.assertTrue(presenter.cancel_active_drag())

        self.assertEqual(presenter.state.interaction_state.selected_point, (2, 3))
        self.assertEqual(presenter.state.interaction_state.last_status_message, "Point drag canceled")

    def test_wx_shell_module_import_path_stays_available(self) -> None:
        from vision_platform.apps.local_shell import run_wx_preview_shell

        self.assertTrue(callable(run_wx_preview_shell))

    def test_copy_shortcut_helper_accepts_ctrl_c_and_rejects_plain_c(self) -> None:
        self.assertTrue(_is_copy_shortcut(_StubKeyEvent(ord("C"), control_down=True)))
        self.assertFalse(_is_copy_shortcut(_StubKeyEvent(ord("C"), control_down=False)))

    def test_focus_summary_helper_formats_valid_focus_for_top_status_line(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        shell._focus_preview_service = object()
        shell._presenter = _StubPresenter(focus_status_visible=True)
        focus_state = FocusPreviewState(
            result=FocusResult(method="laplace", score=0.01234, is_valid=True),
            overlay=FocusOverlayData(
                score=0.01234,
                metric_name="laplace",
                anchor_x=1.0,
                anchor_y=1.0,
                is_valid=True,
            ),
        )

        summary = shell._build_focus_summary(focus_state)

        self.assertEqual(summary, "1.234e-02")

    def test_status_prefix_includes_camera_and_ui_fps(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        shell._session = SimpleNamespace(
            source="hardware",
            resolved_camera_id="DEV_123",
            configuration_profile_id="default",
        )
        shell._subsystem = SimpleNamespace(
            stream_service=SimpleNamespace(is_preview_running=True),
        )
        shell._ui_refresh_fps = 29.97

        status = SimpleNamespace(
            camera=SimpleNamespace(is_initialized=True, reported_acquisition_frame_rate=15.966),
            default_save_directory=Path("captures/wx_shell_snapshot"),
        )

        prefix = shell._build_status_prefix(status)

        self.assertIn("camera_fps=16.0", prefix)
        self.assertIn("ui_fps=30.0", prefix)

    def test_status_prefix_includes_recording_fps_when_recording_is_configured(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        shell._session = SimpleNamespace(
            source="hardware",
            resolved_camera_id="DEV_123",
            configuration_profile_id="default",
        )
        shell._subsystem = SimpleNamespace(
            stream_service=SimpleNamespace(is_preview_running=True),
        )
        shell._ui_refresh_fps = None
        shell._recording_target_frame_rate_value = 12.5

        status = SimpleNamespace(
            camera=SimpleNamespace(is_initialized=True, reported_acquisition_frame_rate=15.966),
            default_save_directory=Path("captures/wx_shell_snapshot"),
        )

        prefix = shell._build_status_prefix(status)

        self.assertIn("recording_fps=12.5", prefix)

    def test_status_prefix_includes_camera_configuration_summary(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        shell._session = SimpleNamespace(
            source="hardware",
            resolved_camera_id="DEV_123",
            configuration_profile_id="default",
        )
        shell._subsystem = SimpleNamespace(
            stream_service=SimpleNamespace(is_preview_running=True),
        )
        shell._ui_refresh_fps = None

        status = SimpleNamespace(
            camera=SimpleNamespace(is_initialized=True, reported_acquisition_frame_rate=15.966),
            default_save_directory=Path("captures/wx_shell_snapshot"),
            configuration=SimpleNamespace(
                exposure_time_us=1500.0,
                gain=3.0,
                pixel_format="Mono8",
                acquisition_frame_rate=12.5,
                roi_offset_x=10,
                roi_offset_y=20,
                roi_width=300,
                roi_height=200,
            ),
        )

        prefix = shell._build_status_prefix(status)

        self.assertTrue(any(entry.startswith("config=") for entry in prefix))
        self.assertIn("config=exp=1500us gain=3 fmt=Mono8 fps=12.5 roi=x=10,y=20,w=300,h=200", prefix)

    def test_status_prefix_falls_back_when_recording_fps_state_is_not_numeric(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        shell._session = SimpleNamespace(
            source="hardware",
            resolved_camera_id="DEV_123",
            configuration_profile_id="default",
        )
        shell._subsystem = SimpleNamespace(
            stream_service=SimpleNamespace(is_preview_running=True),
        )
        shell._ui_refresh_fps = None
        shell._recording_target_frame_rate_value = SimpleNamespace()

        status = SimpleNamespace(
            camera=SimpleNamespace(is_initialized=True, reported_acquisition_frame_rate=15.966),
            default_save_directory=Path("captures/wx_shell_snapshot"),
            recording=SimpleNamespace(is_recording=False),
        )

        prefix = shell._build_status_prefix(status)

        self.assertIn("recording_fps=cfg", prefix)

    def test_status_prefix_includes_last_recording_file_stem_when_available(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        shell._session = SimpleNamespace(
            source="hardware",
            resolved_camera_id="DEV_123",
            configuration_profile_id="default",
        )
        shell._subsystem = SimpleNamespace(
            stream_service=SimpleNamespace(is_preview_running=True),
        )
        shell._ui_refresh_fps = None
        shell._recording_last_file_stem = "delam_run"
        shell._recording_last_save_directory = Path("captures/delam")

        status = SimpleNamespace(
            camera=SimpleNamespace(is_initialized=True, reported_acquisition_frame_rate=15.966),
            default_save_directory=Path("captures/wx_shell_snapshot"),
            recording=SimpleNamespace(is_recording=False, active_file_stem=None),
        )

        prefix = shell._build_status_prefix(status)

        self.assertIn("recording_file=delam_run", prefix)
        self.assertIn(f"recording_save={Path('captures/delam')}", prefix)

    def test_status_prefix_includes_last_snapshot_file_and_save_directory_when_available(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        shell._session = SimpleNamespace(
            source="hardware",
            resolved_camera_id="DEV_123",
            configuration_profile_id="default",
        )
        shell._subsystem = SimpleNamespace(
            stream_service=SimpleNamespace(is_preview_running=True),
        )
        shell._ui_refresh_fps = None
        shell._snapshot_last_saved_path = Path("captures/geometry") / "geometry_000001.bmp"
        shell._snapshot_last_error = None

        status = SimpleNamespace(
            camera=SimpleNamespace(is_initialized=True, reported_acquisition_frame_rate=15.966),
            default_save_directory=Path("captures/wx_shell_snapshot"),
            recording=SimpleNamespace(is_recording=False, active_file_stem=None),
        )

        prefix = shell._build_status_prefix(status)

        self.assertIn("snapshot_file=geometry_000001.bmp", prefix)
        self.assertIn(f"snapshot_save={Path('captures/geometry')}", prefix)

    def test_status_prefix_marks_failed_snapshot_state_when_last_error_exists(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        shell._session = SimpleNamespace(
            source="hardware",
            resolved_camera_id="DEV_123",
            configuration_profile_id="default",
        )
        shell._subsystem = SimpleNamespace(
            stream_service=SimpleNamespace(is_preview_running=True),
        )
        shell._ui_refresh_fps = None
        shell._snapshot_last_saved_path = None
        shell._snapshot_last_error = "disk full"

        status = SimpleNamespace(
            camera=SimpleNamespace(is_initialized=True, reported_acquisition_frame_rate=15.966),
            default_save_directory=Path("captures/wx_shell_snapshot"),
            recording=SimpleNamespace(is_recording=False, active_file_stem=None),
        )

        prefix = shell._build_status_prefix(status)

        self.assertIn("snapshot_state=failed", prefix)

    def test_status_prefix_includes_setup_focus_and_roi_state_when_available(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        shell._session = SimpleNamespace(
            source="hardware",
            resolved_camera_id="DEV_123",
            configuration_profile_id="default",
        )
        shell._subsystem = SimpleNamespace(
            stream_service=SimpleNamespace(
                is_preview_running=True,
                get_roi_state_service=lambda: SimpleNamespace(
                    get_active_roi=lambda: RoiDefinition(
                        roi_id="setup-roi",
                        shape="rectangle",
                        points=((10, 20), (110, 70)),
                    )
                ),
            ),
        )
        shell._presenter = _StubPresenter(focus_status_visible=True)
        shell._focus_preview_service = object()
        shell._ui_refresh_fps = None
        shell._snapshot_last_saved_path = None
        shell._snapshot_last_error = None

        status = SimpleNamespace(
            camera=SimpleNamespace(is_initialized=True, reported_acquisition_frame_rate=15.966),
            default_save_directory=Path("captures/wx_shell_snapshot"),
            recording=SimpleNamespace(is_recording=False, active_file_stem=None),
            configuration=SimpleNamespace(
                exposure_time_us=1500.0,
                gain=3.0,
                pixel_format="Mono8",
                acquisition_frame_rate=12.5,
                roi_offset_x=10,
                roi_offset_y=20,
                roi_width=100,
                roi_height=50,
            ),
        )

        prefix = shell._build_status_prefix(status)

        self.assertIn("setup_focus=visible", prefix)
        self.assertIn("setup_roi=rectangle", prefix)

    def test_status_prefix_includes_host_stop_category_for_last_recording_stop(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        shell._session = SimpleNamespace(
            source="hardware",
            resolved_camera_id="DEV_123",
            configuration_profile_id="default",
        )
        shell._subsystem = SimpleNamespace(
            stream_service=SimpleNamespace(is_preview_running=True),
        )
        shell._ui_refresh_fps = None
        shell._recording_last_stop_reason = "external_cli"

        status = SimpleNamespace(
            camera=SimpleNamespace(is_initialized=True, reported_acquisition_frame_rate=15.966),
            default_save_directory=Path("captures/wx_shell_snapshot"),
            recording=SimpleNamespace(is_recording=False, active_file_stem=None),
        )

        prefix = shell._build_status_prefix(status)

        self.assertIn("recording_stop=host_stop", prefix)

    def test_status_prefix_includes_failure_source_when_failure_reflection_exists(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        shell._session = SimpleNamespace(
            source="hardware",
            resolved_camera_id="DEV_123",
            configuration_profile_id="default",
        )
        shell._subsystem = SimpleNamespace(
            stream_service=SimpleNamespace(is_preview_running=True),
        )
        shell._ui_refresh_fps = None
        shell._set_failure_reflection(
            source="setup",
            action="apply_configuration",
            message="camera rejected roi",
            external=True,
        )

        status = SimpleNamespace(
            camera=SimpleNamespace(is_initialized=True, reported_acquisition_frame_rate=15.966),
            default_save_directory=Path("captures/wx_shell_snapshot"),
            recording=SimpleNamespace(is_recording=False, active_file_stem=None),
        )

        prefix = shell._build_status_prefix(status)

        self.assertIn("failure=setup", prefix)

    def test_recording_summary_formats_bounded_and_unbounded_progress(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        status = SimpleNamespace(recording=SimpleNamespace(is_recording=True, frames_written=3))

        shell._recording_active_frame_limit = 10
        shell._recording_last_summary = None
        bounded_summary = shell._build_recording_summary(status)

        shell._recording_active_frame_limit = None
        unbounded_summary = shell._build_recording_summary(status)

        self.assertEqual(bounded_summary, "3/10")
        self.assertEqual(unbounded_summary, "3/n")

    def test_recording_summary_keeps_last_stopped_value_until_next_start(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        shell._recording_active_frame_limit = None
        shell._recording_last_summary = "17/n"
        status = SimpleNamespace(recording=SimpleNamespace(is_recording=False, frames_written=17))

        self.assertEqual(shell._build_recording_summary(status), "17/n")

    def test_recording_summary_promotes_auto_stopped_bounded_run_into_last_summary(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        shell._recording_active_frame_limit = 3
        shell._recording_last_summary = None
        status = SimpleNamespace(recording=SimpleNamespace(is_recording=False, frames_written=3))

        summary = shell._build_recording_summary(status)

        self.assertEqual(summary, "3/3")
        self.assertEqual(shell._recording_last_summary, "3/3")
        self.assertIsNone(shell._recording_active_frame_limit)
        self.assertEqual(shell._recording_last_stop_reason, "max_frames_reached")

    def test_apply_recording_settings_updates_internal_state_and_controls(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        shell._recording_max_frames = _StubTextControl("0")
        shell._recording_target_frame_rate_input = _StubTextControl("")

        shell._apply_recording_settings_values(
            file_stem="custom_run",
            file_extension=".bmp",
            max_frames="12",
            recording_fps="8.5",
        )

        self.assertEqual(shell._recording_file_stem, "custom_run")
        self.assertEqual(shell._recording_file_extension, ".bmp")
        self.assertEqual(shell._recording_max_frames.GetValue(), "12")
        self.assertEqual(shell._recording_target_frame_rate_input.GetValue(), "8.5")
        self.assertEqual(shell._recording_target_frame_rate_value, 8.5)

    def test_apply_recording_settings_rejects_invalid_extension(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        shell._recording_max_frames = _StubTextControl("0")
        shell._recording_target_frame_rate_input = _StubTextControl("")

        with self.assertRaises(ValueError):
            shell._apply_recording_settings_values(
                file_stem="custom_run",
                file_extension="bmp",
                max_frames="0",
                recording_fps="",
            )

    def test_normalize_wx_recording_file_extension_accepts_supported_values(self) -> None:
        self.assertEqual(_normalize_wx_recording_file_extension(".bmp"), ".bmp")
        self.assertEqual(_normalize_wx_recording_file_extension(".RAW"), ".raw")

    def test_normalize_wx_camera_pixel_format_accepts_unchanged_and_supported_values(self) -> None:
        self.assertIsNone(_normalize_wx_camera_pixel_format("<unchanged>"))
        self.assertEqual(_normalize_wx_camera_pixel_format("Mono8"), "Mono8")

    def test_normalize_wx_camera_pixel_format_rejects_unsupported_values(self) -> None:
        with self.assertRaises(ValueError):
            _normalize_wx_camera_pixel_format("Jpeg")

    def test_build_camera_settings_request_maps_camera_fields(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)

        request = shell._build_camera_settings_request(
            exposure_time_us="1500.5",
            gain="3.0",
            pixel_format="Mono10",
            acquisition_frame_rate="12.5",
            roi_offset_x="10",
            roi_offset_y="20",
            roi_width="300",
            roi_height="200",
        )

        self.assertEqual(request.exposure_time_us, 1500.5)
        self.assertEqual(request.gain, 3.0)
        self.assertEqual(request.pixel_format, "Mono10")
        self.assertEqual(request.acquisition_frame_rate, 12.5)
        self.assertEqual(request.roi_offset_x, 10)
        self.assertEqual(request.roi_offset_y, 20)
        self.assertEqual(request.roi_width, 300)
        self.assertEqual(request.roi_height, 200)

    def test_shortcut_reference_text_includes_camera_settings_and_recording_shortcuts(self) -> None:
        text = WxLocalPreviewShell._build_shortcut_reference_text()

        self.assertIn("Preview:", text)
        self.assertIn("Ctrl+1=zoom in", text)
        self.assertIn("Ctrl+2=zoom out", text)
        self.assertIn("Ctrl+3=fit", text)
        self.assertIn("Ctrl+Shift+C=camera settings", text)
        self.assertIn("Ctrl+Enter=start recording", text)
        self.assertIn("Ctrl+Shift+Enter=stop recording", text)
        self.assertNotIn("OpenCV", text)

    def test_camera_settings_menu_stays_enabled_independent_of_configuration_state(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        shell._menu_camera_settings = _StubMenuItem()
        shell._menu_snapshot = _StubMenuItem()
        shell._menu_start_recording = _StubMenuItem()
        shell._menu_stop_recording = _StubMenuItem()
        shell._menu_recording_settings = _StubMenuItem()
        shell._menu_set_save_directory = _StubMenuItem()
        shell._menu_zoom_in = _StubMenuItem()
        shell._menu_zoom_out = _StubMenuItem()
        shell._menu_fit = _StubMenuItem()
        shell._menu_crosshair = _StubMenuItem()
        shell._menu_focus = _StubMenuItem()
        shell._menu_rect_roi = _StubMenuItem()
        shell._menu_ellipse_roi = _StubMenuItem()
        shell._menu_copy_point = _StubMenuItem()
        shell._menu_cancel_drag = _StubMenuItem()
        shell._menu_shortcuts = _StubMenuItem()

        status = SimpleNamespace(
            can_save_snapshot=False,
            can_apply_configuration=False,
            can_start_recording=False,
            can_stop_recording=False,
        )

        shell._update_menu_state(status)

        self.assertTrue(shell._menu_camera_settings.enabled)

    def test_camera_settings_menu_populates_dialog_with_current_configuration_values(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        status = SimpleNamespace(
            configuration=SimpleNamespace(
                exposure_time_us=1500.0,
                gain=3.0,
                pixel_format="Mono8",
                acquisition_frame_rate=12.5,
                roi_offset_x=10,
                roi_offset_y=20,
                roi_width=300,
                roi_height=200,
            )
        )
        shell._get_status = lambda: status
        shell._build_camera_settings_request = lambda **kwargs: kwargs
        shell._camera_settings_service = wx_preview_shell_module.CameraSettingsService()
        shell._session = SimpleNamespace(
            configuration_profile_id="default",
            configuration_profile_camera_class="1800_u_1240m",
            subsystem=SimpleNamespace(command_controller=SimpleNamespace(apply_configuration=lambda _request: None))
        )
        shell._subsystem = SimpleNamespace(
            camera_service=SimpleNamespace(get_capability_profile=lambda: None),
        )
        shell._cached_status = None
        shell._last_status_refresh_time = 0.0
        shell._cached_focus_state = None
        shell._last_focus_refresh_time = 0.0
        shell._clear_failure_reflection_for_source = lambda _source: None
        shell._set_transient_status_message = lambda _message: None
        shell.request_refresh = lambda: None

        created_dialogs: list = []

        class _FakeDialog:
            def __init__(self, parent, **kwargs):
                created_dialogs.append(kwargs)

            def ShowModal(self):
                return 0

            def Destroy(self):
                pass

        with patch.object(wx_preview_shell_module, "_CameraSettingsDialog", _FakeDialog):
            shell._on_menu_camera_settings(None)

        self.assertEqual(len(created_dialogs), 1)
        self.assertEqual(created_dialogs[0]["exposure_time_us"], "1500")
        self.assertEqual(created_dialogs[0]["gain"], "3")
        self.assertEqual(created_dialogs[0]["pixel_format"], "Mono10")
        self.assertEqual(created_dialogs[0]["acquisition_frame_rate"], "12.5")
        self.assertEqual(created_dialogs[0]["roi_offset_x"], "0")
        self.assertEqual(created_dialogs[0]["roi_offset_y"], "0")
        self.assertEqual(created_dialogs[0]["roi_width"], "2000")
        self.assertEqual(created_dialogs[0]["roi_height"], "1500")

    def test_suppress_unchanged_camera_settings_keeps_only_changed_fields(self) -> None:
        current_configuration = SimpleNamespace(
            exposure_time_us=10031.291,
            gain=3.0,
            pixel_format="Mono10",
            acquisition_frame_rate=None,
            roi_offset_x=0,
            roi_offset_y=0,
            roi_width=2000,
            roi_height=1500,
        )
        request = wx_preview_shell_module.ApplyConfigurationRequest(
            exposure_time_us=10031.291,
            gain=4.0,
            pixel_format="Mono10",
            acquisition_frame_rate=None,
            roi_offset_x=0,
            roi_offset_y=0,
            roi_width=2000,
            roi_height=1500,
        )

        filtered = WxLocalPreviewShell._suppress_unchanged_camera_settings(request, current_configuration)

        self.assertIsNone(filtered.exposure_time_us)
        self.assertEqual(filtered.gain, 4.0)
        self.assertIsNone(filtered.pixel_format)
        self.assertIsNone(filtered.roi_width)
        self.assertIsNone(filtered.roi_height)

    def test_camera_settings_request_has_values_detects_empty_request(self) -> None:
        self.assertFalse(
            WxLocalPreviewShell._camera_settings_request_has_values(
                wx_preview_shell_module.ApplyConfigurationRequest()
            )
        )
        self.assertTrue(
            WxLocalPreviewShell._camera_settings_request_has_values(
                wx_preview_shell_module.ApplyConfigurationRequest(gain=3.0)
            )
        )

    def test_recording_settings_dialog_uses_choice_string_selection(self) -> None:
        dialog = SimpleNamespace(
            _file_stem=_StubTextControl("series"),
            _file_extension=_StubChoiceControl(".png"),
            _max_frames=_StubTextControl("12"),
            _recording_fps=_StubTextControl("8.5"),
        )

        values = {
            "file_stem": dialog._file_stem.GetValue(),
            "file_extension": dialog._file_extension.GetStringSelection(),
            "max_frames": dialog._max_frames.GetValue(),
            "recording_fps": dialog._recording_fps.GetValue(),
        }

        self.assertEqual(values["file_extension"], ".png")

    def test_camera_settings_dialog_uses_choice_string_selection(self) -> None:
        dialog = SimpleNamespace(
            _exposure_time_us=_StubTextControl("1500"),
            _gain=_StubTextControl("3"),
            _pixel_format=_StubChoiceControl("Mono8"),
            _acquisition_frame_rate=_StubTextControl("12.5"),
            _roi_offset_x=_StubTextControl("10"),
            _roi_offset_y=_StubTextControl("20"),
            _roi_width=_StubTextControl("300"),
            _roi_height=_StubTextControl("200"),
        )

        values = {
            "pixel_format": _normalize_wx_camera_pixel_format(dialog._pixel_format.GetStringSelection()) or "",
            "gain": dialog._gain.GetValue(),
        }

        self.assertEqual(values["pixel_format"], "Mono8")
        self.assertEqual(values["gain"], "3")

    def test_wx_shell_default_recording_extension_is_bmp(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        shell._recording_file_extension = ".bmp"

        self.assertEqual(shell._recording_file_extension, ".bmp")

    def test_normalize_wx_recording_file_extension_rejects_unsupported_values(self) -> None:
        with self.assertRaises(ValueError):
            _normalize_wx_recording_file_extension(".jpg")

    def test_start_recording_uses_configured_recording_file_stem_and_extension(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        started_requests: list = []

        def _start_recording(request):
            started_requests.append(request)
            return SimpleNamespace(status=SimpleNamespace(active_file_stem=request.file_stem))

        shell._recording_max_frames = _StubTextControl("0")
        shell._recording_target_frame_rate_input = _StubTextControl("")
        shell._recording_file_stem = "menu_stem"
        shell._recording_file_extension = ".bmp"
        shell._session = SimpleNamespace(
            resolved_camera_id="DEV_123",
            configuration_profile_id="default",
            configuration_profile_camera_class="1800_u_1240m",
            subsystem=SimpleNamespace(
                command_controller=SimpleNamespace(start_recording=_start_recording),
            ),
        )
        shell._get_recording_save_directory = lambda: Path("captures/wx_shell_snapshot")
        shell._set_transient_status_message = lambda _message: None
        shell.request_refresh = lambda: None

        shell._on_start_recording(None)

        self.assertEqual(len(started_requests), 1)
        self.assertEqual(started_requests[0].file_stem, "menu_stem")
        self.assertEqual(started_requests[0].file_extension, ".raw")

    def test_external_start_recording_uses_current_shell_recording_settings_when_overrides_are_omitted(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        started_requests: list = []
        transient_messages: list[str] = []

        def _start_recording(request):
            started_requests.append(request)
            return SimpleNamespace(status=SimpleNamespace(active_file_stem=request.file_stem))

        shell._recording_file_stem = "shell_run"
        shell._recording_file_extension = ".bmp"
        shell._recording_max_frames = _StubTextControl("24")
        shell._recording_target_frame_rate_input = _StubTextControl("8.5")
        shell._recording_target_frame_rate_value = None
        shell._recording_last_summary = "old"
        shell._cached_status = object()
        shell._last_status_refresh_time = 1.0
        shell._session = SimpleNamespace(
            resolved_camera_id="DEV_123",
            configuration_profile_id="default",
            configuration_profile_camera_class="1800_u_1240m",
            subsystem=SimpleNamespace(
                command_controller=SimpleNamespace(start_recording=_start_recording),
            ),
        )
        shell._get_recording_save_directory = lambda: Path("captures/wx_shell_snapshot")
        shell._set_transient_status_message = transient_messages.append

        result = shell._execute_live_command(
            SimpleNamespace(command_name="start_recording", payload={})
        )

        self.assertEqual(result["command"], "start_recording")
        self.assertEqual(len(started_requests), 1)
        self.assertEqual(started_requests[0].file_stem, "shell_run")
        self.assertEqual(started_requests[0].file_extension, ".raw")
        self.assertEqual(started_requests[0].max_frame_count, 24)
        self.assertEqual(started_requests[0].target_frame_rate, 8.5)
        self.assertEqual(shell._recording_active_frame_limit, 24)
        self.assertEqual(shell._recording_target_frame_rate_value, 8.5)
        self.assertIsNone(shell._recording_last_summary)
        self.assertIsNone(shell._cached_status)
        self.assertEqual(shell._last_status_refresh_time, 0.0)
        self.assertEqual(
            transient_messages[-1],
            f"External recording run started: shell_run -> {Path('captures/wx_shell_snapshot')}",
        )

    def test_external_start_recording_honors_explicit_host_overrides(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        started_requests: list = []

        def _start_recording(request):
            started_requests.append(request)
            return SimpleNamespace(status=SimpleNamespace(active_file_stem=request.file_stem))

        shell._recording_file_stem = "shell_run"
        shell._recording_file_extension = ".bmp"
        shell._recording_max_frames = _StubTextControl("24")
        shell._recording_target_frame_rate_input = _StubTextControl("8.5")
        shell._recording_target_frame_rate_value = None
        shell._recording_last_summary = None
        shell._cached_status = object()
        shell._last_status_refresh_time = 1.0
        shell._session = SimpleNamespace(
            resolved_camera_id="DEV_123",
            configuration_profile_id="default",
            configuration_profile_camera_class="1800_u_1240m",
            subsystem=SimpleNamespace(
                command_controller=SimpleNamespace(start_recording=_start_recording),
            ),
        )
        shell._get_recording_save_directory = lambda: Path("captures/wx_shell_snapshot")
        shell._set_transient_status_message = lambda _message: None

        shell._execute_live_command(
            SimpleNamespace(
                command_name="start_recording",
                payload={
                    "file_stem": "host_run",
                    "file_extension": ".raw",
                    "max_frame_count": None,
                    "target_frame_rate": 12.5,
                },
            )
        )

        self.assertEqual(len(started_requests), 1)
        self.assertEqual(started_requests[0].file_stem, "host_run")
        self.assertEqual(started_requests[0].file_extension, ".raw")
        self.assertIsNone(started_requests[0].max_frame_count)
        self.assertEqual(started_requests[0].target_frame_rate, 12.5)
        self.assertIsNone(shell._recording_active_frame_limit)
        self.assertEqual(shell._recording_target_frame_rate_value, 12.5)

    def test_external_save_snapshot_updates_snapshot_reflection_and_message(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        transient_messages: list[str] = []

        def _save_snapshot(request):
            return SimpleNamespace(saved_path=Path("captures/geometry") / f"{request.file_stem}{request.file_extension}")

        shell._cached_status = object()
        shell._last_status_refresh_time = 1.0
        shell._snapshot_last_saved_path = None
        shell._snapshot_last_error = None
        shell._cached_focus_state = None
        command_controller = SimpleNamespace(
            save_snapshot=_save_snapshot,
            get_status=lambda: SimpleNamespace(
                camera=SimpleNamespace(is_initialized=True, reported_acquisition_frame_rate=15.0),
                default_save_directory=Path("captures/geometry"),
                recording=SimpleNamespace(is_recording=False, frames_written=0, active_file_stem=None, save_directory=None, last_error=None),
            ),
        )
        shell._session = SimpleNamespace(
            resolved_camera_id="DEV_123",
            configuration_profile_id="default",
            configuration_profile_camera_class="1800_u_1240m",
            subsystem=SimpleNamespace(command_controller=command_controller),
            selected_save_directory=Path("captures/geometry"),
        )
        shell._subsystem = SimpleNamespace(
            command_controller=command_controller,
            stream_service=SimpleNamespace(get_roi_state_service=lambda: SimpleNamespace(get_active_roi=lambda: None)),
        )
        shell._focus_preview_service = None
        shell._presenter = _StubPresenter(focus_status_visible=False)
        shell._set_transient_status_message = transient_messages.append

        result = shell._execute_live_command(
            SimpleNamespace(
                command_name="save_snapshot",
                payload={"file_stem": "geometry_000001", "file_extension": ".bmp"},
            )
        )

        self.assertEqual(result["command"], "save_snapshot")
        self.assertEqual(result["reflection_kind"], "snapshot")
        self.assertEqual(result["reflection"]["phase"], "saved")
        self.assertEqual(result["reflection"]["file_name"], "geometry_000001.raw")
        self.assertEqual(shell._snapshot_last_saved_path, Path("captures/geometry/geometry_000001.raw"))
        self.assertIsNone(shell._snapshot_last_error)
        self.assertEqual(
            transient_messages[-1],
            f"External geometry snapshot saved: geometry_000001.raw -> {Path('captures/geometry')}",
        )

    def test_build_live_command_result_uses_save_directory_reflection_for_set_save_directory(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        shell._cached_focus_state = None
        shell._session = SimpleNamespace(
            selected_save_directory=Path("captures/new_run"),
        )
        shell._subsystem = SimpleNamespace(
            command_controller=SimpleNamespace(
                get_status=lambda: SimpleNamespace(
                    camera=SimpleNamespace(is_initialized=True, reported_acquisition_frame_rate=15.0),
                    default_save_directory=Path("captures/new_run"),
                    recording=SimpleNamespace(is_recording=False, frames_written=0, active_file_stem=None, save_directory=None, last_error=None),
                )
            )
        )
        shell._focus_preview_service = None
        shell._presenter = _StubPresenter(focus_status_visible=False)

        result = shell._build_live_command_result(
            command_name="set_save_directory",
            result=SimpleNamespace(selected_directory=Path("captures/new_run")),
        )

        self.assertEqual(result["reflection_kind"], "save_directory")
        self.assertEqual(
            result["reflection"],
            {
                "phase": "selected",
                "selected_directory": str(Path("captures/new_run")),
            },
        )
        self.assertIsNone(result["failure_reflection"])

    def test_build_live_command_result_carries_failure_reflection_when_present(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        shell._cached_focus_state = None
        shell._set_failure_reflection(
            source="snapshot",
            action="save_snapshot",
            message="disk full",
            external=True,
        )
        shell._session = SimpleNamespace(
            selected_save_directory=Path("captures/new_run"),
        )
        shell._subsystem = SimpleNamespace(
            command_controller=SimpleNamespace(
                get_status=lambda: SimpleNamespace(
                    camera=SimpleNamespace(is_initialized=True, reported_acquisition_frame_rate=15.0),
                    default_save_directory=Path("captures/new_run"),
                    recording=SimpleNamespace(
                        is_recording=False,
                        frames_written=0,
                        active_file_stem=None,
                        save_directory=None,
                        last_error=None,
                    ),
                )
            )
        )
        shell._focus_preview_service = None
        shell._presenter = _StubPresenter(focus_status_visible=False)

        result = shell._build_live_command_result(
            command_name="set_save_directory",
            result=SimpleNamespace(selected_directory=Path("captures/new_run")),
        )

        self.assertEqual(result["failure_reflection"]["source"], "snapshot")
        self.assertEqual(result["failure_reflection"]["action"], "save_snapshot")

    def test_execute_live_apply_configuration_failure_sets_setup_failure_reflection(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        transient_messages: list[str] = []

        def _apply_configuration(_request):
            raise RuntimeError("camera rejected roi")

        shell._session = SimpleNamespace(
            resolved_camera_id="DEV_123",
            configuration_profile_id="default",
            configuration_profile_camera_class="1800_u_1240m",
            subsystem=SimpleNamespace(
                command_controller=SimpleNamespace(apply_configuration=_apply_configuration),
            ),
        )
        shell._subsystem = shell._session.subsystem
        shell._set_transient_status_message = transient_messages.append

        with self.assertRaises(RuntimeError):
            shell._execute_live_command(
                SimpleNamespace(
                    command_name="apply_configuration",
                    payload={"gain": 5.0},
                )
            )

        failure_reflection = shell._build_failure_reflection()
        self.assertEqual(failure_reflection["source"], "setup")
        self.assertEqual(failure_reflection["action"], "apply_configuration")
        self.assertEqual(failure_reflection["message"], "camera rejected roi")
        self.assertTrue(failure_reflection["external"])
        self.assertEqual(transient_messages[-1], "External setup configuration failed: camera rejected roi")

    def test_build_snapshot_reflection_uses_failed_phase_when_last_error_exists(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        shell._snapshot_last_saved_path = Path("captures/geometry/geometry_000001.bmp")
        shell._snapshot_last_error = "disk full"

        reflection = shell._build_snapshot_reflection()

        self.assertEqual(reflection["phase"], "failed")
        self.assertEqual(reflection["file_name"], "geometry_000001.bmp")
        self.assertEqual(reflection["save_directory"], str(Path("captures/geometry")))
        self.assertEqual(reflection["last_error"], "disk full")

    def test_build_setup_reflection_exposes_focus_roi_and_configuration_state(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        shell._focus_preview_service = object()
        shell._presenter = _StubPresenter(focus_status_visible=True)
        shell._subsystem = SimpleNamespace(
            stream_service=SimpleNamespace(
                get_roi_state_service=lambda: SimpleNamespace(
                    get_active_roi=lambda: RoiDefinition(
                        roi_id="setup-roi",
                        shape="rectangle",
                        points=((10, 20), (110, 70)),
                    )
                )
            )
        )

        reflection = shell._build_setup_reflection(
            focus_summary="1.234e-02",
            status=SimpleNamespace(
                configuration=SimpleNamespace(
                    exposure_time_us=1500.0,
                    gain=3.0,
                    pixel_format="Mono8",
                    acquisition_frame_rate=12.5,
                    roi_offset_x=10,
                    roi_offset_y=20,
                    roi_width=100,
                    roi_height=50,
                )
            ),
        )

        self.assertEqual(reflection["phase"], "ready")
        self.assertEqual(reflection["focus_visibility"], "visible")
        self.assertEqual(reflection["focus_summary"], "1.234e-02")
        self.assertTrue(reflection["roi_active"])
        self.assertEqual(reflection["roi_shape"], "rectangle")
        self.assertEqual(reflection["roi_bounds"], [10, 20, 110, 70])
        self.assertIn("roi=x=10,y=20,w=100,h=50", reflection["configuration_summary"])

    def test_build_recording_reflection_uses_failed_phase_when_last_error_exists(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        shell._recording_last_file_stem = "delam_run"
        shell._recording_last_save_directory = Path("captures/delam")
        shell._recording_last_stop_reason = None
        shell._recording_last_error = "disk full"

        reflection = shell._build_recording_reflection(
            SimpleNamespace(
                recording=SimpleNamespace(
                    is_recording=False,
                    frames_written=4,
                    active_file_stem=None,
                    save_directory=None,
                    last_error=None,
                )
            ),
            recording_summary="4/n",
        )

        self.assertEqual(reflection["phase"], "failed")
        self.assertEqual(reflection["stop_category"], "failure_termination")
        self.assertEqual(reflection["last_error"], "disk full")
        self.assertEqual(reflection["save_directory"], str(Path("captures/delam")))

    def test_build_local_shell_session_reuses_simulated_subsystem_and_save_directory(self) -> None:
        with TemporaryDirectory() as temp_dir:
            session = build_local_shell_session(
                LocalShellLaunchOptions(
                    source="simulated",
                    snapshot_directory=Path(temp_dir),
                    exposure_time_us=1200.0,
                    pixel_format="Mono8",
                )
            )
            try:
                status = session.subsystem.command_controller.get_status()

                self.assertEqual(session.source, "simulated")
                self.assertEqual(session.selected_save_directory, Path(temp_dir))
                self.assertIsNotNone(session.focus_preview_service)
                self.assertTrue(status.camera.is_initialized)
                self.assertEqual(status.default_save_directory, Path(temp_dir))
                self.assertEqual(status.configuration.pixel_format, "Mono8")
                self.assertEqual(status.configuration.exposure_time_us, 1200.0)
            finally:
                session.subsystem.driver.shutdown()

    def test_local_shell_focus_preview_service_refreshes_from_shared_preview_path(self) -> None:
        with TemporaryDirectory() as temp_dir:
            session = build_local_shell_session(
                LocalShellLaunchOptions(
                    source="simulated",
                    snapshot_directory=Path(temp_dir),
                )
            )
            try:
                session.subsystem.stream_service.start_preview()
                try:
                    focus_state = session.focus_preview_service.refresh_once()
                    self.assertIsNotNone(focus_state)
                    self.assertTrue(focus_state.result.is_valid)
                finally:
                    session.subsystem.stream_service.stop_preview()
            finally:
                session.subsystem.driver.shutdown()

    def test_build_local_shell_session_reuses_headless_alias_and_profile_resolution_for_hardware_path(self) -> None:
        with TemporaryDirectory() as temp_dir:
            with patch(
                "vision_platform.apps.local_shell.startup._create_hardware_driver",
                return_value=SimulatedCameraDriver(),
            ):
                session = build_local_shell_session(
                    LocalShellLaunchOptions(
                        source="hardware",
                        camera_alias="tested_camera",
                        configuration_profile="default",
                        profile_camera_class="1800_u_1240m",
                        snapshot_directory=Path(temp_dir),
                    )
                )
            try:
                status = session.subsystem.command_controller.get_status()

                self.assertEqual(session.source, "hardware")
                self.assertEqual(session.resolved_camera_id, "DEV_1AB22C046D81")
                self.assertEqual(session.configuration_profile_id, "default")
                self.assertIsNotNone(session.focus_preview_service)
                self.assertEqual(status.configuration.pixel_format, "Mono10")
                self.assertEqual(status.configuration.gain, 3.0)
                self.assertEqual(status.configuration.roi_width, 2000)
                self.assertEqual(status.default_save_directory, Path(temp_dir))
            finally:
                session.subsystem.driver.shutdown()

    def test_build_local_shell_session_rejects_sample_dir_for_hardware_source(self) -> None:
        with self.assertRaises(LocalShellStartupError):
            build_local_shell_session(
                LocalShellLaunchOptions(
                    source="hardware",
                    sample_dir=Path("fixtures"),
                )
            )


if __name__ == "__main__":
    unittest.main()


class _StubKeyEvent:
    def __init__(self, key_code: int, *, control_down: bool) -> None:
        self._key_code = key_code
        self._control_down = control_down

    def GetKeyCode(self) -> int:
        return self._key_code

    def ControlDown(self) -> bool:
        return self._control_down

    def CmdDown(self) -> bool:
        return False


class _StubPresenter:
    def __init__(self, *, focus_status_visible: bool) -> None:
        self.state = type(
            "State",
            (),
            {"interaction_state": type("InteractionState", (), {"focus_status_visible": focus_status_visible})()},
        )()


class _StubMenuItem:
    def __init__(self) -> None:
        self.enabled = None

    def Enable(self, enabled: bool) -> None:
        self.enabled = enabled


class _StubTextControl:
    def __init__(self, value: str) -> None:
        self._value = value

    def GetValue(self) -> str:
        return self._value

    def ChangeValue(self, value: str) -> None:
        self._value = value


class _StubChoiceControl:
    def __init__(self, value: str) -> None:
        self._value = value

    def GetStringSelection(self) -> str:
        return self._value
