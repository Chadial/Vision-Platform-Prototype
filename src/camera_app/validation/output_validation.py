from __future__ import annotations

from camera_app.validation.request_validation import normalize_file_extension


def validate_frame_output_combination(pixel_format: str | None, file_extension: str) -> str:
    normalized_extension = normalize_file_extension(file_extension, "file_extension")
    normalized_format = (pixel_format or "").strip().lower()

    if normalized_extension in {".raw", ".bin"}:
        return normalized_extension

    if normalized_extension == ".png":
        if normalized_format in {"mono8", "rgb8", "bgr8", "mono10", "mono12", "mono14", "mono16"}:
            return normalized_extension
        raise RuntimeError(
            f"Pixel format '{pixel_format}' is not supported for PNG output."
        )

    if normalized_extension in {".tif", ".tiff"}:
        if normalized_format in {"mono8", "mono10", "mono12", "mono14", "mono16"}:
            return normalized_extension
        raise RuntimeError(
            f"Pixel format '{pixel_format}' is not supported for TIFF output."
        )

    raise RuntimeError(f"Unsupported snapshot file extension '{normalized_extension}'.")
