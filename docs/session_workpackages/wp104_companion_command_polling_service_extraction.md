# WP104 Companion Command Polling Service Extraction

## Purpose

Move the file-backed pending-command polling and result-write loop out of the wx shell into one bounded service seam.

## Branch

- `refactor/wp104-companion-command-polling-service`

## Closure Lane

- headless-kernel preparation after landed `WP100` through `WP102`

## Slice Role

- extraction
- consumer-facing ownership cleanup

## Scope

- extract the `read pending commands -> execute injected callback -> write success/failure result` loop from the wx shell
- keep the current file-backed single-session baseline unchanged
- keep current command-result payload semantics and failure-placeholder behavior unchanged

## Guardrails

- treat this package as ownership extraction only
- do not add commands, retries, queue policies, or transport concepts
- do not redesign result payload semantics while moving the loop
- keep the command executor injected from the shell-side caller rather than hiding new camera logic inside the polling seam

## Out Of Scope

- no new command types
- no retry or backoff policy
- no subscription/event model
- no multi-session runtime redesign

## Affected Modules

- `apps/local_shell`
- `services`
- local-shell live-sync tests

## Validation

- `.\.venv\Scripts\python.exe -m unittest tests.test_local_shell_live_command_sync tests.test_local_shell_control_cli tests.test_wx_preview_shell`

## Done Criteria

- the wx shell no longer owns the per-command polling/result-write loop
- the new service seam takes explicit dependencies for session access, command execution, and failure-result shaping
- current command-result files remain behaviorally unchanged

## Recommended Follow-Up

- extract the bounded status-publication write path next, then reassess one small runtime coordinator seam
