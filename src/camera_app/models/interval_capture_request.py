from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(slots=True)
class IntervalCaptureRequest:
    save_directory: Optional[Path]
    file_stem: str
    interval_seconds: float
    file_extension: str = ".png"
    max_frame_count: Optional[int] = None
    duration_seconds: Optional[float] = None
    create_directories: bool = True
    camera_id: Optional[str] = None
