from __future__ import annotations

from vision_platform.libraries.common_models import FocusPreviewState, FocusRequest, RoiDefinition
from vision_platform.libraries.focus_core import (
    FocusEvaluator,
    LaplaceFocusEvaluator,
    build_focus_overlay_data,
)
from vision_platform.services.stream_service.preview_service import PreviewService
from vision_platform.services.stream_service.roi_state_service import RoiStateService


class FocusPreviewService:
    """Evaluate focus on the latest preview frame without introducing UI coupling."""

    def __init__(
        self,
        preview_service: PreviewService,
        focus_evaluator: FocusEvaluator | None = None,
        roi_state_service: RoiStateService | None = None,
    ) -> None:
        self._preview_service = preview_service
        self._focus_evaluator = focus_evaluator or LaplaceFocusEvaluator()
        self._roi_state_service = roi_state_service
        self._latest_focus_state: FocusPreviewState | None = None

    def refresh_once(self, roi: RoiDefinition | None = None) -> FocusPreviewState | None:
        frame = self._preview_service.get_latest_frame()
        if frame is None:
            self._preview_service.refresh_once()
            frame = self._preview_service.get_latest_frame()
        if frame is None:
            return None

        active_roi = self._resolve_active_roi(roi)
        request = FocusRequest(method="laplace", roi=active_roi)
        result = self._focus_evaluator.evaluate(frame, request=request)
        overlay = build_focus_overlay_data(result, frame=frame, roi=active_roi)
        self._latest_focus_state = FocusPreviewState(result=result, overlay=overlay)
        return self._latest_focus_state

    def get_latest_focus_state(self) -> FocusPreviewState | None:
        return self._latest_focus_state

    def _resolve_active_roi(self, explicit_roi: RoiDefinition | None) -> RoiDefinition | None:
        if self._roi_state_service is None:
            return explicit_roi
        return self._roi_state_service.resolve_active_roi(explicit_roi)
