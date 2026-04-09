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


class _SmokeController:
    def __init__(self) -> None:
        self._status = SimpleNamespace(
            camera=SimpleNamespace(is_initialized=True, reported_acquisition_frame_rate=15.0),
            default_save_directory=Path("captures/delam"),
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
        stream_service=SimpleNamespace(is_preview_running=True),
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
    shell._recording_file_stem = "wx_recording"
    shell._recording_file_extension = ".bmp"
    shell._recording_max_frames = SimpleNamespace(GetValue=lambda: "0")
    shell._recording_target_frame_rate_input = SimpleNamespace(GetValue=lambda: "")
    shell._status_lines = []
    shell._set_transient_status_message = lambda _message: None
    shell._get_recording_save_directory = lambda: Path("captures/delam")
    return shell
