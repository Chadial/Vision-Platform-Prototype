from __future__ import annotations

from vision_platform.libraries.common_models.roi_models import RoiDefinition


def roi_bounds(roi: RoiDefinition) -> tuple[float, float, float, float] | None:
    """Return an axis-aligned bounding box for portable ROI bookkeeping."""

    if not roi.points:
        return None
    xs = [point[0] for point in roi.points]
    ys = [point[1] for point in roi.points]
    return min(xs), min(ys), max(xs), max(ys)
