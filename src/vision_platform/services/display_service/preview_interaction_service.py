from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Literal

from vision_platform.libraries.common_models import RoiDefinition
from vision_platform.services.display_service.display_geometry_service import DisplayGeometryService, ZoomPanState

PreviewInteractionAction = Literal[
    "cursor_moved",
    "zoom_in",
    "zoom_out",
    "enable_fit",
    "toggle_crosshair",
    "toggle_focus",
    "toggle_roi_mode",
    "request_snapshot",
    "request_copy",
    "start_pan",
    "stop_pan",
    "update_pan",
    "wheel_zoom",
    "select_source_point",
]


@dataclass(slots=True)
class PreviewInteractionState:
    selected_point: tuple[int, int] | None = None
    last_status_message: str | None = None
    crosshair_visible: bool = True
    focus_status_visible: bool = True
    roi_mode: str | None = None
    roi_anchor_point: tuple[int, int] | None = None
    roi_preview_point: tuple[int, int] | None = None
    last_cursor_viewport_point: tuple[int, int] | None = None
    last_cursor_source_point: tuple[int, int] | None = None
    hovered_anchor_id: str | None = None
    active_anchor_drag_id: str | None = None


@dataclass(frozen=True, slots=True)
class PreviewInteractionCommand:
    action: PreviewInteractionAction
    viewport_point: tuple[int, int] | None = None
    source_point: tuple[int, int] | None = None
    wheel_delta: int = 0
    roi_mode: str | None = None


@dataclass(frozen=True, slots=True)
class PreviewInteractionOutcome:
    handled: bool = True
    snapshot_requested: bool = False
    copy_text: str | None = None
    copy_success_message: str | None = None
    committed_roi: RoiDefinition | None = None


class PreviewInteractionService:
    """Applies reusable preview interaction semantics independently of a concrete UI toolkit."""

    def __init__(self, geometry_service: DisplayGeometryService | None = None) -> None:
        self._geometry_service = geometry_service or DisplayGeometryService()

    def apply_command(
        self,
        command: PreviewInteractionCommand,
        interaction_state: PreviewInteractionState,
        geometry_state: ZoomPanState,
        *,
        last_display_scale: float,
        last_viewport_mapping,
        zoom_step: float,
        min_zoom_scale: float,
        max_zoom_scale: float,
        has_focus_provider: bool,
        has_snapshot_callback: bool,
        coordinate_formatter: Callable[[int, int], str],
        roi_builder: Callable[[str | None, tuple[int, int], tuple[int, int]], RoiDefinition],
    ) -> PreviewInteractionOutcome:
        action = command.action

        if action == "cursor_moved":
            interaction_state.last_cursor_viewport_point = command.viewport_point
            interaction_state.last_cursor_source_point = command.source_point
            return PreviewInteractionOutcome()

        if action == "zoom_in":
            self._apply_zoom(
                interaction_state,
                geometry_state,
                last_display_scale=last_display_scale,
                last_viewport_mapping=last_viewport_mapping,
                zoom_step=zoom_step,
                min_zoom_scale=min_zoom_scale,
                max_zoom_scale=max_zoom_scale,
                direction=1,
            )
            return PreviewInteractionOutcome()

        if action == "zoom_out":
            self._apply_zoom(
                interaction_state,
                geometry_state,
                last_display_scale=last_display_scale,
                last_viewport_mapping=last_viewport_mapping,
                zoom_step=zoom_step,
                min_zoom_scale=min_zoom_scale,
                max_zoom_scale=max_zoom_scale,
                direction=-1,
            )
            return PreviewInteractionOutcome()

        if action == "enable_fit":
            geometry_state.fit_to_window = True
            geometry_state.manual_zoom_scale = None
            geometry_state.viewport_origin_scaled = (0, 0)
            geometry_state.pan_anchor_viewport_point = None
            geometry_state.pan_anchor_origin_scaled = None
            return PreviewInteractionOutcome()

        if action == "toggle_crosshair":
            interaction_state.crosshair_visible = not interaction_state.crosshair_visible
            interaction_state.last_status_message = (
                "Crosshair shown" if interaction_state.crosshair_visible else "Crosshair hidden"
            )
            return PreviewInteractionOutcome()

        if action == "toggle_focus":
            if not has_focus_provider:
                interaction_state.last_status_message = "Focus display unavailable"
                return PreviewInteractionOutcome()
            interaction_state.focus_status_visible = not interaction_state.focus_status_visible
            interaction_state.last_status_message = (
                "Focus shown" if interaction_state.focus_status_visible else "Focus hidden"
            )
            return PreviewInteractionOutcome()

        if action == "toggle_roi_mode":
            roi_mode = command.roi_mode
            if interaction_state.roi_mode == roi_mode:
                interaction_state.roi_mode = None
                interaction_state.roi_anchor_point = None
                interaction_state.roi_preview_point = None
                interaction_state.last_status_message = "ROI mode cleared"
                return PreviewInteractionOutcome()
            interaction_state.roi_mode = roi_mode
            interaction_state.roi_anchor_point = None
            interaction_state.roi_preview_point = None
            interaction_state.last_status_message = f"ROI mode set to {roi_mode}"
            return PreviewInteractionOutcome()

        if action == "request_snapshot":
            if not has_snapshot_callback:
                interaction_state.last_status_message = "Snapshot shortcut unavailable"
                return PreviewInteractionOutcome()
            return PreviewInteractionOutcome(snapshot_requested=True)

        if action == "request_copy":
            if interaction_state.selected_point is None:
                interaction_state.last_status_message = "No point selected"
                return PreviewInteractionOutcome()
            copy_text = coordinate_formatter(*interaction_state.selected_point)
            return PreviewInteractionOutcome(
                copy_text=copy_text,
                copy_success_message="Point copied",
            )

        if action == "start_pan":
            if geometry_state.fit_to_window:
                interaction_state.last_status_message = "Pan unavailable in fit mode"
                geometry_state.pan_anchor_viewport_point = None
                geometry_state.pan_anchor_origin_scaled = None
                return PreviewInteractionOutcome()
            geometry_state.pan_anchor_viewport_point = command.viewport_point
            geometry_state.pan_anchor_origin_scaled = geometry_state.viewport_origin_scaled
            interaction_state.last_status_message = "Panning"
            return PreviewInteractionOutcome()

        if action == "stop_pan":
            if geometry_state.pan_anchor_viewport_point is None:
                return PreviewInteractionOutcome(handled=False)
            geometry_state.pan_anchor_viewport_point = None
            geometry_state.pan_anchor_origin_scaled = None
            interaction_state.last_status_message = "Pan complete"
            return PreviewInteractionOutcome()

        if action == "update_pan":
            if geometry_state.pan_anchor_viewport_point is None or geometry_state.pan_anchor_origin_scaled is None:
                return PreviewInteractionOutcome(handled=False)
            assert command.viewport_point is not None
            delta_x = command.viewport_point[0] - geometry_state.pan_anchor_viewport_point[0]
            delta_y = command.viewport_point[1] - geometry_state.pan_anchor_viewport_point[1]
            geometry_state.viewport_origin_scaled = (
                geometry_state.pan_anchor_origin_scaled[0] - delta_x,
                geometry_state.pan_anchor_origin_scaled[1] - delta_y,
            )
            interaction_state.last_status_message = "Panning"
            return PreviewInteractionOutcome()

        if action == "wheel_zoom":
            if command.wheel_delta == 0:
                return PreviewInteractionOutcome()
            if command.source_point is None:
                interaction_state.last_status_message = "Wheel zoom ignored outside image"
                return PreviewInteractionOutcome()
            self._apply_zoom(
                interaction_state,
                geometry_state,
                last_display_scale=last_display_scale,
                last_viewport_mapping=last_viewport_mapping,
                zoom_step=zoom_step,
                min_zoom_scale=min_zoom_scale,
                max_zoom_scale=max_zoom_scale,
                direction=1 if command.wheel_delta > 0 else -1,
            )
            return PreviewInteractionOutcome()

        if action == "select_source_point":
            if command.source_point is None:
                return PreviewInteractionOutcome(handled=False)
            if interaction_state.roi_mode is not None:
                return self._apply_roi_selection(
                    interaction_state,
                    command.source_point,
                    coordinate_formatter=coordinate_formatter,
                    roi_builder=roi_builder,
                )
            interaction_state.selected_point = command.source_point
            interaction_state.last_status_message = "Point selected"
            return PreviewInteractionOutcome()

        raise ValueError(f"Unsupported preview interaction action '{action}'.")

    def _apply_zoom(
        self,
        interaction_state: PreviewInteractionState,
        geometry_state: ZoomPanState,
        *,
        last_display_scale: float,
        last_viewport_mapping,
        zoom_step: float,
        min_zoom_scale: float,
        max_zoom_scale: float,
        direction: int,
    ) -> None:
        base_scale = (
            last_display_scale if geometry_state.fit_to_window or geometry_state.manual_zoom_scale is None else geometry_state.manual_zoom_scale
        )
        if direction > 0:
            new_scale = min(base_scale * zoom_step, max_zoom_scale)
        else:
            new_scale = max(base_scale / zoom_step, min_zoom_scale)

        geometry_state.manual_zoom_scale = new_scale
        if last_viewport_mapping is not None:
            anchored_origin = self._geometry_service.build_cursor_anchored_origin(
                last_viewport_mapping,
                interaction_state.last_cursor_viewport_point,
                new_scale,
            )
            if anchored_origin is not None:
                geometry_state.viewport_origin_scaled = anchored_origin
            else:
                top_left_source_x = last_viewport_mapping.src_x / max(base_scale, 1e-9)
                top_left_source_y = last_viewport_mapping.src_y / max(base_scale, 1e-9)
                geometry_state.viewport_origin_scaled = (
                    int(round(top_left_source_x * new_scale)),
                    int(round(top_left_source_y * new_scale)),
                )
        geometry_state.fit_to_window = False

    def _apply_roi_selection(
        self,
        interaction_state: PreviewInteractionState,
        source_point: tuple[int, int],
        *,
        coordinate_formatter: Callable[[int, int], str],
        roi_builder: Callable[[str | None, tuple[int, int], tuple[int, int]], RoiDefinition],
    ) -> PreviewInteractionOutcome:
        if interaction_state.roi_anchor_point is None:
            interaction_state.roi_anchor_point = source_point
            interaction_state.roi_preview_point = None
            interaction_state.last_status_message = f"ROI anchor set to {coordinate_formatter(*source_point)}"
            return PreviewInteractionOutcome()

        roi = roi_builder(interaction_state.roi_mode, interaction_state.roi_anchor_point, source_point)
        interaction_state.roi_anchor_point = None
        interaction_state.roi_preview_point = None
        interaction_state.last_status_message = f"ROI saved as {roi.shape}"
        return PreviewInteractionOutcome(committed_roi=roi)


__all__ = [
    "PreviewInteractionAction",
    "PreviewInteractionCommand",
    "PreviewInteractionOutcome",
    "PreviewInteractionService",
    "PreviewInteractionState",
]
