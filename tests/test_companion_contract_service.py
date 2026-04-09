import unittest

from vision_platform.services.companion_contract_service import (
    build_companion_command_result,
    build_companion_status_snapshot,
    build_failed_companion_command_result,
)


class CompanionContractServiceTests(unittest.TestCase):
    def test_build_companion_command_result_keeps_expected_headless_payload_shape(self) -> None:
        payload = build_companion_command_result(
            command_name="save_snapshot",
            reflection_kind="snapshot",
            reflection={"phase": "saved", "file_name": "geometry_000001.bmp"},
            failure_reflection=None,
            result={"saved_path": "captures/geometry/geometry_000001.bmp"},
        )

        self.assertEqual(
            payload,
            {
                "command": "save_snapshot",
                "reflection_kind": "snapshot",
                "reflection": {"phase": "saved", "file_name": "geometry_000001.bmp"},
                "failure_reflection": None,
                "result": {"saved_path": "captures/geometry/geometry_000001.bmp"},
            },
        )

    def test_build_failed_companion_command_result_keeps_placeholder_shape(self) -> None:
        payload = build_failed_companion_command_result(
            command_name="apply_configuration",
            failure_reflection={
                "phase": "failed",
                "source": "setup",
                "action": "apply_configuration",
                "message": "camera rejected roi",
                "external": True,
            },
        )

        self.assertEqual(payload["command"], "apply_configuration")
        self.assertIsNone(payload["reflection_kind"])
        self.assertIsNone(payload["reflection"])
        self.assertIsNone(payload["result"])
        self.assertEqual(payload["failure_reflection"]["source"], "setup")

    def test_build_companion_status_snapshot_keeps_expected_headless_payload_shape(self) -> None:
        payload = build_companion_status_snapshot(
            session_id="session-123",
            source="hardware",
            camera_id="DEV_123",
            configuration_profile_id="default",
            focus_summary="1.234e-02",
            setup_reflection={"phase": "ready", "roi_active": True},
            failure_reflection=None,
            snapshot_reflection={"phase": "saved", "file_name": "geometry_000001.bmp"},
            recording_summary="4/4",
            recording_reflection={"phase": "idle", "stop_category": "max_frames_reached"},
            status_lines=["source=hardware | preview=running", "FPS 25.0"],
            status={"default_save_directory": "captures/run"},
        )

        self.assertEqual(payload["session_id"], "session-123")
        self.assertEqual(payload["source"], "hardware")
        self.assertEqual(payload["camera_id"], "DEV_123")
        self.assertEqual(payload["focus_summary"], "1.234e-02")
        self.assertEqual(payload["setup_reflection"]["phase"], "ready")
        self.assertEqual(payload["snapshot_reflection"]["file_name"], "geometry_000001.bmp")
        self.assertEqual(payload["recording_reflection"]["stop_category"], "max_frames_reached")
        self.assertEqual(payload["status_lines"][0], "source=hardware | preview=running")


if __name__ == "__main__":
    unittest.main()
