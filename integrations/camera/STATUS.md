# Status

- maturity: active core module
- implemented: `CameraDriver`, `SimulatedCameraDriver`, `VimbaXCameraDriver`
- working now: simulator-backed initialization, configuration, and frame capture
- working now: targeted real-hardware initialization, snapshot, and preview runs have been verified locally through the Vimba X path
- working now: the current real-hardware path now also exposes capability probing through the already opened Vimba camera, avoiding an immediate second Vimba/camera open during `CameraService.initialize()`
- partial: broader repeated real-camera validation is still open beyond the narrowed WP27 serial reuse proof
- known issues: the driver interface still bridges through legacy type locations for compatibility
- technical debt: status and frame models are still split between legacy model paths and new platform-common placeholders
- risk: unsupported camera features still require broader hardware coverage
