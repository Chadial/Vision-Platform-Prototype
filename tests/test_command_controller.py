from pathlib import Path
import unittest
from unittest.mock import MagicMock

from tests import _path_setup
from camera_app.control import CommandController as LegacyCommandController
from vision_platform.control import CommandController
from vision_platform.models import (
    ApplyConfigurationCommandResult,
    ApplyConfigurationRequest,
    CameraCapabilities,
    CameraCapabilityProfile,
    CameraConfiguration,
    CameraHealth,
    CameraStatus,
    FeatureCapability,
    IntervalCaptureCommandResult,
    IntervalCaptureRequest,
    IntervalCaptureStatus,
    RecordingRequest,
    RecordingCommandResult,
    RecordingStatus,
    SaveDirectoryCommandResult,
    SaveSnapshotRequest,
    SnapshotCommandResult,
    SetSaveDirectoryRequest,
    SnapshotRequest,
    StartIntervalCaptureRequest,
    StartRecordingRequest,
    StopIntervalCaptureRequest,
    StopRecordingRequest,
    SubsystemStatus,
)


class CommandControllerTests(unittest.TestCase):
    def test_legacy_camera_app_control_package_reexports_platform_controller(self) -> None:
        self.assertIs(LegacyCommandController, CommandController)

    def test_save_snapshot_uses_default_save_directory_when_request_has_none(self) -> None:
        camera_service = MagicMock()
        snapshot_service = MagicMock()
        recording_service = MagicMock()
        controller = CommandController(camera_service, snapshot_service, recording_service)
        controller.set_save_directory(Path("captures/default"))

        request = SnapshotRequest(save_directory=None, file_stem="image_001", file_extension=".png")
        controller.save_snapshot(request)

        resolved_request = snapshot_service.save_snapshot.call_args.args[0]
        self.assertEqual(resolved_request.save_directory, Path("captures/default"))
        self.assertEqual(resolved_request.file_stem, "image_001")

    def test_start_recording_uses_default_save_directory_when_request_has_none(self) -> None:
        camera_service = MagicMock()
        snapshot_service = MagicMock()
        recording_service = MagicMock()
        controller = CommandController(camera_service, snapshot_service, recording_service)
        controller.set_save_directory(Path("captures/default"))

        request = RecordingRequest(save_directory=None, file_stem="series", file_extension=".raw", frame_limit=3)
        controller.start_recording(request)

        resolved_request = recording_service.start_recording.call_args.args[0]
        self.assertEqual(resolved_request.save_directory, Path("captures/default"))
        self.assertEqual(resolved_request.file_stem, "series")

    def test_set_save_directory_request_can_resolve_new_subdirectory(self) -> None:
        controller = CommandController(MagicMock(), MagicMock(), MagicMock())

        result = controller.set_save_directory(
            SetSaveDirectoryRequest(
                base_directory=Path("captures"),
                mode="new_subdirectory",
                subdirectory_name="run_001",
            )
        )

        status = controller.get_status()

        self.assertIsInstance(result, SaveDirectoryCommandResult)
        self.assertEqual(result.selected_directory, Path("captures/run_001"))
        self.assertFalse(result.was_cleared)
        self.assertEqual(status.default_save_directory, Path("captures/run_001"))

    def test_apply_configuration_request_maps_roi_and_exposure(self) -> None:
        camera_service = MagicMock()
        controller = CommandController(camera_service, MagicMock(), MagicMock())

        result = controller.apply_configuration(
            ApplyConfigurationRequest(
                exposure_time_us=2000.0,
                roi_offset_x=10,
                roi_offset_y=20,
                roi_width=300,
                roi_height=200,
            )
        )

        forwarded_config = camera_service.apply_configuration.call_args.args[0]
        self.assertIsInstance(result, ApplyConfigurationCommandResult)
        self.assertEqual(result.applied_configuration, forwarded_config)
        self.assertEqual(forwarded_config.exposure_time_us, 2000.0)
        self.assertEqual(forwarded_config.roi_offset_x, 10)
        self.assertEqual(forwarded_config.roi_offset_y, 20)
        self.assertEqual(forwarded_config.roi_width, 300)
        self.assertEqual(forwarded_config.roi_height, 200)

    def test_save_snapshot_request_maps_to_snapshot_request(self) -> None:
        snapshot_service = MagicMock()
        snapshot_service.save_snapshot.return_value = Path("captures/default/image_001.png")
        controller = CommandController(MagicMock(), snapshot_service, MagicMock())
        controller.set_save_directory(Path("captures/default"))

        result = controller.save_snapshot(SaveSnapshotRequest(file_stem="image_001"))

        resolved_request = snapshot_service.save_snapshot.call_args.args[0]
        self.assertIsInstance(result, SnapshotCommandResult)
        self.assertEqual(result.saved_path, Path("captures/default/image_001.png"))
        self.assertEqual(resolved_request.save_directory, Path("captures/default"))
        self.assertEqual(resolved_request.file_stem, "image_001")

    def test_start_recording_request_maps_target_frame_rate(self) -> None:
        recording_service = MagicMock()
        recording_service.start_recording.return_value = RecordingStatus(is_recording=True, frames_written=0)
        controller = CommandController(MagicMock(), MagicMock(), recording_service)
        controller.set_save_directory(Path("captures/default"))

        result = controller.start_recording(
            StartRecordingRequest(
                file_stem="series",
                max_frame_count=5,
                duration_seconds=2.0,
                target_frame_rate=12.5,
            )
        )

        resolved_request = recording_service.start_recording.call_args.args[0]
        self.assertIsInstance(result, RecordingCommandResult)
        self.assertTrue(result.status.is_recording)
        self.assertEqual(resolved_request.save_directory, Path("captures/default"))
        self.assertEqual(resolved_request.frame_limit, 5)
        self.assertEqual(resolved_request.duration_seconds, 2.0)
        self.assertEqual(resolved_request.target_frame_rate, 12.5)

    def test_stop_recording_returns_typed_result(self) -> None:
        recording_service = MagicMock()
        recording_service.stop_recording.return_value = RecordingStatus(is_recording=False, frames_written=3)
        controller = CommandController(MagicMock(), MagicMock(), recording_service)

        result = controller.stop_recording()

        self.assertIsInstance(result, RecordingCommandResult)
        self.assertFalse(result.status.is_recording)
        self.assertEqual(result.status.frames_written, 3)
        self.assertEqual(result.stop_reason, "external_request")

    def test_stop_recording_preserves_request_reason_in_result(self) -> None:
        recording_service = MagicMock()
        recording_service.stop_recording.return_value = RecordingStatus(is_recording=False, frames_written=1)
        controller = CommandController(MagicMock(), MagicMock(), recording_service)

        result = controller.stop_recording(StopRecordingRequest(reason="operator_cancelled"))

        self.assertEqual(result.stop_reason, "operator_cancelled")

    def test_save_snapshot_raises_when_no_request_or_default_save_directory_exists(self) -> None:
        controller = CommandController(MagicMock(), MagicMock(), MagicMock())

        with self.assertRaisesRegex(ValueError, "no default save directory"):
            controller.save_snapshot(SnapshotRequest(save_directory=None, file_stem="image_001"))

    def test_get_status_returns_explicit_subsystem_status_model(self) -> None:
        camera_service = MagicMock()
        snapshot_service = MagicMock()
        recording_service = MagicMock()
        interval_capture_service = MagicMock()
        controller = CommandController(camera_service, snapshot_service, recording_service, interval_capture_service)
        controller.set_save_directory(Path("captures/default"))

        camera_service.get_status.return_value = CameraStatus(
            is_initialized=True,
            camera_id="cam2",
            source_kind="simulation",
            driver_name="SimulatedCameraDriver",
        )
        camera_service.get_last_configuration.return_value = CameraConfiguration(pixel_format="Mono8")
        recording_service.get_status.return_value = RecordingStatus(is_recording=True, frames_written=4)
        interval_capture_service.get_status.return_value = IntervalCaptureStatus(is_capturing=False, frames_written=2)

        status = controller.get_status()

        self.assertIsInstance(status, SubsystemStatus)
        self.assertEqual(status.default_save_directory, Path("captures/default"))
        self.assertTrue(status.is_save_directory_configured)
        self.assertTrue(status.has_interval_capture_service)
        self.assertEqual(status.camera.camera_id, "cam2")
        self.assertEqual(status.camera.source_kind, "simulation")
        self.assertEqual(status.camera.driver_name, "SimulatedCameraDriver")
        self.assertEqual(status.configuration.pixel_format, "Mono8")
        self.assertEqual(status.recording.frames_written, 4)
        self.assertEqual(status.interval_capture.frames_written, 2)
        self.assertTrue(status.can_apply_configuration)
        self.assertFalse(status.can_start_recording)
        self.assertTrue(status.can_stop_recording)
        self.assertTrue(status.can_start_interval_capture)
        self.assertFalse(status.can_stop_interval_capture)

    def test_get_status_reports_command_readiness_for_idle_initialized_camera(self) -> None:
        camera_service = MagicMock()
        snapshot_service = MagicMock()
        recording_service = MagicMock()
        interval_capture_service = MagicMock()
        controller = CommandController(camera_service, snapshot_service, recording_service, interval_capture_service)
        controller.set_save_directory(Path("captures/default"))

        camera_service.get_status.return_value = CameraStatus(is_initialized=True, camera_id="cam2")
        camera_service.get_last_configuration.return_value = None
        recording_service.get_status.return_value = RecordingStatus(is_recording=False, frames_written=0)
        interval_capture_service.get_status.return_value = IntervalCaptureStatus(is_capturing=False, frames_written=0)

        status = controller.get_status()

        self.assertTrue(status.can_apply_configuration)
        self.assertTrue(status.is_save_directory_configured)
        self.assertTrue(status.has_interval_capture_service)
        self.assertTrue(status.can_save_snapshot)
        self.assertTrue(status.can_start_recording)
        self.assertFalse(status.can_stop_recording)
        self.assertTrue(status.can_start_interval_capture)
        self.assertFalse(status.can_stop_interval_capture)

    def test_set_save_directory_allows_clearing_default_path(self) -> None:
        camera_service = MagicMock()
        snapshot_service = MagicMock()
        recording_service = MagicMock()
        controller = CommandController(camera_service, snapshot_service, recording_service)
        controller.set_save_directory(Path("captures/default"))
        result = controller.set_save_directory(None)

        camera_service.get_status.return_value = CameraStatus(is_initialized=True)
        camera_service.get_last_configuration.return_value = None
        recording_service.get_status.return_value = RecordingStatus()

        status = controller.get_status()

        self.assertIsInstance(result, SaveDirectoryCommandResult)
        self.assertIsNone(result.selected_directory)
        self.assertTrue(result.was_cleared)
        self.assertIsNone(status.default_save_directory)
        self.assertFalse(status.is_save_directory_configured)
        self.assertFalse(status.can_save_snapshot)
        self.assertFalse(status.can_start_recording)
        self.assertFalse(status.can_start_interval_capture)

    def test_get_status_marks_interval_capture_unavailable_when_service_is_not_configured(self) -> None:
        camera_service = MagicMock()
        snapshot_service = MagicMock()
        recording_service = MagicMock()
        controller = CommandController(camera_service, snapshot_service, recording_service)
        controller.set_save_directory(Path("captures/default"))

        camera_service.get_status.return_value = CameraStatus(is_initialized=True, camera_id="cam2")
        camera_service.get_last_configuration.return_value = None
        recording_service.get_status.return_value = RecordingStatus(is_recording=False, frames_written=0)

        status = controller.get_status()

        self.assertTrue(status.is_save_directory_configured)
        self.assertFalse(status.has_interval_capture_service)
        self.assertFalse(status.can_start_interval_capture)
        self.assertFalse(status.can_stop_interval_capture)

    def test_get_health_returns_compact_current_health_state(self) -> None:
        camera_service = MagicMock()
        snapshot_service = MagicMock()
        recording_service = MagicMock()
        controller = CommandController(camera_service, snapshot_service, recording_service)

        camera_service.get_status.return_value = CameraStatus(
            is_initialized=True,
            source_kind="hardware",
            capabilities_available=False,
            capability_probe_error="probe warning",
        )
        camera_service.get_last_configuration.return_value = None
        recording_service.get_status.return_value = RecordingStatus(
            is_recording=False,
            last_error="writer recovered",
        )

        health = controller.get_health()

        self.assertIsInstance(health, CameraHealth)
        self.assertTrue(health.availability)
        self.assertTrue(health.readiness)
        self.assertTrue(health.degraded)
        self.assertFalse(health.faulted)
        self.assertEqual(health.last_error, "writer recovered")
        self.assertFalse(health.capabilities_available)
        self.assertTrue(health.recording_impaired)

    def test_get_health_marks_camera_error_as_faulted(self) -> None:
        camera_service = MagicMock()
        recording_service = MagicMock()
        controller = CommandController(camera_service, MagicMock(), recording_service)

        camera_service.get_status.return_value = CameraStatus(
            is_initialized=True,
            source_kind="hardware",
            last_error="camera lost",
            capabilities_available=True,
        )
        camera_service.get_last_configuration.return_value = None
        recording_service.get_status.return_value = RecordingStatus()

        health = controller.get_health()

        self.assertTrue(health.faulted)
        self.assertFalse(health.degraded)
        self.assertFalse(health.readiness)
        self.assertEqual(health.last_error, "camera lost")

    def test_get_capabilities_distinguishes_supported_available_and_enabled(self) -> None:
        camera_service = MagicMock()
        snapshot_service = MagicMock()
        recording_service = MagicMock()
        interval_capture_service = MagicMock()
        capability_profile = self._build_capability_profile(
            ExposureTime=FeatureCapability(name="ExposureTime", feature_type="FloatFeature", is_writeable=True),
            Gain=FeatureCapability(name="Gain", feature_type="FloatFeature", is_writeable=True),
            PixelFormat=FeatureCapability(name="PixelFormat", feature_type="EnumFeature", is_writeable=True),
            AcquisitionFrameRate=FeatureCapability(
                name="AcquisitionFrameRate",
                feature_type="FloatFeature",
                is_writeable=True,
            ),
            OffsetX=FeatureCapability(name="OffsetX", feature_type="IntFeature", is_writeable=True),
            OffsetY=FeatureCapability(name="OffsetY", feature_type="IntFeature", is_writeable=True),
            Width=FeatureCapability(name="Width", feature_type="IntFeature", is_writeable=True),
            Height=FeatureCapability(name="Height", feature_type="IntFeature", is_writeable=True),
        )
        controller = CommandController(
            camera_service,
            snapshot_service,
            recording_service,
            interval_capture_service,
            capability_profile=capability_profile,
        )
        controller.set_save_directory(Path("captures/default"))

        camera_service.get_status.return_value = CameraStatus(
            is_initialized=True,
            source_kind="hardware",
            capabilities_available=True,
        )
        camera_service.get_last_configuration.return_value = CameraConfiguration(
            exposure_time_us=1000.0,
            pixel_format="Mono8",
            roi_width=320,
            roi_height=200,
        )
        recording_service.get_status.return_value = RecordingStatus(is_recording=True)
        interval_capture_service.get_status.return_value = IntervalCaptureStatus(is_capturing=False)

        capabilities = controller.get_capabilities()

        self.assertIsInstance(capabilities, CameraCapabilities)
        self.assertTrue(capabilities.capability_profile_available)
        self.assertTrue(capabilities.exposure_time_control.supported)
        self.assertTrue(capabilities.exposure_time_control.currently_available)
        self.assertTrue(capabilities.exposure_time_control.currently_enabled)
        self.assertTrue(capabilities.gain_control.supported)
        self.assertFalse(capabilities.gain_control.currently_enabled)
        self.assertTrue(capabilities.recording.supported)
        self.assertTrue(capabilities.recording.currently_available)
        self.assertTrue(capabilities.recording.currently_enabled)
        self.assertTrue(capabilities.interval_capture.supported)
        self.assertTrue(capabilities.interval_capture.currently_available)
        self.assertFalse(capabilities.interval_capture.currently_enabled)

    def test_apply_configuration_rejects_invalid_roi(self) -> None:
        controller = CommandController(MagicMock(), MagicMock(), MagicMock())

        with self.assertRaisesRegex(ValueError, "roi_width"):
            controller.apply_configuration(ApplyConfigurationRequest(roi_width=0))

    def test_apply_configuration_rejects_capability_profile_increment_mismatch(self) -> None:
        camera_service = MagicMock()
        profile = self._build_capability_profile(
            Width=FeatureCapability(
                name="Width",
                feature_type="IntFeature",
                is_writeable=True,
                minimum=8,
                maximum=4024,
                increment=8,
            )
        )
        controller = CommandController(camera_service, MagicMock(), MagicMock(), capability_profile=profile)

        with self.assertRaisesRegex(ValueError, r"roi_width=14.*increment 8.*nearest valid values: 8, 16"):
            controller.apply_configuration(ApplyConfigurationRequest(roi_width=14))

        camera_service.apply_configuration.assert_not_called()

    def test_apply_configuration_allows_acquisition_frame_rate_when_enable_feature_is_writeable(self) -> None:
        camera_service = MagicMock()
        profile = self._build_capability_profile(
            AcquisitionFrameRate=FeatureCapability(
                name="AcquisitionFrameRate",
                feature_type="FloatFeature",
                is_writeable=False,
                minimum=0.5,
                maximum=15.0,
            ),
            AcquisitionFrameRateEnable=FeatureCapability(
                name="AcquisitionFrameRateEnable",
                feature_type="BoolFeature",
                is_writeable=True,
            ),
        )
        controller = CommandController(camera_service, MagicMock(), MagicMock(), capability_profile=profile)

        controller.apply_configuration(ApplyConfigurationRequest(acquisition_frame_rate=5.0))

        forwarded_config = camera_service.apply_configuration.call_args.args[0]
        self.assertEqual(forwarded_config.acquisition_frame_rate, 5.0)

    def test_apply_configuration_uses_camera_service_capability_profile_when_no_override_is_set(self) -> None:
        camera_service = MagicMock()
        camera_service.get_capability_profile.return_value = self._build_capability_profile(
            PixelFormat=FeatureCapability(
                name="PixelFormat",
                feature_type="EnumFeature",
                is_writeable=True,
                entries=("Mono8", "Mono10"),
            )
        )
        controller = CommandController(camera_service, MagicMock(), MagicMock())

        with self.assertRaisesRegex(ValueError, "PixelFormat"):
            controller.apply_configuration(ApplyConfigurationRequest(pixel_format="Mono16"))

        camera_service.apply_configuration.assert_not_called()

    def test_start_recording_rejects_path_like_file_stem_before_calling_service(self) -> None:
        recording_service = MagicMock()
        controller = CommandController(MagicMock(), MagicMock(), recording_service)
        controller.set_save_directory(Path("captures/default"))

        with self.assertRaisesRegex(ValueError, "file_stem"):
            controller.start_recording(RecordingRequest(save_directory=None, file_stem="nested/series", frame_limit=3))

        recording_service.start_recording.assert_not_called()

    def test_set_save_directory_request_rejects_path_like_subdirectory_name(self) -> None:
        controller = CommandController(MagicMock(), MagicMock(), MagicMock())

        with self.assertRaisesRegex(ValueError, "path separators"):
            controller.set_save_directory(
                SetSaveDirectoryRequest(
                    base_directory=Path("captures"),
                    mode="new_subdirectory",
                    subdirectory_name="run/001",
                )
            )

    def test_save_snapshot_rejects_uninitialized_camera_before_calling_service(self) -> None:
        camera_service = MagicMock()
        camera_service.get_status.return_value = CameraStatus(is_initialized=False)
        snapshot_service = MagicMock()
        controller = CommandController(camera_service, snapshot_service, MagicMock())
        controller.set_save_directory(Path("captures/default"))

        with self.assertRaisesRegex(RuntimeError, "not initialized"):
            controller.save_snapshot(SnapshotRequest(save_directory=None, file_stem="image_001", file_extension=".png"))

        snapshot_service.save_snapshot.assert_not_called()

    def test_start_recording_rejects_uninitialized_camera_before_calling_service(self) -> None:
        camera_service = MagicMock()
        camera_service.get_status.return_value = CameraStatus(is_initialized=False)
        recording_service = MagicMock()
        controller = CommandController(camera_service, MagicMock(), recording_service)
        controller.set_save_directory(Path("captures/default"))

        with self.assertRaisesRegex(RuntimeError, "not initialized"):
            controller.start_recording(RecordingRequest(save_directory=None, file_stem="series", frame_limit=3))

        recording_service.start_recording.assert_not_called()

    def test_start_interval_capture_uses_default_save_directory_when_request_has_none(self) -> None:
        camera_service = MagicMock()
        interval_capture_service = MagicMock()
        controller = CommandController(MagicMock(), MagicMock(), MagicMock(), interval_capture_service)
        controller.set_save_directory(Path("captures/default"))

        request = IntervalCaptureRequest(save_directory=None, file_stem="interval", interval_seconds=1.0, max_frame_count=3)
        controller.start_interval_capture(request)

        resolved_request = interval_capture_service.start_capture.call_args.args[0]
        self.assertEqual(resolved_request.save_directory, Path("captures/default"))
        self.assertEqual(resolved_request.file_stem, "interval")

    def test_start_interval_capture_request_maps_to_interval_capture_request(self) -> None:
        interval_capture_service = MagicMock()
        interval_capture_service.start_capture.return_value = IntervalCaptureStatus(is_capturing=True, frames_written=0)
        controller = CommandController(MagicMock(), MagicMock(), MagicMock(), interval_capture_service)
        controller.set_save_directory(Path("captures/default"))

        result = controller.start_interval_capture(
            StartIntervalCaptureRequest(
                file_stem="interval",
                interval_seconds=1.0,
                max_frame_count=5,
                duration_seconds=10.0,
            )
        )

        resolved_request = interval_capture_service.start_capture.call_args.args[0]
        self.assertIsInstance(result, IntervalCaptureCommandResult)
        self.assertTrue(result.status.is_capturing)
        self.assertEqual(resolved_request.save_directory, Path("captures/default"))
        self.assertEqual(resolved_request.file_stem, "interval")
        self.assertEqual(resolved_request.interval_seconds, 1.0)
        self.assertEqual(resolved_request.max_frame_count, 5)
        self.assertEqual(resolved_request.duration_seconds, 10.0)

    def test_start_interval_capture_rejects_uninitialized_camera_before_calling_service(self) -> None:
        camera_service = MagicMock()
        camera_service.get_status.return_value = CameraStatus(is_initialized=False)
        interval_capture_service = MagicMock()
        controller = CommandController(camera_service, MagicMock(), MagicMock(), interval_capture_service)
        controller.set_save_directory(Path("captures/default"))

        with self.assertRaisesRegex(RuntimeError, "not initialized"):
            controller.start_interval_capture(
                IntervalCaptureRequest(
                    save_directory=None,
                    file_stem="interval",
                    interval_seconds=1.0,
                    max_frame_count=3,
                )
            )

        interval_capture_service.start_capture.assert_not_called()

    def test_stop_interval_capture_calls_service(self) -> None:
        interval_capture_service = MagicMock()
        interval_capture_service.stop_capture.return_value = IntervalCaptureStatus(is_capturing=False, frames_written=2)
        controller = CommandController(MagicMock(), MagicMock(), MagicMock(), interval_capture_service)

        result = controller.stop_interval_capture(StopIntervalCaptureRequest(reason="external_request"))

        interval_capture_service.stop_capture.assert_called_once_with()
        self.assertIsInstance(result, IntervalCaptureCommandResult)
        self.assertFalse(result.status.is_capturing)
        self.assertEqual(result.status.frames_written, 2)
        self.assertEqual(result.stop_reason, "external_request")

    def test_stop_interval_capture_preserves_request_reason_in_result(self) -> None:
        interval_capture_service = MagicMock()
        interval_capture_service.stop_capture.return_value = IntervalCaptureStatus(is_capturing=False, frames_written=0)
        controller = CommandController(MagicMock(), MagicMock(), MagicMock(), interval_capture_service)

        result = controller.stop_interval_capture(StopIntervalCaptureRequest(reason="host_shutdown"))

        self.assertEqual(result.stop_reason, "host_shutdown")

    @staticmethod
    def _build_capability_profile(**features: FeatureCapability) -> CameraCapabilityProfile:
        return CameraCapabilityProfile(
            probe_utc=None,
            camera_id="CAM-001",
            camera_name="TestCam",
            camera_model="ModelA",
            camera_serial=None,
            interface_id=None,
            feature_count=len(features),
            features=dict(features),
        )


if __name__ == "__main__":
    unittest.main()
