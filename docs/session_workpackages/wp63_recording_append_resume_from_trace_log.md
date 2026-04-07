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
- activation state: current next

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

## Headless Follow-Up Note

- this slice should stay compatible with the later headless-kernel direction
- append/resume behavior must be implemented against shared recording/artifact semantics rather than against wx-specific UI state
- the later host-neutral command/session work should be able to reuse the same append/resume rules without depending on the current wx-shell session bridge
