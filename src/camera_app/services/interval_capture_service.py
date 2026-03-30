from __future__ import annotations

import logging
from threading import Event, Lock, Thread, current_thread
from time import monotonic, sleep

from camera_app.drivers.camera_driver import CameraDriver
from camera_app.models.captured_frame import CapturedFrame
from camera_app.models.interval_capture_request import IntervalCaptureRequest
from camera_app.models.interval_capture_status import IntervalCaptureStatus
from camera_app.services.shared_frame_source import SharedFrameSource
from camera_app.validation.request_validation import validate_interval_capture_request
from vision_platform.services.recording_service.file_naming import build_interval_capture_frame_path
from vision_platform.services.recording_service.frame_writer import FrameWriter


class IntervalCaptureService:
    def __init__(
        self,
        driver: CameraDriver,
        frame_writer: FrameWriter | None = None,
        poll_interval_seconds: float = 0.01,
        shared_frame_source: SharedFrameSource | None = None,
    ) -> None:
        self._driver = driver
        self._frame_writer = frame_writer or FrameWriter()
        self._poll_interval_seconds = poll_interval_seconds
        self._shared_frame_source = shared_frame_source
        self._logger = logging.getLogger(__name__)
        self._status_lock = Lock()
        self._status = IntervalCaptureStatus()
        self._active_request: IntervalCaptureRequest | None = None
        self._worker_thread: Thread | None = None
        self._stop_event = Event()
        self._cleanup_lock = Lock()
        self._acquisition_started = False
        self._acquisition_stopped = False
        self._capture_deadline: float | None = None
        self._next_capture_due_at: float | None = None

    def start_capture(self, request: IntervalCaptureRequest) -> IntervalCaptureStatus:
        self._validate_request(request)
        self.stop_capture()
        try:
            with self._status_lock:
                self._status = IntervalCaptureStatus(
                    is_capturing=True,
                    save_directory=request.save_directory,
                    active_file_stem=request.file_stem,
                )

            self._active_request = request
            self._stop_event.clear()
            self._acquisition_stopped = False
            self._capture_deadline = (
                monotonic() + request.duration_seconds if request.duration_seconds is not None else None
            )
            self._next_capture_due_at = monotonic()
            if self._shared_frame_source is not None:
                self._shared_frame_source.acquire()
            else:
                self._driver.start_acquisition()
            self._acquisition_started = True
            self._worker_thread = Thread(target=self._run_capture_loop, name="IntervalCapture", daemon=True)
            self._worker_thread.start()
            return self.get_status()
        except Exception:
            self._stop_event.set()
            self._finalize_capture(suppress_errors=True)
            raise

    def stop_capture(self) -> IntervalCaptureStatus:
        self._stop_event.set()
        active_thread = current_thread()
        if self._worker_thread is not None and self._worker_thread is not active_thread:
            self._worker_thread.join(timeout=1.0)
        self._finalize_capture()
        return self.get_status()

    def get_status(self) -> IntervalCaptureStatus:
        with self._status_lock:
            return IntervalCaptureStatus(
                is_capturing=self._status.is_capturing,
                frames_written=self._status.frames_written,
                skipped_intervals=self._status.skipped_intervals,
                save_directory=self._status.save_directory,
                active_file_stem=self._status.active_file_stem,
                last_error=self._status.last_error,
            )

    def _validate_request(self, request: IntervalCaptureRequest) -> None:
        validate_interval_capture_request(request)
        if request.interval_seconds <= 0:
            raise ValueError("IntervalCaptureRequest.interval_seconds must be greater than zero.")
        if request.max_frame_count is None and request.duration_seconds is None:
            raise ValueError("IntervalCaptureRequest requires max_frame_count or duration_seconds.")
        if request.max_frame_count is not None and request.max_frame_count <= 0:
            raise ValueError("IntervalCaptureRequest.max_frame_count must be greater than zero.")
        if request.duration_seconds is not None and request.duration_seconds <= 0:
            raise ValueError("IntervalCaptureRequest.duration_seconds must be greater than zero.")

    def _run_capture_loop(self) -> None:
        assert self._active_request is not None

        next_frame_index = 0
        last_frame_key = None

        while not self._stop_event.is_set():
            now = monotonic()
            if self._capture_deadline is not None and now >= self._capture_deadline:
                self._stop_event.set()
                break

            assert self._next_capture_due_at is not None
            if now < self._next_capture_due_at:
                sleep(min(self._next_capture_due_at - now, self._poll_interval_seconds))
                continue

            if self._active_request.max_frame_count is not None and next_frame_index >= self._active_request.max_frame_count:
                self._stop_event.set()
                break

            try:
                frame = self._get_latest_frame()
                if frame is None:
                    self._record_timing_skip("no new frame was available at the scheduled capture time")
                    self._next_capture_due_at = monotonic() + self._active_request.interval_seconds
                    continue

                frame_key = (frame.frame_id, id(frame.raw_frame))
                if frame_key == last_frame_key:
                    self._record_timing_skip("no new frame arrived before the next scheduled capture time")
                    self._next_capture_due_at = monotonic() + self._active_request.interval_seconds
                    continue

                target_path = build_interval_capture_frame_path(self._active_request, next_frame_index)
                self._frame_writer.write_frame(
                    frame,
                    target_path,
                    create_directories=self._active_request.create_directories,
                )
                last_frame_key = frame_key
                next_frame_index += 1
                with self._status_lock:
                    self._status.frames_written = next_frame_index
                    if self._status.last_error and self._status.last_error.startswith("Interval timing warning:"):
                        self._status.last_error = None
                self._next_capture_due_at = monotonic() + self._active_request.interval_seconds
            except Exception as exc:
                self._record_error(f"Interval capture failed: {exc}")
                self._stop_event.set()
                break

        self._stop_event.set()
        self._finalize_capture(suppress_errors=True)

    def _get_latest_frame(self) -> CapturedFrame | None:
        if self._shared_frame_source is not None:
            return self._shared_frame_source.get_latest_frame()
        return self._driver.get_latest_frame()

    def _record_error(self, message: str) -> None:
        self._logger.error(message, exc_info=True)
        with self._status_lock:
            self._status.last_error = message

    def _record_timing_skip(self, reason: str) -> None:
        with self._status_lock:
            self._status.skipped_intervals += 1
            self._status.last_error = f"Interval timing warning: {reason}"

    def _finalize_capture(self, suppress_errors: bool = False) -> None:
        with self._cleanup_lock:
            stop_error: Exception | None = None
            has_active_capture = (
                self._active_request is not None
                or self._worker_thread is not None
                or self._status.is_capturing
            )
            if has_active_capture and self._acquisition_started and not self._acquisition_stopped:
                try:
                    if self._shared_frame_source is not None:
                        self._shared_frame_source.release()
                    else:
                        self._driver.stop_acquisition()
                except Exception as exc:
                    stop_error = exc
                    if suppress_errors:
                        self._logger.exception("Interval capture acquisition stop failed during cleanup.")
                finally:
                    self._acquisition_stopped = True

            self._worker_thread = None
            self._active_request = None
            self._capture_deadline = None
            self._next_capture_due_at = None
            self._acquisition_started = False
            with self._status_lock:
                if (
                    self._status.skipped_intervals > 0
                    and self._status.last_error is not None
                    and self._status.last_error.startswith("Interval timing warning:")
                ):
                    self._status.last_error = (
                        f"Interval capture completed with skipped_intervals={self._status.skipped_intervals}"
                    )
                elif self._status.last_error is None and self._status.skipped_intervals > 0:
                    self._status.last_error = (
                        f"Interval capture completed with skipped_intervals={self._status.skipped_intervals}"
                    )
                self._status.is_capturing = False
                self._status.save_directory = None
                self._status.active_file_stem = None

            if stop_error is not None and not suppress_errors:
                raise stop_error
