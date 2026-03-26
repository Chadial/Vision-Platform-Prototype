from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from vision_platform.libraries.common_models.roi_models import RoiDefinition


FocusMethod = Literal["laplace", "tenengrad", "sobel", "scharr", "edge_energy"]


@dataclass(slots=True)
class FocusRequest:
    """Portable focus-analysis request for live, snapshot, or offline use."""

    method: FocusMethod = "laplace"
    roi: RoiDefinition | None = None
    normalize: bool = True


@dataclass(slots=True)
class FocusResult:
    """Portable focus-analysis result for manual focus guidance and later automation."""

    method: FocusMethod
    score: float
    is_valid: bool = True
    metric_name: str | None = None
    roi_id: str | None = None
    source_frame_id: int | None = None

    def __post_init__(self) -> None:
        if self.metric_name is None:
            self.metric_name = self.method


@dataclass(slots=True)
class FocusOverlayData:
    """Portable display payload for preview and overlay consumers."""

    score: float
    metric_name: str
    anchor_x: float
    anchor_y: float
    is_valid: bool
    roi_id: str | None = None
    source_frame_id: int | None = None
    region_bounds: tuple[float, float, float, float] | None = None


@dataclass(slots=True)
class FocusPreviewState:
    """Bundle one focus evaluation with its overlay-ready display payload."""

    result: FocusResult
    overlay: FocusOverlayData
