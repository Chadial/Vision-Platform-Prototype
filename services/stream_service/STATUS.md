# Status

- maturity: active core module
- implemented: preview buffering, shared acquisition, stream orchestration, preview-adjacent focus consumption, and a small shared ROI state path
- working now: simulator-backed preview and preview-plus-recording sharing, plus focus-state derivation from preview frames through `FocusPreviewService` and `CameraStreamService`
- working now: `RoiStateService` can hold one active ROI selection so preview-adjacent consumers can reuse it without moving ROI ownership into UI or stream internals
- partial: no dedicated platform-owned UI adapter yet
- known issues: `IntervalCaptureService` and parts of the recording-side implementation still reside in `src/camera_app/services`
- technical debt: analysis consumers are not yet plugged into the shared frame source beyond preview-pulled refresh behavior
- risk: real-hardware preview timing still needs broader validation
