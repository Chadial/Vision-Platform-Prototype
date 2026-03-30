import unittest
from unittest.mock import MagicMock

from tests import _path_setup
from vision_platform.models import CameraCapabilityProfile, CameraStatus, FeatureCapability
from vision_platform.services.recording_service import CameraService


class CameraServiceTests(unittest.TestCase):
    def test_initialize_prefers_driver_capability_probe_for_hardware_camera_when_available(self) -> None:
        driver = MagicMock()
        driver.initialize.return_value = CameraStatus(
            is_initialized=True,
            source_kind="hardware",
            camera_id="CAM-001",
        )
        driver.get_status.return_value = CameraStatus(
            is_initialized=True,
            source_kind="hardware",
            camera_id="CAM-001",
        )
        capability_service = MagicMock()
        driver.probe_capabilities.return_value = {
            "probe_utc": None,
            "camera": {
                "camera_id": "CAM-001",
                "name": "TestCam",
                "model": "ModelA",
                "serial": None,
                "interface_id": None,
            },
            "feature_count": 1,
            "features": {
                "PixelFormat": {
                    "type": "EnumFeature",
                    "is_writeable": True,
                    "entries": ["Mono8"],
                }
            },
        }
        capability_service.from_probe_payload.return_value = CameraCapabilityProfile(
            probe_utc=None,
            camera_id="CAM-001",
            camera_name="TestCam",
            camera_model="ModelA",
            camera_serial=None,
            interface_id=None,
            feature_count=1,
            features={
                "PixelFormat": FeatureCapability(
                    name="PixelFormat",
                    feature_type="EnumFeature",
                    is_writeable=True,
                    entries=("Mono8",),
                )
            },
        )
        service = CameraService(driver, capability_service=capability_service)

        status = service.initialize(camera_id="CAM-001")

        driver.probe_capabilities.assert_called_once()
        capability_service.from_probe_payload.assert_called_once_with(driver.probe_capabilities.return_value)
        capability_service.probe_live.assert_not_called()
        self.assertTrue(status.capabilities_available)
        self.assertIsNone(status.capability_probe_error)
        self.assertIsNotNone(service.get_capability_profile())

    def test_initialize_falls_back_to_live_capability_probe_when_driver_probe_is_unavailable(self) -> None:
        driver = MagicMock(spec=["initialize", "get_status"])
        driver.initialize.return_value = CameraStatus(
            is_initialized=True,
            source_kind="hardware",
            camera_id="CAM-001",
        )
        driver.get_status.return_value = CameraStatus(
            is_initialized=True,
            source_kind="hardware",
            camera_id="CAM-001",
        )
        capability_service = MagicMock()
        capability_service.probe_live.return_value = CameraCapabilityProfile(
            probe_utc=None,
            camera_id="CAM-001",
            camera_name="TestCam",
            camera_model="ModelA",
            camera_serial=None,
            interface_id=None,
            feature_count=0,
            features={},
        )
        service = CameraService(driver, capability_service=capability_service)

        status = service.initialize(camera_id="CAM-001")

        capability_service.probe_live.assert_called_once_with(camera_id="CAM-001")
        self.assertTrue(status.capabilities_available)

    def test_initialize_keeps_camera_usable_when_capability_probe_fails(self) -> None:
        driver = MagicMock(spec=["initialize", "get_status"])
        driver.initialize.return_value = CameraStatus(
            is_initialized=True,
            source_kind="hardware",
            camera_id="CAM-001",
        )
        driver.get_status.return_value = CameraStatus(
            is_initialized=True,
            source_kind="hardware",
            camera_id="CAM-001",
        )
        capability_service = MagicMock()
        capability_service.probe_live.side_effect = RuntimeError("probe unavailable")
        service = CameraService(driver, capability_service=capability_service)

        status = service.initialize(camera_id="CAM-001")

        self.assertTrue(status.is_initialized)
        self.assertFalse(status.capabilities_available)
        self.assertEqual(status.capability_probe_error, "probe unavailable")
        self.assertIsNone(service.get_capability_profile())
        self.assertTrue(service.get_status().is_initialized)

    def test_initialize_skips_capability_probe_for_simulated_camera(self) -> None:
        driver = MagicMock()
        driver.initialize.return_value = CameraStatus(
            is_initialized=True,
            source_kind="simulation",
            camera_id="SIM-001",
        )
        driver.get_status.return_value = CameraStatus(
            is_initialized=True,
            source_kind="simulation",
            camera_id="SIM-001",
        )
        capability_service = MagicMock()
        service = CameraService(driver, capability_service=capability_service)

        status = service.initialize(camera_id="SIM-001")

        capability_service.probe_live.assert_not_called()
        self.assertFalse(status.capabilities_available)
        self.assertIsNone(status.capability_probe_error)


if __name__ == "__main__":
    unittest.main()
