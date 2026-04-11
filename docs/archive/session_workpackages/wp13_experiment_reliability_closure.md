# Experiment Reliability Closure

## Purpose

This work package defines the first execution-ready Extended MVP closure slice for experiment reliability.

Its purpose is to prove that the existing bounded recording path can survive repeated host-style use and recover cleanly after selected startup or write-side failures without leaving the subsystem in an ambiguous state.

The narrow goal is not broad hardware validation.

It is to harden and verify the first bounded recording recovery slice around:

- bounded recording lifecycle completion
- recovery after one selected recording failure
- safe repeated host-driven recording invocation on the same subsystem path
- stable post-failure status visibility for the next command

## Branch

- intended branch: `feature/experiment-reliability-closure-recording-recovery`
- activation state: current next execution-ready package after the first `Host Control Closure` slice

## Scope

Included:

- verify that bounded recording can be started, completed, and started again cleanly on the same subsystem path
- verify that one selected writer-side failure leaves the service and host-visible status in a reusable state
- harden only the minimal recording/service/controller behavior required to make those reliability expectations reproducible
- keep validation simulator-first and locally executable

Selected slice for this package:

- recording lifecycle restart after successful bounded completion
- recording restart after one selected writer-side failure
- host-visible final status and error-state behavior after those cases, including visible `last_error`

Why this slice:

- it directly supports experiment robustness
- it is locally verifiable without connected hardware
- it builds on the now-hardened host-control path without reopening broad transport work

Excluded:

- broad hardware revalidation runs
- startup-failure recovery as a primary proof point for this slice unless it falls out trivially from the same hardening
- detached recording sessions across multiple processes
- trigger-based recording
- preview/UI work
- file-format broadening or metadata-lane expansion beyond what is required for this reliability slice
- interval-capture reliability unless it falls out trivially from the same service hardening

## Session Goal

Leave the repository with one explicitly verified reliability baseline in which bounded recording can be invoked repeatedly by a host-style caller, and selected failures do not leave the subsystem in a broken or ambiguous reuse state.

The first completed slice should answer a practical experiment question:

- can the Python camera subsystem survive one bounded recording run, one selected failure, and the next bounded recording attempt without requiring a process restart?

For this slice, that selected failure means:

- one writer-side failure during an already active bounded recording path

## Current Context

The repository already has:

- bounded recording stop conditions
- cleanup hardening for selected startup and stop failures
- recording state and error tracking
- host-facing command and status surfaces

The immediate remaining reliability gap is:

- the current baseline documents defensive cleanup and failure handling, but it does not yet explicitly prove the repeated-invocation and post-failure reuse story for the bounded recording path

Primary failure mode frozen for this slice:

- writer-side failure

Reason:

- it is closer to the experiment risk of recording starting successfully and saving breaking during the run
- it proves recovery after the subsystem has already entered an active recording path
- it is more relevant to experiment confidence than a purely early startup rejection for this first slice

## Proposed Narrow Outcome

Preferred outcome for this slice:

- repeated bounded recording runs succeed on the same subsystem path
- the selected writer-side failure leaves the service reusable for the next run
- host-visible status after failure is explicit enough to confirm whether the subsystem is idle, recording, or failed-but-recovered with visible `last_error`
- no process restart is required for the selected simulator-backed scenarios

Recovery for this slice must be true in host-visible terms, not only internal service terms.

The claim to prove is:

- after one bounded successful recording,
- then one selected writer-side failure,
- the subsystem exposes a host-readable non-recording status with visible failure context,
- and the next bounded recording attempt succeeds without process restart

## Learned Constraints

- keep this slice locally testable first; hardware remains a later supporting reliability step
- do not broaden this package into all reliability concerns at once
- preserve the existing thin host adapter path; this is mainly service/control hardening and validation
- use one narrow reproducible failure mode rather than a large matrix

## Open Questions

- does the narrowest useful validation belong at `RecordingService` level, `CommandController` level, or both?

## Current Outcome

Implemented and verified in this slice:

- repeated bounded recording runs now have explicit targeted simulator-backed coverage on the same service path
- a selected writer-side failure now has explicit targeted simulator-backed reuse coverage on the same service path
- host-visible non-recording state plus visible `last_error` after the selected failure are part of the intended proof for this slice
- the selected scenarios did not require additional product-code hardening; the new tests demonstrated that the current bounded recording cleanup and reuse path already satisfies this slice

Follow-up still left for later reliability work:

- controller-level or CLI-level repeated-invocation recovery proofs
- hardware-backed reliability evidence
- startup-failure recovery as a primary proof point
- broader failure matrices beyond the selected writer-side scenario

## Execution Plan

1. Re-read:
   - `docs/STATUS.md`
   - `docs/WORKPACKAGES.md`
   - `docs/archive/session_workpackages/wp12_host_control_closure.md`
   - `docs/archive/session_workpackages/wp04_hardware_revalidation_follow_up.md`
2. Inspect the current recording-service and controller tests for:
   - repeated bounded run coverage
   - post-failure reuse coverage
   - host-visible status/error visibility after failure
3. Keep one narrow primary failure scenario frozen for this slice:
   - writer-side failure
4. Add targeted simulator-backed tests that prove:
   - bounded recording completion
   - clean second invocation
   - selected writer-side failure
   - visible `last_error` plus non-recording status after that failure
   - clean reuse after that failure
5. Apply only the minimal code hardening required if the new tests expose a real recovery gap.
6. Verify that host-visible status remains coherent after the selected scenarios.
7. Update docs once the reliability claim is backed by tests.

## Initial Deliverables

The branch should leave behind at least:

- targeted recording reliability tests for repeated bounded invocation and selected failure recovery
- explicit proof that `last_error` remains visible after the selected writer-side failure while the subsystem is no longer stuck in recording
- minimal service/controller hardening if needed
- updated docs that state exactly which reliability question is now answered

## Validation

Required automated validation:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_recording_service tests.test_command_controller tests.test_bootstrap
```

Recommended focused validation if controller or CLI-visible status behavior changes:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_camera_cli tests.test_recording_service tests.test_command_controller tests.test_bootstrap
```

Manual review points:

- repeated bounded recording leaves the subsystem idle and reusable
- the selected writer-side failure leaves no stuck recording state
- the selected writer-side failure leaves visible `last_error` through the status path
- the next recording attempt succeeds without process restart

## Documentation Updates

Before this work package is considered complete, update:

- `docs/STATUS.md`
- relevant recording or stream module status docs if behavior changes materially
- this file with any newly learned constraints if a follow-up reliability slice is still needed

## Expected Commit Shape

1. `test: add recording recovery reliability coverage`
2. `fix: harden bounded recording recovery path`
3. `docs: record experiment reliability closure baseline`

## Merge Gate

- the slice remains narrow and centered on bounded recording reliability
- the slice keeps writer-side failure as the primary proof point and does not expand into a broad failure matrix
- targeted tests pass locally
- no unrelated host-transport, UI, or data/logging expansion is bundled
- docs clearly state which reliability question is now closed and what still remains open

## Recovery Note

To activate this work package later:

1. Read `AGENTS.md`
2. Read `docs/SESSION_START.md`
3. Read `docs/MODULE_INDEX.md`
4. Read `docs/WORKPACKAGES.md`
5. Read `docs/STATUS.md`
6. Read `docs/archive/session_workpackages/wp12_host_control_closure.md`
7. Read `docs/git_strategy.md`
8. Create the intended branch before any substantive edits
