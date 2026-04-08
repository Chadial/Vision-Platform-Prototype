# WP71 Reference Scenario Validation Narrowing

## Purpose

Turn the official reference scenarios into one small repeatable validation block that a fresh agent can run without reconstructing which tests or launch paths matter most.

## Branch

- intended narrow branch: `feature/reference-scenario-validation-narrowing`
- current planning context: `refactor/move-control-and-imaging-implementation`

## Scope

In scope:

- identify the current code and test entry points for snapshot, bounded recording, and interval capture
- tighten one small validation block around those three official reference scenarios
- prefer existing controller, bootstrap, CLI, or service seams rather than inventing new runtime surfaces
- update central docs so the reference-scenario validation path is easy to find and reuse

Out of scope:

- broad wx-shell usability work
- broad host transport or API expansion
- new hardware revalidation beyond existing trigger-based guidance
- larger namespace migration or compatibility-shim removal beyond `WP70`

## Session Goal

Leave the repository with one explicit, small, repeatable validation path for the three official reference scenarios:

- snapshot
- bounded recording
- interval capture

## Status

Landed on the current topic branch.

## Sub-Packages

1. scenario inventory and seam selection
2. targeted validation implementation or consolidation
3. central-doc update for the verified validation block

## Open Questions

- should the final validation block be test-only, launcher-assisted, or one narrow combination?
- which existing tests already cover enough of the reference scenarios to avoid adding redundant coverage?
- should the preferred entry path live at the controller layer, CLI layer, or mixed seam if that best matches current usage?

## Learned Constraints

- the current priorities already treat snapshot, bounded recording, and interval capture as the official reference scenarios
- the repository should prefer small slice-specific validation over only broad regression runs
- hardware availability is conditional, so the default validation path should remain simulator-first unless hardware is explicitly attached

## Execution Plan

1. inspect the existing tests, launchers, and command/controller seams that already exercise the three reference scenarios
2. choose the smallest coherent validation block that covers all three without introducing duplicate test logic
3. implement or tighten that validation block
4. run the targeted validation
5. update `docs/STATUS.md` and `docs/WORKPACKAGES.md` with the new verified path

## Outcome

- added `tests/test_reference_scenarios.py` as the explicit three-flow reference-scenario validation suite
- added `scripts/launchers/run_reference_scenario_validation.py` as the dedicated wrapper for that suite
- verified the path with `.\.venv\Scripts\python.exe .\scripts\launchers\run_reference_scenario_validation.py`

## Validation

- run the new or consolidated targeted validation block for snapshot, bounded recording, and interval capture
- if the implementation chooses tests, run them with `.\.venv\Scripts\python.exe`
- if the implementation chooses a launcher-assisted smoke path, keep it simulator-first unless hardware is explicitly available

## Documentation Updates

- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- operational docs only if the preferred validated path changes meaningfully

## Expected Commit Shape

One narrow validation/doc slice is preferred.

If the work naturally splits:

1. targeted validation change
2. central doc update

## Merge Gate

- one small repeatable validation path exists for all three official reference scenarios
- the path is documented in the central status/work-package docs
- no broader UI, transport, or migration scope is pulled in

## Recovery Note

Resume with:

1. `AGENTS.md`
2. `docs/SESSION_START.md`
3. `docs/MODULE_INDEX.md`
4. `docs/STATUS.md`
5. `docs/WORKPACKAGES.md`
6. this file
