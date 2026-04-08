# WP75 Reference Scenario Operator Path Tightening

## Purpose

Make the now-validated reference scenarios easier to discover and run through one compact operator-facing path instead of requiring cross-reading across status, launch, and test docs.

## Branch

- intended narrow branch: `docs/reference-scenario-operator-path-tightening`
- derive a feature branch only when this package is actually selected for implementation

## Scope

In scope:

- document one small operator/developer path for running the validated reference scenarios
- keep that path aligned with the existing `WP71` launcher and test-backed validation block
- update only the central operational docs directly needed for discoverability

Out of scope:

- new scenario logic
- new validation coverage beyond `WP71`
- broader manual or runbook rewrite
- hardware-specific operator guidance unless required by the selected path

## Session Goal

Leave the repository with one obvious, low-friction place where a fresh agent or operator can find and run the official reference-scenario path.

## Status

Landed on the current topic branch.

## Sub-Packages

1. choose the single best operator-facing home for the reference-scenario path
2. tighten wording and examples around the validated launcher command
3. verify that the resulting path is discoverable from the central docs

## Open Questions

- should the primary home be `docs/ENTRYPOINT_AND_LAUNCH_BASELINE.md`, `docs/MANUALS_INDEX.md`, or a narrower central note?
- should the preferred path mention only the launcher, or also the underlying test module?
- does the current `WP71` command need one short explanation of what it covers?

## Learned Constraints

- `WP71` already established the validation block and should not be reopened into broader testing work
- the repository now treats official reference scenarios as confidence anchors
- central status and queue ownership must remain in `docs/STATUS.md` and `docs/WORKPACKAGES.md`

## Execution Plan

1. inspect the current central launch/manual docs for the best placement of the reference-scenario path
2. choose one compact operator-facing entry location
3. document the launcher command and its intended scenario coverage
4. update the smallest necessary central docs
5. verify that a fresh reader can find the path without reconstructing it from multiple sources

## Outcome

- added one explicit `Reference Scenario Quick Path` section to `docs/ENTRYPOINT_AND_LAUNCH_BASELINE.md`
- indexed that validated quick path in `docs/MANUALS_INDEX.md`
- revalidated the quick path with `.\.venv\Scripts\python.exe .\scripts\launchers\run_reference_scenario_validation.py`

## Validation

- manual doc-read verification from `docs/SESSION_START.md` or `docs/MANUALS_INDEX.md`
- optionally rerun `.\.venv\Scripts\python.exe .\scripts\launchers\run_reference_scenario_validation.py` if wording or ownership changes imply a recheck

## Documentation Updates

- likely `docs/ENTRYPOINT_AND_LAUNCH_BASELINE.md`
- possibly `docs/MANUALS_INDEX.md`
- `docs/STATUS.md` and `docs/WORKPACKAGES.md` only if package state changes

## Expected Commit Shape

One doc-only commit is preferred.

## Merge Gate

- one small operator-facing path clearly points to the validated reference-scenario command
- no second planning system or duplicated status ownership is introduced
- the path stays aligned with `WP71`

## Recovery Note

Resume with:

1. `AGENTS.md`
2. `docs/SESSION_START.md`
3. `docs/MODULE_INDEX.md`
4. `docs/STATUS.md`
5. `docs/WORKPACKAGES.md`
6. this file
