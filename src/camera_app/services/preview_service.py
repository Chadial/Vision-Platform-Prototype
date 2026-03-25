from __future__ import annotations

import logging
from threading import Event, Lock, Thread
from time import sleep

from camera_app.drivers.camera_driver import CameraDriver
from camera_app.models.captured_frame import CapturedFrame
from camera_app.models.preview_frame_info import PreviewFrameInfo


class PreviewService:
    def __init__(self, driver: CameraDriver, poll_interval_seconds: float = 0.05) -> None:
        self._driver = driver
        self._poll_interval_seconds = poll_interval_seconds
        self._logger = logging.getLogger(__name__)
        self._latest_frame: CapturedFrame | None = None
        self._latest_frame_info: PreviewFrameInfo | None = None
        self._lock = Lock()
        self._stop_event = Event()
        self._worker_thread: Thread | None = None
        self._acquisition_started = False

    def start(self) -> None:
        if self.is_running:
            return

        self._driver.start_acquisition()
        self._acquisition_started = True
        try:
            self._stop_event.clear()
            self._worker_thread = Thread(target=self._run_preview_loop, name="PreviewService", daemon=True)
            self._worker_thread.start()
        except Exception:
            self._stop_event.set()
            self._worker_thread = None
            if self._acquisition_started:
                self._driver.stop_acquisition()
                self._acquisition_started = False
            raise

    def stop(self) -> None:
        self._stop_event.set()
        if self._worker_thread is not None:
            self._worker_thread.join(timeout=max(self._poll_interval_seconds * 4, 0.2))
            self._worker_thread = None
        if self._acquisition_started:
            self._driver.stop_acquisition()
            self._acquisition_started = False

    @property
    def is_running(self) -> bool:
        return self._worker_thread is not None and self._worker_thread.is_alive()

    def refresh_once(self) -> PreviewFrameInfo | None:
        frame = self._driver.get_latest_frame()
        if frame is None:
            return None

        frame_info = frame.to_preview_frame_info()
        with self._lock:
            self._latest_frame = frame
            self._latest_frame_info = frame_info
        return frame_info

    def get_latest_frame(self) -> CapturedFrame | None:
        with self._lock:
            return self._latest_frame

    def get_latest_frame_info(self) -> PreviewFrameInfo | None:
        with self._lock:
            return self._latest_frame_info

    def _run_preview_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                self.refresh_once()
            except Exception:
                self._logger.exception("Preview polling failed.")
            sleep(self._poll_interval_seconds)
