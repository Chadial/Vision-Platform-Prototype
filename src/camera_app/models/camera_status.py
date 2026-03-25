from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class CameraStatus:
    is_initialized: bool = False
    is_acquiring: bool = False
    camera_id: Optional[str] = None
    camera_name: Optional[str] = None
    camera_model: Optional[str] = None
    camera_serial: Optional[str] = None
    interface_id: Optional[str] = None
    last_error: Optional[str] = None
