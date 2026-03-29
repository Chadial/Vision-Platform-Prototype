from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from vision_platform.integrations.camera import SimulatedCameraDriver
from vision_platform.libraries.common_models import FocusRequest, RoiDefinition
from vision_platform.libraries.focus_core import evaluate_focus


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
    driver = SimulatedCameraDriver(sample_image_paths=sample_paths, loop_samples=False)
    driver.initialize(camera_id="postprocess-focus-report")
    try:
        entries: list[PostprocessFocusReportEntry] = []
        request = FocusRequest(method=method, roi=roi)
        for sample_path in sample_paths:
            frame = driver.capture_snapshot()
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
    finally:
        driver.shutdown()


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

    sample_paths = sorted([*sample_dir.glob("*.pgm"), *sample_dir.glob("*.ppm")])
    if not sample_paths:
        raise ValueError(f"Sample directory '{sample_dir}' does not contain any .pgm or .ppm files.")
    return sample_paths


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a thin offline focus report over stored sample images.")
    parser.add_argument("sample_dir", type=Path, help="Directory containing .pgm or .ppm sample images.")
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
