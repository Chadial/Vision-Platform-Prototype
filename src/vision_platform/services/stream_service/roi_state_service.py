from __future__ import annotations

from vision_platform.libraries.common_models import RoiDefinition


class RoiStateService:
    """Store one active ROI selection for preview-adjacent consumers."""

    def __init__(self) -> None:
        self._active_roi: RoiDefinition | None = None

    def set_active_roi(self, roi: RoiDefinition) -> None:
        self._active_roi = roi

    def clear_active_roi(self) -> None:
        self._active_roi = None

    def get_active_roi(self) -> RoiDefinition | None:
        return self._active_roi
