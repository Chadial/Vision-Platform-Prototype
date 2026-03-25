from camera_app.models.recording_request import RecordingRequest
from camera_app.models.recording_status import RecordingStatus


class RecordingService:
    def __init__(self) -> None:
        self._status = RecordingStatus()

    def start_recording(self, request: RecordingRequest) -> RecordingStatus:
        self._status = RecordingStatus(
            is_recording=True,
            save_directory=request.save_directory,
            active_file_stem=request.file_stem,
        )
        return self._status

    def stop_recording(self) -> RecordingStatus:
        self._status.is_recording = False
        return self._status

    def get_status(self) -> RecordingStatus:
        return self._status

