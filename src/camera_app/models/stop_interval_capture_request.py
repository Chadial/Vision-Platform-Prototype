from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class StopIntervalCaptureRequest:
    reason: Optional[str] = None
