from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(slots=True)
class RecordingRequest:
    save_directory: Path
    file_stem: str
    file_extension: str = ".png"
    frame_limit: Optional[int] = None
    duration_seconds: Optional[float] = None
    queue_size: int = 128
    create_directories: bool = True
    camera_id: Optional[str] = None

