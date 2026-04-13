from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from vision_platform.models.artifact_reference import ArtifactReference
from vision_platform.models.camera_health import CameraHealth


@dataclass(frozen=True, slots=True)
class CameraRuntimeEvent:
    event_kind: str
    occurred_utc: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    artifact_reference: ArtifactReference | None = None
    health: CameraHealth | None = None
    details: dict[str, str] = field(default_factory=dict)

