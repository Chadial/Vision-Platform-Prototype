# Hardware Revalidation Follow-Up

## Purpose

This work package captures the next hardware-backed revalidation slice after the archived Phase 9 baseline.

Its role is not to reopen broad hardware-validation work continuously, but to provide a ready recurring place for targeted follow-up checks whenever camera hardware is attached again and new behavior needs real-device evidence.

## Branch

- intended branch: `feature/hardware-revalidation-follow-up`
- predecessor context: `docs/archive/session_workpackages/wp04_hardware_validation_phase_9.md`
- activation state: conditional recurring slice; activate whenever suitable hardware is attached and a recent implementation group needs real-device evidence

## Scope

Included:

- targeted revalidation of already implemented camera, preview, snapshot, interval-capture, or recording behavior on attached hardware
- targeted checks for hardware-specific regressions introduced by later branches
- documenting new hardware evidence, limitations, and device-specific observations
- minimal hardening only when required to make the selected checks reproducible

Excluded:

- broad new feature development
- OpenCV-only UI expansion unrelated to hardware evidence
- speculative camera-driver redesign without a reproducible hardware problem
- simulator-only work that does not need a real-device pass

## Session Goal

Provide one small, reviewable hardware-backed follow-up slice that narrows uncertainty in the current baseline without turning hardware work into a permanent parallel branch.

## Status

- current state: conditional; do not activate until suitable hardware is attached or a specific hardware regression needs confirmation

## Sub-Packages

1. choose one hardware-backed revalidation target
2. prepare the smallest reproducible run path
3. collect hardware evidence
4. harden only what is needed for reproducibility
5. document results and remaining hardware gaps

## Open Questions

- which later changes most justify a real-device rerun first?
- are timeout or disconnect edge cases reproducible enough to justify a dedicated slice?
- should the next hardware pass focus on CLI, OpenCV preview, or configuration validation?

## Learned Constraints

- hardware work should answer one narrow question at a time
- simulator-backed evidence should remain the default when hardware is not attached
- documentation must be updated from evidence, not expectation

## Current Progress

The archived Phase 9 package already established a prototype-level hardware baseline for the previously attached camera path.

This package should therefore start from:

- revalidation of specific later changes
- new device-backed evidence for still-open edge cases
- concise documentation updates tied to actual runs

Latest recurring slice on April 7, 2026:

- target: bounded hardware revalidation after `WP50` and `WP51`
- question answered:
  - does the tested hardware path still behave correctly after extracting headless display geometry and shared preview-interaction ownership?
- executed checks:
  - serial hardware CLI `status` through `tested_camera`
  - hardware CLI `snapshot` through `tested_camera` plus `default` profile to `.bmp`
  - integrated hardware command flow through `run_hardware_command_flow.py`
  - bounded real-hardware OpenCV preview smoke through `run_hardware_preview_demo.py --frame-limit 5`
- observed result:
  - serial hardware `status` succeeded and still reported serial `067WH`
  - hardware `snapshot` succeeded and wrote `captures\hardware_smoke\wp04_revalidation_snapshot\snapshot.bmp`
  - integrated hardware command flow succeeded on `DEV_1AB22C046D81`
  - OpenCV hardware preview rendered 5 frames successfully at `2000x1500 Mono8`
  - `vmbpyLog <VmbError.NotAvailable: -30>` remained non-blocking residual noise
  - an intentionally parallel start of multiple hardware processes reproduced `camera already in use`, confirming that hardware validation commands must remain serial

## Execution Plan

1. confirm that suitable camera hardware is attached and usable
2. re-read:
   - `docs/STATUS.md`
   - `docs/HARDWARE_EVALUATION.md`
  - `docs/archive/session_workpackages/wp04_hardware_validation_phase_9.md`
3. choose one narrow revalidation target instead of a broad checklist rerun unless a full rerun is justified
4. identify the smallest required launcher, test, or manual run path
5. run the hardware check and capture concrete evidence
6. apply only minimal code hardening if a reproducible hardware issue appears
7. update docs from evidence, not from expectation

## Validation

- use the narrowest launcher or test block that covers the selected hardware-backed question
- when relevant, also run the matching simulator-backed regression block to separate hardware issues from general regressions

## Documentation Updates

Before this work package is considered complete for a given slice, update:

- `docs/HARDWARE_EVALUATION.md`
- `docs/STATUS.md`
- this file with newly learned constraints or follow-up notes if additional hardware passes are still expected

## Expected Commit Shape

1. `fix: harden selected hardware follow-up path`
2. `test: cover related regression where feasible`
3. `docs: record hardware revalidation follow-up`

## Merge Gate

- the selected hardware question is answered with real-device evidence
- touched tests pass locally where feasible
- docs clearly distinguish new hardware evidence from simulator-only assumptions
- no unrelated feature work is bundled into the branch

## Recovery Note

To activate this work package later:

1. Read `AGENTS.md`
2. Read `docs/SESSION_START.md`
3. Read `docs/STATUS.md`
4. Read `docs/HARDWARE_EVALUATION.md`
5. Read `docs/archive/session_workpackages/wp04_hardware_validation_phase_9.md`
6. Confirm hardware availability before creating the branch
