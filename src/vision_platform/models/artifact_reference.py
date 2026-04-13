from dataclasses import dataclass
from pathlib import Path

from vision_platform.models.artifact_time_context import ArtifactTimeContext


@dataclass(frozen=True, slots=True)
class ArtifactReference:
    artifact_path: Path
    artifact_kind: str
    file_name: str
    run_id: str | None = None
    frame_id: int | None = None
    camera_id: str | None = None
    time_context: ArtifactTimeContext | None = None

