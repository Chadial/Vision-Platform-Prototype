import re
from pathlib import Path

from camera_app.validation.request_validation import (
    normalize_file_extension,
    validate_interval_capture_request,
    validate_recording_request,
    validate_snapshot_request,
)
from vision_platform.models import IntervalCaptureRequest, RecordingRequest, SnapshotRequest
from vision_platform.services.recording_service.traceability import load_trace_logs_for_directory

_SNAPSHOT_SUFFIX_RE = re.compile(r"^(?P<stem>.+)_(?P<index>\d+)$")
_RECORDING_INDEXED_RE = re.compile(r"^(?P<stem>.+)_(?P<index>\d+)$")


def build_snapshot_path(request: SnapshotRequest) -> Path:
    validate_snapshot_request(request)
    if request.save_directory is None:
        raise ValueError("SnapshotRequest.save_directory must be set before saving.")
    extension = normalize_file_extension(request.file_extension, "SnapshotRequest.file_extension")
    return request.save_directory / f"{request.file_stem}{extension}"


def build_next_snapshot_path(request: SnapshotRequest) -> Path:
    validate_snapshot_request(request)
    if request.save_directory is None:
        raise ValueError("SnapshotRequest.save_directory must be set before saving.")

    extension = normalize_file_extension(request.file_extension, "SnapshotRequest.file_extension")
    next_index = resolve_next_snapshot_index(
        save_directory=request.save_directory,
        file_stem=request.file_stem,
        file_extension=extension,
    )
    return request.save_directory / f"{request.file_stem}_{next_index:06d}{extension}"


def build_recording_frame_path(request: RecordingRequest, frame_index: int) -> Path:
    validate_recording_request(request)
    if frame_index < 0:
        raise ValueError("frame_index must be zero or greater.")
    if request.save_directory is None:
        raise ValueError("RecordingRequest.save_directory must be set before recording.")

    extension = normalize_file_extension(request.file_extension, "RecordingRequest.file_extension")
    return request.save_directory / f"{request.file_stem}_{frame_index:06d}{extension}"


def resolve_next_recording_frame_index(
    *,
    save_directory: Path | None,
    file_stem: str,
    file_extension: str,
) -> int:
    if save_directory is None:
        raise ValueError("save_directory must be set before resolving recording index.")
    extension = normalize_file_extension(file_extension, "RecordingRequest.file_extension")
    max_index = -1
    for image_name in _iter_known_artifact_names(save_directory):
        parsed_index = _parse_recording_index(image_name, file_stem=file_stem, extension=extension)
        if parsed_index is not None:
            max_index = max(max_index, parsed_index)
    return max_index + 1


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


def build_recording_log_path_for_run(request: RecordingRequest, *, start_frame_index: int) -> Path:
    validate_recording_request(request)
    if request.save_directory is None:
        raise ValueError("RecordingRequest.save_directory must be set before recording.")
    if start_frame_index <= 0:
        return build_recording_log_path(request)
    return request.save_directory / f"{request.file_stem}_recording_log_{start_frame_index:06d}.csv"


def resolve_next_snapshot_index(
    *,
    save_directory: Path | None,
    file_stem: str,
    file_extension: str,
) -> int:
    if save_directory is None:
        raise ValueError("save_directory must be set before resolving snapshot index.")
    extension = normalize_file_extension(file_extension, "SnapshotRequest.file_extension")
    max_index = -1
    for image_name in _iter_known_artifact_names(save_directory):
        parsed_index = _parse_snapshot_index(image_name, file_stem=file_stem, extension=extension)
        if parsed_index is not None:
            max_index = max(max_index, parsed_index)
    return max_index + 1


def _iter_known_artifact_names(save_directory: Path):
    if save_directory.exists():
        for path in save_directory.iterdir():
            if path.is_file():
                yield path.name
    if save_directory.exists():
        trace_log_data = load_trace_logs_for_directory(save_directory)
        for image_name in trace_log_data.rows_by_image_name:
            yield image_name


def _parse_recording_index(image_name: str, *, file_stem: str, extension: str) -> int | None:
    if not image_name.endswith(extension):
        return None
    stem_name = image_name[: -len(extension)]
    match = _RECORDING_INDEXED_RE.fullmatch(stem_name)
    if match is None:
        return None
    if match.group("stem") != file_stem:
        return None
    try:
        return int(match.group("index"))
    except ValueError:
        return None


def _parse_snapshot_index(image_name: str, *, file_stem: str, extension: str) -> int | None:
    if not image_name.endswith(extension):
        return None
    stem_name = image_name[: -len(extension)]
    if stem_name == file_stem:
        return 0
    match = _SNAPSHOT_SUFFIX_RE.fullmatch(stem_name)
    if match is None:
        return None
    if match.group("stem") != file_stem:
        return None
    try:
        return int(match.group("index"))
    except ValueError:
        return None

__all__ = [
    "build_next_snapshot_path",
    "build_interval_capture_frame_path",
    "build_recording_frame_path",
    "build_recording_log_path",
    "build_recording_log_path_for_run",
    "build_snapshot_path",
    "resolve_next_recording_frame_index",
    "resolve_next_snapshot_index",
]
