# Status

- maturity: active prototype
- current implementation: smoke/demo flows now live in `src/vision_platform/apps/opencv_prototype`; OpenCV-facing implementation lives under `src/vision_platform/imaging`, while `camera_app.smoke` remains as a compatibility layer
- working now: simulated preview with optional focus-state composition, save demo, command-flow demo, focus-preview smoke demo, overlay-payload demo, root helper scripts, and a first real-hardware preview demo for local live inspection
- partial: operator-friendly display behavior for large camera frames is still missing; the current hardware preview shows the raw frame without fit-to-window, zoom, or pan
- known issues: OpenCV path is optional and still needs broader hardware-backed validation beyond the first verified live preview
- technical debt: demo result typing still comes from the legacy smoke package until a dedicated platform app model is introduced
- risk: direct script execution outside the editable package setup can still depend on the current `src` path helpers
- architecture note: viewport fitting, zoom, pan, and display-space overlay transforms are intentionally treated as UI/display concerns rather than camera-core concerns
