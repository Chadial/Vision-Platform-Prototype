from dataclasses import dataclass
from typing import Optional

from camera_app.models.recording_status import RecordingStatus


@dataclass(slots=True)
class RecordingCommandResult:
    status: RecordingStatus
    stop_reason: Optional[str] = None
