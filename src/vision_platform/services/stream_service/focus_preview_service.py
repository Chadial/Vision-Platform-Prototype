from __future__ import annotations

from vision_platform.libraries.common_models import FocusPreviewState, FocusRequest, RoiDefinition
from vision_platform.libraries.focus_core import (
    FocusEvaluator,
    LaplaceFocusEvaluator,
    build_focus_overlay_data,
)
from vision_platform.services.stream_service.preview_service import PreviewService


class FocusPreviewService:
    """Evaluate focus on the latest preview frame without introducing UI coupling."""

    def __init__(
        self,
        preview_service: PreviewService,
        focus_evaluator: FocusEvaluator | None = None,
    ) -> None:
        self._preview_service = preview_service
        self._focus_evaluator = focus_evaluator or LaplaceFocusEvaluator()
        self._latest_focus_state: FocusPreviewState | None = None

    def refresh_once(self, roi: RoiDefinition | None = None) -> FocusPreviewState | None:
        frame = self._preview_service.get_latest_frame()
        if frame is None:
            self._preview_service.refresh_once()
            frame = self._preview_service.get_latest_frame()
        if frame is None:
            return None

        request = FocusRequest(method="laplace", roi=roi)
        result = self._focus_evaluator.evaluate(frame, request=request)
        overlay = build_focus_overlay_data(result, frame=frame, roi=roi)
        self._latest_focus_state = FocusPreviewState(result=result, overlay=overlay)
        return self._latest_focus_state

    def get_latest_focus_state(self) -> FocusPreviewState | None:
        return self._latest_focus_state
