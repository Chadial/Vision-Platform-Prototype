# Status

- maturity: active core module
- implemented: snapshot saving, snapshot-side focus capture, interval capture, recording queue, frame writer, deterministic naming
- implemented: dependency-free visible frame output now covers `.png` and `.bmp` for `Mono8`, `Rgb8`, and `Bgr8`, while higher-bit grayscale `.png`/`.tiff` still use the optional OpenCV path
- implemented: snapshot save and bounded recording now both write into one folder-local appendable traceability log that reuses the same file when stable context still matches and starts a new run block when only run/session fields differ
- implemented: the shared traceability row shape now also supports optional per-image analysis ROI and focus metadata without turning those artifact-level fields into stable-header identity
- implemented: the shared traceability helper now also exposes a narrow reader path for later offline metadata consumption over one folder's traceability logs
- implemented: focus summary metadata now requires an explicit aggregation-basis field in the shared traceability row shape when summary fields are stored, so `focus_value_mean` and `focus_value_stddev` are no longer ambiguous standalone artifact values
- implemented: snapshot and bounded-recording save flows now support an explicit reusable focus-metadata producer path, and bootstrap composition can opt into that producer wiring
- working now: simulator-backed snapshot/recording/interval flows and root smoke scripts
- working now: bounded recording can now complete, start again, and recover on the same service path after a selected writer-side failure without requiring a process restart, backed by targeted simulator-first tests
- working now: snapshot-side focus evaluation can reuse the shared ROI state path without moving ROI ownership into snapshot save logic
- partial: trigger-based recording and full hardware validation are still open
- partial: producer wiring is now available, but focus metadata emission still depends on explicit service/bootstrap configuration rather than a repository-wide mandatory default
- partial: exact defaults, bounds, and later validation policy for focus-summary aggregation are still open and remain follow-up work beyond the current explicit artifact-metadata shape
- partial: broader data/logging closure work such as richer metadata consumption, wider artifact/linkage coverage, and series-structure refinement is still open beyond the current traceability baseline
- known issues: recording flow still lives largely in `src/camera_app/services`, but naming and frame writing now live behind `src/vision_platform/services/recording_service`
- technical debt: `camera_app.storage` is now a compatibility shim and should eventually stop being the primary import surface
- risk: high-frame-rate hardware scenarios still need measurement under load
