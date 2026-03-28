from dataclasses import dataclass

from camera_app.models.interval_capture_status import IntervalCaptureStatus


@dataclass(slots=True)
class IntervalCaptureCommandResult:
    status: IntervalCaptureStatus
