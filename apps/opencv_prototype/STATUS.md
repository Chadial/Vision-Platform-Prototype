# Status

- maturity: active prototype
- implemented: simulator-backed preview demos, hardware preview demo, preview-frame snapshot save path, overlay-payload demo, and viewport-based preview behavior live under the `vision_platform` app/imaging namespaces
- working now: the current preview baseline supports fit-to-window, cursor-anchored zoom, middle-drag pan, a bottom status band, FPS readout, crosshair and focus-status toggles, two-click rectangle/ellipse ROI creation through shared ROI state, preview-frame snapshot save with explicit directory, and concise operator-facing unavailable/error feedback
- working now: the current hardware preview path has bounded real-device evidence on `DEV_1AB22C046D81`, including visible preview output, zoom/pan behavior, ROI creation, coordinate copy, snapshot shortcut, and normal preview shutdown
- partial: richer operator controls, editable ROI tools, and a broader focus-aware hardware preview path remain open UI-only follow-up work
- technical debt: demo result typing still comes from the legacy smoke package until a dedicated platform app model is introduced
- risk: direct script execution outside the editable package setup can still depend on the current `src` path helpers
- architecture note: viewport fitting, zoom, pan, and display-space overlay transforms are intentionally treated as UI/display concerns rather than camera-core concerns
- residuals:
  - OpenCV HighGUI modifier combinations such as `Ctrl+1` / `Ctrl+2` / `Ctrl+3` are not reliable enough to treat as primary shortcuts on the current Windows setup
  - broader hardware-backed preview validation is still open beyond the bounded verified live-preview path
  - small zoom factors can still show slight cursor-anchor drift because viewport mapping rounds to integer pixel coordinates
  - the preview-frame snapshot shortcut remains available only when an explicit snapshot save directory is configured
