# WP78 Compatibility Shim Usage Inventory

## Purpose

Record where the remaining `camera_app` compatibility imports are still exercised so later retirement work can target real usage instead of assumptions.

## Branch

- intended narrow branch: `docs/compatibility-shim-usage-inventory`
- derive an implementation branch only if the inventory turns into code changes

## Scope

In scope:

- inventory remaining compatibility shims under `src/camera_app`
- identify direct tests, scripts, or modules that still rely on those shims
- classify each seam as active compatibility need, likely removable later, or unclear

Out of scope:

- broad shim removal
- physical namespace migration beyond inventory/audit work
- changing importer code unless a tiny corrective clarification is unavoidable

## Session Goal

Leave the repository with a concrete map of remaining compatibility-shim usage and a defensible later-retirement starting point.

## Status

Prepared only. Do not activate until selected.

## Sub-Packages

1. enumerate remaining compatibility shim files
2. find repo-local usages and test coverage
3. classify each seam for later keep/remove decisions

## Open Questions

- should the inventory live only in the session file, or should the landed result also update a central/module doc?
- are there compatibility imports used only by tests, or also by active runtime entry points?
- do any remaining shims hide deeper ownership confusion that should become a later code WP rather than a doc note?

## Learned Constraints

- `WP70` already removed duplicate control/imaging implementations and left package-level shims intentionally in place
- the next compatibility step should be evidence-based, not another broad migration push
- central status and queue ownership should remain in `docs/STATUS.md` and `docs/WORKPACKAGES.md`

## Execution Plan

1. enumerate remaining `camera_app` compatibility shim modules
2. inspect repo-local imports, tests, and launcher usage against those seams
3. classify each seam by current usage and likely retirement difficulty
4. record the findings in the smallest durable doc set
5. update central docs only if the inventory materially changes package ordering or residual interpretation

## Validation

- repo-local usage search and direct file inspection
- targeted test reruns only if the inventory uncovers a seam that needs immediate correction

## Documentation Updates

- likely this session work-package file first
- `docs/STATUS.md` and `docs/WORKPACKAGES.md` only if the package lands and changes the residual interpretation

## Expected Commit Shape

One inventory/doc commit is preferred.

## Merge Gate

- remaining compatibility shims are listed with real observed repo-local usage
- each seam has at least a preliminary keep/remove/unclear classification
- no broad migration churn is introduced

## Recovery Note

Resume with:

1. `AGENTS.md`
2. `docs/SESSION_START.md`
3. `docs/MODULE_INDEX.md`
4. `docs/STATUS.md`
5. `docs/WORKPACKAGES.md`
6. `docs/archive/session_workpackages/wp70_control_and_imaging_compatibility_cleanup.md`
7. this file
