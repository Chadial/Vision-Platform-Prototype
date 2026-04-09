import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

from vision_platform.apps.local_shell.live_command_sync import (
    LocalShellLiveSyncError,
    append_live_command,
    close_live_sync_session,
    create_live_sync_session,
    read_live_status_snapshot,
    read_pending_live_commands,
    resolve_active_live_sync_session,
    wait_for_live_command_result,
    write_live_command_result,
    write_live_status_snapshot,
)
from vision_platform.apps.local_shell.wx_preview_shell import WxLocalPreviewShell


class LocalShellLiveCommandSyncTests(unittest.TestCase):
    def test_live_sync_session_round_trip_tracks_commands_results_and_status(self) -> None:
        with TemporaryDirectory() as temp_dir:
            session = create_live_sync_session(
                root_directory=Path(temp_dir),
                source="simulated",
                camera_id=None,
                configuration_profile_id=None,
            )

            resolved_session = resolve_active_live_sync_session(Path(temp_dir))
            self.assertEqual(resolved_session.session_id, session.session_id)

            command = append_live_command(
                session,
                command_name="start_recording",
                payload={"file_stem": "wx_recording", "max_frame_count": 5},
            )
            pending, processed_count = read_pending_live_commands(session, processed_count=0)

            self.assertEqual(processed_count, 1)
            self.assertEqual(len(pending), 1)
            self.assertEqual(pending[0].command_id, command.command_id)
            self.assertEqual(pending[0].command_name, "start_recording")

            write_live_command_result(
                session,
                command_id=command.command_id,
                success=True,
                command_name="start_recording",
                result={"ok": True},
            )
            result = wait_for_live_command_result(session, command_id=command.command_id, timeout_seconds=0.2)
            self.assertTrue(result["success"])
            self.assertEqual(result["command_name"], "start_recording")
            self.assertEqual(result["result"], {"ok": True})

            write_live_status_snapshot(
                session,
                {
                    "session_id": session.session_id,
                    "status_lines": ["preview=running"],
                },
            )
            status_snapshot = read_live_status_snapshot(session)
            self.assertEqual(status_snapshot["status_lines"], ["preview=running"])

            close_live_sync_session(session)
            with self.assertRaises(LocalShellLiveSyncError):
                resolve_active_live_sync_session(Path(temp_dir))

    def test_execute_live_start_recording_updates_shell_tracking_state(self) -> None:
        controller = _StubController()
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        shell._session = SimpleNamespace(
            subsystem=SimpleNamespace(command_controller=controller),
            selected_save_directory=Path("captures/wx_shell_snapshot"),
            resolved_camera_id="DEV_123",
            configuration_profile_id="default",
            configuration_profile_camera_class="1800_u_1240m",
            live_sync_session=None,
            source="hardware",
        )
        shell._subsystem = shell._session.subsystem
        shell._cached_status = object()
        shell._last_status_refresh_time = 1.0
        shell._recording_active_frame_limit = None
        shell._recording_target_frame_rate_value = None
        shell._recording_last_summary = "old"
        shell._set_transient_status_message = lambda message: setattr(shell, "_last_message", message)
        shell._get_recording_save_directory = lambda: Path("captures/wx_shell_snapshot")

        result = shell._execute_live_command(
            SimpleNamespace(
                command_name="start_recording",
                payload={
                    "file_stem": "external",
                    "file_extension": ".raw",
                    "max_frame_count": 7,
                    "target_frame_rate": 12.5,
                },
            )
        )

        self.assertEqual(controller.start_recording_calls[0].file_stem, "external")
        self.assertEqual(shell._recording_active_frame_limit, 7)
        self.assertEqual(shell._recording_target_frame_rate_value, 12.5)
        self.assertIsNone(shell._recording_last_summary)
        self.assertEqual(shell._cached_status, None)
        self.assertIn("External recording run started", shell._last_message)
        self.assertEqual(result["command"], "start_recording")
        self.assertEqual(result["reflection_kind"], "recording")
        self.assertEqual(result["reflection"]["phase"], "running")

    def test_execute_live_stop_recording_keeps_last_summary(self) -> None:
        controller = _StubController()
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        shell._session = SimpleNamespace(
            subsystem=SimpleNamespace(command_controller=controller),
            selected_save_directory=Path("captures/wx_shell_snapshot"),
            resolved_camera_id="DEV_123",
            configuration_profile_id="default",
            configuration_profile_camera_class="1800_u_1240m",
            live_sync_session=None,
            source="hardware",
        )
        shell._subsystem = shell._session.subsystem
        shell._cached_status = object()
        shell._last_status_refresh_time = 1.0
        shell._recording_active_frame_limit = 10
        shell._recording_target_frame_rate_value = 12.5
        shell._recording_last_summary = None
        shell._set_transient_status_message = lambda message: setattr(shell, "_last_message", message)

        result = shell._execute_live_command(
            SimpleNamespace(
                command_name="stop_recording",
                payload={"reason": "external_cli"},
            )
        )

        self.assertEqual(shell._recording_active_frame_limit, None)
        self.assertEqual(shell._recording_last_summary, "4/10")
        self.assertIn("External recording run stopped", shell._last_message)
        self.assertEqual(result["command"], "stop_recording")
        self.assertEqual(result["reflection_kind"], "recording")
        self.assertEqual(result["reflection"]["stop_category"], "host_stop")

    def test_publish_live_status_snapshot_writes_current_shell_status(self) -> None:
        with TemporaryDirectory() as temp_dir:
            session = create_live_sync_session(
                root_directory=Path(temp_dir),
                source="simulated",
                camera_id=None,
                configuration_profile_id=None,
            )
            shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
            shell._session = SimpleNamespace(
                live_sync_session=session,
                source="simulated",
                resolved_camera_id=None,
                configuration_profile_id=None,
            )
            shell._focus_preview_service = object()
            shell._presenter = SimpleNamespace(
                state=SimpleNamespace(interaction_state=SimpleNamespace(focus_status_visible=True))
            )
            shell._subsystem = SimpleNamespace(
                stream_service=SimpleNamespace(
                    get_roi_state_service=lambda: SimpleNamespace(
                        get_active_roi=lambda: SimpleNamespace(shape="rectangle", points=((10, 20), (110, 70)))
                    )
                )
            )
            shell._recording_last_file_stem = "delam_run"
            shell._recording_last_save_directory = Path("captures/delam")
            shell._recording_last_stop_reason = "external_cli"
            shell._snapshot_last_saved_path = Path("captures/geometry/geometry_000001.bmp")
            shell._snapshot_last_error = None
            shell._status_lines = ["source=simulated | preview=running", "FPS 25.0"]

            shell._publish_live_status_snapshot(
                SimpleNamespace(
                    camera=SimpleNamespace(is_initialized=True),
                    default_save_directory=Path("captures/wx_shell_snapshot"),
                    recording=SimpleNamespace(
                        is_recording=False,
                        frames_written=3,
                        active_file_stem=None,
                        save_directory=None,
                    ),
                ),
                focus_summary="hidden",
                recording_summary="3/n",
            )

            snapshot = read_live_status_snapshot(session)
            self.assertEqual(snapshot["focus_summary"], "hidden")
            self.assertEqual(
                snapshot["setup_reflection"],
                {
                    "phase": "ready",
                    "focus_visibility": "visible",
                    "focus_summary": "hidden",
                    "roi_active": True,
                    "roi_shape": "rectangle",
                    "roi_bounds": [10, 20, 110, 70],
                    "configuration_summary": None,
                },
            )
            self.assertIsNone(snapshot["failure_reflection"])
            self.assertEqual(
                snapshot["snapshot_reflection"],
                {
                    "phase": "saved",
                    "file_name": "geometry_000001.bmp",
                    "file_stem": "geometry_000001",
                    "save_directory": str(Path("captures/geometry")),
                    "last_error": None,
                },
            )
            self.assertEqual(snapshot["recording_summary"], "3/n")
            self.assertEqual(
                snapshot["recording_reflection"],
                {
                    "phase": "idle",
                    "summary": "3/n",
                    "file_stem": "delam_run",
                    "save_directory": str(Path("captures/delam")),
                    "stop_reason": "external_cli",
                    "stop_category": "host_stop",
                    "frames_written": 3,
                    "last_error": None,
                },
            )
            self.assertEqual(snapshot["status_lines"], shell._status_lines)

    def test_publish_live_status_snapshot_categorizes_max_frames_stop(self) -> None:
        with TemporaryDirectory() as temp_dir:
            session = create_live_sync_session(
                root_directory=Path(temp_dir),
                source="simulated",
                camera_id=None,
                configuration_profile_id=None,
            )
            shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
            shell._session = SimpleNamespace(
                live_sync_session=session,
                source="simulated",
                resolved_camera_id=None,
                configuration_profile_id=None,
            )
            shell._recording_last_file_stem = "delam_run"
            shell._recording_last_save_directory = Path("captures/delam")
            shell._recording_last_stop_reason = "max_frames_reached"
            shell._status_lines = ["source=simulated | preview=running", "FPS 25.0"]

            shell._publish_live_status_snapshot(
                SimpleNamespace(
                    camera=SimpleNamespace(is_initialized=True),
                    default_save_directory=Path("captures/wx_shell_snapshot"),
                    recording=SimpleNamespace(
                        is_recording=False,
                        frames_written=3,
                        active_file_stem=None,
                        save_directory=None,
                    ),
                ),
                focus_summary="hidden",
                recording_summary="3/3",
            )

            snapshot = read_live_status_snapshot(session)
            self.assertEqual(snapshot["recording_reflection"]["stop_reason"], "max_frames_reached")
            self.assertEqual(snapshot["recording_reflection"]["stop_category"], "max_frames_reached")

    def test_publish_live_status_snapshot_marks_failed_recording_reflection_when_last_error_exists(self) -> None:
        with TemporaryDirectory() as temp_dir:
            session = create_live_sync_session(
                root_directory=Path(temp_dir),
                source="simulated",
                camera_id=None,
                configuration_profile_id=None,
            )
            shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
            shell._session = SimpleNamespace(
                live_sync_session=session,
                source="simulated",
                resolved_camera_id=None,
                configuration_profile_id=None,
            )
            shell._recording_last_file_stem = "delam_run"
            shell._recording_last_save_directory = Path("captures/delam")
            shell._recording_last_stop_reason = None
            shell._recording_last_error = "disk full"
            shell._status_lines = ["source=simulated | preview=running", "FPS 25.0"]

            shell._publish_live_status_snapshot(
                SimpleNamespace(
                    camera=SimpleNamespace(is_initialized=True),
                    default_save_directory=Path("captures/wx_shell_snapshot"),
                    recording=SimpleNamespace(
                        is_recording=False,
                        frames_written=4,
                        active_file_stem=None,
                        save_directory=None,
                        last_error=None,
                    ),
                ),
                focus_summary="hidden",
                recording_summary="4/n",
            )

            snapshot = read_live_status_snapshot(session)
            self.assertEqual(snapshot["recording_reflection"]["phase"], "failed")
            self.assertEqual(snapshot["recording_reflection"]["stop_category"], "failure_termination")
            self.assertEqual(snapshot["recording_reflection"]["last_error"], "disk full")

    def test_publish_live_status_snapshot_marks_failed_snapshot_reflection_when_last_error_exists(self) -> None:
        with TemporaryDirectory() as temp_dir:
            session = create_live_sync_session(
                root_directory=Path(temp_dir),
                source="simulated",
                camera_id=None,
                configuration_profile_id=None,
            )
            shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
            shell._session = SimpleNamespace(
                live_sync_session=session,
                source="simulated",
                resolved_camera_id=None,
                configuration_profile_id=None,
            )
            shell._snapshot_last_saved_path = Path("captures/geometry/geometry_000001.bmp")
            shell._snapshot_last_error = "disk full"
            shell._recording_last_file_stem = None
            shell._recording_last_save_directory = None
            shell._recording_last_stop_reason = None
            shell._status_lines = ["source=simulated | preview=running", "FPS 25.0"]

            shell._publish_live_status_snapshot(
                SimpleNamespace(
                    camera=SimpleNamespace(is_initialized=True),
                    default_save_directory=Path("captures/wx_shell_snapshot"),
                    recording=SimpleNamespace(
                        is_recording=False,
                        frames_written=0,
                        active_file_stem=None,
                        save_directory=None,
                        last_error=None,
                    ),
                ),
                focus_summary="hidden",
                recording_summary=None,
            )

            snapshot = read_live_status_snapshot(session)
            self.assertEqual(snapshot["snapshot_reflection"]["phase"], "failed")
            self.assertEqual(snapshot["snapshot_reflection"]["last_error"], "disk full")
            self.assertIsNone(snapshot["failure_reflection"])

    def test_publish_live_status_snapshot_includes_shared_failure_reflection(self) -> None:
        with TemporaryDirectory() as temp_dir:
            session = create_live_sync_session(
                root_directory=Path(temp_dir),
                source="simulated",
                camera_id=None,
                configuration_profile_id=None,
            )
            shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
            shell._session = SimpleNamespace(
                live_sync_session=session,
                source="simulated",
                resolved_camera_id=None,
                configuration_profile_id=None,
            )
            shell._focus_preview_service = None
            shell._presenter = SimpleNamespace(
                state=SimpleNamespace(interaction_state=SimpleNamespace(focus_status_visible=False))
            )
            shell._subsystem = SimpleNamespace(
                stream_service=SimpleNamespace(
                    get_roi_state_service=lambda: SimpleNamespace(get_active_roi=lambda: None)
                )
            )
            shell._recording_last_file_stem = None
            shell._recording_last_save_directory = None
            shell._recording_last_stop_reason = None
            shell._recording_last_error = None
            shell._snapshot_last_saved_path = None
            shell._snapshot_last_error = None
            shell._failure_reflection = {
                "phase": "failed",
                "source": "setup",
                "action": "apply_configuration",
                "message": "camera rejected roi",
                "external": True,
            }
            shell._status_lines = ["source=simulated | preview=running | failure=setup", "FPS 25.0"]

            shell._publish_live_status_snapshot(
                SimpleNamespace(
                    camera=SimpleNamespace(is_initialized=True),
                    default_save_directory=Path("captures/wx_shell_snapshot"),
                    configuration=None,
                    recording=SimpleNamespace(
                        is_recording=False,
                        frames_written=0,
                        active_file_stem=None,
                        save_directory=None,
                        last_error=None,
                    ),
                ),
                focus_summary=None,
                recording_summary=None,
            )

            snapshot = read_live_status_snapshot(session)
            self.assertEqual(
                snapshot["failure_reflection"],
                {
                    "phase": "failed",
                    "source": "setup",
                    "action": "apply_configuration",
                    "message": "camera rejected roi",
                    "external": True,
                },
            )

    def test_execute_live_apply_configuration_uses_setup_oriented_message(self) -> None:
        controller = _StubController()
        shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
        shell._session = SimpleNamespace(
            subsystem=SimpleNamespace(command_controller=controller),
            selected_save_directory=Path("captures/wx_shell_snapshot"),
            resolved_camera_id="DEV_123",
            configuration_profile_id="default",
            configuration_profile_camera_class="1800_u_1240m",
            live_sync_session=None,
            source="hardware",
        )
        shell._subsystem = shell._session.subsystem
        shell._cached_focus_state = object()
        shell._cached_status = object()
        shell._last_status_refresh_time = 1.0
        shell._set_transient_status_message = lambda message: setattr(shell, "_last_message", message)

        result = shell._execute_live_command(
            SimpleNamespace(
                command_name="apply_configuration",
                payload={"gain": 5.0, "roi_width": 100},
            )
        )

        self.assertEqual(result["command"], "apply_configuration")
        self.assertEqual(shell._last_message, "External setup configuration applied")
        self.assertIsNone(shell._cached_focus_state)
        self.assertEqual(result["reflection_kind"], "setup")
        self.assertEqual(result["reflection"]["phase"], "ready")
        self.assertIsNone(result["failure_reflection"])

    def test_poll_live_commands_writes_shared_failure_reflection_for_setup_failure(self) -> None:
        with TemporaryDirectory() as temp_dir:
            session = create_live_sync_session(
                root_directory=Path(temp_dir),
                source="simulated",
                camera_id=None,
                configuration_profile_id=None,
            )
            command = append_live_command(
                session,
                command_name="apply_configuration",
                payload={"gain": 5.0},
            )
            shell = WxLocalPreviewShell.__new__(WxLocalPreviewShell)
            shell._session = SimpleNamespace(
                live_sync_session=session,
                subsystem=SimpleNamespace(command_controller=_FailingApplyConfigurationController()),
                selected_save_directory=Path("captures/wx_shell_snapshot"),
                resolved_camera_id="DEV_123",
                configuration_profile_id="default",
                configuration_profile_camera_class="1800_u_1240m",
                source="simulated",
            )
            shell._subsystem = shell._session.subsystem
            shell._live_sync_processed_count = 0
            shell._cached_status = object()
            shell._last_status_refresh_time = 1.0
            shell._set_transient_status_message = lambda message: setattr(shell, "_last_message", message)

            shell._poll_live_commands()

            result = wait_for_live_command_result(session, command_id=command.command_id, timeout_seconds=0.2)
            self.assertFalse(result["success"])
            self.assertEqual(result["error"], "camera rejected roi")
            self.assertEqual(result["result"]["failure_reflection"]["source"], "setup")
            self.assertEqual(result["result"]["failure_reflection"]["action"], "apply_configuration")
            self.assertTrue(result["result"]["failure_reflection"]["external"])

    def test_write_live_command_result_keeps_failure_command_name_and_placeholder_result(self) -> None:
        with TemporaryDirectory() as temp_dir:
            session = create_live_sync_session(
                root_directory=Path(temp_dir),
                source="simulated",
                camera_id=None,
                configuration_profile_id=None,
            )
            command = append_live_command(
                session,
                command_name="save_snapshot",
                payload={"file_stem": "geometry_000001"},
            )

            write_live_command_result(
                session,
                command_id=command.command_id,
                command_name="save_snapshot",
                success=False,
                result={
                    "command": "save_snapshot",
                    "reflection_kind": None,
                    "reflection": None,
                    "failure_reflection": None,
                    "result": None,
                },
                error="disk full",
            )

            result = wait_for_live_command_result(session, command_id=command.command_id, timeout_seconds=0.2)
            self.assertFalse(result["success"])
            self.assertEqual(result["command_name"], "save_snapshot")
            self.assertEqual(result["result"]["command"], "save_snapshot")
            self.assertEqual(result["error"], "disk full")


class _StubController:
    def __init__(self) -> None:
        self.start_recording_calls = []
        self._status = SimpleNamespace(
            camera=SimpleNamespace(is_initialized=True, reported_acquisition_frame_rate=15.0),
            default_save_directory=Path("captures/wx_shell_snapshot"),
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
        self.start_recording_calls.append(request)
        self._status.recording.is_recording = True
        self._status.recording.frames_written = 0
        self._status.recording.active_file_stem = request.file_stem
        self._status.recording.save_directory = Path("captures/wx_shell_snapshot")
        return SimpleNamespace(status=SimpleNamespace(active_file_stem=request.file_stem, frames_written=0))

    def stop_recording(self, request):
        self._status.recording.is_recording = False
        self._status.recording.frames_written = 4
        self._status.recording.active_file_stem = None
        self._status.recording.save_directory = None
        return SimpleNamespace(status=SimpleNamespace(frames_written=4), stop_reason=request.reason)

    def apply_configuration(self, request):
        self._status.configuration.gain = request.gain
        self._status.configuration.roi_width = request.roi_width
        return request

    def set_save_directory(self, request):
        selected_directory = request.resolve_directory()
        self._status.default_save_directory = selected_directory
        return SimpleNamespace(selected_directory=selected_directory)

    def save_snapshot(self, request):
        return SimpleNamespace(saved_path=Path("captures/wx_shell_snapshot") / f"{request.file_stem}{request.file_extension}")

    def get_status(self):
        return self._status


class _FailingApplyConfigurationController:
    def apply_configuration(self, request):
        raise RuntimeError("camera rejected roi")


if __name__ == "__main__":
    unittest.main()
