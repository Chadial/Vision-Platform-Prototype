# Entrypoint And Launch Baseline

## Purpose

This document defines the currently preferred startup surface for the post-closure Python baseline.

Use it to answer:

- which entry point should be preferred for normal command use
- when `python -m` is preferred over repo-local launcher scripts
- which launchers are the current bounded reference paths
- which startup assumptions must be true before switching from simulator-backed to real-hardware execution

This document is intentionally narrower than a packaging guide.

It does not define:

- installers
- deployment automation
- production service hosting
- broad multi-machine environment management

## Launch Priority

Use this startup order by default:

1. package entry point with the project interpreter
2. installed console script from the editable package install
3. repo-local launcher script when `src` path bootstrapping is needed
4. repo-local PowerShell convenience helper for repeated local operator use
5. hardware-specific integrated launcher only for bounded real-device evidence

Current preferred interpreter:

```powershell
.\.venv\Scripts\python.exe
```

## Preferred Entrypoints

### 1. Camera CLI package entry point

Use this as the default command entry point when the local shell already runs from the repository root and the project interpreter is known:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli
```

Why this is preferred:

- it exercises the package exactly as an importable app surface
- it avoids relying on ad-hoc path bootstrapping when not needed
- it matches the module-oriented shape that later handover paths should preserve

### 2. Camera CLI launcher fallback

### 2. Installed console script

Use this when the editable install is already trusted and a shorter local command is useful:

```powershell
vision-platform-cli
```

Why this now exists:

- it proves the current package manifest exposes one bounded CLI entry point
- it reduces local shell friction without introducing a second business-logic path
- it stays tied to the same `vision_platform.apps.camera_cli:main` owner as the preferred package form

Boundary:

- this is still a local editable-install convenience, not installer-grade packaging
- it does not replace the explicit interpreter form as the clearest baseline command

### 3. Camera CLI launcher fallback

Use this when a repo-local launcher is more practical for operators or scripts:

```powershell
.\.venv\Scripts\python.exe .\scripts\launchers\run_camera_cli.py
```

Why this still exists:

- it bootstraps `src` into `sys.path`
- it remains convenient for local shell usage and repeatable smoke commands
- it stays aligned with the same package `main()` path rather than introducing separate business logic

### 4. Operator convenience helper

Use this when repeated local shell use is more important than typing the full interpreter-plus-launcher form every time:

```powershell
.\scripts\run_python_baseline.ps1
```

Examples:

```powershell
.\scripts\run_python_baseline.ps1 status --source simulated
.\scripts\run_python_baseline.ps1 snapshot --source simulated --base-directory .\captures\sim_smoke --file-extension .bmp
```

Why this exists:

- it keeps the current `.venv` path explicit inside one bounded helper
- it preserves the existing `run_camera_cli.py` launcher path instead of inventing a new app surface
- it reduces local operator and developer startup friction without becoming a packaging contract

Boundary:

- this helper is convenience only
- it does not replace the preferred package entry point
- it does not define cross-machine launch normalization

### 5. Integrated hardware command-flow runner

Use this only for bounded real-device confidence passes:

```powershell
.\.venv\Scripts\python.exe .\scripts\launchers\run_hardware_command_flow.py
```

This is not the default everyday command entry point.

It is the preferred integrated runner when hardware evidence is the actual goal.

## Current Bounded Entry Surface

The current practical startup surface is intentionally small:

- `vision_platform.apps.camera_cli`
- installed `vision-platform-cli`
- `scripts/launchers/run_camera_cli.py`
- `scripts/run_python_baseline.ps1`
- `scripts/launchers/run_hardware_command_flow.py`
- selected visual inspection launchers under `scripts/launchers/` only when preview inspection is actually needed

The current baseline should not be described as having:

- one-click packaging
- installation-grade command aliases
- cross-machine launch normalization

## Current Supported Command Forms

Preferred simulator-backed command examples:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli status --source simulated
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli snapshot --source simulated --base-directory .\captures\sim_smoke --file-extension .bmp
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli recording --source simulated --base-directory .\captures\sim_smoke --frame-limit 3
```

Preferred hardware-backed command examples on the tested path:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli status --source hardware --camera-id DEV_1AB22C046D81
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli snapshot --source hardware --camera-id DEV_1AB22C046D81 --base-directory .\captures\hardware_smoke --file-extension .bmp
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli recording --source hardware --camera-id DEV_1AB22C046D81 --base-directory .\captures\hardware_smoke --frame-limit 5
```

Use the launcher-script form when shell or operator convenience outweighs direct module invocation:

```powershell
.\.venv\Scripts\python.exe .\scripts\launchers\run_camera_cli.py status --source simulated
```

Use the installed console-script form when the editable install is already trusted:

```powershell
vision-platform-cli status --source simulated
```

Use the convenience-helper form when repeated local usage matters more than preserving the full explicit interpreter command at the shell prompt:

```powershell
.\scripts\run_python_baseline.ps1 status --source simulated
```

## Launch Readiness Checklist

Before normal simulator-backed use:

- use `.\.venv\Scripts\python.exe`
- run from repository root
- choose the package entry point by default
- use explicit save directories for snapshot, recording, and interval-capture commands

Before bounded hardware use:

- camera is physically attached
- Vimba X SDK is installed
- the local SDK wheel is installed into the same `.venv`
- the camera id is known
- commands are run serially

## Current Readiness Boundaries

Treat the startup baseline as ready when:

- the package entry point works from the project interpreter
- the installed console script resolves after editable install
- the launcher fallback works from repository root
- the convenience helper works from repository root and clearly behaves as a thin wrapper
- command help and current runbook references agree on the preferred form
- simulator-backed commands do not require extra rediscovery

Treat this as a follow-up trigger when:

- the package entry point and launcher path drift apart in documented behavior
- operators have to guess which startup form is preferred
- startup failures are caused by unclear interpreter or path expectations rather than the actual command task

## Relation To Other Docs

- `docs/PYTHON_BASELINE_RUNBOOK.md`: practical operating order, residuals, and baseline decision rules
- `docs/REFERENCE_SCENARIOS.md`: official bounded snapshot / recording / interval command recipes
- `docs/HARDWARE_EVALUATION.md`: real-device evidence and residual hardware observations
- `apps/camera_cli/README.md`: module-local CLI purpose and usage notes
