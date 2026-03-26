from __future__ import annotations

from dataclasses import dataclass

from vision_platform.libraries.common_models.focus_models import FocusOverlayData


@dataclass(slots=True)
class RoiOverlayData:
    """Portable active-ROI payload for preview, snapshot, or later display consumers."""

    roi_id: str
    anchor_x: float
    anchor_y: float
    region_bounds: tuple[float, float, float, float] | None = None


@dataclass(slots=True)
class DisplayOverlayPayload:
    """UI-free composition result for preview, snapshot, and ROI overlay consumers."""

    active_roi: RoiOverlayData | None = None
    preview_focus: FocusOverlayData | None = None
    snapshot_focus: FocusOverlayData | None = None
