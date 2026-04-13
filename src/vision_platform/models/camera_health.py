from dataclasses import dataclass


@dataclass(slots=True)
class CameraHealth:
    availability: bool
    readiness: bool
    degraded: bool
    faulted: bool
    last_error: str | None = None
    capabilities_available: bool = False
    recording_impaired: bool | None = None

