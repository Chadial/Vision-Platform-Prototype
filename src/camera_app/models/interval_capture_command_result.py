from dataclasses import dataclass
from typing import Optional

from camera_app.models.interval_capture_status import IntervalCaptureStatus


@dataclass(slots=True)
class IntervalCaptureCommandResult:
    status: IntervalCaptureStatus
    stop_reason: Optional[str] = None
