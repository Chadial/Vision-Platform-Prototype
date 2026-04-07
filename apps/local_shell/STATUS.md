# Status

- maturity: active prototype
- implemented: bounded wxPython local working shell with simulated and hardware-backed startup paths under `vision_platform.apps.local_shell`
- working now: the shell starts through the project `.venv`, opens a real wx window, polls the shared preview stream, and renders the latest simulated or hardware-backed frame in a bounded image area
- working now: snapshot is triggered through the existing command-controller path and writes repo-local example output under `captures/`
- working now: fit/zoom, crosshair toggle, focus toggle/status, and rectangle/ellipse ROI entry reuse the extracted display geometry, interaction, preview-status, and focus-preview layers instead of introducing UI-private business logic
- working now: snapshot notices are rendered as transient status messages instead of pinning the status area after a successful save
- working now: the wx shell now evaluates focus through the shared focus-preview service on a bounded downsampled work frame so the existing headless evaluator remains reusable on large live frames
- working now: the wx canvas now renders one visible focus marker/label at the shared focus anchor instead of relying only on status text
- working now: selected-point and copy feedback now use concise non-duplicative status text, and `Ctrl+C` now follows the current OpenCV-style point-copy baseline
- working now: the wx canvas now renders ROI corner handles only on hover / active drag, while the fixed point remains drag-capable without a permanently visible anchor marker
- working now: active ellipse ROI corner dragging now follows bounding-box semantics instead of expanding unexpectedly from a center-anchor interpretation
- working now: anchor dragging now supports both hold-drag-release and click-to-lock-drag-click-to-release interaction on the same bounded point/ROI path
- working now: the shell uses the current OpenCV preview path as the reference for the first feature cut: preview image, snapshot action, status area, zoom/fit, crosshair, and ROI entry
- working now: startup configuration for `source`, camera alias/id resolution, configuration profiles, and direct configuration overrides reuses the same headless bootstrap/controller semantics as the current CLI path
- partial: the shell now has a bounded hardware-backed startup path, but no committed wx-specific real-device smoke evidence exists yet in the permanent test suite
- partial: recording progress display, ROI visibility toggles, configuration editing, and broader operator controls are intentionally not part of this slice
- technical debt: the current shell keeps its viewport rendering in app-local helper code because no shared non-OpenCV image-presenter abstraction exists yet
- risk: future non-OpenCV frontend growth may justify a shared renderer-facing display adapter above the current app-local bitmap conversion path
