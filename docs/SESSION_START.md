# Session Start

## Purpose

This file is the fast bootstrap for a new agent session.

Read this first to get from zero context to a workable repository overview without scanning the full document set.

## Five-Minute Startup Checklist

1. Read `AGENTS.md`, then this file, then `docs/MODULE_INDEX.md`.
2. Read `docs/WORKPACKAGES.md` when the next task is not already explicit.
3. Check the current branch.
4. Run `git status --short`.
5. If the task changes repository state, read `docs/git_strategy.md`.
6. If the worktree is dirty or branch scope is unclear, open `docs/branch_backlog.md` before editing.
7. If the current branch is `main` and the task is substantive, create the correct branch first.
8. Read the target module's `README.md` and `STATUS.md` before changing code in that module; read that module's `ROADMAP.md` only when the local module plan is directly needed.
9. If the target module is `prepared only`, read its `ROADMAP.md` before first activation work in that module.
10. If the task may create a new module or move logic across `apps/`, `integrations/`, `services/`, or `libraries/`, read `docs/root_category_audit.md` first.

## Current Baseline

- The repository is a Python-first vision platform prototype with a parallel repository reorganization toward `src/vision_platform`.
- Legacy compatibility still exists under `src/camera_app`, but new platform-facing code is being moved into `src/vision_platform`.
- The core baseline is implemented for snapshot, preview, recording, interval capture, simulated drivers, and host-style command flow.
- The optional OpenCV prototype now includes a first real-hardware preview path with viewport-based `fit-to-window` and zoom controls.
- The OpenCV prototype also now includes a first operator-facing point-selection baseline with crosshair display, coordinate readout, and `c`-based coordinate copy.
- A first camera-oriented CLI baseline now exists under `src/vision_platform/apps/camera_cli` for status, snapshot, bounded recording, and bounded interval capture without the OpenCV preview path.
- ROI mask primitives, a first focus baseline, and UI-free overlay payload composition are implemented.
- Phase 9 hardware validation has been completed for the previously connected camera path, but the physical hardware is currently not attached locally.

## Current Truth Map

- preferred implementation surface: `src/vision_platform/...`
- legacy compatibility surface: `src/camera_app/...`
- module docs live in the root module folders under `apps/`, `integrations/`, `services/`, and `libraries/`
- module `README.md`: purpose, boundaries, intended contract surface
- module `STATUS.md`: current implemented state, gaps, risks, next step
- module `ROADMAP.md`: optional local future intent only when genuinely useful; central project planning now lives in `docs/WORKPACKAGES.md`
- session work-package handoff notes live under `docs/session_workpackages/`, with completed ones moved to `docs/archive/session_workpackages/`

## Current Architecture Rules

- Keep camera drivers, application services, storage, control, and UI/display concerns separate.
- Real hardware and simulated sources must stay behind the same driver abstraction.
- Screen-dependent behavior such as fit-to-window, zoom, pan, status bars, and display-space overlay transforms belongs in the UI/display layer, not the camera core.
- Treat the host-neutral controller/application command surface as the primary control layer; CLI and any future API/feed surface are adapters over that layer, not competing cores.
- The OpenCV prototype is the current place for local operator-facing preview experiments.

## Current Priority

1. Keep the Python core stable and understandable.
2. Treat `Host Control Closure`, `Experiment Reliability Closure`, and the first `Data And Logging Closure` slice as landed baseline hardening.
3. Treat `WP14` and `WP15` as landed narrow slices inside still-open closure lanes.
4. Use `docs/session_workpackages/wp16_data_logging_traceability.md` as the current default planning package.
5. Open an additional frontend package only when another shell beyond the current OpenCV prototype is actually needed.
6. Keep any further OpenCV work separate and only in the UI/display-facing layer.
7. Continue documenting verified state and next steps as features land.
8. Broaden real-hardware validation when practical.

## Mandatory Reads

Read these for every new session:

1. `AGENTS.md`
2. `docs/SESSION_START.md`
3. `docs/MODULE_INDEX.md`
4. `docs/WORKPACKAGES.md` when the next task is not explicitly assigned

## Task-Based Reads

- For implementation against the current baseline:
  - `docs/STATUS.md`
- For active prioritization or next-step selection:
  - `docs/WORKPACKAGES.md`
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
  - that module's `ROADMAP.md` only when the module is prepared-only or the selected work package explicitly expands that module's local future path
- For hardware-specific work:
  - `docs/HARDWARE_EVALUATION.md`
  - `docs/HARDWARE_CAPABILITIES.md`
  - `docs/archive/session_workpackages/wp04_hardware_validation_phase_9.md`
- For the next OpenCV UI/operator work:
  - `docs/archive/session_workpackages/wp03_opencv_ui_operator_block.md`
- For camera-oriented command-surface work:
  - `docs/archive/session_workpackages/wp01_camera_cli.md`
- For host-neutral command-surface follow-up work:
  - `docs/archive/session_workpackages/wp02_host_integration_command_surface.md`
- For the next optional frontend-expansion work:
  - `docs/session_workpackages/wp11_additional_frontends.md`

## Working Defaults

- `docs/STATUS.md` is the current implementation truth.
- `docs/WORKPACKAGES.md` is the central queue for the next concrete work slice.
- `docs/module_doc_audit.md` is the current reference for how module-local docs should be used and trimmed.
- `docs/root_category_audit.md` is the current reference for how `apps/`, `integrations/`, `services/`, and `libraries/` are meant to be used.
- `docs/ROADMAP.md` is the repository delivery sequence.
- `docs/GlobalRoadmap.md` is the long-term platform direction.
- `docs/archive/StartPrompt.md` is historical reference only.
