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
    camera_alias: Optional[str] = None
    configuration_profile_id: Optional[str] = None
    configuration_profile_camera_class: Optional[str] = None

    @classmethod
    def from_recording_request(cls, request: RecordingRequest) -> "StartRecordingRequest":
        return cls(
            file_stem=request.file_stem,
            file_extension=request.file_extension,
            save_directory=request.save_directory,
            max_frame_count=request.frame_limit,
            duration_seconds=request.duration_seconds,
            target_frame_rate=request.target_frame_rate,
            queue_size=request.queue_size,
            create_directories=request.create_directories,
            camera_id=request.camera_id,
            camera_alias=request.camera_alias,
            configuration_profile_id=request.configuration_profile_id,
            configuration_profile_camera_class=request.configuration_profile_camera_class,
        )

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
            camera_alias=self.camera_alias,
            configuration_profile_id=self.configuration_profile_id,
            configuration_profile_camera_class=self.configuration_profile_camera_class,
        )
