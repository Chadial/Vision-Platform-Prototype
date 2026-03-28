from dataclasses import dataclass

from camera_app.models.recording_status import RecordingStatus


@dataclass(slots=True)
class RecordingCommandResult:
    status: RecordingStatus
