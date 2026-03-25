from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class CameraConfiguration:
    exposure_time_us: Optional[float] = None
    gain: Optional[float] = None
    pixel_format: Optional[str] = None
    acquisition_frame_rate: Optional[float] = None
    roi_offset_x: Optional[int] = None
    roi_offset_y: Optional[int] = None
    roi_width: Optional[int] = None
    roi_height: Optional[int] = None
