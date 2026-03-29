from dataclasses import replace
from pathlib import Path
from typing import Optional

from camera_app.services.camera_service import CameraService
from camera_app.services.interval_capture_service import IntervalCaptureService
from camera_app.services.recording_service import RecordingService
from camera_app.services.snapshot_service import SnapshotService
from camera_app.validation.request_validation import (
    validate_camera_configuration,
    validate_interval_capture_request,
    validate_recording_request,
    validate_save_directory_request,
    validate_snapshot_request,
)
from vision_platform.models import (
    ApplyConfigurationCommandResult,
    ApplyConfigurationRequest,
    CameraCapabilityProfile,
    CameraConfiguration,
    IntervalCaptureCommandResult,
    IntervalCaptureRequest,
    IntervalCaptureStatus,
    RecordingCommandResult,
    RecordingRequest,
    RecordingStatus,
    SaveDirectoryCommandResult,
    SaveSnapshotRequest,
    SnapshotCommandResult,
    SetSaveDirectoryRequest,
    SnapshotRequest,
    StartIntervalCaptureRequest,
    StartRecordingRequest,
    StopIntervalCaptureRequest,
    StopRecordingRequest,
    SubsystemStatus,
)
from vision_platform.services.camera_configuration_validation_service import CameraConfigurationValidationService


class CommandController:
    def __init__(
        self,
        camera_service: CameraService,
        snapshot_service: SnapshotService,
        recording_service: RecordingService,
        interval_capture_service: IntervalCaptureService | None = None,
        capability_profile: CameraCapabilityProfile | None = None,
        configuration_validation_service: CameraConfigurationValidationService | None = None,
    ) -> None:
        self._camera_service = camera_service
        self._snapshot_service = snapshot_service
        self._recording_service = recording_service
        self._interval_capture_service = interval_capture_service
        self._default_save_directory: Optional[Path] = None
        self._capability_profile = capability_profile
        self._configuration_validation_service = configuration_validation_service or CameraConfigurationValidationService()

    def apply_configuration(
        self,
        config: CameraConfiguration | ApplyConfigurationRequest,
    ) -> ApplyConfigurationCommandResult:
        if isinstance(config, ApplyConfigurationRequest):
            config = config.to_camera_configuration()
        self._require_initialized_camera("apply configuration")
        validate_camera_configuration(config)
        self._configuration_validation_service.validate(config, self._get_effective_capability_profile())
        self._camera_service.apply_configuration(config)
        return ApplyConfigurationCommandResult(applied_configuration=config)

    def set_capability_profile(self, capability_profile: CameraCapabilityProfile | None) -> None:
        self._capability_profile = capability_profile

    def set_save_directory(self, path: Optional[Path] | SetSaveDirectoryRequest) -> SaveDirectoryCommandResult:
        if isinstance(path, SetSaveDirectoryRequest):
            validate_save_directory_request(path)
            path = path.resolve_directory()
        self._default_save_directory = path
        return SaveDirectoryCommandResult(selected_directory=path, was_cleared=path is None)

    def save_snapshot(self, request: SnapshotRequest | SaveSnapshotRequest) -> SnapshotCommandResult:
        if isinstance(request, SaveSnapshotRequest):
            request = request.to_snapshot_request()
        self._require_initialized_camera("save a snapshot")
        validate_snapshot_request(request)
        saved_path = self._snapshot_service.save_snapshot(self._resolve_snapshot_request(request))
        return SnapshotCommandResult(saved_path=saved_path)

    def start_recording(self, request: RecordingRequest | StartRecordingRequest) -> RecordingCommandResult:
        if isinstance(request, StartRecordingRequest):
            request = request.to_recording_request()
        self._require_initialized_camera("start recording")
        validate_recording_request(request)
        status = self._recording_service.start_recording(self._resolve_recording_request(request))
        return RecordingCommandResult(status=status)

    def stop_recording(self, request: StopRecordingRequest | None = None) -> RecordingCommandResult:
        stop_request = request or StopRecordingRequest()
        return RecordingCommandResult(
            status=self._recording_service.stop_recording(),
            stop_reason=stop_request.reason,
        )

    def start_interval_capture(
        self,
        request: IntervalCaptureRequest | StartIntervalCaptureRequest,
    ) -> IntervalCaptureCommandResult:
        if self._interval_capture_service is None:
            raise RuntimeError("Interval capture service is not configured.")
        if isinstance(request, StartIntervalCaptureRequest):
            request = request.to_interval_capture_request()
        self._require_initialized_camera("start interval capture")
        validate_interval_capture_request(request)
        status = self._interval_capture_service.start_capture(self._resolve_interval_capture_request(request))
        return IntervalCaptureCommandResult(status=status)

    def stop_interval_capture(
        self,
        request: StopIntervalCaptureRequest | None = None,
    ) -> IntervalCaptureCommandResult:
        if self._interval_capture_service is None:
            raise RuntimeError("Interval capture service is not configured.")
        stop_request = request or StopIntervalCaptureRequest()
        return IntervalCaptureCommandResult(
            status=self._interval_capture_service.stop_capture(),
            stop_reason=stop_request.reason,
        )

    def get_status(self) -> SubsystemStatus:
        camera_status = self._camera_service.get_status()
        configuration = self._camera_service.get_last_configuration()
        recording_status = self._recording_service.get_status()
        has_interval_capture_service = self._interval_capture_service is not None
        interval_capture_status = (
            self._interval_capture_service.get_status()
            if has_interval_capture_service
            else IntervalCaptureStatus()
        )
        is_save_directory_configured = self._default_save_directory is not None
        can_save_to_disk = camera_status.is_initialized and is_save_directory_configured

        return SubsystemStatus(
            camera=camera_status,
            configuration=configuration,
            recording=recording_status,
            interval_capture=interval_capture_status,
            default_save_directory=self._default_save_directory,
            is_save_directory_configured=is_save_directory_configured,
            has_interval_capture_service=has_interval_capture_service,
            can_apply_configuration=camera_status.is_initialized,
            can_save_snapshot=can_save_to_disk,
            can_start_recording=can_save_to_disk and not recording_status.is_recording,
            can_stop_recording=recording_status.is_recording,
            can_start_interval_capture=(
                can_save_to_disk
                and has_interval_capture_service
                and not interval_capture_status.is_capturing
            ),
            can_stop_interval_capture=interval_capture_status.is_capturing,
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

    def _resolve_interval_capture_request(self, request: IntervalCaptureRequest) -> IntervalCaptureRequest:
        resolved_save_directory = request.save_directory or self._default_save_directory
        if resolved_save_directory is None:
            raise ValueError(
                "IntervalCaptureRequest.save_directory is not set and no default save directory is configured."
            )
        return replace(request, save_directory=resolved_save_directory)

    def _require_initialized_camera(self, action: str) -> None:
        camera_status = self._camera_service.get_status()
        if not camera_status.is_initialized:
            raise RuntimeError(f"Cannot {action} because the camera is not initialized.")

    def _get_effective_capability_profile(self) -> CameraCapabilityProfile | None:
        if self._capability_profile is not None:
            return self._capability_profile
        capability_profile = self._camera_service.get_capability_profile()
        if isinstance(capability_profile, CameraCapabilityProfile):
            return capability_profile
        return None


__all__ = ["CommandController"]
