# Status History

## Purpose

This document preserves repository-status history that should not remain in the primary reading path of `docs/STATUS.md`.

Use it to:

- retain important status chronology without losing it
- keep older landed-work and phase-transition notes available
- reduce growth pressure on the decision layer at the top of `docs/STATUS.md`

Do not use this file as the authoritative current-state document.

The authoritative current-state carriers remain:

- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`

## Archival Rule

Append a new status-history snapshot when either of these thresholds is reached:

1. a repository phase changes
2. 20 additional work packages have landed or completed since the last status-history snapshot anchor

Snapshot rule:

- keep snapshots append-only
- preserve the wording that was moved out of `docs/STATUS.md` when practical
- add the snapshot date and anchor range explicitly
- keep `docs/STATUS.md` focused on current truth and the fast decision layer

## Snapshot 2026-04-28 - Hybrid Companion Through WP103 Planning

### Snapshot Scope

- source status date: April 28, 2026
- landed/completed anchor range preserved here: `WP80` through `WP99`
- planning anchor preserved here: `WP100` through `WP103` preparation

### Archived Branch Context

- the latest camera fore-stage documentation and implementation slice from `docs/camera-embedding-analysis` is now merged into `main`
- the latest merged topic branches on top of the current usable-subsystem baseline include `feature/wp86-headless-seam`, `test/simulated-companion-smokes`, `test/hardware-companion-smokes`, the manuals-alignment slice `docs/manuals-host-shell-flow-apr10`, the camera fore-stage slice `docs/camera-embedding-analysis`, and `refactor/wp99-live-sync-service-extraction`

### Archived Current-Next Chronology

- `WP80 Delamination Recording Workflow Narrowing` is now landed on `main`.
- `WP81 Geometry Capture Workflow Narrowing` is now landed on `main`.
- `WP82 Setup Focus ROI Workflow Narrowing` is now landed on `main`.
- `WP83 Host Result And Status Surface Consistency Narrowing` is now landed on `main`.
- `WP84 Usable Failure Reflection Baseline` is now landed on `main`.
- `WP85 Stage-2 LabVIEW Contract Mapping Narrowing` is now landed on `main`.
- `WP86 Headless Command Seam Extraction Baseline` is now landed on `main`.
- `WP87 Hybrid Companion Hardware Workflow Revalidation` was reactivated in this session and completed on April 10, 2026; hardware-backed `status`, `snapshot`, bounded `recording`, and the integrated command-flow run all succeeded on `DEV_1AB22C046D81`.
- after the hardware-validation slice, no unconditional next had been set until the current camera-integration fore-stage was made explicit through `WP93` and `WP94`.
- `WP88 Local Shell Test-Host And UI Validation` is now completed; the running wx shell and separate test-host process agreed on status, snapshot, save-directory, and bounded recording state on the tested hardware path.
- `WP89 Local Shell Camera Settings Defaults And Limits Alignment` is now completed; the running wx shell and separate test-host process agreed on status, snapshot, save-directory, and bounded recording state on the tested hardware path, and the current hardware profile defaults now use a valid `Mono10` / `10013.862us` baseline.
- `WP90 Local Shell Help Text Cleanup And OpenCV Hint Removal` is now completed; the running wx shell help text is now concise and no longer carries the obsolete OpenCV hint.
- `WP91 Local Shell ROI And Crosshair Priority Alignment` is now completed; the shared interaction service and wx shell now agree that crosshair has priority over ROI entry and dragging.
- `WP92 Local Shell Mono10 Rendering And Hardware Profile Alignment` is now completed; the hardware-backed wx shell now renders `Mono10` frames instead of crashing, falls back to hardware-safe snapshot / recording output when BMP is invalid, and the tested hardware shell completed status, snapshot, and bounded recording on `DEV_1AB22C046D81` after the profile correction.
- next if more hardware time is available: do one last live `Camera Settings...` / menu-path check on the current `Mono10` shell; if the camera is no longer attached, stop hardware work and move to branch hygiene instead of opening a broad new rerun lane.
- default next-step derivation should now use the confirmed `Hybrid Companion` product reading through the three functional workflows rather than a broad generic subsystem-hardening lens.
- `WP93 Camera Integration Surface v0.1 Contract Mapping` is now completed as the gatekeeper documentation/contract slice; its detailed file lives at `docs/session_workpackages/wp93_camera_integration_surface_v0_1_contract_mapping.md`
- `WP94 Health And Capabilities Surface Contract` is now completed as the first code-backed surface-contract slice; its detailed file lives at `docs/session_workpackages/wp94_health_and_capabilities_surface_contract.md`
- the repo now exposes `CommandController.get_health()` and `CommandController.get_capabilities()` as narrow surface calls above the existing core, and the adapter layer now has matching API-service payload mappers for health and capabilities
- `WP95 Camera Health Model Baseline` is now completed as the first code-backed internal derivation-model slice after `WP94`; the repo now has one explicit `CameraHealthService` that keeps the stable-now field set small and the `degraded` / `faulted` distinction explicit
- `WP96 Runtime Event Family Baseline` is now completed as the first code-backed event-semantics slice after `WP95`; the repo now has first-class runtime-event builders without introducing a bus, transport, or delivery model
- `WP97 Artifact Reference And Time Context Baseline` is now completed as the first code-backed artifact/time slice after `WP96`; the repo now has explicit `ArtifactReference` and `ArtifactTimeContext` models plus narrow builder helpers
- no unconditional next slice is set after `WP97`; the next selection should be derived from the now-implemented camera-integration fore-stage baseline and the smallest justified follow-up seam
- `WP98 Vision Platform Namespace Boundary Alignment` is now landed on `main`; the remaining `tests.test_vision_platform_namespace` residual was closed by aligning hardware-audit model ownership with `vision_platform.models` and by removing the wx-shell-local logging and snapshot-extension drift back into `camera_app`
- `WP99 Live Sync Service Extraction` is now landed on `main`; the file-backed local-shell session bridge mechanics now live in `vision_platform.services.local_shell_session_service`, while `vision_platform.apps.local_shell.live_command_sync` remains as a thin compatibility wrapper for the existing import surface
- `WP100 Companion Session Protocol Baseline` is now the default next non-hardware slice; it should replace the remaining ad-hoc local-shell session JSON/dict shapes with one explicit typed protocol baseline above the current file-backed bridge
- `WP101 Companion Command Execution Service Extraction` and `WP102 Companion Status Projection Service Extraction` are now the queued follow-ups after `WP100`, keeping the next headless-preparation lane narrow and sequential instead of reopening broad transport work
- `WP103 wx Camera Settings Live Path Revalidation` is now the smallest remaining conditional hardware slice; activate it only when the tested camera is physically attached and a live rerun is actually possible
- the decision layer at the top of `docs/STATUS.md` should remain the primary reading surface; older chronology should move here instead of expanding the fast status read
- the repo-level orientation cleanup now also extends beyond the central PM docs: `README.md`, `docs/WORKFLOW.md`, `docs/NEXT_SESSION_ORDER.md`, `docs/project_overview.md`, and the secondary summary notes now point at the same current product reading instead of older post-closure wording
- `WP75 Reference Scenario Operator Path Tightening` is now landed; `docs/ENTRYPOINT_AND_LAUNCH_BASELINE.md` and `docs/MANUALS_INDEX.md` now expose one compact validated entry path for the official current workflows.
- `WP71 Reference Scenario Validation Narrowing` is now landed; the repository has one explicit repeatable validation block for the current technical anchor flows through `tests.test_reference_scenarios` and `scripts/launchers/run_reference_scenario_validation.py`.
- `WP70 Control And Imaging Compatibility Cleanup` remains complete on the topic branch and already archived as a finished refactor slice.
- the latest documentation-governance maintenance also landed: `docs/STATUS.md` is the authoritative repository status, `docs/WORKPACKAGES.md` is the authoritative repository queue, and `docs/PRIORITIES.md` / `docs/TARGET_MAP.md` are derived views only
- the broader architecture/planning note cluster is now grouped under `docs/BiggerPictureNotes/`; it currently includes the moved baseline note `13_Camera.md`, the sharper follow-up `13.1_Camera.md`, the repo transformation note `Camera_Repo_Strategieplanung_fuer_Gesamtprojekt.md`, and the supporting integration/compatibility analyses for bigger-picture camera planning
- the same `docs/BiggerPictureNotes/` cluster now also includes the new narrow pre-step notes `camera_integration_surface_v0.1.md` and `camera_subsystem_role_and_boundaries.md`, which deliberately define a small camera-integration fore-stage without forcing full end-architecture into the current repo phase
- those `docs/BiggerPictureNotes/` files should be read as architecture/context and strategy material for larger-system alignment, not as the current implementation-truth layer; `docs/STATUS.md` and `docs/WORKPACKAGES.md` remain the authoritative repository-state carriers
- `WP81` now also has landed geometry-capture slices for snapshot reflection, save-path readability, host-triggered snapshot smoke coverage, and explicit snapshot failure reflection
- `WP82` now also has landed setup slices for setup-state reflection, setup-oriented messaging, ROI/focus visibility, and host-triggered setup smoke coverage
- `WP83` now also has landed completion slices for reflection-aligned command results, save-directory result consistency, host/result smoke coverage, and a more consistent failed-result placeholder shape
- `WP76`, `WP77`, and `WP78` are no longer the default open residual lane; they stay dormant unless the workflow-first sequence exposes one concrete seam that actually needs them
- the first `WP80` implementation slice is now landed on `main`: external `start-recording` commands in the wx-shell live-control path now fall back to the shell-visible recording settings when optional overrides are omitted, while explicit host overrides still win when provided
- the second `WP80` implementation slice is now landed on `main`: the wx-shell live status snapshot now publishes one explicit recording-reflection block for host/companion visibility, and the visible shell status prefix now keeps the current or last recording file stem readable
- the third `WP80` implementation slice is now landed on `main`: the wx-shell recording reflection now categorizes stop causes for the delamination path so shell-facing status and published live status distinguish host stop, `max_frames_reached`, and failure-oriented termination more clearly
- the final `WP80` completion slices are now also landed on `main`: shell-visible save-path reflection, tighter run-lifecycle messaging, one repeatable host-control smoke block for the delamination path, and explicit failure reflection through `phase=failed` plus `last_error`
- the `WP81` implementation slices are now also landed on `main`: shell-visible snapshot file/save reflection, published `snapshot_reflection` status, geometry-capture-oriented snapshot messaging, one repeatable host-triggered snapshot smoke block, and explicit snapshot failure reflection through `phase=failed` plus `last_error`
- the `WP82` implementation slices are now also landed on `main`: shell-visible setup focus/ROI cues, published `setup_reflection` status, setup-oriented configuration messaging, and one repeatable host-triggered setup smoke block
- the `WP83` implementation slices are now also landed on `main`: live command results now expose reflection-aligned subsets for setup, snapshot, recording, and save-directory paths, and failed result files now keep one minimal command/result placeholder shape
- the `WP84` implementation slices are now also landed on `main`: shell status, published status, and failed live-command result files now share one readable `failure_reflection` baseline across setup, snapshot, and recording, including source/action/message/external ownership and overwrite-on-latest-failure semantics
- the `WP85` implementation slices are now also landed on `main`: the current `local_shell control` test-host path now exposes one additive `labview_mapping` block for status reads, successful command results, and failed command results, keeping the Stage-2 LabVIEW reading explicit without widening the runtime/transport model
- the `WP86` implementation slices are now also landed on `main`: the current companion command-result payload shape, failed-result placeholder shape, and published status-snapshot payload shape now have one shell-independent home in `vision_platform.services.companion_contract_service`, while the wx-shell bridge consumes that seam instead of assembling those payloads directly
- the `WP87` session now has a fresh April 10, 2026 revalidation result: `camera_cli status --source hardware --camera-alias tested_camera`, hardware `snapshot`, bounded `recording`, and the integrated command-flow run all succeeded on `DEV_1AB22C046D81`, so the earlier April 9 availability miss should now be read as a transient precondition failure rather than current state
- the permanent simulator-backed companion smoke coverage now also includes running-recording status reading plus setup-failure reflection through the current host path, including `labview_mapping` and published status visibility
- the repository now also carries conditional real-hardware CLI smoke tests for the documented tested-camera path (`tested_camera` -> `DEV_1AB22C046D81`), and those tests skip cleanly when that real device is not attached locally
- the current hardware-smoke baseline should therefore be read as `present but conditional`: real-device CLI smokes are ready to execute, but a local session without the documented tested camera will currently produce clean skips rather than fresh hardware evidence

### Archived Current-Next Detail Continuation

- `WP75 Reference Scenario Operator Path Tightening` is now landed; `docs/ENTRYPOINT_AND_LAUNCH_BASELINE.md` and `docs/MANUALS_INDEX.md` now expose one compact validated entry path for the official current workflows.
- `WP71 Reference Scenario Validation Narrowing` is now landed; the repository has one explicit repeatable validation block for the current technical anchor flows through `tests.test_reference_scenarios` and `scripts/launchers/run_reference_scenario_validation.py`.
- `WP70 Control And Imaging Compatibility Cleanup` remains complete on the topic branch and already archived as a finished refactor slice.
- the latest documentation-governance maintenance also landed: `docs/STATUS.md` is the authoritative repository status, `docs/WORKPACKAGES.md` is the authoritative repository queue, and `docs/PRIORITIES.md` / `docs/TARGET_MAP.md` are derived views only
- the broader architecture/planning note cluster is now grouped under `docs/BiggerPictureNotes/`; it currently includes the moved baseline note `13_Camera.md`, the sharper follow-up `13.1_Camera.md`, the repo transformation note `Camera_Repo_Strategieplanung_fuer_Gesamtprojekt.md`, and the supporting integration/compatibility analyses for bigger-picture camera planning
- the same `docs/BiggerPictureNotes/` cluster now also includes the new narrow pre-step notes `camera_integration_surface_v0.1.md` and `camera_subsystem_role_and_boundaries.md`, which deliberately define a small camera-integration fore-stage without forcing full end-architecture into the current repo phase
- those `docs/BiggerPictureNotes/` files should be read as architecture/context and strategy material for larger-system alignment, not as the current implementation-truth layer; `docs/STATUS.md` and `docs/WORKPACKAGES.md` remain the authoritative repository-state carriers
- `WP81` now also has landed geometry-capture slices for snapshot reflection, save-path readability, host-triggered snapshot smoke coverage, and explicit snapshot failure reflection
- `WP82` now also has landed setup slices for setup-state reflection, setup-oriented messaging, ROI/focus visibility, and host-triggered setup smoke coverage
- `WP83` now also has landed completion slices for reflection-aligned command results, save-directory result consistency, host/result smoke coverage, and a more consistent failed-result placeholder shape
- `WP76`, `WP77`, and `WP78` are no longer the default open residual lane; they stay dormant unless the workflow-first sequence exposes one concrete seam that actually needs them
- the first `WP80` implementation slice is now landed on `main`: external `start-recording` commands in the wx-shell live-control path now fall back to the shell-visible recording settings when optional overrides are omitted, while explicit host overrides still win when provided
- the second `WP80` implementation slice is now landed on `main`: the wx-shell live status snapshot now publishes one explicit recording-reflection block for host/companion visibility, and the visible shell status prefix now keeps the current or last recording file stem readable
- the third `WP80` implementation slice is now landed on `main`: the wx-shell recording reflection now categorizes stop causes for the delamination path so shell-facing status and published live status distinguish host stop, `max_frames_reached`, and failure-oriented termination more clearly
- the final `WP80` completion slices are now also landed on `main`: shell-visible save-path reflection, tighter run-lifecycle messaging, one repeatable host-control smoke block for the delamination path, and explicit failure reflection through `phase=failed` plus `last_error`
- the `WP81` implementation slices are now also landed on `main`: shell-visible snapshot file/save reflection, published `snapshot_reflection` status, geometry-capture-oriented snapshot messaging, one repeatable host-triggered snapshot smoke block, and explicit snapshot failure reflection through `phase=failed` plus `last_error`
- the `WP82` implementation slices are now also landed on `main`: shell-visible setup focus/ROI cues, published `setup_reflection` status, setup-oriented configuration messaging, and one repeatable host-triggered setup smoke block
- the `WP83` implementation slices are now also landed on `main`: live command results now expose reflection-aligned subsets for setup, snapshot, recording, and save-directory paths, and failed result files now keep one minimal command/result placeholder shape
- the `WP84` implementation slices are now also landed on `main`: shell status, published status, and failed live-command result files now share one readable `failure_reflection` baseline across setup, snapshot, and recording, including source/action/message/external ownership and overwrite-on-latest-failure semantics
- the `WP85` implementation slices are now also landed on `main`: the current `local_shell control` test-host path now exposes one additive `labview_mapping` block for status reads, successful command results, and failed command results, keeping the Stage-2 LabVIEW reading explicit without widening the runtime/transport model
- the `WP86` implementation slices are now also landed on `main`: the current companion command-result payload shape, failed-result placeholder shape, and published status-snapshot payload shape now have one shell-independent home in `vision_platform.services.companion_contract_service`, while the wx-shell bridge consumes that seam instead of assembling those payloads directly
- the `WP87` session now has a fresh April 10, 2026 revalidation result: `camera_cli status --source hardware --camera-alias tested_camera`, hardware `snapshot`, bounded `recording`, and the integrated command-flow run all succeeded on `DEV_1AB22C046D81`, so the earlier April 9 availability miss should now be read as a transient precondition failure rather than current state
- the permanent simulator-backed companion smoke coverage now also includes running-recording status reading plus setup-failure reflection through the current host path, including `labview_mapping` and published status visibility
- the repository now also carries conditional real-hardware CLI smoke tests for the documented tested-camera path (`tested_camera` -> `DEV_1AB22C046D81`), and those tests skip cleanly when that real device is not attached locally
- the current hardware-smoke baseline should therefore be read as `present but conditional`: real-device CLI smokes are ready to execute, but a local session without the documented tested camera will currently produce clean skips rather than fresh hardware evidence
