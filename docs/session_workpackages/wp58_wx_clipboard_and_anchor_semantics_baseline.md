# WP58 wx Clipboard And Anchor Semantics Baseline

## Purpose

This work package defines the next bounded wx-shell interaction slice after focus visibility and ROI ownership have been made visible.

Closure lane:

- Post-Closure Python Baseline / selective expansion

Slice role:

- operator-interaction baseline

Scope level:

- one bounded clipboard/selection semantics slice for the existing wx shell

Its purpose is to align the wx shell more closely with the already proven OpenCV operator path for point-selection and clipboard behavior while keeping interaction semantics on the shared preview/display layer.

## Branch

- intended branch: `feature/wx-shell-operator-followups`
- activation state: implemented

## Scope

Included:

- add `Ctrl+C` copy behavior in the wx shell
- reuse the existing shared point-selection semantics instead of inventing a separate wx clipboard model
- clarify the distinction between cursor coordinates and fixed selected-point state
- keep the shell ready for later anchor-hover / drag follow-up work without overextending this slice

Excluded:

- full draggable ROI edit handles
- anchor hover tooltips
- crosshair drag editing
- recording progress/status growth

## Session Goal

Leave the repository with one bounded wx-shell clipboard path that matches the current OpenCV point-selection baseline more closely and no longer overloads the status area with duplicated point messages.

## Execution Plan

1. bind one wx keyboard path for `Ctrl+C`
2. route clipboard actions through the existing point-selection semantics
3. tighten status messaging so selected-point and copied-point states remain distinct
4. add bounded tests around copy and selected-point status formatting

## Validation

Minimum local validation:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_wx_preview_shell tests.test_opencv_preview
```

## Documentation Updates

- `docs/WORKPACKAGES.md`
- `docs/STATUS.md`
- `apps/local_shell/README.md`
- `apps/local_shell/STATUS.md`

## Expected Commit Shape

1. `feat: add wx clipboard shortcut baseline`
2. `test: cover wx copy semantics`
3. `docs: record wx clipboard follow-up`

## Merge Gate

- wx `Ctrl+C` works without bypassing the shared point-selection semantics
- copied-point feedback is concise and non-duplicative
- no wx-only coordinate model is introduced
