# Manuals Index

## Purpose

This document is the compact entry point for the current repository manuals and boundary notes.

Use it when you want to know:

- which manual to read first
- which document explains operation versus architecture versus contract boundary
- where the current bounded Python baseline is documented without reading the full PM stack

This is an index, not a new manual layer.

## Recommended Reading By Need

### Operate The Current Python Baseline

- `docs/PYTHON_BASELINE_RUNBOOK.md`
- `docs/PYTHON_BASELINE_ENVIRONMENT.md`

Use for:

- known-good run order
- bounded local install profiles and environment contract
- simulator-versus-hardware choice
- current residual interpretation

### Choose The Right Entry Point

- `docs/ENTRYPOINT_AND_LAUNCH_BASELINE.md`

Use for:

- preferred interpreter
- preferred `python -m` form
- launcher fallback and convenience-helper rules

### Understand The Architecture Quickly

- `docs/ARCHITECTURE_BASELINE.md`
- `docs/architecture_principles.md`

Use for:

- layer ownership
- stable architectural boundaries
- `vision_platform` versus `camera_app`

### Understand The Host Surface

- `docs/HOST_CONTRACT_BASELINE.md`
- `docs/COMMANDS.md`
- `docs/RECORDING_LIFECYCLE_BOUNDARY.md`

Use for:

- stable-now host terms
- command vocabulary
- bounded recording semantics versus detached-later scope

### Review Real Hardware Evidence

- `docs/HARDWARE_EVALUATION.md`
- `docs/HARDWARE_CAPABILITIES.md`

Use for:

- tested camera-path evidence
- current residual hardware observations
- capability-backed control expectations

### Find Current Truth Or PM

- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- `docs/ROADMAP.md`
- `docs/GlobalRoadmap.md`

Use for:

- what is currently true
- what is landed
- what remains deferred or conditional

## Practical Rule

Start with the smallest doc set that matches your question:

- operation question -> runbook or launch baseline
- architecture question -> architecture baseline
- host/contract question -> host baseline and commands
- hardware question -> hardware docs
- planning/truth question -> status and workpackages

Do not start with every document at once unless the task genuinely spans multiple roles.
