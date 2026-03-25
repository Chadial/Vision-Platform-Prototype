from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from camera_app.models.preview_frame_info import PreviewFrameInfo


@dataclass(slots=True)
class CapturedFrame:
    raw_frame: Any
    width: int
    height: int
    frame_id: Optional[int] = None
    pixel_format: Optional[str] = None
    timestamp_utc: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_preview_frame_info(self) -> PreviewFrameInfo:
        return PreviewFrameInfo(
            frame_id=self.frame_id,
            timestamp_utc=self.timestamp_utc,
            width=self.width,
            height=self.height,
            pixel_format=self.pixel_format,
        )
