from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from importlib.util import find_spec

from vision_platform.models import CapturedFrame
from vision_platform.services.display_service.display_geometry_service import ViewportMapping


@dataclass(frozen=True, slots=True)
class RenderedViewportImage:
    width: int
    height: int
    mime_family: str
    payload: bytes

    def to_pnm_bytes(self) -> bytes:
        magic = b"P5" if self.mime_family == "pgm" else b"P6"
        header = magic + b"\n" + f"{self.width} {self.height}\n255\n".encode("ascii")
        return header + self.payload

    def to_rgb_bytes(self) -> bytes:
        if self.mime_family == "ppm":
            return self.payload
        return bytes(self.to_rgb_buffer())

    def to_rgb_buffer(self) -> bytearray:
        if self.mime_family == "ppm":
            return bytearray(self.payload)
        if _is_numpy_available():
            numpy_module = _require_numpy()
            values = numpy_module.frombuffer(self.payload, dtype=numpy_module.uint8)
            return bytearray(numpy_module.repeat(values, 3).tobytes())
        rgb_payload = bytearray(self.width * self.height * 3)
        target_index = 0
        for value in self.payload:
            rgb_payload[target_index : target_index + 3] = bytes((value, value, value))
            target_index += 3
        return rgb_payload


def render_viewport_image(frame: CapturedFrame, mapping: ViewportMapping) -> RenderedViewportImage:
    pixel_format = (frame.pixel_format or "Mono8").lower()
    source_bytes = frame.get_buffer_bytes()
    if pixel_format == "mono8":
        return RenderedViewportImage(
            width=mapping.viewport_width,
            height=mapping.viewport_height,
            mime_family="pgm",
            payload=_render_mono8_payload(
                source_bytes,
                source_width=frame.width,
                source_height=frame.height,
                mapping=mapping,
            ),
        )
    if pixel_format in {"mono10", "mono12", "mono14", "mono16"}:
        mono8_bytes = _convert_high_bit_mono_to_mono8(source_bytes, frame.width, frame.height, pixel_format)
        return RenderedViewportImage(
            width=mapping.viewport_width,
            height=mapping.viewport_height,
            mime_family="pgm",
            payload=_render_mono8_payload(
                mono8_bytes,
                source_width=frame.width,
                source_height=frame.height,
                mapping=mapping,
            ),
        )
    if pixel_format in {"rgb8", "bgr8"}:
        return RenderedViewportImage(
            width=mapping.viewport_width,
            height=mapping.viewport_height,
            mime_family="ppm",
            payload=_render_rgb_payload(
                source_bytes,
                source_width=frame.width,
                source_height=frame.height,
                mapping=mapping,
                source_format=pixel_format,
            ),
        )
    raise RuntimeError(f"Unsupported pixel format '{frame.pixel_format}' for local shell rendering.")


def _render_mono8_payload(
    source_bytes: bytes,
    *,
    source_width: int,
    source_height: int,
    mapping: ViewportMapping,
) -> bytes:
    if _is_numpy_available():
        return _render_mono8_payload_numpy(
            source_bytes,
            source_width=source_width,
            source_height=source_height,
            mapping=mapping,
        )
    payload = bytearray(mapping.viewport_width * mapping.viewport_height)
    for viewport_y in range(mapping.copy_height):
        for viewport_x in range(mapping.copy_width):
            scaled_x = mapping.src_x + viewport_x
            scaled_y = mapping.src_y + viewport_y
            source_x = min(max(int(scaled_x / mapping.display_scale), 0), source_width - 1)
            source_y = min(max(int(scaled_y / mapping.display_scale), 0), source_height - 1)
            payload[(mapping.dst_y + viewport_y) * mapping.viewport_width + mapping.dst_x + viewport_x] = source_bytes[
                source_y * source_width + source_x
            ]
    return bytes(payload)


def _render_rgb_payload(
    source_bytes: bytes,
    *,
    source_width: int,
    source_height: int,
    mapping: ViewportMapping,
    source_format: str,
) -> bytes:
    if _is_numpy_available():
        return _render_rgb_payload_numpy(
            source_bytes,
            source_width=source_width,
            source_height=source_height,
            mapping=mapping,
            source_format=source_format,
        )
    payload = bytearray(mapping.viewport_width * mapping.viewport_height * 3)
    for viewport_y in range(mapping.copy_height):
        for viewport_x in range(mapping.copy_width):
            scaled_x = mapping.src_x + viewport_x
            scaled_y = mapping.src_y + viewport_y
            source_x = min(max(int(scaled_x / mapping.display_scale), 0), source_width - 1)
            source_y = min(max(int(scaled_y / mapping.display_scale), 0), source_height - 1)
            source_index = (source_y * source_width + source_x) * 3
            target_index = ((mapping.dst_y + viewport_y) * mapping.viewport_width + mapping.dst_x + viewport_x) * 3
            pixel = source_bytes[source_index : source_index + 3]
            if source_format == "bgr8":
                payload[target_index : target_index + 3] = bytes((pixel[2], pixel[1], pixel[0]))
            else:
                payload[target_index : target_index + 3] = pixel
    return bytes(payload)


def _render_mono8_payload_numpy(
    source_bytes: bytes,
    *,
    source_width: int,
    source_height: int,
    mapping: ViewportMapping,
) -> bytes:
    numpy_module = _require_numpy()
    expected_size = source_width * source_height
    if len(source_bytes) < expected_size:
        raise RuntimeError("Frame buffer is too small for Mono8 viewport rendering.")

    source_image = numpy_module.frombuffer(source_bytes, dtype=numpy_module.uint8, count=expected_size).reshape(
        (source_height, source_width)
    )
    source_x, source_y = _build_source_indices_numpy(mapping, source_width, source_height, numpy_module)
    sampled = source_image[source_y[:, None], source_x[None, :]]

    viewport = numpy_module.zeros((mapping.viewport_height, mapping.viewport_width), dtype=numpy_module.uint8)
    viewport[
        mapping.dst_y : mapping.dst_y + mapping.copy_height,
        mapping.dst_x : mapping.dst_x + mapping.copy_width,
    ] = sampled
    return viewport.tobytes()


def _render_rgb_payload_numpy(
    source_bytes: bytes,
    *,
    source_width: int,
    source_height: int,
    mapping: ViewportMapping,
    source_format: str,
) -> bytes:
    numpy_module = _require_numpy()
    expected_size = source_width * source_height * 3
    if len(source_bytes) < expected_size:
        raise RuntimeError("Frame buffer is too small for RGB viewport rendering.")

    source_image = numpy_module.frombuffer(source_bytes, dtype=numpy_module.uint8, count=expected_size).reshape(
        (source_height, source_width, 3)
    )
    source_x, source_y = _build_source_indices_numpy(mapping, source_width, source_height, numpy_module)
    sampled = source_image[source_y[:, None], source_x[None, :]]
    if source_format == "bgr8":
        sampled = sampled[:, :, ::-1]

    viewport = numpy_module.zeros((mapping.viewport_height, mapping.viewport_width, 3), dtype=numpy_module.uint8)
    viewport[
        mapping.dst_y : mapping.dst_y + mapping.copy_height,
        mapping.dst_x : mapping.dst_x + mapping.copy_width,
        :,
    ] = sampled
    return viewport.tobytes()


def _build_source_indices_numpy(mapping: ViewportMapping, source_width: int, source_height: int, numpy_module):
    x_scaled = mapping.src_x + numpy_module.arange(mapping.copy_width)
    y_scaled = mapping.src_y + numpy_module.arange(mapping.copy_height)
    x_source = numpy_module.clip((x_scaled / mapping.display_scale).astype(numpy_module.int32), 0, source_width - 1)
    y_source = numpy_module.clip((y_scaled / mapping.display_scale).astype(numpy_module.int32), 0, source_height - 1)
    return x_source, y_source


_NUMPY_MODULE = None
_HAS_NUMPY = find_spec("numpy") is not None


def _is_numpy_available() -> bool:
    return _HAS_NUMPY


def _require_numpy():
    global _NUMPY_MODULE
    if _NUMPY_MODULE is None:
        _NUMPY_MODULE = import_module("numpy")
    return _NUMPY_MODULE


def _convert_high_bit_mono_to_mono8(source_bytes: bytes, width: int, height: int, pixel_format: str) -> bytes:
    expected_size = width * height * 2
    if len(source_bytes) < expected_size:
        raise RuntimeError(f"Frame buffer is too small for {pixel_format} viewport rendering.")
    if _is_numpy_available():
        numpy_module = _require_numpy()
        values = numpy_module.frombuffer(source_bytes, dtype=numpy_module.uint16, count=width * height)
        return (values >> 8).astype(numpy_module.uint8).tobytes()
    return source_bytes[1:expected_size:2]


__all__ = [
    "RenderedViewportImage",
    "render_viewport_image",
]
