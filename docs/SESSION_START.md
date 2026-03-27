# Session Start

## Purpose

This file is the fast bootstrap for a new agent session.

Read this first to get from zero context to a workable repository overview without scanning the full document set.

## Five-Minute Startup Checklist

1. Read `Agents.md`, then this file, then `docs/MODULE_INDEX.md`.
2. Check the current branch.
3. Run `git status --short`.
4. If the task changes repository state, read `docs/git_strategy.md`.
5. If the worktree is dirty or branch scope is unclear, open `docs/branch_backlog.md` before editing.
6. If the current branch is `main` and the task is substantive, create the correct branch first.
7. Read the target module's `README.md`, `STATUS.md`, and `ROADMAP.md` before changing code in that module.

## Current Baseline

- The repository is a Python-first vision platform prototype with a parallel repository reorganization toward `src/vision_platform`.
- Legacy compatibility still exists under `src/camera_app`, but new platform-facing code is being moved into `src/vision_platform`.
- The core baseline is implemented for snapshot, preview, recording, interval capture, simulated drivers, and host-style command flow.
- The optional OpenCV prototype now includes a first real-hardware preview path with viewport-based `fit-to-window` and zoom controls.
- ROI mask primitives, a first focus baseline, and UI-free overlay payload composition are implemented.
- Broad real-hardware validation is still incomplete even though targeted hardware preview and smoke checks are working again.

## Current Truth Map

- preferred implementation surface: `src/vision_platform/...`
- legacy compatibility surface: `src/camera_app/...`
- module docs live in the root module folders under `apps/`, `integrations/`, `services/`, and `libraries/`
- module `README.md`: purpose, boundaries, intended contract surface
- module `STATUS.md`: current implemented state, gaps, risks, next step
- module `ROADMAP.md`: intended next work and target-facing surface that may run ahead of implementation when marked clearly
- session work-package handoff notes live under `docs/session_workpackages/`, with completed ones moved to `docs/archive/session_workpackages/`

## Current Architecture Rules

- Keep camera drivers, application services, storage, control, and UI/display concerns separate.
- Real hardware and simulated sources must stay behind the same driver abstraction.
- Screen-dependent behavior such as fit-to-window, zoom, pan, status bars, and display-space overlay transforms belongs in the UI/display layer, not the camera core.
- The OpenCV prototype is the current place for local operator-facing preview experiments.

## Current Priority

1. Keep the Python core stable and understandable.
2. Extend the OpenCV prototype only in the UI/display-facing layer.
3. Continue documenting verified state and next steps as features land.
4. Broaden real-hardware validation when practical.

## Active Recovery Note

- If work resumes on real-hardware validation, use `docs/session_workpackages/hardware_validation_phase_9.md` as the recovery entry point for the current Phase 9 work package.

## Mandatory Reads

Read these for every new session:

1. `Agents.md`
2. `docs/SESSION_START.md`
3. `docs/MODULE_INDEX.md`

## Task-Based Reads

- For implementation against the current baseline:
  - `docs/STATUS.md`
- For planning or next-step decisions:
  - `docs/ROADMAP.md`
- For long-range architecture or migration questions:
  - `docs/GlobalRoadmap.md`
  - `docs/ProjectDescription.md`
  - `docs/ProjectAgents.md`
- For any substantive repository change:
  - `docs/git_strategy.md`
- For dirty or mixed worktrees:
  - `docs/branch_backlog.md`
- For git or branch workflow questions:
  - `docs/git_strategy.md`
  - `docs/branch_backlog.md`
- For module-specific work:
  - that module's `README.md`
  - that module's `STATUS.md`
  - that module's `ROADMAP.md`
- For hardware-specific work:
  - `docs/HARDWARE_EVALUATION.md`
  - `docs/session_workpackages/hardware_validation_phase_9.md`

## Working Defaults

- `docs/STATUS.md` is the current implementation truth.
- `docs/ROADMAP.md` is the repository delivery sequence.
- `docs/GlobalRoadmap.md` is the long-term platform direction.
- `docs/archive/StartPrompt.md` is historical reference only.
