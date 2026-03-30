from __future__ import annotations

from typing import Callable

from vision_platform.integrations.camera import CameraDriver
from vision_platform.libraries.common_models import FocusMethod
from vision_platform.models import CameraConfiguration, CapturedFrame, PreviewFrameInfo
from vision_platform.services.recording_service import (
    ArtifactFocusMetadataProducer,
    IntervalCaptureService,
    RecordingService,
)
from vision_platform.services.recording_service.frame_writer import FrameWriter
from vision_platform.services.stream_service.focus_preview_service import FocusPreviewService
from vision_platform.services.stream_service.preview_service import PreviewService
from vision_platform.services.stream_service.roi_state_service import RoiStateService
from vision_platform.services.stream_service.shared_frame_source import SharedFrameSource


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
        self._roi_state_service = RoiStateService()

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
        artifact_focus_metadata_producer: ArtifactFocusMetadataProducer | None = None,
    ) -> RecordingService:
        return RecordingService(
            self._driver,
            frame_writer=frame_writer,
            poll_interval_seconds=poll_interval_seconds,
            configuration_provider=configuration_provider,
            shared_frame_source=self._shared_frame_source,
            artifact_focus_metadata_producer=artifact_focus_metadata_producer,
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

    def get_roi_state_service(self) -> RoiStateService:
        return self._roi_state_service

    def create_focus_preview_service(
        self,
        roi_state_service: RoiStateService | None = None,
        focus_method: FocusMethod | None = None,
    ) -> FocusPreviewService:
        return FocusPreviewService(
            self._preview_service,
            focus_method=focus_method,
            roi_state_service=roi_state_service or self._roi_state_service,
        )


__all__ = ["CameraStreamService"]
