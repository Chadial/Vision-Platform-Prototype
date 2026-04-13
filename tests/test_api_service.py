from dataclasses import asdict
from pathlib import Path
import unittest

from tests import _path_setup
from vision_platform.models import CameraConfiguration, CameraStatus, IntervalCaptureStatus, RecordingStatus, SubsystemStatus
from vision_platform.models import CameraCapabilities, CameraHealth, CapabilityState
from vision_platform.services.api_service import (
    ApiCommandEnvelopePayload,
    ApiCameraCapabilitiesPayload,
    ApiCameraHealthPayload,
    ApiSubsystemStatusPayload,
    build_error_command_payload,
    build_success_command_payload,
    map_camera_capabilities_to_api_payload,
    map_camera_health_to_api_payload,
    map_subsystem_status_to_api_payload,
)


class ApiServiceTests(unittest.TestCase):
    def test_map_subsystem_status_to_api_payload_converts_paths_and_nested_models(self) -> None:
        status = SubsystemStatus(
            camera=CameraStatus(
                is_initialized=True,
                is_acquiring=False,
                source_kind="simulation",
                driver_name="SimulatedCameraDriver",
                camera_id="sim-api",
                capabilities_available=True,
            ),
            configuration=CameraConfiguration(
                exposure_time_us=2500.0,
                pixel_format="Mono8",
                roi_width=320,
                roi_height=240,
            ),
            recording=RecordingStatus(
                is_recording=True,
                frames_written=12,
                dropped_frames=1,
                save_directory=Path("C:/captures/recording"),
                active_file_stem="recording",
                run_id="recording@2026-03-30T12:00:00+00:00",
            ),
            interval_capture=IntervalCaptureStatus(
                is_capturing=False,
                frames_written=3,
                skipped_intervals=0,
                save_directory=Path("C:/captures/interval"),
                active_file_stem="interval",
            ),
            default_save_directory=Path("C:/captures"),
            is_save_directory_configured=True,
            has_interval_capture_service=True,
            can_apply_configuration=True,
            can_save_snapshot=True,
            can_start_recording=False,
            can_stop_recording=True,
            can_start_interval_capture=True,
            can_stop_interval_capture=False,
        )

        payload = map_subsystem_status_to_api_payload(status)

        self.assertIsInstance(payload, ApiSubsystemStatusPayload)
        self.assertEqual(payload.camera.camera_id, "sim-api")
        self.assertEqual(payload.configuration.pixel_format, "Mono8")
        self.assertEqual(payload.recording.save_directory, str(Path("C:/captures/recording")))
        self.assertEqual(payload.recording.run_id, "recording@2026-03-30T12:00:00+00:00")
        self.assertEqual(payload.interval_capture.save_directory, str(Path("C:/captures/interval")))
        self.assertIsNotNone(payload.active_run)
        self.assertEqual(payload.active_run.operation_kind, "recording")
        self.assertEqual(payload.active_run.active_file_stem, "recording")
        self.assertEqual(payload.active_run.run_id, "recording@2026-03-30T12:00:00+00:00")
        self.assertEqual(payload.default_save_directory, str(Path("C:/captures")))
        self.assertTrue(payload.can_save_snapshot)

    def test_map_subsystem_status_to_api_payload_exposes_interval_capture_active_run_when_recording_is_idle(self) -> None:
        status = SubsystemStatus(
            camera=CameraStatus(is_initialized=True, camera_id="sim-api"),
            configuration=None,
            recording=RecordingStatus(
                is_recording=False,
                frames_written=12,
                save_directory=Path("C:/captures/recording"),
                active_file_stem="recording",
            ),
            interval_capture=IntervalCaptureStatus(
                is_capturing=True,
                frames_written=3,
                skipped_intervals=1,
                save_directory=Path("C:/captures/interval"),
                active_file_stem="interval",
                last_error="late frame skipped",
            ),
        )

        payload = map_subsystem_status_to_api_payload(status)

        self.assertIsNotNone(payload.active_run)
        self.assertEqual(payload.active_run.operation_kind, "interval_capture")
        self.assertEqual(payload.active_run.save_directory, str(Path("C:/captures/interval")))
        self.assertEqual(payload.active_run.frames_written, 3)
        self.assertEqual(payload.active_run.last_error, "late frame skipped")

    def test_map_subsystem_status_to_api_payload_leaves_active_run_empty_when_no_operation_is_active(self) -> None:
        status = SubsystemStatus(
            camera=CameraStatus(),
            configuration=None,
            recording=RecordingStatus(
                is_recording=False,
                frames_written=4,
                save_directory=Path("C:/captures/recording"),
                active_file_stem="recording",
                last_error="writer recovered",
            ),
            interval_capture=IntervalCaptureStatus(
                is_capturing=False,
                frames_written=2,
                save_directory=Path("C:/captures/interval"),
                active_file_stem="interval",
                last_error="capture completed",
            ),
        )

        payload = map_subsystem_status_to_api_payload(status)

        self.assertIsNone(payload.active_run)

    def test_api_payload_is_dataclass_serializable(self) -> None:
        status = SubsystemStatus(
            camera=CameraStatus(),
            configuration=None,
            recording=RecordingStatus(),
            interval_capture=IntervalCaptureStatus(),
        )

        payload_dict = asdict(map_subsystem_status_to_api_payload(status))

        self.assertIn("camera", payload_dict)
        self.assertIn("recording", payload_dict)
        self.assertIn("active_run", payload_dict)
        self.assertIsNone(payload_dict["default_save_directory"])
        self.assertIsNone(payload_dict["active_run"])
        self.assertFalse(payload_dict["can_save_snapshot"])

    def test_build_success_command_payload_reuses_status_mapper(self) -> None:
        status = SubsystemStatus(
            camera=CameraStatus(camera_id="sim-api"),
            configuration=None,
            recording=RecordingStatus(),
            interval_capture=IntervalCaptureStatus(),
        )

        payload = build_success_command_payload(
            command="status",
            source="simulated",
            result={"status_source": "poll"},
            status=status,
        )

        self.assertIsInstance(payload, ApiCommandEnvelopePayload)
        self.assertTrue(payload.success)
        self.assertEqual(payload.command, "status")
        self.assertEqual(payload.source, "simulated")
        self.assertEqual(payload.result["status_source"], "poll")
        self.assertEqual(payload.status.camera.camera_id, "sim-api")
        self.assertIsNone(payload.error)

    def test_build_error_command_payload_returns_bounded_error_envelope(self) -> None:
        payload = build_error_command_payload(
            code="configuration_error",
            message="roi_width invalid",
            details={"stage": "apply_configuration"},
        )

        self.assertFalse(payload.success)
        self.assertIsNone(payload.command)
        self.assertIsNone(payload.source)
        self.assertIsNone(payload.result)
        self.assertIsNone(payload.status)
        self.assertEqual(payload.error.code, "configuration_error")
        self.assertEqual(payload.error.message, "roi_width invalid")
        self.assertEqual(payload.error.details["stage"], "apply_configuration")

    def test_map_camera_health_to_api_payload_is_dataclass_serializable(self) -> None:
        payload = map_camera_health_to_api_payload(
            CameraHealth(
                availability=True,
                readiness=True,
                degraded=False,
                faulted=False,
                last_error=None,
                capabilities_available=True,
                recording_impaired=None,
            )
        )

        self.assertIsInstance(payload, ApiCameraHealthPayload)
        self.assertEqual(asdict(payload)["availability"], True)
        self.assertIn("recording_impaired", asdict(payload))

    def test_map_camera_capabilities_to_api_payload_preserves_supported_available_enabled_split(self) -> None:
        payload = map_camera_capabilities_to_api_payload(
            CameraCapabilities(
                capability_profile_available=True,
                capability_probe_warning="probe warning",
                exposure_time_control=CapabilityState(True, True, True),
                gain_control=CapabilityState(True, True, False),
                pixel_format_control=CapabilityState(True, True, True),
                acquisition_frame_rate_control=CapabilityState(True, False, False),
                roi_control=CapabilityState(True, True, False),
                snapshot=CapabilityState(True, True, True),
                recording=CapabilityState(True, True, False),
                interval_capture=CapabilityState(False, False, False),
            )
        )

        self.assertIsInstance(payload, ApiCameraCapabilitiesPayload)
        self.assertTrue(payload.capability_profile_available)
        self.assertEqual(payload.capability_probe_warning, "probe warning")
        self.assertTrue(payload.exposure_time_control.currently_enabled)
        self.assertFalse(payload.gain_control.currently_enabled)
        self.assertFalse(payload.acquisition_frame_rate_control.currently_available)
        self.assertFalse(payload.interval_capture.supported)


if __name__ == "__main__":
    unittest.main()
