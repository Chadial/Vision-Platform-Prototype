# Target Map

## Purpose

This is the compact planning card for the current active phase.

Use it as the fast orientation layer above `docs/STATUS.md` and `docs/WORKPACKAGES.md`.
It is a derived reading aid, not the authoritative status carrier.

For a fuller but still lightweight prioritized task brainstorm, see `docs/PRIORITIES.md`.

## Active Phase

**Usable Camera Subsystem / Pre-Product Baseline**

The repository should currently be treated as a host-steerable running `Vision App / wxShell` and as the first reference module for a later assisted measurement system.

## Current Product Goal

- first product goal:
  - a running `Vision App / wxShell`
  - replaces the previous third-party software path
  - can be controlled by a host
- current product form:
  - `Hybrid Companion`
  - local shell remains visible and usable
  - host can steer core camera/acquisition behavior
  - shell reflects host-driven actions and state
  - local adjustability remains intentional in this phase
- near-term host staging:
  - Stage 1: test host
  - Stage 2: LabVIEW host

## Current Role Split

- `wx shell role`: companion/monitor surface for host-driven operation, debug/developer surface, functional replacement path for the previous third-party software, and still locally adjustable in this phase
- `host role`: define save location, define core camera settings, control acquisition, obtain camera metadata, and support experiment documentation

## Now

- host commands to the running `Vision App / wxShell`
- shell reflection of host-driven actions and state
- wx shell settings support
- practical execution of the confirmed workflows

Meaning:

- make the wx shell a practical companion/monitor surface for host-driven work
- keep OpenCV as fallback/reference rather than the intended shell
- keep the shared command/status/result surface practical for the current host stages
- preserve the confirmed workflows as the practical anchor scenarios

## Confirmed Functional Workflows

- `Delamination Recording`: preview, settings, recording start/stop, optional practical stop through `max frames reached`
- `Geometry Capture`: preview, settings, snapshot
- `Setup / Focus / ROI Adjustment`: preview, settings, ROI/focus, optional control snapshot

Technical support modes:

- preview
- snapshot
- recording start/stop
- ROI/focus
- max-frames stop behavior

## Current Usable Definition

- shell starts reliably
- preview is practically usable
- host can send the core commands
- camera settings are accessible in the shell
- snapshot and recording are understandable and usable
- ROI/focus is usable enough for setup
- status and hardware failures are understandable enough
- the three workflows can be executed in practice

## Current Host Expectations

This is the bounded Stage 1 test-host surface and the intended starting point for Stage 2 LabVIEW-host integration.

- `start` / `stop`
- `max frames`
- `recording fps`
- `save path`
- settings for shutter/exposure, hardware ROI, and gain
- ROI enable / disable
- focus value and ROI-related state

Current interpretation notes:

- focus value is a status field in this phase
- `conditional stop` currently means the practical `max frames reached` case

## Host / Shell Workflow

The current companion collaboration flow is file-backed and intentionally narrow.

Typical sequence:

1. start the visible wx shell
2. let it register an active live-sync session under `captures/wx_shell_sessions/`
3. send host commands from a separate process with `vision_platform.apps.local_shell control ...`
4. let the shell execute those commands through the same command-controller path used locally
5. read the published shell status or command result JSON that the shell wrote back

Common host-side examples:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.local_shell control status
.\.venv\Scripts\python.exe -m vision_platform.apps.local_shell control snapshot --file-stem geometry_000001 --file-extension .bmp
.\.venv\Scripts\python.exe -m vision_platform.apps.local_shell control apply-configuration --exposure-time-us 8000 --gain 2.0
```

Reading rule:

- treat the shell as the visible companion surface
- treat the separate `control` process as the host-side command source
- treat the JSON files under `captures/wx_shell_sessions/` as the current collaboration mechanism, not as a full transport contract

## Conditional Later Direction

- truly headless kernel preparation, only when justified by hardware evidence, integration need, test failure, or observed workflow friction

Meaning:

- prepare one kernel shared by local UI, host control, and later automation or agent flows
- do this after local and host usability are real enough and a concrete need has been identified

## Later

- assisted measurement platform growth
- broader integration, MCP-oriented orchestration, and productization

Meaning:

- crack-length or edge-based analysis
- simulation triggering
- statistical evaluation across runs
- audit-capable data handling
- calibration, sample, sensor, and operator entities
- broader transport, packaging, C# handover, and wider product surfaces

## Not The Current Default Lane

- reopen early reorganization logic
- reopen MVP-closure proof work
- broad web/API platform work by default
- broad additional frontend expansion
- broad MCP build-out by default
- full packaging
- full C# handover
- broad offline workstation expansion
- full assisted-measurement-system implementation
