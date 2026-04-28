# WP100 Companion Session Protocol Baseline

## Purpose

Define one explicit, typed session-protocol baseline above the current bounded local-shell bridge so later headless extraction does not continue to depend on ad-hoc JSON/dict shapes.

## Branch

- `refactor/wp100-companion-session-protocol-baseline`

## Closure Lane

- headless-kernel preparation after `WP99`

## Slice Role

- baseline
- structure and contract clarification

## Scope

- define typed protocol models for:
  - active session metadata
  - queued companion command envelope
  - command-result envelope
  - published status-snapshot envelope
- keep the current file-backed bridge and file locations unchanged
- keep the current wx shell and `local_shell control` behavior unchanged
- allow the service layer to serialize/deserialize the typed envelopes instead of passing raw dicts end to end

## Out Of Scope

- no new transport
- no multi-session redesign
- no command semantics expansion
- no detached recording lifecycle work
- no wx-shell UI changes

## Affected Modules

- `apps/local_shell`
- `services/api_service` only if an existing payload mapper can reuse the new protocol types cleanly
- `services` service-layer session/bridge code
- `libraries/common_models` only if the typed protocol models clearly belong there; otherwise keep them local to the service seam

## Session Goal

Replace the remaining ad-hoc live-session JSON shapes with one explicit typed protocol baseline while preserving the current bounded companion behavior.

## Execution Plan

1. Identify the currently persisted session, command, result, and status JSON shapes.
2. Define narrow typed protocol models for those shapes.
3. Update the local-shell session service to read/write those typed envelopes.
4. Keep app-level compatibility imports and runtime behavior stable.
5. Add focused tests around round-trip serialization and compatibility.

## Validation

- `.\.venv\Scripts\python.exe -m unittest tests.test_local_shell_live_command_sync tests.test_local_shell_control_cli tests.test_wx_preview_shell`

## Done Criteria

- the file-backed bridge no longer depends on raw free-form dict payload assembly internally
- protocol ownership is explicit and local to one seam
- current control CLI and wx-shell behavior remain unchanged
- focused tests cover typed round-trip behavior

## Recommended Follow-Up

- `WP101 Companion Command Execution Service Extraction`

