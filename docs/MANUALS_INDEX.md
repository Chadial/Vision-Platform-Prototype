# Manuals Index

## Purpose

This document is the compact entry point for the current repository manuals and boundary notes.

Use it when you want to know:

- which manual to read first
- which document explains operation versus architecture versus contract boundary
- where the current bounded Python baseline is documented without reading the full PM stack

This is an index, not a new manual layer.

## Recommended Reading By Need

### Start Here

- `docs/USER_MANUAL.md`

Use for:

- the current goal in plain terms
- which app or command to start
- CLI, wx shell, and host-style shell-control examples
- what is implemented now versus deferred

### Understand The Service Structure

- `docs/SERVICE_OVERVIEW.md`

Use for:

- the difference between apps, control layer, services, integrations, models, and libraries
- where CLI behavior ends and shared service behavior starts
- where companion-shell command/session mechanics live
- what to change where

### Operate The Current Python Baseline

- `docs/PYTHON_BASELINE_RUNBOOK.md`
- `docs/PYTHON_BASELINE_ENVIRONMENT.md`
- `docs/REFERENCE_SCENARIOS.md`

Use for:

- known-good run order
- bounded local install profiles and environment contract
- bounded technical snapshot / recording / interval reference recipes beneath the broader current workflows
- the compact reference-scenario validation path via `scripts/launchers/run_reference_scenario_validation.py`
- simulator-versus-hardware choice
- current residual interpretation

### Choose The Right Entry Point

- `docs/ENTRYPOINT_AND_LAUNCH_BASELINE.md`

Use for:

- preferred interpreter
- preferred `python -m` form
- launcher fallback and convenience-helper rules
- the quickest validated entry path for the current technical reference flows

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
- `docs/ENTRYPOINT_AND_LAUNCH_BASELINE.md`

Use for:

- stable-now host terms
- command vocabulary
- bounded recording semantics versus detached-later scope
- the current local shell companion flow and its bounded `control` adapter

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

### Understand Bigger-Picture Camera Alignment

- `docs/BiggerPictureNotes/13_Camera.md`
- `docs/BiggerPictureNotes/13.1_Camera.md`
- `docs/BiggerPictureNotes/camera_einbindung_analyse_fuer_planung.md`
- `docs/BiggerPictureNotes/camera_repo_integrationsanalyse_fuer_multi_modul_system.md`
- `docs/BiggerPictureNotes/kamera_und_grossprojekt_kompatibilitaetseinschaetzung.md`
- `docs/BiggerPictureNotes/Camera_Repo_Strategieplanung_fuer_Gesamtprojekt.md`
- `docs/BiggerPictureNotes/camera_integration_surface_v0.1.md`
- `docs/BiggerPictureNotes/camera_subsystem_role_and_boundaries.md`

Use for:

- larger-system camera-role questions
- architecture and integration-boundary sharpening
- strategy and transformation planning from the current repo toward a later multi-module camera subsystem
- compatibility reading between the current repository and the broader project direction
- the deliberately small camera-integration fore-stage that should precede broader end-architecture work in this repo

## Practical Rule

Start with the smallest doc set that matches your question:

- overview question -> user manual
- operation question -> runbook or launch baseline
- service ownership question -> service overview
- architecture question -> architecture baseline
- host/contract question -> host baseline and commands
- hardware question -> hardware docs
- planning/truth question -> status and workpackages

Do not start with every document at once unless the task genuinely spans multiple roles.
