from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class DemoRunResult:
    success: bool
    snapshot_path: Path | None = None
    saved_path: Path | None = None
    rendered_frames: int = 0
    preview_frame_info: Any | None = None
    focus_preview_state: Any | None = None
    snapshot_focus_capture: Any | None = None
    display_overlay_payload: Any | None = None
    initial_interval_capture_status: Any | None = None
    interval_capture_status: Any | None = None
    initial_recording_status: Any | None = None
    recording_status: Any | None = None
    final_status: Any | None = None
    stop_status: Any | None = None
    error_message: str | None = None


__all__ = ["DemoRunResult"]
