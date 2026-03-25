from pathlib import Path

from camera_app.models.snapshot_request import SnapshotRequest


def build_snapshot_path(request: SnapshotRequest) -> Path:
    extension = request.file_extension if request.file_extension.startswith(".") else f".{request.file_extension}"
    return request.save_directory / f"{request.file_stem}{extension}"

