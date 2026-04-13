import unittest

from tests import _path_setup
from vision_platform.models import CameraStatus, IntervalCaptureStatus, RecordingStatus, SubsystemStatus
from vision_platform.services.camera_health_service import CameraHealthService


class CameraHealthServiceTests(unittest.TestCase):
    def test_build_health_keeps_faulted_and_degraded_separate(self) -> None:
        service = CameraHealthService()

        degraded_health = service.build_health(
            SubsystemStatus(
                camera=CameraStatus(
                    is_initialized=True,
                    source_kind="hardware",
                    capabilities_available=False,
                    capability_probe_error="probe warning",
                ),
                configuration=None,
                recording=RecordingStatus(),
                interval_capture=IntervalCaptureStatus(),
            )
        )
        self.assertTrue(degraded_health.degraded)
        self.assertFalse(degraded_health.faulted)
        self.assertTrue(degraded_health.readiness)

        faulted_health = service.build_health(
            SubsystemStatus(
                camera=CameraStatus(
                    is_initialized=True,
                    source_kind="hardware",
                    capabilities_available=True,
                    last_error="camera lost",
                ),
                configuration=None,
                recording=RecordingStatus(),
                interval_capture=IntervalCaptureStatus(),
            )
        )
        self.assertTrue(faulted_health.faulted)
        self.assertFalse(faulted_health.degraded)
        self.assertFalse(faulted_health.readiness)

    def test_build_health_keeps_last_error_contextual(self) -> None:
        service = CameraHealthService()

        health = service.build_health(
            SubsystemStatus(
                camera=CameraStatus(is_initialized=True, source_kind="simulation"),
                configuration=None,
                recording=RecordingStatus(last_error="writer warning"),
                interval_capture=IntervalCaptureStatus(),
            )
        )

        self.assertTrue(health.degraded)
        self.assertEqual(health.last_error, "writer warning")
        self.assertTrue(health.recording_impaired)


if __name__ == "__main__":
    unittest.main()
