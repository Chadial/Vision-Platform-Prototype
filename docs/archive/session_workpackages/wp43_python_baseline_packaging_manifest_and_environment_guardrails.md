# Python Baseline Packaging Manifest And Environment Guardrails

## Purpose

This work package defines the next operational-readiness slice after the current startup and runbook baseline.

Closure lane:

- Post-Closure Python Baseline / operational readiness

Slice role:

- environment and packaging guardrail baseline

Its purpose is to make the current Python baseline easier to install, recognize, and operate on a known-good local machine without pretending to solve full product packaging.

## Branch

- intended branch: `chore/python-baseline-packaging-guardrails`
- activation state: landed

## Scope

Included:

- document or tighten the bounded local environment contract around `.venv`, Vimba X, and launcher assumptions
- add the smallest justified packaging/manifest helper if needed for reproducible local setup
- improve environment diagnostics where that directly reduces operator setup ambiguity

Excluded:

- installer creation
- deployment automation
- cross-machine product packaging
- broad dependency reshaping

## Session Goal

Leave the repository with one clearer bounded local environment contract for the current Python baseline so setup and re-entry require less rediscovery.

Landed outcome:

- `pyproject.toml` now exposes one bounded installed console script, `vision-platform-cli`, above the existing CLI `main()` owner
- the bootstrap path now prints clearer guardrails around missing `VmbPy` and optional OpenCV support instead of only reporting a coarse install profile
- the current bounded local install contract now lives in `docs/PYTHON_BASELINE_ENVIRONMENT.md`
- runbook, launch-baseline, root README, and camera-CLI docs now point to the same environment contract and entry-point expectations

## Validation

- verify documented setup paths and current launcher paths still work
- run at least one simulated command through the preferred entry point

## Documentation Updates

- `docs/PYTHON_BASELINE_RUNBOOK.md`
- `docs/ENTRYPOINT_AND_LAUNCH_BASELINE.md`
- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`

## Merge Gate

- local environment assumptions are clearer
- no false promise of installer-grade packaging is introduced
- changes stay bounded to current baseline operations
