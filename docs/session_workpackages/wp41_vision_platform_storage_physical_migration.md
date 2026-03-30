# Vision Platform Storage Physical Migration

## Purpose

This work package defines the next architecture-convergence follow-up after `WP40`.

Closure lane:

- Post-Closure Python Baseline / architecture convergence

Slice role:

- physical migration refactor

Its purpose is to move the current storage and persistence helpers behind the preferred `src/vision_platform` boundary without widening behavior or redesigning the recording lane.

## Branch

- intended branch: `refactor/vision-platform-storage-migration`
- activation state: active lane

## Scope

Included:

- file naming implementation
- frame writer implementation
- traceability/persistence helper ownership only where the physical move requires it
- compatibility-import preservation
- focused regression coverage and doc updates

Excluded:

- new file formats
- new recording behavior
- large persistence redesign
- offline reporting expansion

## Session Goal

Leave the repository with storage-facing implementation physically aligned to `src/vision_platform` while preserving the current runtime behavior and compatibility surface.

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
