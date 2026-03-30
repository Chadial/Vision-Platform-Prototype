# Host Contract Stability And Deferred Surface Clarification

## Purpose

This work package defines the first explicit later-handover / productization clarification slice in the post-closure phase.

Closure lane:

- Post-Closure Python Baseline / Later Product And Handover Preparation

Slice role:

- contract clarification and deferred-scope mapping

Scope level:

- current host-facing command, status, and result baseline only

Its purpose is to make the existing host-oriented Python baseline easier to hand over by documenting which parts of the current command/status/result surface should be treated as stable enough for reuse now and which broader surfaces remain intentionally deferred.

This package should be read as:

- current host-contract clarification
- not transport expansion
- not a full API-design package

## Branch

- intended branch: `docs/host-contract-stability-clarification`
- activation state: queued

## Scope

Included:

- inspect the current host-facing command, status, and result surfaces
- classify a small stable baseline for:
  - command names
  - core request/result shapes
  - active polling subset
  - confirmed-settings subset
  - run-id linkage expectations
- document which broader areas remain deferred, such as:
  - broader transport/API DTO families
  - richer query surfaces
  - broader frontend or IPC assumptions

Excluded:

- transport implementation
- contract redesign
- new host commands
- broad API growth

What this package does not close:

- full external interface productization
- complete transport-neutral contract freeze
- full C# handover planning

## Session Goal

Leave the repository with one clearer host-contract baseline so later handover or integration work starts from explicit documented stability assumptions instead of inference.

## Execution Plan

1. Re-read:
   - `docs/STATUS.md`
   - `docs/WORKPACKAGES.md`
   - `apps/camera_cli/STATUS.md`
   - relevant host/control module docs
2. Inspect the current command/result/status surfaces.
3. Document one narrow stable-now / deferred-later split.
4. Link that clarification from the central PM/status docs if needed.

## Validation

- documentation consistency review against the current implemented host surface

## Documentation Updates

- one central or module-local contract-clarification doc section
- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- host/control module docs if they are the clearest home for the stability note

## Expected Commit Shape

1. `docs: clarify host contract stability baseline`
2. `docs: mark deferred host surfaces explicitly`

## Merge Gate

- the slice remains documentation-only and contract-clarifying
- the current host baseline becomes easier to hand over without widening it
- no transport/API expansion is bundled

## Recovery Note

To activate this work package later:

1. read the current host/control status docs
2. inspect the current CLI/API-facing status and command-result surface
3. keep the stable-now / deferred-later split narrow and explicit
