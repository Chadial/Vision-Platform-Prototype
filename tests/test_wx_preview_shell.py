import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from types import SimpleNamespace

from tests import _path_setup
from vision_platform.apps.local_shell import PreviewShellPresenter
from vision_platform.apps.local_shell.wx_preview_shell import WxLocalPreviewShell, _is_copy_shortcut
from vision_platform.apps.local_shell.preview_shell_state import render_viewport_image
from vision_platform.apps.local_shell.startup import (
    LocalShellLaunchOptions,
    LocalShellStartupError,
    build_local_shell_session,
)
from vision_platform.integrations.camera import SimulatedCameraDriver
from vision_platform.libraries.common_models import FocusOverlayData, FocusPreviewState, FocusResult
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

    def test_recording_summary_formats_bounded_and_unbounded_progress(self) -> None:
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        status = SimpleNamespace(recording=SimpleNamespace(is_recording=True, frames_written=3))

        shell._recording_active_frame_limit = 10
        bounded_summary = shell._build_recording_summary(status)

        shell._recording_active_frame_limit = None
        unbounded_summary = shell._build_recording_summary(status)

        self.assertEqual(bounded_summary, "3/10")
        self.assertEqual(unbounded_summary, "3/n")

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
                self.assertEqual(status.configuration.pixel_format, "Mono8")
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
