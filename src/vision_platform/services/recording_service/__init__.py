"""Recording and persistence service access through the platform namespace."""

__all__ = [
    "ArtifactFocusMetadataProducer",
    "CameraService",
    "FrameWriter",
    "IntervalCaptureService",
    "RecordingService",
    "SnapshotFocusCapture",
    "SnapshotFocusService",
    "SnapshotService",
    "build_interval_capture_frame_path",
    "build_next_snapshot_path",
    "build_recording_frame_path",
    "build_recording_log_path",
    "build_recording_log_path_for_run",
    "build_snapshot_path",
    "resolve_next_recording_frame_index",
    "resolve_next_snapshot_index",
]


def __getattr__(name: str):
    if name == "ArtifactFocusMetadataProducer":
        from vision_platform.services.recording_service.artifact_focus_metadata_producer import ArtifactFocusMetadataProducer

        return ArtifactFocusMetadataProducer
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
    if name == "build_next_snapshot_path":
        from vision_platform.services.recording_service.file_naming import build_next_snapshot_path

        return build_next_snapshot_path
    if name == "build_recording_frame_path":
        from vision_platform.services.recording_service.file_naming import build_recording_frame_path

        return build_recording_frame_path
    if name == "build_recording_log_path":
        from vision_platform.services.recording_service.file_naming import build_recording_log_path

        return build_recording_log_path
    if name == "build_recording_log_path_for_run":
        from vision_platform.services.recording_service.file_naming import build_recording_log_path_for_run

        return build_recording_log_path_for_run
    if name == "build_snapshot_path":
        from vision_platform.services.recording_service.file_naming import build_snapshot_path

        return build_snapshot_path
    if name == "resolve_next_recording_frame_index":
        from vision_platform.services.recording_service.file_naming import resolve_next_recording_frame_index

        return resolve_next_recording_frame_index
    if name == "resolve_next_snapshot_index":
        from vision_platform.services.recording_service.file_naming import resolve_next_snapshot_index

        return resolve_next_snapshot_index
    raise AttributeError(name)
