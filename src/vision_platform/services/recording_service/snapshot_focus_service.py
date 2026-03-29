from __future__ import annotations

from dataclasses import dataclass

from vision_platform.integrations.camera import CameraDriver
from vision_platform.libraries.common_models import FocusMethod, FocusPreviewState, FocusRequest, RoiDefinition
from vision_platform.libraries.focus_core import (
    FocusEvaluator,
    LaplaceFocusEvaluator,
    TenengradFocusEvaluator,
    build_focus_overlay_data,
    create_focus_evaluator,
)
from vision_platform.models import CapturedFrame
from vision_platform.services.stream_service.roi_state_service import RoiStateService


@dataclass(slots=True)
class SnapshotFocusCapture:
    """Bundle one captured snapshot frame with its derived focus state."""

    frame: CapturedFrame
    focus_state: FocusPreviewState


class SnapshotFocusService:
    """Capture one snapshot frame and derive focus state without coupling to UI code."""

    def __init__(
        self,
        driver: CameraDriver,
        focus_evaluator: FocusEvaluator | None = None,
        focus_method: FocusMethod | None = None,
        roi_state_service: RoiStateService | None = None,
    ) -> None:
        self._driver = driver
        self._focus_evaluator = focus_evaluator or create_focus_evaluator(focus_method or "laplace")
        self._focus_method: FocusMethod = focus_method or _infer_focus_method(self._focus_evaluator)
        self._roi_state_service = roi_state_service

    def capture_focus_state(self, roi: RoiDefinition | None = None) -> SnapshotFocusCapture:
        frame = self._driver.capture_snapshot()
        active_roi = self._resolve_active_roi(roi)
        request = FocusRequest(method=self._focus_method, roi=active_roi)
        result = self._focus_evaluator.evaluate(frame, request=request)
        overlay = build_focus_overlay_data(result, frame=frame, roi=active_roi)
        return SnapshotFocusCapture(
            frame=frame,
            focus_state=FocusPreviewState(result=result, overlay=overlay),
        )

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
