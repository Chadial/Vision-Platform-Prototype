"""Storage compatibility shim for the legacy camera_app namespace."""

__all__ = [
    "FrameWriter",
    "build_interval_capture_frame_path",
    "build_recording_frame_path",
    "build_recording_log_path",
    "build_snapshot_path",
]


def __getattr__(name: str):
    if name == "FrameWriter":
        from vision_platform.services.recording_service import FrameWriter

        return FrameWriter
    if name == "build_interval_capture_frame_path":
        from vision_platform.services.recording_service import build_interval_capture_frame_path

        return build_interval_capture_frame_path
    if name == "build_recording_frame_path":
        from vision_platform.services.recording_service import build_recording_frame_path

        return build_recording_frame_path
    if name == "build_recording_log_path":
        from vision_platform.services.recording_service import build_recording_log_path

        return build_recording_log_path
    if name == "build_snapshot_path":
        from vision_platform.services.recording_service import build_snapshot_path

        return build_snapshot_path
    raise AttributeError(name)

