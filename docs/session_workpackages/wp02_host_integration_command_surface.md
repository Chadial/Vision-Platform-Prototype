# Host Integration Command Surface

## Purpose

This work package defines the first focused follow-up after the initial camera CLI baseline.

Its purpose is to harden the shared host-neutral command surface so later C# embedding, desktop integration, and external adapters can reuse one clearer control contract instead of reverse-engineering CLI-oriented behavior.

## Branch

- intended branch: `feature/host-integration-command-surface`
- predecessor branch: `feature/camera-cli`
- activation state: ready after the CLI baseline is documented as intentionally narrow and stable

## Scope

Included:

- tighten the shared `CommandController` surface as the primary host-facing application layer
- clarify which request, result, and status shapes are intended for host use versus local CLI summary output
- identify one small implementation slice that improves host-visible command clarity without creating a transport layer
- keep changes simulator-verifiable
- document how CLI and future API work should consume the same command/application path

Excluded:

- new API/feed transport work
- OpenCV preview or viewport work
- broad ROI or analysis feature expansion
- large refactors outside the control/application boundary
- hardware-only validation requirements that cannot be rerun locally

## Session Goal

Leave the repository with one clearer host-integration-ready command slice that is:

- explicit about its request and status contracts
- independent from CLI presentation choices
- covered by targeted tests
- documented as the preferred control path for later adapters

## Status

- current state: implementation slices completed; package ready for close-out or archival once PM wants it moved
- contract baseline: typed command results now exist for save-directory, apply-configuration, snapshot, recording start/stop, and interval-capture start/stop
- status baseline: `SubsystemStatus` now exposes explicit save-directory-configuration and interval-capture-availability flags so hosts do not need to infer those facts indirectly from readiness booleans alone
- outcome baseline: stop-command results now preserve the stop request reason so host callers do not lose that control intent at the command boundary

## Execution Readiness Assessment

- executable for a fresh agent: yes, after narrowing the package into ordered sub-packages
- missing before refinement: the original file named the general theme, but it did not give a fresh agent a clear first slice, completion boundary, or explicit dependency order between result typing, status shaping, and adapter alignment
- refinement outcome: the package now carries a small ordered sub-package ladder with local validation and exit criteria so the next slice can be selected directly without reopening broad architecture planning

## Sub-Packages

### SP1. Apply-Configuration Result Typing

- goal: remove the remaining `None` return from the primary configuration command so host callers get an explicit outcome model
- scope: add a typed `ApplyConfigurationCommandResult`, return it from `CommandController.apply_configuration(...)`, and cover the behavior in controller/bootstrap tests
- non-scope: transport envelopes, richer configuration diffing, hardware-specific confirmation semantics, or CLI-only payload changes
- validation: `.\.venv\Scripts\python.exe -m unittest tests.test_command_controller tests.test_bootstrap`
- dependencies: existing `ApplyConfigurationRequest` / `CameraConfiguration` mapping and current controller validation path
- exit criterion: hosts can call `apply_configuration(...)` and receive a typed result containing the applied normalized configuration without inspecting side effects
- status: completed in this session

### SP2. Consolidated Host Status Tightening

- goal: sharpen `SubsystemStatus` so host consumers can tell more directly which command path is currently actionable and why
- scope: one small improvement to the shared status/readiness contract in `CommandController.get_status()` and its tests
- non-scope: transport/API DTOs, CLI presentation changes beyond adapter alignment, or broad service refactors
- validation: `.\.venv\Scripts\python.exe -m unittest tests.test_command_controller tests.test_bootstrap` and `tests.test_camera_cli` if CLI summaries change indirectly
- dependencies: SP1 complete; current typed command result baseline stable
- exit criterion: one concrete host-facing readiness ambiguity is removed and the status contract is clearer than before without adding transport concerns
- status: completed in this session

### SP3. Command Outcome Consistency For Host Callers

- goal: align one remaining controller outcome or failure edge so hosts do not have to infer behavior from mixed service-native exceptions or implicit state
- scope: one controller-local outcome consistency slice plus targeted tests
- non-scope: global exception framework, HTTP/API error mapping, or broad cross-module validation redesign
- validation: `.\.venv\Scripts\python.exe -m unittest tests.test_command_controller`
- dependencies: SP2 completed so this is now the next preferred implementation slice
- exit criterion: the selected controller path exposes a clearer and more uniform host-facing behavior than the current baseline
- status: completed in this session

### SP4. Adapter Alignment And Host-Path Documentation

- goal: confirm that CLI and later API preparation are documented as consumers of the same host-neutral command surface
- scope: update the active work package, affected status docs, and narrow CLI usage notes if a prior sub-package changed consumption details
- non-scope: new CLI features, API service implementation, or broader PM reprioritization
- validation: doc consistency check plus `tests.test_camera_cli` only if adapter behavior changed
- dependencies: complete the immediately preceding command-surface slice first
- exit criterion: the next agent can see both the implemented contract state and the next bounded follow-up directly from docs
- status: completed in this session through the current WP and status-doc updates

## Selected First Sub-Package

- chosen slice: `SP1. Apply-Configuration Result Typing`
- selection reason: it was the smallest remaining host-facing gap inside the existing command surface because `apply_configuration(...)` still returned `None` while the other primary control commands already exposed typed command results
- local verifiability: controller and bootstrap tests cover the full slice without needing hardware or transport work

## Open Questions

- should SP2 focus on adding more explicit readiness reasons, or is one additional status field enough for the next bounded slice?
- which controller path still has the highest host-facing ambiguity after configuration result typing: consolidated status semantics or failure/outcome consistency?
- how long should host-visible error normalization stay out of scope before API preparation begins?

Resolved in this session:

- SP2 was kept intentionally narrow: explicit availability/configuration signals were added instead of introducing a broader readiness-reason taxonomy too early
- SP3 was also kept narrow: stop request intent is now preserved in typed stop-command results instead of being silently dropped at the controller boundary

## Learned Constraints

- CLI must remain a consumer of the shared control path, not a second business-logic path
- no transport or API envelope should be introduced prematurely
- simulator-verifiable slices are preferred over hardware-dependent contract work
- the safest next slices are controller-local contract clarifications that do not force changes into preview/UI modules or hardware-specific logic
- narrow host-facing status flags are a good fit when they remove multi-field inference without committing the project to a full error-envelope design
- small outcome enrichments on typed command results are a better fit than broad exception-framework work at the current repository phase

## Candidate Slice

- completed slice this session:
- `CommandController.apply_configuration(...)` now returns a typed `ApplyConfigurationCommandResult`
- the result keeps the normalized applied configuration explicit at the host-facing control layer instead of returning `None`
- `CommandController.set_save_directory(...)` now returns a typed `SaveDirectoryCommandResult`
- the result makes the selected directory versus an explicit clear operation visible without requiring hosts to infer state changes indirectly
- the older `SetSaveDirectoryResult` name remains available as a compatibility alias while the command-surface naming is normalized
- the CLI continues to consume the same shared controller path and now uses that typed result instead of re-resolving the path on its own
- `CommandController.save_snapshot(...)` now also returns a typed `SnapshotCommandResult`
- the result keeps the saved-path outcome explicit at the host-facing control layer instead of leaking a raw service return value upward
- the older `SaveSnapshotResult` name remains available as a compatibility alias while the command-surface naming is normalized
- `CommandController.start_recording(...)` and `stop_recording(...)` now also return a typed `RecordingCommandResult`
- the result keeps recording control outcomes explicit for host callers while reusing the existing `RecordingStatus` payload as the nested status contract
- `CommandController.start_interval_capture(...)` and `stop_interval_capture(...)` now also return a typed `IntervalCaptureCommandResult`
- the result keeps interval-capture control outcomes explicit for host callers while reusing the existing `IntervalCaptureStatus` payload as the nested status contract

Preferred next slice:

- no additional slice is selected inside this work package; the currently defined sub-packages are complete and any follow-up should be derived from the central queue rather than extending this file ad hoc

Completed status-tightening slice this session:

- `SubsystemStatus` now exposes `is_save_directory_configured` so hosts can distinguish "not actionable because no save path is configured" from other readiness failures without comparing `default_save_directory` and command booleans manually
- `SubsystemStatus` now also exposes `has_interval_capture_service` so hosts can distinguish "interval capture unavailable in this subsystem wiring" from "interval capture currently idle"
- targeted controller tests and CLI-facing serialization coverage passed locally after the contract change

Completed outcome-consistency slice this session:

- `RecordingCommandResult` now preserves `stop_reason` when `CommandController.stop_recording(...)` is called
- `IntervalCaptureCommandResult` now also preserves `stop_reason` when `CommandController.stop_interval_capture(...)` is called
- the default stop path still reports `external_request` for recording, while interval-capture keeps the optional request reason shape
- targeted controller tests passed locally after the contract change

## Execution Plan

1. Keep `src/vision_platform/control/command_controller.py` and `tests/test_command_controller.py` as the primary execution surface.
2. Select exactly one pending sub-package from this file.
3. Implement the change in the shared control/application layer, not in the CLI adapter.
4. Run the narrowest relevant local validation for that sub-package.
5. Update this work-package file with status, learned constraints, and the next bounded slice.
6. Update `docs/STATUS.md` only if the implemented contract surface changed in reality.

## Close-Out Note

- the refined sub-packages defined in this file are complete
- this work package should not be expanded further inside the session-workpackage layer without a new central selection signal
- the next implementation package should now come from `docs/WORKPACKAGES.md`

## Validation

Minimum:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_command_controller tests.test_bootstrap
```

If CLI-visible behavior changes indirectly:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_command_controller tests.test_bootstrap tests.test_camera_cli
```

## Documentation Updates

Before this work package is considered complete, update:

- `docs/STATUS.md`
- any directly affected module `STATUS.md` / `ROADMAP.md`
- only update `docs/NEXT_SESSION_ORDER.md` or `services/api_service/...` if a later slice materially changes their dependency notes

## Expected Commit Shape

1. `feat: harden host command surface baseline`
2. `test: cover host command surface contract`
3. `docs: update host integration workpackage status`

## Merge Gate

- the shared control/application layer is clearer for host use than before
- CLI remains an adapter rather than a second business-logic path
- no API transport layer is introduced prematurely
- touched tests pass locally
- docs clearly explain the next follow-up step

## Recovery Note

To resume this work:

1. Read `AGENTS.md`
2. Read `docs/SESSION_START.md`
3. Read `docs/MODULE_INDEX.md`
4. Read `docs/STATUS.md`
5. Read this file
6. Inspect `src/vision_platform/control/command_controller.py`
7. Inspect `tests/test_command_controller.py`
8. Pick the first pending sub-package whose validation can run locally without expanding scope
