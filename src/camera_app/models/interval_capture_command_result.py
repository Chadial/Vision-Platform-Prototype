from dataclasses import dataclass
from typing import Optional

from camera_app.models.interval_capture_status import IntervalCaptureStatus


@dataclass(slots=True)
class IntervalCaptureCommandResult:
    status: IntervalCaptureStatus
    stop_reason: Optional[str] = None

    @classmethod
    def from_status(
        cls,
        status: IntervalCaptureStatus,
        stop_reason: Optional[str] = None,
    ) -> "IntervalCaptureCommandResult":
        return cls(status=status, stop_reason=stop_reason)
