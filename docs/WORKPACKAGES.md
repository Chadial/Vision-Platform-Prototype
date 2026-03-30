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

## Phase Transition

The repository should no longer be planned as if `Extended MVP Closure` were still the active phase.

That phase is now considered closed.

Historical meaning of the closed Extended MVP phase:

- establish one host-steerable Python camera baseline
- prove bounded real-hardware viability on the tested camera path
- land the first practical reliability, traceability, and offline-follow-up slices
- replace broad MVP ambiguity with one usable Python working reference baseline

What the closure result now means:

- the Python camera subsystem is a bounded, host-oriented, hardware-validated working baseline on the tested camera path
- future work should no longer default to "what is still needed to prove the MVP is real?"
- future work should now default to "what is the next justified hardening, productization, or selective expansion step on top of the closed Python baseline?"

## Post-Closure Python Baseline Lens

The active planning lens is now:

**Post-Closure Python Baseline = stable Python working reference baseline for hardening, operational readiness, controlled productization, and selective expansion**

This phase should optimize for four work types:

1. `Hardening`
   - smooth the last real friction points in the current baseline
   - continue lifecycle / cleanup follow-ups, host-readable diagnostics, bounded reliability polish, and small real-use rough-edge removal
2. `Operational readiness`
   - make the Python baseline easier to run, document, operate, and hand over
   - improve docs, packaging / startup paths, clearer stable contracts, and explicit activation / operating rules when needed
3. `Selective expansion`
   - open the next surface only when there is a concrete reason
   - allow broader host / transport, offline / measurement, or UI / frontend follow-ups only when justified by actual need
4. `Later product / handover preparation`
   - keep the next larger horizon visible without treating it as the default immediate lane
   - preserve C# handover, broader productization, additional frontends, and wider hardware / deployment coverage as later post-closure directions

This phase should **not** be treated as:

- another generic MVP-closure backlog
- a broad architecture rewrite phase
- proof that the Python baseline is still not usable
- default reopening of API, frontend, or hardware breadth without a concrete driver

## Closed Extended MVP Axes

These four axes should remain visible as the historical closure structure that produced the current working baseline.

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

The Extended MVP packages remain visible as the closed historical phase that established the current working baseline.

Post-closure packages should now be read as hardening, operational-readiness, productization, or selective-expansion candidates above that closed phase.

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
| 11 | Additional Frontends | prepare desktop and later web-capable paths | dormant | keep for later continuity; not part of the current post-closure default lane | `docs/session_workpackages/wp11_additional_frontends.md` |
| 12 | Host Control Closure | prove and tighten the host-steerable command/response and status-polling baseline | dormant | closed Extended MVP lane; first narrow slice landed through `WP12` | `docs/session_workpackages/wp12_host_control_closure.md` |
| 13 | Experiment Reliability Closure | narrow runtime and hardware risk for experiment-relevant recording and control flows | dormant | closed Extended MVP lane; first narrow slice landed through `WP13` | `docs/session_workpackages/wp13_experiment_reliability_closure.md` |
| 14 | Data And Logging Closure | make saved image, metadata, timestamp, and series structure experimentally usable | dormant | closed Extended MVP lane; first narrow slice landed through `WP14`, later extended by traceability follow-ups | `docs/session_workpackages/wp14_data_logging_closure.md` |
| 15 | Offline And Measurement Closure | prove that saved data is useful for offline focus and measurement-oriented follow-up | dormant | closed Extended MVP lane; first narrow slice landed through `WP15`, later extended by metadata-aware offline follow-ups | `docs/session_workpackages/wp15_offline_measurement_closure.md` |
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
| 26 | Hardware Revalidation Resume | resume one bounded real-hardware revalidation block once the camera is attached again | dormant | landed final bounded confidence rerun inside the closed Extended MVP phase; future reruns are residual-driven only | `docs/session_workpackages/wp26_hardware_revalidation_resume.md` |
| 27 | Hardware Lifecycle And Camera Release Hardening | narrow the remaining real-device lifecycle gap around camera release, process-to-process reuse, and cleanup determinism | active lane | landed first post-closure hardening slice after the bounded hardware baseline was already real | `docs/session_workpackages/wp27_hardware_lifecycle_camera_release_hardening.md` |
| 28 | Capability-Aware ROI Constraint Reporting | make ROI width/height/offset constraint failures clearer and more host-usable on capability-backed camera paths | active lane | landed first post-closure diagnostics/polish slice; strict capability enforcement remains intact while host-readable guidance improved | `docs/session_workpackages/wp28_capability_aware_roi_constraint_reporting.md` |
| 29 | Hardware Startup Warning Classification | classify and narrow the remaining real-device startup warnings so hardware runs distinguish actionable lifecycle issues from SDK-noise residuals | active lane | landed post-closure diagnostics slice; current March 30 evidence shows `VmbError.NotAvailable: -30` persists as a non-blocking SDK log residual during successful `status` / `snapshot` runs, while capability probing still succeeds and does not surface it as `capability_probe_error` | `docs/session_workpackages/wp29_hardware_startup_warning_classification.md` |
| 30 | Interval Capture Timing And Polling Tightening | tighten bounded interval-capture timing evidence and active-run polling meaning on the integrated baseline | current next | next prepared hardening slice; narrow the current skipped-interval / timing-confidence residual without redesigning scheduling or transport | `docs/session_workpackages/wp30_interval_capture_timing_polling_tightening.md` |
| 31 | Python Baseline Operations Runbook | document the stable operating baseline, known-good commands, hardware assumptions, and residual rules for real use | queued | first operational-readiness slice; make the post-closure Python baseline easier to run and trust without changing product scope | `docs/session_workpackages/wp31_python_baseline_operations_runbook.md` |
| 32 | Entry-Point And Launch Readiness Baseline | tighten the practical startup surface for the Python baseline through clearer launch paths and bounded readiness polish | queued | second operational-readiness slice; improve how the current baseline is started and handed over without building a full installer | `docs/session_workpackages/wp32_entrypoint_launch_readiness_baseline.md` |
| 33 | Host Contract Stability And Deferred Surface Clarification | define which host-facing command/status/result fields are stable now and which broader surfaces remain intentionally deferred | queued | first later-handover/productization slice; make the current host baseline easier to hand over without widening transport scope | `docs/session_workpackages/wp33_host_contract_stability_deferred_surface_clarification.md` |

## Immediate PM Backlog

These are the work-package groups PM should treat as the current actionable post-closure backlog categories:

1. residual-driven hardening
2. operational readiness and productization polish
3. selective expansion only when justified

Current prepared post-closure sequence:

1. `WP30 Interval Capture Timing And Polling Tightening`
2. `WP31 Python Baseline Operations Runbook`
3. `WP32 Entry-Point And Launch Readiness Baseline`
4. `WP33 Host Contract Stability And Deferred Surface Clarification`

Most recently landed detailed packages:

- `docs/session_workpackages/wp29_hardware_startup_warning_classification.md`
  - landed narrow diagnostics follow-up; fresh March 30 serial hardware `status` and `snapshot(.bmp)` proofs showed that `vmbpyLog <VmbError.NotAvailable: -30>` still appears during successful runs, but the current host/status surface remains successful with `capabilities_available=True` and `capability_probe_error=None`, so the line is currently classified as non-blocking SDK/logging residual rather than active startup failure
- `docs/session_workpackages/wp28_capability_aware_roi_constraint_reporting.md`
  - landed narrow follow-up to improve host-usable ROI constraint reporting around width/height/offset increments and ranges, including clearer CLI-side configuration errors
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

Current explicitly activated detailed package state:

- `WP30` is the current default prepared post-closure activation
- `WP31` through `WP33` are prepared as the first operational-readiness and later-handover follow-ups
- `WP12` through `WP26` should now be read primarily as the landed Extended MVP closure history that established the current Python working baseline
- `WP27`, `WP28`, and `WP29` are already landed post-closure hardening / diagnostics slices on top of that baseline
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

### Layer 3: Closed Extended MVP

Goal:

- preserve the now-closed phase that established the bounded Python working baseline
- retain visibility of the host-control, reliability, data/logging, and offline slices that made the baseline real
- avoid reopening this phase as if its core closure question were still unresolved

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
- `WP28` is now landed as the narrow capability-aware ROI constraint reporting follow-up
- this layer is now historical continuity, not the default active planning lens

### Layer 4: Post-Closure Python Baseline

Goal:

- operate from the now-usable Python working baseline
- prioritize hardening, operational readiness, controlled productization, and selective expansion
- only open new technical slices when they are justified by concrete residuals, operational friction, or a deliberate new scope decision

Primary work types in this layer:

1. `Hardening`
   - remaining lifecycle or diagnostics hardening
   - bounded reliability polish
   - real-use friction removal without broad redesign
2. `Operational readiness`
   - clearer docs, startup paths, packaging, and operating rules
   - clearer stable contracts and activation boundaries
3. `Selective expansion`
   - selective API, offline, frontend, or measurement follow-up only when justified
4. `Later product / handover preparation`
   - preserve broader C# handover, productization, additional frontend work, and wider hardware / deployment scope as the next larger horizon rather than the default immediate stream
### Layer 5: Later Breadth Expansion

Goal:

- keep later breadth visible without letting it outrun the closure phase
- only reopen broader frontend, transport, tracking, or handover expansion after the post-closure baseline hardening priorities are explicitly judged ready for it

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
7. treat `WP12` through `WP26` as the closed Extended MVP foundation rather than as still-open proof work
8. treat `WP27` and `WP28` as the first landed post-closure hardening slices
9. treat `WP29` as the landed startup-warning classification slice that narrowed the current `NotAvailable` residual to non-blocking SDK/logging noise on the successful tested path
10. treat `WP30` as the next residual-driven hardening slice after that clarification
11. treat `WP31` and `WP32` as the first operational-readiness sequence for making the Python baseline easier to run and trust
12. treat `WP33` as the first explicit later-handover clarification slice without widening the current host transport surface
13. select any further technical slice only from concrete residuals or an explicit user-directed lane, then revisit tracking, broader API, C# handover widening, and additional frontends as post-closure expansion candidates rather than closure obligations

## Recommended Next Detailed Work Package

If the user does not explicitly redirect the session, the next PM-recommended execution-ready package is:

- `WP30 Interval Capture Timing And Polling Tightening`

Reason:

- the repository already has a usable Python working baseline with command, preview, recording, storage, traceability, offline reuse, and bounded real-hardware evidence
- the Extended MVP closure question is no longer "is there a real baseline?" but "what is the next justified improvement on top of that baseline?"
- the startup-warning residual has now been narrowed enough to classify the current `NotAvailable` line as non-blocking SDK/logging noise on the successful tested path
- the next most concrete remaining residual is interval-capture timing confidence
- broad frontend preparation, transport growth, offline tooling growth, and C# handover remain meaningful later, but they are now post-closure phase options rather than unfinished MVP proof obligations

## Fresh Agent Decision Rule

When a fresh agent is not explicitly assigned a package:

1. read `AGENTS.md`
2. read `docs/SESSION_START.md`
3. read `docs/MODULE_INDEX.md`
4. read `docs/WORKPACKAGES.md`
5. choose the package marked `current next`, unless the user or current branch scope clearly overrides it; if no package is marked `current next`, derive the next smallest justified post-closure slice from concrete residuals or the user's explicit direction
6. if that package does not yet have a detailed session file, derive the narrowest execution-ready session work-package file from the selected post-closure need or explicitly chosen expansion lane before implementation
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
- `docs/session_workpackages/wp29_hardware_startup_warning_classification.md`
- `docs/session_workpackages/wp30_interval_capture_timing_polling_tightening.md`
- `docs/session_workpackages/wp31_python_baseline_operations_runbook.md`
- `docs/session_workpackages/wp32_entrypoint_launch_readiness_baseline.md`
- `docs/session_workpackages/wp33_host_contract_stability_deferred_surface_clarification.md`

The Extended MVP closure lanes are now historical context rather than the active PM lens.

New detailed execution-ready files should now be created only when a concrete post-closure hardening, productization, or selective-expansion slice is actually chosen.

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
- `Capability-Aware ROI Constraint Reporting` now has its landed execution-ready file at `docs/session_workpackages/wp28_capability_aware_roi_constraint_reporting.md`
- `Hardware Startup Warning Classification` now has its landed execution-ready file at `docs/session_workpackages/wp29_hardware_startup_warning_classification.md`
- `Interval Capture Timing And Polling Tightening` now has its prepared execution-ready file at `docs/session_workpackages/wp30_interval_capture_timing_polling_tightening.md`
- `Python Baseline Operations Runbook` now has its prepared execution-ready file at `docs/session_workpackages/wp31_python_baseline_operations_runbook.md`
- `Entry-Point And Launch Readiness Baseline` now has its prepared execution-ready file at `docs/session_workpackages/wp32_entrypoint_launch_readiness_baseline.md`
- `Host Contract Stability And Deferred Surface Clarification` now has its prepared execution-ready file at `docs/session_workpackages/wp33_host_contract_stability_deferred_surface_clarification.md`

## PM Refinement Rule

When PM activates one package from this file:

1. choose one item from the current recommended order
2. if a detailed file already exists, use it as the execution source
3. if the selected package is a new post-closure need without a detailed file yet, first create one narrow execution-ready session work-package file for that slice
4. refine progress, sub-work-packages, and discoveries inside that detailed file
5. keep branch scope coherent and narrow
6. update this file only at the level of order, activation, and dependency changes

## Archive Rule

When a session work package is completed:

- move it to `docs/archive/session_workpackages/`
- update this PM file if that changes the current recommended order
- update `docs/STATUS.md` if the repository baseline changed
