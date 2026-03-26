"""Recording and persistence service access through the platform namespace."""

from vision_platform.services.recording_service.camera_service import CameraService
from vision_platform.services.recording_service.file_naming import (
    build_interval_capture_frame_path,
    build_recording_frame_path,
    build_recording_log_path,
    build_snapshot_path,
)
from vision_platform.services.recording_service.frame_writer import FrameWriter
from vision_platform.services.recording_service.interval_capture_service import IntervalCaptureService
from vision_platform.services.recording_service.recording_service import RecordingService
from vision_platform.services.recording_service.snapshot_service import SnapshotService

__all__ = [
    "CameraService",
    "FrameWriter",
    "IntervalCaptureService",
    "RecordingService",
    "SnapshotService",
    "build_interval_capture_frame_path",
    "build_recording_frame_path",
    "build_recording_log_path",
    "build_snapshot_path",
]
