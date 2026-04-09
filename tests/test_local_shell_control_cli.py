import argparse
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from vision_platform.apps.local_shell import control_cli
from vision_platform.apps.local_shell.live_command_sync import (
    append_live_command,
    create_live_sync_session,
    read_live_status_snapshot,
    read_pending_live_commands,
    wait_for_live_command_result,
    write_live_command_result,
)
from vision_platform.apps.local_shell.wx_preview_shell import WxLocalPreviewShell


class LocalShellControlCliTests(unittest.TestCase):
    def test_snapshot_command_passes_file_stem_and_extension(self) -> None:
        args = argparse.Namespace(
            session_root=Path("captures/wx_shell_sessions"),
            file_stem="geometry_000001",
            file_extension=".bmp",
        )

        with patch.object(control_cli, "_send_command", return_value={"ok": True}) as send_command:
            control_cli._handle_snapshot_command(args)

        send_command.assert_called_once_with(
            Path("captures/wx_shell_sessions"),
            command_name="save_snapshot",
            payload={
                "file_stem": "geometry_000001",
                "file_extension": ".bmp",
            },
        )

    def test_start_recording_command_omits_unset_optional_overrides(self) -> None:
        args = argparse.Namespace(
            session_root=Path("captures/wx_shell_sessions"),
            file_stem=None,
            file_extension=None,
            max_frames=None,
            recording_fps=None,
        )

        with patch.object(control_cli, "_send_command", return_value={"ok": True}) as send_command:
            control_cli._handle_start_recording_command(args)

        send_command.assert_called_once_with(
            Path("captures/wx_shell_sessions"),
            command_name="start_recording",
            payload={},
        )

    def test_start_recording_command_preserves_explicit_unbounded_override(self) -> None:
        args = argparse.Namespace(
            session_root=Path("captures/wx_shell_sessions"),
            file_stem="host_run",
            file_extension=".bmp",
            max_frames=0,
            recording_fps=12.5,
        )

        with patch.object(control_cli, "_send_command", return_value={"ok": True}) as send_command:
            control_cli._handle_start_recording_command(args)

        send_command.assert_called_once_with(
            Path("captures/wx_shell_sessions"),
            command_name="start_recording",
            payload={
                "file_stem": "host_run",
                "file_extension": ".bmp",
                "max_frame_count": None,
                "target_frame_rate": 12.5,
            },
        )

    def test_start_recording_command_rejects_negative_max_frames(self) -> None:
        args = argparse.Namespace(
            session_root=Path("captures/wx_shell_sessions"),
            file_stem=None,
            file_extension=None,
            max_frames=-1,
            recording_fps=None,
        )

        with self.assertRaises(control_cli.LocalShellLiveSyncError):
            control_cli._handle_start_recording_command(args)

    def test_host_control_smoke_covers_start_status_and_stop_for_delamination_path(self) -> None:
        with TemporaryDirectory() as temp_dir:
            session = create_live_sync_session(
                root_directory=Path(temp_dir),
                source="simulated",
                camera_id="DEV_123",
                configuration_profile_id="default",
            )
            controller = _SmokeController()
            shell = _build_smoke_shell(session=session, controller=controller)

            start_command = append_live_command(
                session,
                command_name="start_recording",
                payload={"file_stem": "delam_run", "max_frame_count": 3},
            )
            commands, processed_count = read_pending_live_commands(session, processed_count=0)
            self.assertEqual(processed_count, 1)
            result = shell._execute_live_command(commands[0])
            write_live_command_result(session, command_id=start_command.command_id, success=True, result=result)
            shell._publish_live_status_snapshot(controller.get_status(), focus_summary="hidden", recording_summary="0/3")
            start_result = wait_for_live_command_result(session, command_id=start_command.command_id, timeout_seconds=0.2)
            self.assertTrue(start_result["success"])
            self.assertEqual(start_result["result"]["reflection_kind"], "recording")
            self.assertEqual(start_result["result"]["reflection"]["phase"], "running")

            status_snapshot = read_live_status_snapshot(session)
            self.assertEqual(status_snapshot["recording_reflection"]["phase"], "running")
            self.assertEqual(status_snapshot["recording_reflection"]["file_stem"], "delam_run")
            self.assertEqual(status_snapshot["recording_reflection"]["save_directory"], str(Path("captures/delam")))

            stop_command = append_live_command(
                session,
                command_name="stop_recording",
                payload={"reason": "external_cli"},
            )
            commands, processed_count = read_pending_live_commands(session, processed_count=processed_count)
            self.assertEqual(processed_count, 2)
            result = shell._execute_live_command(commands[0])
            write_live_command_result(session, command_id=stop_command.command_id, success=True, result=result)
            shell._publish_live_status_snapshot(controller.get_status(), focus_summary="hidden", recording_summary="4/3")
            stop_result = wait_for_live_command_result(session, command_id=stop_command.command_id, timeout_seconds=0.2)
            self.assertTrue(stop_result["success"])

            status_snapshot = read_live_status_snapshot(session)
            self.assertEqual(status_snapshot["recording_reflection"]["phase"], "idle")
            self.assertEqual(status_snapshot["recording_reflection"]["stop_category"], "host_stop")
            self.assertEqual(status_snapshot["recording_reflection"]["frames_written"], 4)

    def test_host_control_smoke_covers_snapshot_status_for_geometry_capture_path(self) -> None:
        with TemporaryDirectory() as temp_dir:
            session = create_live_sync_session(
                root_directory=Path(temp_dir),
                source="simulated",
                camera_id="DEV_123",
                configuration_profile_id="default",
            )
            controller = _SmokeController()
            shell = _build_smoke_shell(session=session, controller=controller)

            snapshot_command = append_live_command(
                session,
                command_name="save_snapshot",
                payload={"file_stem": "geometry_000001", "file_extension": ".bmp"},
            )
            commands, processed_count = read_pending_live_commands(session, processed_count=0)
            self.assertEqual(processed_count, 1)
            result = shell._execute_live_command(commands[0])
            write_live_command_result(session, command_id=snapshot_command.command_id, success=True, result=result)
            shell._publish_live_status_snapshot(controller.get_status(), focus_summary="hidden", recording_summary=None)
            command_result = wait_for_live_command_result(session, command_id=snapshot_command.command_id, timeout_seconds=0.2)
            self.assertTrue(command_result["success"])
            self.assertEqual(command_result["result"]["reflection_kind"], "snapshot")
            self.assertEqual(command_result["result"]["reflection"]["phase"], "saved")

            status_snapshot = read_live_status_snapshot(session)
            self.assertEqual(status_snapshot["snapshot_reflection"]["phase"], "saved")
            self.assertEqual(status_snapshot["snapshot_reflection"]["file_name"], "geometry_000001.bmp")
            self.assertEqual(status_snapshot["snapshot_reflection"]["save_directory"], str(Path("captures/geometry")))

    def test_host_control_smoke_covers_setup_status_for_setup_path(self) -> None:
        with TemporaryDirectory() as temp_dir:
            session = create_live_sync_session(
                root_directory=Path(temp_dir),
                source="simulated",
                camera_id="DEV_123",
                configuration_profile_id="default",
            )
            controller = _SmokeController()
            shell = _build_smoke_shell(session=session, controller=controller)
            shell._focus_preview_service = object()
            shell._presenter = SimpleNamespace(
                state=SimpleNamespace(interaction_state=SimpleNamespace(focus_status_visible=True))
            )
            controller._roi = SimpleNamespace(shape="rectangle", points=((10, 20), (110, 70)))

            config_command = append_live_command(
                session,
                command_name="apply_configuration",
                payload={"gain": 5.0, "roi_width": 100, "roi_height": 50},
            )
            commands, processed_count = read_pending_live_commands(session, processed_count=0)
            self.assertEqual(processed_count, 1)
            result = shell._execute_live_command(commands[0])
            write_live_command_result(session, command_id=config_command.command_id, success=True, result=result)
            shell._publish_live_status_snapshot(controller.get_status(), focus_summary="1.234e-02", recording_summary=None)
            command_result = wait_for_live_command_result(session, command_id=config_command.command_id, timeout_seconds=0.2)
            self.assertTrue(command_result["success"])
            self.assertEqual(command_result["result"]["reflection_kind"], "setup")
            self.assertEqual(command_result["result"]["reflection"]["phase"], "ready")

            status_snapshot = read_live_status_snapshot(session)
            self.assertEqual(status_snapshot["setup_reflection"]["phase"], "ready")
            self.assertEqual(status_snapshot["setup_reflection"]["focus_visibility"], "visible")
            self.assertEqual(status_snapshot["setup_reflection"]["roi_shape"], "rectangle")
            self.assertEqual(status_snapshot["setup_reflection"]["roi_bounds"], [10, 20, 110, 70])


class _SmokeController:
    def __init__(self) -> None:
        self._roi = None
        self._status = SimpleNamespace(
            camera=SimpleNamespace(is_initialized=True, reported_acquisition_frame_rate=15.0),
            default_save_directory=Path("captures/delam"),
            configuration=SimpleNamespace(
                exposure_time_us=None,
                gain=None,
                pixel_format=None,
                acquisition_frame_rate=None,
                roi_offset_x=None,
                roi_offset_y=None,
                roi_width=None,
                roi_height=None,
            ),
            recording=SimpleNamespace(
                is_recording=False,
                frames_written=0,
                active_file_stem=None,
                save_directory=None,
                last_error=None,
            ),
        )

    def start_recording(self, request):
        self._status.recording.is_recording = True
        self._status.recording.frames_written = 0
        self._status.recording.active_file_stem = request.file_stem
        self._status.recording.save_directory = request.save_directory
        self._status.recording.last_error = None
        return SimpleNamespace(status=SimpleNamespace(active_file_stem=request.file_stem, frames_written=0))

    def stop_recording(self, request):
        self._status.recording.is_recording = False
        self._status.recording.frames_written = 4
        self._status.recording.active_file_stem = None
        self._status.recording.save_directory = None
        self._status.recording.last_error = None
        return SimpleNamespace(status=SimpleNamespace(frames_written=4), stop_reason=request.reason)

    def save_snapshot(self, request):
        return SimpleNamespace(saved_path=Path("captures/geometry") / f"{request.file_stem}{request.file_extension}")

    def apply_configuration(self, request):
        self._status.configuration.gain = request.gain
        self._status.configuration.roi_width = request.roi_width
        self._status.configuration.roi_height = request.roi_height
        self._status.configuration.roi_offset_x = 10 if request.roi_width is not None else None
        self._status.configuration.roi_offset_y = 20 if request.roi_height is not None else None
        return request

    def get_status(self):
        return self._status


def _build_smoke_shell(*, session, controller) -> WxLocalPreviewShell:
    shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
    shell._session = SimpleNamespace(
        subsystem=SimpleNamespace(command_controller=controller),
        selected_save_directory=Path("captures/delam"),
        resolved_camera_id="DEV_123",
        configuration_profile_id="default",
        configuration_profile_camera_class="1800_u_1240m",
        live_sync_session=session,
        source="simulated",
    )
    shell._subsystem = SimpleNamespace(
        stream_service=SimpleNamespace(
            is_preview_running=True,
            get_roi_state_service=lambda: SimpleNamespace(get_active_roi=lambda: controller._roi),
        ),
    )
    shell._cached_status = None
    shell._last_status_refresh_time = 0.0
    shell._recording_active_frame_limit = None
    shell._recording_target_frame_rate_value = None
    shell._recording_last_summary = None
    shell._recording_last_file_stem = None
    shell._recording_last_save_directory = None
    shell._recording_last_stop_reason = None
    shell._recording_last_error = None
    shell._snapshot_last_saved_path = None
    shell._snapshot_last_error = None
    shell._recording_file_stem = "wx_recording"
    shell._recording_file_extension = ".bmp"
    shell._recording_max_frames = SimpleNamespace(GetValue=lambda: "0")
    shell._recording_target_frame_rate_input = SimpleNamespace(GetValue=lambda: "")
    shell._status_lines = []
    shell._set_transient_status_message = lambda _message: None
    shell._get_recording_save_directory = lambda: Path("captures/delam")
    return shell
