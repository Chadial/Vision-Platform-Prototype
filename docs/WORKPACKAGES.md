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
| 30 | Interval Capture Timing And Polling Tightening | tighten bounded interval-capture timing evidence and active-run polling meaning on the integrated baseline | active lane | landed hardening slice; active interval polling now exposes non-fatal timing warnings during skipped intervals and reports compact completion summaries such as `completed with skipped_intervals=N` instead of leaving the end state implicit | `docs/session_workpackages/wp30_interval_capture_timing_polling_tightening.md` |
| 31 | Python Baseline Operations Runbook | document the stable operating baseline, known-good commands, hardware assumptions, and residual rules for real use | active lane | landed first operational-readiness slice; the compact central runbook now lives in `docs/PYTHON_BASELINE_RUNBOOK.md` without changing product scope | `docs/session_workpackages/wp31_python_baseline_operations_runbook.md` |
| 32 | Entry-Point And Launch Readiness Baseline | tighten the practical startup surface for the Python baseline through clearer launch paths and bounded readiness polish | active lane | landed second operational-readiness slice; the compact startup-surface reference now lives in `docs/ENTRYPOINT_AND_LAUNCH_BASELINE.md` without opening packaging work | `docs/session_workpackages/wp32_entrypoint_launch_readiness_baseline.md` |
| 33 | Host Contract Stability And Deferred Surface Clarification | define which host-facing command/status/result fields are stable now and which broader surfaces remain intentionally deferred | active lane | landed later-handover/productization clarification slice; the compact stable-now / deferred-later reference now lives in `docs/HOST_CONTRACT_BASELINE.md` without widening transport scope | `docs/session_workpackages/wp33_host_contract_stability_deferred_surface_clarification.md` |
| 34 | Interval-Capture Host Contract Normalization | bring the current bounded `interval-capture` path closer to the same host-envelope expectations used by the other bounded host commands | active lane | landed hardening slice; bounded `interval-capture` now returns selected save directory, frames written, stop reason, accepted capture bounds, and confirmed settings in the current host-envelope model | `docs/session_workpackages/wp34_interval_capture_host_contract_normalization.md` |
| 35 | Hardware Enumeration And Startup Residual Narrowing | narrow duplicate camera enumeration and remaining startup-log ambiguity on the tested hardware path | active lane | landed residual-driven hardware follow-up; raw Vimba X enumeration still duplicates `DEV_1AB22C046D81`, but the repository now prefers the richer candidate and preserves serial `067WH` in host-visible status while `VmbError.NotAvailable: -30` remains non-blocking residual noise | `docs/session_workpackages/wp35_hardware_enumeration_startup_residual_narrowing.md` |
| 36 | Detached Recording Lifecycle Decision Slice | document the current bounded recording meaning versus any later detached lifecycle control direction | active lane | landed decision-oriented handover slice; the stable-now versus deferred-later recording boundary now lives in `docs/RECORDING_LIFECYCLE_BOUNDARY.md` without implementing detached lifecycle control | `docs/session_workpackages/wp36_detached_recording_lifecycle_decision_slice.md` |
| 37 | Python Baseline Operator Start Helper | reduce repeated local startup friction with one bounded helper if justified | active lane | landed operational-readiness polish slice; `scripts/run_python_baseline.ps1` now provides one thin local convenience wrapper over the existing `.venv` plus `run_camera_cli.py` path without becoming a new startup contract | `docs/session_workpackages/wp37_python_baseline_operator_start_helper.md` |
| 38 | Selective Offline Follow-Up | preserve one bounded offline-expansion option only when a concrete user need appears | active lane | landed selective-expansion slice; the compact offline focus-report bundle now adds one additive summary line for entry count, traceability coverage, and the current highest-score image without widening into explorer or export scope | `docs/session_workpackages/wp38_selective_offline_followup.md` |
| 39 | Module Documentation Audit And Shrink Pass | refresh module-local docs, shrink stale local roadmaps, and reduce drift between local module docs and the post-closure baseline | active lane | landed bounded meta-documentation cleanup slice; active-module roadmaps were shrunk, stale transition wording reduced, and module-local doc roles clarified without central PM rewrite | `docs/session_workpackages/wp39_module_documentation_audit_and_shrink_pass.md` |
| 40 | Vision Platform Control And Imaging Physical Migration | move current control and optional imaging implementation behind the preferred `src/vision_platform` boundary while preserving compatibility imports | active lane | landed first post-closure architecture-convergence slice; `vision_platform` now owns bootstrap/control/imaging implementation directly while `camera_app` remains the compatibility shim layer | `docs/session_workpackages/wp40_vision_platform_control_imaging_physical_migration.md` |
| 41 | Vision Platform Storage Physical Migration | move storage and persistence helpers behind the preferred `src/vision_platform` boundary while preserving current behavior | active lane | landed second architecture-convergence slice; storage-facing legacy services now import platform-owned file-naming and frame-writer helpers directly while `camera_app.storage` remains the compatibility shim layer | `docs/session_workpackages/wp41_vision_platform_storage_physical_migration.md` |
| 42 | Vision Platform Namespace Coverage And Compatibility Audit | tighten trust in the preferred `vision_platform` import surface while keeping remaining compatibility shims explicit | active lane | landed trust-and-shim audit slice; current remaining `camera_app` dependencies are now bounded, tested, and documented as intentional compatibility seams rather than silent drift | `docs/session_workpackages/wp42_vision_platform_namespace_coverage_and_compatibility_audit.md` |
| 43 | Python Baseline Packaging Manifest And Environment Guardrails | make the bounded local Python baseline easier to set up and re-enter without pretending to solve full product packaging | active lane | landed operational-readiness follow-up; the package manifest now exposes `vision-platform-cli`, bootstrap output carries clearer install guardrails, and the bounded local install contract now lives in `docs/PYTHON_BASELINE_ENVIRONMENT.md` | `docs/session_workpackages/wp43_python_baseline_packaging_manifest_and_environment_guardrails.md` |
| 44 | Bounded API Adapter Command Surface | expose one narrow adapter-facing API slice only when a real integration consumer justifies it | active lane | landed selective-expansion slice; `api_service` now owns the bounded transport-neutral command-envelope payload family reused by the current CLI without introducing framework or transport runtime scope | `docs/session_workpackages/wp44_bounded_api_adapter_command_surface.md` |
| 45 | Stored Camera Configuration Profiles Baseline | introduce one bounded named profile baseline over the current host-neutral `CameraConfiguration` path | active lane | landed post-closure operational-readiness / selective-expansion slice; the CLI now resolves repo-local camera-class-first profiles through `configs/camera_configuration_profiles.json`, starting with a `default` profile and continuing to reuse the existing capability-aware configuration path | `docs/session_workpackages/wp45_stored_camera_configuration_profiles_baseline.md` |
| 46 | Camera Alias And ID Resolution Baseline | introduce one bounded alias-to-camera-id resolution layer above the current explicit camera-selection path | active lane | landed post-closure operational-readiness slice; the camera CLI now supports repo-local alias resolution through `configs/camera_aliases.json`, including the tested example alias `tested_camera`, while preserving direct explicit `camera_id` support and avoiding device-inventory scope | `docs/session_workpackages/wp46_camera_alias_and_id_resolution.md` |
| 47 | Traceability Control Context Extension | carry additive alias and profile-selection context into the existing snapshot and bounded-recording traceability path | active lane | landed post-closure data/logging follow-up; snapshot and bounded recording now preserve `camera_alias` and optional profile identity in stable traceability context when the current request path provides them, while the offline stable-context consumer exposes those fields additively | `docs/session_workpackages/wp47_traceability_control_context_extension.md` |
| 50 | Display Geometry Service Extraction | extract reusable viewport geometry from the OpenCV preview so later UI and host-facing work can share one headless mapping core | active lane | implemented on the current architecture baseline; OpenCV preview now consumes a headless geometry service and dedicated geometry coverage exists | `docs/session_workpackages/wp50_display_geometry_service_extraction.md` |
| 51 | Shared Preview Interaction Command Layer | introduce a shared preview interaction/action layer above geometry and below concrete UI event systems | active lane | implemented on the current architecture branch; OpenCV preview now translates HighGUI input into shared interaction commands with dedicated service coverage | `docs/session_workpackages/wp51_shared_preview_interaction_command_layer.md` |
| 52 | Overlay And Preview Status Model Definition | define UI-agnostic overlay/status models once geometry and interaction ownership are separated | active lane | implemented on the current architecture baseline; OpenCV preview now formats and renders shared descriptive status / overlay models | `docs/session_workpackages/wp52_overlay_and_preview_status_model_definition.md` |
| 53 | Local Working UI Shell Baseline | add a first pragmatic local UI shell on top of the extracted geometry and interaction layers | active lane | implemented as a bounded wxPython local shell over the shared controller/preview/display stack while OpenCV remains the fallback/reference path | `docs/session_workpackages/wp53_local_working_ui_shell_baseline.md` |
| 54 | wx Shell Hardware Enablement | add one bounded real-hardware startup path for the existing wxPython shell | active lane | implemented; the wx shell now reuses the same headless source-selection, alias/profile, and configuration startup semantics on both simulated and hardware-backed paths | `docs/session_workpackages/wp54_wx_shell_hardware_enablement.md` |
| 55 | Hardware Audit & Incident Logging Baseline | establish structured auditing for extraordinary camera states and incidents | current next | operational-readiness follow-up now that wx-shell hardware enablement exists | `docs/session_workpackages/wp55_hardware_audit_and_incident_logging_baseline.md` |
| 56 | CLI Help & Documentation | refine CLI help and human-readable command documentation | queued | operational-readiness polish behind the current architecture and hardware-shell chain | `docs/session_workpackages/wp56_cli_help_and_command_documentation.md` |

## Immediate PM Backlog

These are the work-package groups PM should treat as the current actionable post-closure backlog categories:

1. residual-driven hardening after the now-implemented `WP50` to `WP54` architecture/frontend chain, starting with hardware audit/logging
2. residual-driven hardening
3. operational readiness and productization polish after the architecture chain is prepared

Current prepared post-closure sequence:

- `WP50 Display Geometry Service Extraction` implemented on the integrated architecture baseline
- `WP51 Shared Preview Interaction Command Layer` implemented on the current branch
- `WP53 Local Working UI Shell Baseline` implemented as a bounded wxPython shell baseline
- `WP54 wx Shell Hardware Enablement` implemented as the bounded real-device startup follow-up for the existing shell
- `WP55 Hardware Audit & Incident Logging Baseline`
- defer `WP56` unless a concrete operational-help defect outranks the hardware-facing slices above it

Most recently landed detailed packages:

- `docs/session_workpackages/wp30_interval_capture_timing_polling_tightening.md`
  - landed narrow timing/polling follow-up; interval capture now surfaces non-fatal timing warnings while active and records a compact completion summary when skipped intervals occurred, with fresh March 30 real-device evidence showing active warnings plus a final `completed with skipped_intervals=7` status on `DEV_1AB22C046D81`
- `docs/session_workpackages/wp35_hardware_enumeration_startup_residual_narrowing.md`
  - landed residual-narrowing follow-up; raw Vimba X enumeration still duplicates `DEV_1AB22C046D81`, but the repository now prefers the richer duplicate candidate and preserves the richer pre-open serial `067WH` in host-visible status even when the opened camera object degrades to `N/A`
- `docs/session_workpackages/wp36_detached_recording_lifecycle_decision_slice.md`
  - landed decision-oriented handover slice; current `recording` is now explicitly documented as bounded in-process recording on one live subsystem boundary, while detached multi-invocation lifecycle control remains intentionally deferred
- `docs/session_workpackages/wp37_python_baseline_operator_start_helper.md`
  - landed operational-readiness polish slice; `scripts/run_python_baseline.ps1` now gives one bounded PowerShell convenience helper for repeated local CLI startup without replacing the preferred package entry point
- `docs/session_workpackages/wp39_module_documentation_audit_and_shrink_pass.md`
  - landed meta-documentation cleanup slice; stale module-local `ROADMAP.md` / `STATUS.md` wording was reduced and module-doc roles were tightened without broad doc rewrites
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

- `WP31` is now landed as the first compact operational-readiness runbook slice
- `WP32` is now landed as the startup-surface follow-up to that runbook slice
- `WP33` is now landed as the first explicit host-contract stability / deferred-scope clarification slice
- `WP34` is now landed as the bounded `interval-capture` host-contract normalization slice
- `WP35` is now landed as the bounded enumeration / startup residual-narrowing slice
- `WP36` is now landed as the bounded detached-recording lifecycle decision slice
- `WP37` is now landed as the bounded operator-start convenience slice
- `WP38` remains conditional selective expansion only
- `WP39` is now landed as the bounded module-documentation trust / shrink slice
- `WP12` through `WP26` should now be read primarily as the landed Extended MVP closure history that established the current Python working baseline
- `WP27` through `WP30` are already landed post-closure hardening / diagnostics slices on top of that baseline
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
10. treat `WP30` as the landed interval timing / polling clarification slice for the current integrated baseline
11. treat `WP31` as the landed compact runbook slice for the current Python baseline
12. treat `WP32` as the landed startup and launcher-clarity slice for the current Python baseline
13. treat `WP33` as the landed host-contract stability / deferred-scope clarification slice for the current bounded host surface
14. treat `WP34` as the landed bounded `interval-capture` normalization slice inside the current host-envelope baseline
15. treat `WP35` as the landed enumeration / startup residual-narrowing slice on the tested camera path
16. treat `WP36` as the landed recording-lifecycle boundary clarification slice
17. treat `WP37` as the landed operator-start convenience slice and `WP38` as conditional selective expansion only
18. treat `WP39` as the landed module-doc governance / shrink slice
19. treat `WP40` as the landed first architecture-convergence slice; `vision_platform.bootstrap`, `vision_platform.control`, and `vision_platform.imaging` now own the implementation while `camera_app` paths stay as compatibility shims
20. treat `WP41` as the landed storage/persistence follow-up; legacy storage import paths now consume platform-owned helpers while `camera_app.storage` remains the compatibility shim layer
21. treat `WP42` as the landed trust-and-shim audit; remaining `camera_app` dependencies inside `vision_platform` are now tested and documented as explicit compatibility seams
22. treat `WP43` as landed; the bounded package-manifest and environment-contract guardrails are now explicit through `vision-platform-cli`, bootstrap output, and `docs/PYTHON_BASELINE_ENVIRONMENT.md`
23. treat `WP38` and `WP44` as landed selective-expansion slices rather than as open default lanes
24. treat `WP45` as the landed bounded profile-baseline slice over the existing `CameraConfiguration` path rather than as a property-store or alias-system expansion
25. treat `WP46` as the landed bounded alias-to-camera-id convenience slice rather than as a discovery or inventory lane
26. treat `WP47` as the landed additive traceability follow-up for alias and profile-selection context rather than as a broader host-contract or inventory expansion
27. treat `WP50` as the implemented headless geometry slice on the integrated architecture baseline
28. treat `WP51` as the implemented shared interaction slice on the current branch
29. treat `WP52` as implemented; shared preview-status and overlay models now sit above OpenCV formatting and drawing
30. treat `WP53` as implemented; one bounded wxPython local shell now exercises the shared controller/preview/display stack while OpenCV remains the fallback/reference path
31. treat `WP54` as implemented; the wx shell now has a bounded real-hardware startup path without introducing UI-private bootstrap logic
32. make `WP55` the current next slice before opening CLI-help polish
33. defer `WP56` unless a concrete help/documentation defect outranks the hardware-facing slices above it
34. continue to derive any further technical slice from concrete residuals or explicit user direction instead of reopening broad closure logic

## Recommended Next Detailed Work Package

`WP55 Hardware Audit & Incident Logging Baseline`

Reason:

- the bounded wx shell can now start against the tested hardware path, so the next justified residual is no longer shell bootstrapping
- the next narrower operational gap is structured audit evidence for extraordinary hardware warnings, failures, and degraded startup states
- `WP55` now follows naturally from the April 7, 2026 manual reruns, which still show non-blocking SDK noise and access-mode warnings worth classifying and preserving more explicitly
- delaying `WP55` would keep those extraordinary cases spread across ad-hoc terminal logs instead of one bounded append-only audit path

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
- `docs/session_workpackages/wp34_interval_capture_host_contract_normalization.md`
- `docs/session_workpackages/wp35_hardware_enumeration_startup_residual_narrowing.md`
- `docs/session_workpackages/wp36_detached_recording_lifecycle_decision_slice.md`
- `docs/session_workpackages/wp37_python_baseline_operator_start_helper.md`
- `docs/session_workpackages/wp38_selective_offline_followup.md`
- `docs/session_workpackages/wp39_module_documentation_audit_and_shrink_pass.md`
- `docs/session_workpackages/wp40_vision_platform_control_imaging_physical_migration.md`
- `docs/session_workpackages/wp41_vision_platform_storage_physical_migration.md`
- `docs/session_workpackages/wp42_vision_platform_namespace_coverage_and_compatibility_audit.md`
- `docs/session_workpackages/wp43_python_baseline_packaging_manifest_and_environment_guardrails.md`
- `docs/session_workpackages/wp44_bounded_api_adapter_command_surface.md`
- `docs/session_workpackages/wp45_stored_camera_configuration_profiles_baseline.md`
- `docs/session_workpackages/wp46_camera_alias_and_id_resolution.md`
- `docs/session_workpackages/wp47_traceability_control_context_extension.md`
- `docs/session_workpackages/wp50_display_geometry_service_extraction.md`
- `docs/session_workpackages/wp51_shared_preview_interaction_command_layer.md`
- `docs/session_workpackages/wp52_overlay_and_preview_status_model_definition.md`
- `docs/session_workpackages/wp53_local_working_ui_shell_baseline.md`
- `docs/session_workpackages/wp54_wx_shell_hardware_enablement.md`
- `docs/session_workpackages/wp55_hardware_audit_and_incident_logging_baseline.md`
- `docs/session_workpackages/wp56_cli_help_and_command_documentation.md`

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
- `Interval Capture Timing And Polling Tightening` now has its landed execution-ready file at `docs/session_workpackages/wp30_interval_capture_timing_polling_tightening.md`
- `Python Baseline Operations Runbook` now has its landed execution-ready file at `docs/session_workpackages/wp31_python_baseline_operations_runbook.md`
- `Entry-Point And Launch Readiness Baseline` now has its landed execution-ready file at `docs/session_workpackages/wp32_entrypoint_launch_readiness_baseline.md`
- `Host Contract Stability And Deferred Surface Clarification` now has its landed execution-ready file at `docs/session_workpackages/wp33_host_contract_stability_deferred_surface_clarification.md`
- `Interval-Capture Host Contract Normalization` now has its landed execution-ready file at `docs/session_workpackages/wp34_interval_capture_host_contract_normalization.md`
- `Hardware Enumeration And Startup Residual Narrowing` now has its landed execution-ready file at `docs/session_workpackages/wp35_hardware_enumeration_startup_residual_narrowing.md`
- `Detached Recording Lifecycle Decision Slice` now has its landed execution-ready file at `docs/session_workpackages/wp36_detached_recording_lifecycle_decision_slice.md`
- `Python Baseline Operator Start Helper` now has its landed execution-ready file at `docs/session_workpackages/wp37_python_baseline_operator_start_helper.md`
- `Selective Offline Follow-Up` now has its landed execution-ready file at `docs/session_workpackages/wp38_selective_offline_followup.md`
- `Module Documentation Audit And Shrink Pass` now has its landed execution-ready file at `docs/session_workpackages/wp39_module_documentation_audit_and_shrink_pass.md`
- `Vision Platform Control And Imaging Physical Migration` now has its landed execution-ready file at `docs/session_workpackages/wp40_vision_platform_control_imaging_physical_migration.md`
- `Vision Platform Storage Physical Migration` now has its landed execution-ready file at `docs/session_workpackages/wp41_vision_platform_storage_physical_migration.md`
- `Vision Platform Namespace Coverage And Compatibility Audit` now has its landed execution-ready file at `docs/session_workpackages/wp42_vision_platform_namespace_coverage_and_compatibility_audit.md`
- `Python Baseline Packaging Manifest And Environment Guardrails` now has its landed execution-ready file at `docs/session_workpackages/wp43_python_baseline_packaging_manifest_and_environment_guardrails.md`
- `Bounded API Adapter Command Surface` now has its landed execution-ready file at `docs/session_workpackages/wp44_bounded_api_adapter_command_surface.md`
- `Stored Camera Configuration Profiles Baseline` now has its landed execution-ready file at `docs/session_workpackages/wp45_stored_camera_configuration_profiles_baseline.md`
- `Camera Alias And ID Resolution Baseline` now has its landed execution-ready file at `docs/session_workpackages/wp46_camera_alias_and_id_resolution.md`
- `Traceability Control Context Extension` now has its landed execution-ready file at `docs/session_workpackages/wp47_traceability_control_context_extension.md`
- `Display Geometry Service Extraction` now has its implementation and execution-ready file at `docs/session_workpackages/wp50_display_geometry_service_extraction.md`
- `Shared Preview Interaction Command Layer` now has its implementation and execution-ready file at `docs/session_workpackages/wp51_shared_preview_interaction_command_layer.md`
- `Overlay And Preview Status Model Definition` is now implemented on the architecture baseline through `docs/session_workpackages/wp52_overlay_and_preview_status_model_definition.md`
- `Local Working UI Shell Baseline` is now implemented through `docs/session_workpackages/wp53_local_working_ui_shell_baseline.md`
- `wx Shell Hardware Enablement` is now implemented through `docs/session_workpackages/wp54_wx_shell_hardware_enablement.md`
- `Hardware Audit And Incident Logging Baseline` is now the current next execution-ready file at `docs/session_workpackages/wp55_hardware_audit_and_incident_logging_baseline.md`
- `CLI Help And Command Documentation` remains queued at `docs/session_workpackages/wp56_cli_help_and_command_documentation.md`

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
