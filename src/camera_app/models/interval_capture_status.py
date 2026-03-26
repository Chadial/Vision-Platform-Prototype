from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(slots=True)
class IntervalCaptureStatus:
    is_capturing: bool = False
    frames_written: int = 0
    skipped_intervals: int = 0
    save_directory: Optional[Path] = None
    active_file_stem: Optional[str] = None
    last_error: Optional[str] = None
