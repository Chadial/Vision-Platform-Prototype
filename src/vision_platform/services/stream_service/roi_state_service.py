from __future__ import annotations

from vision_platform.libraries.common_models import RoiDefinition


class RoiStateService:
    """Store one active ROI selection and resolve the shared ROI fallback rule."""

    def __init__(self) -> None:
        self._active_roi: RoiDefinition | None = None

    def set_active_roi(self, roi: RoiDefinition) -> None:
        self._active_roi = roi

    def clear_active_roi(self) -> None:
        self._active_roi = None

    def get_active_roi(self) -> RoiDefinition | None:
        return self._active_roi

    def resolve_active_roi(self, explicit_roi: RoiDefinition | None = None) -> RoiDefinition | None:
        if explicit_roi is not None:
            return explicit_roi
        return self._active_roi
