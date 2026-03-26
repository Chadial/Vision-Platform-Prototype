"""Camera integration adapters exposed through the platform namespace."""

from vision_platform.integrations.camera.camera_driver import CameraDriver
from vision_platform.integrations.camera.simulated_camera_driver import SimulatedCameraDriver
from vision_platform.integrations.camera.vimbax_camera_driver import VimbaXCameraDriver

__all__ = [
    "CameraDriver",
    "SimulatedCameraDriver",
    "VimbaXCameraDriver",
]
