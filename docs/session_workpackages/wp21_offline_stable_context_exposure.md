# Offline Stable Context Exposure

## Purpose

This work package defines the next execution-ready extension slice after the landed `WP20` focus-metadata policy hardening step.

Closure lane:

- offline and measurement follow-up over the existing traceability-backed saved-artifact reporting path

Slice role:

- narrow consumer-side offline reporting extension over the already existing traceability baseline

Its purpose is to move the offline focus-report path from "per-image artifact metadata can be joined" toward "the compact offline report can also surface one narrow folder-level stable-context summary from the same traceability baseline."

The narrow goal is to consume existing stable traceability-header context in the offline report without producing any new traceability structure and without turning the postprocess tool into a run/session explorer, report framework, or broader offline workstation.

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

- per-image artifact metadata already exists from the earlier offline metadata-consumption slice
- this package adds one separate narrow folder-level stable-context exposure layer above that existing per-image path
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
- general artifact browsing
- broader export changes
- UI or API work
- new offline analytics beyond the current focus-report path

What this package does not close:

- broader run/session exploration
- general metadata query behavior
- broader report-framework or export redesign
- any producer-side traceability redesign

## Session Goal

Leave the repository with one explicit proof that offline reporting can reuse both per-image artifact metadata and one narrow folder-level stable context from the same traceability source, while staying compact.

## Current Context

The repository already has:

- a shared folder-local traceability baseline from the earlier data/logging slices
- offline per-image artifact-metadata consumption from the earlier offline metadata-consumer slice
- one compact text-oriented focus-report path over stored artifacts

The immediate remaining gap is:

- the offline report can already consume per-image artifact metadata, but it does not yet expose one separate compact stable-context summary from the same traceability header level

## Narrow Decisions

- this package is consumer-side only and does not create new traceability structure
- this package distinguishes two levels explicitly:
  - per-image artifact metadata already exists
  - folder-level stable-context exposure is the new additive layer for this slice
- the added stable-context view remains compact and text-oriented
- the existing `run_focus_report(...) -> list[...]` caller path should stay usable rather than being replaced unnecessarily
- this package should not drift into run/session browsing, query-style metadata access, or a general artifact browser

## Validation

Required automated validation:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_postprocess_tool tests.test_snapshot_service
```

Manual review points:

- per-image artifact metadata remains available through the existing path
- the added stable-context view is visibly folder-level rather than per-run or per-image history
- the report shape remains compact and additive instead of replacing existing caller expectations unnecessarily
- missing traceability headers degrade cleanly without blocking offline reporting
- no run/session explorer, metadata query layer, or report-framework behavior is bundled

## Merge Gate

- the slice remains consumer-side and offline-report-focused
- no new producer-side traceability structure is introduced
- the added stable-context summary stays compact, additive, and folder-level
- the existing per-image caller path remains usable
- no run/session explorer, metadata query system, artifact browser, or broad export redesign is bundled
