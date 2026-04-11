# Python Baseline Operations Runbook

## Purpose

This runbook is the compact operating reference for the current post-closure Python camera baseline.

Use it to:

- choose the correct interpreter and launcher path
- prefer the right execution mode for simulator-backed versus real-hardware work
- run the currently supported command paths in a known-good order
- distinguish stable baseline behavior from residuals that deserve follow-up

This document is intentionally operational.

It does not define:

- new feature scope
- packaging automation
- broad deployment policy
- hardware matrix expansion

## Current Operating Verdict

- current baseline: usable Python working baseline with bounded host-oriented and hardware-validated evidence on tested camera path `DEV_1AB22C046D81`
- preferred interpreter: `.\.venv\Scripts\python.exe`
- preferred command entry point: `.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli`
- installed console entry point: `vision-platform-cli`
- preferred launcher fallback: `.\scripts\launchers\run_camera_cli.py`
- preferred local convenience helper: `.\scripts\run_python_baseline.ps1`
- preferred integrated real-hardware evidence path: `.\scripts\launchers\run_hardware_command_flow.py`
- preferred local shell companion host path: `.\.venv\Scripts\python.exe -m vision_platform.apps.local_shell control`
- current hardware residuals: `vmbpyLog <VmbError.NotAvailable: -30>`, duplicate SDK visibility for the tested camera id, bounded interval jitter, timing-sensitive back-to-back CLI reuse observations

## Stable Baseline

The current Python baseline should be treated as stable for these bounded paths:

- simulated `status`, `snapshot`, `recording`, and `interval-capture` through the camera CLI
- hardware-backed `status`, `snapshot`, bounded `recording`, and bounded `interval-capture` on the tested camera path
- traceability / recording-log output for current snapshot and bounded-recording flows
- offline reuse of current hardware-generated `BMP` output through the postprocess focus-report path
- capability-aware ROI validation with host-readable constraint details

The current baseline should not be described as:

- broadly hardware-validated across many devices
- stress-tested for long unattended runs
- packaging-complete
- final transport / API surface

Recording lifecycle boundary:

- current `recording` is bounded and in-process
- separate CLI or process invocations should not currently be treated as detached start / later stop control
- use `docs/RECORDING_LIFECYCLE_BOUNDARY.md` for the stable-now versus deferred-later recording semantics

## Preferred Environment

Use the project virtual environment:

```powershell
.\.venv\Scripts\python.exe
```

Assumptions for real-hardware work:

- Allied Vision Vimba X SDK is installed locally
- the local `vmbpy` wheel from that SDK is installed into the same `.venv`
- the camera is physically attached
- the intended camera id is known
- or the repo-local alias file `configs/camera_aliases.json` contains the intended hardware alias
- and, when profile-based hardware reuse matters, `configs/camera_configuration_profiles.json` contains the intended camera-class-first `default` profile

When these assumptions are not confirmed, prefer simulator-first execution.

For the bounded local install contract behind these assumptions, use:

- `docs/PYTHON_BASELINE_ENVIRONMENT.md`

For the official bounded confidence and handover recipes, use:

- `docs/REFERENCE_SCENARIOS.md`

## Known-Good Entry Points

For the launch-priority rules behind these paths, use:

- `docs/ENTRYPOINT_AND_LAUNCH_BASELINE.md`

Primary command entry point:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli
```

Supported current commands:

- `status`
- `snapshot`
- `recording`
- `interval-capture`

Preferred hardware integration runner:

```powershell
.\.venv\Scripts\python.exe .\scripts\launchers\run_hardware_command_flow.py
```

Useful secondary launchers:

- `vision-platform-cli`
- `.\.venv\Scripts\python.exe -m vision_platform.apps.local_shell`
- `.\scripts\run_python_baseline.ps1`
- `.\scripts\launchers\run_camera_cli.py`
- `.\scripts\launchers\run_snapshot_smoke.py`
- `.\scripts\launchers\run_simulated_demo.py`
- `.\scripts\launchers\run_hardware_preview_demo.py`
- `.\scripts\launchers\export_camera_capabilities.py`

Current practical rule:

- prefer `python -m vision_platform.apps.camera_cli` when the project interpreter and repository root are already explicit
- use `vision-platform-cli` when the editable install is already trusted and a shorter local command is useful
- use `run_python_baseline.ps1` as the bounded local convenience wrapper when repeated shell use matters more than keeping the full interpreter command visible
- use `run_camera_cli.py` for bounded host-surface checks when a repo-local launcher is more practical
- use `run_hardware_command_flow.py` for integrated real-device confidence passes
- use the OpenCV launchers only when local visual inspection is actually needed
- use `vision_platform.apps.local_shell` when a bounded local working frontend is needed and the optional `wxPython` dependency is installed in the same `.venv`
- use `vision_platform.apps.local_shell control ...` when a separate host-side process should drive a running shell through the bounded live-sync session

## Local Shell Host Workflow

The current host-plus-shell collaboration flow is file-backed and intentionally narrow.

Typical sequence:

1. start the visible wx shell with `vision_platform.apps.local_shell`
2. let the shell register an active live-sync session under `captures/wx_shell_sessions/`
3. send host commands from a separate process with `vision_platform.apps.local_shell control ...`
4. let the shell execute those commands through the same command-controller path
5. read the published shell status or command result JSON that the shell wrote back

Interaction rule for the shell side:

- `Crosshair` currently takes priority over ROI entry and ROI dragging
- enabling crosshair aborts any in-progress ROI draft or ROI drag
- `Camera Settings...` stays openable as a modal shell dialog even when apply is not currently available

Common host-side examples:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.local_shell control status
.\.venv\Scripts\python.exe -m vision_platform.apps.local_shell control snapshot --file-stem geometry_000001 --file-extension .bmp
.\.venv\Scripts\python.exe -m vision_platform.apps.local_shell control apply-configuration --exposure-time-us 8000 --gain 2.0
.\.venv\Scripts\python.exe -m vision_platform.apps.local_shell control start-recording --max-frames 0 --recording-fps 12.5
```

Reading rule:

- treat the shell as the visible companion surface
- treat the separate `control` process as the host-side command source
- treat the JSON files under `captures/wx_shell_sessions/` as the current collaboration mechanism, not as a full transport contract

## When To Prefer Simulator First

Prefer simulator-backed execution when:

- the camera is not confirmed attached for the current session
- the task is primarily service, command, validation, or contract work
- the task does not need fresh real-device evidence
- you are checking documentation, status payloads, or bounded request behavior

Prefer real hardware only when:

- the task is explicitly hardware-facing
- a current residual needs confirmation on the real device path
- a bounded confidence rerun is needed after a hardware-relevant change

Do not default to hardware for general regression work.

## Practical Run Order

For a normal bounded session, use this order:

1. `status`
2. `snapshot`
3. bounded `recording`
4. bounded `interval-capture` only when that path is relevant
5. integrated hardware command flow only when hardware evidence is actually needed

Preferred simulated sanity commands:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli status --source simulated
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli snapshot --source simulated --base-directory .\captures\sim_smoke --file-extension .bmp
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli recording --source simulated --base-directory .\captures\sim_smoke --frame-limit 3
```

Equivalent local convenience-helper form:

```powershell
.\scripts\run_python_baseline.ps1 status --source simulated
```

Preferred bounded hardware commands on tested path:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli status --source hardware --camera-alias tested_camera
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli snapshot --source hardware --camera-alias tested_camera --configuration-profile default --base-directory .\captures\hardware_smoke --file-extension .bmp
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli recording --source hardware --camera-id DEV_1AB22C046D81 --base-directory .\captures\hardware_smoke --frame-limit 5
```

Practical camera-selection rule:

- use direct `--camera-id` when you need exact explicitness
- use `--camera-alias` when the repo-local mapping is already trusted and you want shorter repeatable hardware commands

Preferred integrated hardware evidence command:

```powershell
.\.venv\Scripts\python.exe .\scripts\launchers\run_hardware_command_flow.py --base-directory .\captures\hardware_smoke --run-name run_001 --camera-id DEV_1AB22C046D81 --pixel-format Mono8 --frame-limit 3 --interval-frame-count 3
```

Practical caution:

- keep separate real-device CLI invocations serial
- avoid aggressive back-to-back hardware process launches when a simulator-backed check would do

## Save Path And Artifact Expectations

Use repo-local output directories:

- `captures\sim_smoke\`
- `captures\hardware_smoke\`

Expected current behavior:

- commands use explicit base directories for saved output
- `snapshot` and bounded `recording` can produce traceability output
- bounded `recording` writes a recording log
- host-facing `snapshot` and bounded `recording` surfaces expose a narrow confirmed-settings subset
- hardware-generated `BMP` output remains reusable through the current offline focus-report path

## Known Residuals

These are current residual observations, not default evidence of baseline failure:

- `vmbpyLog <VmbError.NotAvailable: -30>` may still appear during otherwise successful hardware runs
- SDK enumeration can show duplicate visible entries for `DEV_1AB22C046D81`
- interval capture on real hardware is boundedly acceptable, not perfectly scheduler-stable
- tightly back-to-back separate hardware CLI invocations can still be timing-sensitive

Treat these as follow-up triggers only when they become:

- reproducible blockers
- user-visible contract problems
- or clearly worse than the currently documented bounded behavior

## Stable Vs. Follow-Up Decision Rule

Treat the baseline as stable when:

- the command succeeds
- the host/status surface remains plausible
- output artifacts land in the expected directory
- traceability / recording-log output is present where expected
- residuals stay within the currently documented bounded observations

Open a follow-up when:

- a previously passing bounded path now fails reproducibly
- `camera already in use` returns in normal serial operation without aggressive back-to-back process timing
- status or command envelopes become misleading
- traceability or saved-artifact linkage breaks
- residual SDK noise starts correlating with actual startup or capability failure

## Deferred Areas

Still intentionally outside this runbook:

- packaging and installer automation
- broad deployment policy
- multi-camera validation
- performance benchmarking
- broader transport / API expansion
- broader UI / frontend planning
- later C# handover and productization work

Use this document as the operating reference for the current Python baseline, not as a replacement for later product-delivery docs.
