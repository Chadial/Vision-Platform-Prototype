# Global Roadmap

## Purpose

This document is the platform-wide master roadmap for evolving the current Python camera prototype into a modular vision platform that can later be handed over to a C#/.NET team and eventually support multiple frontends and external interfaces.

Detailed implementation planning should increasingly move into the module-local `ROADMAP.md` files. This document stays at the master-roadmap level.

## Platform Modules

- camera / integration
- stream / frame pipeline
- recording / persistence
- display / interaction / overlays
- ROI / masks
- focus global / local
- edge / tracking / drift logic
- API / feeds / external systems
- postprocess
- multiple frontends

## Cross-Cutting Rules

- preserve a working Python baseline
- keep hardware access, UI, orchestration, and reusable analysis logic separate
- treat simulation as a first-class development path
- favor typed, portable contracts that can survive a later C# handover
- avoid forcing web or desktop framework choices into the core too early

## Master Phases

| Phase | Focus | Outcome |
| --- | --- | --- |
| 0 | Repository reorganization | platform modules visible in repo structure and docs |
| 1 | Python subsystem baseline | stable camera, snapshot, preview, recording flows |
| 2 | Integration and streaming hardening | shared acquisition, command flow, simulator parity, hardware checks |
| 3 | Common analysis foundations | shared models, ROI, focus groundwork |
| 4 | Interactive analysis MVP | ROI-driven focus and overlay-capable prototype |
| 5 | Tracking and drift preparation | edge/tracking kernels and feed-ready results |
| 6 | External interfaces | API/feed or host integration contracts |
| 7 | C# handover path | core concepts ready for direct port or parallel implementation |
| 8 | Additional frontends | desktop app, web-capable path, postprocess tooling |

## Phase 0: Repository Reorganization

### Goal

Turn the repository from a camera-centric code package into an explicitly modular platform repository without breaking the working Python baseline.

### Completed In This Round

- repository-level module folders for apps, integrations, services, and libraries
- per-module `README.md`, `STATUS.md`, and `ROADMAP.md`
- `MODULE_INDEX.md`
- reorganization documents in `docs/`
- `src/vision_platform` namespace mirroring the current stable implementation

### Still Open

- progressive physical relocation of implementation files out of `src/camera_app`
- tests that exercise the new namespace more broadly

## Phase 1: Python Subsystem Baseline

### Scope

- camera initialization
- snapshot saving
- live preview buffering
- recording and interval capture
- deterministic save paths and naming
- simulator-backed demos and smoke paths

### Status

- functionally completed
- still needs repeated real-hardware confirmation to be treated as validated baseline

## Phase 2: Integration And Streaming Hardening

### Scope

- shared acquisition path for preview plus recording
- host-neutral command surface
- simulator parity with hardware path
- hardware evaluation and recovery behavior

### Status

- mostly completed on the simulator-backed path
- real-hardware evaluation remains the main open item

## Phase 3: Common Analysis Foundations

### Scope

- shared frame metadata contracts
- ROI definitions and mask foundations
- focus request/result contracts
- analysis-ready module boundaries for later tracking and overlays

### Status

- initial groundwork completed in this round
- no full analysis implementation yet

## Phase 4: Interactive Analysis MVP

### Scope

- interactive ROI handling
- global and local focus metrics
- overlay-ready live display
- snapshot analysis using the same contracts

### Status

- not implemented yet

## Phase 5: Tracking And Drift Preparation

### Scope

- edge/profile analysis
- feature tracking or drift indication
- first crack-tip-oriented heuristics if the image data supports it

### Status

- prepared structurally only

## Phase 6: External Interfaces

### Scope

- host-facing contract hardening
- feed or API exposure of status and analysis results
- later automation hooks

### Status

- command-style Python controller exists
- transport/API contract is still intentionally deferred

## Phase 7: C# Handover Path

### Scope

- keep Python structures aligned with likely C# service and model boundaries
- identify modules ready for direct port
- make contracts explicit enough for a .NET team to own them

### Status

- architecture is being shaped for this path
- no C# implementation exists yet in this repository

## Phase 8: Additional Frontends

### Scope

- sustained OpenCV prototype
- later desktop frontend
- later web-capable frontend path
- later postprocess tooling

### Status

- OpenCV prototype path exists
- desktop, web, and postprocess fronts are prepared structurally only

## Recommended Next Platform Steps

1. Run the current Python baseline against real camera hardware again.
2. Add a first real focus metric on top of the new foundation modules.
3. Decide how ROI objects should enter preview and snapshot workflows without mixing UI and analysis responsibilities.
4. Expand tests to cover the `vision_platform` namespace as the preferred future import surface.
5. After that, move selected implementation files physically behind the already established platform module boundaries.
