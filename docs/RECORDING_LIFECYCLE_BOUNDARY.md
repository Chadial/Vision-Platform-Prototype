# Recording Lifecycle Boundary

## Purpose

This document defines the current decision boundary for recording lifecycle semantics in the post-closure Python baseline.

Use it to answer:

- what `recording` means on the current stable host-facing baseline
- what detached lifecycle control does not currently mean
- why detached multi-invocation control remains deferred
- what the smallest later activation shape would be if that direction is chosen

This is a boundary and decision document.

It does not define:

- a new recording implementation
- a transport design
- a background service architecture
- a commitment to detached recording as the next mandatory feature

## Current Decision

The current Python baseline should treat `recording` as:

- bounded
- in-process
- owned by one live subsystem instance
- completed within the same invocation / process lifetime that started it

The current baseline should not treat `recording` as:

- detached across multiple process invocations
- background-job control
- daemon-managed capture
- resumable remote lifecycle ownership

This is an intentional scope boundary, not an accidental gap.

## Current Stable Meaning

For the current host-oriented baseline:

- `StartRecordingRequest` starts recording on the active in-process subsystem instance
- recording is expected to end through bounded completion or an explicit stop on that same live subsystem path
- `StopRecordingRequest` belongs to the same live process / subsystem ownership boundary
- active polling and `run_id` linkage are meaningful during the currently active in-process run

Current practical examples:

- bounded CLI recording
- bounded integrated hardware command-flow recording
- simulator-first reliability and recovery tests on the same subsystem instance

These current semantics are already validated and documented.

## Why Detached Lifecycle Remains Deferred

Detached multi-invocation recording lifecycle control remains deferred because the current baseline is intentionally optimized for:

- one bounded Python working baseline
- one thin host-oriented command layer
- explicit in-process ownership of camera, stream, writer, and status state
- narrow traceability and status linkage rather than long-lived remote orchestration

Detached lifecycle control would materially widen scope because it would need clearer decisions about:

- process ownership across start / status / stop boundaries
- long-lived subsystem identity across separate invocations
- active-run persistence outside one process lifetime
- what happens when the initiating caller exits
- whether stop / status targets a live in-memory subsystem, a background worker, or a transport endpoint

Those decisions belong to a later deliberate expansion step, not to the current stable host baseline.

## Current Practical Rule

For current operation and handover:

- treat bounded recording as the stable baseline
- treat `StopRecordingRequest` as meaningful only against the same live subsystem ownership boundary
- do not promise detached recording across separate CLI invocations
- do not describe the current baseline as a background-recording controller

If a host needs detached lifecycle behavior later, that should be introduced as a separate explicit expansion slice.

## Smallest Later Activation Shape

If detached recording lifecycle control is chosen later, the smallest justified next shape should be:

- one explicitly long-lived host-owned subsystem boundary
- one recording start that returns an identity usable by later status / stop calls
- one explicit ownership rule for who keeps the subsystem alive while recording continues
- one narrow status / stop surface over that same long-lived boundary

The smallest later shape should not start with:

- a broad transport redesign
- multi-camera orchestration
- broad background-job management
- a full remote-control framework

## Relation To Other Docs

- `docs/HOST_CONTRACT_BASELINE.md`: stable-now versus deferred-later host boundary
- `docs/COMMANDS.md`: command vocabulary and bounded command semantics
- `docs/PYTHON_BASELINE_RUNBOOK.md`: practical operating rule for bounded recording use today
- `apps/camera_cli/STATUS.md`: current CLI-module implementation scope
