from __future__ import annotations

import math

from vision_platform.libraries.common_models.roi_models import RoiDefinition


def roi_bounds(roi: RoiDefinition) -> tuple[float, float, float, float] | None:
    """Return an axis-aligned bounding box for portable ROI bookkeeping."""

    if not roi.points:
        return None
    xs = [point[0] for point in roi.points]
    ys = [point[1] for point in roi.points]
    return min(xs), min(ys), max(xs), max(ys)


def roi_centroid(roi: RoiDefinition) -> tuple[float, float] | None:
    """Return a portable ROI center point for overlays and other display consumers."""

    if not roi.points:
        return None
    x_sum = sum(point[0] for point in roi.points)
    y_sum = sum(point[1] for point in roi.points)
    point_count = len(roi.points)
    return x_sum / point_count, y_sum / point_count


def roi_pixel_bounds(roi: RoiDefinition, width: int, height: int) -> tuple[int, int, int, int] | None:
    """Return frame-clamped integer ROI bounds for consumers that work on pixel grids."""

    bounds = roi_bounds(roi)
    if bounds is None:
        return None

    min_x, min_y, max_x, max_y = bounds
    left = max(0, min(width, math.floor(min_x)))
    top = max(0, min(height, math.floor(min_y)))
    right = max(0, min(width, math.ceil(max_x)))
    bottom = max(0, min(height, math.ceil(max_y)))
    if right <= left or bottom <= top:
        return None
    return left, top, right, bottom


def roi_mask(roi: RoiDefinition, width: int, height: int) -> tuple[tuple[int, int, int, int], list[list[bool]]] | None:
    """Return a cropped boolean mask for the ROI intersection with a frame."""

    pixel_bounds = roi_pixel_bounds(roi, width=width, height=height)
    if pixel_bounds is None:
        return None

    left, top, right, bottom = pixel_bounds
    mask_width = right - left
    mask_height = bottom - top
    if mask_width <= 0 or mask_height <= 0:
        return None

    if roi.shape == "rectangle":
        mask = [[True for _ in range(mask_width)] for _ in range(mask_height)]
        return pixel_bounds, mask

    if roi.shape == "ellipse":
        float_bounds = roi_bounds(roi)
        if float_bounds is None:
            return None

        min_x, min_y, max_x, max_y = float_bounds
        radius_x = (max_x - min_x) / 2.0
        radius_y = (max_y - min_y) / 2.0
        if radius_x <= 0.0 or radius_y <= 0.0:
            return None

        center_x = min_x + radius_x
        center_y = min_y + radius_y
        mask: list[list[bool]] = []
        for y in range(top, bottom):
            row: list[bool] = []
            for x in range(left, right):
                relative_x = ((x + 0.5) - center_x) / radius_x
                relative_y = ((y + 0.5) - center_y) / radius_y
                row.append((relative_x * relative_x) + (relative_y * relative_y) <= 1.0)
            mask.append(row)

        if not any(any(row) for row in mask):
            return None
        return pixel_bounds, mask

    return None
