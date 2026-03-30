# Offline Stable Context Exposure

## Purpose

This work package defines the next execution-ready extension slice after the landed `WP20` focus-metadata policy hardening step.

Its purpose is to move the offline focus-report path from "per-image artifact metadata can be joined" toward "the compact offline report can also surface one narrow folder-level stable-context summary from the same traceability baseline."

The narrow goal is to expose stable traceability-header context in the offline report without turning the postprocess tool into a run/session explorer, report framework, or broader offline workstation.

## Branch

- intended branch: `feature/offline-stable-context-exposure`
- activation state: current next execution-ready package after landed `WP20`

## Scope

Included:

- extend the thin offline focus-report path with one additive stable-context exposure surface above the existing traceability reader
- keep the existing per-image report entry path compatible
- expose one compact folder-level summary from the stable traceability header when available
- keep behavior graceful when no traceability log exists
- add focused tests for context presence and absence
- update docs to mark the offline report as context-aware at both per-image and folder-stable-context level

Selected slice for this package:

- add one additive offline report bundle that can expose, where available:
  - `record_kind`
  - `camera_id`
  - `pixel_format`
  - `exposure_time_us`
  - `gain`
  - ROI context fields already present in the stable traceability header
- keep the current `run_focus_report(...) -> list[...]` path usable for existing callers
- make the CLI use the richer bundle formatting path

Excluded:

- run/session browsing
- per-run history display
- metadata filtering or querying
- broader export changes
- UI or API work
- new offline analytics beyond the current focus-report path

## Session Goal

Leave the repository with one explicit proof that offline reporting can reuse both per-image artifact metadata and one narrow folder-level stable context from the same traceability source, while staying compact.

## Validation

Required automated validation:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_postprocess_tool tests.test_snapshot_service
```
