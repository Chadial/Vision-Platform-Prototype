# Vision Platform Storage Physical Migration

## Purpose

This work package defines the next architecture-convergence follow-up after `WP40`.

Closure lane:

- Post-Closure Python Baseline / architecture convergence

Slice role:

- physical migration refactor

Its purpose is to move the current storage and persistence helpers behind the preferred `src/vision_platform` boundary without widening behavior or redesigning the recording lane.

Working discipline:

- do not pull this work into `WP40`
- activate it only after `WP40` is completed and re-stabilized
- keep this slice strictly on storage/persistence ownership rather than turning it into a broader recording refactor

## Branch

- intended branch: `refactor/vision-platform-storage-migration`
- activation state: landed

## Scope

Included:

- file naming implementation
- frame writer implementation
- traceability/persistence helper ownership only where the physical move requires it
- compatibility-import preservation
- focused regression coverage and doc updates

Explicitly included and no more:

- storage-facing helpers
- persistence ownership that is immediately adjacent to those helpers
- the minimum compatibility-shim adjustments required by that move

Excluded:

- new file formats
- new recording behavior
- large persistence redesign
- offline reporting expansion
- control or imaging migration
- broad namespace cleanup outside the touched storage/persistence seam

## Session Goal

Leave the repository with storage-facing implementation physically aligned to `src/vision_platform` while preserving the current runtime behavior and compatibility surface.

This package should be read as the follow-up storage slice after `WP40`, not as work to "pull along" while `WP40` is in progress.

Landed outcome:

- legacy service implementations now import platform-owned `file_naming` and `frame_writer` helpers directly
- `camera_app.storage` now acts as a package-level compatibility shim, not as the primary ownership surface
- focused regression coverage now proves those storage compatibility edges explicitly

## Validation

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_file_naming tests.test_frame_writer tests.test_snapshot_service tests.test_recording_service tests.test_interval_capture_service
```

## Documentation Updates

- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- affected storage/recording module `STATUS.md`

## Merge Gate

- storage behavior is unchanged
- compatibility imports still work
- touched tests pass
- no unrelated feature work is bundled
- no control/imaging migration is bundled
- no broader recording-lane redesign is bundled
