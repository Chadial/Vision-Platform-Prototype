import logging
from pathlib import Path

from camera_app.drivers.camera_driver import CameraDriver
from camera_app.models.snapshot_request import SnapshotRequest
from camera_app.storage.file_naming import build_snapshot_path
from camera_app.storage.frame_writer import FrameWriter
from camera_app.validation.request_validation import validate_snapshot_request


class SnapshotService:
    def __init__(self, driver: CameraDriver, frame_writer: FrameWriter | None = None) -> None:
        self._driver = driver
        self._frame_writer = frame_writer or FrameWriter()
        self._logger = logging.getLogger(__name__)

    def save_snapshot(self, request: SnapshotRequest) -> Path:
        validate_snapshot_request(request)
        target_path = build_snapshot_path(request)
        self._logger.info("Saving snapshot to '%s'.", target_path)

        try:
            frame = self._driver.capture_snapshot()
            saved_path = self._frame_writer.write_frame(
                frame,
                target_path,
                create_directories=request.create_directories,
            )
        except Exception:
            self._logger.exception("Snapshot save failed for '%s'.", target_path)
            raise

        self._logger.info(
            "Snapshot saved to '%s' (frame_id=%s, size=%sx%s, pixel_format=%s).",
            saved_path,
            frame.frame_id,
            frame.width,
            frame.height,
            frame.pixel_format,
        )
        return saved_path
