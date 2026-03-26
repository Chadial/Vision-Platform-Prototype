from __future__ import annotations

from vision_platform.imaging.opencv_adapter import OpenCvFrameAdapter
from vision_platform.services.stream_service.preview_service import PreviewService


class OpenCvPreviewWindow:
    """Optional OpenCV-backed preview window on top of PreviewService."""

    def __init__(
        self,
        preview_service: PreviewService,
        window_name: str = "Camera Preview",
        frame_adapter: OpenCvFrameAdapter | None = None,
    ) -> None:
        self._preview_service = preview_service
        self._window_name = window_name
        self._frame_adapter = frame_adapter or OpenCvFrameAdapter()

    def render_latest_frame(self, delay_ms: int = 1) -> bool:
        frame = self._preview_service.get_latest_frame()
        if frame is None:
            return False

        self._frame_adapter.show_frame(self._window_name, frame, delay_ms=delay_ms)
        return True

    def close(self) -> None:
        self._frame_adapter.destroy_window(self._window_name)


__all__ = ["OpenCvPreviewWindow"]
