# Status

- maturity: active core module
- implemented: snapshot saving, snapshot-side focus capture, interval capture, recording queue, frame writer, deterministic naming
- implemented: dependency-free visible frame output now covers `.png` and `.bmp` for `Mono8`, `Rgb8`, and `Bgr8`, while higher-bit grayscale `.png`/`.tiff` still use the optional OpenCV path
- working now: simulator-backed snapshot/recording/interval flows and root smoke scripts
- working now: bounded recording can now complete, start again, and recover on the same service path after a selected writer-side failure without requiring a process restart, backed by targeted simulator-first tests
- working now: snapshot-side focus evaluation can reuse the shared ROI state path without moving ROI ownership into snapshot save logic
- partial: trigger-based recording and full hardware validation are still open
- partial: broader data/logging closure work such as metadata schema, richer timestamp surfacing, and series-structure refinement is still open beyond the first visible-format slice
- known issues: recording flow still lives largely in `src/camera_app/services`, but naming and frame writing now live behind `src/vision_platform/services/recording_service`
- technical debt: `camera_app.storage` is now a compatibility shim and should eventually stop being the primary import surface
- risk: high-frame-rate hardware scenarios still need measurement under load
