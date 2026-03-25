from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class PreviewFrameInfo:
    frame_id: Optional[int]
    timestamp_utc: datetime
    width: int
    height: int
    pixel_format: Optional[str] = None

