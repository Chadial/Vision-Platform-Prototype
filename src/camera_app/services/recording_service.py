from __future__ import annotations

import csv
from dataclasses import replace
import logging
from datetime import datetime, timezone
from queue import Empty, Full, Queue
from threading import current_thread, Event, Lock, Thread
from time import monotonic, sleep
from typing import Callable, TextIO

from camera_app.drivers.camera_driver import CameraDriver
from camera_app.models.camera_configuration import CameraConfiguration
from camera_app.models.captured_frame import CapturedFrame
from camera_app.models.recording_request import RecordingRequest
from camera_app.models.recording_status import RecordingStatus
from camera_app.services.shared_frame_source import SharedFrameSource
from camera_app.validation.request_validation import validate_recording_request
from vision_platform.services.recording_service.artifact_focus_metadata_producer import ArtifactFocusMetadataProducer
from vision_platform.services.recording_service.file_naming import build_recording_frame_path, build_recording_log_path
from vision_platform.services.recording_service.frame_writer import FrameWriter
from vision_platform.services.recording_service.traceability import (
    append_trace_image_row,
    append_trace_run_end,
    append_trace_run_start,
    build_bounded_recording_run_id,
    build_recording_stable_context,
    open_trace_log,
    resolve_trace_log_path,
)


class RecordingService:
    def __init__(
        self,
        driver: CameraDriver,
        frame_writer: FrameWriter | None = None,
        poll_interval_seconds: float = 0.01,
        configuration_provider: Callable[[], CameraConfiguration | None] | None = None,
        shared_frame_source: SharedFrameSource | None = None,
        artifact_focus_metadata_producer: ArtifactFocusMetadataProducer | None = None,
    ) -> None:
        self._driver = driver
        self._frame_writer = frame_writer or FrameWriter()
        self._poll_interval_seconds = poll_interval_seconds
        self._configuration_provider = configuration_provider
        self._shared_frame_source = shared_frame_source
        self._artifact_focus_metadata_producer = artifact_focus_metadata_producer
        self._logger = logging.getLogger(__name__)
        self._status_lock = Lock()
        self._status = RecordingStatus()
        self._active_request: RecordingRequest | None = None
        self._frame_queue: Queue[tuple[int, CapturedFrame]] | None = None
        self._producer_thread: Thread | None = None
        self._writer_thread: Thread | None = None
        self._stop_event = Event()
        self._cleanup_lock = Lock()
        self._acquisition_stopped = False
        self._acquisition_started = False
        self._recording_deadline: float | None = None
        self._next_frame_due_at: float | None = None
        self._recording_log_handle: TextIO | None = None
        self._recording_log_writer: csv.writer | None = None
        self._recording_session_started_utc: str | None = None
        self._trace_log_handle: TextIO | None = None
        self._trace_log_writer: csv.writer | None = None
        self._trace_run_id: str | None = None
        self._last_completed_run_id: str | None = None

    def start_recording(self, request: RecordingRequest) -> RecordingStatus:
        self._validate_request(request)
        self.stop_recording()
        try:
            with self._status_lock:
                self._status = RecordingStatus(
                    is_recording=True,
                    save_directory=request.save_directory,
                    active_file_stem=request.file_stem,
                )

            self._active_request = request
            self._frame_queue = Queue(maxsize=request.queue_size)
            self._stop_event.clear()
            self._last_completed_run_id = None
            self._acquisition_stopped = False
            self._recording_session_started_utc = self._current_system_time_utc()
            self._recording_deadline = (
                monotonic() + request.duration_seconds if request.duration_seconds is not None else None
            )
            self._next_frame_due_at = monotonic()
            if self._artifact_focus_metadata_producer is not None:
                self._artifact_focus_metadata_producer.reset()
            self._open_recording_log(request)
            self._open_traceability_log(request)
            with self._status_lock:
                self._status.run_id = self._trace_run_id
            if self._shared_frame_source is not None:
                self._shared_frame_source.acquire()
            else:
                self._driver.start_acquisition()
            self._acquisition_started = True

            self._producer_thread = Thread(target=self._producer_loop, name="RecordingProducer", daemon=True)
            self._writer_thread = Thread(target=self._writer_loop, name="RecordingWriter", daemon=True)
            self._producer_thread.start()
            self._writer_thread.start()
            return self.get_status()
        except Exception as exc:
            self._record_error(f"Recording startup failed: {exc}")
            self._stop_event.set()
            self._finalize_recording(suppress_errors=True)
            raise

    def stop_recording(self) -> RecordingStatus:
        active_run_id = self._trace_run_id or self._last_completed_run_id
        self._stop_event.set()

        active_thread = current_thread()
        if self._producer_thread is not None and self._producer_thread is not active_thread:
            self._producer_thread.join(timeout=1.0)
        if self._writer_thread is not None and self._writer_thread is not active_thread:
            self._writer_thread.join(timeout=1.0)

        self._finalize_recording()
        return replace(self.get_status(), run_id=active_run_id)

    def get_status(self) -> RecordingStatus:
        with self._status_lock:
            return RecordingStatus(
                is_recording=self._status.is_recording,
                frames_written=self._status.frames_written,
                dropped_frames=self._status.dropped_frames,
                save_directory=self._status.save_directory,
                active_file_stem=self._status.active_file_stem,
                run_id=self._status.run_id,
                last_error=self._status.last_error,
            )

    def _validate_request(self, request: RecordingRequest) -> None:
        validate_recording_request(request)
        if not request.file_stem:
            raise ValueError("RecordingRequest.file_stem must not be empty.")
        if request.queue_size <= 0:
            raise ValueError("RecordingRequest.queue_size must be greater than zero.")
        if request.frame_limit is None and request.duration_seconds is None:
            raise ValueError("RecordingRequest requires frame_limit or duration_seconds.")
        if request.frame_limit is not None and request.frame_limit <= 0:
            raise ValueError("RecordingRequest.frame_limit must be greater than zero.")
        if request.duration_seconds is not None and request.duration_seconds <= 0:
            raise ValueError("RecordingRequest.duration_seconds must be greater than zero.")
        if request.target_frame_rate is not None and request.target_frame_rate <= 0:
            raise ValueError("RecordingRequest.target_frame_rate must be greater than zero.")

    def _producer_loop(self) -> None:
        assert self._frame_queue is not None
        assert self._active_request is not None

        next_frame_index = 0
        last_frame_key = None

        while not self._stop_event.is_set():
            if self._recording_deadline is not None and monotonic() >= self._recording_deadline:
                self._stop_event.set()
                break
            if self._active_request.frame_limit is not None and next_frame_index >= self._active_request.frame_limit:
                self._stop_event.set()
                break
            if self._active_request.target_frame_rate is not None:
                assert self._next_frame_due_at is not None
                now = monotonic()
                if now < self._next_frame_due_at:
                    sleep(min(self._next_frame_due_at - now, self._poll_interval_seconds))
                    continue

            try:
                frame = (
                    self._shared_frame_source.get_latest_frame()
                    if self._shared_frame_source is not None
                    else self._driver.get_latest_frame()
                )
                if frame is None:
                    sleep(self._poll_interval_seconds)
                    continue

                frame_key = (frame.frame_id, id(frame.raw_frame))
                if frame_key == last_frame_key:
                    sleep(self._poll_interval_seconds)
                    continue

                self._frame_queue.put((next_frame_index, frame), timeout=self._poll_interval_seconds)
                last_frame_key = frame_key
                next_frame_index += 1
                if self._active_request.target_frame_rate is not None:
                    self._next_frame_due_at = monotonic() + (1.0 / self._active_request.target_frame_rate)
            except Full:
                with self._status_lock:
                    self._status.dropped_frames += 1
            except Exception as exc:
                self._record_error(f"Recording acquisition failed: {exc}")
                self._stop_event.set()
                break

        self._stop_event.set()

    def _writer_loop(self) -> None:
        assert self._frame_queue is not None
        assert self._active_request is not None

        while not self._stop_event.is_set() or not self._frame_queue.empty():
            try:
                frame_index, frame = self._frame_queue.get(timeout=self._poll_interval_seconds)
            except Empty:
                continue

            try:
                target_path = build_recording_frame_path(self._active_request, frame_index)
                self._frame_writer.write_frame(
                    frame,
                    target_path,
                    create_directories=self._active_request.create_directories,
                )
                self._write_recording_log_entry(target_path.name, frame)
                self._write_traceability_entry(target_path.name, frame)
                with self._status_lock:
                    self._status.frames_written += 1
                    if (
                        self._active_request.frame_limit is not None
                        and self._status.frames_written >= self._active_request.frame_limit
                    ):
                        self._stop_event.set()
            except Exception as exc:
                self._record_error(f"Recording write failed: {exc}")
                self._stop_event.set()
            finally:
                self._frame_queue.task_done()

        self._finalize_recording(suppress_errors=True)

    def _record_error(self, message: str) -> None:
        self._logger.error(message, exc_info=True)
        with self._status_lock:
            self._status.last_error = message

    def _open_recording_log(self, request: RecordingRequest) -> None:
        log_path = build_recording_log_path(request)
        if request.create_directories:
            log_path.parent.mkdir(parents=True, exist_ok=True)

        self._recording_log_handle = log_path.open("w", newline="", encoding="utf-8")
        self._recording_log_writer = csv.writer(self._recording_log_handle)
        session_configuration = self._configuration_provider() if self._configuration_provider is not None else None
        for key, value in self._build_recording_log_metadata(request, session_configuration):
            self._recording_log_handle.write(f"# {key}: {value}\n")
        self._recording_log_writer.writerow(
            [
                "image_name",
                "frame_id",
                "camera_timestamp",
                "system_timestamp_utc",
            ]
        )
        self._recording_log_handle.flush()

    def _open_traceability_log(self, request: RecordingRequest) -> None:
        configuration = self._configuration_provider() if self._configuration_provider is not None else None
        stable_context = build_recording_stable_context(request, configuration)
        log_path, reused_existing_log = resolve_trace_log_path(request.save_directory, stable_context)
        self._trace_log_handle, self._trace_log_writer = open_trace_log(
            log_path,
            stable_context,
            reused_existing_log=reused_existing_log,
        )
        self._trace_run_id = build_bounded_recording_run_id(
            request.file_stem,
            self._recording_session_started_utc or self._current_system_time_utc(),
        )
        append_trace_run_start(
            self._trace_log_handle,
            "bounded_recording",
            self._trace_run_id,
            request.file_stem,
            self._recording_session_started_utc,
            request.frame_limit,
            request.duration_seconds,
            request.target_frame_rate,
        )

    def _build_recording_log_metadata(
        self,
        request: RecordingRequest,
        configuration: CameraConfiguration | None,
    ) -> list[tuple[str, str]]:
        return [
            ("recording_start_signal_utc", self._recording_session_started_utc or self._current_system_time_utc()),
            ("save_directory", str(request.save_directory)),
            ("file_stem", request.file_stem),
            ("file_extension", request.file_extension),
            ("camera_id", request.camera_id or ""),
            ("frame_limit", "" if request.frame_limit is None else str(request.frame_limit)),
            ("duration_seconds", "" if request.duration_seconds is None else str(request.duration_seconds)),
            ("target_frame_rate", "" if request.target_frame_rate is None else str(request.target_frame_rate)),
            ("continues_previous_series", "false"),
            (
                "exposure_time_us",
                "" if configuration is None or configuration.exposure_time_us is None else str(configuration.exposure_time_us),
            ),
            ("gain", "" if configuration is None or configuration.gain is None else str(configuration.gain)),
            (
                "pixel_format",
                "" if configuration is None or configuration.pixel_format is None else str(configuration.pixel_format),
            ),
            (
                "acquisition_frame_rate",
                ""
                if configuration is None or configuration.acquisition_frame_rate is None
                else str(configuration.acquisition_frame_rate),
            ),
            (
                "roi_x",
                "" if configuration is None or configuration.roi_offset_x is None else str(configuration.roi_offset_x),
            ),
            (
                "roi_y",
                "" if configuration is None or configuration.roi_offset_y is None else str(configuration.roi_offset_y),
            ),
            (
                "roi_width",
                "" if configuration is None or configuration.roi_width is None else str(configuration.roi_width),
            ),
            (
                "roi_height",
                "" if configuration is None or configuration.roi_height is None else str(configuration.roi_height),
            ),
        ]

    def _write_recording_log_entry(self, image_name: str, frame: CapturedFrame) -> None:
        if self._recording_log_writer is None or self._recording_log_handle is None:
            raise RuntimeError("Recording log is not initialized.")

        self._recording_log_writer.writerow(
            [
                image_name,
                frame.frame_id,
                frame.camera_timestamp,
                frame.timestamp_utc.isoformat(),
            ]
        )
        self._recording_log_handle.flush()

    def _write_traceability_entry(self, image_name: str, frame: CapturedFrame) -> None:
        if self._trace_log_writer is None or self._trace_log_handle is None or self._trace_run_id is None:
            raise RuntimeError("Recording traceability log is not initialized.")

        append_trace_image_row(
            self._trace_log_writer,
            self._trace_log_handle,
            "bounded_recording",
            self._trace_run_id,
            image_name,
            frame,
            artifact_metadata=(
                self._artifact_focus_metadata_producer.build_metadata(frame)
                if self._artifact_focus_metadata_producer is not None
                else None
            ),
        )

    @staticmethod
    def _current_system_time_utc() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _finalize_recording(self, suppress_errors: bool = False) -> None:
        with self._cleanup_lock:
            stop_error: Exception | None = None
            traceability_error: Exception | None = None
            has_active_recording = (
                self._active_request is not None
                or self._producer_thread is not None
                or self._writer_thread is not None
                or self._status.is_recording
            )
            if has_active_recording and self._acquisition_started and not self._acquisition_stopped:
                try:
                    if self._shared_frame_source is not None:
                        self._shared_frame_source.release()
                    else:
                        self._driver.stop_acquisition()
                except Exception as exc:
                    stop_error = exc
                    if suppress_errors:
                        self._logger.exception("Recording acquisition stop failed during cleanup.")
                finally:
                    self._acquisition_stopped = True

            active_request = self._active_request
            final_status = self.get_status()
            session_started_utc = self._recording_session_started_utc
            session_end_utc = self._current_system_time_utc() if active_request is not None else None
            end_state = "failed" if final_status.last_error else "completed"
            completed_run_id = self._trace_run_id
            if active_request is not None and self._trace_log_handle is not None and self._trace_run_id is not None:
                try:
                    append_trace_run_end(
                        self._trace_log_handle,
                        "bounded_recording",
                        self._trace_run_id,
                        final_status.frames_written,
                        final_status.dropped_frames,
                        final_status.last_error,
                        session_end_utc,
                        end_state,
                    )
                except Exception as exc:
                    traceability_error = exc
                    self._record_error(f"Recording traceability log failed: {exc}")

            self._producer_thread = None
            self._writer_thread = None
            self._frame_queue = None
            self._active_request = None
            self._recording_session_started_utc = None
            self._recording_deadline = None
            self._next_frame_due_at = None
            self._acquisition_started = False
            if self._recording_log_handle is not None:
                self._recording_log_handle.close()
                self._recording_log_handle = None
                self._recording_log_writer = None
            if self._trace_log_handle is not None:
                self._trace_log_handle.close()
                self._trace_log_handle = None
                self._trace_log_writer = None
                self._trace_run_id = None
            self._last_completed_run_id = completed_run_id
            with self._status_lock:
                self._status.is_recording = False
                self._status.save_directory = None
                self._status.active_file_stem = None
                self._status.run_id = None

            if stop_error is not None and not suppress_errors:
                raise stop_error
            if traceability_error is not None and not suppress_errors:
                raise traceability_error
