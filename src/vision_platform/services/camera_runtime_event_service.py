from __future__ import annotations

from datetime import datetime, timezone

from vision_platform.models import (
    ApplyConfigurationCommandResult,
    ArtifactReference,
    CameraHealth,
    CameraRuntimeEvent,
    RecordingCommandResult,
    SnapshotCommandResult,
)


def build_configuration_applied_event(
    result: ApplyConfigurationCommandResult,
    *,
    occurred_utc: datetime | None = None,
) -> CameraRuntimeEvent:
    return CameraRuntimeEvent(
        event_kind="CameraConfigurationApplied",
        occurred_utc=occurred_utc or datetime.now(timezone.utc),
        details={"pixel_format": str(result.applied_configuration.pixel_format or "")},
    )


def build_snapshot_saved_event(
    result: SnapshotCommandResult,
    *,
    artifact_reference: ArtifactReference,
    occurred_utc: datetime | None = None,
) -> CameraRuntimeEvent:
    return CameraRuntimeEvent(
        event_kind="CameraSnapshotSaved",
        occurred_utc=occurred_utc or datetime.now(timezone.utc),
        artifact_reference=artifact_reference,
        details={"saved_path": str(result.saved_path)},
    )


def build_recording_started_event(
    result: RecordingCommandResult,
    *,
    occurred_utc: datetime | None = None,
) -> CameraRuntimeEvent:
    return CameraRuntimeEvent(
        event_kind="CameraRecordingStarted",
        occurred_utc=occurred_utc or datetime.now(timezone.utc),
        details={
            "run_id": result.status.run_id or "",
            "file_stem": result.status.active_file_stem or "",
        },
    )


def build_recording_stopped_event(
    result: RecordingCommandResult,
    *,
    occurred_utc: datetime | None = None,
) -> CameraRuntimeEvent:
    return CameraRuntimeEvent(
        event_kind="CameraRecordingStopped",
        occurred_utc=occurred_utc or datetime.now(timezone.utc),
        details={
            "run_id": result.status.run_id or "",
            "stop_reason": result.stop_reason or "",
        },
    )


def build_faulted_event(
    health: CameraHealth,
    *,
    occurred_utc: datetime | None = None,
) -> CameraRuntimeEvent | None:
    if not health.faulted:
        return None
    return CameraRuntimeEvent(
        event_kind="CameraFaulted",
        occurred_utc=occurred_utc or datetime.now(timezone.utc),
        health=health,
        details={"last_error": health.last_error or ""},
    )


def build_health_changed_event(
    previous: CameraHealth,
    current: CameraHealth,
    *,
    occurred_utc: datetime | None = None,
) -> CameraRuntimeEvent | None:
    if previous == current:
        return None
    return CameraRuntimeEvent(
        event_kind="CameraHealthChanged",
        occurred_utc=occurred_utc or datetime.now(timezone.utc),
        health=current,
        details={
            "previous_faulted": str(previous.faulted).lower(),
            "current_faulted": str(current.faulted).lower(),
            "previous_degraded": str(previous.degraded).lower(),
            "current_degraded": str(current.degraded).lower(),
        },
    )


__all__ = [
    "build_configuration_applied_event",
    "build_faulted_event",
    "build_health_changed_event",
    "build_recording_started_event",
    "build_recording_stopped_event",
    "build_snapshot_saved_event",
]
