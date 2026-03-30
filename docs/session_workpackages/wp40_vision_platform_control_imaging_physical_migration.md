# Vision Platform Control And Imaging Physical Migration

## Purpose

This work package defines the next execution-ready post-closure architecture-convergence slice.

Closure lane:

- Post-Closure Python Baseline / architecture convergence

Slice role:

- physical migration refactor

Its purpose is to move the current control and optional imaging implementation behind the already preferred `src/vision_platform` boundary while preserving the current working baseline and compatibility imports.

This slice is about physical ownership convergence, not feature expansion.

## Branch

- intended branch: `refactor/vision-platform-control-imaging-migration`
- activation state: current next

## Scope

Included:

- move or re-home the `CommandController` implementation behind `src/vision_platform`
- move or re-home optional imaging/OpenCV adapter implementation behind `src/vision_platform`
- preserve compatibility imports through `src/camera_app`
- keep launcher and test paths working
- update the smallest affected module and central docs

Excluded:

- storage migration
- recording-service redesign
- transport/API expansion
- OpenCV feature widening

## Session Goal

Leave the repository with the preferred `vision_platform` boundary owning control and optional imaging implementation physically, while `camera_app` remains only a compatibility bridge where still needed.

## Execution Plan

1. Read affected module docs for `integrations/camera`, `services/api_service`, `apps/opencv_prototype`, and any touched compatibility surface.
2. Move control implementation behind `src/vision_platform` while preserving compatibility imports.
3. Move imaging/OpenCV implementation behind `src/vision_platform` while preserving compatibility imports.
4. Update imports and launcher paths only as needed.
5. Run focused regression tests.
6. Update local and central docs.

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
- docs reflect the new physical ownership cleanly

## Recovery Note

To resume later:

1. Read `AGENTS.md`
2. Read `docs/SESSION_START.md`
3. Read `docs/MODULE_INDEX.md`
4. Read `docs/WORKPACKAGES.md`
5. Read `docs/STATUS.md`
6. Create the intended branch before substantive edits
