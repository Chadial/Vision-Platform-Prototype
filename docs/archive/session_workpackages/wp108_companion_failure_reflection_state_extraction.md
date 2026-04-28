# WP108 Companion Failure Reflection State Extraction

## Purpose

Move the bounded latest-failure reflection state helper out of the wx shell into one explicit companion service seam.

## Branch

- `refactor/wp108-companion-failure-reflection-state`

## Closure Lane

- headless-kernel preparation after landed `WP107`

## Slice Role

- extraction
- bounded state-ownership cleanup

## Scope

- extract the current `set / clear-for-source / copy` helper behavior for `failure_reflection`
- preserve the current single-latest-failure policy exactly
- keep shell-visible failure messaging and host-visible failure payload semantics unchanged

## Guardrails

- do not turn this into an incident log, event stream, or history model
- keep the current overwrite-and-clear behavior unchanged
- do not widen failure fields or add severity/category policy
- keep this package bounded to helper ownership only

## Policy Preservation

The current failure-reflection policy must remain exactly unchanged:

- one latest failure only
- overwrite-on-newer-failure behavior
- clear-on-success only for the same relevant lane/source
- copy behavior unchanged
- no persistence beyond the current companion state
- no incident / audit / history interpretation

If any ambiguity appears around failure policy, do not decide it inside this package.
Record it as a follow-up question instead.

## Out Of Scope

- no incident history
- no severity or category semantics
- no audit interpretation
- no retry/recovery policy
- no new status fields
- no host protocol changes

## Affected Modules

- `apps/local_shell`
- `services`
- local-shell failure-reflection tests

## Validation

- `.\.venv\Scripts\python.exe -m unittest tests.test_local_shell_live_command_sync tests.test_local_shell_control_cli tests.test_wx_preview_shell`

## Done Criteria

- the wx shell no longer owns the bounded failure-reflection helper logic directly
- current overwrite, clear-on-success-in-same-lane, and copy behavior remain unchanged
- no failure-history or policy widening is introduced

## Recommended Follow-Up

- only after projection-input and failure-state ownership are both narrowed, reassess whether one bounded app-facing companion facade is justified
- after `WP107` through `WP109`, do not derive further companion extraction work from cleanup momentum alone
- any later headless, runtime, host-contract, or LabVIEW-facing slice must be justified by a concrete residual, integration need, test failure, or user-observed workflow friction
- read `WP107` through `WP109` as the final bounded cleanup of the current companion-service extraction lane, not as the start of a broader facade/runtime architecture push
