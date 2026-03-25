from __future__ import annotations

import csv
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
from camera_app.storage.file_naming import build_recording_frame_path, build_recording_log_path
from camera_app.storage.frame_writer import FrameWriter


class RecordingService:
    def __init__(
        self,
        driver: CameraDriver,
        frame_writer: FrameWriter | None = None,
        poll_interval_seconds: float = 0.01,
        configuration_provider: Callable[[], CameraConfiguration | None] | None = None,
    ) -> None:
        self._driver = driver
        self._frame_writer = frame_writer or FrameWriter()
        self._poll_interval_seconds = poll_interval_seconds
        self._configuration_provider = configuration_provider
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
        self._recording_deadline: float | None = None
        self._recording_log_handle: TextIO | None = None
        self._recording_log_writer: csv.writer | None = None

    def start_recording(self, request: RecordingRequest) -> RecordingStatus:
        self._validate_request(request)
        self.stop_recording()

        with self._status_lock:
            self._status = RecordingStatus(
                is_recording=True,
                save_directory=request.save_directory,
                active_file_stem=request.file_stem,
            )

        self._active_request = request
        self._frame_queue = Queue(maxsize=request.queue_size)
        self._stop_event.clear()
        self._acquisition_stopped = False
        self._recording_deadline = (
            monotonic() + request.duration_seconds if request.duration_seconds is not None else None
        )
        self._open_recording_log(request)
        self._driver.start_acquisition()

        self._producer_thread = Thread(target=self._producer_loop, name="RecordingProducer", daemon=True)
        self._writer_thread = Thread(target=self._writer_loop, name="RecordingWriter", daemon=True)
        self._producer_thread.start()
        self._writer_thread.start()
        return self.get_status()

    def stop_recording(self) -> RecordingStatus:
        self._stop_event.set()

        active_thread = current_thread()
        if self._producer_thread is not None and self._producer_thread is not active_thread:
            self._producer_thread.join(timeout=1.0)
        if self._writer_thread is not None and self._writer_thread is not active_thread:
            self._writer_thread.join(timeout=1.0)

        self._finalize_recording()
        return self.get_status()

    def get_status(self) -> RecordingStatus:
        with self._status_lock:
            return RecordingStatus(
                is_recording=self._status.is_recording,
                frames_written=self._status.frames_written,
                dropped_frames=self._status.dropped_frames,
                save_directory=self._status.save_directory,
                active_file_stem=self._status.active_file_stem,
                last_error=self._status.last_error,
            )

    def _validate_request(self, request: RecordingRequest) -> None:
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

            try:
                frame = self._driver.get_latest_frame()
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

        self._finalize_recording()

    def _record_error(self, message: str) -> None:
        self._logger.exception(message)
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

    def _build_recording_log_metadata(
        self,
        request: RecordingRequest,
        configuration: CameraConfiguration | None,
    ) -> list[tuple[str, str]]:
        return [
            ("recording_start_signal_utc", self._current_system_time_utc()),
            ("save_directory", str(request.save_directory)),
            ("file_stem", request.file_stem),
            ("file_extension", request.file_extension),
            ("camera_id", request.camera_id or ""),
            ("frame_limit", "" if request.frame_limit is None else str(request.frame_limit)),
            ("duration_seconds", "" if request.duration_seconds is None else str(request.duration_seconds)),
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
            ("roi_x", ""),
            ("roi_y", ""),
            ("roi_width", ""),
            ("roi_height", ""),
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

    @staticmethod
    def _current_system_time_utc() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _finalize_recording(self) -> None:
        with self._cleanup_lock:
            has_active_recording = (
                self._active_request is not None
                or self._producer_thread is not None
                or self._writer_thread is not None
                or self._status.is_recording
            )
            if has_active_recording and not self._acquisition_stopped:
                self._driver.stop_acquisition()
                self._acquisition_stopped = True

            self._producer_thread = None
            self._writer_thread = None
            self._frame_queue = None
            self._active_request = None
            self._recording_deadline = None
            if self._recording_log_handle is not None:
                self._recording_log_handle.close()
                self._recording_log_handle = None
                self._recording_log_writer = None
            with self._status_lock:
                self._status.is_recording = False
