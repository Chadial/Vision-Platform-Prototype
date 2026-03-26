# Status

- maturity: active core module
- implemented: preview buffering, shared acquisition, stream orchestration, preview-adjacent focus consumption
- working now: simulator-backed preview and preview-plus-recording sharing, plus focus-state derivation from preview frames
- partial: no dedicated platform-owned UI adapter yet
- known issues: `IntervalCaptureService` and parts of the recording-side implementation still reside in `src/camera_app/services`
- technical debt: analysis consumers are not yet plugged into the shared frame source
- risk: real-hardware preview timing still needs broader validation
