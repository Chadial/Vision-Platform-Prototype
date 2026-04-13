"""Compatibility model facade for the platform namespace."""

from vision_platform.models.apply_configuration_command_result import ApplyConfigurationCommandResult
from vision_platform.models.apply_configuration_request import ApplyConfigurationRequest
from vision_platform.models.artifact_reference import ArtifactReference
from vision_platform.models.artifact_time_context import ArtifactTimeContext
from vision_platform.models.camera_capability_profile import CameraCapabilityProfile, FeatureCapability
from vision_platform.models.camera_capabilities import CameraCapabilities, CapabilityState
from vision_platform.models.camera_configuration import CameraConfiguration
from vision_platform.models.camera_health import CameraHealth
from vision_platform.models.camera_runtime_event import CameraRuntimeEvent
from vision_platform.models.camera_status import CameraStatus
from vision_platform.models.captured_frame import CapturedFrame
from vision_platform.models.interval_capture_command_result import IntervalCaptureCommandResult
from vision_platform.models.interval_capture_request import IntervalCaptureRequest
from vision_platform.models.interval_capture_status import IntervalCaptureStatus
from vision_platform.models.preview_frame_info import PreviewFrameInfo
from vision_platform.models.recording_command_result import RecordingCommandResult
from vision_platform.models.recording_request import RecordingRequest
from vision_platform.models.recording_status import RecordingStatus
from vision_platform.models.save_directory_command_result import SaveDirectoryCommandResult
from vision_platform.models.save_snapshot_request import SaveSnapshotRequest
from vision_platform.models.save_snapshot_result import SaveSnapshotResult
from vision_platform.models.snapshot_command_result import SnapshotCommandResult
from vision_platform.models.set_save_directory_request import SetSaveDirectoryRequest
from vision_platform.models.set_save_directory_result import SetSaveDirectoryResult
from vision_platform.models.snapshot_request import SnapshotRequest
from vision_platform.models.start_interval_capture_request import StartIntervalCaptureRequest
from vision_platform.models.start_recording_request import StartRecordingRequest
from vision_platform.models.stop_interval_capture_request import StopIntervalCaptureRequest
from vision_platform.models.stop_recording_request import StopRecordingRequest
from vision_platform.models.subsystem_status import SubsystemStatus

__all__ = [
    "ApplyConfigurationCommandResult",
    "ApplyConfigurationRequest",
    "ArtifactReference",
    "ArtifactTimeContext",
    "CameraCapabilityProfile",
    "CameraCapabilities",
    "CameraConfiguration",
    "CameraHealth",
    "CameraRuntimeEvent",
    "CameraStatus",
    "CapabilityState",
    "CapturedFrame",
    "IntervalCaptureCommandResult",
    "FeatureCapability",
    "IntervalCaptureRequest",
    "IntervalCaptureStatus",
    "PreviewFrameInfo",
    "RecordingCommandResult",
    "RecordingRequest",
    "RecordingStatus",
    "SaveDirectoryCommandResult",
    "SaveSnapshotRequest",
    "SaveSnapshotResult",
    "SnapshotCommandResult",
    "SetSaveDirectoryRequest",
    "SetSaveDirectoryResult",
    "SnapshotRequest",
    "StartIntervalCaptureRequest",
    "StartRecordingRequest",
    "StopIntervalCaptureRequest",
    "StopRecordingRequest",
    "SubsystemStatus",
]
