# WP101 Companion Command Execution Service Extraction

## Purpose

Move the bounded external companion-command execution path out of the wx shell into one service seam above the shared controller.

## Branch

- `refactor/wp101-companion-command-execution-service`

## Closure Lane

- headless-kernel preparation after `WP100`

## Slice Role

- extraction
- producer-facing ownership cleanup

## Scope

- extract the current bounded command execution for:
  - `set_save_directory`
  - `apply_configuration`
  - `save_snapshot`
  - `start_recording`
  - `stop_recording`
- keep the command set unchanged
- keep the current file-backed session bridge unchanged
- keep the wx shell responsible only for invoking the service and reflecting the returned result

## Out Of Scope

- no new commands
- no transport/runtime expansion
- no status-projection rewrite
- no detached lifecycle semantics

## Affected Modules

- `apps/local_shell`
- `services`
- command-result tests for local-shell companion control

## Validation

- `.\.venv\Scripts\python.exe -m unittest tests.test_local_shell_live_command_sync tests.test_local_shell_control_cli tests.test_wx_preview_shell`

## Done Criteria

- the wx shell no longer owns the concrete external companion-command execution logic
- the extracted service consumes the typed protocol introduced by `WP100`
- current command behavior and result semantics remain unchanged

## Recommended Follow-Up

- `WP102 Companion Status Projection Service Extraction`

