from __future__ import annotations

from abc import ABC, abstractmethod

from vision_platform.libraries.common_models.focus_models import FocusResult, FocusRequest
from vision_platform.libraries.common_models.focus_models import FocusRequest
from vision_platform.libraries.common_models.frame_models import FrameData
from vision_platform.libraries.roi_core import roi_bounds
from vision_platform.models import CapturedFrame


class FocusEvaluator(ABC):
    """Stable focus-evaluation boundary for manual focus and later automation."""

    @abstractmethod
    def evaluate(self, frame: FrameData | CapturedFrame, request: FocusRequest | None = None) -> FocusResult:
        """Compute one focus score for the supplied frame."""


class LaplaceFocusEvaluator(FocusEvaluator):
    """Compute a manual-focus score using the variance of a discrete Laplacian."""

    def evaluate(self, frame: FrameData | CapturedFrame, request: FocusRequest | None = None) -> FocusResult:
        focus_request = request or FocusRequest(method="laplace")
        frame_data = _to_frame_data(frame)
        if not focus_score_available(frame_data, focus_request):
            return FocusResult(
                method="laplace",
                metric_name="laplace_variance",
                score=0.0,
                is_valid=False,
                roi_id=focus_request.roi.roi_id if focus_request.roi is not None else None,
                source_frame_id=frame_data.metadata.frame_id,
            )

        intensity_plane, dynamic_range = _decode_intensity_plane(
            data=frame_data.data or b"",
            width=frame_data.metadata.width or 0,
            height=frame_data.metadata.height or 0,
            pixel_format=frame_data.metadata.pixel_format,
        )
        bounded_plane = _apply_roi(
            intensity_plane,
            width=frame_data.metadata.width or 0,
            height=frame_data.metadata.height or 0,
            request=focus_request,
        )
        if bounded_plane is None or len(bounded_plane) < 3 or len(bounded_plane[0]) < 3:
            return FocusResult(
                method="laplace",
                metric_name="laplace_variance",
                score=0.0,
                is_valid=False,
                roi_id=focus_request.roi.roi_id if focus_request.roi is not None else None,
                source_frame_id=frame_data.metadata.frame_id,
            )

        score = _laplace_variance_score(
            bounded_plane,
            normalize=focus_request.normalize,
            dynamic_range=dynamic_range,
        )
        return FocusResult(
            method="laplace",
            metric_name="laplace_variance",
            score=score,
            is_valid=True,
            roi_id=focus_request.roi.roi_id if focus_request.roi is not None else None,
            source_frame_id=frame_data.metadata.frame_id,
        )


def evaluate_focus(frame: FrameData | CapturedFrame, request: FocusRequest | None = None) -> FocusResult:
    """Convenience entry point for the default manual-focus metric."""

    return LaplaceFocusEvaluator().evaluate(frame, request=request)


def focus_score_available(frame: FrameData | CapturedFrame, request: FocusRequest) -> bool:
    """Report whether a frame contains enough data for focus evaluation."""

    frame_data = _to_frame_data(frame)
    width = frame_data.metadata.width or 0
    height = frame_data.metadata.height or 0
    if frame_data.data is None or len(frame_data.data) == 0:
        return False
    if width < 3 or height < 3:
        return False
    if not bool(request.method):
        return False

    expected_min_size = width * height
    pixel_format = (frame_data.metadata.pixel_format or "Mono8").lower()
    if pixel_format == "mono16":
        expected_min_size *= 2
    elif pixel_format in {"rgb8", "bgr8"}:
        expected_min_size *= 3
    return len(frame_data.data) >= expected_min_size


def _to_frame_data(frame: FrameData | CapturedFrame) -> FrameData:
    if isinstance(frame, FrameData):
        return frame

    return frame.to_frame_data()


def _decode_intensity_plane(data: bytes, width: int, height: int, pixel_format: str | None) -> tuple[list[list[int]], int]:
    normalized_format = (pixel_format or "").lower()
    if not normalized_format:
        if len(data) == width * height:
            normalized_format = "mono8"
        elif len(data) == width * height * 2:
            normalized_format = "mono16"
        elif len(data) == width * height * 3:
            normalized_format = "rgb8"
        else:
            raise RuntimeError("Unable to infer pixel format for focus evaluation.")

    if normalized_format == "mono8":
        expected_size = width * height
        buffer = data[:expected_size]
        plane = [list(buffer[row_start : row_start + width]) for row_start in range(0, expected_size, width)]
        return plane, 255

    if normalized_format == "mono16":
        expected_size = width * height * 2
        buffer = data[:expected_size]
        values = [
            int.from_bytes(buffer[index : index + 2], byteorder="little")
            for index in range(0, expected_size, 2)
        ]
        plane = [values[row_start : row_start + width] for row_start in range(0, len(values), width)]
        return plane, 65535

    if normalized_format not in {"rgb8", "bgr8"}:
        raise RuntimeError(f"Unsupported focus-evaluation pixel format '{pixel_format}'.")

    expected_size = width * height * 3
    buffer = data[:expected_size]
    values: list[int] = []
    for index in range(0, expected_size, 3):
        first = buffer[index]
        second = buffer[index + 1]
        third = buffer[index + 2]
        if normalized_format == "rgb8":
            red, green, blue = first, second, third
        else:
            blue, green, red = first, second, third
        values.append((77 * red + 150 * green + 29 * blue) // 256)
    plane = [values[row_start : row_start + width] for row_start in range(0, len(values), width)]
    return plane, 255


def _apply_roi(plane: list[list[int]], width: int, height: int, request: FocusRequest) -> list[list[int]] | None:
    if request.roi is None:
        return plane

    bounds = roi_bounds(request.roi)
    if bounds is None:
        return None

    min_x, min_y, max_x, max_y = bounds
    left = max(0, int(min_x))
    top = max(0, int(min_y))
    right = min(width, int(max_x))
    bottom = min(height, int(max_y))
    if right - left < 3 or bottom - top < 3:
        return None

    return [row[left:right] for row in plane[top:bottom]]


def _laplace_variance_score(plane: list[list[int]], normalize: bool, dynamic_range: int) -> float:
    responses: list[float] = []
    for y in range(1, len(plane) - 1):
        previous_row = plane[y - 1]
        current_row = plane[y]
        next_row = plane[y + 1]
        for x in range(1, len(current_row) - 1):
            response = (
                previous_row[x]
                + next_row[x]
                + current_row[x - 1]
                + current_row[x + 1]
                - (4 * current_row[x])
            )
            responses.append(float(response))

    if not responses:
        return 0.0

    mean_response = sum(responses) / len(responses)
    variance = sum((response - mean_response) ** 2 for response in responses) / len(responses)
    if not normalize:
        return variance
    return variance / float(dynamic_range * dynamic_range)
