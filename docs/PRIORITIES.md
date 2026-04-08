# Priorities

## Purpose

This note turns the current implicit and explicit task landscape into a visible working queue.

Use it as a brainstormed prioritization aid and derived reading view, not as the authoritative work-package queue or status carrier.

For active implementation ordering, continue to use:

- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- `docs/TARGET_MAP.md`

## Must Now

- keep completed refactor slices like `WP70` out of the active queue unless merge cleanup or a regression reopens them
- keep the `vision_platform` namespace as the real implementation home
- prevent `camera_app` compatibility shims from growing back into duplicate implementation surfaces
- keep the central docs aligned with the actual implementation state

## Should Next

- remove any remaining redundant legacy import paths that still point at old implementation locations
- keep the local shell moving toward the primary daily working frontend
- keep host-side command/status behavior practical and narrow
- continue making snapshot, bounded recording, and interval capture the stable reference scenarios
- standardize small, slice-specific validation instead of relying only on broad test runs

## Later

- complete the broader `camera_app` to `vision_platform` physical migration where it still adds clarity
- improve wx-shell usability where concrete friction still exists
- harden host-facing payload clarity only when a concrete integration need appears
- prepare the headless kernel after local and host usability are clearly strong enough
- grow API, web-capable, MCP, and C#-handover scope only after the current baseline is stable

## Trigger-Based

- re-run hardware validation when a camera is attached again or a hardware regression appears
- update operator guidance when a startup or recovery step becomes materially easier or harder
- add a new work package only when a concrete residual is observed, not just because the roadmap is broad
- revisit module docs when a module's role changes materially or a compat seam becomes stale

## Implicit Tasks Worth Watching

- compatibility debt cleanup
- doc de-duplication
- queue hygiene
- branch-scope discipline
- status-vs-implementation drift reduction
- test-surface tightening

## Bucket Items Lifted From WorkPackages

- conditional hardware revalidation when a camera is attached again
- the completed control/imaging compatibility cleanup on the current refactor branch
- the later `camera_app` to `vision_platform` physical migration where it still adds clarity
- wx-shell usability follow-ups where concrete friction is still visible
- host-facing payload clarity only when a concrete integration need appears
- headless-kernel preparation only after local and host usability are strong enough
- hardware-attached operator guidance updates when startup or recovery steps materially change
- new work-package creation only when a concrete residual is observed
- module-doc review when a module role changes materially or a compat seam becomes stale

## Entry Points

Status ownership remains in:

- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`

This section only records useful starting points for the listed themes.

### Central References By Theme

- `WP70 / control and imaging compatibility cleanup`
  - see status: `docs/STATUS.md`
  - see queue: `docs/WORKPACKAGES.md`
  - see execution history: `docs/archive/session_workpackages/wp70_control_and_imaging_compatibility_cleanup.md`
- `hardware revalidation and operator guidance`
  - see status: `docs/STATUS.md`
  - see queue: `docs/WORKPACKAGES.md`
  - see execution context: `docs/session_workpackages/wp04_hardware_revalidation_follow_up.md`
- `later camera_app to vision_platform migration`
  - see status: `docs/STATUS.md`
  - see queue: `docs/WORKPACKAGES.md`
  - see branch planning: `docs/branch_backlog.md`
- `wx-shell usability follow-up`
  - see status: `docs/STATUS.md`
  - see queue: `docs/WORKPACKAGES.md`
  - see module state: `apps/local_shell/STATUS.md`
- `host-facing payload and command-surface follow-up`
  - see status: `docs/STATUS.md`
  - see queue: `docs/WORKPACKAGES.md`
  - see contract boundary: `docs/HOST_CONTRACT_BASELINE.md`
- `headless-kernel preparation`
  - see status: `docs/STATUS.md`
  - see queue: `docs/WORKPACKAGES.md`
  - see phase card: `docs/TARGET_MAP.md`

### Common Entry Scripts

These are the most practical launch points when you want to inspect or exercise the current state without inventing new entry points:

- `src/vision_platform/apps/local_shell/__main__.py`
- `src/vision_platform/apps/local_shell/control_cli.py`
- `scripts/launchers/run_camera_cli.py`
- `scripts/launchers/run_command_flow_demo.py`
- `scripts/launchers/run_hardware_preview_demo.py`
- `scripts/launchers/run_opencv_preview_demo.py`
- `scripts/launchers/run_simulated_demo.py`
- `scripts/launchers/run_snapshot_smoke.py`

### Entry Points By Theme

- hardware revalidation and operator guidance:
  - `docs/STATUS.md`
  - `docs/WORKPACKAGES.md`
  - `docs/session_workpackages/wp04_hardware_revalidation_follow_up.md`
  - `docs/PYTHON_BASELINE_RUNBOOK.md`
  - `docs/ENTRYPOINT_AND_LAUNCH_BASELINE.md`
  - `integrations/camera/STATUS.md`
  - `src/vision_platform/apps/local_shell/startup.py`
- compatibility cleanup and later `camera_app` to `vision_platform` migration:
  - `docs/branch_backlog.md`
  - `docs/archive/session_workpackages/wp70_control_and_imaging_compatibility_cleanup.md`
  - `src/camera_app/control/__init__.py`
  - `src/camera_app/imaging/__init__.py`
  - `src/vision_platform/bootstrap.py`
  - `src/vision_platform/control/command_controller.py`
  - `src/vision_platform/imaging/opencv_adapter.py`
  - `src/vision_platform/imaging/opencv_preview.py`
  - `tests/test_command_controller.py`
  - `tests/test_opencv_adapter.py`
  - `tests/test_opencv_preview.py`
- wx-shell usability and local working frontend evolution:
  - `apps/local_shell/README.md`
  - `apps/local_shell/STATUS.md`
  - `src/vision_platform/apps/local_shell/wx_preview_shell.py`
  - `src/vision_platform/apps/local_shell/startup.py`
  - `src/vision_platform/apps/local_shell/control_cli.py`
  - `src/vision_platform/apps/local_shell/live_command_sync.py`
- host-facing payload and command-surface follow-up:
  - `docs/HOST_CONTRACT_BASELINE.md`
  - `docs/COMMANDS.md`
  - `services/api_service/STATUS.md`
  - `src/vision_platform/services/api_service/status_payloads.py`
  - `src/vision_platform/services/api_service/command_payloads.py`
  - `src/vision_platform/control/command_controller.py`
- headless-kernel preparation and stable reference scenarios:
  - `docs/TARGET_MAP.md`
  - `docs/WORKPACKAGES.md`
  - `src/vision_platform/bootstrap.py`
  - `src/vision_platform/services/recording_service`
  - `src/vision_platform/services/stream_service`
  - `tests/test_snapshot_service.py`
  - `tests/test_recording_service.py`
  - `tests/test_interval_capture_service.py`
- governance and doc hygiene:
  - `docs/STATUS.md`
  - `docs/WORKPACKAGES.md`
  - `docs/session_workpackages/README.md`
  - `docs/module_doc_audit.md`
  - `docs/MODULE_INDEX.md`

## Notes

The list is intentionally short and operational. It is meant to keep the next few moves obvious without turning into a second PM system.
