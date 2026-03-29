from dataclasses import dataclass
from typing import Optional

from camera_app.models.recording_status import RecordingStatus


@dataclass(slots=True)
class RecordingCommandResult:
    status: RecordingStatus
    stop_reason: Optional[str] = None

    @classmethod
    def from_status(
        cls,
        status: RecordingStatus,
        stop_reason: Optional[str] = None,
    ) -> "RecordingCommandResult":
        return cls(status=status, stop_reason=stop_reason)
