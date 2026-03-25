from pathlib import Path

from camera_app.models.recording_request import RecordingRequest
from camera_app.models.snapshot_request import SnapshotRequest


def build_snapshot_path(request: SnapshotRequest) -> Path:
    if request.save_directory is None:
        raise ValueError("SnapshotRequest.save_directory must be set before saving.")
    extension = request.file_extension if request.file_extension.startswith(".") else f".{request.file_extension}"
    return request.save_directory / f"{request.file_stem}{extension}"


def build_recording_frame_path(request: RecordingRequest, frame_index: int) -> Path:
    if frame_index < 0:
        raise ValueError("frame_index must be zero or greater.")
    if request.save_directory is None:
        raise ValueError("RecordingRequest.save_directory must be set before recording.")

    extension = request.file_extension if request.file_extension.startswith(".") else f".{request.file_extension}"
    return request.save_directory / f"{request.file_stem}_{frame_index:06d}{extension}"


def build_recording_log_path(request: RecordingRequest) -> Path:
    if request.save_directory is None:
        raise ValueError("RecordingRequest.save_directory must be set before recording.")
    return request.save_directory / f"{request.file_stem}_recording_log.csv"
