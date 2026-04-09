import argparse
import unittest
from pathlib import Path
from unittest.mock import patch

from vision_platform.apps.local_shell import control_cli


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
