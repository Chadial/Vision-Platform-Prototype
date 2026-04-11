# Offline And Measurement Closure

## Purpose

This work package defines the first execution-ready Extended MVP closure slice for offline and measurement-oriented reuse of saved image artifacts.

Its purpose is to close one narrow but practical gap between stored camera output and offline experiment use:

- the repository can already save practical visible image artifacts
- the repository should now prove that at least one saved artifact format can be consumed again for offline focus inspection without a live camera path

The narrow goal is to make the existing postprocess focus-report path usable with saved `BMP` artifacts produced by the current dependency-free frame writer.

## Branch

- intended branch: `feature/offline-measurement-closure-focus-report`
- activation state: current next execution-ready package after the first `Data And Logging Closure` slice

## Scope

Included:

- extend the thin offline focus-report path so it can read saved `BMP` files from a directory
- keep the supported `BMP` scope deliberately aligned with the current writer baseline
- add focused tests that prove saved `BMP` artifacts are usable for offline focus inspection
- update docs so the repository no longer implies that offline focus reporting works only with simulator-style `.pgm` / `.ppm` inputs

Selected slice for this package:

- offline focus-report support for `.bmp` files written in the current narrow baseline:
  - `Mono8`
  - `Rgb8`
  - `Bgr8`

Why this slice:

- it directly reuses the output of the newly landed `WP14` visible-format path
- it proves offline artifact reuse without needing broader metadata joins or workstation behavior
- it is locally verifiable and stays within the prepared `postprocess_tool` boundary

Excluded:

- generic arbitrary image loading
- TIFF or PNG offline loading
- richer measurement export formats
- broad metadata joins
- large postprocess workstation behavior
- tracking or overlay export

## Session Goal

Leave the repository with one explicit offline-usefulness proof for saved experiment artifacts:

- a directory of saved `BMP` files can be evaluated by the thin focus-report path without a live camera or simulator sample-sequence dependency

The first completed slice should answer one concrete question:

- can the repository reuse its own dependency-free visible `BMP` outputs for offline focus checks?

## Current Context

The repository already has:

- a thin postprocess focus-report path for `.pgm` / `.ppm`
- `WP14` support for dependency-free `BMP` output on the shared frame-writing path
- existing focus-core evaluation that already works on `Mono8`, `Rgb8`, and `Bgr8`

The immediate remaining gap is:

- saved camera artifacts from the current writer path are not yet proven usable through the postprocess focus-report flow

## Narrow Decisions

- this slice targets `BMP` only, not broader offline image loading
- supported `BMP` input is limited to the narrow baseline produced by the current writer:
  - uncompressed `Mono8`
  - uncompressed `Rgb8` / `Bgr8`-equivalent 24-bit color input
- `PNG` and `TIFF` offline loading stay deferred to later slices because they would widen codec and dependency decisions

## Execution Plan

1. Re-read:
   - `docs/STATUS.md`
   - `docs/WORKPACKAGES.md`
   - `apps/postprocess_tool/README.md`
   - `apps/postprocess_tool/STATUS.md`
   - `docs/archive/session_workpackages/wp10_postprocess_baseline.md`
2. Inspect the current postprocess focus-report path for the narrowest point to add saved-`BMP` reuse.
3. Implement a minimal loader path for the selected `BMP` baseline.
4. Keep unsupported `BMP` shapes explicit and test-covered.
5. Add targeted tests for:
   - successful offline report generation over saved `BMP` artifacts
   - unsupported or malformed `BMP` rejection where relevant
6. Update docs once the offline reuse path is real.

## Validation

Required automated validation:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_postprocess_tool tests.test_focus_core tests.test_frame_writer
```

Recommended focused validation if the report path shape changes:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_postprocess_tool tests.test_focus_core tests.test_vision_platform_namespace
```

Manual review points:

- saved `BMP` files written by the repository can be read back through the offline focus-report path
- unsupported `BMP` structures fail clearly instead of producing ambiguous reports

## Documentation Updates

Before this work package is considered complete, update:

- `apps/postprocess_tool/STATUS.md`
- `apps/postprocess_tool/README.md`
- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`

## Expected Commit Shape

1. `feat: add bmp offline focus report baseline`
2. `test: cover bmp offline focus reporting`
3. `docs: record offline measurement closure slice`

## Merge Gate

- the slice remains narrow and focused on offline reuse of saved `BMP` artifacts
- targeted tests pass locally
- no unrelated workstation, UI, or transport work is bundled
- docs clearly state what offline artifact gap is now closed and what remains open

## Recovery Note

To activate this work package later:

1. Read `AGENTS.md`
2. Read `docs/SESSION_START.md`
3. Read `docs/MODULE_INDEX.md`
4. Read `docs/WORKPACKAGES.md`
5. Read `docs/STATUS.md`
6. Read `apps/postprocess_tool/README.md`
7. Read `apps/postprocess_tool/STATUS.md`
8. Read `docs/git_strategy.md`
9. Create the intended branch before any substantive edits
