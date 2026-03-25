from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(slots=True)
class RecordingStatus:
    is_recording: bool = False
    frames_written: int = 0
    dropped_frames: int = 0
    save_directory: Optional[Path] = None
    active_file_stem: Optional[str] = None
    last_error: Optional[str] = None

