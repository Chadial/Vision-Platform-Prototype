# WP102 Companion Status Projection Service Extraction

## Purpose

Move published companion-status derivation and projection out of the wx shell into one reusable service seam.

## Branch

- `refactor/wp102-companion-status-projection-service`

## Closure Lane

- headless-kernel preparation after `WP101`

## Slice Role

- extraction
- consumer-facing ownership cleanup

## Scope

- extract setup, snapshot, recording, and failure reflection projection from the wx shell
- extract published status-snapshot assembly inputs that are currently spread across shell-local state
- keep current published status content and file-backed publication timing unchanged

## Guardrails

- treat this package as ownership extraction only
- do not use it to redesign status semantics, rename fields, or add “small” status improvements opportunistically
- keep setup, snapshot, recording, and failure reflection meaning stable while moving their assembly into a service seam
- if a status improvement is genuinely needed, queue it as a separate follow-up after the ownership extraction is complete

## Out Of Scope

- no new status fields by default
- no event bus or subscription model
- no UI rendering changes
- no transport/runtime widening

## Affected Modules

- `apps/local_shell`
- `services`
- local-shell status publication tests

## Validation

- `.\.venv\Scripts\python.exe -m unittest tests.test_local_shell_live_command_sync tests.test_local_shell_control_cli tests.test_wx_preview_shell`

## Done Criteria

- published companion-status projection no longer depends on a wx-shell-local assembler method
- shell-local state needed for projection is passed explicitly into the new service seam
- existing status/readback behavior remains unchanged
- the package does not introduce semantic status drift while moving ownership

## Recommended Follow-Up

- derive the next headless-kernel seam only after `WP100` through `WP102` are validated together

