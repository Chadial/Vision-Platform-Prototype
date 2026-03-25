from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(slots=True)
class SnapshotRequest:
    save_directory: Path
    file_stem: str
    file_extension: str = ".png"
    create_directories: bool = True
    camera_id: Optional[str] = None

