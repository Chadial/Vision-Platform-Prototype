# Entry-Point And Launch Readiness Baseline

## Purpose

This work package defines the second operational-readiness slice behind `WP31`.

Closure lane:

- Post-Closure Python Baseline / Operational Readiness

Slice role:

- startup-surface and launch-readiness polish

Scope level:

- clearer entry-point and startup behavior for the current Python baseline

Its purpose is to make the current Python baseline easier to start correctly by tightening the practical launch surface without opening a full packaging or installer effort.

This package should be read as:

- bounded launch/readiness polish
- not full distribution packaging
- not repository restructuring

## Branch

- intended branch: `fix/entrypoint-launch-readiness-baseline`
- activation state: landed

## Scope

Included:

- inspect current preferred `python -m` entry points and launch assumptions
- identify one narrow readiness improvement set such as:
  - clearer startup/help text
  - clearer interpreter or environment checks
  - clearer error text for missing save directory or unsupported hardware assumptions
  - small wrapper/readme alignment where useful
- keep the resulting startup surface easy to hand over

Excluded:

- installers
- dependency-management overhaul
- broad CLI feature growth
- deployment-system work

What this package does not close:

- full packaging/distribution
- environment management across many machines
- broad host transport productization

## Session Goal

Leave the repository with one clearer and less error-prone practical launch baseline for the current Python system.

Implemented result:

- central startup-surface reference added at `docs/ENTRYPOINT_AND_LAUNCH_BASELINE.md`
- runbook, session bootstrap, PM/status surfaces, and `apps/camera_cli/README.md` now align on preferred `python -m` entrypoint versus launcher fallback

## Execution Plan

1. Re-read:
   - `docs/STATUS.md`
   - `docs/WORKPACKAGES.md`
   - `apps/camera_cli/STATUS.md`
2. Inspect the current entry points and startup messaging.
3. Freeze one bounded readiness polish slice.
4. Implement the narrowest useful change and update the launch docs.

## Validation

Recommended validation depends on the selected slice, but should stay narrow, for example:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_camera_cli tests.test_bootstrap
```

## Documentation Updates

- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- launch or app-facing docs that describe the preferred entry points

## Expected Commit Shape

1. `fix: tighten entrypoint launch readiness`
2. `test: cover launch readiness path`
3. `docs: record launch readiness baseline`

## Merge Gate

- the slice remains bounded to startup and launch readiness
- no installer or broad CLI growth is bundled
- any code change is paired with a narrow validation path

## Recovery Note

To activate this work package later:

1. inspect the currently preferred launch commands
2. inspect current bootstrap and CLI startup behavior
3. keep the selected slice bounded before editing
