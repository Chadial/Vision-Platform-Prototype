# Host Contract Baseline

## Purpose

This document defines the current stable-now versus deferred-later split for the host-facing Python baseline.

Use it to answer:

- which current command names are stable enough for near-term reuse
- which request, result, and status shapes are the current bounded baseline
- which parts of the present host surface are intentionally narrow
- which broader surfaces remain deferred rather than missing by accident

This is a contract-clarification document.

It does not define:

- a new transport layer
- a full API schema family
- IPC design
- a complete long-term contract freeze

## Stability Verdict

The current host-facing Python baseline should be treated as:

- stable enough for bounded host reuse on the current command surface
- intentionally narrow in scope
- not yet a full external-interface product surface
- specifically aimed at the current `Hybrid Companion` phase where a host steers a running visible wx shell rather than a fully detached headless runtime

The stable-now baseline is centered on:

- typed request terms
- bounded CLI host envelopes
- additive active polling
- narrow confirmed-settings subsets
- narrow `run_id` linkage
- the current phase-1 host command and status surface for the running companion app

The deferred-later area includes:

- broader query surfaces
- richer transport/API DTO families
- detached long-running remote control semantics
- broader frontend- or IPC-specific contract layers

For the current bounded recording meaning versus detached-later scope, use:

- `docs/RECORDING_LIFECYCLE_BOUNDARY.md`

## Stable Now

### Current phase-1 host expectations

The host should currently be able to:

- define save location
- define core camera settings
- control acquisition
- obtain camera metadata
- support experiment documentation

This current host surface should be read as:

- the bounded Stage 1 test-host baseline
- the intended starting point for Stage 2 LabVIEW-host integration
- intentionally coexisting with shell-local adjustability while the app remains a visible companion

The current phase-1 mandatory host surface includes at least:

- `start`
- `stop`
- `max frames`
- `recording fps`
- `save path`
- settings for shutter/exposure, hardware ROI, and gain
- ROI enable / disable
- focus value and ROI-related state

Current interpretation notes:

- focus value should currently be treated as a status field, not as a separate command surface
- `conditional stop` should currently be read as the practical `max frames reached` case, not as a broad new stop-rule system

### Command terms

These command/request names should be treated as the current stable host-facing baseline:

- `ApplyConfigurationRequest`
- `SetSaveDirectoryRequest`
- `SaveSnapshotRequest`
- `StartRecordingRequest`
- `StopRecordingRequest`
- `StartIntervalCaptureRequest`
- `StopIntervalCaptureRequest`
- `SubsystemStatus`

These names are the current bounded reference vocabulary for:

- direct Python host use
- later C#-side mapping work
- later transport mapping on top of the same core terms

Current request-context note:

- the current snapshot and bounded-recording request terms can now also carry a small additive traceability control-context subset such as `camera_alias` and optional profile identity
- this should be read as traceability-context passthrough, not as a broader host-surface expansion or inventory model
- the current CLI can now also resolve one bounded repo-local `camera_class -> configuration profile` selection before applying the existing host-neutral configuration request; this should be read as local operational convenience rather than as a broad profile-management contract

### Stable command surface

The current bounded host-oriented command surface is:

- `status`
- `snapshot`
- bounded `recording`
- bounded `interval-capture`

Current meaning:

- `status` is the polling-oriented command for host-readable current state
- `snapshot` is a short-running save command with a stable success/error envelope
- `recording` means bounded in-process recording that starts and completes within one invocation
- `interval-capture` means bounded in-process timed capture that starts and completes within one invocation and now returns the same bounded result-ownership style as the other host-oriented commands

Recording boundary note:

- `recording` is stable now only in that bounded in-process sense
- detached multi-invocation recording lifecycle control remains intentionally deferred rather than partially promised

### Stable error envelope

The current host-facing error shape should be treated as stable at this narrow level:

- `code`
- `message`
- `details`

This is a bounded baseline, not a full future error taxonomy.

### Stable success envelope ownership

The current CLI host envelope ownership should be treated as stable for the bounded baseline:

- `success`
- `command`
- `source`
- `result`
- `status`
- `error`

The exact breadth of nested payloads remains intentionally narrow.

Current adapter-facing ownership note:

- the bounded current command envelope family now also has one transport-neutral home in `vision_platform.services.api_service`
- this should be read as payload ownership reuse, not as a new transport/runtime layer

### Stable status baseline

The stable current host-readable status baseline includes:

- transport-neutral status payload mapping rather than raw core-model exposure
- readiness and availability fields from the current `SubsystemStatus` family
- one additive `active_run` subset during active bounded recording or interval capture
- focus value and ROI-related state as current status-facing fields for setup / adjustment use

This should be treated as:

- current polling baseline
- not a broader historical query or session browser

### Stable confirmed-settings subset

The current bounded confirmed-settings subset is stable enough for near-term host logging and traceability use:

- camera id
- pixel format
- exposure
- resolved save directory
- resolved file stem / extension where applicable
- accepted bounded recording or interval-capture limits where applicable

This subset is intentionally small.

It should not be read as a promise that all future resolved settings will automatically appear here.

### Stable run identity linkage

The current narrow `run_id` expectations are stable enough for bounded host reuse:

- `snapshot` exposes one deterministic `run_id`
- bounded `recording` exposes one deterministic `run_id`
- active bounded-recording polling exposes that identity during active work
- traceability blocks use the same narrow linkage idea

This is current linkage stability, not a broader run/session identity framework.

## Intentionally Deferred

The following areas are intentionally deferred rather than accidentally unfinished:

- broader transport/API DTO families
- richer query or search surfaces
- generalized artifact browsing
- detached multi-invocation recording lifecycle control
- preview-oriented control surfaces
- frontend- or IPC-specific payload contracts
- full external-interface freeze for all nested fields
- treating the current companion-shell bridge as the final headless command/runtime architecture

## Practical Handover Reading

For near-term handover or integration, read the current host baseline as:

- one bounded reusable contract nucleus
- one stable command vocabulary
- one stable narrow envelope ownership model
- one stable additive polling slice
- one stable narrow confirmed-settings and `run_id` traceability slice

Do not read it as:

- complete productized API surface
- broad host contract for all future workflows
- commitment that every current CLI detail is frozen forever

## Relation To Other Docs

- `docs/COMMANDS.md`: command vocabulary and request-level rules
- `docs/PYTHON_BASELINE_RUNBOOK.md`: practical operating rules for the current baseline
- `docs/ENTRYPOINT_AND_LAUNCH_BASELINE.md`: preferred startup surface for the current baseline
- `apps/camera_cli/STATUS.md`: current CLI-module implemented reality and still-deferred CLI surface
