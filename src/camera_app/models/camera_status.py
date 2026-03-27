from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class CameraStatus:
    is_initialized: bool = False
    is_acquiring: bool = False
    source_kind: Optional[str] = None
    driver_name: Optional[str] = None
    camera_id: Optional[str] = None
    camera_name: Optional[str] = None
    camera_model: Optional[str] = None
    camera_serial: Optional[str] = None
    interface_id: Optional[str] = None
    reported_acquisition_frame_rate: Optional[float] = None
    acquisition_frame_rate_enabled: Optional[bool] = None
    capabilities_available: bool = False
    capability_probe_error: Optional[str] = None
    last_error: Optional[str] = None
