from __future__ import annotations

from vision_platform.libraries.common_models.focus_models import FocusRequest
from vision_platform.libraries.common_models.frame_models import FrameData


def focus_score_available(frame: FrameData, request: FocusRequest) -> bool:
    """Report whether a frame contains enough structure for focus evaluation wiring."""

    return frame.data is not None and len(frame.data) > 0 and bool(request.method)
