from abc import ABC, abstractmethod
from typing import Optional

from camera_app.models.captured_frame import CapturedFrame
from camera_app.models.camera_configuration import CameraConfiguration
from camera_app.models.camera_status import CameraStatus


class CameraDriver(ABC):
    @abstractmethod
    def initialize(self, camera_id: Optional[str] = None) -> CameraStatus:
        """Initialize the underlying camera connection."""

    @abstractmethod
    def get_status(self) -> CameraStatus:
        """Return the latest known camera status."""

    @abstractmethod
    def shutdown(self) -> None:
        """Release SDK and camera resources."""

    @abstractmethod
    def apply_configuration(self, config: CameraConfiguration) -> None:
        """Apply camera parameters."""

    @abstractmethod
    def start_acquisition(self) -> None:
        """Start acquisition for preview or recording."""

    @abstractmethod
    def stop_acquisition(self) -> None:
        """Stop acquisition."""

    @abstractmethod
    def capture_snapshot(self) -> CapturedFrame:
        """Capture a single frame object from the camera."""

    @abstractmethod
    def get_latest_frame(self) -> Optional[CapturedFrame]:
        """Return the most recent frame object if available."""
