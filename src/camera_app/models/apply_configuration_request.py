from dataclasses import dataclass
from typing import Optional

from camera_app.models.camera_configuration import CameraConfiguration


@dataclass(slots=True)
class ApplyConfigurationRequest:
    exposure_time_us: Optional[float] = None
    gain: Optional[float] = None
    pixel_format: Optional[str] = None
    acquisition_frame_rate: Optional[float] = None
    roi_offset_x: Optional[int] = None
    roi_offset_y: Optional[int] = None
    roi_width: Optional[int] = None
    roi_height: Optional[int] = None

    @classmethod
    def from_camera_configuration(cls, configuration: CameraConfiguration) -> "ApplyConfigurationRequest":
        return cls(
            exposure_time_us=configuration.exposure_time_us,
            gain=configuration.gain,
            pixel_format=configuration.pixel_format,
            acquisition_frame_rate=configuration.acquisition_frame_rate,
            roi_offset_x=configuration.roi_offset_x,
            roi_offset_y=configuration.roi_offset_y,
            roi_width=configuration.roi_width,
            roi_height=configuration.roi_height,
        )

    def to_camera_configuration(self) -> CameraConfiguration:
        return CameraConfiguration(
            exposure_time_us=self.exposure_time_us,
            gain=self.gain,
            pixel_format=self.pixel_format,
            acquisition_frame_rate=self.acquisition_frame_rate,
            roi_offset_x=self.roi_offset_x,
            roi_offset_y=self.roi_offset_y,
            roi_width=self.roi_width,
            roi_height=self.roi_height,
        )
