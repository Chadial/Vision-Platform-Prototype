# WP91 Local Shell ROI And Crosshair Priority Alignment

## Goal

Make crosshair the superior interaction mode in the preview shell so it cancels or blocks ROI entry and ROI dragging when enabled, while the same rule is enforced in the shared core interaction service and the wx shell.

## Status

Completed after implementation.

## Scope

- crosshair has priority over ROI anchor entry
- enabling crosshair aborts in-progress ROI draft or drag
- clicks while crosshair is active select the point instead of starting ROI entry
- ROI body and anchor dragging are blocked while crosshair is enabled
- core interaction state and shell UI stay aligned on the same priority rule

## Out Of Scope

- redesigning ROI geometry
- adding more ROI shapes
- changing the host command surface

## Affected Areas

- `src/vision_platform/services/display_service/preview_interaction_service.py`
- `src/vision_platform/apps/local_shell/preview_shell_state.py`
- `src/vision_platform/apps/local_shell/wx_preview_shell.py`
- `tests/test_preview_interaction_service.py`
- `tests/test_roi_state_service.py`
- `tests/test_wx_preview_shell.py`

## Validation

- `tests.test_preview_interaction_service`
- `tests.test_roi_state_service`
- `tests.test_wx_preview_shell`

## Done Criteria

- crosshair selection wins over ROI entry
- ROI draft is cleared when crosshair is enabled
- ROI drag/anchor movement does not occur while crosshair is on
- behavior is reflected in both core tests and shell tests
