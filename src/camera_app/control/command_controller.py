from dataclasses import replace
from pathlib import Path
from typing import Optional

from camera_app.models.camera_configuration import CameraConfiguration
from camera_app.models.recording_request import RecordingRequest
from camera_app.models.snapshot_request import SnapshotRequest
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
        return self._snapshot_service.save_snapshot(self._resolve_snapshot_request(request))

    def start_recording(self, request: RecordingRequest):
        return self._recording_service.start_recording(self._resolve_recording_request(request))

    def stop_recording(self):
        return self._recording_service.stop_recording()

    def get_status(self) -> dict:
        return {
            "camera": self._camera_service.get_status(),
            "configuration": self._camera_service.get_last_configuration(),
            "recording": self._recording_service.get_status(),
            "default_save_directory": self._default_save_directory,
        }

    def _resolve_snapshot_request(self, request: SnapshotRequest) -> SnapshotRequest:
        resolved_save_directory = request.save_directory or self._default_save_directory
        if resolved_save_directory is None:
            raise ValueError("SnapshotRequest.save_directory is not set and no default save directory is configured.")
        return replace(request, save_directory=resolved_save_directory)

    def _resolve_recording_request(self, request: RecordingRequest) -> RecordingRequest:
        resolved_save_directory = request.save_directory or self._default_save_directory
        if resolved_save_directory is None:
            raise ValueError("RecordingRequest.save_directory is not set and no default save directory is configured.")
        return replace(request, save_directory=resolved_save_directory)
