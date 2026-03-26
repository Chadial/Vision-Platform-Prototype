from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class FrameMetadata:
    """Portable frame metadata for later cross-language handover."""

    frame_id: int | None = None
    camera_timestamp: float | None = None
    captured_utc: datetime | None = None
    pixel_format: str | None = None
    width: int | None = None
    height: int | None = None
    source_kind: str = "unknown"
    extras: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class FrameData:
    """Bundle raw frame payload with normalized metadata."""

    data: bytes | None = None
    metadata: FrameMetadata = field(default_factory=FrameMetadata)
