# Detached Recording Lifecycle Decision Slice

## Purpose

This work package defines the next narrow decision-oriented handover slice after the landed host-contract clarification.

Closure lane:

- Post-Closure Python Baseline / Later Product And Handover Preparation

Slice role:

- decision and scope-boundary clarification

Scope level:

- bounded recording lifecycle semantics only

Its purpose is to make explicit whether detached multi-invocation recording lifecycle control should remain deferred or become a deliberate next expansion target, without implementing that broader behavior yet.

This package should be read as:

- a scope-decision slice
- not runtime redesign
- not immediate feature expansion

## Branch

- intended branch: `docs/detached-recording-lifecycle-decision`
- activation state: queued

## Scope

Included:

- document the current bounded in-process recording meaning
- document why detached lifecycle control is currently deferred
- identify the smallest later activation shape if that direction is chosen

Excluded:

- implementation of detached lifecycle control
- transport redesign
- broader recording-service refactoring

What this package does not close:

- the full future recording-control roadmap

## Session Goal

Leave the repository with one clearer documented decision boundary for bounded current recording versus any later detached host-control path.

## Landed Outcome

Observed result on March 30, 2026:

- the current repository already has one consistent bounded-recording baseline across:
  - CLI host envelopes
  - simulator-first recovery tests
  - traceability / `run_id` linkage
  - bounded real-hardware evidence
- no current repository surface actually implements detached multi-invocation recording lifecycle control
- the main remaining ambiguity was therefore documentation and handover reading, not missing runtime behavior

Decision recorded by this slice:

- `recording` on the current stable Python baseline means bounded in-process recording on one live subsystem ownership boundary
- `StartRecordingRequest` and `StopRecordingRequest` should not currently be read as a promise of detached start-in-one-process / stop-in-another-process control
- detached multi-invocation recording lifecycle control remains intentionally deferred

Smallest later activation shape recorded:

- if detached recording is chosen later, the smallest justified next step should start with one explicit long-lived host-owned subsystem boundary plus one narrow identity-bearing start/status/stop surface
- it should not begin as broad transport redesign, daemonization, or general background-job management

