"""Recording and persistence service access through the platform namespace."""

__all__ = [
    "CameraService",
    "FrameWriter",
    "IntervalCaptureService",
    "RecordingService",
    "SnapshotFocusCapture",
    "SnapshotFocusService",
    "SnapshotService",
    "build_interval_capture_frame_path",
    "build_recording_frame_path",
    "build_recording_log_path",
    "build_snapshot_path",
]


def __getattr__(name: str):
    if name == "CameraService":
        from vision_platform.services.recording_service.camera_service import CameraService

        return CameraService
    if name == "FrameWriter":
        from vision_platform.services.recording_service.frame_writer import FrameWriter

        return FrameWriter
    if name == "IntervalCaptureService":
        from vision_platform.services.recording_service.interval_capture_service import IntervalCaptureService

        return IntervalCaptureService
    if name == "RecordingService":
        from vision_platform.services.recording_service.recording_service import RecordingService

        return RecordingService
    if name == "SnapshotService":
        from vision_platform.services.recording_service.snapshot_service import SnapshotService

        return SnapshotService
    if name == "SnapshotFocusCapture":
        from vision_platform.services.recording_service.snapshot_focus_service import SnapshotFocusCapture

        return SnapshotFocusCapture
    if name == "SnapshotFocusService":
        from vision_platform.services.recording_service.snapshot_focus_service import SnapshotFocusService

        return SnapshotFocusService
    if name == "build_interval_capture_frame_path":
        from vision_platform.services.recording_service.file_naming import build_interval_capture_frame_path

        return build_interval_capture_frame_path
    if name == "build_recording_frame_path":
        from vision_platform.services.recording_service.file_naming import build_recording_frame_path

        return build_recording_frame_path
    if name == "build_recording_log_path":
        from vision_platform.services.recording_service.file_naming import build_recording_log_path

        return build_recording_log_path
    if name == "build_snapshot_path":
        from vision_platform.services.recording_service.file_naming import build_snapshot_path

        return build_snapshot_path
    raise AttributeError(name)
