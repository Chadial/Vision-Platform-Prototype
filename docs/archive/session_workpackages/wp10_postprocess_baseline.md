# Postprocess Baseline

## Purpose

This work package defines the first explicit offline or postprocess-oriented path for the platform.

Its purpose is to make stored images and later analysis results reusable outside the live camera loop without prematurely building a large secondary application.

## Branch

- intended branch: `feature/postprocess-baseline`
- activation state: planned after storage and analysis contracts are stable enough to reuse offline

## Scope

Included:

- identify one useful offline evaluation slice over stored images or image series
- keep the path aligned with existing storage, ROI, and focus contracts where possible
- clarify what belongs in a future postprocess tool versus what remains a shared library concern

Excluded:

- broad desktop UI work
- full analytics workstation behavior
- duplicate storage pipelines unrelated to current core contracts
- unrelated live-preview feature work

## Session Goal

Leave the repository with one explicit postprocess baseline or one implementation-ready contract slice for offline evaluation.

## Execution Readiness Assessment

For a fresh agent, the package was directionally valid but not execution-ready enough:

- the first offline use case was still too open between image loading, focus, metadata reuse, and broader analysis
- it was unclear whether the first slice should stay library-only or already activate the prepared app module
- exit criteria did not yet say what a minimally useful postprocess path would look like

The package is now refined around one thin offline focus-report path over stored `.pgm`/`.ppm` sample images, because that slice reuses the current simulator-backed image-ingestion path and the existing focus core without inventing a second analysis pipeline.

## Status

- current state: completed; archive after queue/status sync

## Sub-Packages

### SP1 Stored-Image Focus Report Baseline

- Goal: add one thin offline focus-evaluation path over stored sample images
- Scope:
  - activate `postprocess_tool` with one report-oriented entry point for `.pgm`/`.ppm` directories
  - reuse the existing simulated sample-image ingestion path and `focus_core`
  - return one typed per-image focus report shape
- Non-Scope:
  - generic offline image loading for arbitrary formats
  - tracking or overlay export
  - desktop UI work
- Validation:
  - targeted `tests.test_postprocess_tool`
- Dependencies:
  - current simulated sample-image support and focus-core baseline
- Exit Criterion:
  - the repository contains one real offline analysis path that reuses existing core contracts

### SP2 Postprocess Tool Module Activation

- Goal: move `postprocess_tool` from prepared-only to an explicit baseline module
- Scope:
  - update module docs and central status to reflect the new offline focus-report capability
  - record what remains deferred
- Non-Scope:
  - broad postprocess workstation planning
- Validation:
  - docs match the implemented offline slice
- Dependencies:
  - SP1
- Exit Criterion:
  - a fresh agent can identify what the postprocess tool now does

### SP3 Deferred Offline Boundary Close-Out

- Goal: close the package without widening it into a large analytics tool
- Scope:
  - explicitly defer richer file formats, metadata joins, and broader analysis/export concerns
  - record the next likely offline follow-up
- Non-Scope:
  - implementation of deferred offline concerns
- Validation:
  - `WP10` remains one bounded baseline
- Dependencies:
  - SP1 and SP2
- Exit Criterion:
  - no further work remains in this package without widening the intended postprocess scope

## Open Questions

- should the first offline slice focus on saved-image loading, focus evaluation, or metadata reuse?
- what stored metadata is required before offline analysis becomes genuinely useful?
- should the first slice be tool-backed or library-first?

## Learned Constraints

- do not build a second analytics core
- reuse current storage, ROI, and focus contracts where possible
- keep the first postprocess slice intentionally narrow

## Current Progress

The repository already has:

- stored image and metadata paths
- focus and ROI foundations that should later be reusable offline
- a prepared `apps/postprocess_tool` module area

What remains open:

- the first concrete offline use case
- the first thin entry point for offline evaluation

Chosen first slice:

- `SP1 Stored-Image Focus Report Baseline`
- reason: it reuses existing sample-image ingestion plus focus-core contracts directly and gives the repository one real offline path without opening a broader analytics or export lane

Implemented progress:

- `SP1` completed
- `postprocess_tool` now contains a thin offline focus-report entry point over stored `.pgm` / `.ppm` sample directories
- the new offline path reuses the existing simulator-backed sample-image ingestion path and `focus_core` instead of introducing a second image-loading or focus-analysis stack

Remaining package focus:

- `SP2` completed through module activation and permanent doc updates
- `SP3` completed by explicitly deferring broader file-format support, metadata joins, and richer export concerns

Package outcome:

- `postprocess_tool` is no longer only a prepared placeholder
- the repository now has one real offline analysis baseline that can run without a live camera connection
- the first offline baseline stays report-oriented and intentionally narrow, so it does not expand into a workstation or frontend project

## Execution Plan

1. re-read:
   - `docs/ProjectDescription.md`
   - `docs/STATUS.md`
   - `apps/postprocess_tool/README.md`
   - `apps/postprocess_tool/STATUS.md`
   - `apps/postprocess_tool/ROADMAP.md`
2. choose one small offline use case that already fits the current core
3. keep shared logic in libraries or services where possible
4. add a thin app or tool layer only if needed for the selected slice
5. add focused tests or smoke coverage
6. update docs once the baseline is real

## Validation

- targeted tests for the shared analysis or storage path being reused
- smoke validation for a thin postprocess entry point if one is added

Completed validation for `SP1`:

- `.\.venv\Scripts\python.exe -m unittest tests.test_postprocess_tool tests.test_focus_core tests.test_vision_platform_namespace`

## Documentation Updates

Before this work package is considered complete, update:

- `apps/postprocess_tool/STATUS.md`
- `apps/postprocess_tool/ROADMAP.md`
- `docs/STATUS.md`

## Expected Commit Shape

1. `feat: add postprocess baseline`
2. `test: cover postprocess baseline`
3. `docs: update postprocess baseline status`

## Merge Gate

- the offline path reuses current shared contracts rather than inventing a second core
- touched tests pass locally where relevant
- docs explain what postprocess behavior is now available and what remains prepared only

## Recovery Note

To activate this work package later:

1. Read `AGENTS.md`
2. Read `docs/SESSION_START.md`
3. Read `docs/STATUS.md`
4. Read `apps/postprocess_tool/STATUS.md`
5. Read `apps/postprocess_tool/ROADMAP.md`
6. Confirm that the selected offline slice can reuse current storage and analysis contracts cleanly
