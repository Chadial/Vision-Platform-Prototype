# WP68 Unified Artifact Recording Log Append Baseline

## Purpose

Use one deterministic `recording_log.csv` per save directory as the shared append base for both snapshots and recording runs so saved image names and timestamps remain available for append/resume continuity.

## Closure lane

- Usable Camera Subsystem / Pre-Product Baseline

## Slice role

- bounded artifact-log continuation baseline

## Scope level

- one narrow logging-policy slice after the per-image timestamp anchor alignment

## Branch

- intended branch: `feature/recording-log-unified-append`
- activation state: prepared

## Scope

Included:

- create `recording_log.csv` automatically when the first snapshot or recording frame is saved in a directory
- append snapshot rows and recording rows into the same directory-scoped recording log
- preserve the existing image-name and timestamp columns for append/resume use
- keep traceability logs separate from the operational recording log

Excluded:

- traceability schema redesign
- database storage
- host/API transport changes
- UI redesign

## Validation

- snapshot-only save creates `recording_log.csv`
- subsequent recording appends to the same `recording_log.csv`
- repeated recording sessions do not create stem-suffixed recording-log files
- local unit tests cover the unified recording-log path
