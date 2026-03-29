from __future__ import annotations

from abc import ABC, abstractmethod

from vision_platform.libraries.common_models.focus_models import FocusRequest, FocusResult
from vision_platform.libraries.common_models.frame_models import FrameData
from vision_platform.libraries.roi_core import roi_mask
from vision_platform.models import CapturedFrame


class FocusEvaluator(ABC):
    """Stable focus-evaluation boundary for manual focus and later automation."""

    @abstractmethod
    def evaluate(self, frame: FrameData | CapturedFrame, request: FocusRequest | None = None) -> FocusResult:
        """Compute one focus score for the supplied frame."""


def create_focus_evaluator(method: str) -> FocusEvaluator:
    """Create the evaluator that matches one portable focus-method name."""

    normalized_method = method.strip().lower()
    if normalized_method == "laplace":
        return LaplaceFocusEvaluator()
    if normalized_method == "tenengrad":
        return TenengradFocusEvaluator()
    raise ValueError(f"Unsupported focus method '{method}'.")


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
        bounded_plane, mask = _apply_roi(
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
            mask=mask,
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


class TenengradFocusEvaluator(FocusEvaluator):
    """Compute a manual-focus score using mean squared Sobel gradient magnitude."""

    def evaluate(self, frame: FrameData | CapturedFrame, request: FocusRequest | None = None) -> FocusResult:
        focus_request = request or FocusRequest(method="tenengrad")
        frame_data = _to_frame_data(frame)
        if not focus_score_available(frame_data, focus_request):
            return FocusResult(
                method="tenengrad",
                metric_name="tenengrad_mean_gradient_energy",
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
        bounded_plane, mask = _apply_roi(
            intensity_plane,
            width=frame_data.metadata.width or 0,
            height=frame_data.metadata.height or 0,
            request=focus_request,
        )
        if bounded_plane is None or len(bounded_plane) < 3 or len(bounded_plane[0]) < 3:
            return FocusResult(
                method="tenengrad",
                metric_name="tenengrad_mean_gradient_energy",
                score=0.0,
                is_valid=False,
                roi_id=focus_request.roi.roi_id if focus_request.roi is not None else None,
                source_frame_id=frame_data.metadata.frame_id,
            )

        score = _tenengrad_score(
            bounded_plane,
            mask=mask,
            normalize=focus_request.normalize,
            dynamic_range=dynamic_range,
        )
        return FocusResult(
            method="tenengrad",
            metric_name="tenengrad_mean_gradient_energy",
            score=score,
            is_valid=True,
            roi_id=focus_request.roi.roi_id if focus_request.roi is not None else None,
            source_frame_id=frame_data.metadata.frame_id,
        )


def evaluate_focus(frame: FrameData | CapturedFrame, request: FocusRequest | None = None) -> FocusResult:
    """Convenience entry point for the default manual-focus metric."""

    focus_request = request or FocusRequest(method="laplace")
    return create_focus_evaluator(focus_request.method).evaluate(frame, request=focus_request)


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


def _apply_roi(
    plane: list[list[int]],
    width: int,
    height: int,
    request: FocusRequest,
) -> tuple[list[list[int]] | None, list[list[bool]] | None]:
    if request.roi is None or not request.roi.enabled:
        return plane, None

    masked_roi = roi_mask(request.roi, width=width, height=height)
    if masked_roi is None:
        return None, None

    (left, top, right, bottom), mask = masked_roi
    if right - left < 3 or bottom - top < 3:
        return None, None

    return [row[left:right] for row in plane[top:bottom]], mask


def _laplace_variance_score(
    plane: list[list[int]],
    mask: list[list[bool]] | None,
    normalize: bool,
    dynamic_range: int,
) -> float:
    responses: list[float] = []
    for y in range(1, len(plane) - 1):
        previous_row = plane[y - 1]
        current_row = plane[y]
        next_row = plane[y + 1]
        for x in range(1, len(current_row) - 1):
            if mask is not None and not _laplace_kernel_is_inside_mask(mask, x=x, y=y):
                continue
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


def _laplace_kernel_is_inside_mask(mask: list[list[bool]], x: int, y: int) -> bool:
    return (
        mask[y][x]
        and mask[y - 1][x]
        and mask[y + 1][x]
        and mask[y][x - 1]
        and mask[y][x + 1]
    )


def _tenengrad_score(
    plane: list[list[int]],
    mask: list[list[bool]] | None,
    normalize: bool,
    dynamic_range: int,
) -> float:
    gradient_energies: list[float] = []
    for y in range(1, len(plane) - 1):
        previous_row = plane[y - 1]
        current_row = plane[y]
        next_row = plane[y + 1]
        for x in range(1, len(current_row) - 1):
            if mask is not None and not _sobel_kernel_is_inside_mask(mask, x=x, y=y):
                continue
            gradient_x = (
                -previous_row[x - 1]
                + previous_row[x + 1]
                - (2 * current_row[x - 1])
                + (2 * current_row[x + 1])
                - next_row[x - 1]
                + next_row[x + 1]
            )
            gradient_y = (
                previous_row[x - 1]
                + (2 * previous_row[x])
                + previous_row[x + 1]
                - next_row[x - 1]
                - (2 * next_row[x])
                - next_row[x + 1]
            )
            gradient_energies.append(float(gradient_x * gradient_x + gradient_y * gradient_y))

    if not gradient_energies:
        return 0.0

    mean_energy = sum(gradient_energies) / len(gradient_energies)
    if not normalize:
        return mean_energy
    return mean_energy / float(dynamic_range * dynamic_range)


def _sobel_kernel_is_inside_mask(mask: list[list[bool]], x: int, y: int) -> bool:
    return (
        mask[y - 1][x - 1]
        and mask[y - 1][x]
        and mask[y - 1][x + 1]
        and mask[y][x - 1]
        and mask[y][x]
        and mask[y][x + 1]
        and mask[y + 1][x - 1]
        and mask[y + 1][x]
        and mask[y + 1][x + 1]
    )
