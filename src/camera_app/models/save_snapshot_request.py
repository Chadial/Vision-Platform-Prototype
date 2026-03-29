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

    @classmethod
    def from_snapshot_request(cls, request: SnapshotRequest) -> "SaveSnapshotRequest":
        return cls(
            file_stem=request.file_stem,
            file_extension=request.file_extension,
            save_directory=request.save_directory,
            create_directories=request.create_directories,
            camera_id=request.camera_id,
        )

    def to_snapshot_request(self) -> SnapshotRequest:
        return SnapshotRequest(
            save_directory=self.save_directory,
            file_stem=self.file_stem,
            file_extension=self.file_extension,
            create_directories=self.create_directories,
            camera_id=self.camera_id,
        )
