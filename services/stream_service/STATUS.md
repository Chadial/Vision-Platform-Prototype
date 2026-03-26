# Status

- maturity: active core module
- implemented: preview buffering, shared acquisition, stream orchestration
- working now: simulator-backed preview and preview-plus-recording sharing
- partial: no dedicated platform-owned UI adapter yet
- known issues: code still resides in `src/camera_app/services`
- technical debt: analysis consumers are not yet plugged into the shared frame source
- risk: real-hardware preview timing still needs broader validation
