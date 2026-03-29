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
2. treat the current Python camera baseline as already broad enough to justify a closure phase instead of immediate breadth expansion
3. keep OpenCV UI work separate and bounded instead of letting UI expansion define the next phase
4. treat hardware work as evidence-driven closure work, not as a permanently separate stream
5. prioritize host control, runtime reliability, data/logging, and offline experiment usability over new frontend breadth
6. keep tracking, broad API expansion, C# handover widening, and further frontends visible as later lanes rather than the next default step

## Extended MVP Lens

The next project phase should not be planned as breadth expansion.

It should be planned as:

**Extended MVP = host-steerable, hardware-relevant Python camera working prototype**

This tactical lens narrows the broad platform roadmap into a product-near closure phase aimed at replacing the previous third-party camera executable in the AMB context with a controlled Python subsystem.

Primary users for this phase:

1. the developer
2. the AMB control software as the host/master system

This means the next PM default should optimize for:

1. host-callable commands with structured results
2. stable runtime status polling during active experiments
3. experiment-safe recording, failure handling, and reproducibility
4. usable saved image and metadata structures for later analysis
5. offline focus and measurement usefulness of stored data

This phase does **not** treat the following as default next-step priorities:

- additional large frontend shells
- broad web-capable work
- speculative transport expansion
- broad tracking expansion
- C#-parallel work beyond what is directly justified by the current Python control surface

## Closure Axes

The current PM should derive the next work from four tactical closure axes rather than from broad roadmap breadth alone.

### 1. Host Control Closure

Question:

- is it practically proven that an external host can configure, trigger, stop, and query the Python camera subsystem reliably through a structured command/response path plus status polling?

Focus:

- host-callable commands
- structured command results
- confirmation of applied settings
- stable host-readable status payloads
- failure and readiness reporting

### 2. Experiment Reliability Closure

Question:

- is it practically proven that the system survives realistic experiment runs with acceptable reliability on the relevant hardware path?

Focus:

- start/stop robustness
- recording robustness
- hardware-backed revalidation
- recovery behavior
- bounded and reproducible validation slices

### 3. Data And Logging Closure

Question:

- is it practically proven that saved images, naming, settings, timestamps, and folder structure are experiment-usable and traceable?

Focus:

- explicit save-target behavior
- deterministic series structure
- image-plus-metadata linkage
- camera and system timestamps
- settings traceability
- practical visible formats such as TIFF, PNG, and BMP where appropriate

### 4. Offline And Measurement Closure

Question:

- is it practically proven that stored snapshots and series are useful for offline focus checks, measurement-oriented inspection, and experiment follow-up analysis?

Focus:

- stored-image reuse
- offline focus/report utility
- measurement-oriented format choices
- data suitability for later experiment evaluation

## WP Overview

This is the current PM overview of work packages to activate or defer.

The existing archived packages remain part of the repository history.

The newly added Extended MVP packages define the next tactical planning lane without erasing that earlier sequence.

| PM Order | Work Package | Purpose | Activation State | Priority | Detailed File |
| --- | --- | --- | --- | --- | --- |
| 1 | Camera CLI Baseline Narrowing | keep the CLI intentionally thin and stable over the shared control layer | dormant | completed and archived; keep for continuity only | `docs/archive/session_workpackages/wp01_camera_cli.md` |
| 2 | Host Integration Command Surface | harden the shared host-neutral command surface for later CLI, API, and C# embedding reuse | dormant | completed and archived; keep for continuity only | `docs/archive/session_workpackages/wp02_host_integration_command_surface.md` |
| 3 | OpenCV UI Operator Follow-Up | continue bounded UI/operator work without leaking screen concerns into core services | dormant | completed and archived; keep for continuity only | `docs/archive/session_workpackages/wp03_opencv_ui_operator_block.md` |
| 4 | Hardware Revalidation Follow-Up | re-run selected hardware checks and capture new evidence when hardware is attached again | conditional | conditional / deferred until hardware is attached | `docs/session_workpackages/wp04_hardware_revalidation_follow_up.md` |
| 5 | ROI Workflow Consolidation | define ownership and reuse of ROI state across preview, snapshot, and analysis | dormant | completed and archived; keep for continuity only | `docs/archive/session_workpackages/wp05_roi_workflow_consolidation.md` |
| 6 | Focus Method Expansion | add a stronger focus-method slice beyond the current baseline | dormant | completed and archived; keep for continuity only | `docs/archive/session_workpackages/wp06_focus_method_expansion.md` |
| 7 | Tracking Core Baseline | establish the first edge/tracking foundation slice | dormant | completed and archived; keep for continuity only | `docs/archive/session_workpackages/wp07_tracking_core_baseline.md` |
| 8 | API Surface Preparation | prepare the first external adapter above the host-neutral control layer | dormant | completed and archived; keep for continuity only | `docs/archive/session_workpackages/wp08_api_surface_preparation.md` |
| 9 | C# Handover Hardening | identify and tighten contracts that are most likely to survive direct C# porting | dormant | completed and archived; keep for continuity only | `docs/archive/session_workpackages/wp09_csharp_handover_hardening.md` |
| 10 | Postprocess Baseline | define an offline evaluation path over stored images and analysis data | dormant | completed and archived; keep for continuity only | `docs/archive/session_workpackages/wp10_postprocess_baseline.md` |
| 11 | Additional Frontends | prepare desktop and later web-capable paths | dormant | keep for later continuity; not part of the default Extended MVP lane | `docs/session_workpackages/wp11_additional_frontends.md` |
| 12 | Host Control Closure | prove and tighten the host-steerable command/response and status-polling baseline | active lane | first Extended MVP closure lane; first narrow slice landed through `WP12` | `docs/session_workpackages/wp12_host_control_closure.md` |
| 13 | Experiment Reliability Closure | narrow runtime and hardware risk for experiment-relevant recording and control flows | current next | second Extended MVP closure lane; first narrow slice is active through `WP13` | `docs/session_workpackages/wp13_experiment_reliability_closure.md` |
| 14 | Data And Logging Closure | make saved image, metadata, timestamp, and series structure experimentally usable | active lane | third Extended MVP closure lane | to be created on activation |
| 15 | Offline And Measurement Closure | prove that saved data is useful for offline focus and measurement-oriented follow-up | queued | fourth Extended MVP closure lane | to be created on activation |

## Immediate PM Backlog

These are the work packages PM should treat as the current actionable backlog:

1. `Host Control Closure`
2. `Experiment Reliability Closure`
3. `Data And Logging Closure`
4. `Offline And Measurement Closure`

Current explicitly activated detailed package:

- `docs/session_workpackages/wp13_experiment_reliability_closure.md`
  - first narrow `Experiment Reliability Closure` slice
  - centers bounded recording lifecycle restart and recovery after selected failures

These are important but should not be treated as the main always-on stream:

1. `Hardware Revalidation Follow-Up`
2. `Camera CLI Baseline Narrowing`
3. `Host Integration Command Surface`
4. `OpenCV UI Operator Follow-Up`
5. `Additional Frontends`

These should remain queued behind the above:

1. `Tracking Core Baseline`
2. `API Surface Preparation`
3. `C# Handover Hardening`
4. `Postprocess Baseline`

## Rough PM Sequence

The PM should currently plan in these layers.

### Layer 1: Historical Baseline Stabilization And Narrowing

Goal:

- preserve continuity with the work already completed
- keep the earlier command, UI, ROI, focus, and API-baseline packages visible as already-landed groundwork
- avoid reopening old baseline packages unless a concrete defect appears

Detailed work-package files:

- `docs/archive/session_workpackages/wp01_camera_cli.md`
- `docs/archive/session_workpackages/wp02_host_integration_command_surface.md`
- `docs/archive/session_workpackages/wp03_opencv_ui_operator_block.md`
- `docs/session_workpackages/wp04_hardware_revalidation_follow_up.md`
- `docs/archive/session_workpackages/wp04_hardware_validation_phase_9.md`

### Layer 2: Historical Analysis MVP Boundary

Goal:

- retain the ROI/focus/tracking/postprocess history as completed groundwork
- keep those packages available as dependency context for the next closure-focused planning phase

Detailed work-package files:

- `docs/archive/session_workpackages/wp05_roi_workflow_consolidation.md`
- `docs/archive/session_workpackages/wp06_focus_method_expansion.md`
- `docs/archive/session_workpackages/wp07_tracking_core_baseline.md`

Detailed work-package files:

- `docs/archive/session_workpackages/wp08_api_surface_preparation.md`
- `docs/archive/session_workpackages/wp09_csharp_handover_hardening.md`
- `docs/archive/session_workpackages/wp10_postprocess_baseline.md`

### Layer 3: Extended MVP Closure

Goal:

- reinterpret the next project phase as closure, not breadth expansion
- prove that the Python camera subsystem is host-steerable, hardware-relevant, experiment-safe, and data-usable
- derive the next execution-ready branches from the four closure axes instead of from speculative future breadth

Current closure lanes:

1. `Host Control Closure`
2. `Experiment Reliability Closure`
3. `Data And Logging Closure`
4. `Offline And Measurement Closure`

Existing detailed support files:

- `docs/session_workpackages/wp04_hardware_revalidation_follow_up.md`
- `docs/session_workpackages/wp12_host_control_closure.md`
- `docs/session_workpackages/wp13_experiment_reliability_closure.md`

Current activation note:

- `Host Control Closure` is no longer only a planning lane and now has its first landed slice in `docs/session_workpackages/wp12_host_control_closure.md`
- `Experiment Reliability Closure` is now the active next lane through `docs/session_workpackages/wp13_experiment_reliability_closure.md`
- that slice is intentionally narrow and centers bounded recording lifecycle restart and recovery after selected failures
- the remaining closure lanes stay at PM-lane level until a later concrete slice is selected

### Layer 4: Later Breadth Expansion

Goal:

- keep later breadth visible without letting it outrun the closure phase
- only reopen broader frontend, transport, tracking, or handover expansion after the Extended MVP lane is sufficiently closed

Detailed work-package files:

- `docs/session_workpackages/wp11_additional_frontends.md`

## Current Recommended Order

The current coarse PM order should be:

1. treat the CLI baseline as intentionally narrow unless a concrete defect appears
2. treat the host-integration and bounded OpenCV follow-up packages as completed baseline-hardening work
3. do not open `Additional Frontends` by default, because frontend breadth is not the next tactical bottleneck
4. treat the first `Host Control Closure` slice as landed baseline hardening and move to `Experiment Reliability Closure` as the default next package
5. keep `Data And Logging Closure` as the next active lane directly behind it
6. use `Hardware Revalidation Follow-Up` as one supporting slice inside reliability closure whenever hardware is attached
7. open `Offline And Measurement Closure` after the command, runtime, and data/logging baseline is clearer
8. revisit tracking, broader API, C# handover widening, and additional frontends only after the closure phase has materially advanced

## Recommended Next Detailed Work Package

If the user does not explicitly redirect the session, the next PM-recommended execution-ready package is:

- `docs/session_workpackages/wp13_experiment_reliability_closure.md`

Reason:

- the repository already has a broad Python camera baseline with command, preview, recording, storage, and first hardware evidence
- the first host-control slice is already landed, so the next tactical need is to prove bounded recording lifecycle robustness and recovery
- the currently activated next slice is the reliability hardening path for repeated bounded recording and selected failure recovery
- broad frontend preparation is still meaningful later, but it is not the highest-value default next step for the current phase

## Fresh Agent Decision Rule

When a fresh agent is not explicitly assigned a package:

1. read `AGENTS.md`
2. read `docs/SESSION_START.md`
3. read `docs/MODULE_INDEX.md`
4. read `docs/WORKPACKAGES.md`
5. choose the package marked `current next`, unless the user or current branch scope clearly overrides it
6. if that package does not yet have a detailed session file, derive the narrowest execution-ready session work-package file from the selected closure lane before implementation
7. otherwise open that package's detailed `docs/session_workpackages/wpXX_*.md` file before implementation

## Detailed Package Inventory

The repository currently has explicit detailed session work-package files for the historical baseline packages and the still-valid later frontend/hardware placeholders:

- `docs/archive/session_workpackages/wp01_camera_cli.md`
- `docs/archive/session_workpackages/wp02_host_integration_command_surface.md`
- `docs/archive/session_workpackages/wp03_opencv_ui_operator_block.md`
- `docs/session_workpackages/wp04_hardware_revalidation_follow_up.md`
- `docs/archive/session_workpackages/wp05_roi_workflow_consolidation.md`
- `docs/archive/session_workpackages/wp06_focus_method_expansion.md`
- `docs/archive/session_workpackages/wp07_tracking_core_baseline.md`
- `docs/archive/session_workpackages/wp08_api_surface_preparation.md`
- `docs/archive/session_workpackages/wp09_csharp_handover_hardening.md`
- `docs/archive/session_workpackages/wp10_postprocess_baseline.md`
- `docs/session_workpackages/wp11_additional_frontends.md`
- `docs/session_workpackages/wp12_host_control_closure.md`
- `docs/session_workpackages/wp13_experiment_reliability_closure.md`

The new Extended MVP closure lanes are intentionally introduced first at the PM level.

Their detailed execution-ready files should be created only when a concrete closure slice is activated, so PM does not invent detailed branch work prematurely.

Current explicit activation:

- `Host Control Closure` now has its first landed slice at `docs/session_workpackages/wp12_host_control_closure.md`
- `Experiment Reliability Closure` now has the active next implementation-oriented package at `docs/session_workpackages/wp13_experiment_reliability_closure.md`
- the remaining closure lanes still intentionally wait for later activation

## PM Refinement Rule

When PM activates one package from this file:

1. choose one item from the current recommended order
2. if a detailed file already exists, use it as the execution source
3. if the selected package is one of the Extended MVP closure lanes, first create one narrow execution-ready session work-package file for that lane
4. refine progress, sub-work-packages, and discoveries inside that detailed file
5. keep branch scope coherent and narrow
6. update this file only at the level of order, activation, and dependency changes

## Archive Rule

When a session work package is completed:

- move it to `docs/archive/session_workpackages/`
- update this PM file if that changes the current recommended order
- update `docs/STATUS.md` if the repository baseline changed
