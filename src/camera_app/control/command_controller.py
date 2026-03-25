from pathlib import Path
from typing import Optional

from camera_app.models.camera_configuration import CameraConfiguration
from camera_app.models.snapshot_request import SnapshotRequest
from camera_app.models.recording_request import RecordingRequest
from camera_app.services.camera_service import CameraService
from camera_app.services.recording_service import RecordingService
from camera_app.services.snapshot_service import SnapshotService


class CommandController:
    def __init__(
        self,
        camera_service: CameraService,
        snapshot_service: SnapshotService,
        recording_service: RecordingService,
    ) -> None:
        self._camera_service = camera_service
        self._snapshot_service = snapshot_service
        self._recording_service = recording_service
        self._default_save_directory: Optional[Path] = None

    def apply_configuration(self, config: CameraConfiguration) -> None:
        self._camera_service.apply_configuration(config)

    def set_save_directory(self, path: Path) -> None:
        self._default_save_directory = path

    def save_snapshot(self, request: SnapshotRequest):
        return self._snapshot_service.save_snapshot(request)

    def start_recording(self, request: RecordingRequest):
        return self._recording_service.start_recording(request)

    def stop_recording(self):
        return self._recording_service.stop_recording()

    def get_status(self) -> dict:
        return {
            "recording": self._recording_service.get_status(),
            "default_save_directory": self._default_save_directory,
        }

