# Service Overview

## Purpose

This document explains how the current Python camera subsystem is organized internally.

Use it when you need to know:

- which code is app/adapter code
- which code is reusable service logic
- which code is hardware integration
- where the current host-control and wx-shell companion pieces live

For practical commands and operator use, start with `docs/USER_MANUAL.md`.

## Mental Model

The repository is intentionally split into thin apps over reusable services.

Current layering:

1. apps parse user input or render UI
2. control layer exposes host-neutral operations
3. services own workflows such as preview, snapshot, recording, status projection, display geometry, and companion sync
4. integrations own camera driver implementations
5. libraries and models own portable contracts and reusable domain helpers

Compact shape:

```text
apps
  camera_cli / local_shell / opencv_prototype
        |
control.command_controller
        |
services
  recording / stream / display / companion / api payload
        |
integrations.camera
        |
hardware or simulator
```

The goal is to keep the Python prototype portable toward a later headless kernel, C#/.NET reuse, and additional frontends.

## Main App Surfaces

### `vision_platform.apps.camera_cli`

Role:

- command-line adapter for status, snapshot, interval capture, and bounded recording
- thin over the shared command/controller and service layer
- useful for smoke tests, reference scenarios, and host-style command examples

It should not own:

- camera SDK calls
- recording internals
- UI state
- broad host transport semantics

### `vision_platform.apps.local_shell`

Role:

- current visible wxPython companion shell
- operator-facing preview, snapshot, recording, settings, focus, ROI, and crosshair surface
- bounded host-control endpoint through `local_shell control`

It owns:

- wx window layout
- wx event translation
- bitmap painting
- local menus, shortcuts, and transient operator feedback

It should not own:

- camera acquisition semantics
- recording semantics
- host contract vocabulary
- display-coordinate math that can be shared

### `vision_platform.apps.opencv_prototype`

Role:

- older optional prototype and visual inspection surface
- still useful as fallback/reference for preview and hardware experiments

It is not the current primary product shell.

### `vision_platform.apps.postprocess_tool`

Role:

- small offline focus-report utility over stored images
- useful for checking saved snapshot or interval output

It is not a broad measurement workstation.

## Control Layer

### `vision_platform.control.command_controller`

Role:

- host-neutral command surface above the core services
- central place where typed command requests are handled
- shared by CLI, demos, and shell paths where applicable

Representative command terms:

- `ApplyConfigurationRequest`
- `SetSaveDirectoryRequest`
- `SaveSnapshotRequest`
- `StartRecordingRequest`
- `StopRecordingRequest`
- `StartIntervalCaptureRequest`
- `StopIntervalCaptureRequest`
- `SubsystemStatus`

This layer is the contract nucleus for later host, transport, or C# mapping.

## Core Services

### Recording Services

Package:

- `vision_platform.services.recording_service`

Main responsibilities:

- camera service composition
- snapshot saving
- bounded recording
- interval capture
- frame writing
- deterministic file naming
- recording logs
- traceability
- snapshot and artifact focus metadata

Use this layer for acquisition workflows that produce files.

### Stream Services

Package:

- `vision_platform.services.stream_service`

Main responsibilities:

- preview frame acquisition
- shared frame source
- preview service
- focus preview service
- ROI state service
- stream composition for preview plus recording or interval capture

Use this layer for live acquisition and preview-adjacent data.

### Display Services

Package:

- `vision_platform.services.display_service`

Main responsibilities:

- display geometry
- source/viewport coordinate mapping
- preview interaction commands
- overlay composition
- preview status model creation
- coordinate export
- viewport image rendering helper

Use this layer for UI-independent display behavior.

The wx shell still owns actual wx bitmap painting.

### Camera Capability And Health Services

Modules:

- `camera_capability_service.py`
- `camera_configuration_validation_service.py`
- `camera_health_service.py`
- `camera_runtime_event_service.py`

Main responsibilities:

- expose bounded capability information
- validate configuration against generic or probed capability data
- derive camera health/readiness
- describe runtime events without tying them to a transport

These services support host-readable status and later integration surfaces.

### Companion Shell Services

Modules:

- `local_shell_session_protocol.py`
- `local_shell_session_service.py`
- `local_shell_command_execution_service.py`
- `local_shell_command_polling_service.py`
- `local_shell_status_projection_service.py`
- `local_shell_status_publication_service.py`
- `local_shell_projection_input_builder_service.py`
- `local_shell_failure_reflection_state_service.py`
- `local_shell_runtime_tick_coordinator.py`
- `local_shell_companion_facade.py`
- `companion_contract_service.py`

Main responsibilities:

- represent the current file-backed local-shell session protocol
- read pending external commands
- execute bounded companion commands through the existing controller path
- publish current shell status snapshots
- project setup, snapshot, recording, and failure state into host-readable payloads
- coordinate one shell tick without introducing daemon or transport semantics
- provide one app-facing facade consumed by the wx shell

Boundary:

- this is the current bounded companion path
- it is not the final headless runtime architecture
- later transport or daemon work must be justified by a concrete integration need

### API-Style Payload Services

Package:

- `vision_platform.services.api_service`

Main responsibilities:

- shape bounded command payloads
- shape status payloads
- provide transport-neutral JSON-like envelope ownership

Boundary:

- this is payload reuse, not an HTTP service
- broader API/transport work remains deferred

### Artifact, Time, And Audit Services

Modules:

- `artifact_reference_service.py`
- `hardware_audit_service.py`

Main responsibilities:

- provide artifact-reference and time-context helpers
- record hardware warnings, degraded startup states, and incidents through a bounded audit log

The hardware audit path is not normal artifact traceability and not a full run history browser.

## Integration Layer

Package:

- `vision_platform.integrations.camera`

Main responsibilities:

- real Vimba X camera driver
- simulated camera driver
- driver abstraction shared by services

Rule:

- SDK-specific calls belong here
- simulated behavior belongs in the simulator driver
- services should work against the same camera-driver abstraction

## Models And Libraries

### `vision_platform.models`

Role:

- Python-facing request, status, frame, configuration, recording, and preview data models

### `vision_platform.libraries`

Role:

- portable reusable kernels and contracts
- includes common models, ROI helpers, focus core, and tracking core baseline

Current rule:

- libraries may expose some target-facing contract shapes ahead of full implementation, but module status docs should mark readiness clearly

## Current Host/Shell Runtime Flow

When a host controls the running wx shell:

1. `vision_platform.apps.local_shell` starts the wx shell
2. shell creates or updates a file-backed active session under `captures/wx_shell_sessions/`
3. external process calls `vision_platform.apps.local_shell control ...`
4. control adapter writes a pending command into the active session
5. shell tick uses companion services to poll, execute, and write a result
6. status-publication service writes the latest shell status snapshot
7. host reads JSON result/status from the session path

This flow is intentionally local and bounded.

## Current CLI Runtime Flow

When a user runs the camera CLI:

1. `camera_cli` parses arguments
2. source selection chooses simulated or hardware-backed driver setup
3. optional alias/profile resolution applies repo-local configuration shortcuts
4. command controller executes status, snapshot, recording, or interval capture
5. services perform acquisition and file output
6. CLI prints a bounded host-style result envelope

This flow is useful for repeatable validation, but the CLI is not the business-logic owner.

## What To Change Where

Add or adjust camera SDK behavior:

- use `vision_platform.integrations.camera`

Change snapshot, recording, naming, writer, or traceability behavior:

- use `vision_platform.services.recording_service`

Change preview acquisition or shared-frame behavior:

- use `vision_platform.services.stream_service`

Change ROI/focus state used by preview:

- use stream services and relevant libraries, not app-local UI state only

Change display mapping, zoom/pan math, overlay composition, or interaction transitions:

- use `vision_platform.services.display_service`

Change host-neutral command behavior:

- use `vision_platform.control.command_controller` and request/status models

Change wx layout, buttons, menus, shortcuts, or bitmap painting:

- use `vision_platform.apps.local_shell`

Change file-backed host-to-shell sync mechanics:

- use the companion shell services under `vision_platform.services`

Change command-line argument names or CLI help:

- use `vision_platform.apps.camera_cli` or `vision_platform.apps.local_shell.control_cli`

## Deferred Boundaries

Do not treat these as implemented just because the service boundaries exist:

- production daemon
- HTTP API server
- final IPC/transport contract
- detached long-running recording control across unrelated processes
- browser UI
- final C# implementation
- broad measurement workstation

The current rule is evidence-first: open one of these areas only when there is a concrete residual, integration need, test failure, or observed workflow friction.
