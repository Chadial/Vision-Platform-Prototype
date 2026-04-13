from __future__ import annotations

from pathlib import Path

from vision_platform.models import ArtifactReference, ArtifactTimeContext, CapturedFrame
from vision_platform.services.recording_service.traceability import TraceArtifactRow


def build_time_context_from_captured_frame(
    frame: CapturedFrame,
    *,
    host_monotonic: float | None = None,
    time_source: str | None = None,
    time_quality: str | None = None,
) -> ArtifactTimeContext:
    return ArtifactTimeContext(
        device_timestamp=None if frame.camera_timestamp is None else str(frame.camera_timestamp),
        host_utc=frame.timestamp_utc.isoformat(),
        host_monotonic=host_monotonic,
        frame_id=frame.frame_id,
        time_source=time_source,
        time_quality=time_quality,
    )


def build_artifact_reference(
    *,
    artifact_path: Path,
    artifact_kind: str,
    file_name: str | None = None,
    run_id: str | None = None,
    frame_id: int | None = None,
    camera_id: str | None = None,
    time_context: ArtifactTimeContext | None = None,
) -> ArtifactReference:
    return ArtifactReference(
        artifact_path=artifact_path,
        artifact_kind=artifact_kind,
        file_name=file_name or artifact_path.name,
        run_id=run_id,
        frame_id=frame_id,
        camera_id=camera_id,
        time_context=time_context,
    )


def build_artifact_reference_from_trace_row(
    *,
    save_directory: Path,
    row: TraceArtifactRow,
    camera_id: str | None = None,
) -> ArtifactReference:
    parsed_frame_id = int(row.frame_id) if row.frame_id else None
    return ArtifactReference(
        artifact_path=save_directory / row.image_name,
        artifact_kind=row.artifact_kind,
        file_name=row.image_name,
        run_id=row.run_id or None,
        frame_id=parsed_frame_id,
        camera_id=camera_id,
        time_context=ArtifactTimeContext(
            device_timestamp=row.camera_timestamp,
            host_utc=row.system_timestamp_utc,
            frame_id=parsed_frame_id,
        ),
    )


__all__ = [
    "build_artifact_reference",
    "build_artifact_reference_from_trace_row",
    "build_time_context_from_captured_frame",
]
