from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from camera_app.models.camera_configuration import CameraConfiguration
from camera_app.models.recording_request import RecordingRequest
from camera_app.models.snapshot_request import SnapshotRequest

if TYPE_CHECKING:
    from camera_app.models.set_save_directory_request import SetSaveDirectoryRequest


def validate_snapshot_request(request: SnapshotRequest) -> None:
    _validate_file_stem(request.file_stem, "SnapshotRequest.file_stem")
    _validate_file_extension(request.file_extension, "SnapshotRequest.file_extension")
    if request.save_directory is not None:
        _validate_directory_path(request.save_directory, "SnapshotRequest.save_directory")


def validate_recording_request(request: RecordingRequest) -> None:
    _validate_file_stem(request.file_stem, "RecordingRequest.file_stem")
    _validate_file_extension(request.file_extension, "RecordingRequest.file_extension")
    if request.save_directory is not None:
        _validate_directory_path(request.save_directory, "RecordingRequest.save_directory")


def validate_save_directory_request(request: "SetSaveDirectoryRequest") -> None:
    _validate_directory_path(request.base_directory, "SetSaveDirectoryRequest.base_directory")
    if request.mode == "new_subdirectory":
        if not request.subdirectory_name:
            raise ValueError("SetSaveDirectoryRequest.subdirectory_name is required for mode 'new_subdirectory'.")
        _validate_path_segment(request.subdirectory_name, "SetSaveDirectoryRequest.subdirectory_name")


def validate_camera_configuration(config: CameraConfiguration) -> None:
    if config.exposure_time_us is not None and config.exposure_time_us <= 0:
        raise ValueError("CameraConfiguration.exposure_time_us must be greater than zero.")
    if config.gain is not None and config.gain < 0:
        raise ValueError("CameraConfiguration.gain must be zero or greater.")
    if config.acquisition_frame_rate is not None and config.acquisition_frame_rate <= 0:
        raise ValueError("CameraConfiguration.acquisition_frame_rate must be greater than zero.")
    for name, value in (
        ("roi_offset_x", config.roi_offset_x),
        ("roi_offset_y", config.roi_offset_y),
        ("roi_width", config.roi_width),
        ("roi_height", config.roi_height),
    ):
        if value is not None and value < 0:
            raise ValueError(f"CameraConfiguration.{name} must be zero or greater.")
    for name, value in (("roi_width", config.roi_width), ("roi_height", config.roi_height)):
        if value == 0:
            raise ValueError(f"CameraConfiguration.{name} must be greater than zero when provided.")


def normalize_file_extension(file_extension: str, field_name: str) -> str:
    stripped_extension = file_extension.strip()
    if not stripped_extension:
        raise ValueError(f"{field_name} must not be empty.")
    if any(separator in stripped_extension for separator in ("/", "\\")):
        raise ValueError(f"{field_name} must be a file extension, not a path.")

    if stripped_extension.startswith("."):
        stripped_extension = stripped_extension[1:]
    if not stripped_extension:
        raise ValueError(f"{field_name} must include characters after '.'.")
    if "." in stripped_extension:
        raise ValueError(f"{field_name} must contain only a single extension segment.")
    if any(character.isspace() for character in stripped_extension):
        raise ValueError(f"{field_name} must not contain whitespace.")
    return f".{stripped_extension}"


def _validate_file_extension(file_extension: str, field_name: str) -> None:
    normalize_file_extension(file_extension, field_name)


def _validate_file_stem(file_stem: str, field_name: str) -> None:
    stripped_stem = file_stem.strip()
    if not stripped_stem:
        raise ValueError(f"{field_name} must not be empty.")
    _validate_path_segment(stripped_stem, field_name)


def _validate_directory_path(path: Path, field_name: str) -> None:
    if str(path).strip() == "":
        raise ValueError(f"{field_name} must not be empty.")


def _validate_path_segment(value: str, field_name: str) -> None:
    if value in {".", ".."}:
        raise ValueError(f"{field_name} must not be '.' or '..'.")
    if any(separator in value for separator in ("/", "\\")):
        raise ValueError(f"{field_name} must not contain path separators.")
