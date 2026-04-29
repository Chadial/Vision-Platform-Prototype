# User Manual

## Purpose

This is the practical first-read manual for the current camera subsystem.

Use it when you need to understand:

- what the repository currently is for
- which app or command to start
- how to run the current simulator-backed workflows
- how a host process can control the visible wx shell
- what has been implemented and what is intentionally not implemented yet

For deeper service ownership and internal module boundaries, see `docs/SERVICE_OVERVIEW.md`.

## Current Goal

The current product direction is a host-steerable `Vision App / wxShell` in `Hybrid Companion` form.

That means:

- the local wx shell is visible and usable by an operator
- an external host process can send bounded camera and acquisition commands
- the shell reflects host-driven state and command results
- camera/acquisition logic stays outside the UI so it can later move toward a headless kernel, C#/.NET, or another frontend

The current system is not a finished product installer, a broad API server, or a final LabVIEW integration. It is a usable Python reference baseline with a narrow host-control path.

## Current Functional Workflows

### Delamination Recording

Goal:

- preview the specimen
- configure camera and recording settings
- start and stop recording
- use `max frames` as the current practical bounded stop condition when needed

Main surfaces:

- wx shell for visible preview and operator control
- `local_shell control start-recording` / `stop-recording` for host-style control
- camera CLI `recording` for repeatable command-line validation

### Geometry Capture

Goal:

- preview the specimen
- set camera/save settings
- save individual snapshots for later geometry measurement

Main surfaces:

- wx shell snapshot button or host-side `local_shell control snapshot`
- camera CLI `snapshot` for repeatable command-line validation

### Setup / Focus / ROI Adjustment

Goal:

- set exposure/gain/ROI-related camera parameters
- use the visible preview for focus and ROI setup
- optionally save a control snapshot

Main surfaces:

- wx shell preview, focus display, crosshair, ROI tools, and camera settings dialog
- host-side `local_shell control apply-configuration` for bounded external configuration

## Which Surface To Use

Use the wx shell when you need a visible operator app:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.local_shell --snapshot-directory .\captures\wx_shell_snapshot
```

Use the camera CLI when you want a repeatable non-UI command:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli status --source simulated
```

Use the local shell control adapter when the wx shell is already running and another process should act like a host:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.local_shell control status
```

Use the reference scenario validation when you want one quick simulator-backed confidence pass:

```powershell
.\.venv\Scripts\python.exe .\scripts\launchers\run_reference_scenario_validation.py
```

Use hardware mode only when the tested camera is physically attached and the Vimba X environment is available.

## Environment Basics

Run commands from the repository root.

Preferred interpreter:

```powershell
.\.venv\Scripts\python.exe
```

Default to simulator mode unless the real camera is intentionally part of the task:

```powershell
--source simulated
```

Current tested hardware shortcut when the camera is attached:

```powershell
--source hardware --camera-alias tested_camera --configuration-profile default
```

The known tested camera path is the Allied Vision device behind alias `tested_camera`. Hardware availability is session-dependent.

## Camera CLI

The camera CLI is the thin command-line adapter over the shared controller and service layer.

Entry point:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli
```

Supported commands:

- `status`: initialize the selected source and print consolidated status
- `snapshot`: save one image through the shared controller path
- `recording`: save a bounded image series through the shared controller path
- `interval-capture`: save timed single-image captures from the shared stream

Common options:

- `--source simulated|hardware`
- `--camera-id` or `--camera-alias`
- `--configuration-profile`
- `--base-directory`
- `--save-mode append|new_subdirectory`
- `--run-name`

Snapshot example:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli snapshot --source simulated --base-directory .\captures\manual_snapshot --file-stem manual_snapshot --file-extension .bmp
```

Bounded recording example:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli recording --source simulated --base-directory .\captures\manual_recording --file-stem manual_recording --file-extension .bmp --frame-limit 3
```

Interval capture example:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli interval-capture --source simulated --base-directory .\captures\manual_interval --file-stem manual_interval --file-extension .bmp --interval-seconds 0.10 --frame-limit 3
```

Hardware snapshot example when the tested camera is attached:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli snapshot --source hardware --camera-alias tested_camera --configuration-profile default --base-directory .\captures\hardware_manual_snapshot --file-stem hardware_manual_snapshot --file-extension .bmp
```

## wx Local Shell

The wx shell is the current visible companion app.

Start simulator-backed shell:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.local_shell --snapshot-directory .\captures\wx_shell_snapshot
```

Start hardware-backed shell when the tested camera is attached:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.local_shell --source hardware --camera-alias tested_camera --configuration-profile default --snapshot-directory .\captures\wx_shell_snapshot
```

Implemented shell functions:

- live preview from simulated or hardware source
- snapshot save
- recording start/stop with max frames and recording FPS
- recording progress and latest recording summary
- camera settings dialog
- focus display
- crosshair and point-copy support
- rectangle/ellipse ROI entry and bounded editing
- zoom, fit, pan, and coordinate mapping
- status and failure reflection
- external host-style control through the local shell control adapter

Important interaction rule:

- crosshair has priority over ROI entry and ROI dragging
- enabling crosshair aborts an in-progress ROI draft or ROI drag

## Host-Style Control Of The Running Shell

Start the wx shell first. It registers one active local session under:

```text
captures/wx_shell_sessions/
```

Then send commands from another terminal:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.local_shell control status
.\.venv\Scripts\python.exe -m vision_platform.apps.local_shell control set-save-directory --base-directory .\captures\host_control
.\.venv\Scripts\python.exe -m vision_platform.apps.local_shell control snapshot --file-stem geometry_000001 --file-extension .bmp
.\.venv\Scripts\python.exe -m vision_platform.apps.local_shell control apply-configuration --exposure-time-us 8000 --gain 2.0
.\.venv\Scripts\python.exe -m vision_platform.apps.local_shell control start-recording --max-frames 3 --recording-fps 12.5
.\.venv\Scripts\python.exe -m vision_platform.apps.local_shell control stop-recording --reason external_cli
```

Reading rules:

- this is a bounded file-backed companion path, not a production transport layer
- the shell executes commands through the shared command-controller path
- command results and published status are JSON files under the active session directory
- the shell remains the visible companion surface
- the host-side command process is the external command source

## Output Files

Use explicit output directories under `captures/`.

Typical outputs:

- snapshot image files such as `.bmp`, `.png`, `.tiff`, or `.raw` depending on pixel format
- bounded recording image series
- recording CSV logs for recording runs
- traceability files for snapshot and recording outputs
- hardware-audit JSONL entries only for warnings, degraded states, or incidents

Current naming policy:

- prefer deterministic file stems such as `geometry_000001`, `manual_recording`, or `delam_run_001`
- reused directories continue naming instead of overwriting previous snapshot or recording outputs

## Current Service Meaning

The user-facing apps are intentionally thin.

The shared service layer owns the reusable behavior:

- camera initialization and status
- snapshot and recording semantics
- interval capture
- stream and preview frame sharing
- focus and ROI state support
- display geometry and interaction models
- host/status/result payload shaping
- local shell companion command/session mechanics

The wx shell owns the visible window, buttons, menus, wx event translation, and bitmap painting.

The camera CLI owns command-line parsing and output, not camera business logic.

For a fuller map, see `docs/SERVICE_OVERVIEW.md`.

## What Is Implemented Now

Implemented baseline:

- simulator-backed camera source
- Vimba X hardware-backed source on the bounded tested path
- status, snapshot, bounded recording, and interval capture through the CLI
- visible wx shell with preview, snapshot, recording, settings, focus, ROI, and crosshair support
- external control of an already open wx shell through `local_shell control`
- traceability and recording logs for current snapshot/recording outputs
- bounded API-style payload mappers for status and command results
- LabVIEW-near mapping block on current local-shell control reads

## What Is Not Implemented Yet

Not current default scope:

- production installer or one-click deployment
- broad HTTP/API server
- final LabVIEW transport
- detached long-running recording lifecycle across unrelated processes
- browser UI
- final C# handover
- full assisted-measurement-system workflow
- broad historical artifact browser
- broad plugin/MCP orchestration

Conditional remaining evidence:

- `WP103` live wx camera-settings revalidation is only active when the tested hardware is physically attached and the narrow live rerun is possible.

## Where To Read Next

- `docs/SERVICE_OVERVIEW.md`: internal service/module map
- `docs/ENTRYPOINT_AND_LAUNCH_BASELINE.md`: startup surfaces and launch rules
- `docs/COMMANDS.md`: request names and command vocabulary
- `docs/HOST_CONTRACT_BASELINE.md`: stable-now versus deferred-later host contract
- `docs/REFERENCE_SCENARIOS.md`: repeatable simulator-backed technical recipes
- `docs/STATUS.md`: authoritative current state
- `docs/WORKPACKAGES.md`: work queue and conditional future work
