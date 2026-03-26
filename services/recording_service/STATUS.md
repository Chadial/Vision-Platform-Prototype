# Status

- maturity: active core module
- implemented: snapshot saving, interval capture, recording queue, frame writer, deterministic naming
- working now: simulator-backed snapshot/recording/interval flows and root smoke scripts
- partial: trigger-based recording and full hardware validation are still open
- known issues: implementation remains split between `src/camera_app/services` and `src/camera_app/storage`
- technical debt: app/service boundaries are clearer in docs than in the current code layout
- risk: high-frame-rate hardware scenarios still need measurement under load
