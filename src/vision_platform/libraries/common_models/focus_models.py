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
    """Minimal focus-analysis result placeholder for later expansion."""

    method: FocusMethod
    score: float
    roi_id: str | None = None
    source_frame_id: int | None = None
