# WP52 Overlay And Preview Status Model Definition

## Purpose

This work package defines the descriptive model cleanup that should follow `WP51`.

Closure lane:

- Post-Closure Python Baseline / selective expansion through architecture readiness

Slice role:

- UI-agnostic model definition

Scope level:

- overlay and preview-status modeling only

Its purpose is to stop treating OpenCV status-band strings and renderer-local overlay assumptions as the de facto model boundary.

## Branch

- intended branch: `refactor/overlay-preview-status-model-definition`
- activation state: active lane

## Scope

Included:

- define UI-agnostic preview-status and overlay-facing models
- separate descriptive state from rendered strings
- keep current OpenCV preview as a rendering adapter over those models
- align status ownership with the extracted geometry and interaction layers

Excluded:

- new renderer work
- local UI shell implementation
- hardware audit/help polish

## Session Goal

Leave the repository with status/overlay information described as shared models rather than implicit OpenCV presentation details.

## Execution Plan

1. Identify current preview-status lines and overlay-relevant state.
2. Define additive shared models under the preferred platform boundary.
3. Keep the current OpenCV status band as a formatter over those models.
4. Reuse existing overlay composition where practical instead of duplicating fields.
5. Add focused tests for formatter-independent status ownership.

## Validation

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_opencv_preview tests.test_bootstrap
```

## Documentation Updates

- `docs/WORKPACKAGES.md`
- `docs/STATUS.md`
- `services/display_service/STATUS.md`

## Expected Commit Shape

1. `refactor: define preview status and overlay models`
2. `refactor: route opencv status rendering through shared models`
3. `test: cover preview status model formatting`
4. `docs: record overlay and status model slice`
