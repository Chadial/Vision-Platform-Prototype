from __future__ import annotations

from camera_app.validation.request_validation import normalize_file_extension

_BMP_COMPATIBLE_PIXEL_FORMATS = {"mono8", "rgb8", "bgr8"}


def is_bmp_compatible_pixel_format(pixel_format: str | None) -> bool:
    return _normalize_pixel_format(pixel_format) in _BMP_COMPATIBLE_PIXEL_FORMATS


def choose_snapshot_file_extension(
    *,
    pixel_format: str | None,
    requested_extension: str | None = None,
) -> str:
    if requested_extension is not None:
        normalized_extension = normalize_file_extension(requested_extension, "file_extension")
        if normalized_extension == ".bmp" and not is_bmp_compatible_pixel_format(pixel_format):
            return ".raw"
        return normalized_extension
    return ".bmp" if is_bmp_compatible_pixel_format(pixel_format) else ".raw"


def _normalize_pixel_format(pixel_format: str | None) -> str:
    return (pixel_format or "").strip().lower()
