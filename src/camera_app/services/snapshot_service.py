import logging
from pathlib import Path
from typing import Callable

from camera_app.drivers.camera_driver import CameraDriver
from camera_app.models.camera_configuration import CameraConfiguration
from camera_app.models.snapshot_request import SnapshotRequest
from camera_app.validation.request_validation import validate_snapshot_request
from vision_platform.services.recording_service.artifact_focus_metadata_producer import ArtifactFocusMetadataProducer
from vision_platform.services.recording_service.file_naming import build_next_snapshot_path
from vision_platform.services.recording_service.frame_writer import FrameWriter
from vision_platform.services.recording_service.recording_log import append_recording_log_row, build_recording_log_path, open_recording_log
from vision_platform.services.recording_service.traceability import record_snapshot_trace


class SnapshotService:
    def __init__(
        self,
        driver: CameraDriver,
        frame_writer: FrameWriter | None = None,
        configuration_provider: Callable[[], CameraConfiguration | None] | None = None,
        artifact_focus_metadata_producer: ArtifactFocusMetadataProducer | None = None,
    ) -> None:
        self._driver = driver
        self._frame_writer = frame_writer or FrameWriter()
        self._configuration_provider = configuration_provider
        self._artifact_focus_metadata_producer = artifact_focus_metadata_producer
        self._logger = logging.getLogger(__name__)

    def save_snapshot(self, request: SnapshotRequest) -> Path:
        validate_snapshot_request(request)
        target_path = build_next_snapshot_path(request)
        self._logger.info("Saving snapshot to '%s'.", target_path)

        try:
            frame = self._driver.capture_snapshot()
            saved_path = self._frame_writer.write_frame(
                frame,
                target_path,
                create_directories=request.create_directories,
            )
            recording_log_path = build_recording_log_path(request.save_directory)
            recording_log_handle, recording_log_writer, _is_new_log = open_recording_log(
                recording_log_path,
                create_directories=request.create_directories,
            )
            try:
                append_recording_log_row(
                    recording_log_writer,
                    recording_log_handle,
                    image_name=saved_path.name,
                    frame_id=frame.frame_id,
                    camera_timestamp=frame.camera_timestamp,
                    system_timestamp_utc=frame.timestamp_utc.isoformat(),
                )
            finally:
                recording_log_handle.close()
            configuration = self._configuration_provider() if self._configuration_provider is not None else None
            artifact_metadata = (
                self._artifact_focus_metadata_producer.build_metadata(frame)
                if self._artifact_focus_metadata_producer is not None
                else None
            )
            record_snapshot_trace(saved_path, request, frame, configuration, artifact_metadata=artifact_metadata)
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
