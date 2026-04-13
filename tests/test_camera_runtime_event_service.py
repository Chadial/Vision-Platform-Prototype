from datetime import datetime, timezone
from pathlib import Path
import unittest

from tests import _path_setup
from vision_platform.models import (
    ApplyConfigurationCommandResult,
    ArtifactReference,
    ArtifactTimeContext,
    CameraConfiguration,
    CameraHealth,
    RecordingCommandResult,
    RecordingStatus,
    SnapshotCommandResult,
)
from vision_platform.services.camera_runtime_event_service import (
    build_configuration_applied_event,
    build_faulted_event,
    build_health_changed_event,
    build_recording_started_event,
    build_recording_stopped_event,
    build_snapshot_saved_event,
)


class CameraRuntimeEventServiceTests(unittest.TestCase):
    def test_build_snapshot_saved_event_keeps_event_distinct_from_artifact_reference(self) -> None:
        occurred_utc = datetime(2026, 4, 14, 12, 0, tzinfo=timezone.utc)
        artifact_reference = ArtifactReference(
            artifact_path=Path("captures/image_001.png"),
            artifact_kind="snapshot",
            file_name="image_001.png",
            frame_id=7,
            time_context=ArtifactTimeContext(host_utc=occurred_utc.isoformat(), frame_id=7),
        )

        event = build_snapshot_saved_event(
            SnapshotCommandResult(saved_path=Path("captures/image_001.png")),
            artifact_reference=artifact_reference,
            occurred_utc=occurred_utc,
        )

        self.assertEqual(event.event_kind, "CameraSnapshotSaved")
        self.assertEqual(event.artifact_reference, artifact_reference)
        self.assertEqual(event.details["saved_path"], "captures\\image_001.png")

    def test_build_health_changed_event_only_emits_on_change(self) -> None:
        previous = CameraHealth(True, True, False, False, None, True, None)
        current = CameraHealth(True, True, True, False, "warning", False, None)

        self.assertIsNone(build_health_changed_event(previous, previous))

        event = build_health_changed_event(previous, current)

        self.assertIsNotNone(event)
        self.assertEqual(event.event_kind, "CameraHealthChanged")
        self.assertEqual(event.health, current)

    def test_build_faulted_event_requires_faulted_health(self) -> None:
        healthy = CameraHealth(True, True, False, False, None, True, None)
        self.assertIsNone(build_faulted_event(healthy))

        faulted = CameraHealth(True, False, False, True, "camera lost", True, None)
        event = build_faulted_event(faulted)

        self.assertIsNotNone(event)
        self.assertEqual(event.event_kind, "CameraFaulted")
        self.assertEqual(event.details["last_error"], "camera lost")

    def test_build_configuration_and_recording_events_are_narrow(self) -> None:
        config_event = build_configuration_applied_event(
            ApplyConfigurationCommandResult(CameraConfiguration(pixel_format="Mono8"))
        )
        self.assertEqual(config_event.event_kind, "CameraConfigurationApplied")

        started = build_recording_started_event(
            RecordingCommandResult(status=RecordingStatus(is_recording=True, run_id="run-1", active_file_stem="series"))
        )
        stopped = build_recording_stopped_event(
            RecordingCommandResult(
                status=RecordingStatus(is_recording=False, run_id="run-1"),
                stop_reason="operator",
            )
        )
        self.assertEqual(started.event_kind, "CameraRecordingStarted")
        self.assertEqual(stopped.event_kind, "CameraRecordingStopped")
        self.assertEqual(stopped.details["stop_reason"], "operator")


if __name__ == "__main__":
    unittest.main()
