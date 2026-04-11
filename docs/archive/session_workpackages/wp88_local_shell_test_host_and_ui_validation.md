# WP88 Local Shell Test-Host And UI Validation

## Purpose

Validate the current wx shell against a separate test-host process and confirm that the visible UI shell reflects host-driven actions correctly on the current tested hardware path.

## Closure lane

- Usable Camera Subsystem / Pre-Product Baseline

## Slice role

- bounded host-plus-UI validation slice

## Scope level

- one narrow test-host smoke pass plus one narrow UI-shell observation pass

## Branch

- intended branch: `test/wp88-local-shell-test-host-ui-validation`
- activation state: completed

## Scope

Included:

- start the current wx shell on the tested hardware path
- send bounded commands from a separate host-side process through `vision_platform.apps.local_shell control ...`
- confirm the shell visibly reflects host-driven status, snapshot, and recording changes
- confirm the shell remains usable while the host process is issuing commands
- capture any UI-shell-specific friction or reflection mismatch that appears during the smoke

Excluded:

- new transport framework
- broad UI redesign
- new command semantics
- broader host automation or continuous integration changes
- extra hardware matrix expansion

## Session Goal

Prove that the current test-host path and the visible wx shell still agree on the same state model when exercised together on the tested camera path.

## Execution Plan

1. start the wx shell on the tested hardware path
2. issue `control status` from a separate process and compare the reflected state with the shell header/status area
3. issue one snapshot command and confirm the shell shows the expected save/result reflection
4. issue one bounded recording command and confirm the shell shows start, progress, and stop reflection
5. note any mismatch between host results and UI-shell presentation

## Validation

- the shell starts on the tested hardware path
- the host process can issue `control` commands while the shell remains open
- the UI shell visibly reflects the host-driven actions without restart
- snapshot and bounded recording remain understandable from both the host and shell sides

## Documentation Updates

- update `docs/STATUS.md` if the tested host-plus-shell state changes
- update `docs/WORKPACKAGES.md` if this slice becomes current-next or completes

## Expected Commit Shape

- docs-only slice unless validation exposes a concrete code gap

## Merge Gate

- this slice is complete after the host-plus-UI smoke has been executed and documented

## Observed Result

- the wx shell started on the tested hardware path
- the separate host process successfully issued `status`, `set-save-directory`, `snapshot`, `apply-configuration`, and `start-recording` commands against the open shell
- the shell published reflected status, snapshot, and recording state without restart
- one intentionally invalid configuration request surfaced the expected hardware increment error, and a subsequent valid configuration request reflected `exp=9004.2us gain=2.6` in the shell status
- the recording completed with `max_frames_reached` and produced three output frames plus traceability/log artifacts in `captures/wx_shell_test_host_ui`

## Recovery Note

- if the shell or control path mismatch is larger than expected, split the issue into the smallest host-result or UI-reflection follow-up instead of widening this slice
