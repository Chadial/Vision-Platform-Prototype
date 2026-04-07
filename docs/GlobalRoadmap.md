# Global Roadmap

## Purpose

This document is the platform-wide master roadmap for evolving the current Python camera prototype into a modular vision platform that can later be handed over to a C#/.NET team and eventually support multiple frontends and external interfaces.

Detailed implementation planning should primarily move into the centralized `docs/WORKPACKAGES.md` queue, with module-local `ROADMAP.md` files kept only where genuinely useful. This document stays at the master-roadmap level.

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

Current master-roadmap interpretation:

- the repository now has a usable Python working baseline on the tested hardware path
- the former Extended MVP closure concern is no longer the active planning lens
- near-term work should now emphasize practical subsystem usability before broader platform expansion

## Current Active Phase

Within this master roadmap, the active repository-level phase is now:

**Usable Camera Subsystem / Pre-Product Baseline**

Meaning:

- treat the camera software as a practically usable subsystem rather than as an MVP proof artifact
- make the wx shell the primary local working path, with OpenCV kept as fallback/reference
- make the host-neutral command/status/result surface practically usable from the AMB control side
- preserve a small set of official reference scenarios such as snapshot, bounded recording, and interval capture
- use that usable subsystem as the first reference module for a later assisted measurement system
- treat a truly headless kernel as the next structural step after local and host usability are real enough

This active phase is not primarily about:

- broad web or API platform expansion
- broad MCP-oriented build-out
- full product packaging
- full C# handover
- broad offline workstation expansion
- reopening the old MVP-closure logic

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
- `docs/MODULE_INDEX.md`
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
- viewport-aware preview controls such as fit-to-window, zoom, and pan
- display-stable overlay mapping on top of those viewport transforms

### Status

- partially implemented
- viewport-based preview controls now exist in the OpenCV prototype path
- broader interactive ROI, focus-overlay toggles, and operator-facing preview controls remain open

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
- operator-friendly display behavior for large camera frames on limited screens
- frontend-owned viewport management instead of core-owned screen sizing

### Status

- OpenCV prototype path exists
- first real-hardware OpenCV preview path now exists for local inspection
- a first viewport-based OpenCV preview path with fit-to-window and zoom controls now exists as the prototype UI baseline
- desktop, web, and postprocess fronts are prepared structurally only

## Recommended Next Platform Steps

1. Improve the wx shell as the primary local working frontend while keeping OpenCV as the fallback/reference path.
2. Improve host-side usability through the shared command/status/result surface instead of opening broad transport work by default.
3. Preserve snapshot, bounded recording, and interval capture as official reference scenarios with clear operational confidence value.
4. Use those usable scenarios to guide the next shell and host-sync slices, including the current open-shell live-sync work.
5. After local and host usability are strong enough, prepare the next structural step: a truly headless kernel shared by UI, host control, and later automation flows.
6. Keep the broader assisted-measurement system direction visible, but treat it as later platform growth rather than the current default lane.
