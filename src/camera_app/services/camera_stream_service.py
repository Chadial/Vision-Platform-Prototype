from __future__ import annotations

from camera_app.drivers.camera_driver import CameraDriver
from camera_app.models.captured_frame import CapturedFrame
from camera_app.models.camera_configuration import CameraConfiguration
from camera_app.models.preview_frame_info import PreviewFrameInfo
from camera_app.services.interval_capture_service import IntervalCaptureService
from camera_app.services.preview_service import PreviewService
from camera_app.services.recording_service import RecordingService
from camera_app.services.shared_frame_source import SharedFrameSource
from camera_app.storage.frame_writer import FrameWriter
from typing import Callable


class CameraStreamService:
    """Coordinates one shared live frame stream for preview and recording consumers."""

    def __init__(
        self,
        driver: CameraDriver,
        preview_poll_interval_seconds: float = 0.05,
        shared_poll_interval_seconds: float = 0.01,
    ) -> None:
        self._driver = driver
        self._shared_frame_source = SharedFrameSource(
            driver,
            poll_interval_seconds=shared_poll_interval_seconds,
        )
        self._preview_service = PreviewService(
            driver,
            poll_interval_seconds=preview_poll_interval_seconds,
            shared_frame_source=self._shared_frame_source,
        )

    def start_preview(self) -> None:
        self._preview_service.start()

    def stop_preview(self) -> None:
        self._preview_service.stop()

    @property
    def is_preview_running(self) -> bool:
        return self._preview_service.is_running

    def refresh_preview_once(self) -> PreviewFrameInfo | None:
        return self._preview_service.refresh_once()

    def get_latest_frame(self) -> CapturedFrame | None:
        return self._preview_service.get_latest_frame()

    def get_latest_frame_info(self) -> PreviewFrameInfo | None:
        return self._preview_service.get_latest_frame_info()

    def create_recording_service(
        self,
        frame_writer: FrameWriter | None = None,
        poll_interval_seconds: float = 0.01,
        configuration_provider: Callable[[], CameraConfiguration | None] | None = None,
    ) -> RecordingService:
        return RecordingService(
            self._driver,
            frame_writer=frame_writer,
            poll_interval_seconds=poll_interval_seconds,
            configuration_provider=configuration_provider,
            shared_frame_source=self._shared_frame_source,
        )

    def create_interval_capture_service(
        self,
        frame_writer: FrameWriter | None = None,
        poll_interval_seconds: float = 0.01,
    ) -> IntervalCaptureService:
        return IntervalCaptureService(
            self._driver,
            frame_writer=frame_writer,
            poll_interval_seconds=poll_interval_seconds,
            shared_frame_source=self._shared_frame_source,
        )
