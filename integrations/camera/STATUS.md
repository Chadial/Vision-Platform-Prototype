# Status

- maturity: active core module
- implemented: `CameraDriver`, `SimulatedCameraDriver`, `VimbaXCameraDriver`
- working now: simulator-backed initialization, configuration, and frame capture
- working now: targeted real-hardware initialization, snapshot, and preview runs have been verified locally through the Vimba X path
- working now: the current real-hardware path now also exposes capability probing through the already opened Vimba camera, avoiding an immediate second Vimba/camera open during `CameraService.initialize()`
- working now: the current startup-warning interpretation is narrower; successful serial March 30 `status` and `snapshot(.bmp)` proofs on `DEV_1AB22C046D81` still emitted `VmbError.NotAvailable: -30`, but the repository status surface kept `capabilities_available=True` and `capability_probe_error=None`, so the current evidence classifies that line as non-blocking SDK/logging residual rather than active startup failure
- working now: the current hardware-selection path also resolves duplicate SDK-visible entries for the tested camera id by preferring the richer identity candidate and preserving pre-open identity fields for host-visible status when the opened camera object degrades fields such as `camera_serial` to `N/A`
- partial: broader repeated real-camera validation is still open beyond the narrowed WP27 serial reuse proof
- residual: raw Vimba X enumeration on `DEV_1AB22C046D81` still shows duplicate SDK-visible entries, and successful startup may still emit `VmbError.NotAvailable: -30` as non-blocking SDK/logging noise
- known issues: the driver interface still bridges through legacy type locations for compatibility
- technical debt: status and frame models are still split between legacy model paths and new platform-common placeholders
- risk: unsupported camera features still require broader hardware coverage
