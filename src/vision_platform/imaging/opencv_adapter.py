from __future__ import annotations

from importlib import import_module
from importlib.util import find_spec
from pathlib import Path
from typing import Any

from vision_platform.models import CapturedFrame


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
        return self.show_image(window_name, image, delay_ms=delay_ms)

    def show_image(self, window_name: str, image: Any, delay_ms: int = 1) -> int:
        cv2_module = self._require_cv2()
        cv2_module.imshow(window_name, image)
        wait_key_ex = getattr(cv2_module, "waitKeyEx", None)
        if wait_key_ex is not None:
            return int(wait_key_ex(delay_ms))
        return int(cv2_module.waitKey(delay_ms))

    def create_window(self, window_name: str) -> None:
        cv2_module = self._require_cv2()
        cv2_module.namedWindow(window_name, getattr(cv2_module, "WINDOW_NORMAL", 0))

    def get_window_image_size(self, window_name: str) -> tuple[int, int] | None:
        cv2_module = self._require_cv2()
        get_rect = getattr(cv2_module, "getWindowImageRect", None)
        if get_rect is None:
            return None

        try:
            _, _, width, height = get_rect(window_name)
        except Exception:
            return None

        if width <= 0 or height <= 0:
            return None
        return int(width), int(height)

    def is_window_visible(self, window_name: str) -> bool:
        cv2_module = self._require_cv2()
        get_property = getattr(cv2_module, "getWindowProperty", None)
        if get_property is None:
            return True

        property_id = getattr(cv2_module, "WND_PROP_VISIBLE", 4)
        try:
            return bool(get_property(window_name, property_id) >= 1)
        except Exception:
            return False

    def resize_image(self, image: Any, width: int, height: int) -> Any:
        cv2_module = self._require_cv2()
        return cv2_module.resize(image, (int(width), int(height)), interpolation=getattr(cv2_module, "INTER_AREA", 3))

    def render_into_viewport(
        self,
        image: Any,
        viewport_width: int,
        viewport_height: int,
        scale: float,
        overlay_text: str | None = None,
    ) -> Any:
        viewport_width = max(1, int(viewport_width))
        viewport_height = max(1, int(viewport_height))
        scaled_width = max(1, int(round(image.shape[1] * scale)))
        scaled_height = max(1, int(round(image.shape[0] * scale)))
        scaled_image = self.resize_image(image, scaled_width, scaled_height)
        canvas = self._create_black_canvas(viewport_height, viewport_width, image)

        src_x = max(0, (scaled_width - viewport_width) // 2)
        src_y = max(0, (scaled_height - viewport_height) // 2)
        dst_x = max(0, (viewport_width - scaled_width) // 2)
        dst_y = max(0, (viewport_height - scaled_height) // 2)
        copy_width = min(scaled_width, viewport_width)
        copy_height = min(scaled_height, viewport_height)

        canvas[dst_y : dst_y + copy_height, dst_x : dst_x + copy_width] = scaled_image[
            src_y : src_y + copy_height,
            src_x : src_x + copy_width,
        ]

        if overlay_text:
            self._draw_overlay_text(canvas, overlay_text)

        return canvas

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
        cv2_module = self._require_cv2()
        try:
            cv2_module.destroyWindow(window_name)
        except Exception:
            return

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

    def _create_black_canvas(self, height: int, width: int, image: Any) -> Any:
        numpy_module = self._require_numpy()
        if len(image.shape) == 2:
            return numpy_module.zeros((height, width), dtype=image.dtype)
        return numpy_module.zeros((height, width, image.shape[2]), dtype=image.dtype)

    def _draw_overlay_text(self, image: Any, overlay_text: str) -> None:
        cv2_module = self._require_cv2()
        put_text = getattr(cv2_module, "putText", None)
        if put_text is None:
            return

        font = getattr(cv2_module, "FONT_HERSHEY_SIMPLEX", 0)
        line_type = getattr(cv2_module, "LINE_AA", 16)
        color = 255 if len(image.shape) == 2 else (255, 255, 255)
        put_text(image, overlay_text, (12, 28), font, 0.7, color, 2, line_type)


__all__ = ["OpenCvFrameAdapter"]
