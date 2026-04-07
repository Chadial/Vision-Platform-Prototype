# Status

- maturity: active prototype
- implemented: bounded wxPython local working shell with simulated and hardware-backed startup paths under `vision_platform.apps.local_shell`
- working now: the shell starts through the project `.venv`, opens a real wx window, polls the shared preview stream, and renders the latest simulated or hardware-backed frame in a bounded image area
- working now: snapshot is triggered through the existing command-controller path and writes repo-local example output under `captures/`
- working now: fit/zoom, crosshair toggle, focus toggle/status, and rectangle/ellipse ROI entry reuse the extracted display geometry, interaction, preview-status, and focus-preview layers instead of introducing UI-private business logic
- working now: the shell uses the current OpenCV preview path as the reference for the first feature cut: preview image, snapshot action, status area, zoom/fit, crosshair, and ROI entry
- working now: startup configuration for `source`, camera alias/id resolution, configuration profiles, and direct configuration overrides reuses the same headless bootstrap/controller semantics as the current CLI path
- partial: the shell now has a bounded hardware-backed startup path, but no committed wx-specific real-device smoke evidence exists yet in the permanent test suite
- partial: recording, configuration editing, focus display, and broader operator controls are intentionally not part of this first slice
- technical debt: the current shell keeps its viewport rendering in app-local helper code because no shared non-OpenCV image-presenter abstraction exists yet
- risk: future non-OpenCV frontend growth may justify a shared renderer-facing display adapter above the current app-local bitmap conversion path
