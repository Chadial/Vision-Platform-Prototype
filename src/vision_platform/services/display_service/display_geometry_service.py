from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ViewportMapping:
    source_width: int
    source_height: int
    viewport_width: int
    viewport_height: int
    display_scale: float
    scaled_width: int
    scaled_height: int
    src_x: int
    src_y: int
    dst_x: int
    dst_y: int
    copy_width: int
    copy_height: int


@dataclass(slots=True)
class ZoomPanState:
    fit_to_window: bool = True
    manual_zoom_scale: float | None = None
    viewport_origin_scaled: tuple[int, int] = (0, 0)
    pan_anchor_viewport_point: tuple[int, int] | None = None
    pan_anchor_origin_scaled: tuple[int, int] | None = None


class DisplayGeometryService:
    """Owns viewport math without depending on a concrete UI toolkit."""

    def resolve_display_scale(
        self,
        frame_width: int,
        frame_height: int,
        viewport_width: int,
        viewport_height: int,
        state: ZoomPanState,
        *,
        min_zoom_scale: float,
    ) -> float:
        if state.fit_to_window:
            return max(min(viewport_width / frame_width, viewport_height / frame_height), min_zoom_scale)

        assert state.manual_zoom_scale is not None
        return state.manual_zoom_scale

    def resolve_viewport_origin(
        self,
        frame_width: int,
        frame_height: int,
        viewport_width: int,
        viewport_height: int,
        display_scale: float,
        state: ZoomPanState,
    ) -> tuple[int, int]:
        if state.fit_to_window:
            state.viewport_origin_scaled = (0, 0)
            return state.viewport_origin_scaled

        scaled_width = max(1, int(round(frame_width * display_scale)))
        scaled_height = max(1, int(round(frame_height * display_scale)))
        max_src_x = max(0, scaled_width - viewport_width)
        max_src_y = max(0, scaled_height - viewport_height)
        origin_x = min(max(0, state.viewport_origin_scaled[0]), max_src_x)
        origin_y = min(max(0, state.viewport_origin_scaled[1]), max_src_y)
        state.viewport_origin_scaled = (origin_x, origin_y)
        return state.viewport_origin_scaled

    def build_viewport_mapping(
        self,
        frame_width: int,
        frame_height: int,
        viewport_width: int,
        viewport_height: int,
        display_scale: float,
        src_x: int = 0,
        src_y: int = 0,
    ) -> ViewportMapping:
        scaled_width = max(1, int(round(frame_width * display_scale)))
        scaled_height = max(1, int(round(frame_height * display_scale)))
        max_src_x = max(0, scaled_width - viewport_width)
        max_src_y = max(0, scaled_height - viewport_height)
        src_x = min(max(0, src_x), max_src_x)
        src_y = min(max(0, src_y), max_src_y)
        dst_x = 0
        dst_y = 0
        copy_width = min(scaled_width - src_x, viewport_width)
        copy_height = min(scaled_height - src_y, viewport_height)
        return ViewportMapping(
            source_width=frame_width,
            source_height=frame_height,
            viewport_width=viewport_width,
            viewport_height=viewport_height,
            display_scale=display_scale,
            scaled_width=scaled_width,
            scaled_height=scaled_height,
            src_x=src_x,
            src_y=src_y,
            dst_x=dst_x,
            dst_y=dst_y,
            copy_width=copy_width,
            copy_height=copy_height,
        )

    def map_viewport_point_to_source(self, mapping: ViewportMapping | None, x: int, y: int) -> tuple[int, int] | None:
        if mapping is None:
            return None
        if not (
            mapping.dst_x <= x < mapping.dst_x + mapping.copy_width
            and mapping.dst_y <= y < mapping.dst_y + mapping.copy_height
        ):
            return None

        scaled_x = mapping.src_x + (x - mapping.dst_x)
        scaled_y = mapping.src_y + (y - mapping.dst_y)
        source_x = int(scaled_x / mapping.display_scale)
        source_y = int(scaled_y / mapping.display_scale)
        source_x = min(max(source_x, 0), mapping.source_width - 1)
        source_y = min(max(source_y, 0), mapping.source_height - 1)
        return source_x, source_y

    def map_source_point_to_viewport(
        self,
        mapping: ViewportMapping | None,
        point: tuple[int, int] | None,
    ) -> tuple[int, int] | None:
        if mapping is None or point is None:
            return None

        scaled_x = int(round(point[0] * mapping.display_scale))
        scaled_y = int(round(point[1] * mapping.display_scale))
        viewport_x = mapping.dst_x + scaled_x - mapping.src_x
        viewport_y = mapping.dst_y + scaled_y - mapping.src_y
        if not (
            mapping.dst_x <= viewport_x < mapping.dst_x + mapping.copy_width
            and mapping.dst_y <= viewport_y < mapping.dst_y + mapping.copy_height
        ):
            return None
        return viewport_x, viewport_y

    def build_cursor_anchored_origin(
        self,
        mapping: ViewportMapping | None,
        cursor_viewport_point: tuple[int, int] | None,
        new_scale: float,
    ) -> tuple[int, int] | None:
        if mapping is None or cursor_viewport_point is None:
            return None

        cursor_source_point = self.map_viewport_point_to_source(
            mapping,
            cursor_viewport_point[0],
            cursor_viewport_point[1],
        )
        if cursor_source_point is None:
            return None

        return (
            int(round(cursor_source_point[0] * new_scale - cursor_viewport_point[0])),
            int(round(cursor_source_point[1] * new_scale - cursor_viewport_point[1])),
        )


__all__ = ["DisplayGeometryService", "ViewportMapping", "ZoomPanState"]
