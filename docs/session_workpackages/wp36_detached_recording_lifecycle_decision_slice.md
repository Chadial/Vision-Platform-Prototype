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

