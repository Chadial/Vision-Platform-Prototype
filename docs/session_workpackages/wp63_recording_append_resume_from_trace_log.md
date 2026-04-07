# WP63 Recording Append / Resume From Trace Log

## Purpose

Stop bounded recording and snapshot flows from overwriting prior outputs in reused save directories, and derive the next file index from the existing trace/log context instead of restarting from fixed stems.

## Closure lane

- Usable Camera Subsystem / Pre-Product Baseline

## Slice role

- bounded recording artifact continuity baseline

## Scope level

- one bounded append/resume path for reused save directories

## Branch

- intended branch: `feature/recording-append-resume`
- activation state: landed

## Scope

Included:

- append-safe naming when recording into an already used target directory
- reuse the existing traceability/log surface to determine the next sequence position
- make the wx shell and shared controller reflect reused-directory progress more honestly
- preserve deterministic naming without silently overwriting prior artifacts

Excluded:

- broad run browser UI
- history explorer
- cross-machine coordination
- new transport or daemon work

## Validation

- start two bounded recordings into the same target directory and confirm that the second run continues numbering instead of overwriting
- verify that the visible progress can later support `n/n` semantics for append-mode runs

## Implementation Status

Landed on `feature/recording-append-resume` with:

- append/resume-safe snapshot path resolution (`snapshot`, `snapshot_000001`, ...)
- append/resume-safe recording frame indexing across repeated runs in the same directory and stem
- historical note: this slice originally kept first-run compatibility while suffixing continuation logs (`..._recording_log.csv`, then `..._recording_log_000002.csv`, ...); `WP67` later replaced that with one append-only deterministic recording log per `save_directory + file_stem`
- additive recording metadata fields for continuation visibility (`continues_previous_series`, `recording_start_frame_index`)

Validated with:

- `.\.venv\Scripts\python.exe -m unittest tests.test_file_naming tests.test_snapshot_service tests.test_recording_service`

## Headless Follow-Up Note

- this slice should stay compatible with the later headless-kernel direction
- append/resume behavior must be implemented against shared recording/artifact semantics rather than against wx-specific UI state
- the later host-neutral command/session work should be able to reuse the same append/resume rules without depending on the current wx-shell session bridge
