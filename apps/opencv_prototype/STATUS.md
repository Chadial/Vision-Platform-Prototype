# Status

- maturity: active prototype
- current implementation: smoke/demo flows now live in `src/vision_platform/apps/opencv_prototype`; OpenCV-facing implementation lives under `src/vision_platform/imaging`, while `camera_app.smoke` remains as a compatibility layer
- working now: simulated preview with optional focus-state composition, save demo, command-flow demo, focus-preview smoke demo, overlay-payload demo, root helper scripts
- partial: hardware-backed preview remains dependent on camera availability
- known issues: OpenCV path is optional and still simulator-validated first
- technical debt: demo result typing still comes from the legacy smoke package until a dedicated platform app model is introduced
- risk: direct script execution outside the editable package setup can still depend on the current `src` path helpers
