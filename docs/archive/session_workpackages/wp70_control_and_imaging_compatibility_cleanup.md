# WP70 Control And Imaging Compatibility Cleanup

## Purpose

Remove the last redundant legacy control and imaging submodule implementations from `src/camera_app` now that the real code lives under `src/vision_platform`, while keeping package-level compatibility imports intact.

## Branch

`refactor/move-control-and-imaging-implementation`

## Scope

Included:

- delete the legacy `camera_app.control.command_controller` implementation file
- delete the legacy `camera_app.imaging.opencv_adapter` implementation file
- delete the legacy `camera_app.imaging.opencv_preview` implementation file
- keep `camera_app.control` and `camera_app.imaging` as compatibility shims through their package `__init__.py` files
- update central status and work-package tracking to reflect the cleanup slice

Excluded:

- driver, storage, or recording behavior changes
- new feature work in control or imaging
- broader `vision_platform` namespace migration outside the touched compatibility boundary

## Session Goal

The legacy submodule files are gone, the platform namespace remains the implementation home, and the compatibility package imports still resolve for existing callers.

## Status

Completed.

## Sub-Packages

- control compatibility cleanup
- imaging compatibility cleanup
- documentation synchronization

## Open Questions

- none for this slice

## Learned Constraints

- package-level `camera_app.control` and `camera_app.imaging` compatibility is sufficient for the current test surface
- direct submodule imports should be treated as deprecated compatibility debt, not as the canonical public path

## Execution Plan

1. remove the redundant legacy submodule files
2. verify the package-level compatibility imports still resolve
3. update central status and work-package documents
4. run the targeted unit tests for the touched import surfaces

## Validation

- `.\.venv\Scripts\python.exe -m unittest tests.test_command_controller tests.test_opencv_adapter tests.test_opencv_preview`

## Documentation Updates

- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`

## Expected Commit Shape

- one refactor commit for the cleanup
- one docs commit if the refactor and doc updates are kept separate

## Merge Gate

- targeted tests pass
- compatibility imports through `camera_app.control` and `camera_app.imaging` still work
- no unrelated behavior change is bundled
- central docs match the new implementation location

## Recovery Note

Read in this order if resumed later:

1. `AGENTS.md`
2. `docs/SESSION_START.md`
3. `docs/MODULE_INDEX.md`
4. `docs/STATUS.md`
5. `docs/WORKPACKAGES.md`
6. `docs/archive/session_workpackages/wp70_control_and_imaging_compatibility_cleanup.md`
