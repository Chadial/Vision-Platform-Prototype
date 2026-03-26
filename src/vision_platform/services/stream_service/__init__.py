"""Stream-service access through the platform namespace."""

from vision_platform.services.stream_service.camera_stream_service import CameraStreamService
from vision_platform.services.stream_service.preview_service import PreviewService
from vision_platform.services.stream_service.shared_frame_source import SharedFrameSource

__all__ = [
    "CameraStreamService",
    "PreviewService",
    "SharedFrameSource",
]
