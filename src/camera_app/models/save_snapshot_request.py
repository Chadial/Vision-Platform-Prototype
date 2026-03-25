from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from camera_app.models.snapshot_request import SnapshotRequest


@dataclass(slots=True)
class SaveSnapshotRequest:
    file_stem: str
    file_extension: str = ".png"
    save_directory: Optional[Path] = None
    create_directories: bool = True
    camera_id: Optional[str] = None

    def to_snapshot_request(self) -> SnapshotRequest:
        return SnapshotRequest(
            save_directory=self.save_directory,
            file_stem=self.file_stem,
            file_extension=self.file_extension,
            create_directories=self.create_directories,
            camera_id=self.camera_id,
        )
