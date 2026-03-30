from __future__ import annotations

from dataclasses import dataclass

from vision_platform.models import SubsystemStatus


@dataclass(slots=True)
class ApiCameraStatusPayload:
    is_initialized: bool
    is_acquiring: bool
    source_kind: str | None
    driver_name: str | None
    camera_id: str | None
    camera_name: str | None
    camera_model: str | None
    camera_serial: str | None
    interface_id: str | None
    reported_acquisition_frame_rate: float | None
    acquisition_frame_rate_enabled: bool | None
    capabilities_available: bool
    capability_probe_error: str | None
    last_error: str | None


@dataclass(slots=True)
class ApiCameraConfigurationPayload:
    exposure_time_us: float | None
    gain: float | None
    pixel_format: str | None
    acquisition_frame_rate: float | None
    roi_offset_x: int | None
    roi_offset_y: int | None
    roi_width: int | None
    roi_height: int | None


@dataclass(slots=True)
class ApiRecordingStatusPayload:
    is_recording: bool
    frames_written: int
    dropped_frames: int
    save_directory: str | None
    active_file_stem: str | None
    last_error: str | None


@dataclass(slots=True)
class ApiIntervalCaptureStatusPayload:
    is_capturing: bool
    frames_written: int
    skipped_intervals: int
    save_directory: str | None
    active_file_stem: str | None
    last_error: str | None


@dataclass(slots=True)
class ApiActiveRunStatusPayload:
    operation_kind: str
    save_directory: str | None
    active_file_stem: str | None
    frames_written: int
    last_error: str | None


@dataclass(slots=True)
class ApiSubsystemStatusPayload:
    camera: ApiCameraStatusPayload
    configuration: ApiCameraConfigurationPayload | None
    recording: ApiRecordingStatusPayload
    interval_capture: ApiIntervalCaptureStatusPayload
    active_run: ApiActiveRunStatusPayload | None
    default_save_directory: str | None
    is_save_directory_configured: bool
    has_interval_capture_service: bool
    can_apply_configuration: bool
    can_save_snapshot: bool
    can_start_recording: bool
    can_stop_recording: bool
    can_start_interval_capture: bool
    can_stop_interval_capture: bool


def map_subsystem_status_to_api_payload(status: SubsystemStatus) -> ApiSubsystemStatusPayload:
    """Map host-neutral subsystem status into transport-neutral API adapter payloads."""

    configuration = status.configuration
    return ApiSubsystemStatusPayload(
        camera=ApiCameraStatusPayload(
            is_initialized=status.camera.is_initialized,
            is_acquiring=status.camera.is_acquiring,
            source_kind=status.camera.source_kind,
            driver_name=status.camera.driver_name,
            camera_id=status.camera.camera_id,
            camera_name=status.camera.camera_name,
            camera_model=status.camera.camera_model,
            camera_serial=status.camera.camera_serial,
            interface_id=status.camera.interface_id,
            reported_acquisition_frame_rate=status.camera.reported_acquisition_frame_rate,
            acquisition_frame_rate_enabled=status.camera.acquisition_frame_rate_enabled,
            capabilities_available=status.camera.capabilities_available,
            capability_probe_error=status.camera.capability_probe_error,
            last_error=status.camera.last_error,
        ),
        configuration=(
            ApiCameraConfigurationPayload(
                exposure_time_us=configuration.exposure_time_us,
                gain=configuration.gain,
                pixel_format=configuration.pixel_format,
                acquisition_frame_rate=configuration.acquisition_frame_rate,
                roi_offset_x=configuration.roi_offset_x,
                roi_offset_y=configuration.roi_offset_y,
                roi_width=configuration.roi_width,
                roi_height=configuration.roi_height,
            )
            if configuration is not None
            else None
        ),
        recording=ApiRecordingStatusPayload(
            is_recording=status.recording.is_recording,
            frames_written=status.recording.frames_written,
            dropped_frames=status.recording.dropped_frames,
            save_directory=_stringify_path(status.recording.save_directory),
            active_file_stem=status.recording.active_file_stem,
            last_error=status.recording.last_error,
        ),
        interval_capture=ApiIntervalCaptureStatusPayload(
            is_capturing=status.interval_capture.is_capturing,
            frames_written=status.interval_capture.frames_written,
            skipped_intervals=status.interval_capture.skipped_intervals,
            save_directory=_stringify_path(status.interval_capture.save_directory),
            active_file_stem=status.interval_capture.active_file_stem,
            last_error=status.interval_capture.last_error,
        ),
        active_run=_map_active_run_status(status),
        default_save_directory=_stringify_path(status.default_save_directory),
        is_save_directory_configured=status.is_save_directory_configured,
        has_interval_capture_service=status.has_interval_capture_service,
        can_apply_configuration=status.can_apply_configuration,
        can_save_snapshot=status.can_save_snapshot,
        can_start_recording=status.can_start_recording,
        can_stop_recording=status.can_stop_recording,
        can_start_interval_capture=status.can_start_interval_capture,
        can_stop_interval_capture=status.can_stop_interval_capture,
    )


def _stringify_path(path) -> str | None:
    if path is None:
        return None
    return str(path)


def _map_active_run_status(status: SubsystemStatus) -> ApiActiveRunStatusPayload | None:
    recording = status.recording
    if recording.is_recording:
        return ApiActiveRunStatusPayload(
            operation_kind="recording",
            save_directory=_stringify_path(recording.save_directory),
            active_file_stem=recording.active_file_stem,
            frames_written=recording.frames_written,
            last_error=recording.last_error,
        )

    interval_capture = status.interval_capture
    if interval_capture.is_capturing:
        return ApiActiveRunStatusPayload(
            operation_kind="interval_capture",
            save_directory=_stringify_path(interval_capture.save_directory),
            active_file_stem=interval_capture.active_file_stem,
            frames_written=interval_capture.frames_written,
            last_error=interval_capture.last_error,
        )

    return None
