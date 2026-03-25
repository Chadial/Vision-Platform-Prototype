from __future__ import annotations

from importlib import import_module
from importlib.util import find_spec
from pathlib import Path
from typing import Any

from camera_app.models.captured_frame import CapturedFrame


class OpenCvFrameAdapter:
    """Optional OpenCV-backed adapter for preview display and grayscale-safe saving."""

    _GRAYSCALE_BIT_DEPTHS = {
        "mono8": 8,
        "mono10": 10,
        "mono12": 12,
        "mono14": 14,
        "mono16": 16,
    }

    def __init__(self, cv2_module: Any | None = None, numpy_module: Any | None = None) -> None:
        self._cv2 = cv2_module
        self._numpy = numpy_module

    @classmethod
    def is_available(cls) -> bool:
        return find_spec("cv2") is not None and find_spec("numpy") is not None

    def to_image(self, frame: CapturedFrame) -> Any:
        buffer = frame.get_buffer_bytes()
        normalized_format = self._normalize_pixel_format(frame.pixel_format)
        numpy_module = self._require_numpy()

        if normalized_format == "mono8":
            expected_size = frame.width * frame.height
            pixel_bytes = self._slice_checked_buffer(buffer, expected_size, frame)
            return numpy_module.frombuffer(pixel_bytes, dtype=numpy_module.uint8).reshape((frame.height, frame.width)).copy()

        if normalized_format in self._GRAYSCALE_BIT_DEPTHS and normalized_format != "mono8":
            expected_size = frame.width * frame.height * 2
            pixel_bytes = self._slice_checked_buffer(buffer, expected_size, frame)
            image = numpy_module.frombuffer(pixel_bytes, dtype=numpy_module.uint16).reshape((frame.height, frame.width)).copy()
            return image

        if normalized_format == "bgr8":
            expected_size = frame.width * frame.height * 3
            pixel_bytes = self._slice_checked_buffer(buffer, expected_size, frame)
            return numpy_module.frombuffer(pixel_bytes, dtype=numpy_module.uint8).reshape((frame.height, frame.width, 3)).copy()

        if normalized_format == "rgb8":
            expected_size = frame.width * frame.height * 3
            pixel_bytes = self._slice_checked_buffer(buffer, expected_size, frame)
            converted_bytes = self._convert_rgb_to_bgr_bytes(pixel_bytes)
            return (
                numpy_module.frombuffer(converted_bytes, dtype=numpy_module.uint8)
                .reshape((frame.height, frame.width, 3))
                .copy()
            )

        raise RuntimeError(f"Unsupported pixel format '{frame.pixel_format}' for OpenCV conversion.")

    def show_frame(self, window_name: str, frame: CapturedFrame, delay_ms: int = 1) -> int:
        image = self.to_image(frame)
        cv2_module = self._require_cv2()
        cv2_module.imshow(window_name, image)
        return int(cv2_module.waitKey(delay_ms))

    def save_lossless_grayscale(
        self,
        frame: CapturedFrame,
        target_path: Path,
        create_directories: bool = True,
    ) -> Path:
        if create_directories:
            target_path.parent.mkdir(parents=True, exist_ok=True)

        extension = target_path.suffix.lower()
        if extension not in {".png", ".tif", ".tiff"}:
            raise RuntimeError(
                f"Unsupported lossless grayscale extension '{target_path.suffix}'. Use .png, .tif, or .tiff."
            )

        normalized_format = self._normalize_pixel_format(frame.pixel_format)
        if normalized_format not in self._GRAYSCALE_BIT_DEPTHS:
            raise RuntimeError(
                f"Pixel format '{frame.pixel_format}' is not supported for lossless grayscale OpenCV output."
            )

        image = self.to_image(frame)
        success = bool(self._require_cv2().imwrite(str(target_path), image))
        if not success:
            raise RuntimeError(f"OpenCV failed to write '{target_path}'.")
        return target_path

    def destroy_window(self, window_name: str) -> None:
        self._require_cv2().destroyWindow(window_name)

    def destroy_all_windows(self) -> None:
        self._require_cv2().destroyAllWindows()

    def _require_cv2(self) -> Any:
        if self._cv2 is None:
            try:
                self._cv2 = import_module("cv2")
            except ModuleNotFoundError as exc:
                raise RuntimeError(
                    "Optional OpenCV preview/save path requires 'cv2'. Install opencv-python and numpy to use it."
                ) from exc
        return self._cv2

    def _require_numpy(self) -> Any:
        if self._numpy is None:
            try:
                self._numpy = import_module("numpy")
            except ModuleNotFoundError as exc:
                raise RuntimeError(
                    "Optional OpenCV preview/save path requires 'numpy'. Install opencv-python and numpy to use it."
                ) from exc
        return self._numpy

    @classmethod
    def _normalize_pixel_format(cls, pixel_format: str | None) -> str:
        return (pixel_format or "").strip().lower()

    @classmethod
    def _slice_checked_buffer(cls, buffer: bytes, expected_size: int, frame: CapturedFrame) -> bytes:
        if len(buffer) < expected_size:
            raise RuntimeError(
                f"Frame buffer is too small for {frame.width}x{frame.height} {frame.pixel_format} image data."
            )
        return buffer[:expected_size]

    @staticmethod
    def _convert_rgb_to_bgr_bytes(buffer: bytes) -> bytes:
        converted = bytearray(len(buffer))
        for index in range(0, len(buffer), 3):
            red, green, blue = buffer[index : index + 3]
            converted[index : index + 3] = bytes((blue, green, red))
        return bytes(converted)
