# Status

- maturity: active core module
- implemented: snapshot saving, interval capture, recording queue, frame writer, deterministic naming
- working now: simulator-backed snapshot/recording/interval flows and root smoke scripts
- partial: trigger-based recording and full hardware validation are still open
- known issues: recording flow still lives largely in `src/camera_app/services`, but naming and frame writing now live behind `src/vision_platform/services/recording_service`
- technical debt: `camera_app.storage` is now a compatibility shim and should eventually stop being the primary import surface
- risk: high-frame-rate hardware scenarios still need measurement under load
