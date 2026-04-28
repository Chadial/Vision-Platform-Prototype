# WP105 Companion Status Publication Service Extraction

## Purpose

Move the file-backed live-status publication write path out of the wx shell into one bounded service seam above the landed status-projection baseline.

## Branch

- `refactor/wp105-companion-status-publication-service`

## Closure Lane

- headless-kernel preparation after landed `WP102`

## Slice Role

- extraction
- consumer-facing ownership cleanup

## Scope

- extract the `live session present -> write current status snapshot` path from the wx shell
- reuse the landed explicit projection input and projection service
- keep current published status content, cadence, and active-session update behavior unchanged

## Guardrails

- treat this package as ownership extraction only
- do not use it to add status throttling, eventing, or new status fields
- keep publication timing owned by the shell caller; move only the write-path ownership
- keep the file-backed single-session baseline unchanged

## Out Of Scope

- no new status semantics
- no background publisher thread
- no transport/runtime widening
- no shell timer redesign

## Affected Modules

- `apps/local_shell`
- `services`
- local-shell status publication tests

## Validation

- `.\.venv\Scripts\python.exe -m unittest tests.test_local_shell_live_command_sync tests.test_local_shell_control_cli tests.test_wx_preview_shell`

## Done Criteria

- the wx shell no longer writes live-status snapshot files directly
- the new service seam takes explicit live-session and projection-input dependencies
- current published snapshot payloads remain behaviorally unchanged

## Recommended Follow-Up

- derive one minimal runtime coordinator seam only after command polling and status publication ownership are both extracted
