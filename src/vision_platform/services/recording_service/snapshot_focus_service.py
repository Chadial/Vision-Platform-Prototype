from __future__ import annotations

from dataclasses import dataclass

from vision_platform.integrations.camera import CameraDriver
from vision_platform.libraries.common_models import FocusPreviewState, FocusRequest, RoiDefinition
from vision_platform.libraries.focus_core import FocusEvaluator, LaplaceFocusEvaluator, build_focus_overlay_data
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
        roi_state_service: RoiStateService | None = None,
    ) -> None:
        self._driver = driver
        self._focus_evaluator = focus_evaluator or LaplaceFocusEvaluator()
        self._roi_state_service = roi_state_service

    def capture_focus_state(self, roi: RoiDefinition | None = None) -> SnapshotFocusCapture:
        frame = self._driver.capture_snapshot()
        active_roi = roi if roi is not None else self._get_active_roi()
        request = FocusRequest(method="laplace", roi=active_roi)
        result = self._focus_evaluator.evaluate(frame, request=request)
        overlay = build_focus_overlay_data(result, frame=frame, roi=active_roi)
        return SnapshotFocusCapture(
            frame=frame,
            focus_state=FocusPreviewState(result=result, overlay=overlay),
        )

    def _get_active_roi(self) -> RoiDefinition | None:
        if self._roi_state_service is None:
            return None
        return self._roi_state_service.get_active_roi()
