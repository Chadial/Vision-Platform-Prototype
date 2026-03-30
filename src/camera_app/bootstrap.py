"""Compatibility bootstrap shim for the legacy camera_app namespace."""

from vision_platform.bootstrap import CameraSubsystem, build_camera_subsystem, build_simulated_camera_subsystem


__all__ = ["CameraSubsystem", "build_camera_subsystem", "build_simulated_camera_subsystem"]
