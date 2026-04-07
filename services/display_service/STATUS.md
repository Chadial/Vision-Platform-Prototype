# Status

- maturity: active baseline module
- implemented: UI-free composition of preview focus, snapshot focus, and active ROI into one shared display payload, plus a headless display-geometry service for viewport mapping, zoom, and pan, a shared preview-interaction command layer, and a shared preview-status / overlay model service
- working now: display consumers can reuse one payload shape without owning ROI or focus composition logic
- working now: preview consumers can reuse one `DisplayGeometryService` for fit-scale resolution, viewport-origin clamping, cursor-anchored zoom, and source/viewport coordinate transforms without depending on OpenCV
- working now: preview consumers can now also reuse one `PreviewInteractionService` for interaction-state transitions such as zoom commands, focus/crosshair toggles, ROI-mode changes, point selection, pan updates, copy requests, and snapshot requests without depending on OpenCV event codes
- working now: preview consumers can now also reuse one `PreviewStatusModelService` for descriptive status-line and overlay-layer ownership without depending on OpenCV string formatting or HighGUI drawing assumptions
- working now: a lightweight console-oriented overlay-payload demo consumes the shared payload without introducing a concrete renderer dependency
- working now: the current OpenCV preview window now consumes the geometry service instead of owning viewport math privately
- working now: the current OpenCV preview window now translates HighGUI keyboard/mouse input into shared interaction commands instead of owning those state transitions privately
- working now: the current OpenCV preview window now formats and renders shared preview-status / overlay models instead of owning status-band meaning privately
- working now: the current wx shell now also consumes the geometry service as its bounded non-OpenCV viewport baseline
- working now: the current wx shell now also consumes the shared interaction layer for zoom, pan, ROI entry, point-copy semantics, and bounded anchor hover/drag state
- working now: the current wx shell now also consumes the shared preview-status / overlay model layer, while app-local rendering still decides how those models are drawn
- working now: the shared preview overlay contract now also carries bounded active-ROI emphasis (`normal` / `hover` / `drag`) so non-OpenCV frontends can render stateful frame feedback without owning separate ROI-mode semantics
- working now: the current wx shell now also reuses shared interaction state to keep ROI body panning usable on very small selections through effective body hit bounds, rectangle side-midpoint handles, live `Shift` axis projection toggling, and cancel-to-drag-start behavior
- known issues: payload currently carries focus overlays and active ROI only, not future tracking or annotation layers
- technical debt: preview and snapshot focus states still reuse the preview-oriented `FocusPreviewState` name
- risk: future overlay growth may require a small layer model instead of flat fields only; the new bounded anchor-handle model should stay narrow unless later frontends genuinely need richer editing semantics
