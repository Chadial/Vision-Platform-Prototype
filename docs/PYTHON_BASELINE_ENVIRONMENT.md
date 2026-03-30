# Python Baseline Environment

## Purpose

This document defines the bounded local environment contract for the current Python baseline.

Use it to answer:

- which installation profile is expected for normal simulator-backed work
- which extra assumption is required for OpenCV preview paths
- which extra assumption is required for real hardware
- which entry points are expected after local setup

This is an operational guardrail note.

It does not define:

- installer-grade packaging
- cross-machine deployment policy
- containerization
- full product distribution

## Current Environment Contract

- supported Python baseline: `>=3.11`
- preferred local interpreter on this machine: `.\.venv\Scripts\python.exe`
- packaging source of truth: `pyproject.toml`
- preferred install mode: editable install from repository root

Current install profiles:

1. `core`
   - `pip install -e .`
   - enough for simulator-backed CLI, service, and command-surface work
2. `opencv`
   - `pip install -e .[opencv]`
   - adds the current optional OpenCV preview and grayscale-save path
3. `hardware add-on`
   - local Vimba X SDK installed on the machine
   - local `vmbpy` wheel installed into the same `.venv`
   - required only for real-camera commands

## Preferred Setup Paths

Manual core setup:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .
```

Manual OpenCV-enabled setup:

```powershell
.\.venv\Scripts\python.exe -m pip install -e .[opencv]
```

Preferred Windows bootstrap:

```powershell
.\scripts\bootstrap.ps1
```

Variants:

```powershell
.\scripts\bootstrap.ps1 -IncludeOpenCv
.\scripts\bootstrap.ps1 -VmbPyWheel "C:\Path\To\vmbpy-X.Y.Z-py-none-any.whl"
.\scripts\bootstrap.ps1 -IncludeOpenCv -VmbPyWheel "C:\Path\To\vmbpy-X.Y.Z-py-none-any.whl"
```

## Entry-Point Guardrails

After a normal editable install, the intended command surfaces are:

- preferred package form:
  - `.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli`
- installed console script:
  - `vision-platform-cli`
- bounded repo-local helper:
  - `.\scripts\run_python_baseline.ps1`

Practical rule:

- prefer `python -m vision_platform.apps.camera_cli` when the interpreter is already explicit
- use `vision-platform-cli` when the editable install is already trusted and a shorter command helps
- use `run_python_baseline.ps1` as a repo-local convenience helper, not as the primary packaging contract

## Hardware Guardrails

Real-camera use still requires all of these:

- Allied Vision Vimba X SDK installed locally
- matching local `vmbpy` wheel installed into the same `.venv`
- physically attached tested camera path when hardware evidence is the goal

Do not read `pip install -e .` as meaning hardware readiness.

The editable install provides the repository package.
It does not provide:

- Vimba X transport layers
- camera drivers
- the `vmbpy` wheel

## Minimum Verification

After setup, verify the bounded baseline with one simulated command:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli status --source simulated
```

Or through the installed console script:

```powershell
vision-platform-cli status --source simulated
```

Treat the environment as ready when:

- editable install succeeds
- the preferred package entry point works
- the installed console script resolves
- simulator-backed status succeeds without extra path bootstrapping

Use `docs/PYTHON_BASELINE_RUNBOOK.md` for normal run order and `docs/ENTRYPOINT_AND_LAUNCH_BASELINE.md` for startup-priority rules.
