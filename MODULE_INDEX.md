# Module Index

## Root Guidance

- `ProjectDescription.md`: platform target picture and module responsibilities
- `ProjectAgents.md`: repository reorganization workflow and modular documentation rules
- `GlobalRoadmap.md`: platform-wide master roadmap
- `docs/ROADMAP.md`: repository-specific implementation flow
- `docs/STATUS.md`: verified current implementation state
- `docs/git_strategy.md`: operational branch and commit workflow
- `docs/branch_backlog.md`: file-to-branch assignment for remaining worktree changes

## Active Modules

| Module | Status | Notes |
| --- | --- | --- |
| `integrations/camera` | active core | drivers implemented, hardware validation still open |
| `services/stream_service` | active core | preview/shared acquisition implemented |
| `services/recording_service` | active core | snapshot, interval capture, recording implemented |
| `services/display_service` | active baseline | UI-free overlay composition for preview/snapshot focus and ROI |
| `apps/opencv_prototype` | active prototype | runnable wrapper scripts and demos available |
| `libraries/common_models` | active foundation | portable contracts and overlay/display payloads added |
| `libraries/roi_core` | active foundation | ROI bounds and centroid helpers added |
| `libraries/focus_core` | active baseline | Laplace focus scoring and overlay-ready mapping added |

For each active module:

- `README.md`: purpose and interfaces
- `STATUS.md`: current maturity and risks
- `ROADMAP.md`: next steps

## Prepared Later Modules

| Module | Status | Notes |
| --- | --- | --- |
| `libraries/tracking_core` | prepared only | reserved for edge/tracking/drift work |
| `services/api_service` | prepared only | reserved for external feed/API work |
| `apps/postprocess_tool` | prepared only | reserved for offline evaluation tooling |
| `apps/desktop_app` | prepared only | reserved for later desktop frontend work |
