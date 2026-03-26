from __future__ import annotations

from vision_platform.libraries.common_models import FocusOverlayData, FocusResult, FrameData, FrameMetadata, RoiDefinition
from vision_platform.libraries.roi_core import roi_bounds, roi_centroid
from vision_platform.models import CapturedFrame


def build_focus_overlay_data(
    focus_result: FocusResult,
    frame: FrameData | FrameMetadata | CapturedFrame,
    roi: RoiDefinition | None = None,
) -> FocusOverlayData:
    """Build read-only overlay data without coupling the focus core to a specific UI."""

    metadata = _to_frame_metadata(frame)
    region_bounds = None
    anchor = _frame_center(metadata)
    if roi is not None and roi.enabled:
        region_bounds = roi_bounds(roi)
        centroid = roi_centroid(roi)
        if centroid is not None:
            anchor = centroid

    return FocusOverlayData(
        score=focus_result.score,
        metric_name=focus_result.metric_name or focus_result.method,
        anchor_x=anchor[0],
        anchor_y=anchor[1],
        is_valid=focus_result.is_valid,
        roi_id=focus_result.roi_id,
        source_frame_id=focus_result.source_frame_id,
        region_bounds=region_bounds,
    )


def _to_frame_metadata(frame: FrameData | FrameMetadata | CapturedFrame) -> FrameMetadata:
    if isinstance(frame, FrameMetadata):
        return frame
    if isinstance(frame, FrameData):
        return frame.metadata
    return frame.to_frame_data().metadata


def _frame_center(metadata: FrameMetadata) -> tuple[float, float]:
    width = float(metadata.width or 0)
    height = float(metadata.height or 0)
    return width / 2.0, height / 2.0
