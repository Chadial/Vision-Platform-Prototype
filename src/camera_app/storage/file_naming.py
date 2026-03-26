from pathlib import Path

from camera_app.models.interval_capture_request import IntervalCaptureRequest
from camera_app.models.recording_request import RecordingRequest
from camera_app.models.snapshot_request import SnapshotRequest
from camera_app.validation.request_validation import (
    normalize_file_extension,
    validate_interval_capture_request,
    validate_recording_request,
    validate_snapshot_request,
)


def build_snapshot_path(request: SnapshotRequest) -> Path:
    validate_snapshot_request(request)
    if request.save_directory is None:
        raise ValueError("SnapshotRequest.save_directory must be set before saving.")
    extension = normalize_file_extension(request.file_extension, "SnapshotRequest.file_extension")
    return request.save_directory / f"{request.file_stem}{extension}"


def build_recording_frame_path(request: RecordingRequest, frame_index: int) -> Path:
    validate_recording_request(request)
    if frame_index < 0:
        raise ValueError("frame_index must be zero or greater.")
    if request.save_directory is None:
        raise ValueError("RecordingRequest.save_directory must be set before recording.")

    extension = normalize_file_extension(request.file_extension, "RecordingRequest.file_extension")
    return request.save_directory / f"{request.file_stem}_{frame_index:06d}{extension}"


def build_interval_capture_frame_path(request: IntervalCaptureRequest, frame_index: int) -> Path:
    validate_interval_capture_request(request)
    if frame_index < 0:
        raise ValueError("frame_index must be zero or greater.")
    if request.save_directory is None:
        raise ValueError("IntervalCaptureRequest.save_directory must be set before interval capture.")

    extension = normalize_file_extension(request.file_extension, "IntervalCaptureRequest.file_extension")
    return request.save_directory / f"{request.file_stem}_{frame_index:06d}{extension}"


def build_recording_log_path(request: RecordingRequest) -> Path:
    validate_recording_request(request)
    if request.save_directory is None:
        raise ValueError("RecordingRequest.save_directory must be set before recording.")
    return request.save_directory / f"{request.file_stem}_recording_log.csv"
