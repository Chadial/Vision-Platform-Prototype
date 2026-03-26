"""Compatibility bootstrap exposed through the new platform namespace."""

from camera_app.bootstrap import CameraSubsystem, build_camera_subsystem, build_simulated_camera_subsystem

__all__ = [
    "CameraSubsystem",
    "build_camera_subsystem",
    "build_simulated_camera_subsystem",
]
