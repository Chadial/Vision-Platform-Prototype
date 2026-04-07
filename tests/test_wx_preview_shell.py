import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from tests import _path_setup
from vision_platform.apps.local_shell import PreviewShellPresenter
from vision_platform.apps.local_shell.preview_shell_state import render_viewport_image
from vision_platform.apps.local_shell.startup import (
    LocalShellLaunchOptions,
    LocalShellStartupError,
    build_local_shell_session,
)
from vision_platform.integrations.camera import SimulatedCameraDriver
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
                self.assertTrue(status.camera.is_initialized)
                self.assertEqual(status.default_save_directory, Path(temp_dir))
                self.assertEqual(status.configuration.pixel_format, "Mono8")
                self.assertEqual(status.configuration.exposure_time_us, 1200.0)
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
