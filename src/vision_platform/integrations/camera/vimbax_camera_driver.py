from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock
from typing import Optional

from vmbpy import Camera, VmbSystem

from vision_platform.integrations.camera.camera_driver import CameraDriver
from vision_platform.integrations.camera.capability_probe import (
    DEFAULT_FEATURE_NAMES,
    probe_open_camera_capabilities,
    select_camera_from_system,
)
from vision_platform.models import CameraConfiguration, CameraStatus, CapturedFrame


class VimbaXCameraDriver(CameraDriver):
    """Thin driver wrapper around the Vimba X Python API."""

    def __init__(self, snapshot_timeout_ms: int = 2000) -> None:
        self._status = CameraStatus()
        self._vmb_system = None
        self._camera: Optional[Camera] = None
        self._latest_frame: Optional[CapturedFrame] = None
        self._snapshot_timeout_ms = snapshot_timeout_ms
        self._selected_camera_identity: dict[str, str | None] | None = None
        self._capture_lock = Lock()

    @staticmethod
    def _normalize_identity_value(value: str | None) -> str | None:
        text = (value or "").strip()
        if not text or text.upper() == "N/A":
            return None
        return text

    def _capture_camera_identity(self, camera: Camera) -> dict[str, str | None]:
        return {
            "camera_id": camera.get_id(),
            "camera_name": self._normalize_identity_value(camera.get_name()),
            "camera_model": self._normalize_identity_value(camera.get_model()),
            "camera_serial": self._normalize_identity_value(camera.get_serial()),
            "interface_id": self._normalize_identity_value(camera.get_interface_id()),
        }

    def _prefer_identity_value(self, current: str | None, fallback_key: str) -> str | None:
        normalized_current = self._normalize_identity_value(current)
        if normalized_current is not None:
            return normalized_current
        if self._selected_camera_identity is None:
            return current
        return self._selected_camera_identity.get(fallback_key) or current

    def _build_camera_status(self, camera: Camera) -> CameraStatus:
        return CameraStatus(
            is_initialized=True,
            is_acquiring=self._status.is_acquiring,
            source_kind="hardware",
            driver_name=self.__class__.__name__,
            camera_id=camera.get_id(),
            camera_name=self._prefer_identity_value(camera.get_name(), "camera_name"),
            camera_model=self._prefer_identity_value(camera.get_model(), "camera_model"),
            camera_serial=self._prefer_identity_value(camera.get_serial(), "camera_serial"),
            interface_id=self._prefer_identity_value(camera.get_interface_id(), "interface_id"),
            reported_acquisition_frame_rate=self._try_read_feature_value("AcquisitionFrameRate"),
            acquisition_frame_rate_enabled=self._try_read_feature_value("AcquisitionFrameRateEnable"),
        )

    def _select_camera(self, camera_id: Optional[str]) -> Camera:
        assert self._vmb_system is not None
        return select_camera_from_system(self._vmb_system, camera_id=camera_id)

    def _require_camera(self) -> Camera:
        if self._camera is None:
            raise RuntimeError("Camera driver is not initialized.")
        return self._camera

    def _get_feature(self, feature_name: str):
        camera = self._require_camera()
        try:
            return camera.get_feature_by_name(feature_name)
        except Exception as exc:
            raise RuntimeError(f"Camera feature '{feature_name}' is not available.") from exc

    @staticmethod
    def _try_read_frame_value(frame, method_name: str, default=None):
        method = getattr(frame, method_name, None)
        if method is None:
            return default

        try:
            return method()
        except Exception:
            return default

    def _try_read_feature_value(self, feature_name: str, default=None):
        if self._camera is None:
            return default

        try:
            feature = self._camera.get_feature_by_name(feature_name)
        except Exception:
            return default

        is_readable = getattr(feature, "is_readable", None)
        if callable(is_readable):
            try:
                if not is_readable():
                    return default
            except Exception:
                return default

        getter = getattr(feature, "get", None)
        if getter is None:
            return default

        try:
            return getter()
        except Exception:
            return default

    def _build_captured_frame(self, frame) -> CapturedFrame:
        pixel_format = self._try_read_frame_value(frame, "get_pixel_format")
        if pixel_format is not None:
            pixel_format = str(pixel_format)

        return CapturedFrame(
            raw_frame=frame,
            frame_id=self._try_read_frame_value(frame, "get_id"),
            camera_timestamp=self._try_read_frame_value(frame, "get_timestamp"),
            timestamp_utc=datetime.now(timezone.utc),
            width=self._try_read_frame_value(frame, "get_width", 0),
            height=self._try_read_frame_value(frame, "get_height", 0),
            pixel_format=pixel_format,
        )

    def _set_feature_value(self, feature_name: str, value) -> None:
        feature = self._get_feature(feature_name)
        if not feature.is_writeable():
            raise RuntimeError(f"Camera feature '{feature_name}' is not writeable.")

        try:
            feature.set(value)
        except Exception as exc:
            raise RuntimeError(f"Failed to set camera feature '{feature_name}' to '{value}': {exc}") from exc

    def _set_acquisition_frame_rate(self, value: float) -> None:
        enable_feature = None
        try:
            enable_feature = self._get_feature("AcquisitionFrameRateEnable")
        except RuntimeError:
            enable_feature = None

        if enable_feature is not None:
            if not enable_feature.is_writeable():
                raise RuntimeError("Camera feature 'AcquisitionFrameRateEnable' is not writeable.")
            try:
                enable_feature.set(True)
            except Exception as exc:
                raise RuntimeError(f"Failed to set camera feature 'AcquisitionFrameRateEnable' to 'True': {exc}") from exc

        self._set_feature_value("AcquisitionFrameRate", value)

    def _refresh_status(self) -> CameraStatus:
        if self._camera is None:
            self._status = CameraStatus()
            return self._status

        self._status = self._build_camera_status(self._camera)
        return self._status

    def initialize(self, camera_id: Optional[str] = None) -> CameraStatus:
        self.shutdown()
        try:
            self._vmb_system = VmbSystem.get_instance()
            self._vmb_system.__enter__()
            self._camera = self._select_camera(camera_id)
            self._selected_camera_identity = self._capture_camera_identity(self._camera)
            self._camera.__enter__()
            return self._refresh_status()
        except Exception as exc:
            self._status = CameraStatus(last_error=str(exc))
            self.shutdown()
            raise RuntimeError(f"Failed to initialize camera driver: {exc}") from exc

    def get_status(self) -> CameraStatus:
        return self._refresh_status()

    def probe_capabilities(self, feature_names: tuple[str, ...] = DEFAULT_FEATURE_NAMES) -> dict:
        return probe_open_camera_capabilities(self._require_camera(), feature_names=feature_names)

    def shutdown(self) -> None:
        if self._camera is not None:
            try:
                self._camera.__exit__(None, None, None)
            finally:
                self._camera = None

        if self._vmb_system is not None:
            try:
                self._vmb_system.__exit__(None, None, None)
            finally:
                self._vmb_system = None

        self._latest_frame = None
        self._selected_camera_identity = None
        self._status = CameraStatus()

    def apply_configuration(self, config: CameraConfiguration) -> None:
        if config.exposure_time_us is not None:
            self._set_feature_value("ExposureTime", config.exposure_time_us)

        if config.gain is not None:
            self._set_feature_value("Gain", config.gain)

        if config.pixel_format is not None:
            self._set_feature_value("PixelFormat", config.pixel_format)

        if config.acquisition_frame_rate is not None:
            self._set_acquisition_frame_rate(config.acquisition_frame_rate)
        if config.roi_offset_x is not None:
            self._set_feature_value("OffsetX", config.roi_offset_x)
        if config.roi_offset_y is not None:
            self._set_feature_value("OffsetY", config.roi_offset_y)
        if config.roi_width is not None:
            self._set_feature_value("Width", config.roi_width)
        if config.roi_height is not None:
            self._set_feature_value("Height", config.roi_height)

        self._refresh_status()

    def start_acquisition(self) -> None:
        self._status.is_acquiring = True

    def stop_acquisition(self) -> None:
        self._status.is_acquiring = False

    def capture_snapshot(self) -> CapturedFrame:
        camera = self._require_camera()

        with self._capture_lock:
            try:
                frame = camera.get_frame(timeout_ms=self._snapshot_timeout_ms)
            except Exception as exc:
                error_text = str(exc).lower()
                if "timeout" in error_text:
                    raise RuntimeError("Timed out while waiting for a camera frame.") from exc
                if "disconnect" in error_text or "disconnected" in error_text:
                    raise RuntimeError("Camera disconnected during snapshot acquisition.") from exc
                raise RuntimeError(f"Failed to capture camera frame: {exc}") from exc

        captured_frame = self._build_captured_frame(frame)
        self._latest_frame = captured_frame
        return captured_frame

    def get_latest_frame(self) -> Optional[CapturedFrame]:
        if self._status.is_acquiring:
            return self.capture_snapshot()

        return self._latest_frame


__all__ = ["VimbaXCameraDriver"]
