# WP98 Vision Platform Namespace Boundary Alignment

## Goal

Narrow the remaining namespace-boundary drift still surfaced by `tests.test_vision_platform_namespace` without reopening the broader camera-integration fore-stage or forcing a wide physical migration.

## Why This Exists Now

`WP94` through `WP97` completed the intended camera-integration fore-stage slice and passed their focused validation set. One broader residual remains outside that fore-stage: the repository still has namespace-boundary cases that are visible in `tests.test_vision_platform_namespace`.

This package exists so that the remaining namespace behavior is treated as one explicit, narrow follow-up slice instead of remaining an unnamed background defect.

## Scope

- inspect the currently failing namespace-test cases
- classify each failing path as one of:
  - stale drift that should be aligned now
  - accepted compatibility seam that should stay explicit
  - policy exception that should be documented and tested deliberately
- apply the narrowest justified fix or documentation/test adjustment per case
- keep the preferred `vision_platform` namespace readable without forcing a broad package move or historical cleanup wave

## Explicitly Out Of Scope

- broad physical relocation of remaining `camera_app` modules
- reopening the completed `WP93` through `WP97` camera-integration slices
- large package-renaming campaigns
- end-state namespace purity work
- unrelated API or UI cleanup

## Affected Areas

- `tests/test_vision_platform_namespace.py`
- `src/vision_platform/...`
- any still-referenced compatibility seams under `src/camera_app/...`
- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`

## Current Situation

- the camera-integration fore-stage (`WP93` through `WP97`) is now implemented and locally validated
- the focused validation suite for that slice is green
- the broader namespace validation still exposes residual drift outside the implemented fore-stage

## Expected Output

- one explicit inventory of the remaining namespace-boundary failures
- one narrow decision per failure: align, keep-as-explicit-compatibility, or document-as-exception
- the smallest justified code/doc/test change set that makes the namespace boundary more intentional

## Validation

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_vision_platform_namespace
```

## Done Criteria

- the remaining namespace-boundary cases are no longer implicit
- every still-allowed compatibility seam is explicit in code, tests, or docs
- no broad migration is performed just to make the test superficially green

## Recommended Branch

`refactor/wp98-vision-platform-namespace-boundary-alignment`

## How This Pays Into The Repository

This package isolates the remaining namespace-governance residual from the completed camera-integration fore-stage. That keeps the repo honest about the known gap without falsely implying that the fore-stage itself is still incomplete.
