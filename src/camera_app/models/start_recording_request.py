from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from camera_app.models.recording_request import RecordingRequest


@dataclass(slots=True)
class StartRecordingRequest:
    file_stem: str
    file_extension: str = ".png"
    save_directory: Optional[Path] = None
    max_frame_count: Optional[int] = None
    duration_seconds: Optional[float] = None
    target_frame_rate: Optional[float] = None
    queue_size: int = 128
    create_directories: bool = True
    camera_id: Optional[str] = None

    def to_recording_request(self) -> RecordingRequest:
        return RecordingRequest(
            save_directory=self.save_directory,
            file_stem=self.file_stem,
            file_extension=self.file_extension,
            frame_limit=self.max_frame_count,
            duration_seconds=self.duration_seconds,
            target_frame_rate=self.target_frame_rate,
            queue_size=self.queue_size,
            create_directories=self.create_directories,
            camera_id=self.camera_id,
        )
