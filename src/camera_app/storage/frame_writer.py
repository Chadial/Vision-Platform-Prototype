from __future__ import annotations

import struct
import zlib
from pathlib import Path

from camera_app.models.captured_frame import CapturedFrame


class FrameWriter:
    def write_frame(
        self,
        frame: CapturedFrame,
        target_path: Path,
        create_directories: bool = True,
    ) -> Path:
        if create_directories:
            target_path.parent.mkdir(parents=True, exist_ok=True)

        extension = target_path.suffix.lower()
        if extension == ".png":
            self._write_png(frame, target_path)
            return target_path

        if extension in {".raw", ".bin"}:
            target_path.write_bytes(self._get_frame_buffer(frame))
            return target_path

        raise RuntimeError(f"Unsupported snapshot file extension '{target_path.suffix}'.")

    def _write_png(self, frame: CapturedFrame, target_path: Path) -> None:
        if frame.width <= 0 or frame.height <= 0:
            raise RuntimeError("Frame dimensions must be positive to save a PNG image.")

        raw_buffer = self._get_frame_buffer(frame)
        normalized_format = (frame.pixel_format or "").strip().lower()

        if normalized_format == "mono8":
            color_type = 0
            bytes_per_pixel = 1
            image_bytes = raw_buffer
        elif normalized_format == "rgb8":
            color_type = 2
            bytes_per_pixel = 3
            image_bytes = raw_buffer
        elif normalized_format == "bgr8":
            color_type = 2
            bytes_per_pixel = 3
            image_bytes = self._convert_bgr_to_rgb(raw_buffer)
        else:
            raise RuntimeError(f"Unsupported pixel format '{frame.pixel_format}' for PNG output.")

        expected_size = frame.width * frame.height * bytes_per_pixel
        if len(image_bytes) < expected_size:
            raise RuntimeError(
                f"Frame buffer is too small for {frame.width}x{frame.height} {frame.pixel_format} image data."
            )

        png_rows = bytearray()
        row_size = frame.width * bytes_per_pixel
        pixel_bytes = image_bytes[:expected_size]
        for row_start in range(0, expected_size, row_size):
            png_rows.append(0)
            png_rows.extend(pixel_bytes[row_start : row_start + row_size])

        compressed = zlib.compress(bytes(png_rows))
        png_bytes = b"".join(
            [
                b"\x89PNG\r\n\x1a\n",
                self._build_chunk(
                    b"IHDR",
                    struct.pack(">IIBBBBB", frame.width, frame.height, 8, color_type, 0, 0, 0),
                ),
                self._build_chunk(b"IDAT", compressed),
                self._build_chunk(b"IEND", b""),
            ]
        )
        target_path.write_bytes(png_bytes)

    @staticmethod
    def _get_frame_buffer(frame: CapturedFrame) -> bytes:
        raw_frame = frame.raw_frame
        get_buffer = getattr(raw_frame, "get_buffer", None)
        if callable(get_buffer):
            return bytes(get_buffer())

        if isinstance(raw_frame, (bytes, bytearray, memoryview)):
            return bytes(raw_frame)

        raise RuntimeError("Frame does not expose a writable buffer.")

    @staticmethod
    def _convert_bgr_to_rgb(buffer: bytes) -> bytes:
        if len(buffer) % 3 != 0:
            raise RuntimeError("BGR frame buffer size is not divisible by 3.")

        converted = bytearray(len(buffer))
        for index in range(0, len(buffer), 3):
            blue, green, red = buffer[index : index + 3]
            converted[index : index + 3] = bytes((red, green, blue))
        return bytes(converted)

    @staticmethod
    def _build_chunk(chunk_type: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(chunk_type)
        crc = zlib.crc32(data, crc)
        return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", crc & 0xFFFFFFFF)
