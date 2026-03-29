from __future__ import annotations

import argparse
import struct
from dataclasses import dataclass
from pathlib import Path

from vision_platform.integrations.camera import SimulatedCameraDriver
from vision_platform.libraries.common_models import FocusRequest, RoiDefinition
from vision_platform.libraries.focus_core import evaluate_focus
from vision_platform.models import CapturedFrame


@dataclass(slots=True)
class PostprocessFocusReportEntry:
    source_path: Path
    method: str
    score: float
    is_valid: bool
    roi_id: str | None
    frame_width: int
    frame_height: int
    pixel_format: str | None


def run_focus_report(
    sample_dir: Path,
    method: str = "laplace",
    roi: RoiDefinition | None = None,
) -> list[PostprocessFocusReportEntry]:
    sample_paths = _collect_sample_paths(sample_dir)
    entries: list[PostprocessFocusReportEntry] = []
    request = FocusRequest(method=method, roi=roi)
    for sample_path in sample_paths:
        frame = _load_focus_frame(sample_path)
        result = evaluate_focus(frame, request=request)
        entries.append(
            PostprocessFocusReportEntry(
                source_path=sample_path,
                method=result.method,
                score=result.score,
                is_valid=result.is_valid,
                roi_id=result.roi_id,
                frame_width=frame.width,
                frame_height=frame.height,
                pixel_format=frame.pixel_format,
            )
        )
    return entries


def format_focus_report(entries: list[PostprocessFocusReportEntry]) -> str:
    lines = [
        (
            f"{entry.source_path.name}: method={entry.method} "
            f"score={entry.score:.6f} valid={str(entry.is_valid).lower()} "
            f"size={entry.frame_width}x{entry.frame_height} pixel_format={entry.pixel_format or '-'}"
        )
        for entry in entries
    ]
    return "\n".join(lines)


def _collect_sample_paths(sample_dir: Path) -> list[Path]:
    if not sample_dir.exists() or not sample_dir.is_dir():
        raise ValueError(f"Sample directory '{sample_dir}' does not exist or is not a directory.")

    sample_paths = sorted([*sample_dir.glob("*.pgm"), *sample_dir.glob("*.ppm"), *sample_dir.glob("*.bmp")])
    if not sample_paths:
        raise ValueError(f"Sample directory '{sample_dir}' does not contain any .pgm, .ppm, or .bmp files.")
    return sample_paths


def _load_focus_frame(sample_path: Path) -> CapturedFrame:
    suffix = sample_path.suffix.lower()
    if suffix in {".pgm", ".ppm"}:
        return _load_sample_frame(sample_path)
    if suffix == ".bmp":
        return _load_bmp_frame(sample_path)
    raise ValueError(f"Unsupported offline focus input '{sample_path.name}'.")


def _load_sample_frame(sample_path: Path) -> CapturedFrame:
    driver = SimulatedCameraDriver(sample_image_paths=[sample_path], loop_samples=False)
    driver.initialize(camera_id="postprocess-focus-report")
    try:
        return driver.capture_snapshot()
    finally:
        driver.shutdown()


def _load_bmp_frame(sample_path: Path) -> CapturedFrame:
    payload = sample_path.read_bytes()
    if len(payload) < 54 or payload[:2] != b"BM":
        raise RuntimeError(f"Unsupported BMP input '{sample_path.name}'.")

    pixel_offset = struct.unpack_from("<I", payload, 10)[0]
    dib_header_size = struct.unpack_from("<I", payload, 14)[0]
    if dib_header_size < 40 or len(payload) < 14 + dib_header_size:
        raise RuntimeError(f"Unsupported BMP DIB header in '{sample_path.name}'.")

    width, height = struct.unpack_from("<ii", payload, 18)
    planes, bits_per_pixel, compression = struct.unpack_from("<HHI", payload, 26)
    if planes != 1 or width <= 0 or height == 0:
        raise RuntimeError(f"Unsupported BMP geometry in '{sample_path.name}'.")
    if compression != 0 or bits_per_pixel not in {8, 24}:
        raise RuntimeError(f"Unsupported BMP encoding in '{sample_path.name}'.")

    top_down = height < 0
    frame_height = abs(height)
    bytes_per_pixel = 1 if bits_per_pixel == 8 else 3
    row_stride = width * bytes_per_pixel
    padded_row_stride = (row_stride + 3) & ~3
    expected_size = padded_row_stride * frame_height
    if pixel_offset + expected_size > len(payload):
        raise RuntimeError(f"BMP pixel data is truncated in '{sample_path.name}'.")

    rows: list[bytes] = []
    for row_index in range(frame_height):
        row_start = pixel_offset + (row_index * padded_row_stride)
        rows.append(payload[row_start : row_start + row_stride])
    if not top_down:
        rows.reverse()

    pixel_bytes = b"".join(rows)
    pixel_format = "Mono8" if bits_per_pixel == 8 else "Bgr8"
    return CapturedFrame(
        raw_frame=pixel_bytes,
        width=width,
        height=frame_height,
        pixel_format=pixel_format,
    )


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a thin offline focus report over stored sample or BMP images.")
    parser.add_argument("sample_dir", type=Path, help="Directory containing .pgm, .ppm, or .bmp images.")
    parser.add_argument(
        "--method",
        default="laplace",
        help="Focus method to evaluate (`laplace` or `tenengrad`).",
    )
    return parser


def main() -> int:
    parser = _build_argument_parser()
    args = parser.parse_args()
    report = run_focus_report(sample_dir=args.sample_dir, method=args.method)
    print(format_focus_report(report))
    return 0


__all__ = [
    "PostprocessFocusReportEntry",
    "format_focus_report",
    "main",
    "run_focus_report",
]
