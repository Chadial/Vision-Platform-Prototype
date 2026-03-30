from __future__ import annotations

from collections import deque
from math import sqrt

from vision_platform.libraries.common_models import FocusMethod, FocusRequest, RoiDefinition
from vision_platform.libraries.focus_core import FocusEvaluator, create_focus_evaluator
from vision_platform.models import CapturedFrame
from vision_platform.services.recording_service.traceability import TraceArtifactMetadata, build_trace_artifact_metadata
from vision_platform.services.stream_service.roi_state_service import RoiStateService


class ArtifactFocusMetadataProducer:
    """Build optional artifact-level focus metadata from saved frames."""

    def __init__(
        self,
        *,
        focus_method: FocusMethod = "laplace",
        focus_score_frame_interval: int | None = None,
        focus_evaluator: FocusEvaluator | None = None,
        roi_state_service: RoiStateService | None = None,
    ) -> None:
        if focus_score_frame_interval is not None and focus_score_frame_interval <= 0:
            raise ValueError("focus_score_frame_interval must be greater than zero when provided.")

        self._focus_method: FocusMethod = focus_method
        self._focus_evaluator = focus_evaluator or create_focus_evaluator(focus_method)
        self._focus_score_frame_interval = focus_score_frame_interval
        self._roi_state_service = roi_state_service
        self._recent_scores: deque[float] = deque(maxlen=focus_score_frame_interval or 1)

    def reset(self) -> None:
        self._recent_scores.clear()

    def build_metadata(
        self,
        frame: CapturedFrame,
        *,
        roi: RoiDefinition | None = None,
    ) -> TraceArtifactMetadata:
        active_roi = self._resolve_active_roi(roi)
        result = self._focus_evaluator.evaluate(
            frame,
            request=FocusRequest(method=self._focus_method, roi=active_roi),
        )

        if self._focus_score_frame_interval is None:
            return build_trace_artifact_metadata(
                analysis_roi=active_roi,
                focus_method=result.method,
                focus_roi=active_roi,
            )

        self._recent_scores.append(result.score)
        mean_score = sum(self._recent_scores) / len(self._recent_scores)
        variance = sum((score - mean_score) ** 2 for score in self._recent_scores) / len(self._recent_scores)
        return build_trace_artifact_metadata(
            analysis_roi=active_roi,
            focus_method=result.method,
            focus_score_frame_interval=self._focus_score_frame_interval,
            focus_value_mean=mean_score,
            focus_value_stddev=sqrt(variance),
            focus_roi=active_roi,
        )

    def _resolve_active_roi(self, explicit_roi: RoiDefinition | None) -> RoiDefinition | None:
        if self._roi_state_service is None:
            return explicit_roi
        return self._roi_state_service.resolve_active_roi(explicit_roi)


__all__ = ["ArtifactFocusMetadataProducer"]
