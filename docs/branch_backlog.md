# Branch Backlog

## Purpose

This document assigns the currently remaining worktree changes to future branches. It exists so unfinished repository reorganization work does not drift into `main` or get mixed into unrelated feature branches.

Use this file as the operational source when deciding:

- which files belong to which next branch
- which files must explicitly stay out of a branch
- which validation block must run before merge

## Current Rule

The remaining changes in the worktree are not a candidate for one bulk commit and not a candidate for direct merge into `main`.

Everything below must be moved through coherent follow-up branches.

## Current Worktree Inventory

This inventory reflects the currently still open files after the control/imaging branch commits.

| File Or Group | Target Branch | Notes |
| --- | --- | --- |
| `AGENTS.md` | `docs/reorg-foundation-sync` | repository working rules |
| `README.md` | `docs/reorg-foundation-sync` | root orientation and structure references |
| `docs/GlobalRoadmap.md` | `docs/reorg-foundation-sync` | master roadmap sync |
| `docs/MODULE_INDEX.md` | `docs/reorg-foundation-sync` | module index |
| `docs/ROADMAP.md` | `docs/reorg-foundation-sync` | repo roadmap sync |
| `docs/project_overview.md` | `docs/reorg-foundation-sync` | new root project doc |
| `docs/target_structure.md` | `docs/reorg-foundation-sync` | target structure doc |
| `docs/migration_plan.md` | `docs/reorg-foundation-sync` | migration doc |
| `docs/architecture_principles.md` | `docs/reorg-foundation-sync` | architecture doc |
| `docs/git_strategy.md` | `docs/reorg-foundation-sync` | git workflow doc |
| `docs/branch_backlog.md` | `docs/reorg-foundation-sync` | branch assignment doc |
| `apps/desktop_app/*` | `docs/reorg-foundation-sync` | prepared module docs |
| `apps/postprocess_tool/*` | `docs/reorg-foundation-sync` | prepared module docs |
| `apps/opencv_prototype/README.md` | `docs/reorg-foundation-sync` | module doc |
| `apps/opencv_prototype/ROADMAP.md` | `docs/reorg-foundation-sync` | module doc |
| `integrations/**/*` | `docs/reorg-foundation-sync` | module docs only in repo root tree |
| `libraries/**/*` | `docs/reorg-foundation-sync` | module docs only in repo root tree |
| `services/**/*` | `docs/reorg-foundation-sync` | module docs only in repo root tree |
| `docs/ProjectAgents.md` | hold / explicit decision | commit only if intentionally maintained in repo |
| `docs/ProjectDescription.md` | hold / explicit decision | commit only if intentionally maintained in repo |
| `docs/archive/StartPrompt.md` | hold / explicit decision | archived reference only; do not mix into normal refactor branches |
| `src/vision_platform/__init__.py` | `refactor/add-platform-foundation-surface` | namespace foundation |
| `src/vision_platform/bootstrap.py` | `refactor/add-platform-foundation-surface` | namespace foundation |
| `src/vision_platform/apps/**/*` | `refactor/add-platform-foundation-surface` | app facade surface |
| `src/vision_platform/integrations/**/*` | `refactor/add-platform-foundation-surface` | integration facade surface |
| `src/vision_platform/libraries/common_models/**/*` | `refactor/add-platform-foundation-surface` | common model surface |
| `src/vision_platform/libraries/roi_core/**/*` | `refactor/add-platform-foundation-surface` | ROI foundation surface |
| `src/vision_platform/libraries/focus_core/**/*` | `refactor/add-platform-foundation-surface` now, `feature/focus-core-baseline` later for behavior | scaffolding only belongs to foundation branch |
| `src/vision_platform/models/**/*` | `refactor/add-platform-foundation-surface` | model facade surface |
| `src/vision_platform/services/stream_service/camera_stream_service.py` | `refactor/add-platform-foundation-surface` | current facade only |
| `src/vision_platform/services/stream_service/preview_service.py` | `refactor/add-platform-foundation-surface` | current facade only |
| `src/vision_platform/services/stream_service/shared_frame_source.py` | `refactor/add-platform-foundation-surface` | current facade only |
| `src/vision_platform/services/stream_service/__init__.py` | `refactor/add-platform-foundation-surface` | facade package |
| `src/vision_platform/services/recording_service/camera_service.py` | `refactor/add-platform-foundation-surface` | current facade only |
| `src/vision_platform/services/recording_service/recording_service.py` | `refactor/add-platform-foundation-surface` | current facade only |
| `src/vision_platform/services/recording_service/interval_capture_service.py` | `refactor/add-platform-foundation-surface` | current facade only |
| `src/vision_platform/services/recording_service/snapshot_service.py` | `refactor/add-platform-foundation-surface` | current facade only |
| `src/vision_platform/services/recording_service/file_naming.py` | `refactor/move-storage-implementation` | storage move branch |
| `src/vision_platform/services/recording_service/frame_writer.py` | `refactor/move-storage-implementation` | storage move branch |
| `src/vision_platform/services/recording_service/__init__.py` | `refactor/move-storage-implementation` | if changed for storage move |
| `src/vision_platform/services/__init__.py` | `refactor/add-platform-foundation-surface` | package surface |
| `tests/test_vision_platform_namespace.py` | `refactor/add-platform-foundation-surface` | foundation coverage |
| `tests/test_file_naming.py` | `refactor/move-storage-implementation` | storage-related |
| `tests/test_frame_writer.py` | `refactor/move-storage-implementation` | storage-related |
| `tests/test_interval_capture_service.py` | `refactor/move-storage-implementation` | storage-facing output path coverage |
| `tests/test_recording_service.py` | `refactor/move-storage-implementation` | storage-facing recording output |
| `tests/test_snapshot_service.py` | `refactor/move-storage-implementation` | storage-facing snapshot output |
| `tests/test_camera_stream_service.py` | `refactor/move-service-import-surface` | remaining service import migration |
| `tests/test_command_flow_demo.py` | `refactor/move-service-import-surface` | remaining app/service import migration |
| `tests/test_preview_service.py` | `refactor/move-service-import-surface` | remaining service import migration |
| `tests/test_request_models.py` | `refactor/move-service-import-surface` | model-facade usage cleanup |
| `tests/test_simulated_camera_driver.py` | `refactor/move-service-import-surface` | remaining service/import cleanup |
| `tests/test_simulated_demo.py` | `refactor/move-service-import-surface` | remaining app import cleanup |
| `tests/test_snapshot_smoke.py` | `refactor/move-service-import-surface` | remaining app import cleanup |
| `tests/test_vimbax_camera_driver.py` | `refactor/move-service-import-surface` | integration import cleanup |
| `scripts/launchers/run_command_flow_demo.py` | `refactor/move-service-import-surface` | launcher script alignment |
| `scripts/launchers/run_opencv_preview_demo.py` | `refactor/move-service-import-surface` | launcher script alignment |
| `scripts/launchers/run_opencv_save_demo.py` | `refactor/move-service-import-surface` | launcher script alignment |
| `scripts/launchers/run_simulated_demo.py` | `refactor/move-service-import-surface` | launcher script alignment |
| `scripts/launchers/run_snapshot_smoke.py` | `refactor/move-service-import-surface` | launcher script alignment |

## Ignored Artifacts

The following should not be committed and are already covered by `.gitignore`:

- all `__pycache__/` directories
- all `*.pyc`, `*.pyo`, and `*.pyd` files
- local virtualenv and IDE state

## Branch A

Name:

- `refactor/move-storage-implementation`

Goal:

- move storage implementation behind `vision_platform`
- keep `camera_app.storage` as a compatibility layer only

Include:

- `src/vision_platform/services/recording_service/file_naming.py`
- `src/vision_platform/services/recording_service/frame_writer.py`
- `src/camera_app/storage/file_naming.py`
- `src/camera_app/storage/frame_writer.py`
- `tests/test_file_naming.py`
- `tests/test_frame_writer.py`
- `tests/test_snapshot_service.py`
- `tests/test_recording_service.py`
- `tests/test_interval_capture_service.py`

Exclude:

- stream-service migration beyond storage dependencies
- focus or ROI feature work
- broad root-document rewrites not required by the storage move

Expected commits:

1. `refactor: move file naming implementation behind vision_platform`
2. `refactor: move frame writer implementation behind vision_platform`
3. `test: align storage tests with moved implementation`
4. `docs: update recording module status after storage move`

Validation:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_file_naming tests.test_frame_writer tests.test_snapshot_service tests.test_recording_service tests.test_interval_capture_service
```

## Branch B

Name:

- `refactor/move-service-import-surface`

Goal:

- continue the physical migration for stream- and recording-adjacent imports where the platform namespace already exists
- reduce remaining direct reliance on `camera_app` internals

Include:

- `tests/test_camera_stream_service.py`
- `tests/test_simulated_camera_driver.py`
- `tests/test_simulated_demo.py`
- `tests/test_command_flow_demo.py`
- `tests/test_snapshot_smoke.py`
- `tests/test_vimbax_camera_driver.py`
- any directly required files under:
  - `src/vision_platform/services/`
  - `src/vision_platform/apps/`
  - `src/vision_platform/integrations/`

Exclude:

- storage implementation move
- root-level documentation sweep
- focus/ROI implementation

Expected commits:

1. `refactor: tighten service imports behind vision_platform`
2. `test: align remaining service and demo tests with platform namespace`
3. `docs: update service migration status`

Validation:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_camera_stream_service tests.test_simulated_camera_driver tests.test_simulated_demo tests.test_command_flow_demo tests.test_snapshot_smoke tests.test_vimbax_camera_driver
```

## Branch C

Name:

- `docs/reorg-foundation-sync`

Goal:

- commit the repository-structure and roadmap documentation that should have been isolated from code refactors

Include:

- `AGENTS.md`
- `README.md`
- `docs/GlobalRoadmap.md`
- `docs/ROADMAP.md`
- `docs/project_overview.md`
- `docs/target_structure.md`
- `docs/migration_plan.md`
- `docs/architecture_principles.md`
- `docs/git_strategy.md`
- `docs/MODULE_INDEX.md`
- module-doc folders under:
  - `apps/`
  - `integrations/`
  - `services/`
  - `libraries/`

Review carefully before inclusion:

- `docs/ProjectAgents.md`
- `docs/ProjectDescription.md`
- `docs/archive/StartPrompt.md`

These three files appear in the current worktree but are not normal implementation outputs. They should only be committed if they are intentionally meant to live in the repository as maintained source documents.

Exclude:

- service/runtime refactors
- storage implementation changes
- focus feature code

Expected commits:

1. `docs: add repository reorganization overview and target structure`
2. `docs: add per-module readme status and roadmap files`
3. `docs: define strict git workflow for future branches`
4. `docs: sync master roadmap with platform structure`

Validation:

- manual link/path verification
- verify referenced commands and file paths still exist

## Branch D

Name:

- `refactor/add-platform-foundation-surface`

Goal:

- commit the non-runtime-breaking platform namespace foundations that are already prepared

Include:

- `src/vision_platform/__init__.py`
- `src/vision_platform/bootstrap.py`
- `src/vision_platform/apps/`
- `src/vision_platform/integrations/`
- `src/vision_platform/libraries/`
- `src/vision_platform/models/`
- `src/vision_platform/services/`
- `tests/test_vision_platform_namespace.py`

Exclude:

- physical storage move if not completed yet
- focus metric implementation
- documentation-only reorganization commits

Expected commits:

1. `refactor: add vision_platform namespace foundations`
2. `test: add platform namespace coverage`
3. `docs: record foundation module readiness`

Validation:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_vision_platform_namespace
```

## Branch E

Name:

- `feature/focus-core-baseline`

Goal:

- move from prepared focus scaffolding to the first real focus capability

Include:

- `libraries/focus_core/*`
- required files under `src/vision_platform/libraries/focus_core/`
- new tests for focus core
- focus-related status and roadmap updates

Exclude:

- unrelated repository reorganization
- storage migration
- broad app/frontend work

Expected commits:

1. `feat: add baseline focus evaluator contract`
2. `feat: implement first simulator-backed focus metric`
3. `test: add focus core coverage`
4. `docs: update focus module roadmap and status`

Validation:

- focus-core-specific unit tests
- simulator-backed validation for the selected metric

## Pre-Commit Safety Check

Before starting any future branch from this backlog:

1. inspect `git status --short`
2. inspect `git diff --cached --stat`
3. ensure no unrelated files are already staged
4. stage only the files listed for the selected branch
5. run the branch-specific validation block before merge
