from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from camera_app.models.camera_configuration import CameraConfiguration
from camera_app.models.camera_status import CameraStatus
from camera_app.models.interval_capture_status import IntervalCaptureStatus
from camera_app.models.recording_status import RecordingStatus


@dataclass(slots=True)
class SubsystemStatus:
    camera: CameraStatus
    recording: RecordingStatus
    interval_capture: IntervalCaptureStatus
    configuration: Optional[CameraConfiguration] = None
    default_save_directory: Optional[Path] = None
    is_save_directory_configured: bool = False
    has_interval_capture_service: bool = False
    can_apply_configuration: bool = False
    can_save_snapshot: bool = False
    can_start_recording: bool = False
    can_stop_recording: bool = False
    can_start_interval_capture: bool = False
    can_stop_interval_capture: bool = False
