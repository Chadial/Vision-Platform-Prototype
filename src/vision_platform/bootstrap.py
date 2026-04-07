from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from camera_app.drivers.camera_driver import CameraDriver
from camera_app.drivers.simulated_camera_driver import SimulatedCameraDriver
from camera_app.services.camera_service import CameraService
from camera_app.services.camera_stream_service import CameraStreamService
from camera_app.services.interval_capture_service import IntervalCaptureService
from camera_app.services.recording_service import RecordingService
from camera_app.services.snapshot_service import SnapshotService
from vision_platform.control import CommandController
from vision_platform.libraries.common_models import FocusMethod
from vision_platform.services.hardware_audit_service import HardwareAuditService
from vision_platform.services.recording_service.artifact_focus_metadata_producer import ArtifactFocusMetadataProducer


@dataclass(slots=True)
class CameraSubsystem:
    driver: CameraDriver
    camera_service: CameraService
    snapshot_service: SnapshotService
    stream_service: CameraStreamService
    recording_service: RecordingService
    interval_capture_service: IntervalCaptureService
    command_controller: CommandController
    hardware_audit_service: HardwareAuditService | None = None


def build_camera_subsystem(
    driver: CameraDriver,
    preview_poll_interval_seconds: float = 0.05,
    shared_poll_interval_seconds: float = 0.01,
    recording_poll_interval_seconds: float = 0.01,
    interval_capture_poll_interval_seconds: float = 0.01,
    artifact_focus_method: FocusMethod | None = None,
    focus_score_frame_interval: int | None = None,
    hardware_audit_log_directory: Path | None = Path("captures/hardware_audit"),
) -> CameraSubsystem:
    hardware_audit_service = (
        HardwareAuditService(hardware_audit_log_directory / "hardware_audit.jsonl")
        if hardware_audit_log_directory is not None
        else None
    )
    camera_service = CameraService(driver, hardware_audit_service=hardware_audit_service)
    stream_service = CameraStreamService(
        driver,
        preview_poll_interval_seconds=preview_poll_interval_seconds,
        shared_poll_interval_seconds=shared_poll_interval_seconds,
    )
    roi_state_service = stream_service.get_roi_state_service()
    snapshot_focus_metadata_producer = (
        ArtifactFocusMetadataProducer(
            focus_method=artifact_focus_method,
            focus_score_frame_interval=focus_score_frame_interval,
            roi_state_service=roi_state_service,
        )
        if artifact_focus_method is not None
        else None
    )
    recording_focus_metadata_producer = (
        ArtifactFocusMetadataProducer(
            focus_method=artifact_focus_method,
            focus_score_frame_interval=focus_score_frame_interval,
            roi_state_service=roi_state_service,
        )
        if artifact_focus_method is not None
        else None
    )
    snapshot_service = SnapshotService(
        driver,
        configuration_provider=camera_service.get_last_configuration,
        artifact_focus_metadata_producer=snapshot_focus_metadata_producer,
    )
    recording_service = stream_service.create_recording_service(
        poll_interval_seconds=recording_poll_interval_seconds,
        configuration_provider=camera_service.get_last_configuration,
        artifact_focus_metadata_producer=recording_focus_metadata_producer,
    )
    interval_capture_service = stream_service.create_interval_capture_service(
        poll_interval_seconds=interval_capture_poll_interval_seconds,
    )
    command_controller = CommandController(
        camera_service,
        snapshot_service,
        recording_service,
        interval_capture_service,
        hardware_audit_service=hardware_audit_service,
    )
    return CameraSubsystem(
        driver=driver,
        camera_service=camera_service,
        snapshot_service=snapshot_service,
        stream_service=stream_service,
        recording_service=recording_service,
        interval_capture_service=interval_capture_service,
        command_controller=command_controller,
        hardware_audit_service=hardware_audit_service,
    )


def build_simulated_camera_subsystem(
    sample_image_paths: Sequence[Path] | None = None,
    preview_poll_interval_seconds: float = 0.001,
    shared_poll_interval_seconds: float = 0.001,
    recording_poll_interval_seconds: float = 0.001,
    interval_capture_poll_interval_seconds: float = 0.001,
    artifact_focus_method: FocusMethod | None = None,
    focus_score_frame_interval: int | None = None,
    hardware_audit_log_directory: Path | None = Path("captures/hardware_audit"),
) -> CameraSubsystem:
    driver = SimulatedCameraDriver(sample_image_paths=sample_image_paths or [])
    return build_camera_subsystem(
        driver,
        preview_poll_interval_seconds=preview_poll_interval_seconds,
        shared_poll_interval_seconds=shared_poll_interval_seconds,
        recording_poll_interval_seconds=recording_poll_interval_seconds,
        interval_capture_poll_interval_seconds=interval_capture_poll_interval_seconds,
        artifact_focus_method=artifact_focus_method,
        focus_score_frame_interval=focus_score_frame_interval,
        hardware_audit_log_directory=hardware_audit_log_directory,
    )


__all__ = ["CameraSubsystem", "build_camera_subsystem", "build_simulated_camera_subsystem"]
