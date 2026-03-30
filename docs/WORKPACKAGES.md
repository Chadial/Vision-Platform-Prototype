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

When creating or materially refining future work packages, apply this precision discipline as well:

- explicitly distinguish the broader `Closure Lane` from the selected narrow slice
- explicitly name the `Slice Role`, such as `baseline`, `patch`, `extension`, `producer`, `consumer`, or `validation`
- explicitly state that the package does not close the whole lane unless that is genuinely true
- explicitly distinguish stable-context, run/session, and artifact/per-image scope whenever metadata, logging, traceability, save-artifact behavior, or offline artifact reuse is involved
- explicitly distinguish whether the package is structure-only, producer-facing, consumer-facing, or one narrow combination
- explicitly record unresolved policy choices rather than silently freezing or omitting them
- explicitly state the small gap the package closes and the larger concerns it intentionally defers

For future package generation, a short classification block or equivalent wording should make these points explicit:

- `Closure Lane`
- `Slice Role`
- `Scope Level`
- `Producer / Consumer / Structure impact`
- `What this package does not close`
- `Which policy questions remain open`

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
| 13 | Experiment Reliability Closure | narrow runtime and hardware risk for experiment-relevant recording and control flows | active lane | second Extended MVP closure lane; first narrow slice landed through `WP13` | `docs/session_workpackages/wp13_experiment_reliability_closure.md` |
| 14 | Data And Logging Closure | make saved image, metadata, timestamp, and series structure experimentally usable | active lane | third Extended MVP closure lane; first narrow slice landed through `WP14`, lane still open for traceability extensions | `docs/session_workpackages/wp14_data_logging_closure.md` |
| 15 | Offline And Measurement Closure | prove that saved data is useful for offline focus and measurement-oriented follow-up | active lane | fourth Extended MVP closure lane; first narrow slice landed through `WP15`, lane still open for metadata-aware offline reuse | `docs/session_workpackages/wp15_offline_measurement_closure.md` |
| 16 | Data And Logging Traceability Extension | add one stable artifact-level metadata traceability path for saved snapshot and bounded recording outputs | active lane | first post-`WP14` extension slice; landed through `WP16` with one shared folder-local appendable trace log for snapshot and bounded recording | `docs/session_workpackages/wp16_data_logging_traceability.md` |
| 17 | Offline And Measurement Metadata Extension | reuse saved artifact metadata in the offline report path so artifact context and focus results stay linked | active lane | landed narrow metadata-aware offline slice; compact postprocess reporting now joins folder-local traceability rows by saved image name | `docs/session_workpackages/wp17_offline_measurement_metadata_extension.md` |
| 18 | Focus Metadata Artifact Extension | define one narrow reusable artifact-level focus and analysis-ROI metadata baseline above the traceability path | active lane | landed narrow extension after `WP16`; focus summary metadata now requires an explicit aggregation basis, while exact defaults/bounds still need later testing and definition | `docs/session_workpackages/wp18_focus_metadata_artifact_extension.md` |
| 19 | Focus Metadata Producer Wiring | wire the artifact-level focus metadata producer into normal save flows without freezing broader statistics policy | active lane | landed narrow follow-up after `WP18`; snapshot and bounded-recording flows can now emit focus metadata when explicitly configured | `docs/session_workpackages/wp19_focus_metadata_producer_wiring.md` |
| 20 | Focus Metadata Policy Hardening | define and test explicit defaults, bounds, and validation policy for artifact-level focus summary metadata | active lane | landed narrow post-`WP19` policy slice; current summary fields now require `focus_method`, a positive integer `focus_score_frame_interval`, and non-negative `focus_value_stddev` values | `docs/session_workpackages/wp20_focus_metadata_policy_hardening.md` |
| 21 | Offline Stable Context Exposure | expose one compact folder-level stable-context summary from traceability headers in the offline focus report | active lane | landed narrow post-`WP20` consumer slice; the additive report-bundle path now exposes stable header context while the existing list-return path stays usable | `docs/session_workpackages/wp21_offline_stable_context_exposure.md` |
| 22 | Host Status Polling Hardening | tighten one narrow host-readable status payload slice during active experiment runs | active lane | landed bounded post-`WP21` closure slice; the adapter-facing status family now exposes a conservative additive active-run polling subset without redesigning core status models | `docs/session_workpackages/wp22_host_status_polling_hardening.md` |
| 23 | Host Command Confirmation Hardening | return one more explicit confirmed-settings subset for host-triggered capture and recording commands | active lane | landed host-control follow-up after `WP22`; command results now expose a narrower explicit confirmed-settings subset without widening the transport surface | `docs/session_workpackages/wp23_host_command_confirmation_hardening.md` |
| 24 | Run Identity And Trace Linkage | align one deterministic run identity across host results, traceability blocks, and recording-side metadata outputs | active lane | landed cross-lane linkage slice; the current host path now reuses the same narrow `run_id` across snapshot / bounded-recording results and traceability blocks | `docs/session_workpackages/wp24_run_identity_trace_linkage.md` |
| 25 | Experiment Recovery Validation Extension | prove one tighter simulator-first recovery block over host-driven recording failures and repeated restart behavior | active lane | landed reliability-focused validation slice; the integrated bootstrap/controller path now proves write-failure recovery plus repeated stop/restart idempotence without runtime redesign | `docs/session_workpackages/wp25_experiment_recovery_validation_extension.md` |
| 26 | Hardware Revalidation Resume | resume one bounded real-hardware revalidation block once the camera is attached again | active lane | landed bounded confidence rerun on March 30, 2026; future reruns stay conditional and should target concrete residual observations only | `docs/session_workpackages/wp26_hardware_revalidation_resume.md` |
| 27 | Hardware Lifecycle And Camera Release Hardening | narrow the remaining real-device lifecycle gap around camera release, process-to-process reuse, and cleanup determinism | active lane | landed follow-up after `WP26`; the current hardware path now reuses the already opened camera for capability probing and no longer reopened Vimba/camera immediately during initialization | `docs/session_workpackages/wp27_hardware_lifecycle_camera_release_hardening.md` |
| 28 | Capability-Aware ROI Constraint Reporting | make ROI width/height/offset constraint failures clearer and more host-usable on capability-backed camera paths | current next | narrow validation/reporting follow-up after landed `WP27`; keep strict capability enforcement but improve returned guidance | `docs/session_workpackages/wp28_capability_aware_roi_constraint_reporting.md` |

## Immediate PM Backlog

These are the work packages PM should treat as the current actionable backlog:

1. `Host Control Closure`
2. `Experiment Reliability Closure`
3. `Data And Logging Closure`
4. `Offline And Measurement Closure`

Most recently landed detailed packages:

- `docs/session_workpackages/wp28_capability_aware_roi_constraint_reporting.md`
  - newly prepared follow-up to improve host-usable ROI constraint reporting around width/height/offset increments and ranges
- `docs/session_workpackages/wp27_hardware_lifecycle_camera_release_hardening.md`
  - landed narrow lifecycle hardening follow-up; hardware capability probing now reuses the already opened driver camera and the March 30 serial `status -> status`, `snapshot -> status`, and `recording -> status` proofs no longer reproduced `camera already in use`
- `docs/session_workpackages/wp26_hardware_revalidation_resume.md`
  - landed the bounded March 30, 2026 real-device confidence rerun over the current integrated baseline, including preview readiness, snapshot, bounded recording, interval capture, active polling, traceability output, offline BMP reuse, and same-subsystem reuse without process restart
- `docs/session_workpackages/wp25_experiment_recovery_validation_extension.md`
  - landed the simulator-first integrated recovery proof for writer-side recording failure, repeated stop calls, and successful restart on the same subsystem path
- `docs/session_workpackages/wp24_run_identity_trace_linkage.md`
  - landed one deterministic `run_id` alignment across snapshot / bounded-recording host results, active bounded-recording polling, and saved-artifact traceability blocks
- `docs/session_workpackages/wp23_host_command_confirmation_hardening.md`
  - landed the narrow confirmed-settings subset for `snapshot` and bounded `recording` command results in the current CLI host surface
- `docs/session_workpackages/wp22_host_status_polling_hardening.md`
  - landed the additive active-run polling subset in the API-/CLI-facing status path for active bounded recording and interval capture
- `docs/session_workpackages/wp21_offline_stable_context_exposure.md`
  - landed the additive compact stable-context exposure path for offline focus reporting
- `docs/session_workpackages/wp20_focus_metadata_policy_hardening.md`
  - landed the first explicit shared validation policy for current focus-summary metadata fields
- `docs/session_workpackages/wp17_offline_measurement_metadata_extension.md`
  - landed the consumer-side offline metadata join over folder-local traceability data
- `docs/session_workpackages/wp18_focus_metadata_artifact_extension.md`
  - landed the explicit aggregation-basis requirement for stored focus-summary fields
- `docs/session_workpackages/wp19_focus_metadata_producer_wiring.md`
  - landed the explicit producer wiring for snapshot and bounded-recording save flows

Current explicitly activated detailed package:

- `WP26` is now landed as the bounded hardware-evidence refresh for the current integrated baseline
- `WP27` is now landed as the narrow lifecycle/cleanup hardening follow-up for the current real-device initialization seam
- `WP28` is now the default next narrow capability-aware ROI-validation follow-up
- `WP17`, `WP18`, `WP19`, `WP20`, `WP21`, `WP22`, `WP23`, `WP24`, and `WP25` are all landed metadata-, host-control-, or simulator-first reliability follow-ups and should no longer be treated as pending activation
- future hardware reruns remain conditional on local hardware attachment and should only be reopened for concrete residual observations such as the current `NotAvailable` startup log, duplicate camera enumeration behavior, or interval-timing quirks

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
- `docs/session_workpackages/wp14_data_logging_closure.md`
- `docs/session_workpackages/wp15_offline_measurement_closure.md`

Current activation note:

- `Host Control Closure` is no longer only a planning lane and now has its first landed slice in `docs/session_workpackages/wp12_host_control_closure.md`
- `Experiment Reliability Closure` now has its first landed slice in `docs/session_workpackages/wp13_experiment_reliability_closure.md`
- `Data And Logging Closure` now has its first landed slice in `docs/session_workpackages/wp14_data_logging_closure.md`
- that slice intentionally stayed narrow and centered `BMP` as an additional practical visible output format
- `Offline And Measurement Closure` now has its first landed slice in `docs/session_workpackages/wp15_offline_measurement_closure.md`
- that slice intentionally stayed narrow and centered offline focus-report reuse of saved `BMP` artifacts
- `WP16` is now landed and extends `Data And Logging Closure` at the traceability level with one shared folder-local appendable traceability log for snapshot and bounded recording
- `WP17` is now landed as the corresponding offline/reporting consumer slice over that traceability baseline
- `WP18` is now landed behind that and makes optional focus/analysis ROI artifact metadata more explicit without silently finalizing focus-summary aggregation defaults or bounds
- `WP19` is now landed behind `WP18` and wires that metadata into normal snapshot and bounded-recording save paths when explicitly configured
- `WP20` is now landed as the first explicit policy-hardening slice over those current focus-summary metadata structures
- `WP21` is now landed as the corresponding compact folder-level stable-context exposure slice above the same traceability baseline
- `WP22` is now landed as one narrow host-status polling hardening slice with an additive active-run polling subset above the existing status baseline
- `WP23` is now landed as the corresponding narrow command-confirmation slice for explicit resolved save-directory, file-shape, and bounded-recording confirmations
- `WP24` is now landed as the corresponding deterministic run-identity linkage slice across traceability and the current host path
- `WP25` is now landed as the corresponding simulator-first integrated recovery-validation slice
- `WP26` is now landed as one bounded real-device confidence rerun over the current integrated host/traceability/reliability baseline
- `WP27` is now landed as the narrow lifecycle/cleanup hardening follow-up for remaining real-device camera-release uncertainty
- `WP28` remains prepared as the narrow capability-aware ROI constraint reporting follow-up
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
4. treat the first `Host Control Closure`, `Experiment Reliability Closure`, `WP14`, and `WP15` slices as landed baseline hardening rather than full lane closure
5. treat `WP17`, `WP18`, `WP19`, `WP20`, and `WP21` as landed metadata-consumer, producer, policy, and stable-context hardening slices rather than as pending activation work
6. treat `WP22`, `WP23`, `WP24`, `WP25`, and `WP26` as landed baseline-hardening slices rather than as pending activation work
7. treat `WP27` as landed lifecycle hardening on the real-device initialization seam rather than as pending activation work
8. treat `WP28` as the default next narrow validation/reporting slice, then revisit tracking, broader API, C# handover widening, and additional frontends only after the closure phase has materially advanced

## Recommended Next Detailed Work Package

If the user does not explicitly redirect the session, the next PM-recommended execution-ready package is:

- activate `WP28` for `Capability-Aware ROI Constraint Reporting`

Reason:

- the repository already has a broad Python camera baseline with command, preview, recording, storage, and first hardware evidence
- the first host-control, reliability, visible-format, traceability, offline metadata-consumption, metadata-producer, metadata-policy, and stable-context slices are already landed
- the active-run polling, post-command confirmation, run-identity linkage, simulator-first recovery-validation, and bounded real-device confidence rerun slices are now landed
- the double-open capability-probe seam has now been narrowed in the current hardware baseline and the March 30 serial reuse proofs no longer reproduced `camera already in use`
- `WP28` now follows naturally by tightening host-usable reporting around capability-constrained ROI requests without changing the strict validation stance
- no broader default reopening of UI, transport, or history scope is justified by PM from this result alone
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
- `docs/session_workpackages/wp14_data_logging_closure.md`
- `docs/session_workpackages/wp15_offline_measurement_closure.md`
- `docs/session_workpackages/wp16_data_logging_traceability.md`
- `docs/session_workpackages/wp17_offline_measurement_metadata_extension.md`
- `docs/session_workpackages/wp18_focus_metadata_artifact_extension.md`
- `docs/session_workpackages/wp19_focus_metadata_producer_wiring.md`
- `docs/session_workpackages/wp20_focus_metadata_policy_hardening.md`
- `docs/session_workpackages/wp21_offline_stable_context_exposure.md`
- `docs/session_workpackages/wp22_host_status_polling_hardening.md`
- `docs/session_workpackages/wp23_host_command_confirmation_hardening.md`
- `docs/session_workpackages/wp24_run_identity_trace_linkage.md`
- `docs/session_workpackages/wp25_experiment_recovery_validation_extension.md`
- `docs/session_workpackages/wp26_hardware_revalidation_resume.md`
- `docs/session_workpackages/wp27_hardware_lifecycle_camera_release_hardening.md`
- `docs/session_workpackages/wp28_capability_aware_roi_constraint_reporting.md`

The new Extended MVP closure lanes are intentionally introduced first at the PM level.

Their detailed execution-ready files should be created only when a concrete closure slice is activated, so PM does not invent detailed branch work prematurely.

Current explicit activation:

- `Host Control Closure` now has its first landed slice at `docs/session_workpackages/wp12_host_control_closure.md`
- `Experiment Reliability Closure` now has its first landed slice at `docs/session_workpackages/wp13_experiment_reliability_closure.md`
- `Data And Logging Closure` now has its first landed implementation-oriented package at `docs/session_workpackages/wp14_data_logging_closure.md`
- `Offline And Measurement Closure` now has its first landed implementation-oriented package at `docs/session_workpackages/wp15_offline_measurement_closure.md`
- `Data And Logging Traceability Extension` now has its first landed implementation-oriented package at `docs/session_workpackages/wp16_data_logging_traceability.md`
- `Offline And Measurement Metadata Extension` now has its landed execution-ready file at `docs/session_workpackages/wp17_offline_measurement_metadata_extension.md`
- `Focus Metadata Artifact Extension` now has its landed execution-ready file at `docs/session_workpackages/wp18_focus_metadata_artifact_extension.md`
- `Focus Metadata Producer Wiring` now has its landed execution-ready file at `docs/session_workpackages/wp19_focus_metadata_producer_wiring.md`
- `Focus Metadata Policy Hardening` now has its landed execution-ready file at `docs/session_workpackages/wp20_focus_metadata_policy_hardening.md`
- `Offline Stable Context Exposure` now has its landed execution-ready file at `docs/session_workpackages/wp21_offline_stable_context_exposure.md`
- `Host Status Polling Hardening` now has its landed execution-ready file at `docs/session_workpackages/wp22_host_status_polling_hardening.md`
- `Host Command Confirmation Hardening` now has its landed execution-ready file at `docs/session_workpackages/wp23_host_command_confirmation_hardening.md`
- `Run Identity And Trace Linkage` now has its landed execution-ready file at `docs/session_workpackages/wp24_run_identity_trace_linkage.md`
- `Experiment Recovery Validation Extension` now has its landed execution-ready file at `docs/session_workpackages/wp25_experiment_recovery_validation_extension.md`
- `Hardware Revalidation Resume` now has its landed execution-ready file at `docs/session_workpackages/wp26_hardware_revalidation_resume.md`
- `Hardware Lifecycle And Camera Release Hardening` now has its landed execution-ready file at `docs/session_workpackages/wp27_hardware_lifecycle_camera_release_hardening.md`
- `Capability-Aware ROI Constraint Reporting` now has its prepared execution-ready file at `docs/session_workpackages/wp28_capability_aware_roi_constraint_reporting.md`

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
