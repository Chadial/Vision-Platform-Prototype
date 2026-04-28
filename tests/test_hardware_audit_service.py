import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tests import _path_setup
from vision_platform.models import CameraStatus
from vision_platform.models import IntervalCaptureStatus
from vision_platform.models import RecordingStatus
from vision_platform.models import SubsystemStatus
from vision_platform.services.hardware_audit_service import HardwareAuditService


class HardwareAuditServiceTests(unittest.TestCase):
    def test_records_degraded_camera_status_once(self) -> None:
        with TemporaryDirectory() as temp_dir:
            audit_path = Path(temp_dir) / "hardware_audit.jsonl"
            service = HardwareAuditService(audit_path)
            status = CameraStatus(
                is_initialized=True,
                source_kind="hardware",
                camera_id="DEV_1AB22C046D81",
                camera_serial="067WH",
                capability_probe_error="Non-blocking hardware startup warning during capability probe.",
            )

            self.assertTrue(service.record_camera_status(stage="camera.initialize", status=status))
            self.assertFalse(service.record_camera_status(stage="camera.initialize", status=status))

            lines = audit_path.read_text(encoding="utf-8").splitlines()
            payload = json.loads(lines[0])
            self.assertEqual(len(lines), 1)
            self.assertEqual(payload["severity"], "warning")
            self.assertEqual(payload["event"], "capability_probe_warning")
            self.assertEqual(payload["camera_id"], "DEV_1AB22C046D81")
            self.assertIn("capability_probe_error", payload["details"])

    def test_records_recording_status_incident(self) -> None:
        with TemporaryDirectory() as temp_dir:
            audit_path = Path(temp_dir) / "hardware_audit.jsonl"
            service = HardwareAuditService(audit_path)
            status = SubsystemStatus(
                camera=CameraStatus(
                    is_initialized=True,
                    source_kind="hardware",
                    camera_id="DEV_1",
                    capabilities_available=True,
                ),
                recording=RecordingStatus(last_error="writer failed"),
                interval_capture=IntervalCaptureStatus(),
            )

            self.assertTrue(service.record_subsystem_status(stage="controller.get_status", status=status))

            lines = audit_path.read_text(encoding="utf-8").splitlines()
            payload = json.loads(lines[0])
            self.assertEqual(payload["severity"], "error")
            self.assertEqual(payload["event"], "recording_error")
            self.assertEqual(payload["category"], "subsystem")
            self.assertEqual(payload["camera_id"], "DEV_1")
            self.assertEqual(payload["details"]["recording_last_error"], "writer failed")


if __name__ == "__main__":
    unittest.main()
