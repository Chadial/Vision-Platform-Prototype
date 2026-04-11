# Vision Platform Control And Imaging Physical Migration

## Purpose

This work package defines the next execution-ready post-closure architecture-convergence slice.

Closure lane:

- Post-Closure Python Baseline / architecture convergence

Slice role:

- physical migration refactor

Its purpose is to move the current control and optional imaging implementation behind the already preferred `src/vision_platform` boundary while preserving the current working baseline and compatibility imports.

This slice is about physical ownership convergence, not feature expansion.

Working discipline:

- keep this slice strictly limited to `control` and optional `imaging`
- do not treat this package as the start of a broader namespace sweep
- when in doubt, defer remaining migration work to `WP41` or later

## Branch

- intended branch: `refactor/vision-platform-control-imaging-migration`
- activation state: landed

## Scope

Included:

- move or re-home the `CommandController` implementation behind `src/vision_platform`
- move or re-home optional imaging/OpenCV adapter implementation behind `src/vision_platform`
- preserve compatibility imports through `src/camera_app`
- keep launcher and test paths working
- update the smallest affected module and central docs

Explicitly included and no more:

- control-layer implementation ownership
- optional imaging/OpenCV adapter ownership
- the minimum compatibility-shim adjustments required by that move

Excluded:

- storage migration
- file naming migration
- frame writer migration
- traceability helper migration
- recording-service redesign
- transport/API expansion
- OpenCV feature widening
- broad import cleanup outside the directly touched control/imaging path
- namespace-wide shim reduction

## Session Goal

Leave the repository with the preferred `vision_platform` boundary owning control and optional imaging implementation physically, while `camera_app` remains only a compatibility bridge where still needed.

This package should not leave the repository half-migrated across unrelated storage or persistence areas.

Landed outcome:

- `vision_platform.bootstrap` now owns the bootstrap implementation directly
- `camera_app.bootstrap` is now a compatibility shim to that platform-owned implementation
- `camera_app.control` and `camera_app.imaging` now expose package-level compatibility reexports in addition to the existing submodule shims
- focused regression coverage now proves those compatibility edges explicitly

## Execution Plan

1. Read affected module docs for `integrations/camera`, `services/api_service`, `apps/opencv_prototype`, and any touched compatibility surface.
2. Move control implementation behind `src/vision_platform` while preserving compatibility imports.
3. Move imaging/OpenCV implementation behind `src/vision_platform` while preserving compatibility imports.
4. Update imports and launcher paths only as needed.
5. Stop and defer any storage/persistence ownership drift encountered beyond the narrow touched seam.
6. Run focused regression tests.
7. Update local and central docs.

## Validation

Required:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_command_controller tests.test_opencv_adapter tests.test_opencv_preview tests.test_opencv_smoke_demos tests.test_bootstrap
```

## Documentation Updates

- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- affected module `STATUS.md`
- affected module `README.md` only if ownership wording changes materially

## Expected Commit Shape

1. `refactor: move control implementation behind vision_platform`
2. `refactor: move imaging implementation behind vision_platform`
3. `test: align control and imaging regression coverage`
4. `docs: record control and imaging migration`

## Merge Gate

- compatibility imports still work
- touched tests pass
- no unrelated storage or service redesign is bundled
- no storage/persistence migration is bundled "because the files were nearby"
- no broad namespace cleanup is bundled beyond the directly required control/imaging seam
- docs reflect the new physical ownership cleanly

## Recovery Note

To resume later:

1. Read `AGENTS.md`
2. Read `docs/SESSION_START.md`
3. Read `docs/MODULE_INDEX.md`
4. Read `docs/WORKPACKAGES.md`
5. Read `docs/STATUS.md`
6. Create the intended branch before substantive edits
