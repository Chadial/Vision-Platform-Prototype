# Host Control Closure

## Purpose

This work package defines the first execution-ready Extended MVP closure slice for host control.

Its purpose is to make the existing Python command/controller baseline practically usable from an external host-process perspective without opening a new transport stack.

The narrow goal is to turn the current camera CLI from a developer-oriented JSON summary path into a clearer host-callable adapter with:

- explicit machine-readable command success/failure semantics
- one stable command-response envelope for selected commands
- one stable status-polling payload for runtime state inspection

This package should prove the host-control direction in the AMB context without trying to solve all later automation or transport concerns at once.

## Branch

- intended branch: `feature/host-control-closure-cli-envelope`
- activation state: current next detailed package for the `Host Control Closure` lane

## Scope

Included:

- define one external-process-friendly JSON command envelope for a narrow selected command set
- tighten command success/failure semantics so a host process can consume stdout plus process exit status predictably
- keep `status` as the explicit polling-oriented command for runtime-readable subsystem state
- make selected command results and polled status payloads clearer and more stable for AMB host consumption
- reuse the existing command-controller path and any already prepared adapter DTOs where that keeps the CLI thin

Selected command slice for this package:

- `status`
- `snapshot`
- `recording`

Why this slice:

- `status` proves the polling path
- `snapshot` proves a short-running save command with artifact confirmation
- `recording` proves a long-running bounded command that ends with a host-readable final state

Recording semantics for this first slice:

- `recording` is explicitly treated as a bounded recording command
- it starts and completes within the invoked process
- it returns one final structured result after bounded completion

Deferred for later slices:

- detached recording sessions spanning multiple host invocations
- background recording lifecycle ownership across calls
- richer stop/resume orchestration beyond the current bounded path

Excluded:

- new GUI or OpenCV operator work
- broad CLI capability expansion such as ROI or analysis commands
- interval-capture follow-up unless it falls out trivially from the shared result/status shape
- server, IPC, HTTP, WebSocket, SignalR, broker, or browser transport work
- broad API framework work
- packaging or installer work
- C# handover or broader contract families beyond this narrow host-process slice

## Session Goal

Leave the repository with one immediately usable host-invocation baseline in which the selected CLI commands return a stable structured envelope that an external AMB-controlled process can consume reliably, while `status` acts as the explicit polling path for readiness, recording, and failure state.

The first completed slice should make it unnecessary for a host caller to infer success from ad-hoc stdout shape or Python exceptions alone.

## Current Context

The repository already has:

- a typed host-neutral `CommandController`
- typed request and command-result models
- a typed `SubsystemStatus`
- a thin `vision_platform.apps.camera_cli` adapter
- a first transport-neutral status DTO family under `services/api_service`

The immediate gap is:

- the CLI still exposes one post-command summary object that is useful for humans and tests, but is not yet a deliberately normalized host-facing command envelope
- failure semantics and command-specific result payload ownership are still conservative from an external-process perspective

## Proposed Narrow Outcome

Preferred output direction for the selected commands:

- top-level envelope fields such as:
  - `success`
  - `command`
  - `source`
  - `result`
  - `status`
  - `error`

Where relevant:

- `result` should carry command-specific confirmation such as saved snapshot path or bounded recording summary
- `status` should remain the runtime-readable subsystem state payload
- `error` should be machine-readable enough for a host process to log or branch on without scraping human prose

Exact field names can still be adjusted during implementation, but the envelope must stay stable across the selected command slice once chosen.

Preferred minimal error shape for this first slice:

- `code`
- `message`
- `details`

Meaning:

- `code`: short stable machine-readable identifier
- `message`: short human-readable explanation
- `details`: optional extra structured or textual context

Avoid in this slice:

- raw Python exception dumping as the only host-facing error form
- an overdesigned full error taxonomy

Applied-settings confirmation expectation for this first slice:

- host-facing results or their accompanying status should expose enough confirmed context for experiment traceability
- at minimum, where relevant:
  - active camera id
  - pixel format
  - exposure value
  - save target or saved path
  - recording bounds for bounded recording
- this slice should not try to mirror every possible camera feature

## Learned Constraints

- the CLI must remain a thin adapter above the shared command/application layer
- host control should use command-response plus explicit status polling, not a mandatory push channel
- screen and preview concerns must stay outside this package
- the package should prefer reusing existing typed status/result structures over inventing a second business-logic path
- simulator-first validation is the default while the camera hardware is not attached locally

## Open Questions

- should the CLI envelope serialize `SubsystemStatus` directly for this slice, or should it route through the already prepared API-service status DTO mapper?
- how much error-code structure is worth adding in this first slice before a broader adapter lane is opened?
- should bounded `recording` expose only final-state result data in this package, or also a more explicit completion summary field derived from the final status?

## Execution Plan

1. Re-read:
   - `docs/STATUS.md`
   - `docs/WORKPACKAGES.md`
   - `apps/camera_cli/README.md`
   - `apps/camera_cli/STATUS.md`
   - `services/api_service/README.md`
   - `services/api_service/STATUS.md`
2. Inspect the current CLI output path under `src/vision_platform/apps/camera_cli` and identify where command summaries, failures, and exit codes are currently shaped.
3. Freeze one narrow selected command slice for this package:
   - `status`
   - `snapshot`
   - `recording`
4. Decide whether the status portion of the envelope should:
   - serialize `SubsystemStatus` directly for now
   - or reuse the existing API-service DTO mapping as the adapter-facing status payload
5. Define one stable envelope contract for the selected commands with explicit success/failure semantics and command/result/status ownership.
6. Implement the envelope and failure-path handling without moving business logic out of the controller/service layer.
7. Ensure process-facing behavior is explicit:
   - successful commands return exit code `0`
   - command failures return a non-zero exit code
   - stdout/stderr behavior remains predictable enough for host invocation
   - bounded `recording` remains an in-process start-to-completion command for this slice
8. Extend or update tests so the selected command slice is locked to the new machine-readable contract.
9. Update the touched module docs and repository status notes once the host-facing adapter shape is real.

## Initial Deliverables

The branch should leave behind at least:

- one stable host-oriented JSON envelope for `status`, `snapshot`, and `recording`
- explicit command success/failure semantics suitable for external process invocation
- one clear status-polling payload path through the `status` command
- targeted tests that protect the selected envelope and error behavior
- updated docs that state what this first Host Control Closure slice proves and what remains out of scope

## Validation

Use targeted simulator-backed validation first.

Required automated validation:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_camera_cli tests.test_command_controller tests.test_command_results tests.test_api_service tests.test_bootstrap
```

Recommended manual smoke checks after implementation:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli status
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli snapshot --base-directory .\tmp_host_control --file-stem host_snapshot
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli recording --base-directory .\tmp_host_control --file-stem host_recording --frame-limit 2
```

Manual review points:

- stdout remains machine-readable JSON for successful commands
- failures return a non-zero process exit code
- `status` output is suitable as the host polling path
- `snapshot` confirms the saved artifact path
- `recording` confirms a host-readable final non-recording state after bounded completion

## Documentation Updates

Before this work package is considered complete, update:

- `apps/camera_cli/STATUS.md`
- `apps/camera_cli/README.md` if the host-facing output contract needs documenting there
- `services/api_service/STATUS.md` if the status DTO mapper becomes part of the selected adapter path
- `docs/STATUS.md`
- `docs/WORKPACKAGES.md` only if activation/order/reference details change after implementation

## Expected Commit Shape

1. `feat: add host-oriented cli command envelope baseline`
2. `test: lock camera cli host-output contract`
3. `docs: record host control closure baseline`

## Merge Gate

- the package remains a thin adapter-level hardening slice above the existing controller/service path
- the selected command slice is narrow and coherent
- success/failure semantics are explicit enough for external process use
- targeted tests pass locally
- no UI, transport-stack, or unrelated command-expansion work is bundled
- docs clearly state what host-control gap is now closed and what remains for later closure slices

## Recovery Note

To activate this work package later:

1. Read `AGENTS.md`
2. Read `docs/SESSION_START.md`
3. Read `docs/MODULE_INDEX.md`
4. Read `docs/WORKPACKAGES.md`
5. Read `docs/STATUS.md`
6. Read `apps/camera_cli/README.md`
7. Read `apps/camera_cli/STATUS.md`
8. Read `services/api_service/README.md`
9. Read `services/api_service/STATUS.md`
10. Read `docs/git_strategy.md`
11. Create the intended branch before any substantive edits
