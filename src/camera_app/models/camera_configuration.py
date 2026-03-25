from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class CameraConfiguration:
    exposure_time_us: Optional[float] = None
    gain: Optional[float] = None
    pixel_format: Optional[str] = None
    acquisition_frame_rate: Optional[float] = None

