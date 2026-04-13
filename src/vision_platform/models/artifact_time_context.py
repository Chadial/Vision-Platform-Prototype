from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ArtifactTimeContext:
    device_timestamp: str | None = None
    host_utc: str | None = None
    host_monotonic: float | None = None
    frame_id: int | None = None
    time_source: str | None = None
    time_quality: str | None = None

