from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from camera_app.models.interval_capture_request import IntervalCaptureRequest


@dataclass(slots=True)
class StartIntervalCaptureRequest:
    file_stem: str
    interval_seconds: float
    file_extension: str = ".png"
    save_directory: Optional[Path] = None
    max_frame_count: Optional[int] = None
    duration_seconds: Optional[float] = None
    create_directories: bool = True
    camera_id: Optional[str] = None

    @classmethod
    def from_interval_capture_request(cls, request: IntervalCaptureRequest) -> "StartIntervalCaptureRequest":
        return cls(
            file_stem=request.file_stem,
            interval_seconds=request.interval_seconds,
            file_extension=request.file_extension,
            save_directory=request.save_directory,
            max_frame_count=request.max_frame_count,
            duration_seconds=request.duration_seconds,
            create_directories=request.create_directories,
            camera_id=request.camera_id,
        )

    def to_interval_capture_request(self) -> IntervalCaptureRequest:
        return IntervalCaptureRequest(
            save_directory=self.save_directory,
            file_stem=self.file_stem,
            interval_seconds=self.interval_seconds,
            file_extension=self.file_extension,
            max_frame_count=self.max_frame_count,
            duration_seconds=self.duration_seconds,
            create_directories=self.create_directories,
            camera_id=self.camera_id,
        )
