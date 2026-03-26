from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


RoiShape = Literal["rectangle", "ellipse", "freehand"]


@dataclass(slots=True)
class RoiDefinition:
    """Minimal ROI definition that stays portable to C# DTOs."""

    roi_id: str
    shape: RoiShape
    points: tuple[tuple[float, float], ...] = ()
    label: str | None = None
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
