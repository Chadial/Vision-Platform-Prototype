# WP66 Recording Timestamp Anchor Alignment

## Purpose

Tighten recording-side timing semantics so each recording session has one explicit first-frame camera/system anchor while still preserving per-image timestamps for later lag analysis.

## Closure lane

- Usable Camera Subsystem / Pre-Product Baseline

## Slice role

- bounded logging and traceability semantics hardening

## Scope level

- one narrow recording/snapshot timestamp policy alignment slice

## Branch

- intended branch: `feature/recording-timestamp-anchor-alignment`
- activation state: landed

## Scope

Included:

- preserve `camera_timestamp` and `system_timestamp_utc` for every saved recording frame
- store the first accepted recording-frame camera/system timestamps as one explicit session anchor
- write that first-frame anchor into recording-side logs
- keep snapshot timing semantics explicit and per-artifact

Excluded:

- clock-drift correction math
- offline synchronization tooling
- transport/API redesign
- detached runtime services

## Validation

- recording logs contain per-frame camera/system timestamps as before
- recording logs additionally contain first-frame camera/system anchor metadata
- traceability/run metadata keeps enough timing context to reconstruct first-frame alignment later
- local validation passed with `.\.venv\Scripts\python.exe -m unittest tests.test_recording_service tests.test_snapshot_service`
