# Status

## Source References

This status document should always be read and updated in relation to:

- `docs/WORKPACKAGES.md` for the active project-level work queue
- `docs/ROADMAP.md` for the repository-specific implementation phases
- `docs/GlobalRoadmap.md` for the broader Python -> C# -> web-capable target path

Each status update should state progress and gaps against both roadmaps.

## Current Branch

- `docs/wp80-workflow-realignment` is the current checked-out topic branch for the active workflow-first PM realignment slice
- `main` remains the latest integrated implementation baseline
- short-lived topic branches are created per active work package and merged back after local validation
- branch or general git housekeeping that changes repository-state truth must be reflected here when this section would otherwise drift from the actual git state

## Current Phase

- `Usable Camera Subsystem / Pre-Product Baseline`

## Current Product Direction

- first product goal: a running `Vision App / wxShell` that replaces the previous third-party software path and can be controlled by a host
- current product form: `Hybrid Companion`
- current operating balance:
  - a local shell remains visible, usable, and locally adjustable
  - a host can send the important camera/acquisition commands
  - the shell should reflect host-driven actions and current state without becoming the command authority itself
- near-term host staging:
  - Stage 1: test host
  - Stage 2: LabVIEW host
- next structural direction after this phase:
  - move toward a truly headless kernel
  - keep reusable camera/acquisition/workflow logic outside shell-specific UI composition

## Current Shell Role

- companion/monitor surface for host-driven operation
- debug/developer surface for the current bounded baseline
- functional replacement path for the previous third-party software
- still locally adjustable while it remains a standalone-running companion app

## Current Next

- `WP80 Delamination Recording Workflow Narrowing` is now the `current next`.
- default next-step derivation should now use the confirmed `Hybrid Companion` product reading through the three functional workflows rather than a broad generic subsystem-hardening lens.
- the repo-level orientation cleanup now also extends beyond the central PM docs: `README.md`, `docs/WORKFLOW.md`, `docs/NEXT_SESSION_ORDER.md`, `docs/project_overview.md`, and the secondary summary notes now point at the same current product reading instead of older post-closure wording
- `WP75 Reference Scenario Operator Path Tightening` is now landed; `docs/ENTRYPOINT_AND_LAUNCH_BASELINE.md` and `docs/MANUALS_INDEX.md` now expose one compact validated entry path for the official current workflows.
- `WP71 Reference Scenario Validation Narrowing` is now landed; the repository has one explicit repeatable validation block for the current technical anchor flows through `tests.test_reference_scenarios` and `scripts/launchers/run_reference_scenario_validation.py`.
- `WP70 Control And Imaging Compatibility Cleanup` remains complete on the topic branch and already archived as a finished refactor slice.
- the latest documentation-governance maintenance also landed: `docs/STATUS.md` is the authoritative repository status, `docs/WORKPACKAGES.md` is the authoritative repository queue, and `docs/PRIORITIES.md` / `docs/TARGET_MAP.md` are derived views only
- `WP81 Geometry Capture Workflow Narrowing` and `WP82 Setup Focus ROI Workflow Narrowing` are now the prepared next workflow packages behind `WP80`
- `WP76`, `WP77`, and `WP78` are no longer the default open residual lane; they stay dormant unless the workflow-first sequence exposes one concrete seam that actually needs them

## Immediate Priorities

- host commands to the running `Vision App / wxShell`
- visible reflection of host-driven actions and state in the wx shell
- wx shell settings-menu support as part of practical usability
- execution of the three confirmed functional workflows in practice
- then headless-kernel preparation

## Not Current Priorities

- broad transport or platform expansion by default
- broad MCP work
- broad product packaging
- broad additional frontend expansion
- full C# handover work
- full assisted-measurement-system build-out

## Confirmed Functional Workflows

### Workflow A: Delamination Recording

- purpose: record specimen behavior during the delamination test
- required technical functions:
  - preview
  - settings
  - recording start/stop
  - optional stop through practical `max frames reached` behavior when relevant

### Workflow B: Geometry Capture

- purpose: acquire overlapping specimen images for later geometric measurement and support-point spacing evaluation
- required technical functions:
  - preview
  - settings
  - snapshot

### Workflow C: Setup / Focus / ROI Adjustment

- purpose: set camera parameters, maximize focus, and define the relevant ROI before the main workflow
- required technical functions:
  - preview
  - settings
  - ROI/focus
  - optional control snapshot

## Current Must-Have Function Set

- preview
- settings
- snapshot
- recording start/stop
- max frames as the current practical stop condition
- ROI/focus

Current stop-condition note:

- in this phase, `conditional stop` should be read as the practical `max frames reached` case, not as a broad new stop-rule system

## Current Host Expectations

- define save location
- define core camera settings
- control acquisition
- obtain camera metadata
- support experiment documentation

Current phase note:

- this is the bounded Stage 1 test-host surface and the intended starting point for Stage 2 LabVIEW-host integration

Phase-1 mandatory host surface:

- `start`
- `stop`
- `max frames`
- `recording fps`
- `save path`
- settings:
  - shutter / exposure
  - hardware ROI
  - gain
- ROI enable / disable
- focus value and ROI-related state

Current interpretation note:

- focus value is currently a status field, not a separate command surface

## Current Usable Definition

- the shell starts reliably
- preview is practically usable
- the host can send the core commands
- camera settings are accessible in the shell
- snapshot and recording are understandable and usable
- ROI/focus is usable enough for setup
- status and hardware failures are understandable enough
- the three confirmed functional workflows can be executed in practice

## Roadmap Position

- Against `docs/ROADMAP.md`: Phase 0 repository reorganization is now completed for its first round, and Foundation, Camera Access, Snapshot Flow, Preview Flow, Recording Flow, Simulation, Host Integration, and the Python-side optional OpenCV path remain functionally implemented. Validation is no longer only simulator-backed: the March 27, 2026 hardware passes now cover an integrated command-flow baseline for snapshot save, preview readiness, interval capture from the shared preview stream, frame-limit recording, duration-only recording, target-frame-rate recording, supported alternate pixel format capture (`Mono10` as `.raw`), and explicit hardware-side failures for invalid camera id, unsupported pixel format, and invalid ROI increment choices on the Allied Vision `1800 U-1240m`. Phase 9 can therefore be treated as prototype-level hardware-validated for the current camera baseline, with remaining work limited to edge-case expansion rather than baseline viability. The focus baseline now also exists as a first implemented analysis capability on top of that reorganized platform surface, ROI groundwork has advanced from geometry-only helpers to analysis-consumable mask derivation for rectangle and ellipse shapes, and this branch now adds a first unified camera-oriented CLI baseline on top of the existing controller and service layer.
- Against `docs/GlobalRoadmap.md`: the platform-reorganization phase is now established alongside the existing Python prototype baseline. Camera integration, stream/recording services, host-neutral command flow, the optional OpenCV prototype path, ROI geometry groundwork, ROI mask primitives, and a first manual-focus baseline are in place. A first real-hardware OpenCV preview path is now available for local inspection, and the OpenCV prototype now also provides a first viewport-based preview baseline with fit-to-window plus zoom controls, mouse-wheel zoom, middle-drag pan, cursor-anchored zoom, top-left image anchoring, a dedicated bottom status band, FPS readout, operator toggles for crosshair and focus-status visibility, a first two-click ROI creation baseline for rectangle and ellipse with live preview, a preview-frame snapshot shortcut driven by an explicit save directory, and a first layer of concise operator-facing warning/error feedback while keeping those concerns explicitly in the UI/display layer. That preview path now also treats status-band meaning and overlay-layer meaning as shared descriptive models above the renderer, instead of OpenCV-private strings and drawing assumptions. A bounded optional wxPython shell path now also exists as the first non-OpenCV local working frontend: it starts from the same project `.venv`, reuses the existing bootstrap/controller/preview/display layers, follows the proven OpenCV feature cut for preview, snapshot, status, zoom/fit, crosshair, ROI entry, focus status/toggle, and bounded drag interaction, and keeps OpenCV as fallback/reference rather than as the only local shell. The April 7, 2026 follow-up after that first shell slice first revalidated the broader hardware baseline through CLI and OpenCV, and now also closes the concrete gap it exposed: the wx shell itself has a bounded real-device startup path that reuses the same headless source-selection, alias-resolution, configuration-profile, and configuration-override semantics as the CLI. Same-day wx follow-ups now also treat snapshot feedback as transient shell status, evaluate focus through the shared headless service on a bounded downsampled work frame, render a visible focus marker/label in the image area, align point-selection / clipboard feedback more closely with the OpenCV baseline instead of duplicating raw coordinates in the status area, refine the first anchor-hover/drag baseline so ROI handles appear only on hover / active drag, ellipse-corner editing follows bounding-box semantics, support both hold-drag-release and click-to-lock-drag-click-to-release, allow whole-ROI body panning with optional `Shift` dominant-axis locking, keep small ROI body interaction usable through enlarged invisible body hit bounds, expose active ROI frame state cleanly to the wx renderer through shared `normal` / `hover` / `drag` overlay emphasis, add rectangle side-midpoint handles for one-axis box resizing, let active ROI/point drags be canceled back to their drag-start geometry with `Esc`, surface the camera acquisition FPS and measured wx UI refresh FPS explicitly in the shell header, and now add bounded recording controls for start/stop, max frames, recording FPS, visible recording progress, and bounded menu/settings dialogs on the same shell surface, with the last recording summary staying visible after `Stop Recording` until the next `Start Recording`. The shell now also exposes a bounded open-session live-command path: it publishes one active local session under `captures/wx_shell_sessions/`, accepts external save/configuration/snapshot/recording commands through `python -m vision_platform.apps.local_shell control ...`, and reflects those controller-driven changes in the visible shell state without restart. The shared contract layer under `libraries/common_models` now also intentionally exposes some target-facing surface ahead of full implementation, with feature readiness expected to be marked in module-local status docs. Tracking/API modules remain open, but the Python camera baseline can now be regarded as architecturally, simulator-, and prototype-level hardware-validated for the tested camera path. The new `WP55` hardware-audit baseline now also exists as a separate append-only JSONL audit path under `captures/hardware_audit/`, and it records only warnings, degraded startup states, and incidents instead of normal artifact traceability. An April 7, 2026 recurring `WP04` hardware block now also revalidated the current tested device path after `WP50` and `WP51`: serial hardware `status`, hardware `snapshot`, integrated hardware command flow, and a bounded OpenCV hardware preview smoke all succeeded on `DEV_1AB22C046D81`. `WP65`, `WP66`, and `WP67` are now landed; the recording side now persists per-image system timestamps, one explicit first-frame timing anchor per run, and one deterministic append-only recording log per save directory.
- Against `docs/WORKPACKAGES.md`: project-level prioritization now runs through the centralized work-package queue instead of many distributed module roadmaps. The earlier command-surface, bounded OpenCV UI, ROI, focus, tracking, first API-preparation, and first postprocess packages can be treated as completed baseline-building work. The repository should no longer be read as being in an open-ended Extended MVP closure phase. That phase is now historical. Its landed slices through `docs/session_workpackages/wp12_host_control_closure.md`, `docs/session_workpackages/wp13_experiment_reliability_closure.md`, `docs/session_workpackages/wp14_data_logging_closure.md`, `docs/session_workpackages/wp15_offline_measurement_closure.md`, `docs/session_workpackages/wp16_data_logging_traceability.md`, `docs/session_workpackages/wp17_offline_measurement_metadata_extension.md`, `docs/session_workpackages/wp18_focus_metadata_artifact_extension.md`, `docs/session_workpackages/wp19_focus_metadata_producer_wiring.md`, `docs/session_workpackages/wp20_focus_metadata_policy_hardening.md`, `docs/session_workpackages/wp21_offline_stable_context_exposure.md`, `docs/session_workpackages/wp22_host_status_polling_hardening.md`, `docs/session_workpackages/wp23_host_command_confirmation_hardening.md`, `docs/session_workpackages/wp24_run_identity_trace_linkage.md`, `docs/session_workpackages/wp25_experiment_recovery_validation_extension.md`, and `docs/session_workpackages/wp26_hardware_revalidation_resume.md` established one bounded, host-oriented, hardware-validated Python working baseline on the tested camera path. `WP27` through `WP30` should now be read as the first landed post-closure hardening / diagnostics slices on top of that baseline. `WP29` specifically narrowed the current startup-warning interpretation: fresh serial March 30 hardware `status` and `snapshot(.bmp)` proofs on `DEV_1AB22C046D81` remained successful with `capabilities_available=True` and `capability_probe_error=None`, while `vmbpyLog <VmbError.NotAvailable: -30>` still appeared as SDK stderr output, so the current repository should classify that line as non-blocking SDK/logging residual on the successful tested path rather than as active startup failure. `WP35` now narrows the remaining enumeration ambiguity further: raw Vimba X enumeration on `DEV_1AB22C046D81` still shows duplicate SDK-visible entries for the same camera id, and the opened camera object can degrade serial from `067WH` to `N/A`, but the repository now resolves duplicate SDK-visible candidates by camera id and preserves the richer pre-open identity in host-visible status fields so the current hardware `status` surface again reports serial `067WH` on the tested path. The active planning lens is now `Usable Camera Subsystem / Pre-Product Baseline` in its confirmed `Hybrid Companion` reading: host commands to the running wx shell, visible shell reflection of host-driven state, shell settings/workflow usability, then headless-kernel preparation. In that lens, `WP62` through `WP67` are now landed, while the `WP62` file-backed session bridge must still be read as a bounded wx-shell solution rather than as the final host-neutral runtime-command model. `WP69 wx Camera Settings Menu And Shortcut Baseline` is now landed. No other package should be treated as the default next pick unless the user redirects or the branch scope changes.

The immediate baseline-building profile / alias / traceability follow-up sequence is now landed.

Current order:

`WP45 Stored Camera Configuration Profiles Baseline` is now landed.

This sequence should be read as:

- first landed residual-driven hardening / diagnostics slices through `WP30`
- then one landed operational-readiness runbook slice through `WP31`
- then one landed startup-surface slice through `WP32`
- then one landed later-handover/productization clarification slice through `WP33`
- then one explicit continuation toward the usable-subsystem phase:
  - `WP34` landed as bounded host-surface normalization
  - `WP35` landed as bounded enumeration / startup residual narrowing
  - `WP36` landed as bounded recording-lifecycle decision clarification
  - `WP37` landed as bounded operator-start convenience polish
  - `WP38` landed as conditional selective offline follow-up once explicitly chosen
  - `WP39` landed as bounded module-documentation trust / shrink cleanup
  - `WP40` landed as the first architecture-convergence slice behind the preferred `vision_platform` boundary
  - `WP41` landed as the direct storage/persistence follow-up
  - `WP42` landed as the namespace trust / compatibility-audit follow-up
  - `WP43` landed as a bounded operational-readiness guardrail slice
  - `WP44` landed as a bounded adapter-facing selective-expansion slice
  - `WP45` landed as the bounded camera-class-first configuration-profile slice
  - `WP46` landed as the follow-up bounded camera-alias / explicit-id convenience slice
  - `WP47` landed as the additive traceability control-context follow-up

The active usable-subsystem phase should now be read in four priorities:

1. `Host commands and shell reflection`
   - make host commands to the running wx shell practical first
   - ensure the shell visibly reflects host-driven behavior and state
2. `Settings and workflow usability`
   - keep camera/settings access usable in the shell
   - make delamination recording, geometry capture, and setup/focus/ROI adjustment executable in practice
3. `Technical anchor flows`
   - preserve preview, snapshot, recording start/stop, ROI/focus, and max-frames stop as the supporting technical execution modes
   - keep those flows understandable and validated
4. `Headless preparation after usability`
   - prepare the next shared kernel only after the subsystem is locally and host-side usable enough

## Merge Note

- `feature/roi-core-mask-baseline` has been merged into `main`.
- The merged ROI/focus/overlay baseline was revalidated on `main` with the targeted simulator-backed regression block before continuing.

## Current Summary

The repository should currently be read as a host-steerable running `Vision App / wxShell` in `Hybrid Companion` form, not as a generic platform-build-out and not as a repository still dominated by MVP-proof work.
The control/imaging compatibility cleanup is complete, the wx shell already has bounded host-reflection and settings-menu groundwork, and the official technical anchor flows now have one explicit repeatable simulator-first validation block.
The current phase remains `Usable Camera Subsystem / Pre-Product Baseline`, but "usable" is now concretely defined around host-driven control, visible shell reflection, shell settings access, understandable status/failure behavior, and practical execution of delamination recording, geometry capture, and setup/focus/ROI adjustment.
The supporting repo-orientation surfaces now also follow that reading: the root README, workflow-selection notes, and secondary summary docs no longer present the old post-closure framing as the active default and now defer clearly to `docs/STATUS.md`, `docs/WORKPACKAGES.md`, and `docs/TARGET_MAP.md`.

The larger assisted-measurement vision and later headless-kernel direction remain visible, but they are secondary to the near-term product direction above.

The compact operating reference for that baseline now lives at:

- `docs/MANUALS_INDEX.md`
- `docs/ARCHITECTURE_BASELINE.md`
- `docs/PYTHON_BASELINE_RUNBOOK.md`
- `docs/ENTRYPOINT_AND_LAUNCH_BASELINE.md`
- `docs/HOST_CONTRACT_BASELINE.md`
- `docs/TARGET_MAP.md`

The repository currently provides a structured Python prototype for the vision platform with:

- package layout under `src/camera_app/`
- request, configuration, and status models
- `CameraDriver` abstraction
- `VimbaXCameraDriver` initialization, camera selection, configuration, and single-frame capture
- snapshot save flow with explicit target path
- preview service with latest-frame buffering and polling loop
- optional OpenCV imaging adapter for preview-window display and grayscale-safe export
- recording base flow with bounded queue, writer loop, and frame-limit stop condition
- command-controller support for default save-directory resolution and consolidated subsystem status
- `CameraStreamService` as a small orchestration layer for shared live acquisition across preview and recording
- `IntervalCaptureService` for deterministic timed single-image capture from the shared live stream
- `camera_app.bootstrap` as a small composition root for consistently wiring driver, services, stream orchestration, and command controller
- `RoiStateService` as a small service-layer holder for one active ROI selection that preview-adjacent consumers can reuse
- OpenCV preview ownership alignment so a wired `RoiStateService` is also the committed active ROI source for preview rendering, while the window keeps only draft ROI entry interaction state locally
- explicit ROI precedence now lives in one shared ROI-state rule: explicit per-call ROI overrides the shared active ROI; otherwise consumers use the shared active ROI; otherwise they fall back to full-frame behavior
- `SnapshotFocusService` as a separate snapshot-analysis consumer that can reuse the same active ROI state path without mixing focus logic into snapshot saving
- `OverlayCompositionService` as a UI-free display composition layer that can merge active ROI plus preview/snapshot focus overlays into one shared payload
- simulator-backed overlay-payload demo that consumes the shared payload and prints a simple console summary without committing to a concrete renderer
- first unified camera CLI app entry point with `status`, `snapshot`, `recording`, and `interval-capture` subcommands above the existing command-controller path
- repo-local CLI camera alias resolution through `configs/camera_aliases.json`, with the tested example alias `tested_camera` resolving to the current hardware path
- repo-local camera-class-first CLI configuration profiles through `configs/camera_configuration_profiles.json`, with the current tested hardware path inferring class `1800_u_1240m` from `camera_model` and supporting the repo-local `default` profile
- first host-oriented CLI command envelope baseline for `status`, `snapshot`, and bounded `recording`, with stable success/failure ownership, machine-readable error payloads, and adapter-facing status serialization
- explicit `SubsystemStatus` model with host-facing command readiness flags
- camera status metadata that identifies hardware vs. simulation source kind and active driver name
- external request models for configuration, save-directory changes, snapshot save, and recording start/stop
- camera configuration now models ROI offsets and ROI size in addition to exposure, gain, pixel format, and acquisition frame rate
- recording requests can now carry a target frame rate and log it alongside ROI metadata
- smoke-test entry point for explicit camera id usage such as `example_camera_id`
- command-flow demo for host-style external control using the simulated driver
- a clear architectural basis for separating real hardware drivers from future simulation/demo drivers
- a working simulated driver for hardware-free preview, snapshot, and recording flows
- a shared frame-source path that lets preview and recording consume one acquisition loop together
- optional OpenCV preview demo on top of the simulated preview service
- optional OpenCV hardware preview demo for local live inspection with an explicit camera id
- integrated hardware command-flow runner for Phase 9 validation across snapshot, preview-backed interval capture, and recording
- optional OpenCV-backed lossless grayscale path for `.png` and `.tiff`
- dependency-free visible `BMP` output for `Mono8`, `Rgb8`, and `Bgr8` on the shared frame-writing path
- one shared folder-local appendable traceability log for snapshot and bounded-recording experiment context
- additive traceability control-context fields for alias and optional profile identity on snapshot and bounded-recording logs when the current request path provides them
- the current CLI profile path applies through the same capability-aware `ApplyConfigurationRequest` seam rather than bypassing host-neutral validation
- per-image traceability rows can now also carry optional analysis ROI and focus metadata without changing stable log identity
- focus summary metadata in those per-image rows now also requires an explicit aggregation-basis field when summary values are present
- focus summary metadata now also requires `focus_method` when summary values are present, while the current `focus_score_frame_interval` basis is validated as a positive integer count and `focus_value_stddev` must be non-negative when present
- snapshot and bounded-recording save flows now also support an explicit reusable focus-metadata producer path for writing those fields during normal saves
- the offline focus-report path now also exposes one compact folder-level stable-context summary from traceability headers through an additive report-bundle path, while keeping the existing per-image list-return path usable for earlier callers
- viewport-based OpenCV preview controls for fit-to-window and zoom on large hardware frames
- additional service hardening so preview/recording cleanup resets internal state defensively even when acquisition stop fails during recovery
- additional shared-stream cleanup hardening so real-hardware preview-backed acquisition can shut down without Vimba X `Invalid Camera` errors after the integrated Phase 9 run
- hardware-backed validation now also covers duration-only recording, target-frame-rate recording, explicit invalid camera id / invalid pixel format / invalid ROI increment failures, and a supported alternate `Mono10` snapshot-save path
- Vimba X acquisition-frame-rate control now enables `AcquisitionFrameRateEnable` automatically when a rate is configured, while `CameraStatus` also exposes the reported hardware frame-rate value and whether camera-side frame-rate control is enabled
- camera initialization can now best-effort probe a live capability profile for hardware-backed runtime validation, while capability-probe failures degrade softly to generic validation and are exposed through `CameraStatus` instead of blocking camera use
- hardware-backed camera initialization now prefers probing capability data from the already opened driver camera, avoiding an immediate second Vimba/camera open during `CameraService.initialize()` on the current real-device path
- capability-backed ROI validation now reports requested value, allowed range, increment/base, and nearest valid values for width/height/offset failures, while the CLI host surface returns those apply-configuration failures as `configuration_error`
- the OpenCV hardware-preview path treats that probe state as a warning-only concern: successful probing stays silent, while capability-probe failures may be surfaced as a status-bar/overlay warning for operators
- the OpenCV hardware-preview path now also supports click-based point selection with image-space coordinate display in a dedicated bottom status band and `c`-based coordinate copy, using a reusable coordinate-export formatter that can later be reused by an embedded host GUI
- the OpenCV preview/operator path now also keeps its shortcut hints capability-aware, so startup text and the in-window status band advertise snapshot/focus controls only when those paths are actually wired in the active preview entry point
- the OpenCV preview/operator path now also clears active pan anchors when returning to fit-to-window, so stale drag state does not survive a viewport-mode reset
- a headless `DisplayGeometryService` now owns fit-scale resolution, viewport-origin clamping, source/viewport mapping, and cursor-anchored zoom-origin calculation for preview consumers
- the OpenCV preview path now consumes that display-service geometry layer instead of owning the viewport math privately inside the window class
- a shared `PreviewInteractionService` now owns preview interaction-state transitions such as zoom commands, focus/crosshair toggles, ROI-mode changes, point selection, pan updates, copy requests, and snapshot requests
- the OpenCV preview path now translates HighGUI keyboard and mouse input into shared preview-interaction commands instead of owning those state transitions privately
- the ROI workflow consolidation package is now completed: when the OpenCV preview path is wired to `RoiStateService`, that service now acts as the committed active ROI source for preview rendering as well as downstream preview-focus, snapshot-focus, and overlay-composition consumers
- ROI workflow precedence is now also explicit and shared through `RoiStateService.resolve_active_roi(...)`, so ROI-consuming services no longer each restate that fallback rule privately
- new repository-level module workspaces for apps, integrations, services, and libraries
- new `src/vision_platform` namespace that exposes the current platform shape without breaking legacy `camera_app` imports
- new shared foundation modules for common models, ROI groundwork, and focus groundwork
- common model contracts now intentionally allow some future-facing surface to appear before full downstream implementation, with readiness expected to be marked in module-local docs
- physical migration of control and imaging implementation into `src/vision_platform`, with `camera_app` retained as a compatibility shim for those areas
- physical migration of file naming and frame writing into `src/vision_platform.services.recording_service`, with `camera_app.storage` retained as a compatibility shim
- physical migration of stream-service internals, camera drivers, and prototype demo entry points into `src/vision_platform`, with legacy `camera_app` modules retained as compatibility shims
- first implemented focus baseline with Laplace scoring, ROI-aware overlay anchors, and preview-consumer integration
- focus core now also implements a Tenengrad-based second metric with explicit method dispatch through `FocusRequest.method`, while Laplace remains the default path
- preview- and snapshot-side focus consumers now also expose a small service-level focus-method selection path, so multi-method support no longer requires custom evaluator injection for every consumer
- tracking core now also contains a first library-only edge/profile baseline that derives a dominant horizontal or vertical edge transition from full-frame or ROI-bounded image data through transport-neutral request/result contracts
- api-service preparation now also contains a first transport-neutral adapter payload family for `SubsystemStatus`, so future external adapters do not need to serialize the shared core status model directly
- api-service status payloads now also expose one additive `active_run` polling subset for active bounded recording or interval capture, derived from the existing shared status baseline
- hardware-backed validation now also refreshes the current CLI/API-facing host surface on March 30, 2026 for `status`, `snapshot`, bounded `recording`, and in-process active polling over interval capture plus bounded recording
- ROI core now also provides frame-clamped pixel bounds and rectangle/ellipse mask derivation so analysis consumers can apply ROI selection without reimplementing ROI math
- freehand ROI remains a target contract direction only and is not yet implemented through ROI-core mask derivation or downstream analysis consumers
- stream services now expose a small ROI state path so active ROI selection can be shared with preview-adjacent analysis without moving ROI ownership into UI or stream internals
- snapshot-side focus analysis can now also consume the same ROI state path while staying separate from snapshot persistence
- preview- and snapshot-side focus overlays can now be composed together with the active ROI into one shared display payload without introducing a concrete UI dependency
- the OpenCV prototype app layer now includes a simulator-backed payload demo that exercises this shared display payload through a lightweight console-facing adapter path
- viewport management concerns such as fit-to-window, zoom, pan, and display-space overlay transforms are now explicitly treated as UI/display-layer responsibilities instead of camera-core responsibilities
- the first integrated viewport implementation now preserves aspect ratio and uses black padding/cropping in the OpenCV prototype instead of naive display stretching
- the postprocess-tool baseline now also supports offline focus reporting over saved `BMP` artifacts produced by the current dependency-free writer path
- the postprocess-tool baseline now also consumes saved-artifact traceability metadata where present, reusing deterministic image-name joins without turning the tool into a broader offline explorer
- the postprocess-tool baseline now also surfaces explicit aggregation-basis metadata when focus-summary values are present in traceability rows
- the postprocess-tool baseline now also has fresh real-device evidence through a hardware-generated `BMP` snapshot with successful traceability-aware offline focus reporting on March 30, 2026

## Completed Work

### Foundation

- package structure created
- core domain models added
- logging setup scaffold added
- file naming scaffold added
- command controller skeleton added
- portable focus/ROI model extensions now include overlay-ready focus payloads and ROI centroid support
- ROI helper primitives now also include frame-clamped pixel bounds plus rectangle/ellipse mask derivation for analysis consumers
- common models now also include a shared display overlay payload for later preview, snapshot, or host consumers

### Camera Access

- camera discovery and initialization implemented
- explicit camera selection by id implemented
- clean shutdown implemented
- configuration application implemented
- single-frame acquisition implemented
- frame metadata model added through `CapturedFrame`
- real hardware currently runs through `VimbaXCameraDriver`
- hardware-free development now runs through `SimulatedCameraDriver`
- platform-owned driver implementations now live in `vision_platform.integrations.camera`

### Snapshot Flow

- snapshot request to target-path flow implemented
- frame writer added for `.png`, `.bmp`, `.raw`, and `.bin`
- `FrameWriter` implementation now lives in `vision_platform.services.recording_service`
- frame writer can now use an optional OpenCV adapter for higher-bit grayscale `.png` and `.tiff`, while `.bmp` stays on the dependency-free writer path for `Mono8`, `Rgb8`, and `Bgr8`
- snapshot logging added
- snapshot save now also writes into the shared folder-local traceability log with timestamp and active acquisition context fields where available
- snapshot smoke-test flow added
- snapshot smoke entry point now lives in `vision_platform.apps.opencv_prototype`
- `SnapshotFocusService` now provides a separate snapshot-analysis path for focus evaluation without coupling that behavior into `SnapshotService`
- `overlay_payload_demo` now validates a demo path that consumes the shared display payload without forcing a concrete window implementation

### Preview Flow

- preview service start/stop implemented
- latest-frame buffer implemented
- polling-based preview refresh implemented
- preview frame metadata exposure implemented
- optional OpenCV preview window adapter implemented above `PreviewService`
- optional OpenCV hardware preview demo implemented above `PreviewService` and `VimbaXCameraDriver`
- viewport-based fit-to-window and zoom controls now implemented in the OpenCV prototype preview path
- `PreviewService`, `SharedFrameSource`, and `CameraStreamService` now live in `vision_platform.services.stream_service`
- `FocusPreviewService` now derives focus state from preview frames without embedding analysis logic into the stream loop or window layer
- `RoiStateService` now lets preview-adjacent consumers reuse one active ROI selection without making ROI a stream-owned concern

### Recording Flow

- basic producer/consumer pipeline implemented
- bounded queue implemented
- sequential recording file naming implemented
- recording naming helpers now live in `vision_platform.services.recording_service`
- per-recording CSV log file implemented
- recording log header includes session metadata such as start signal time, stop conditions, save path, and known camera settings
- frame-limit stop condition implemented
- duration-based stop condition implemented
- target-frame-rate pacing implemented for recording requests
- recording state and error tracking implemented
- repeated bounded recording invocation and reuse after a selected writer-side failure are now explicitly covered by simulator-backed reliability tests on the same service path
- the first `Data And Logging Closure` slice now explicitly covers `BMP` as an additional practical visible output format on the shared writer path
- `WP16` now adds the next `Data And Logging Closure` extension slice: snapshot and bounded recording both write into one folder-local appendable traceability log with stable context header, run/session blocks, and per-image rows, while the per-image row shape now also allows optional analysis ROI and focus metadata
- `WP18` now adds the next narrow artifact-metadata extension slice: focus-summary fields are supported only with an explicit aggregation basis, while exact defaults and bounds remain later tested policy work
- `WP19` now adds the next producer-wiring slice: snapshot and bounded-recording save flows can emit artifact-level focus metadata through explicit reusable producer wiring

### Focus And ROI Foundations

- portable ROI definitions now expose bounds and centroid helpers for later overlay consumers
- portable ROI definitions now also expose frame-clamped pixel bounds and rectangle/ellipse mask derivation for analysis consumers
- `common_models` may now expose some target-facing contract surface ahead of end-to-end implementation, with readiness expected to be marked in module status docs
- ROI remains a reusable geometry/selection input instead of a UI-owned concern
- `focus_core` now provides a baseline Laplace evaluator for manual focus decisions
- focus evaluation remains consumer-driven, so stream layers expose frames while preview-facing consumers decide when focus is computed
- overlay-ready focus payloads now exist for preview and display consumers without coupling UI code into the analysis layer
- focus evaluation now consumes ROI mask helpers from `roi_core` instead of keeping ROI pixel-window logic private inside `focus_core`
- preview-adjacent consumers can now read an active ROI through `RoiStateService`, while explicit per-call ROI still remains possible
- snapshot-side focus consumers can now reuse the same ROI state path or override it explicitly per call
- overlay composition is now a separate service-layer concern that can merge active ROI plus preview/snapshot focus states into one UI-free payload
- the first `WP05` slice now aligns the OpenCV preview path with that same shared ROI ownership rule for committed ROI state, while leaving in-progress ROI drafting local to the window
- live preview-adjacent consumers now derive focus state from preview frames, while richer metric selection and operator-facing overlay controls remain open
- `WP06` is now completed: the focus-method surface no longer only names multiple methods ahead of implementation, because `tenengrad` is now a real second evaluator path, `evaluate_focus(...)` dispatches explicitly by requested method, and preview-/snapshot-adjacent focus consumers plus the stream-service preview factory can select `laplace` or `tenengrad` explicitly without widening the UI or host-facing surface
- `WP07` is now completed: `tracking_core` no longer only reserves future tracking space, because a first profile-based edge kernel now exists as a reusable analysis baseline under the existing ROI/frame model boundaries
- `WP08` is now completed: `api_service` no longer only reserves future API space, because a first adapter-facing status DTO family and mapper now exist above the shared command/controller layer
- `WP09` is now completed: adapter-facing command request DTOs now expose explicit `from_*` mapping methods in addition to their existing `to_*` methods, while typed command results now also expose named constructors for their common result shapes and the controller uses those factories instead of assembling result fields inline
- `WP10` is now completed: `postprocess_tool` no longer only reserves future offline tooling space, because a first stored-image focus-report baseline now exists above the current sample-image ingestion and focus-core contracts
- `WP15` now extends that offline baseline narrowly by proving reuse of saved `BMP` artifacts from the current writer path
- `WP01` is now also formally completed and archived: the camera CLI baseline already exists as a thin unified command surface above the shared command/controller path, and no further CLI widening is justified by default

## Partially Implemented

### Recording

- `frame_limit` stop condition is implemented
- `duration_seconds` stop condition is implemented
- both stop conditions can be combined
- `target_frame_rate` can now be provided to pace acquisition in the recording producer loop
- each recording writes a CSV log with image name, frame id, camera timestamp, and system UTC timestamp
- each recording log starts with metadata header lines for start signal time, save path, stop conditions, continuation flag, and known camera settings
- ROI fields in the log header are populated when ROI is present in `CameraConfiguration`
- no trigger-based recording yet
- no hardware-backed continuous acquisition validation yet

### Interval Capture

- `IntervalCaptureService` now supports timed single-image saving from a running shared acquisition
- interval capture uses explicit stop conditions via `max_frame_count`, `duration_seconds`, or explicit stop
- interval capture writes deterministic sequential filenames and can run in parallel with preview on the simulator-backed path
- interval capture is now exposed through bootstrap wiring and the host-facing command controller
- hardware-backed validation is still open

### Host Integration

- command surface exists
- `CommandController` implementation now lives in `vision_platform.control`, while `camera_app.control` remains as a compatibility import
- default save directory can now be resolved into snapshot and recording requests
- controller now exposes a typed `SubsystemStatus` model instead of an untyped dictionary
- subsystem status now includes command readiness flags for configuration, snapshot, recording start, and recording stop
- subsystem status now also includes interval-capture status together with start/stop readiness flags
- subsystem status now also exposes whether a save directory is currently configured and whether interval-capture support is present in the active subsystem wiring, so host callers do not have to infer those facts indirectly from readiness booleans alone
- camera status now exposes whether the active source is `hardware` or `simulation` together with the driver name
- external request types now exist for `ApplyConfigurationRequest`, `SetSaveDirectoryRequest`, `SaveSnapshotRequest`, `StartRecordingRequest`, `StopRecordingRequest`, `StartIntervalCaptureRequest`, and `StopIntervalCaptureRequest`
- apply-configuration commands now also expose a typed `ApplyConfigurationCommandResult`, so host-facing callers no longer need to treat successful configuration changes as a `None`-return side effect
- save-directory commands now also expose a typed `SaveDirectoryCommandResult`, with `SetSaveDirectoryResult` retained as a compatibility alias while the host-facing naming is normalized
- snapshot commands now also expose a typed `SnapshotCommandResult`, with `SaveSnapshotResult` retained as a compatibility alias while the host-facing naming is normalized
- recording start/stop commands now also expose a typed `RecordingCommandResult` so host-facing callers receive an explicit control result instead of a bare service status payload
- interval-capture start/stop commands now also expose a typed `IntervalCaptureCommandResult` so host-facing callers receive an explicit control result instead of a bare service status payload
- recording and interval-capture stop-command results now also preserve the requested stop reason, so host callers do not lose that control intent once the command crosses the controller boundary
- save-directory requests now support append-to-directory or create-new-subdirectory behavior
- host-style command flow now covers interval capture from the shared stream in addition to snapshot and recording
- deeper host-specific payload shaping is still open
- runtime capability-aware configuration validation is now available without any UI dependency, and it automatically falls back to generic request validation when live probing is unavailable
- a first UI-independent camera CLI baseline now exists in `vision_platform.apps.camera_cli` for explicit command-line access to status, snapshot, bounded recording, and bounded interval capture, with the first capability slice intentionally kept to `Capture`, `Camera`, and `Storage`
- the first Host Control Closure implementation slice now also hardens that CLI path for external process use by emitting a stable command envelope for `status`, `snapshot`, and bounded `recording`, reusing the API-service status payload mapper for the polling-oriented status portion, and exposing a minimal `code` / `message` / `details` error shape plus small confirmed-settings subsets for experiment traceability
- the host-polling follow-up slice now also exposes one additive `active_run` subset in that CLI/API-facing status payload family, keeping active-work observability separate from later post-command confirmation work
- the command-confirmation follow-up slice now also returns one narrower explicit confirmed-settings subset for `snapshot` and bounded `recording`, including resolved save directory, resolved file stem / extension, and accepted recording bounds where relevant
- the run-identity linkage follow-up now also aligns one deterministic `run_id` across snapshot and bounded-recording traceability blocks, active bounded-recording polling, and the current host-facing `snapshot` / bounded-`recording` command results
- the simulator-first recovery-validation follow-up now also proves the same bounded recording path can fail during write, degrade to a host-visible idle/restartable state, tolerate repeated stop calls, and then complete a later restart successfully on the same integrated subsystem path

### Validation

- unit coverage exists for naming, preview, recording, driver integration, and command-controller behavior
- dedicated tests now cover the external request model mappings and save-directory resolution rules
- dedicated tests now also cover the typed apply-configuration controller result so configuration commands are aligned with the other host-facing command outcomes
- dedicated tests now also cover the new subsystem-status availability/configuration flags, and CLI-facing JSON serialization remained valid after the host-status contract expansion
- dedicated tests now also cover stop-command reason preservation for recording and interval capture, keeping those typed control outcomes aligned with the stop requests that hosts already send
- a simulated command-flow demo now validates a host-style `configure -> set save directory -> snapshot -> interval capture -> recording -> status` sequence
- the direct simulated demo now also validates interval-based single-image saving from the shared stream before recording
- runnable demo entry points exist for both the direct simulated service flow and the command-controller flow
- dedicated tests now cover the optional OpenCV adapter, preview-window bridge, and Mono16 simulated frames
- request and path validation is now hardened for snapshot, recording, file naming, and save-directory commands
- additional tests now cover invalid file stems, unsupported extension shapes, and invalid save-directory subpaths
- preview and recording services now handle repeated stop calls and startup failures more defensively
- additional tests now cover cleanup and stable state recovery when preview thread setup or recording startup fails
- command-controller calls now reject uninitialized camera operations before delegating into snapshot or recording services
- snapshot smoke execution now rejects partially injected service dependencies to avoid inconsistent test and demo wiring
- simulated demo and command-flow demo now return a shared typed result model instead of loosely shaped dictionaries
- frame output validation now rejects unsupported pixel-format and file-extension combinations such as RGB-to-TIFF before writing
- frame output validation now also accepts `.bmp` only for `Mono8`, `Rgb8`, and `Bgr8`, while rejecting unsupported combinations such as `Mono16` to `BMP`
- dedicated OpenCV smoke-demo tests now verify the preview and save demo entry points against the simulator-backed path
- preview and recording cleanup now preserve stable service state even when `stop_acquisition()` itself fails during shutdown or recovery
- additional tests now verify that startup failures keep their original exception even if cleanup also fails afterwards
- additional tests now cover baseline focus scoring, ROI-centroid geometry, ROI pixel bounds, rectangle/ellipse mask derivation, ROI-state-driven preview-focus consumption, snapshot-side focus capture, UI-free overlay composition, overlay-payload demo consumption, stream-level focus integration, and the simulated focus-preview smoke/demo path
- real hardware validation is still pending separately from the simulator-backed validation
- a first integrated real-hardware command-flow run on March 27, 2026 now verifies snapshot save, preview readiness, interval capture, and frame-limit recording on camera `DEV_1AB22C046D81` (`Allied Vision 1800 U-1240m`)
- the first two integrated hardware runs exposed cleanup-side Vimba X `Invalid Camera` errors during shared-stream shutdown; the follow-up cleanup ordering and timeout hardening removed those errors on the subsequent `run_003` validation pass
- additional March 27, 2026 runs now verify duration-only recording, target-frame-rate recording, `Mono10` raw snapshot capture, and explicit hardware-side failures for invalid camera id, unsupported pixel format `Mono16`, and invalid ROI width increment values
- the tested camera reports `AcquisitionFrameRate` as present and read-only by default, but the driver now enables `AcquisitionFrameRateEnable` automatically before setting a requested rate and exposes the read-back state through `CameraStatus`
- capability-aware configuration validation now consumes live or stored `CameraCapabilityProfile` data in the service/control layer, while failed hardware capability probes only disable the extra device-specific validation instead of failing camera initialization
- the March 30, 2026 camera-specific rerun against `DEV_1AB22C046D81` now also refreshes the documented capability-backed control paths for combined `Mono8` + exposure + gain + ROI, `target_frame_rate=5.0`, `Mono10` snapshot save to `.raw`, explicit `Mono16` and invalid-ROI-width failures, and one non-zero ROI-offset snapshot through the current CLI host path

### Preview

- service layer exists and is test-covered
- preview can now run against an optional shared frame source instead of starting an independent acquisition loop
- `CameraStreamService` now exposes that shared-acquisition path as the preferred composition point for live preview plus concurrent recording
- `CameraStreamService` can now also create `IntervalCaptureService` for preview plus timed single-image saving from the same stream
- `CameraStreamService` can now also create `FocusPreviewService` so focus state can be derived from the same preview path
- an optional OpenCV preview window now exists above the service layer
- a first real-hardware preview demo now exists on top of the optional OpenCV layer for local desktop inspection
- the preview demo can now optionally compose focus state while keeping the window class itself free of focus logic
- fit-to-window and zoom are now implemented in the OpenCV prototype UI layer, and a dedicated bottom status band now keeps preview status text out of the image viewport; crosshair and focus-status toggles plus a rolling FPS readout also now exist in that same UI layer, rectangle/ellipse ROI modes now support a first two-click creation baseline with live preview that also updates the shared ROI state path, the viewport now anchors image content to the top-left while using both keyboard- and wheel-driven cursor-anchored zoom plus middle-drag pan and a thin outline for visible padded image bounds, the `+` shortcut can now save the latest preview frame through an explicit preview-frame save path while reporting unavailability cleanly when no save directory is configured, and the demo entry points now fail with concise operator-readable terminal messages when preview startup fails; richer ROI drawing/editing interaction is intentionally deferred as non-MVP work, while any further OpenCV-side control expansion should be treated only as a lightweight in-preview operator strip rather than a real menu UI
- click-based point selection, crosshair display, coordinate readout, and `c`-based coordinate copy now exist as the first operator-facing point-inspection baseline in that same OpenCV preview path
- no browser preview or non-OpenCV UI layer yet
- the real-hardware preview path is implemented and historically verified, but the physical hardware is currently not attached locally
- simulated preview exists through `SimulatedCameraDriver`

### Simulation vs. Real Hardware

- architecture now explicitly expects separate real-hardware and simulated driver implementations
- `SimulatedCameraDriver` is implemented for generated frames and `.pgm`/`.ppm` sample image sequences
- a simulated demo entry point exists for preview, snapshot, and recording without hardware
- a simulated focus-preview smoke/demo path now exists for preview-to-focus validation without hardware
- the simulated and Vimba X drivers now live physically in `vision_platform.integrations.camera`
- simulator-backed tests now verify that preview and recording can share one acquisition loop without fighting over the driver
- simulator-backed tests now also verify preview plus timed interval capture from the same shared stream
- simulated generation now also covers `Mono16` frames for grayscale-save-path validation
- sample-image demo support is limited to `.pgm` and `.ppm` files for now
- real hardware validation is still required separately from simulation

### Optional OpenCV Integration

- optional OpenCV implementation now lives in `vision_platform.imaging`
- `camera_app.imaging` remains as a compatibility shim for legacy imports
- the app-facing OpenCV demos now live in `vision_platform.apps.opencv_prototype`
- OpenCV remains outside `CameraDriver` and outside the mandatory core dependency set
- preview display can now run through `cv2.imshow()` on top of `PreviewService`
- preview display can now also run against a real Vimba X camera through the optional OpenCV prototype path
- the preview demo can now optionally carry focus state alongside the rendered preview path without moving analysis into the OpenCV window class
- fit-to-window and zoom are now implemented as frontend/display concerns rather than core-service concerns, and a dedicated bottom status band now separates status text from the image viewport
- crosshair visibility and focus-status visibility can now be toggled directly in the OpenCV preview loop without moving that state into the camera or stream layers
- richer ROI drawing/editing interaction remains planned only as non-MVP follow-up work in that same frontend/display layer, while any remaining OpenCV-side control expansion should be limited to a lightweight in-preview operator strip rather than a real menu UI
- lossless grayscale save now supports `.png` and `.tiff` through the optional adapter for `Mono8` and unpacked higher-bit grayscale formats such as `Mono16`
- the standard-library writer remains the default for dependency-free `Mono8`, `Rgb8`, and `Bgr8` PNG output
- packed grayscale formats are still not decoded automatically and should be transformed explicitly before using the OpenCV save path if required
- simulator-backed validation for the optional path is complete, but hardware-backed validation is still pending

## Known Constraints

- real-hardware availability remains conditional across sessions even though a fresh bounded rerun was completed on March 30, 2026; assume simulator-first validation again unless the camera is confirmed attached for the active session
- the terminal default `python` may differ from the project interpreter on this machine
- the project virtual environment currently uses Python 3.14.3 at `.\.venv\Scripts\python.exe`
- project tests should be run with `.\.venv\Scripts\python.exe`

## Verified Test Commands

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_snapshot_service tests.test_frame_writer tests.test_snapshot_smoke tests.test_preview_service tests.test_file_naming tests.test_recording_service tests.test_interval_capture_service tests.test_camera_stream_service tests.test_bootstrap tests.test_simulated_camera_driver tests.test_simulated_demo tests.test_command_flow_demo tests.test_command_controller tests.test_request_models tests.test_opencv_adapter tests.test_opencv_preview tests.test_opencv_smoke_demos tests.test_focus_core tests.test_focus_preview_service tests.test_focus_preview_demo tests.test_vision_platform_namespace
.\.venv\Scripts\python.exe .\scripts\launchers\run_reference_scenario_validation.py
```

## Next Recommended Steps

1. Treat this documentation pass as the product-direction alignment layer: future package selection should now default to the `Hybrid Companion` reading of the current phase.
2. Keep `WP75` as the compact operator-facing path for the current functional workflows and `WP71` as the technical validation anchor for the underlying execution modes.
3. Execute the workflow-first sequence through `WP80`, then `WP81`, then `WP82` so future work is selected from the three confirmed functional workflows rather than from older residual buckets.
4. Keep shell-side follow-up work conditional and product-facing: reactivate `WP76` only when one of those workflow packages exposes a concrete host-reflection, status, or settings-feedback blocker.
5. Keep host-surface follow-up work conditional and product-facing: reactivate `WP77` only when a concrete AMB/test-host naming or interpretation ambiguity appears in the current phase-1 command surface.
6. Keep compatibility-seam work evidence-first: `WP78` is acceptable later, but not ahead of the workflow-first Hybrid Companion slices.
7. Keep broader API growth, additional frontends, larger offline tooling, MCP-oriented orchestration, and C# handover visible as later directions rather than current default obligations.
8. When the later headless-kernel work starts, revisit the current wx-shell live-sync bridge explicitly and lift or replace it with a host-neutral command/session seam instead of freezing the app-local file bridge as the long-term architecture.

## Deferred Profile-System Bucket List

These items are intentionally recorded as future-facing profile-system considerations, not as active queued work:

- keep the current repo-local `camera_class`-first reference-profile baseline as the shared, versioned source of truth
- add an optional local operator-override layer only when repeated machine-local or user-local tuning becomes a real need
- keep the intended merge precedence explicit if local overrides are ever added:
  1. repo reference profile
  2. local operator override
  3. explicit CLI arguments
- add narrow `show` / `list` inspection commands before considering any broader profile-management surface
- keep profile creation manual or tightly controlled until a clear need exists for `save current as profile`
- capture simple profile metadata later if useful, such as purpose, notes, or last validated hardware path
- treat any future `camera_id`- or `camera_alias`-specific override layer as a later step above the current `camera_class` baseline, not as the first profile model
- continue to preserve requested profile identity, resolved camera identity, and actually applied settings through traceability rather than relying only on file names or operator memory
- consider a later desktop operator window baseline that reuses proven OpenCV-prototype interactions in a more explicit window shell with menu/command area and status bar, but keep that as a separate frontend/productization step rather than folding it into the current CLI or baseline hardening
- consider a later host-emulator companion flow that can send commands, poll status, and change configuration while a live preview stays visible in OpenCV or another frontend, so the current host/control separation can be exercised more realistically without immediately committing to a full transport or daemon architecture
- consider narrow profile inspection commands such as `show` / `list` as the first usability step before any broader profile-management workflow, so profile trust and discoverability improve without adding editing scope
- consider local operator profile overrides as a later machine-local or user-local layer for repeated real usage, but keep them clearly separate from the shared repo reference profiles to preserve reproducibility
- consider operator-session runbook refinement when repeated real usage patterns stabilize, so known good startup / preview / save / recovery flows become easier to hand over and repeat without expanding the core command surface
- consider a more explicit desktop-ready warning and error surface later, especially if hardware residuals, startup warnings, or capability failures need to be presented to operators more clearly than the current JSON/terminal path
- consider a dedicated preview-plus-control split validation slice later, where one frontend shows live preview while a separate bounded controller/emulator changes settings and triggers capture, to prove that the current separation also behaves well under more realistic operator-plus-host use
- evaluate future interaction slices explicitly by deployment mode before implementation:
  - `host-embedded`, where an external host owns workflow and the camera subsystem should behave as a component
  - `standalone operator`, where a local app owns preview, status, and controls directly
  - `hybrid companion`, where preview and host-style control coexist and stress the current separation more realistically
- consider a later host-notification model beyond polling:
  - goal: let the camera/control side actively report warnings, failures, and important state changes instead of relying only on a host-side polling loop
  - important design questions: who subscribes, how subscriptions are registered, what event ownership and delivery guarantees exist, how missed listeners behave, and when polling remains the fallback
  - especially valuable for non-regular events such as startup degradation, capability-probe warnings, unexpected stop conditions, snapshot/recording failures, and warning-state changes
- consider a later non-regular run audit log above the current traceability baseline:
  - goal: preserve irregular cases for measurement audits, debugging, and recovery analysis after the run
  - likely first scope: warnings, failures, aborted runs, recovery cases, and unusual timing or hardware states rather than broad session browsing
  - keep this distinct from a full history explorer; the first useful slice is audit/debug evidence for exceptional cases, not a generic run browser





