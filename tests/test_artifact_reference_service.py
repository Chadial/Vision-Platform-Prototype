from datetime import datetime, timezone
from pathlib import Path
import unittest

from tests import _path_setup
from vision_platform.models import CapturedFrame
from vision_platform.services.artifact_reference_service import (
    build_artifact_reference,
    build_artifact_reference_from_trace_row,
    build_time_context_from_captured_frame,
)
from vision_platform.services.recording_service.traceability import TraceArtifactMetadata, TraceArtifactRow


class ArtifactReferenceServiceTests(unittest.TestCase):
    def test_build_artifact_reference_keeps_optional_fields_optional(self) -> None:
        reference = build_artifact_reference(
            artifact_path=Path("captures/image_001.png"),
            artifact_kind="snapshot",
        )

        self.assertEqual(reference.file_name, "image_001.png")
        self.assertIsNone(reference.run_id)
        self.assertIsNone(reference.frame_id)
        self.assertIsNone(reference.camera_id)

    def test_build_time_context_from_captured_frame_keeps_minimal_baseline(self) -> None:
        frame = CapturedFrame(
            raw_frame=b"\x00",
            width=1,
            height=1,
            frame_id=7,
            camera_timestamp=123456,
            timestamp_utc=datetime(2026, 4, 14, 12, 0, tzinfo=timezone.utc),
        )

        time_context = build_time_context_from_captured_frame(frame, host_monotonic=42.5, time_source="camera+host")

        self.assertEqual(time_context.device_timestamp, "123456")
        self.assertEqual(time_context.host_utc, "2026-04-14T12:00:00+00:00")
        self.assertEqual(time_context.host_monotonic, 42.5)
        self.assertEqual(time_context.frame_id, 7)
        self.assertEqual(time_context.time_source, "camera+host")

    def test_build_artifact_reference_from_trace_row_uses_traceability_as_source_material_only(self) -> None:
        row = TraceArtifactRow(
            artifact_kind="snapshot",
            run_id="run-1",
            image_name="image_001.png",
            frame_id="7",
            camera_timestamp="123456",
            system_timestamp_utc="2026-04-14T12:00:00+00:00",
            metadata=TraceArtifactMetadata(),
        )

        reference = build_artifact_reference_from_trace_row(
            save_directory=Path("captures"),
            row=row,
            camera_id="CAM-001",
        )

        self.assertEqual(reference.artifact_path, Path("captures/image_001.png"))
        self.assertEqual(reference.run_id, "run-1")
        self.assertEqual(reference.frame_id, 7)
        self.assertEqual(reference.camera_id, "CAM-001")
        self.assertEqual(reference.time_context.host_utc, "2026-04-14T12:00:00+00:00")


if __name__ == "__main__":
    unittest.main()
