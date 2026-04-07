# Status

- maturity: active baseline module
- implemented: UI-free composition of preview focus, snapshot focus, and active ROI into one shared display payload, plus a headless display-geometry service for viewport mapping, zoom, and pan, and a shared preview-interaction command layer
- working now: display consumers can reuse one payload shape without owning ROI or focus composition logic
- working now: preview consumers can reuse one `DisplayGeometryService` for fit-scale resolution, viewport-origin clamping, cursor-anchored zoom, and source/viewport coordinate transforms without depending on OpenCV
- working now: preview consumers can now also reuse one `PreviewInteractionService` for interaction-state transitions such as zoom commands, focus/crosshair toggles, ROI-mode changes, point selection, pan updates, copy requests, and snapshot requests without depending on OpenCV event codes
- working now: a lightweight console-oriented overlay-payload demo consumes the shared payload without introducing a concrete renderer dependency
- working now: the current OpenCV preview window now consumes the geometry service instead of owning viewport math privately
- working now: the current OpenCV preview window now translates HighGUI keyboard/mouse input into shared interaction commands instead of owning those state transitions privately
- partial: no renderer outside the current OpenCV path consumes the geometry service yet
- partial: no non-OpenCV frontend consumes the shared interaction layer yet
- known issues: payload currently carries focus overlays and active ROI only, not future tracking or annotation layers
- technical debt: preview and snapshot focus states still reuse the preview-oriented `FocusPreviewState` name
- risk: future overlay growth may require a small layer model instead of flat fields only
- risk: overlay/status presentation still needs a shared descriptive model above the extracted geometry and interaction layers
