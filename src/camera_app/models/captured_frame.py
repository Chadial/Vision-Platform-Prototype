from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from vision_platform.libraries.common_models.frame_models import FrameData, FrameMetadata
from camera_app.models.preview_frame_info import PreviewFrameInfo


@dataclass(slots=True)
class CapturedFrame:
    raw_frame: Any
    width: int
    height: int
    frame_id: Optional[int] = None
    camera_timestamp: Optional[int] = None
    pixel_format: Optional[str] = None
    timestamp_utc: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def get_buffer_bytes(self) -> bytes:
        raw_frame = self.raw_frame
        get_buffer = getattr(raw_frame, "get_buffer", None)
        if callable(get_buffer):
            return bytes(get_buffer())

        if isinstance(raw_frame, (bytes, bytearray, memoryview)):
            return bytes(raw_frame)

        raise RuntimeError("Frame does not expose a writable buffer.")

    def to_preview_frame_info(self) -> PreviewFrameInfo:
        return PreviewFrameInfo(
            frame_id=self.frame_id,
            timestamp_utc=self.timestamp_utc,
            width=self.width,
            height=self.height,
            pixel_format=self.pixel_format,
        )

    def to_frame_data(self) -> FrameData:
        return FrameData(
            data=self.get_buffer_bytes(),
            metadata=FrameMetadata(
                frame_id=self.frame_id,
                camera_timestamp=self.camera_timestamp,
                captured_utc=self.timestamp_utc,
                pixel_format=self.pixel_format,
                width=self.width,
                height=self.height,
            ),
        )
