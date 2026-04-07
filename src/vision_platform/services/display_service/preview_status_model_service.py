from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from vision_platform.libraries.common_models import FocusPreviewState, RoiDefinition

PreviewScaleMode = Literal["fit", "zoom"]
PreviewSeverity = Literal["info", "warning"]


def format_focus_score(score: float) -> str:
    return f"{score:.3e}"


@dataclass(frozen=True, slots=True)
class PreviewStatusEntry:
    label: str
    value: str
    severity: PreviewSeverity = "info"


@dataclass(frozen=True, slots=True)
class PreviewStatusLineModel:
    entries: tuple[PreviewStatusEntry, ...]


@dataclass(frozen=True, slots=True)
class PreviewShortcutHint:
    key: str
    action: str


@dataclass(frozen=True, slots=True)
class PreviewFocusStatusModel:
    state: Literal["hidden", "waiting", "invalid", "valid"]
    metric_name: str | None = None
    score: float | None = None


@dataclass(frozen=True, slots=True)
class PreviewRoiStatusModel:
    state: Literal["inactive", "mode_active", "anchor_pending", "active"]
    roi_mode: str | None = None
    anchor_point: tuple[int, int] | None = None
    preview_point: tuple[int, int] | None = None
    active_shape: str | None = None


@dataclass(frozen=True, slots=True)
class PreviewStatusModel:
    primary_line: PreviewStatusLineModel
    roi_status: PreviewRoiStatusModel | None
    focus_status: PreviewFocusStatusModel | None
    shortcuts: tuple[PreviewShortcutHint, ...]


@dataclass(frozen=True, slots=True)
class PreviewOverlayModel:
    @dataclass(frozen=True, slots=True)
    class AnchorHandle:
        anchor_id: str
        point: tuple[int, int]
        role: Literal["point", "roi"]
        is_hovered: bool = False
        is_active: bool = False

    crosshair_point: tuple[int, int] | None = None
    draft_roi: RoiDefinition | None = None
    active_roi: RoiDefinition | None = None
    active_roi_emphasis: Literal["normal", "hover", "drag"] = "normal"
    focus_anchor_point: tuple[int, int] | None = None
    focus_label: str | None = None
    show_viewport_outline: bool = False
    anchor_handles: tuple[AnchorHandle, ...] = ()


class PreviewStatusModelService:
    """Compose preview status and overlay models independently of a concrete renderer."""

    def build_status_model(
        self,
        *,
        fit_to_window: bool,
        display_scale: float,
        viewport_origin_scaled: tuple[int, int],
        fps: float | None,
        selected_point: tuple[int, int] | None,
        selected_point_text: str | None,
        warning: str | None,
        transient_message: str | None,
        has_focus_provider: bool,
        focus_status_visible: bool,
        focus_state: FocusPreviewState | None,
        roi_mode: str | None,
        roi_anchor_point: tuple[int, int] | None,
        roi_preview_point: tuple[int, int] | None,
        active_roi: RoiDefinition | None,
        has_snapshot_shortcut: bool,
        has_focus_toggle: bool,
    ) -> PreviewStatusModel:
        primary_entries = [
            PreviewStatusEntry(
                label="mode",
                value=f'{"FIT" if fit_to_window else "ZOOM"} {display_scale:.2f}x',
            )
        ]
        if not fit_to_window:
            primary_entries.append(
                PreviewStatusEntry(
                    label="viewport",
                    value=f"view={viewport_origin_scaled[0]},{viewport_origin_scaled[1]}",
                )
            )
        if fps is not None:
            primary_entries.append(PreviewStatusEntry(label="fps", value=f"FPS {fps:.1f}"))
        if selected_point is not None and selected_point_text is not None:
            primary_entries.append(PreviewStatusEntry(label="selection", value=f"Selected {selected_point_text}"))
        if warning:
            primary_entries.append(PreviewStatusEntry(label="warning", value=f"WARN: {warning}", severity="warning"))
        if transient_message:
            primary_entries.append(PreviewStatusEntry(label="message", value=transient_message))

        return PreviewStatusModel(
            primary_line=PreviewStatusLineModel(entries=tuple(primary_entries)),
            roi_status=self.build_roi_status_model(
                roi_mode=roi_mode,
                roi_anchor_point=roi_anchor_point,
                roi_preview_point=roi_preview_point,
                active_roi=active_roi,
            ),
            focus_status=self.build_focus_status_model(
                has_focus_provider=has_focus_provider,
                focus_status_visible=focus_status_visible,
                focus_state=focus_state,
            ),
            shortcuts=self.build_shortcut_hints(
                has_snapshot_shortcut=has_snapshot_shortcut,
                has_focus_toggle=has_focus_toggle,
            ),
        )

    def build_focus_status_model(
        self,
        *,
        has_focus_provider: bool,
        focus_status_visible: bool,
        focus_state: FocusPreviewState | None,
    ) -> PreviewFocusStatusModel | None:
        if not has_focus_provider:
            return None
        if not focus_status_visible:
            return PreviewFocusStatusModel(state="hidden")
        if focus_state is None:
            return PreviewFocusStatusModel(state="waiting")
        if not focus_state.result.is_valid:
            return PreviewFocusStatusModel(
                state="invalid",
                metric_name=focus_state.result.metric_name,
            )
        return PreviewFocusStatusModel(
            state="valid",
            metric_name=focus_state.result.metric_name,
            score=focus_state.result.score,
        )

    def build_roi_status_model(
        self,
        *,
        roi_mode: str | None,
        roi_anchor_point: tuple[int, int] | None,
        roi_preview_point: tuple[int, int] | None,
        active_roi: RoiDefinition | None,
    ) -> PreviewRoiStatusModel | None:
        if roi_anchor_point is not None and roi_mode is not None:
            return PreviewRoiStatusModel(
                state="anchor_pending",
                roi_mode=roi_mode,
                anchor_point=roi_anchor_point,
                preview_point=roi_preview_point,
            )
        if active_roi is not None:
            return PreviewRoiStatusModel(
                state="active",
                active_shape=active_roi.shape,
            )
        if roi_mode is not None:
            return PreviewRoiStatusModel(
                state="mode_active",
                roi_mode=roi_mode,
            )
        return None

    def build_overlay_model(
        self,
        *,
        crosshair_visible: bool,
        selected_point: tuple[int, int] | None,
        draft_roi: RoiDefinition | None,
        active_roi: RoiDefinition | None,
        focus_status_visible: bool,
        focus_state: FocusPreviewState | None,
        focus_anchor_point: tuple[int, int] | None,
        show_viewport_outline: bool,
    ) -> PreviewOverlayModel:
        focus_label = None
        resolved_focus_anchor = focus_anchor_point
        if focus_status_visible and focus_state is not None:
            resolved_focus_anchor = (
                int(round(focus_state.overlay.anchor_x)),
                int(round(focus_state.overlay.anchor_y)),
            )
            if focus_state.result.is_valid:
                focus_label = f"Focus {format_focus_score(focus_state.result.score)}"
            else:
                focus_label = "Focus invalid"
        elif focus_status_visible and resolved_focus_anchor is not None:
            focus_label = "Focus..."
        return PreviewOverlayModel(
            crosshair_point=selected_point if crosshair_visible else None,
            draft_roi=draft_roi,
            active_roi=active_roi,
            focus_anchor_point=resolved_focus_anchor,
            focus_label=focus_label,
            show_viewport_outline=show_viewport_outline,
        )

    @staticmethod
    def build_shortcut_hints(
        *,
        has_snapshot_shortcut: bool,
        has_focus_toggle: bool,
    ) -> tuple[PreviewShortcutHint, ...]:
        shortcuts = [
            PreviewShortcutHint(key="i", action="in"),
            PreviewShortcutHint(key="o", action="out"),
            PreviewShortcutHint(key="f", action="fit"),
        ]
        if has_snapshot_shortcut:
            shortcuts.append(PreviewShortcutHint(key="+", action="snapshot"))
        shortcuts.append(PreviewShortcutHint(key="x", action="crosshair"))
        if has_focus_toggle:
            shortcuts.append(PreviewShortcutHint(key="y", action="focus"))
        shortcuts.extend(
            [
                PreviewShortcutHint(key="r", action="rect"),
                PreviewShortcutHint(key="e", action="ellipse"),
                PreviewShortcutHint(key="wheel", action="zoom"),
                PreviewShortcutHint(key="mdrag", action="pan"),
                PreviewShortcutHint(key="c", action="copy"),
                PreviewShortcutHint(key="q", action="quit"),
            ]
        )
        return tuple(shortcuts)


__all__ = [
    "PreviewFocusStatusModel",
    "PreviewOverlayModel",
    "PreviewRoiStatusModel",
    "PreviewShortcutHint",
    "PreviewStatusEntry",
    "PreviewStatusLineModel",
    "PreviewStatusModel",
    "PreviewStatusModelService",
    "format_focus_score",
]
