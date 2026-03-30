# Python Baseline Operator Start Helper

## Purpose

This work package defines the next operational-readiness follow-up after the landed runbook and launch-baseline slices.

Closure lane:

- Post-Closure Python Baseline / Operational Readiness

Slice role:

- startup helper and operating-friction reduction

Scope level:

- current local operator and developer startup path only

Its purpose is to reduce small recurring startup friction for the current Python baseline without turning the repository into a packaging or installer effort.

This package should be read as:

- bounded operational-readiness polish
- not installer creation
- not deployment automation

## Branch

- intended branch: `chore/python-baseline-operator-start-helper`
- activation state: queued

## Scope

Included:

- evaluate whether one small helper script or command alias wrapper would reduce repeated startup friction
- keep any helper aligned with the currently preferred `.venv` and `python -m` paths
- document the helper as convenience, not as a new primary contract

Excluded:

- installer or packaging work
- environment manager replacement
- multi-machine deployment support

What this package does not close:

- full startup automation across environments

## Session Goal

Leave the repository with one smaller-friction startup helper only if it materially improves repeated local use without obscuring the preferred baseline paths.

## Landed Outcome

Observed result on March 30, 2026:

- the preferred startup surface was already clear in docs, but repeated local use still required operators and developers to repeatedly type the full `.venv` interpreter plus launcher or module form
- the current repository already had the right bounded launcher path in `scripts/launchers/run_camera_cli.py`
- the remaining gap was convenience, not missing startup semantics

Implemented narrowing:

- one bounded PowerShell convenience helper now exists at `scripts/run_python_baseline.ps1`
- the helper:
  - resolves repository root
  - uses the project `.venv` interpreter explicitly
  - delegates to `scripts/launchers/run_camera_cli.py`
  - falls back to `--help` when no command arguments are provided

Current interpretation after landing:

- the helper is convenience only
- the preferred baseline entry point remains `.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli`
- the helper reduces repeated local startup friction without introducing packaging, installer, or cross-machine launch guarantees

