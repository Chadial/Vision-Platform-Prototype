# Data And Logging Closure

## Purpose

This work package defines the first execution-ready Extended MVP closure slice for data and logging.

Its purpose is to close one narrow but practical gap between the current Python camera baseline and experiment-usable saved artifacts:

- visible standard image output should not depend only on PNG and TIFF
- the repository should support one additional simple visible export format explicitly aligned with the next-phase target picture

The narrow goal is to add and verify `BMP` as a supported visible image format for the current standard-library frame-writing path where that can be done without widening the architecture.

## Branch

- intended branch: `feature/data-logging-closure-visible-formats`
- activation state: current next execution-ready package after the first `Experiment Reliability Closure` slice

## Scope

Included:

- add `BMP` output support to the current frame-writing path where the pixel format maps cleanly
- keep the supported `BMP` scope deliberately narrow and explicit
- add targeted tests for the new format and its validation boundaries
- update docs so the repository no longer implies that visible practical output means only PNG/TIFF plus RAW/BIN

Selected slice for this package:

- `BMP` support for `Mono8`, `Rgb8`, and `Bgr8` through the standard-library path

Why this slice:

- it is directly named in the next-phase product intent
- it is locally verifiable
- it improves experiment usability without opening broad metadata or offline-analysis work yet

Excluded:

- broad metadata schema expansion
- CSV log redesign
- timestamp model redesign
- series-folder naming redesign
- higher-bit `BMP` support beyond what maps cleanly onto the current writer
- broad CLI or controller output changes unless needed trivially for format exposure

## Session Goal

Leave the repository with one explicit additional visible save format that makes experiment artifacts more practically usable without depending on the optional OpenCV path or reopening broader logging work.

The first completed slice should answer a small but concrete question:

- can the current snapshot/frame-writing path save `BMP` cleanly for the baseline visible pixel formats?

## Current Context

The repository already has:

- standard-library PNG support for `Mono8`, `Rgb8`, and `Bgr8`
- optional OpenCV grayscale support for higher-bit PNG and TIFF
- raw/bin output for acquisition-oriented artifacts

The immediate remaining gap is:

- `BMP` is part of the intended practical output set for the next phase, but it is not yet implemented or documented as a supported format

## Proposed Narrow Outcome

Preferred outcome for this slice:

- `BMP` can be written for `Mono8`, `Rgb8`, and `Bgr8`
- unsupported combinations still fail clearly
- the current visible-format story becomes:
  - PNG for current standard-library visible output
  - TIFF for grayscale paths where appropriate
  - BMP as an additional simple visible export path

## Learned Constraints

- keep this slice focused on file output, not on broad logging redesign
- preserve the separation between mandatory standard-library paths and optional OpenCV paths
- avoid adding speculative format support that is not needed for the current phase

## Narrow Decisions

- `BMP` is intentionally limited to `Mono8`, `Rgb8`, and `Bgr8` in this first slice
- higher-bit `BMP` support stays deferred because it would widen the format and conversion surface without helping the immediate Extended MVP proof
- recording and snapshot documentation should explicitly describe `BMP` as part of the practical visible-format baseline once the implementation lands

## Execution Plan

1. Re-read:
   - `docs/STATUS.md`
   - `docs/WORKPACKAGES.md`
   - `services/recording_service/README.md`
   - `services/recording_service/STATUS.md`
2. Inspect the current frame-writer and output-validation path for the narrowest place to add `BMP`.
3. Implement `BMP` writing through the standard-library path for:
   - `Mono8`
   - `Rgb8`
   - `Bgr8`
4. Keep unsupported combinations explicit and test-covered.
5. Add targeted tests for:
   - successful `BMP` write
   - unsupported format rejection where relevant
6. Update docs once the format support is real.

## Initial Deliverables

The branch should leave behind at least:

- `BMP` support in the frame writer for the selected pixel formats
- targeted format-validation and writer tests
- updated docs that include `BMP` in the practical visible-format story

## Validation

Required automated validation:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_frame_writer tests.test_snapshot_service
```

Recommended focused validation if shared output validation changes:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_frame_writer tests.test_snapshot_service tests.test_recording_service
```

Manual review points:

- written `BMP` files exist and are structurally valid for the selected baseline formats
- unsupported combinations still fail with clear messages

## Documentation Updates

Before this work package is considered complete, update:

- `docs/STATUS.md`
- `services/recording_service/STATUS.md`
- this file if follow-up format or metadata slices are still needed

## Expected Commit Shape

1. `feat: add bmp frame output baseline`
2. `test: cover bmp frame writing`
3. `docs: record data logging closure format slice`

## Merge Gate

- the slice remains narrow and focused on visible output formats
- targeted tests pass locally
- no unrelated metadata, UI, or transport work is bundled
- docs clearly state what visible format gap is now closed and what remains open

## Recovery Note

To activate this work package later:

1. Read `AGENTS.md`
2. Read `docs/SESSION_START.md`
3. Read `docs/MODULE_INDEX.md`
4. Read `docs/WORKPACKAGES.md`
5. Read `docs/STATUS.md`
6. Read `services/recording_service/README.md`
7. Read `services/recording_service/STATUS.md`
8. Read `docs/git_strategy.md`
9. Create the intended branch before any substantive edits
