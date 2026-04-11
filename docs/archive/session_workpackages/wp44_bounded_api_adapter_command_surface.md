# Bounded API Adapter Command Surface

## Purpose

This work package defines one deliberate selective-expansion option above the current bounded Python baseline.

Closure lane:

- Post-Closure Python Baseline / selective expansion

Slice role:

- adapter-facing expansion

Its purpose is to expose one narrow API-adapter command surface on top of the already stable host-neutral controller instead of treating transport/API work as an all-or-nothing future block.

## Branch

- intended branch: `feature/bounded-api-adapter-command-surface`
- activation state: landed

## Scope

Included:

- one narrow adapter-facing command surface over current stable command terms
- reuse of current controller, status payload, and bounded host-contract rules
- focused request/result shaping only where needed for the adapter

Excluded:

- broad web/API framework build-out
- authentication
- streaming feeds
- general query/search system
- detached lifecycle redesign

## Session Goal

Leave the repository with one deliberately narrow adapter-facing API slice only if an actual integration consumer needs it.

Landed outcome:

- `vision_platform.services.api_service` now owns one bounded transport-neutral command-envelope payload family in addition to the existing status payload family
- the camera CLI now reuses those adapter-facing success/error envelope builders instead of owning its command-envelope payload shape alone
- no HTTP framework, feed, authentication, or detached lifecycle scope was introduced

## Validation

- adapter-facing tests for the touched request/result path
- regression checks for the reused controller/status surface

## Documentation Updates

- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- `services/api_service/STATUS.md`
- `services/api_service/README.md` if the adapter scope changes materially

## Merge Gate

- the slice remains adapter-facing and bounded
- no broad transport platform is implied
- existing host-neutral control logic remains the reused core
