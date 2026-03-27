# Status

- maturity: active core module
- implemented: `CameraDriver`, `SimulatedCameraDriver`, `VimbaXCameraDriver`
- working now: simulator-backed initialization, configuration, and frame capture
- working now: targeted real-hardware initialization, snapshot, and preview runs have been verified locally through the Vimba X path
- partial: repeated real-camera validation is still open
- known issues: the driver interface still bridges through legacy type locations for compatibility
- technical debt: status and frame models are still split between legacy request models and new platform-common placeholders
- risk: unsupported camera features still require broader hardware coverage
