from __future__ import annotations

_BMP_COMPATIBLE_PIXEL_FORMATS = {"mono8", "rgb8", "bgr8"}


def is_bmp_compatible_pixel_format(pixel_format: str | None) -> bool:
    return _normalize_pixel_format(pixel_format) in _BMP_COMPATIBLE_PIXEL_FORMATS


def choose_snapshot_file_extension(
    *,
    pixel_format: str | None,
    requested_extension: str | None = None,
) -> str:
    if requested_extension is not None:
        normalized_extension = _normalize_file_extension(requested_extension, "file_extension")
        if normalized_extension == ".bmp" and not is_bmp_compatible_pixel_format(pixel_format):
            return ".raw"
        return normalized_extension
    return ".bmp" if is_bmp_compatible_pixel_format(pixel_format) else ".raw"


def _normalize_file_extension(file_extension: str, field_name: str) -> str:
    stripped_extension = file_extension.strip()
    if not stripped_extension:
        raise ValueError(f"{field_name} must not be empty.")
    if any(separator in stripped_extension for separator in ("/", "\\")):
        raise ValueError(f"{field_name} must be a file extension, not a path.")
    if stripped_extension.startswith("."):
        stripped_extension = stripped_extension[1:]
    if not stripped_extension:
        raise ValueError(f"{field_name} must include characters after '.'.")
    if "." in stripped_extension:
        raise ValueError(f"{field_name} must contain only a single extension segment.")
    if any(character.isspace() for character in stripped_extension):
        raise ValueError(f"{field_name} must not contain whitespace.")
    return f".{stripped_extension}"


def _normalize_pixel_format(pixel_format: str | None) -> str:
    return (pixel_format or "").strip().lower()
