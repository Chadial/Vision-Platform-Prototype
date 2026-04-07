from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(slots=True)
class RecordingRequest:
    save_directory: Optional[Path]
    file_stem: str
    file_extension: str = ".bmp"
    frame_limit: Optional[int] = None
    duration_seconds: Optional[float] = None
    target_frame_rate: Optional[float] = None
    queue_size: int = 128
    create_directories: bool = True
    camera_id: Optional[str] = None
    camera_alias: Optional[str] = None
    configuration_profile_id: Optional[str] = None
    configuration_profile_camera_class: Optional[str] = None
