from __future__ import annotations

from vision_platform.libraries.common_models import (
    DisplayOverlayPayload,
    FocusPreviewState,
    RoiDefinition,
    RoiOverlayData,
)
from vision_platform.libraries.roi_core import roi_bounds, roi_centroid
from vision_platform.services.recording_service.snapshot_focus_service import SnapshotFocusCapture
from vision_platform.services.stream_service.roi_state_service import RoiStateService


class OverlayCompositionService:
    """Compose preview, snapshot, and active-ROI data into one UI-free display payload."""

    def __init__(self, roi_state_service: RoiStateService | None = None) -> None:
        self._roi_state_service = roi_state_service

    def compose(
        self,
        preview_focus_state: FocusPreviewState | None = None,
        snapshot_focus_state: FocusPreviewState | None = None,
        snapshot_focus_capture: SnapshotFocusCapture | None = None,
        active_roi: RoiDefinition | None = None,
    ) -> DisplayOverlayPayload:
        resolved_snapshot_focus_state = snapshot_focus_state
        if resolved_snapshot_focus_state is None and snapshot_focus_capture is not None:
            resolved_snapshot_focus_state = snapshot_focus_capture.focus_state

        resolved_active_roi = active_roi if active_roi is not None else self._get_active_roi()
        return DisplayOverlayPayload(
            active_roi=_build_active_roi_overlay(resolved_active_roi),
            preview_focus=preview_focus_state.overlay if preview_focus_state is not None else None,
            snapshot_focus=resolved_snapshot_focus_state.overlay if resolved_snapshot_focus_state is not None else None,
        )

    def _get_active_roi(self) -> RoiDefinition | None:
        if self._roi_state_service is None:
            return None
        return self._roi_state_service.get_active_roi()


def _build_active_roi_overlay(roi: RoiDefinition | None) -> RoiOverlayData | None:
    if roi is None or not roi.enabled:
        return None

    bounds = roi_bounds(roi)
    anchor = roi_centroid(roi)
    if bounds is None or anchor is None:
        return None

    return RoiOverlayData(
        roi_id=roi.roi_id,
        anchor_x=anchor[0],
        anchor_y=anchor[1],
        region_bounds=bounds,
    )
