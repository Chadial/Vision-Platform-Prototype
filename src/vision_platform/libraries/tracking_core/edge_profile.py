from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from vision_platform.libraries.common_models import FrameData, RoiDefinition
from vision_platform.libraries.roi_core import roi_mask
from vision_platform.models import CapturedFrame


EdgeOrientation = Literal["horizontal", "vertical"]


@dataclass(slots=True)
class EdgeProfileRequest:
    """Portable request for one directional edge-profile analysis pass."""

    orientation: EdgeOrientation = "vertical"
    roi: RoiDefinition | None = None
    normalize: bool = True


@dataclass(slots=True)
class EdgeProfileResult:
    """Portable edge-profile result for later overlay, drift, or postprocess consumers."""

    orientation: EdgeOrientation
    profile: tuple[float, ...]
    gradient_profile: tuple[float, ...]
    dominant_edge_index: int | None
    dominant_edge_position: float | None
    dominant_edge_strength: float
    is_valid: bool = True
    roi_id: str | None = None
    source_frame_id: int | None = None


def analyze_edge_profile(
    frame: FrameData | CapturedFrame,
    request: EdgeProfileRequest | None = None,
) -> EdgeProfileResult:
    """Analyze one horizontal or vertical intensity profile and report the dominant edge transition."""

    edge_request = request or EdgeProfileRequest()
    frame_data = _to_frame_data(frame)
    width = frame_data.metadata.width or 0
    height = frame_data.metadata.height or 0
    if frame_data.data is None or width <= 0 or height <= 0:
        return _invalid_result(edge_request, source_frame_id=frame_data.metadata.frame_id)

    plane, dynamic_range = _decode_intensity_plane(
        data=frame_data.data,
        width=width,
        height=height,
        pixel_format=frame_data.metadata.pixel_format,
    )
    bounded_plane, mask, bounds = _apply_roi(
        plane=plane,
        width=width,
        height=height,
        roi=edge_request.roi,
    )
    if bounded_plane is None or not bounded_plane or not bounded_plane[0]:
        return _invalid_result(
            edge_request,
            source_frame_id=frame_data.metadata.frame_id,
        )

    profile = _build_profile(
        bounded_plane=bounded_plane,
        mask=mask,
        orientation=edge_request.orientation,
        normalize=edge_request.normalize,
        dynamic_range=dynamic_range,
    )
    if len(profile) < 2:
        return _invalid_result(
            edge_request,
            source_frame_id=frame_data.metadata.frame_id,
        )

    gradient_profile = tuple(profile[index + 1] - profile[index] for index in range(len(profile) - 1))
    if not gradient_profile:
        return _invalid_result(
            edge_request,
            source_frame_id=frame_data.metadata.frame_id,
        )

    dominant_gradient_index = max(range(len(gradient_profile)), key=lambda index: abs(gradient_profile[index]))
    dominant_strength = gradient_profile[dominant_gradient_index]
    bound_offset = bounds[0] if edge_request.orientation == "vertical" else bounds[1]
    dominant_position = float(bound_offset + dominant_gradient_index) + 0.5
    return EdgeProfileResult(
        orientation=edge_request.orientation,
        profile=profile,
        gradient_profile=gradient_profile,
        dominant_edge_index=bound_offset + dominant_gradient_index,
        dominant_edge_position=dominant_position,
        dominant_edge_strength=dominant_strength,
        is_valid=True,
        roi_id=edge_request.roi.roi_id if edge_request.roi is not None else None,
        source_frame_id=frame_data.metadata.frame_id,
    )


def _invalid_result(request: EdgeProfileRequest, source_frame_id: int | None) -> EdgeProfileResult:
    return EdgeProfileResult(
        orientation=request.orientation,
        profile=(),
        gradient_profile=(),
        dominant_edge_index=None,
        dominant_edge_position=None,
        dominant_edge_strength=0.0,
        is_valid=False,
        roi_id=request.roi.roi_id if request.roi is not None else None,
        source_frame_id=source_frame_id,
    )


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
            raise RuntimeError("Unable to infer pixel format for edge-profile analysis.")

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
        raise RuntimeError(f"Unsupported edge-profile pixel format '{pixel_format}'.")

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
    roi: RoiDefinition | None,
) -> tuple[list[list[int]] | None, list[list[bool]], tuple[int, int, int, int]]:
    if roi is None or not roi.enabled:
        full_mask = [[True for _ in range(width)] for _ in range(height)]
        return plane, full_mask, (0, 0, width, height)

    masked_roi = roi_mask(roi, width=width, height=height)
    if masked_roi is None:
        return None, [], (0, 0, 0, 0)

    (left, top, right, bottom), mask = masked_roi
    bounded_plane = [row[left:right] for row in plane[top:bottom]]
    return bounded_plane, mask, (left, top, right, bottom)


def _build_profile(
    *,
    bounded_plane: list[list[int]],
    mask: list[list[bool]],
    orientation: EdgeOrientation,
    normalize: bool,
    dynamic_range: int,
) -> tuple[float, ...]:
    if orientation == "vertical":
        profile_values = _average_columns(bounded_plane, mask)
    else:
        profile_values = _average_rows(bounded_plane, mask)
    if not normalize:
        return profile_values
    return tuple(value / float(dynamic_range) for value in profile_values)


def _average_columns(plane: list[list[int]], mask: list[list[bool]]) -> tuple[float, ...]:
    column_values: list[float] = []
    width = len(plane[0])
    height = len(plane)
    for x in range(width):
        total = 0.0
        sample_count = 0
        for y in range(height):
            if not mask[y][x]:
                continue
            total += plane[y][x]
            sample_count += 1
        column_values.append(total / sample_count if sample_count > 0 else 0.0)
    return tuple(column_values)


def _average_rows(plane: list[list[int]], mask: list[list[bool]]) -> tuple[float, ...]:
    row_values: list[float] = []
    for y, row in enumerate(plane):
        total = 0.0
        sample_count = 0
        for x, value in enumerate(row):
            if not mask[y][x]:
                continue
            total += value
            sample_count += 1
        row_values.append(total / sample_count if sample_count > 0 else 0.0)
    return tuple(row_values)
