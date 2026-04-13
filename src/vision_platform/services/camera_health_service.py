from __future__ import annotations

from vision_platform.models import CameraHealth, SubsystemStatus


class CameraHealthService:
    """Build one compact current health state from the current subsystem status."""

    def build_health(self, status: SubsystemStatus) -> CameraHealth:
        camera_status = status.camera
        recording_impaired = bool(status.recording.last_error)
        interval_capture_impaired = bool(status.interval_capture.last_error)
        faulted = bool(camera_status.last_error)
        degraded = (
            not faulted
            and (
                bool(camera_status.capability_probe_error)
                or (camera_status.source_kind == "hardware" and not camera_status.capabilities_available)
                or recording_impaired
                or interval_capture_impaired
            )
        )
        return CameraHealth(
            availability=camera_status.is_initialized,
            readiness=camera_status.is_initialized and not faulted,
            degraded=degraded,
            faulted=faulted,
            last_error=(
                camera_status.last_error
                or status.recording.last_error
                or status.interval_capture.last_error
                or camera_status.capability_probe_error
            ),
            capabilities_available=camera_status.capabilities_available,
            recording_impaired=recording_impaired if recording_impaired else None,
        )


__all__ = ["CameraHealthService"]
