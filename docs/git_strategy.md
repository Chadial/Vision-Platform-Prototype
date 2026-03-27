# Git Strategy

## Purpose

This repository now follows a strict trunk-based workflow with short-lived branches. The goal is to keep `main` stable while making the migration from `camera_app` to the modular platform structure reviewable and reversible in small steps.

## Branch Rules

- `main` is the integration branch and should remain stable.
- Substantive work happens on short-lived branches only.
- One branch covers one coherent work package.
- Do not mix unrelated concerns in one branch.

## Branch Naming

Use one of these prefixes:

- `feature/`
- `fix/`
- `refactor/`
- `docs/`
- `test/`
- `chore/`

Examples:

- `refactor/platform-model-facades`
- `test/migrate-vision-platform-imports`
- `feature/focus-core-baseline`
- `fix/recording-stop-cleanup`
- `docs/reorg-status-sync`

## Required Scope Separation

Keep these concerns separate whenever possible:

- repository reorganization
- behavioral or runtime changes
- tests
- documentation
- hardware-specific integration changes

Good:

- one branch for import-surface migration
- one branch for ROI foundation
- one branch for real-hardware validation notes

Bad:

- one branch containing namespace migration, new ROI behavior, unrelated README rewrites, and formatting churn

## Commit Rules

Commits must be:

- small
- logically ordered
- reviewable without reconstructing the entire repository history

Preferred commit types:

- `feat:`
- `fix:`
- `refactor:`
- `test:`
- `docs:`
- `chore:`

Recommended format:

```text
<type>: <scope> <intent>
```

Examples:

- `refactor: expose control layer through vision_platform`
- `test: migrate command controller coverage to platform namespace`
- `docs: record repository git workflow`

## Expected Branch Flow

For a normal work package:

1. create branch from current `main`
2. implement one coherent change set
3. add or update tests for the touched scope
4. update docs if status, structure, or roadmap changed
5. run local validation
6. merge only when the branch is internally consistent
7. delete the local topic branch after merge unless there is a deliberate short-term reason to keep it

## Required Validation Before Merge

At minimum, run the relevant local checks for the touched scope.

Examples:

- namespace or service migration:
  - `.\.venv\Scripts\python.exe -m unittest`
- documentation-only branch:
  - verify linked paths and referenced commands still match the repository
- hardware-related branch:
  - document clearly whether validation is simulator-only or hardware-backed

## Rules For This Repository Specifically

- do not commit direct work on `main` except for trivial emergency fixes
- do not bundle module reorganization and new functional analysis features in one branch
- do not bundle broad rename churn without the corresponding tests
- use `docs/branch_backlog.md` to assign remaining worktree changes to future branches before committing mixed repository states
- when architecture changes touch module boundaries, update:
  - `docs/MODULE_INDEX.md`
  - relevant module `STATUS.md`
  - relevant module `ROADMAP.md`
  - `docs/STATUS.md` when roadmap position changed
- periodically check which local branches are already merged into `main` and delete them before they become stale context
- if an old branch is clearly obsolete because the repository has moved on structurally or functionally, delete it explicitly rather than treating it as still-actionable work

## Recommended Next Branches

Based on the current repository state, the next sensible branch scopes are:

- `refactor/move-control-and-imaging-implementation`
- `refactor/move-storage-implementation`
- `feature/focus-core-baseline`
- `docs/module-roadmap-tightening`

## Immediate Execution Plan

### Branch 1

Name:

- `refactor/move-control-and-imaging-implementation`

Goal:

- physically move the control and imaging implementation behind the already established `vision_platform` module boundary
- keep the public platform import surface stable
- preserve the current test behavior

Scope Included:

- `src/camera_app/control`
- `src/camera_app/imaging`
- corresponding `vision_platform` facades
- affected imports
- affected tests
- affected module docs and status notes

Scope Excluded:

- storage migration
- recording-service internals unrelated to moved imports
- ROI/focus feature work
- unrelated README cleanup

### Required Commit Sequence

Commit 1:

- `refactor: move control implementation behind vision_platform`
- move or re-home `CommandController` implementation
- keep compatibility imports working

Commit 2:

- `refactor: move imaging implementation behind vision_platform`
- move or re-home OpenCV adapter and preview wrapper
- keep compatibility imports working

Commit 3:

- `test: align control and imaging tests with moved implementation`
- update or extend tests for the physical move

Commit 4:

- `docs: update module status after control and imaging move`
- update affected `STATUS.md`, `ROADMAP.md`, and `docs/STATUS.md` if roadmap position changes

### Required Validation For Branch 1

Run at minimum:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_command_controller tests.test_opencv_adapter tests.test_opencv_preview tests.test_opencv_smoke_demos tests.test_bootstrap
```

Preferred full validation before merge:

```powershell
.\.venv\Scripts\python.exe -m unittest
```

### Merge Gate For Branch 1

Do not merge unless all of the following are true:

- compatibility imports still work
- touched tests pass
- no unrelated service or storage changes are bundled
- affected docs are updated
- repository remains runnable through the existing root scripts

### Branch 2

Name:

- `refactor/move-storage-implementation`

Required commit sequence:

1. `refactor: move file naming implementation behind vision_platform`
2. `refactor: move frame writer implementation behind vision_platform`
3. `test: align storage tests with moved implementation`
4. `docs: update recording module status after storage move`

Validation focus:

- `tests.test_file_naming`
- `tests.test_frame_writer`
- `tests.test_snapshot_service`
- `tests.test_recording_service`
- `tests.test_interval_capture_service`

### Branch 3

Name:

- `feature/focus-core-baseline`

Required commit sequence:

1. `feat: add baseline focus evaluator contract`
2. `feat: implement first simulator-backed focus metric`
3. `test: add focus core coverage`
4. `docs: update focus module roadmap and status`
