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
11. If the task changes documentation structure, update rules, or documentation role boundaries, read `docs/DOCUMENTATION_PLAYBOOK.md`.
12. If context is getting dense, run a documentation checkpoint (`docs/STATUS.md`, `docs/WORKPACKAGES.md`, active `docs/session_workpackages/wpXX_*.md`) before broad further changes.

## Current Baseline

- The repository now operates from `Usable Camera Subsystem / Pre-Product Baseline`, not from an open Extended MVP closure phase.
- The preferred platform-facing implementation surface is `src/vision_platform`, with `src/camera_app` retained as a compatibility bridge while physical migration stays incremental.
- The bounded baseline already covers snapshot, preview, bounded recording, bounded interval capture, simulation, host-style command flow, traceability, and bounded offline reuse.
- The tested hardware path has bounded real-device evidence on `DEV_1AB22C046D81`; broader hardware matrix coverage is still intentionally out of scope.
- The OpenCV prototype remains an optional frontend/prototype path rather than the platform core.

## Historical vs Current

- historical context: repository reorganization and Extended MVP closure built the current baseline
- current active phase: `Usable Camera Subsystem / Pre-Product Baseline`
- immediate priorities: local usability, host-side usability, official reference scenarios, then headless-kernel preparation
- later but not current: broad transport/platform work, broad MCP expansion, broad packaging, full C# handover

## Current Truth Map

- preferred implementation surface: `src/vision_platform/...`
- legacy compatibility surface: `src/camera_app/...`
- module docs live in the root module folders under `apps/`, `integrations/`, `services/`, and `libraries/`
- module `README.md`: purpose, boundaries, intended contract surface
- module `STATUS.md`: current implemented state, residuals, and local known limits
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
2. Treat the current Python baseline as already real and reusable on its bounded tested path.
3. Derive new slices from concrete residuals, operational friction, or explicit expansion needs rather than from old MVP-closure logic.
4. Keep host/control, runtime services, hardware integration, and UI/frontend shells separated.
5. Open broader transport, frontend, offline, or handover scope only when there is a clear reason.
6. Continue documenting verified state and stable boundaries without turning docs into shadow PM surfaces.

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
- For documentation-model or documentation-maintenance questions:
  - `docs/DOCUMENTATION_PLAYBOOK.md`
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
  - `docs/PYTHON_BASELINE_RUNBOOK.md`
  - `docs/ENTRYPOINT_AND_LAUNCH_BASELINE.md`
  - `docs/archive/session_workpackages/wp04_hardware_validation_phase_9.md`
- For operational or launch-readiness questions:
  - `docs/MANUALS_INDEX.md`
  - `docs/PYTHON_BASELINE_ENVIRONMENT.md`
  - `docs/PYTHON_BASELINE_RUNBOOK.md`
  - `docs/ENTRYPOINT_AND_LAUNCH_BASELINE.md`
- For architecture or boundary questions:
  - `docs/MANUALS_INDEX.md`
  - `docs/ARCHITECTURE_BASELINE.md`
  - `docs/architecture_principles.md`
- For host-contract or handover-boundary questions:
  - `docs/HOST_CONTRACT_BASELINE.md`
  - `docs/COMMANDS.md`
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
- `docs/PYTHON_BASELINE_RUNBOOK.md` is the compact operating reference for the current post-closure Python baseline.
- `docs/PYTHON_BASELINE_ENVIRONMENT.md` is the compact bounded install-profile and environment-contract reference.
- `docs/ENTRYPOINT_AND_LAUNCH_BASELINE.md` is the compact startup-surface reference for the preferred current entry points.
- `docs/MANUALS_INDEX.md` is the compact reading map for manuals and boundary notes.
- `docs/ARCHITECTURE_BASELINE.md` is the compact architecture reference for the current post-closure baseline.
- `docs/HOST_CONTRACT_BASELINE.md` is the compact stable-now / deferred-later reference for the bounded current host surface.
- `docs/DOCUMENTATION_PLAYBOOK.md` is the documentation-role and maintenance reference for stable, operational, and current-state docs.
- `docs/module_doc_audit.md` is the current reference for how module-local docs should be used and trimmed.
- `docs/root_category_audit.md` is the current reference for how `apps/`, `integrations/`, `services/`, and `libraries/` are meant to be used.
- `docs/ROADMAP.md` is the repository delivery sequence.
- `docs/GlobalRoadmap.md` is the long-term platform direction.
- `docs/archive/StartPrompt.md` is historical reference only.
