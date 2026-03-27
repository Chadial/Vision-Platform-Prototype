from __future__ import annotations

from pathlib import Path

from vision_platform.models import SnapshotRequest
from vision_platform.services.recording_service import FrameWriter, build_snapshot_path
from vision_platform.services.stream_service.preview_service import PreviewService


class PreviewSnapshotSaver:
    """Save the latest preview frame without triggering a competing hardware snapshot call."""

    def __init__(
        self,
        preview_service: PreviewService,
        save_directory: Path,
        file_stem: str = "preview_snapshot",
        file_extension: str = ".png",
        frame_writer: FrameWriter | None = None,
    ) -> None:
        self._preview_service = preview_service
        self._save_directory = save_directory
        self._file_stem = file_stem
        self._file_extension = file_extension
        self._frame_writer = frame_writer or FrameWriter()
        self._next_index = 0

    def save_latest_frame(self) -> Path:
        frame = self._preview_service.get_latest_frame()
        if frame is None:
            raise RuntimeError("No preview frame available.")

        request = SnapshotRequest(
            save_directory=self._save_directory,
            file_stem=f"{self._file_stem}_{self._next_index:06d}",
            file_extension=self._file_extension,
        )
        target_path = build_snapshot_path(request)
        saved_path = self._frame_writer.write_frame(
            frame,
            target_path,
            create_directories=request.create_directories,
        )
        self._next_index += 1
        return saved_path


__all__ = ["PreviewSnapshotSaver"]
