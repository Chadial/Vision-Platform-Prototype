# WP57 wx Focus Visibility And ROI Ownership

## Purpose

This work package defines the next bounded wx-shell operator slice after the first hardware-backed startup baseline.

Closure lane:

- Post-Closure Python Baseline / selective expansion

Slice role:

- operator-visibility hardening baseline

Scope level:

- one bounded wx-shell follow-up over the existing shared preview/display/focus stack

Its purpose is to make focus in the wx shell visibly trustworthy for real operator use by reusing the existing headless focus and ROI layers instead of introducing a wx-only focus model.

## Branch

- intended branch: `feature/wx-shell-operator-followups`
- activation state: implemented

## Scope

Included:

- make wx-shell focus visibly represented in the image area instead of only as a hidden-or-missing status concept
- keep focus evaluation on the shared `FocusPreviewService`
- use the active shared ROI when present and otherwise fall back to a full-frame / image-centered focus presentation
- keep the existing ROI state as the focus-ownership source instead of introducing a second wx-only focus ROI
- clean up duplicated point/status rendering where the fixed-point and transient message paths currently repeat the same coordinate payload

Excluded:

- ROI anchor hover and drag editing
- full ROI edit handles
- recording controls
- hardware audit / incident logging

## Session Goal

Leave the repository with a wx shell that can show where focus is being reported, keeps ROI ownership on the shared state path, and no longer duplicates selected-coordinate information in the status area.

## Execution Plan

1. extend the shared preview overlay/status model only where needed for focus visibility
2. reuse the existing `FocusPreviewService` output rather than adding wx-private focus computation
3. draw one visible focus marker/label in the wx canvas
4. keep ROI ownership on the shared `RoiStateService`
5. reduce duplicated coordinate status entries in the wx shell
6. cover the new semantics with targeted presenter/service tests

## Validation

Minimum local validation:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_wx_preview_shell tests.test_focus_preview_service tests.test_opencv_preview
```

## Documentation Updates

- `docs/WORKPACKAGES.md`
- `docs/STATUS.md`
- `apps/local_shell/README.md`
- `apps/local_shell/STATUS.md`

## Expected Commit Shape

1. `feat: show shared focus overlay in wx shell`
2. `test: cover wx focus visibility semantics`
3. `docs: record wx focus visibility follow-up`

## Merge Gate

- focus remains computed through the shared headless service
- the active ROI remains the focus-ownership source when defined
- the wx shell shows a visible focus marker/label without creating a new parallel focus model
- duplicate selected-point status text is removed
