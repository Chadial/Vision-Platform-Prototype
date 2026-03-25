from dataclasses import replace
from pathlib import Path
from typing import Optional

from camera_app.models.apply_configuration_request import ApplyConfigurationRequest
from camera_app.models.camera_configuration import CameraConfiguration
from camera_app.models.recording_request import RecordingRequest
from camera_app.models.save_snapshot_request import SaveSnapshotRequest
from camera_app.models.snapshot_request import SnapshotRequest
from camera_app.models.start_recording_request import StartRecordingRequest
from camera_app.models.stop_recording_request import StopRecordingRequest
from camera_app.models.set_save_directory_request import SetSaveDirectoryRequest
from camera_app.models.subsystem_status import SubsystemStatus
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

    def apply_configuration(self, config: CameraConfiguration | ApplyConfigurationRequest) -> None:
        if isinstance(config, ApplyConfigurationRequest):
            config = config.to_camera_configuration()
        self._validate_configuration(config)
        self._camera_service.apply_configuration(config)

    def set_save_directory(self, path: Optional[Path] | SetSaveDirectoryRequest) -> None:
        if isinstance(path, SetSaveDirectoryRequest):
            path = path.resolve_directory()
        self._default_save_directory = path

    def save_snapshot(self, request: SnapshotRequest | SaveSnapshotRequest):
        if isinstance(request, SaveSnapshotRequest):
            request = request.to_snapshot_request()
        return self._snapshot_service.save_snapshot(self._resolve_snapshot_request(request))

    def start_recording(self, request: RecordingRequest | StartRecordingRequest):
        if isinstance(request, StartRecordingRequest):
            request = request.to_recording_request()
        return self._recording_service.start_recording(self._resolve_recording_request(request))

    def stop_recording(self, request: StopRecordingRequest | None = None):
        return self._recording_service.stop_recording()

    def get_status(self) -> SubsystemStatus:
        camera_status = self._camera_service.get_status()
        configuration = self._camera_service.get_last_configuration()
        recording_status = self._recording_service.get_status()
        can_save_to_disk = camera_status.is_initialized and self._default_save_directory is not None

        return SubsystemStatus(
            camera=camera_status,
            configuration=configuration,
            recording=recording_status,
            default_save_directory=self._default_save_directory,
            can_apply_configuration=camera_status.is_initialized,
            can_save_snapshot=can_save_to_disk,
            can_start_recording=can_save_to_disk and not recording_status.is_recording,
            can_stop_recording=recording_status.is_recording,
        )

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

    @staticmethod
    def _validate_configuration(config: CameraConfiguration) -> None:
        if config.exposure_time_us is not None and config.exposure_time_us <= 0:
            raise ValueError("CameraConfiguration.exposure_time_us must be greater than zero.")
        for name, value in (
            ("roi_offset_x", config.roi_offset_x),
            ("roi_offset_y", config.roi_offset_y),
            ("roi_width", config.roi_width),
            ("roi_height", config.roi_height),
        ):
            if value is not None and value < 0:
                raise ValueError(f"CameraConfiguration.{name} must be zero or greater.")
        for name, value in (("roi_width", config.roi_width), ("roi_height", config.roi_height)):
            if value == 0:
                raise ValueError(f"CameraConfiguration.{name} must be greater than zero when provided.")
