from __future__ import annotations

from vision_platform.libraries.common_models import RoiDefinition, RoiShape


class RoiStateService:
    """Store ROI selections by shape and resolve the shared ROI fallback rule."""

    def __init__(self) -> None:
        self._rois_by_shape: dict[RoiShape, RoiDefinition] = {}
        self._active_shape: RoiShape | None = None

    def set_active_roi(self, roi: RoiDefinition) -> None:
        self._rois_by_shape[roi.shape] = self._set_roi_active(roi, True)
        self._active_shape = roi.shape
        for shape, other_roi in list(self._rois_by_shape.items()):
            if shape != roi.shape:
                self._rois_by_shape[shape] = self._set_roi_active(other_roi, False)

    def clear_active_roi(self) -> None:
        if self._active_shape is None:
            return
        active_roi = self._rois_by_shape.get(self._active_shape)
        if active_roi is not None:
            self._rois_by_shape[self._active_shape] = self._set_roi_active(active_roi, False)
        self._active_shape = None

    def get_active_roi(self) -> RoiDefinition | None:
        if self._active_shape is None:
            return None
        active_roi = self._rois_by_shape.get(self._active_shape)
        if active_roi is None or not active_roi.enabled:
            return None
        return active_roi

    def get_roi(self, roi_shape: RoiShape) -> RoiDefinition | None:
        return self._rois_by_shape.get(roi_shape)

    def get_active_roi_shape(self) -> RoiShape | None:
        return self._active_shape

    def resolve_active_roi(self, explicit_roi: RoiDefinition | None = None) -> RoiDefinition | None:
        if explicit_roi is not None:
            return explicit_roi
        return self.get_active_roi()

    @staticmethod
    def _set_roi_active(roi: RoiDefinition, enabled: bool) -> RoiDefinition:
        if roi.enabled == enabled:
            return roi
        return RoiDefinition(
            roi_id=roi.roi_id,
            shape=roi.shape,
            points=roi.points,
            label=roi.label,
            enabled=enabled,
            metadata=dict(roi.metadata),
        )
