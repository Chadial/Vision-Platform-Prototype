from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from vision_platform.apps.postprocess_tool.focus_report import _load_bmp_frame
from vision_platform.libraries.common_models import FocusRequest, RoiDefinition
from vision_platform.libraries.focus_core import evaluate_focus


@dataclass(slots=True)
class BarRoi:
    left: int
    top: int
    right: int
    bottom: int
    threshold: int
    row_mean_min: float
    row_mean_max: float

    @property
    def width(self) -> int:
        return self.right - self.left

    @property
    def height(self) -> int:
        return self.bottom - self.top

    def to_roi_definition(self) -> RoiDefinition:
        return RoiDefinition(
            roi_id="bar",
            shape="rectangle",
            points=(
                (float(self.left), float(self.top)),
                (float(self.right), float(self.top)),
                (float(self.right), float(self.bottom)),
                (float(self.left), float(self.bottom)),
            ),
        )


def _intensity_plane(frame) -> list[list[int]]:
    data = frame.raw_frame
    width = frame.width
    height = frame.height
    pixel_format = (frame.pixel_format or "Mono8").lower()

    if pixel_format == "mono8":
        return [list(data[row_start : row_start + width]) for row_start in range(0, width * height, width)]

    if pixel_format == "mono16":
        expected_size = width * height * 2
        values = [
            int.from_bytes(data[index : index + 2], byteorder="little") // 257
            for index in range(0, expected_size, 2)
        ]
        return [values[row_start : row_start + width] for row_start in range(0, len(values), width)]

    if pixel_format not in {"rgb8", "bgr8"}:
        raise RuntimeError(f"Unsupported pixel format for bar detection: {frame.pixel_format!r}")

    expected_size = width * height * 3
    values: list[int] = []
    for index in range(0, expected_size, 3):
        first = data[index]
        second = data[index + 1]
        third = data[index + 2]
        if pixel_format == "rgb8":
            red, green, blue = first, second, third
        else:
            blue, green, red = first, second, third
        values.append((77 * red + 150 * green + 29 * blue) // 256)
    return [values[row_start : row_start + width] for row_start in range(0, len(values), width)]


def _otsu_threshold(values: list[float]) -> int:
    histogram = [0] * 256
    for value in values:
        bucket = max(0, min(255, int(round(value))))
        histogram[bucket] += 1

    total = sum(histogram)
    weighted_total = sum(bucket * count for bucket, count in enumerate(histogram))
    weighted_background = 0
    background_count = 0
    best_threshold = 0
    best_variance = -1.0

    for threshold, count in enumerate(histogram):
        background_count += count
        if background_count == 0:
            continue
        foreground_count = total - background_count
        if foreground_count == 0:
            break

        weighted_background += threshold * count
        background_mean = weighted_background / background_count
        foreground_mean = (weighted_total - weighted_background) / foreground_count
        variance = background_count * foreground_count * (background_mean - foreground_mean) ** 2
        if variance > best_variance:
            best_variance = variance
            best_threshold = threshold

    return best_threshold


def _largest_true_run(mask: list[bool]) -> tuple[int, int]:
    best_start = 0
    best_end = -1
    current_start: int | None = None

    for index, value in enumerate([*mask, False]):
        if value and current_start is None:
            current_start = index
        if not value and current_start is not None:
            current_end = index - 1
            if current_end - current_start > best_end - best_start:
                best_start = current_start
                best_end = current_end
            current_start = None

    if best_end < best_start:
        raise RuntimeError("No dark horizontal bar candidate was found.")
    return best_start, best_end


def detect_bar_roi(
    plane: list[list[int]],
    *,
    threshold: int | None = None,
    padding: int = 8,
    min_column_dark_fraction: float = 0.4,
) -> BarRoi:
    height = len(plane)
    width = len(plane[0]) if plane else 0
    if width < 3 or height < 3:
        raise RuntimeError("Image is too small for bar ROI detection.")

    row_means = [sum(row) / width for row in plane]
    effective_threshold = threshold if threshold is not None else _otsu_threshold(row_means)
    dark_row_mask = [row_mean < effective_threshold for row_mean in row_means]
    top, bottom_inclusive = _largest_true_run(dark_row_mask)
    top = max(0, top - padding)
    bottom = min(height, bottom_inclusive + 1 + padding)

    column_dark_fractions: list[float] = []
    for x in range(width):
        dark_count = sum(1 for y in range(top, bottom) if plane[y][x] < effective_threshold)
        column_dark_fractions.append(dark_count / max(1, bottom - top))

    dark_column_mask = [fraction >= min_column_dark_fraction for fraction in column_dark_fractions]
    try:
        left, right_inclusive = _largest_true_run(dark_column_mask)
    except RuntimeError:
        left, right_inclusive = 0, width - 1

    left = max(0, left - padding)
    right = min(width, right_inclusive + 1 + padding)

    return BarRoi(
        left=left,
        top=top,
        right=right,
        bottom=bottom,
        threshold=effective_threshold,
        row_mean_min=min(row_means),
        row_mean_max=max(row_means),
    )


def analyze_image(
    image_path: Path,
    *,
    threshold: int | None = None,
    padding: int = 8,
    min_column_dark_fraction: float = 0.4,
) -> dict[str, object]:
    frame = _load_bmp_frame(image_path)
    plane = _intensity_plane(frame)
    bar_roi = detect_bar_roi(
        plane,
        threshold=threshold,
        padding=padding,
        min_column_dark_fraction=min_column_dark_fraction,
    )
    roi_definition = bar_roi.to_roi_definition()

    focus_results: dict[str, dict[str, object]] = {}
    for method in ("laplace", "tenengrad"):
        full_result = evaluate_focus(frame, FocusRequest(method=method))
        roi_result = evaluate_focus(frame, FocusRequest(method=method, roi=roi_definition))
        focus_results[method] = {
            "full_score": full_result.score,
            "full_valid": full_result.is_valid,
            "bar_roi_score": roi_result.score,
            "bar_roi_valid": roi_result.is_valid,
            "metric_name": roi_result.metric_name,
        }

    return {
        "image": str(image_path),
        "image_size": {"width": frame.width, "height": frame.height},
        "pixel_format": frame.pixel_format,
        "bar_roi": {
            "left": bar_roi.left,
            "top": bar_roi.top,
            "right": bar_roi.right,
            "bottom": bar_roi.bottom,
            "width": bar_roi.width,
            "height": bar_roi.height,
            "threshold": bar_roi.threshold,
            "row_mean_min": bar_roi.row_mean_min,
            "row_mean_max": bar_roi.row_mean_max,
        },
        "focus": focus_results,
    }


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Detect the horizontal dark bar in a BMP image and compute focus scores for the bar ROI.",
    )
    parser.add_argument("image_path", type=Path, help="Path to the BMP image to analyze.")
    parser.add_argument(
        "--threshold",
        type=int,
        default=None,
        help="Optional dark-row threshold. Defaults to Otsu thresholding over row means.",
    )
    parser.add_argument("--padding", type=int, default=8, help="Pixel padding added around the detected ROI.")
    parser.add_argument(
        "--min-column-dark-fraction",
        type=float,
        default=0.4,
        help="Minimum dark-pixel fraction per column inside the bar row band.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser


def _format_result(result: dict[str, object]) -> str:
    roi = result["bar_roi"]
    focus = result["focus"]
    lines = [
        f"image={result['image']}",
        f"size={result['image_size']['width']}x{result['image_size']['height']} pixel_format={result['pixel_format']}",
        (
            "bar_roi="
            f"left={roi['left']} top={roi['top']} right={roi['right']} bottom={roi['bottom']} "
            f"width={roi['width']} height={roi['height']} threshold={roi['threshold']}"
        ),
        f"row_mean_range={roi['row_mean_min']:.3f}..{roi['row_mean_max']:.3f}",
    ]
    for method in ("laplace", "tenengrad"):
        method_result = focus[method]
        lines.append(
            f"{method}: full={method_result['full_score']:.9f} "
            f"bar_roi={method_result['bar_roi_score']:.9f} "
            f"metric={method_result['metric_name']} "
            f"valid={str(method_result['bar_roi_valid']).lower()}"
        )
    return "\n".join(lines)


def main() -> int:
    parser = _build_argument_parser()
    args = parser.parse_args()
    result = analyze_image(
        args.image_path,
        threshold=args.threshold,
        padding=args.padding,
        min_column_dark_fraction=args.min_column_dark_fraction,
    )
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(_format_result(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
