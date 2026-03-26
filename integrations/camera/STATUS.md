# Status

- maturity: active core module
- implemented: `CameraDriver`, `SimulatedCameraDriver`, `VimbaXCameraDriver`
- working now: simulator-backed initialization, configuration, and frame capture
- partial: repeated real-camera validation is still open
- known issues: driver implementation still physically lives under `src/camera_app/drivers`
- technical debt: status and frame models are still split between legacy request models and new platform-common placeholders
- risk: unsupported camera features still require broader hardware coverage
