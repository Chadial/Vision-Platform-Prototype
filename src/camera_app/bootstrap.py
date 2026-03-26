from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from camera_app.control.command_controller import CommandController
from camera_app.drivers.camera_driver import CameraDriver
from camera_app.drivers.simulated_camera_driver import SimulatedCameraDriver
from camera_app.services.camera_service import CameraService
from camera_app.services.camera_stream_service import CameraStreamService
from camera_app.services.interval_capture_service import IntervalCaptureService
from camera_app.services.recording_service import RecordingService
from camera_app.services.snapshot_service import SnapshotService


@dataclass(slots=True)
class CameraSubsystem:
    driver: CameraDriver
    camera_service: CameraService
    snapshot_service: SnapshotService
    stream_service: CameraStreamService
    recording_service: RecordingService
    interval_capture_service: IntervalCaptureService
    command_controller: CommandController


def build_camera_subsystem(
    driver: CameraDriver,
    preview_poll_interval_seconds: float = 0.05,
    shared_poll_interval_seconds: float = 0.01,
    recording_poll_interval_seconds: float = 0.01,
    interval_capture_poll_interval_seconds: float = 0.01,
) -> CameraSubsystem:
    camera_service = CameraService(driver)
    snapshot_service = SnapshotService(driver)
    stream_service = CameraStreamService(
        driver,
        preview_poll_interval_seconds=preview_poll_interval_seconds,
        shared_poll_interval_seconds=shared_poll_interval_seconds,
    )
    recording_service = stream_service.create_recording_service(
        poll_interval_seconds=recording_poll_interval_seconds,
        configuration_provider=camera_service.get_last_configuration,
    )
    interval_capture_service = stream_service.create_interval_capture_service(
        poll_interval_seconds=interval_capture_poll_interval_seconds,
    )
    command_controller = CommandController(
        camera_service,
        snapshot_service,
        recording_service,
        interval_capture_service,
    )
    return CameraSubsystem(
        driver=driver,
        camera_service=camera_service,
        snapshot_service=snapshot_service,
        stream_service=stream_service,
        recording_service=recording_service,
        interval_capture_service=interval_capture_service,
        command_controller=command_controller,
    )


def build_simulated_camera_subsystem(
    sample_image_paths: Sequence[Path] | None = None,
    preview_poll_interval_seconds: float = 0.001,
    shared_poll_interval_seconds: float = 0.001,
    recording_poll_interval_seconds: float = 0.001,
    interval_capture_poll_interval_seconds: float = 0.001,
) -> CameraSubsystem:
    driver = SimulatedCameraDriver(sample_image_paths=sample_image_paths or [])
    return build_camera_subsystem(
        driver,
        preview_poll_interval_seconds=preview_poll_interval_seconds,
        shared_poll_interval_seconds=shared_poll_interval_seconds,
        recording_poll_interval_seconds=recording_poll_interval_seconds,
        interval_capture_poll_interval_seconds=interval_capture_poll_interval_seconds,
    )
