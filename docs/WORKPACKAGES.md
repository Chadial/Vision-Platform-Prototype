# Work Packages

## Purpose

This document is the central PM planning surface for repository-level work-package selection.

It does not replace the detailed work-package notes under `docs/session_workpackages/`.

Use it to:

- derive the next repository-level work package
- understand the rough execution order across modules
- map strategic project documents to concrete next branches
- decide which detailed session work-package note should be activated next

Detailed execution shape, branch-local notes, progress tracking, sub-package tracking, and recovery guidance should continue to live in:

- `docs/session_workpackages/`
- `docs/archive/session_workpackages/`

## Planning Sources

This PM view is derived from:

- `docs/STATUS.md`
- `docs/ROADMAP.md`
- `docs/GlobalRoadmap.md`
- `docs/NEXT_SESSION_ORDER.md`
- `docs/ProjectAgents.md`
- `docs/ProjectDescription.md`
- active and archived files under `docs/session_workpackages/` and `docs/archive/session_workpackages/`

## Planning Rule

Use two planning levels:

1. repository-level PM plan in this file
2. execution-ready session work packages in `docs/session_workpackages/`

This file should stay coarse enough to be stable for several sessions.

The session work-package files should stay detailed enough to resume interrupted implementation directly, record progress, split into sub-work-packages, and preserve later lessons.

## Current Work-Package Style Rule

The detailed style already used in `docs/session_workpackages/` is the preferred format for execution-ready work packages.

That means a real implementation work package should usually contain:

- `Purpose`
- `Branch`
- `Scope`
- `Session Goal`
- `Execution Plan`
- `Validation`
- `Documentation Updates`
- `Expected Commit Shape`
- `Merge Gate`
- `Recovery Note`

This file should not try to duplicate that full detail for every item.

## Activation State Legend

Use these meanings consistently:

- `current next`: the default package a fresh agent should pick when the user does not redirect
- `active lane`: important and already prepared, but not the default next pick
- `conditional`: only activate when the stated condition becomes true
- `queued`: valid package, but not yet next
- `dormant`: keep for continuity, but do not activate unless a concrete reason appears

## Goal, Status, Order Overview

This section gives PM one compact view of:

- what the repository is moving toward
- what is already available
- which work packages exist
- in which order they should currently run

### Target Picture

The project goal, derived from `docs/ProjectDescription.md`, `docs/ProjectAgents.md`, and `docs/GlobalRoadmap.md`, is:

1. keep a stable Python-first camera and acquisition baseline
2. preserve a clean modular architecture suitable for later C# handover
3. support preview, snapshot, recording, ROI, focus, and later tracking
4. keep one host-neutral command surface as the main control layer
5. treat OpenCV as the current operator-facing preview/UI path, not as the platform core
6. prepare later API/feed, postprocess, desktop, and web-capable paths only after the core contracts are stable

### Current Implemented Baseline

Derived from `docs/STATUS.md`:

- camera, snapshot, preview, recording, interval capture, and simulator path are implemented
- host-neutral command/controller baseline exists
- narrow camera CLI baseline exists
- OpenCV preview/operator baseline exists
- ROI rectangle/ellipse groundwork exists
- first focus baseline exists
- hardware validation has been completed at prototype level for the previously attached camera path, with further revalidation still useful when hardware is available again

### Current Priority Source

The strongest currently documented sequencing signals are:

1. `docs/NEXT_SESSION_ORDER.md`
2. `docs/STATUS.md`
3. `docs/GlobalRoadmap.md`
4. `docs/ProjectDescription.md`
5. existing active session work-package files

Combined interpretation:

1. keep the CLI baseline narrow and stable
2. next harden the host-neutral command surface
3. keep OpenCV UI work separate and bounded
4. use hardware work as selective revalidation, not as the main planning lane
5. after current control/UI stabilization, define the next ROI/focus-closing packages
6. only then move toward tracking, API, handover hardening, postprocess, and further frontends

## WP Overview

This is the current PM overview of work packages to activate or defer.

| PM Order | Work Package | Purpose | Activation State | Priority | Detailed File |
| --- | --- | --- | --- | --- | --- |
| 1 | Camera CLI Baseline Narrowing | keep the CLI intentionally thin and stable over the shared control layer | dormant | active baseline, not primary next package | `docs/session_workpackages/wp01_camera_cli.md` |
| 2 | Host Integration Command Surface | harden the shared host-neutral command surface for later CLI, API, and C# embedding reuse | dormant | completed and archived; keep for continuity only | `docs/archive/session_workpackages/wp02_host_integration_command_surface.md` |
| 3 | OpenCV UI Operator Follow-Up | continue bounded UI/operator work without leaking screen concerns into core services | dormant | completed and archived; keep for continuity only | `docs/archive/session_workpackages/wp03_opencv_ui_operator_block.md` |
| 4 | Hardware Revalidation Follow-Up | re-run selected hardware checks and capture new evidence when hardware is attached again | conditional | conditional / deferred until hardware is attached | `docs/session_workpackages/wp04_hardware_revalidation_follow_up.md` |
| 5 | ROI Workflow Consolidation | define ownership and reuse of ROI state across preview, snapshot, and analysis | dormant | completed and archived; keep for continuity only | `docs/archive/session_workpackages/wp05_roi_workflow_consolidation.md` |
| 6 | Focus Method Expansion | add a stronger focus-method slice beyond the current baseline | dormant | completed and archived; keep for continuity only | `docs/archive/session_workpackages/wp06_focus_method_expansion.md` |
| 7 | Tracking Core Baseline | establish the first edge/tracking foundation slice | dormant | completed and archived; keep for continuity only | `docs/archive/session_workpackages/wp07_tracking_core_baseline.md` |
| 8 | API Surface Preparation | prepare the first external adapter above the host-neutral control layer | current next | next package after ROI/focus/tracking MVP boundary is clearer | `docs/session_workpackages/wp08_api_surface_preparation.md` |
| 9 | C# Handover Hardening | identify and tighten contracts that are most likely to survive direct C# porting | queued | medium-term, after control and analysis contracts settle | `docs/session_workpackages/wp09_csharp_handover_hardening.md` |
| 10 | Postprocess Baseline | define an offline evaluation path over stored images and analysis data | queued | later, after storage and analysis contracts stabilize | `docs/session_workpackages/wp10_postprocess_baseline.md` |
| 11 | Additional Frontends | prepare desktop and later web-capable paths | queued | low current priority | `docs/session_workpackages/wp11_additional_frontends.md` |

## Immediate PM Backlog

These are the work packages PM should treat as the current actionable backlog:

1. `API Surface Preparation`
2. `C# Handover Hardening`
3. `Postprocess Baseline`

These are important but should not be treated as the main always-on stream:

1. `Camera CLI Baseline Narrowing`
2. `Hardware Revalidation Follow-Up`
3. `Host Integration Command Surface`
4. `OpenCV UI Operator Follow-Up`

These should remain queued behind the above:

1. `C# Handover Hardening`
2. `Postprocess Baseline`
3. `Additional Frontends`

## Rough PM Sequence

The PM should currently plan in these layers.

### Layer 1: Stabilize And Narrow The Current Baseline

Goal:

- keep the current Python platform stable
- avoid mixing too many new directions at once
- reduce ambiguity around the preferred command and UI paths

Detailed work-package files:

- `docs/session_workpackages/wp01_camera_cli.md`
- `docs/session_workpackages/wp02_host_integration_command_surface.md`
- `docs/session_workpackages/wp03_opencv_ui_operator_block.md`
- `docs/session_workpackages/wp04_hardware_revalidation_follow_up.md`
- `docs/archive/session_workpackages/wp04_hardware_validation_phase_9.md`

### Layer 2: Complete The Analysis MVP Boundary

Goal:

- turn the current ROI/focus groundwork into a deliberate MVP boundary
- make clear which parts are foundation, which parts are already operator-usable, and which parts remain deferred

Detailed work-package files:

- `docs/archive/session_workpackages/wp05_roi_workflow_consolidation.md`
- `docs/archive/session_workpackages/wp06_focus_method_expansion.md`

### Layer 3: Prepare The Next Analysis Expansion

Goal:

- move from focus/ROI baseline toward tracking or edge-oriented groundwork without overcommitting too early

Detailed work-package file:

- `docs/archive/session_workpackages/wp07_tracking_core_baseline.md`

### Layer 4: External Interfaces And Handover Preparation

Goal:

- harden the platform so later C# embedding, API exposure, and external automation reuse the same core contracts

Detailed work-package files:

- `docs/session_workpackages/wp08_api_surface_preparation.md`
- `docs/session_workpackages/wp09_csharp_handover_hardening.md`

### Layer 5: Additional Frontends And Offline Paths

Goal:

- expand beyond the OpenCV prototype only after the core paths above are sufficiently stable

Detailed work-package files:

- `docs/session_workpackages/wp10_postprocess_baseline.md`
- `docs/session_workpackages/wp11_additional_frontends.md`

## Current Recommended Order

The current coarse PM order should be:

1. treat the CLI baseline as intentionally narrow unless a concrete defect appears
2. treat the host-integration and bounded OpenCV follow-up packages as completed baseline-hardening work
3. use hardware validation as a revalidation package when hardware is attached, not as the main always-active stream
4. treat the ROI workflow package as completed baseline-clarification work
5. treat the focus expansion package as completed baseline-hardening work
6. then open the next API preparation package

## Recommended Next Detailed Work Package

If the user does not explicitly redirect the session, the next PM-recommended execution-ready package is:

- `docs/session_workpackages/wp08_api_surface_preparation.md`

Reason:

- the ROI/focus/tracking MVP boundary is now explicitly implemented and documented
- the next open package is API surface preparation above the shared command/controller layer
- that next package can now build on the clearer core analysis baseline without reopening ROI/focus/tracking kernel questions

## Fresh Agent Decision Rule

When a fresh agent is not explicitly assigned a package:

1. read `AGENTS.md`
2. read `docs/SESSION_START.md`
3. read `docs/MODULE_INDEX.md`
4. read `docs/WORKPACKAGES.md`
5. choose the package marked `current next`, unless the user or current branch scope clearly overrides it
6. open that package's detailed `docs/session_workpackages/wpXX_*.md` file before implementation

## Detailed Package Inventory

The repository now has explicit detailed session work-package files for all currently identified packages:

- `docs/session_workpackages/wp01_camera_cli.md`
- `docs/archive/session_workpackages/wp02_host_integration_command_surface.md`
- `docs/archive/session_workpackages/wp03_opencv_ui_operator_block.md`
- `docs/session_workpackages/wp04_hardware_revalidation_follow_up.md`
- `docs/archive/session_workpackages/wp05_roi_workflow_consolidation.md`
- `docs/archive/session_workpackages/wp06_focus_method_expansion.md`
- `docs/archive/session_workpackages/wp07_tracking_core_baseline.md`
- `docs/session_workpackages/wp08_api_surface_preparation.md`
- `docs/session_workpackages/wp09_csharp_handover_hardening.md`
- `docs/session_workpackages/wp10_postprocess_baseline.md`
- `docs/session_workpackages/wp11_additional_frontends.md`

## PM Refinement Rule

When PM activates one package from this file:

1. choose one item from the current recommended order
2. use the detailed file under `docs/session_workpackages/` as the execution source
3. refine progress, sub-work-packages, and discoveries inside that detailed file
4. keep branch scope coherent and narrow
5. update this file only at the level of order, activation, and dependency changes

## Archive Rule

When a session work package is completed:

- move it to `docs/archive/session_workpackages/`
- update this PM file if that changes the current recommended order
- update `docs/STATUS.md` if the repository baseline changed
