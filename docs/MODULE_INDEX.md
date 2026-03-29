# Module Index

## Root Guidance

- `docs/SESSION_START.md`: compact session bootstrap and reading map
- `docs/WORKFLOW.md`: operational execution flow for agents
- `docs/WORKPACKAGES.md`: central work-package queue and next-step prioritization
- `docs/root_category_audit.md`: meaning and decision rules for `apps/`, `integrations/`, `services/`, and `libraries/`
- primary command-surface rule: keep one host-neutral control layer; CLI is a local adapter and future API/feed work should reuse that same layer
- `docs/ProjectDescription.md`: platform target picture and module responsibilities
- `docs/ProjectAgents.md`: repository reorganization workflow and modular documentation rules
- `docs/GlobalRoadmap.md`: platform-wide master roadmap
- `docs/ROADMAP.md`: repository-specific implementation flow
- `docs/STATUS.md`: verified current implementation state
- `docs/git_strategy.md`: operational branch and commit workflow
- `docs/branch_backlog.md`: file-to-branch assignment for remaining worktree changes

## Active Modules

| Module | Status | Notes |
| --- | --- | --- |
| `apps/camera_cli` | active baseline | unified camera-oriented CLI for status, snapshot, recording, and interval capture |
| `integrations/camera` | active core | drivers implemented, hardware validation still open |
| `services/stream_service` | active core | preview/shared acquisition implemented |
| `services/recording_service` | active core | snapshot, interval capture, recording implemented |
| `services/display_service` | active baseline | UI-free overlay composition implemented; lightweight payload demo exists, renderer-facing adapter still open |
| `apps/opencv_prototype` | active prototype | simulator and first real-hardware preview path available; viewport-based preview controls now implemented |
| `libraries/common_models` | active foundation | portable contracts and overlay/display payloads added; some target-facing contract elements are intentionally ahead of implementation and must be marked in module status |
| `libraries/roi_core` | active foundation | ROI bounds, centroid, pixel bounds, and rectangle/ellipse mask helpers implemented; freehand remains deferred |
| `libraries/focus_core` | active baseline | Laplace focus scoring and overlay-ready mapping added; live preview-adjacent consumers now use the baseline |

For each active module:

- read before edits:
  - `README.md`
  - `STATUS.md`
- `ROADMAP.md`: local future intent only when it adds module-specific value beyond the central work-package queue

Root category usage:

- `apps/`: runnable or operator/developer-facing shells
- `integrations/`: external adapters
- `services/`: workflow orchestration
- `libraries/`: reusable core building blocks

## Prepared Later Modules

| Module | Status | Notes |
| --- | --- | --- |
| `libraries/tracking_core` | active baseline | profile-based edge baseline implemented; drift/tracking expansion remains open |
| `services/api_service` | active baseline | first adapter-facing status payload family implemented above the shared host-neutral control layer |
| `apps/postprocess_tool` | active baseline | thin stored-image focus-report baseline implemented above shared sample-image and focus contracts |
| `apps/desktop_app` | prepared only | reserved for later desktop frontend work |

For each prepared-only module:

- read before first activation work:
  - `README.md`
  - `STATUS.md`
  - `ROADMAP.md`

Governance note:

- `docs/module_doc_audit.md` records the current keep/shrink guidance for module-local docs
