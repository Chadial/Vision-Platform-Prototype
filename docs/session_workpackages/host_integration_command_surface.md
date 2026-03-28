# Host Integration Command Surface

## Purpose

This work package defines the first focused follow-up after the initial camera CLI baseline.

Its purpose is to harden the shared host-neutral command surface so later C# embedding, desktop integration, and external adapters can reuse one clearer control contract instead of reverse-engineering CLI-oriented behavior.

## Branch

- intended branch: `feature/host-integration-command-surface`
- predecessor branch: `feature/camera-cli`
- activation state: ready after the CLI baseline is documented as intentionally narrow and stable

## Scope

Included:

- tighten the shared `CommandController` surface as the primary host-facing application layer
- clarify which request, result, and status shapes are intended for host use versus local CLI summary output
- identify one small implementation slice that improves host-visible command clarity without creating a transport layer
- keep changes simulator-verifiable
- document how CLI and future API work should consume the same command/application path

Excluded:

- new API/feed transport work
- OpenCV preview or viewport work
- broad ROI or analysis feature expansion
- large refactors outside the control/application boundary
- hardware-only validation requirements that cannot be rerun locally

## Session Goal

Leave the repository with one clearer host-integration-ready command slice that is:

- explicit about its request and status contracts
- independent from CLI presentation choices
- covered by targeted tests
- documented as the preferred control path for later adapters

## Candidate Slice

Preferred first slice:

- make one explicit typed command result path for host-facing command outcomes where the controller currently returns `None` or service-native values directly

Good targets:

- save-directory application result
- snapshot command result
- recording start/stop result
- interval-capture start/stop result

Selection rule:

- choose the smallest slice that improves host clarity without forcing a transport/API envelope too early

Current implemented slice:

- `CommandController.set_save_directory(...)` now returns a typed `SetSaveDirectoryResult`
- the result makes the selected directory versus an explicit clear operation visible without requiring hosts to infer state changes indirectly
- the CLI continues to consume the same shared controller path and now uses that typed result instead of re-resolving the path on its own
- `CommandController.save_snapshot(...)` now also returns a typed `SaveSnapshotResult`
- the result keeps the saved-path outcome explicit at the host-facing control layer instead of leaking a raw service return value upward

## Execution Plan

1. Re-read `docs/STATUS.md`, `docs/ROADMAP.md`, `docs/GlobalRoadmap.md`, and `docs/NEXT_SESSION_ORDER.md`.
2. Re-read `docs/git_strategy.md` before changing repository state.
3. Inspect `src/vision_platform/control/command_controller.py` and its tests to identify the narrowest host-facing ambiguity.
4. Choose one explicit contract improvement that stays below API/transport scope.
5. Implement the change in the shared control/application layer, not in the CLI adapter.
6. Update or extend targeted tests first around controller-visible behavior.
7. Confirm the CLI still remains a thin adapter over that shared path.
8. Update permanent docs after the behavior is real.

## Validation

Minimum:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_command_controller tests.test_bootstrap
```

If CLI-visible behavior changes indirectly:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_command_controller tests.test_bootstrap tests.test_camera_cli
```

## Documentation Updates

Before this work package is considered complete, update:

- `docs/STATUS.md`
- `docs/NEXT_SESSION_ORDER.md`
- any affected module `STATUS.md` / `ROADMAP.md`
- `services/api_service/STATUS.md` or `services/api_service/ROADMAP.md` if the API module's dependency on the host-neutral control layer becomes clearer

## Expected Commit Shape

1. `feat: harden host command surface baseline`
2. `test: cover host command surface contract`
3. `docs: update host integration workpackage status`

## Merge Gate

- the shared control/application layer is clearer for host use than before
- CLI remains an adapter rather than a second business-logic path
- no API transport layer is introduced prematurely
- touched tests pass locally
- docs clearly explain the next follow-up step

## Recovery Note

To resume this work:

1. Read `Agents.md`
2. Read `docs/SESSION_START.md`
3. Read `docs/MODULE_INDEX.md`
4. Read `docs/NEXT_SESSION_ORDER.md`
5. Read `docs/STATUS.md`
6. Read this file
7. Inspect `src/vision_platform/control/command_controller.py`
8. Inspect `tests/test_command_controller.py`
