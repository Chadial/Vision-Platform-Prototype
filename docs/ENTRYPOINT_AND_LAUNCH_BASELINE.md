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
2. repo-local launcher script when `src` path bootstrapping is needed
3. hardware-specific integrated launcher only for bounded real-device evidence

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

Use this when a repo-local launcher is more practical for operators or scripts:

```powershell
.\.venv\Scripts\python.exe .\scripts\launchers\run_camera_cli.py
```

Why this still exists:

- it bootstraps `src` into `sys.path`
- it remains convenient for local shell usage and repeatable smoke commands
- it stays aligned with the same package `main()` path rather than introducing separate business logic

### 3. Integrated hardware command-flow runner

Use this only for bounded real-device confidence passes:

```powershell
.\.venv\Scripts\python.exe .\scripts\launchers\run_hardware_command_flow.py
```

This is not the default everyday command entry point.

It is the preferred integrated runner when hardware evidence is the actual goal.

## Current Bounded Entry Surface

The current practical startup surface is intentionally small:

- `vision_platform.apps.camera_cli`
- `scripts/launchers/run_camera_cli.py`
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
- the launcher fallback works from repository root
- command help and current runbook references agree on the preferred form
- simulator-backed commands do not require extra rediscovery

Treat this as a follow-up trigger when:

- the package entry point and launcher path drift apart in documented behavior
- operators have to guess which startup form is preferred
- startup failures are caused by unclear interpreter or path expectations rather than the actual command task

## Relation To Other Docs

- `docs/PYTHON_BASELINE_RUNBOOK.md`: practical operating order, residuals, and baseline decision rules
- `docs/HARDWARE_EVALUATION.md`: real-device evidence and residual hardware observations
- `apps/camera_cli/README.md`: module-local CLI purpose and usage notes
