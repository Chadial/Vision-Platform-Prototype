# WP51 Shared Preview Interaction Command Layer

## Purpose

This work package defines the next architecture slice after `WP50`.

Closure lane:

- Post-Closure Python Baseline / selective expansion through architecture readiness

Slice role:

- interaction ownership extraction

Scope level:

- preview interaction intents and commands only

Its purpose is to separate reusable preview interactions from OpenCV-specific keyboard and mouse event handling.

## Branch

- intended branch: `refactor/shared-preview-interaction-command-layer`
- activation state: current next

## Scope

Included:

- define one UI-agnostic interaction command set for current preview behaviors
- model reusable actions such as zoom in/out, fit-to-window, toggle crosshair, toggle focus line, ROI mode selection, point selection, pan start/update/stop, snapshot shortcut, and coordinate copy
- keep current OpenCV preview behavior by translating HighGUI events into those shared commands
- prepare the command layer so later UI shells and host-assisted preview control can reuse it

Excluded:

- new UI toolkit work
- overlay/status data-model redesign
- geometry extraction beyond `WP50`
- hardware audit/help polish

## Session Goal

Leave the repository with one shared preview-interaction layer so event semantics no longer live exclusively inside `OpenCvPreviewWindow`.

## Execution Plan

1. Identify current preview actions in `opencv_preview.py`.
2. Define one transport- and toolkit-neutral command family under the preferred platform boundary.
3. Add one small state transition layer where that improves reuse.
4. Adapt the OpenCV preview path so event handlers translate input into shared commands.
5. Keep geometry and rendering separate from command interpretation.
6. Add focused tests for command dispatch and state effects.

## Validation

Required automated validation:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_opencv_preview tests.test_opencv_smoke_demos
```

Recommended focused validation:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_display_geometry_service tests.test_bootstrap
```

## Documentation Updates

- `docs/WORKPACKAGES.md`
- `docs/STATUS.md`
- affected module `STATUS.md` files for `apps/opencv_prototype` and any new interaction-owning module

## Expected Commit Shape

1. `refactor: add shared preview interaction commands`
2. `refactor: route opencv preview input through shared interaction layer`
3. `test: cover preview interaction commands`
4. `docs: record preview interaction extraction`

## Merge Gate

- OpenCV input handling becomes an adapter over shared interaction semantics
- no new UI framework is introduced
- current preview behaviors remain test-covered
- no overlay/status redesign is mixed into this branch
