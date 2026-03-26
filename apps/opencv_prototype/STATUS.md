# Status

- maturity: active prototype
- current implementation: existing smoke/demo flows remain in `src/camera_app/smoke` and are exposed through `src/vision_platform/apps/opencv_prototype`; OpenCV-facing implementation now lives under `src/vision_platform/imaging`
- working now: simulated preview, save demo, command-flow demo, root helper scripts
- partial: hardware-backed preview remains dependent on camera availability
- known issues: OpenCV path is optional and still simulator-validated first
- technical debt: smoke/demo entry points still originate in `src/camera_app/smoke`, even though the imaging implementation has been moved behind `vision_platform`
- risk: direct script execution outside the editable package setup can still depend on the current `src` path helpers
