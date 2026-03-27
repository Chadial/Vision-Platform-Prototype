from __future__ import annotations

import logging
from threading import Event, Lock, Thread
from time import sleep

from vision_platform.integrations.camera import CameraDriver
from vision_platform.models import CapturedFrame


class SharedFrameSource:
    """Maintains one shared acquisition loop for multiple consumers."""

    _RELEASE_JOIN_TIMEOUT_SECONDS = 3.0

    def __init__(self, driver: CameraDriver, poll_interval_seconds: float = 0.01) -> None:
        self._driver = driver
        self._poll_interval_seconds = poll_interval_seconds
        self._logger = logging.getLogger(__name__)
        self._lock = Lock()
        self._latest_frame: CapturedFrame | None = None
        self._consumer_count = 0
        self._stop_event = Event()
        self._worker_thread: Thread | None = None

    def acquire(self) -> None:
        with self._lock:
            self._consumer_count += 1
            if self._consumer_count > 1:
                return

            self._stop_event.clear()
            self._driver.start_acquisition()
            try:
                self._worker_thread = Thread(target=self._run, name="SharedFrameSource", daemon=True)
                self._worker_thread.start()
            except Exception:
                self._consumer_count = 0
                self._worker_thread = None
                self._stop_event.set()
                try:
                    self._driver.stop_acquisition()
                except Exception:
                    self._logger.exception("Shared frame source cleanup failed after startup error.")
                raise

    def release(self) -> None:
        worker_to_join: Thread | None = None

        with self._lock:
            if self._consumer_count == 0:
                return

            self._consumer_count -= 1
            if self._consumer_count > 0:
                return

            self._stop_event.set()
            worker_to_join = self._worker_thread
            self._worker_thread = None

        if worker_to_join is not None:
            worker_to_join.join(timeout=max(self._poll_interval_seconds * 4, self._RELEASE_JOIN_TIMEOUT_SECONDS))

        self._driver.stop_acquisition()

    def get_latest_frame(self) -> CapturedFrame | None:
        with self._lock:
            return self._latest_frame

    @property
    def is_running(self) -> bool:
        with self._lock:
            return self._worker_thread is not None and self._worker_thread.is_alive()

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                frame = self._driver.get_latest_frame()
                if frame is not None:
                    with self._lock:
                        self._latest_frame = frame
            except Exception:
                if self._stop_event.is_set():
                    break
                self._logger.exception("Shared frame polling failed.")
            sleep(self._poll_interval_seconds)


__all__ = ["SharedFrameSource"]
