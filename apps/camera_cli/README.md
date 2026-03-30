# Camera CLI

## Purpose

Provides a camera-oriented command-line app surface for exercising the existing platform services without depending on the OpenCV preview path.

## Responsibility

- expose one coherent CLI entry command for camera operations
- reuse command-controller and service-layer contracts instead of ad-hoc script logic
- keep storage, camera configuration, and bounded capture options explicit
- keep CLI concerns separate from preview/UI-specific prototype behavior
- remain a thin local adapter above the shared host-neutral control layer rather than becoming a second business-logic path

## Functions

- consolidated `status` command
- consolidated `snapshot` command
- consolidated bounded `recording` command
- consolidated bounded `interval-capture` command
- simulator-backed and hardware-backed source selection
- bounded repo-local `camera_alias -> camera_id` resolution for repeated hardware use
- bounded repo-local `camera_class -> configuration profile` resolution for repeated hardware use through `configs/camera_configuration_profiles.json`

## Inputs / Outputs

- inputs: CLI arguments for camera source, camera id, configuration, save-directory behavior, and bounded capture options
- outputs: machine-readable JSON command envelopes on stdout for successful commands and on stderr for failures, with stable `success`, `command`, `result`, `status`, and `error` ownership
- outputs: the `status` portion of that envelope now reuses the transport-neutral API-service status payload family instead of exposing raw core models directly

## Host-Oriented Baseline

- `status` is the explicit polling-oriented command for host-readable runtime state
- `status` now also carries one additive `active_run` subset for active bounded recording or interval-capture work without widening into command-result confirmation
- `snapshot` returns a short-running command result with saved-path confirmation
- `recording` currently means bounded in-process recording that starts and completes within one invocation and then returns a final structured result
- `interval-capture` now also returns a bounded structured result with selected save directory, frames written, stop reason, accepted bounds, and a narrow confirmed-settings subset instead of remaining a result-shape special case
- the first host-oriented error shape is intentionally minimal: `code`, `message`, `details`
- command results now also include a small confirmed-settings subset for experiment traceability, such as camera id, pixel format, exposure, resolved save directory, resolved file stem / extension, and accepted recording bounds where relevant
- `snapshot` and bounded `recording` now also expose one deterministic `run_id` aligned with the traceability logs, while the bounded-recording status path surfaces that identity only during active work

## Dependencies

- `integrations/camera`
- `services/stream_service`
- `services/recording_service`
- `src/vision_platform/control`

## Usage

Prefer the package entry point:

- `.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli`

Or use the launcher:

- `.\.venv\Scripts\python.exe .\scripts\launchers\run_camera_cli.py`

Or use the installed console script after editable install:

- `vision-platform-cli`

Or use the bounded local convenience helper:

- `.\scripts\run_python_baseline.ps1`

Current practical preference:

- prefer the package entry point when the project interpreter and repository root are already explicit
- use `vision-platform-cli` when the editable install is already trusted and a shorter local command helps
- use `run_python_baseline.ps1` when repeated local shell use matters more than typing the full interpreter path every time
- use the launcher when repo-local path bootstrapping is more convenient for smoke commands or operator use

Examples:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli status --source simulated
vision-platform-cli status --source simulated
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli snapshot --source simulated --base-directory .\captures\sim_smoke --file-extension .bmp
.\.venv\Scripts\python.exe .\scripts\launchers\run_camera_cli.py recording --source simulated --base-directory .\captures\sim_smoke --frame-limit 3
.\scripts\run_python_baseline.ps1 status --source simulated
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli status --source hardware --camera-alias tested_camera
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli status --source hardware --camera-alias tested_camera --configuration-profile default
```

## Implementation Location

- app entry points currently live under `src/vision_platform/apps/camera_cli`
