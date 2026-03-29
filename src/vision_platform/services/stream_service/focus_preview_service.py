from __future__ import annotations

from vision_platform.libraries.common_models import FocusMethod, FocusPreviewState, FocusRequest, RoiDefinition
from vision_platform.libraries.focus_core import (
    FocusEvaluator,
    LaplaceFocusEvaluator,
    TenengradFocusEvaluator,
    build_focus_overlay_data,
    create_focus_evaluator,
)
from vision_platform.services.stream_service.preview_service import PreviewService
from vision_platform.services.stream_service.roi_state_service import RoiStateService


class FocusPreviewService:
    """Evaluate focus on the latest preview frame without introducing UI coupling."""

    def __init__(
        self,
        preview_service: PreviewService,
        focus_evaluator: FocusEvaluator | None = None,
        focus_method: FocusMethod | None = None,
        roi_state_service: RoiStateService | None = None,
    ) -> None:
        self._preview_service = preview_service
        self._focus_evaluator = focus_evaluator or create_focus_evaluator(focus_method or "laplace")
        self._focus_method: FocusMethod = focus_method or _infer_focus_method(self._focus_evaluator)
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
        request = FocusRequest(method=self._focus_method, roi=active_roi)
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


def _infer_focus_method(focus_evaluator: FocusEvaluator) -> FocusMethod:
    if isinstance(focus_evaluator, TenengradFocusEvaluator):
        return "tenengrad"
    if isinstance(focus_evaluator, LaplaceFocusEvaluator):
        return "laplace"
    return "laplace"
