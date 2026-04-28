from __future__ import annotations

from dataclasses import dataclass, field

from vision_platform.libraries.roi_core import roi_bounds
from vision_platform.libraries.common_models import FocusPreviewState, RoiDefinition
from vision_platform.models import CapturedFrame
from vision_platform.services.display_service.viewport_rendering_service import (
    RenderedViewportImage,
    render_viewport_image,
)
from vision_platform.services.display_service import (
    CoordinateExportService,
    DisplayGeometryService,
    PreviewAnchorHandle,
    PreviewInteractionCommand,
    PreviewInteractionOutcome,
    PreviewInteractionService,
    PreviewInteractionState,
    PreviewOverlayModel,
    PreviewStatusModelService,
    ViewportMapping,
    ZoomPanState,
    format_focus_score,
)
from vision_platform.services.stream_service import RoiStateService


@dataclass(frozen=True, slots=True)
class PreviewShellViewModel:
    image: RenderedViewportImage
    overlay_model: PreviewOverlayModel
    status_lines: list[str]
    viewport_mapping: ViewportMapping


@dataclass(slots=True)
class PreviewShellState:
    geometry_state: ZoomPanState = field(default_factory=ZoomPanState)
    interaction_state: PreviewInteractionState = field(default_factory=PreviewInteractionState)
    last_display_scale: float = 1.0
    last_viewport_mapping: ViewportMapping | None = None


class PreviewShellPresenter:
    """UI-agnostic preview-shell adapter over shared geometry, interaction, and status services."""

    def __init__(
        self,
        *,
        coordinate_export_service: CoordinateExportService | None = None,
        geometry_service: DisplayGeometryService | None = None,
        interaction_service: PreviewInteractionService | None = None,
        status_model_service: PreviewStatusModelService | None = None,
        roi_state_service: RoiStateService | None = None,
        zoom_step: float = 2.0,
        min_zoom_scale: float = 0.25,
        max_zoom_scale: float = 4.0,
    ) -> None:
        self._coordinate_export_service = coordinate_export_service or CoordinateExportService()
        self._geometry_service = geometry_service or DisplayGeometryService()
        self._roi_state_service = roi_state_service or RoiStateService()
        self._interaction_service = interaction_service or PreviewInteractionService(
            self._geometry_service,
            self._roi_state_service,
        )
        self._status_model_service = status_model_service or PreviewStatusModelService()
        self._zoom_step = zoom_step
        self._min_zoom_scale = min_zoom_scale
        self._max_zoom_scale = max_zoom_scale
        self._anchor_hit_radius_pixels = 6
        self._state = PreviewShellState()

    @property
    def state(self) -> PreviewShellState:
        return self._state

    def build_view(
        self,
        frame: CapturedFrame,
        *,
        viewport_width: int,
        viewport_height: int,
        fps: float | None = None,
        focus_state: FocusPreviewState | None = None,
        warning: str | None = None,
        has_focus_toggle: bool = False,
    ) -> PreviewShellViewModel:
        display_scale = self._geometry_service.resolve_display_scale(
            frame.width,
            frame.height,
            viewport_width,
            viewport_height,
            self._state.geometry_state,
            min_zoom_scale=self._min_zoom_scale,
        )
        self._state.last_display_scale = display_scale
        viewport_origin = self._geometry_service.resolve_viewport_origin(
            frame.width,
            frame.height,
            viewport_width,
            viewport_height,
            display_scale,
            self._state.geometry_state,
        )
        mapping = self._geometry_service.build_viewport_mapping(
            frame.width,
            frame.height,
            viewport_width,
            viewport_height,
            display_scale,
            src_x=viewport_origin[0],
            src_y=viewport_origin[1],
        )
        self._state.last_viewport_mapping = mapping
        selected_point = self._state.interaction_state.selected_point
        crosshair_point = selected_point or self._state.interaction_state.last_cursor_source_point
        selected_point_text = None
        if selected_point is not None:
            selected_point_text = self._coordinate_export_service.format_point(*selected_point)
        active_roi = self._roi_state_service.get_active_roi()
        focus_anchor_point = self._resolve_focus_anchor_point(
            frame=frame,
            active_roi=active_roi,
            focus_state=focus_state,
        )
        status_model = self._status_model_service.build_status_model(
            fit_to_window=self._state.geometry_state.fit_to_window,
            display_scale=display_scale,
            viewport_origin_scaled=self._state.geometry_state.viewport_origin_scaled,
            fps=fps,
            selected_point=selected_point,
            selected_point_text=selected_point_text,
            warning=warning,
            transient_message=self._state.interaction_state.last_status_message,
            has_focus_provider=has_focus_toggle,
            focus_status_visible=self._state.interaction_state.focus_status_visible,
            focus_state=focus_state,
            roi_mode=self._state.interaction_state.roi_mode,
            roi_anchor_point=self._state.interaction_state.roi_anchor_point,
            roi_preview_point=self._state.interaction_state.roi_preview_point,
            active_roi=active_roi,
            has_snapshot_shortcut=False,
            has_focus_toggle=has_focus_toggle,
        )
        overlay_model = self._status_model_service.build_overlay_model(
            crosshair_visible=self._state.interaction_state.crosshair_visible,
            selected_point=crosshair_point,
            draft_roi=self._build_draft_roi(),
            active_roi=active_roi,
            focus_status_visible=self._state.interaction_state.focus_status_visible,
            focus_state=focus_state,
            focus_anchor_point=focus_anchor_point,
            show_viewport_outline=self._should_draw_viewport_outline(mapping),
        )
        overlay_model = PreviewOverlayModel(
            crosshair_point=overlay_model.crosshair_point,
            draft_roi=overlay_model.draft_roi,
            active_roi=overlay_model.active_roi,
            active_roi_emphasis=self._resolve_active_roi_emphasis(active_roi),
            focus_anchor_point=overlay_model.focus_anchor_point,
            focus_label=overlay_model.focus_label,
            show_viewport_outline=overlay_model.show_viewport_outline,
            anchor_handles=self._build_anchor_handles(active_roi),
        )
        return PreviewShellViewModel(
            image=render_viewport_image(frame, mapping),
            overlay_model=overlay_model,
            status_lines=self._format_status_lines(status_model),
            viewport_mapping=mapping,
        )

    def apply_command(
        self,
        command: PreviewInteractionCommand,
        *,
        has_focus_provider: bool = False,
    ) -> PreviewInteractionOutcome:
        outcome = self._interaction_service.apply_command(
            command,
            self._state.interaction_state,
            self._state.geometry_state,
            last_display_scale=self._state.last_display_scale,
            last_viewport_mapping=self._state.last_viewport_mapping,
            zoom_step=self._zoom_step,
            min_zoom_scale=self._min_zoom_scale,
            max_zoom_scale=self._max_zoom_scale,
            has_focus_provider=has_focus_provider,
            has_snapshot_callback=False,
            coordinate_formatter=self._coordinate_export_service.format_point,
            roi_builder=self._build_roi_definition,
        )
        if outcome.committed_roi is not None:
            self._roi_state_service.set_active_roi(outcome.committed_roi)
        return outcome

    def handle_canvas_click(self, x: int, y: int) -> PreviewInteractionOutcome:
        self.apply_command(
            PreviewInteractionCommand(action="cursor_moved", viewport_point=(x, y)),
        )
        if self._state.interaction_state.crosshair_visible:
            source_point = self._geometry_service.map_viewport_point_to_source(self._state.last_viewport_mapping, x, y)
            return self.apply_command(
                PreviewInteractionCommand(action="select_source_point", source_point=source_point),
            )
        if self._toggle_locked_anchor_drag_if_active(x, y):
            return PreviewInteractionOutcome()
        if self._start_anchor_drag_if_hit(x, y):
            return PreviewInteractionOutcome()
        if self._start_roi_body_drag_if_hit(x, y):
            return PreviewInteractionOutcome()
        source_point = self._geometry_service.map_viewport_point_to_source(self._state.last_viewport_mapping, x, y)
        return self.apply_command(
            PreviewInteractionCommand(action="select_source_point", source_point=source_point),
        )

    def handle_left_release(self, x: int, y: int, *, shift_down: bool = False) -> PreviewInteractionOutcome:
        if self._state.interaction_state.active_anchor_drag_id is None:
            return PreviewInteractionOutcome(handled=False)
        source_point = self._geometry_service.map_viewport_point_to_source(self._state.last_viewport_mapping, x, y)
        if source_point is not None:
            self._update_anchor_drag(source_point, shift_down=shift_down)
        drag_mode = self._state.interaction_state.active_anchor_drag_mode
        if drag_mode == "pending":
            anchor_id = self._state.interaction_state.active_anchor_drag_id
            self._state.interaction_state.active_anchor_drag_mode = "locked"
            self._state.interaction_state.hovered_anchor_id = anchor_id
            if anchor_id == "selected_point":
                self._state.interaction_state.last_status_message = "Point drag locked"
            else:
                self._state.interaction_state.last_status_message = "ROI drag locked"
            return PreviewInteractionOutcome()
        if drag_mode == "locked":
            return PreviewInteractionOutcome()
        anchor_id = self._state.interaction_state.active_anchor_drag_id
        self._clear_active_drag_state()
        self._state.interaction_state.hovered_anchor_id = anchor_id
        if anchor_id == "selected_point":
            self._state.interaction_state.last_status_message = "Point moved"
        else:
            self._state.interaction_state.last_status_message = "ROI updated"
        return PreviewInteractionOutcome()

    def handle_mouse_wheel(self, x: int, y: int, wheel_delta: int) -> PreviewInteractionOutcome:
        self.apply_command(
            PreviewInteractionCommand(action="cursor_moved", viewport_point=(x, y)),
        )
        source_point = self._geometry_service.map_viewport_point_to_source(self._state.last_viewport_mapping, x, y)
        return self.apply_command(
            PreviewInteractionCommand(action="wheel_zoom", source_point=source_point, wheel_delta=wheel_delta),
        )

    def handle_pan_start(self, x: int, y: int) -> PreviewInteractionOutcome:
        return self.apply_command(PreviewInteractionCommand(action="start_pan", viewport_point=(x, y)))

    def handle_pan_move(self, x: int, y: int) -> PreviewInteractionOutcome:
        self.apply_command(
            PreviewInteractionCommand(action="cursor_moved", viewport_point=(x, y)),
        )
        return self.apply_command(PreviewInteractionCommand(action="update_pan", viewport_point=(x, y)))

    def handle_pan_stop(self) -> PreviewInteractionOutcome:
        return self.apply_command(PreviewInteractionCommand(action="stop_pan"))

    def handle_pointer_move(self, x: int, y: int, *, left_button_down: bool = False, shift_down: bool = False) -> None:
        source_point = self._geometry_service.map_viewport_point_to_source(self._state.last_viewport_mapping, x, y)
        self.apply_command(
            PreviewInteractionCommand(action="cursor_moved", viewport_point=(x, y), source_point=source_point),
        )
        if self._state.interaction_state.crosshair_visible:
            return
        active_anchor_drag_id = self._state.interaction_state.active_anchor_drag_id
        if active_anchor_drag_id is not None:
            self._state.interaction_state.hovered_anchor_id = active_anchor_drag_id
            if self._state.interaction_state.active_anchor_drag_mode == "pending" and left_button_down:
                self._state.interaction_state.active_anchor_drag_mode = "hold"
            self._sync_active_drag_modifier_state(shift_down=shift_down)
            if source_point is not None and self._state.interaction_state.active_anchor_drag_mode in {"hold", "locked"}:
                self._update_anchor_drag(source_point, shift_down=shift_down)
            return
        self._state.interaction_state.hovered_anchor_id = self._resolve_hovered_anchor_id(x, y)
        if self._state.interaction_state.roi_anchor_point is None:
            return
        self._state.interaction_state.roi_preview_point = source_point

    def clear_hovered_anchor(self) -> None:
        self._state.interaction_state.hovered_anchor_id = None

    def cancel_active_drag(self) -> bool:
        anchor_id = self._state.interaction_state.active_anchor_drag_id
        if anchor_id is None:
            return False
        if anchor_id == "selected_point":
            start_point = self._state.interaction_state.active_drag_start_selected_point
            if start_point is not None:
                self._state.interaction_state.selected_point = start_point
            self._state.interaction_state.last_status_message = "Point drag canceled"
        else:
            start_roi = self._state.interaction_state.active_drag_start_roi
            if start_roi is not None:
                self._roi_state_service.set_active_roi(start_roi)
            self._state.interaction_state.last_status_message = "ROI drag canceled"
        self._clear_active_drag_state()
        return True

    def _build_draft_roi(self) -> RoiDefinition | None:
        roi_mode = self._state.interaction_state.roi_mode
        anchor = self._state.interaction_state.roi_anchor_point
        preview = self._state.interaction_state.roi_preview_point
        if roi_mode is None or anchor is None or preview is None:
            return None
        return self._build_roi_definition(roi_mode, anchor, preview)

    def _build_anchor_handles(self, active_roi: RoiDefinition | None) -> tuple[PreviewAnchorHandle, ...]:
        handles: list[PreviewAnchorHandle] = []
        if active_roi is None:
            return tuple(handles)
        show_roi_handles = self._should_show_roi_handles(active_roi)
        if not show_roi_handles:
            return tuple(handles)
        bounds = roi_bounds(active_roi)
        if bounds is None:
            return tuple(handles)
        left = int(round(bounds[0]))
        top = int(round(bounds[1]))
        right = int(round(bounds[2]))
        bottom = int(round(bounds[3]))
        for anchor_id, point in (
            ("roi_top_left", (left, top)),
            ("roi_top_right", (right, top)),
            ("roi_bottom_left", (left, bottom)),
            ("roi_bottom_right", (right, bottom)),
        ):
            handles.append(
                PreviewAnchorHandle(
                    anchor_id=anchor_id,
                    point=point,
                    role="roi",
                    is_hovered=self._state.interaction_state.hovered_anchor_id == anchor_id,
                    is_active=self._state.interaction_state.active_anchor_drag_id == anchor_id,
                )
            )
        if active_roi.shape == "rectangle":
            midpoint_x = int(round((left + right) / 2.0))
            midpoint_y = int(round((top + bottom) / 2.0))
            for anchor_id, point in (
                ("roi_mid_top", (midpoint_x, top)),
                ("roi_mid_right", (right, midpoint_y)),
                ("roi_mid_bottom", (midpoint_x, bottom)),
                ("roi_mid_left", (left, midpoint_y)),
            ):
                handles.append(
                    PreviewAnchorHandle(
                        anchor_id=anchor_id,
                        point=point,
                        role="roi",
                        is_hovered=self._state.interaction_state.hovered_anchor_id == anchor_id,
                        is_active=self._state.interaction_state.active_anchor_drag_id == anchor_id,
                    )
                )
        return tuple(handles)

    def _should_show_roi_handles(self, active_roi: RoiDefinition) -> bool:
        active_anchor_drag_id = self._state.interaction_state.active_anchor_drag_id
        if active_anchor_drag_id is not None and active_anchor_drag_id.startswith("roi_"):
            return True
        cursor_point = self._state.interaction_state.last_cursor_source_point
        if cursor_point is None:
            return False
        bounds = roi_bounds(active_roi)
        if bounds is None:
            return False
        return bounds[0] <= cursor_point[0] <= bounds[2] and bounds[1] <= cursor_point[1] <= bounds[3]

    def _resolve_hovered_anchor_id(self, viewport_x: int, viewport_y: int) -> str | None:
        best_anchor_id = None
        best_distance_sq = (self._anchor_hit_radius_pixels + 1) ** 2
        for anchor_id, point in self._iter_anchor_hit_targets():
            viewport_point = self._geometry_service.map_source_point_to_viewport(
                self._state.last_viewport_mapping,
                point,
            )
            if viewport_point is None:
                continue
            delta_x = viewport_x - viewport_point[0]
            delta_y = viewport_y - viewport_point[1]
            distance_sq = delta_x * delta_x + delta_y * delta_y
            if distance_sq <= self._anchor_hit_radius_pixels * self._anchor_hit_radius_pixels and distance_sq < best_distance_sq:
                best_anchor_id = anchor_id
                best_distance_sq = distance_sq
        return best_anchor_id

    def _iter_anchor_hit_targets(self) -> tuple[tuple[str, tuple[int, int]], ...]:
        targets: list[tuple[str, tuple[int, int]]] = []
        selected_point = self._state.interaction_state.selected_point
        if selected_point is not None:
            targets.append(("selected_point", selected_point))
        active_roi = self._roi_state_service.get_active_roi()
        if active_roi is None:
            return tuple(targets)
        bounds = roi_bounds(active_roi)
        if bounds is None:
            return tuple(targets)
        left = int(round(bounds[0]))
        top = int(round(bounds[1]))
        right = int(round(bounds[2]))
        bottom = int(round(bounds[3]))
        targets.extend(
            (
                ("roi_top_left", (left, top)),
                ("roi_top_right", (right, top)),
                ("roi_bottom_left", (left, bottom)),
                ("roi_bottom_right", (right, bottom)),
            )
        )
        if active_roi.shape == "rectangle":
            midpoint_x = int(round((left + right) / 2.0))
            midpoint_y = int(round((top + bottom) / 2.0))
            targets.extend(
                (
                    ("roi_mid_top", (midpoint_x, top)),
                    ("roi_mid_right", (right, midpoint_y)),
                    ("roi_mid_bottom", (midpoint_x, bottom)),
                    ("roi_mid_left", (left, midpoint_y)),
                )
            )
        return tuple(targets)

    def _start_anchor_drag_if_hit(self, viewport_x: int, viewport_y: int) -> bool:
        if self._state.interaction_state.roi_mode is not None:
            if self._state.interaction_state.roi_anchor_point is not None:
                return False
            if self._roi_state_service.get_active_roi() is None:
                return False
        anchor_id = self._resolve_hovered_anchor_id(viewport_x, viewport_y)
        if anchor_id is None:
            return False
        self._state.interaction_state.active_anchor_drag_id = anchor_id
        self._state.interaction_state.active_anchor_drag_mode = "pending"
        self._state.interaction_state.hovered_anchor_id = anchor_id
        self._state.interaction_state.active_drag_origin_source_point = self._geometry_service.map_viewport_point_to_source(
            self._state.last_viewport_mapping,
            viewport_x,
            viewport_y,
        )
        self._state.interaction_state.active_drag_initial_roi = self._roi_state_service.get_active_roi()
        self._state.interaction_state.active_drag_start_roi = self._roi_state_service.get_active_roi()
        self._state.interaction_state.active_drag_start_selected_point = self._state.interaction_state.selected_point
        self._state.interaction_state.active_drag_shift_down = False
        self._state.interaction_state.active_drag_locked_axis = None
        if anchor_id == "selected_point":
            self._state.interaction_state.last_status_message = "Dragging point"
        else:
            self._state.interaction_state.last_status_message = "Dragging ROI"
        return True

    def _start_roi_body_drag_if_hit(self, viewport_x: int, viewport_y: int) -> bool:
        if self._state.interaction_state.roi_anchor_point is not None:
            return False
        active_roi = self._roi_state_service.get_active_roi()
        if active_roi is None:
            return False
        source_point = self._geometry_service.map_viewport_point_to_source(self._state.last_viewport_mapping, viewport_x, viewport_y)
        if source_point is None or not self._is_point_inside_roi_bounds(active_roi, source_point):
            return False
        self._state.interaction_state.active_anchor_drag_id = "roi_body"
        self._state.interaction_state.active_anchor_drag_mode = "pending"
        self._state.interaction_state.active_drag_origin_source_point = source_point
        self._state.interaction_state.active_drag_initial_roi = active_roi
        self._state.interaction_state.active_drag_start_roi = active_roi
        self._state.interaction_state.active_drag_start_selected_point = self._state.interaction_state.selected_point
        self._state.interaction_state.active_drag_shift_down = False
        self._state.interaction_state.active_drag_locked_axis = None
        self._state.interaction_state.last_status_message = "Dragging ROI"
        return True

    def _toggle_locked_anchor_drag_if_active(self, viewport_x: int, viewport_y: int) -> bool:
        if self._state.interaction_state.active_anchor_drag_id is None:
            return False
        if self._state.interaction_state.active_anchor_drag_mode != "locked":
            return False
        source_point = self._geometry_service.map_viewport_point_to_source(self._state.last_viewport_mapping, viewport_x, viewport_y)
        if source_point is not None:
            self._update_anchor_drag(source_point, shift_down=False)
        anchor_id = self._state.interaction_state.active_anchor_drag_id
        self._clear_active_drag_state()
        self._state.interaction_state.hovered_anchor_id = anchor_id
        if anchor_id == "selected_point":
            self._state.interaction_state.last_status_message = "Point moved"
        else:
            self._state.interaction_state.last_status_message = "ROI updated"
        return True

    def _update_anchor_drag(self, source_point: tuple[int, int], *, shift_down: bool) -> None:
        anchor_id = self._state.interaction_state.active_anchor_drag_id
        if anchor_id is None:
            return
        if anchor_id == "selected_point":
            self._state.interaction_state.selected_point = source_point
            return
        if anchor_id == "roi_body":
            active_roi = self._state.interaction_state.active_drag_initial_roi
            origin_point = self._state.interaction_state.active_drag_origin_source_point
            if active_roi is None or origin_point is None:
                return
            translated_roi = self._build_translated_roi(
                active_roi,
                origin_point,
                source_point,
                shift_down=shift_down,
            )
            if translated_roi is not None:
                self._roi_state_service.set_active_roi(translated_roi)
            return
        active_roi = self._roi_state_service.get_active_roi()
        if active_roi is None:
            return
        updated_roi = self._build_dragged_roi(active_roi, anchor_id, source_point)
        if updated_roi is None:
            return
        self._roi_state_service.set_active_roi(updated_roi)
        self._state.interaction_state.active_drag_initial_roi = updated_roi

    def _build_dragged_roi(
        self,
        active_roi: RoiDefinition,
        anchor_id: str,
        source_point: tuple[int, int],
    ) -> RoiDefinition | None:
        bounds = roi_bounds(active_roi)
        if bounds is None:
            return None
        left = int(round(bounds[0]))
        top = int(round(bounds[1]))
        right = int(round(bounds[2]))
        bottom = int(round(bounds[3]))
        opposite_points = {
            "roi_top_left": (right, bottom),
            "roi_top_right": (left, bottom),
            "roi_bottom_left": (right, top),
            "roi_bottom_right": (left, top),
        }
        opposite = opposite_points.get(anchor_id)
        if opposite is None:
            if active_roi.shape != "rectangle":
                return None
            if anchor_id == "roi_mid_top":
                top = source_point[1]
            elif anchor_id == "roi_mid_right":
                right = source_point[0]
            elif anchor_id == "roi_mid_bottom":
                bottom = source_point[1]
            elif anchor_id == "roi_mid_left":
                left = source_point[0]
            else:
                return None
            return RoiDefinition(
                roi_id=active_roi.roi_id,
                shape="rectangle",
                points=((left, top), (right, bottom)),
                label=active_roi.label,
                enabled=active_roi.enabled,
                metadata=dict(active_roi.metadata),
            )
        if active_roi.shape == "ellipse":
            left = min(opposite[0], source_point[0])
            top = min(opposite[1], source_point[1])
            right = max(opposite[0], source_point[0])
            bottom = max(opposite[1], source_point[1])
            return RoiDefinition(roi_id=active_roi.roi_id, shape="ellipse", points=((left, top), (right, bottom)))
        return self._build_roi_definition(active_roi.shape, opposite, source_point)

    def _build_translated_roi(
        self,
        active_roi: RoiDefinition,
        origin_point: tuple[int, int],
        source_point: tuple[int, int],
        *,
        shift_down: bool,
    ) -> RoiDefinition | None:
        delta_x = source_point[0] - origin_point[0]
        delta_y = source_point[1] - origin_point[1]
        if shift_down:
            locked_axis = self._state.interaction_state.active_drag_locked_axis
            if locked_axis is None:
                locked_axis = "x" if abs(delta_x) >= abs(delta_y) else "y"
                self._state.interaction_state.active_drag_locked_axis = locked_axis
            if locked_axis == "x":
                delta_y = 0
            else:
                delta_x = 0
        translated_points = tuple((point[0] + delta_x, point[1] + delta_y) for point in active_roi.points)
        return RoiDefinition(
            roi_id=active_roi.roi_id,
            shape=active_roi.shape,
            points=translated_points,
            label=active_roi.label,
            enabled=active_roi.enabled,
            metadata=dict(active_roi.metadata),
        )

    def _is_point_inside_roi_bounds(self, active_roi: RoiDefinition, point: tuple[int, int]) -> bool:
        bounds = self._resolve_effective_roi_drag_bounds(active_roi)
        return bounds[0] <= point[0] <= bounds[2] and bounds[1] <= point[1] <= bounds[3]

    def _resolve_effective_roi_drag_bounds(self, active_roi: RoiDefinition) -> tuple[float, float, float, float]:
        bounds = roi_bounds(active_roi)
        if bounds is None:
            return (0.0, 0.0, 0.0, 0.0)
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        minimum_hit_size_source = max(1.0, 20.0 / max(self._state.last_display_scale, 1e-9))
        pad_x = max(0.0, (minimum_hit_size_source - width) / 2.0)
        pad_y = max(0.0, (minimum_hit_size_source - height) / 2.0)
        return (
            bounds[0] - pad_x,
            bounds[1] - pad_y,
            bounds[2] + pad_x,
            bounds[3] + pad_y,
        )

    def _sync_active_drag_modifier_state(self, *, shift_down: bool) -> None:
        if self._state.interaction_state.active_anchor_drag_id != "roi_body":
            return
        if shift_down == self._state.interaction_state.active_drag_shift_down:
            return
        self._state.interaction_state.active_drag_shift_down = shift_down
        self._state.interaction_state.active_drag_locked_axis = None

    def _resolve_active_roi_emphasis(self, active_roi: RoiDefinition | None) -> str:
        if active_roi is None:
            return "normal"
        active_anchor_drag_id = self._state.interaction_state.active_anchor_drag_id
        if active_anchor_drag_id is not None and active_anchor_drag_id.startswith("roi_"):
            return "drag"
        if active_anchor_drag_id == "roi_body":
            return "drag"
        hovered_anchor_id = self._state.interaction_state.hovered_anchor_id
        if hovered_anchor_id is not None and hovered_anchor_id.startswith("roi_"):
            return "hover"
        cursor_point = self._state.interaction_state.last_cursor_source_point
        if cursor_point is not None:
            bounds = self._resolve_effective_roi_drag_bounds(active_roi)
            if bounds[0] <= cursor_point[0] <= bounds[2] and bounds[1] <= cursor_point[1] <= bounds[3]:
                return "hover"
        return "normal"

    def _clear_active_drag_state(self) -> None:
        self._state.interaction_state.active_anchor_drag_id = None
        self._state.interaction_state.active_anchor_drag_mode = None
        self._state.interaction_state.active_drag_origin_source_point = None
        self._state.interaction_state.active_drag_initial_roi = None
        self._state.interaction_state.active_drag_start_roi = None
        self._state.interaction_state.active_drag_start_selected_point = None
        self._state.interaction_state.active_drag_shift_down = False
        self._state.interaction_state.active_drag_locked_axis = None

    @staticmethod
    def _resolve_focus_anchor_point(
        *,
        frame: CapturedFrame,
        active_roi: RoiDefinition | None,
        focus_state: FocusPreviewState | None,
    ) -> tuple[int, int] | None:
        if focus_state is not None:
            return (
                int(round(focus_state.overlay.anchor_x)),
                int(round(focus_state.overlay.anchor_y)),
            )
        if active_roi is not None:
            bounds = roi_bounds(active_roi)
            if bounds is not None:
                return (
                    int(round((bounds[0] + bounds[2]) / 2.0)),
                    int(round((bounds[1] + bounds[3]) / 2.0)),
                )
        return (frame.width // 2, frame.height // 2)

    @staticmethod
    def _should_draw_viewport_outline(mapping: ViewportMapping) -> bool:
        return not (mapping.copy_width >= mapping.viewport_width and mapping.copy_height >= mapping.viewport_height)

    def _build_roi_definition(
        self,
        roi_mode: str | None,
        anchor_point: tuple[int, int],
        selected_point: tuple[int, int],
    ) -> RoiDefinition:
        if roi_mode == "ellipse":
            radius_x = abs(selected_point[0] - anchor_point[0])
            radius_y = abs(selected_point[1] - anchor_point[1])
            points = (
                (anchor_point[0] - radius_x, anchor_point[1] - radius_y),
                (anchor_point[0] + radius_x, anchor_point[1] + radius_y),
            )
            return RoiDefinition(roi_id="shell-roi", shape="ellipse", points=points)
        return RoiDefinition(roi_id="shell-roi", shape="rectangle", points=(anchor_point, selected_point))

    def _format_status_lines(self, status_model) -> list[str]:
        lines = [" | ".join(entry.value for entry in status_model.primary_line.entries)]
        if status_model.roi_status is not None:
            lines.append(self._format_roi_status(status_model.roi_status))
        if status_model.focus_status is not None and status_model.focus_status.state != "hidden":
            lines.append(self._format_focus_status(status_model.focus_status))
        lines.append(" ".join(f"{item.key}={item.action}" for item in status_model.shortcuts))
        return [line for line in lines if line]

    def _format_roi_status(self, roi_status) -> str:
        if roi_status.state == "active":
            return f"ROI active: {roi_status.active_shape}"
        if roi_status.state == "mode_active":
            if roi_status.roi_mode == "rectangle":
                return "ROI mode: rectangle (entry point active)"
            if roi_status.roi_mode == "ellipse":
                return "ROI mode: ellipse (entry point active)"
            return f"ROI mode: {roi_status.roi_mode}"
        anchor_text = self._coordinate_export_service.format_point(*roi_status.anchor_point)
        base = f"ROI mode: {roi_status.roi_mode} anchor={anchor_text}"
        if roi_status.preview_point is None:
            return base
        preview_text = self._coordinate_export_service.format_point(*roi_status.preview_point)
        return f"{base} preview={preview_text}"

    @staticmethod
    def _format_focus_status(focus_status) -> str:
        if focus_status.state == "waiting":
            return "Focus: waiting"
        if focus_status.state == "invalid":
            return f"Focus: invalid ({focus_status.metric_name})"
        return f"Focus: {focus_status.metric_name}={format_focus_score(focus_status.score)}"
__all__ = [
    "PreviewShellPresenter",
    "PreviewShellState",
    "PreviewShellViewModel",
    "RenderedViewportImage",
    "render_viewport_image",
]
