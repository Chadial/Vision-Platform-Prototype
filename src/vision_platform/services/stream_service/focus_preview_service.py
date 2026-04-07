from __future__ import annotations

from dataclasses import replace

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
        max_frame_dimension: int | None = None,
    ) -> None:
        self._preview_service = preview_service
        self._focus_evaluator = focus_evaluator or create_focus_evaluator(focus_method or "laplace")
        self._focus_method: FocusMethod = focus_method or _infer_focus_method(self._focus_evaluator)
        self._roi_state_service = roi_state_service
        self._latest_focus_state: FocusPreviewState | None = None
        self._max_frame_dimension = max_frame_dimension

    def refresh_once(self, roi: RoiDefinition | None = None) -> FocusPreviewState | None:
        frame = self._preview_service.get_latest_frame()
        if frame is None:
            self._preview_service.refresh_once()
            frame = self._preview_service.get_latest_frame()
        if frame is None:
            return None
        return self.refresh_from_frame(frame, roi=roi)

    def refresh_from_frame(
        self,
        frame,
        roi: RoiDefinition | None = None,
    ) -> FocusPreviewState | None:
        active_roi = self._resolve_active_roi(roi)
        evaluation_frame, evaluation_roi = _prepare_focus_inputs(
            frame,
            active_roi,
            max_frame_dimension=self._max_frame_dimension,
        )
        request = FocusRequest(method=self._focus_method, roi=evaluation_roi)
        result = self._focus_evaluator.evaluate(evaluation_frame, request=request)
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


def _prepare_focus_inputs(
    frame,
    roi: RoiDefinition | None,
    *,
    max_frame_dimension: int | None,
):
    if max_frame_dimension is None or max_frame_dimension <= 0:
        return frame, roi
    largest_dimension = max(frame.width, frame.height)
    if largest_dimension <= max_frame_dimension:
        return frame, roi

    scale = max_frame_dimension / float(largest_dimension)
    scaled_width = max(1, int(round(frame.width * scale)))
    scaled_height = max(1, int(round(frame.height * scale)))
    if scaled_width >= frame.width and scaled_height >= frame.height:
        return frame, roi

    scaled_frame = _resize_captured_frame_nearest(frame, scaled_width=scaled_width, scaled_height=scaled_height)
    scaled_roi = _scale_roi_definition(roi, scale=scale)
    return scaled_frame, scaled_roi


def _resize_captured_frame_nearest(frame, *, scaled_width: int, scaled_height: int):
    source_bytes = frame.get_buffer_bytes()
    pixel_format = (frame.pixel_format or "Mono8").lower()
    channel_count = _channel_count_for_focus(pixel_format)
    source_x = [min(int(index * frame.width / scaled_width), frame.width - 1) for index in range(scaled_width)]
    source_y = [min(int(index * frame.height / scaled_height), frame.height - 1) for index in range(scaled_height)]
    resized = bytearray(scaled_width * scaled_height * channel_count)

    for target_y, original_y in enumerate(source_y):
        for target_x, original_x in enumerate(source_x):
            source_index = (original_y * frame.width + original_x) * channel_count
            target_index = (target_y * scaled_width + target_x) * channel_count
            resized[target_index : target_index + channel_count] = source_bytes[source_index : source_index + channel_count]

    return replace(
        frame,
        raw_frame=bytes(resized),
        width=scaled_width,
        height=scaled_height,
    )


def _channel_count_for_focus(pixel_format: str) -> int:
    if pixel_format == "mono16":
        return 2
    if pixel_format in {"rgb8", "bgr8"}:
        return 3
    return 1


def _scale_roi_definition(roi: RoiDefinition | None, *, scale: float) -> RoiDefinition | None:
    if roi is None:
        return None
    return RoiDefinition(
        roi_id=roi.roi_id,
        shape=roi.shape,
        points=tuple((point[0] * scale, point[1] * scale) for point in roi.points),
        label=roi.label,
        enabled=roi.enabled,
        metadata=dict(roi.metadata),
    )
