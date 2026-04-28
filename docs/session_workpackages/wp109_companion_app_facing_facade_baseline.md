# WP109 Companion App-Facing Facade Baseline

## Purpose

Introduce one bounded app-facing companion facade that composes the already extracted companion services for the wx shell without widening the current file-backed baseline.

## Branch

- `refactor/wp109-companion-app-facing-facade`

## Closure Lane

- headless-kernel preparation after landed `WP107` and `WP108`

## Slice Role

- baseline
- app/service boundary cleanup

## Scope

- define one small facade that the wx shell can call for the current companion command/result/status/runtime helpers
- compose only the already extracted bounded services
- keep the current file-backed single-session baseline and host-visible semantics unchanged

## Guardrails

- do not turn this facade into a transport host, daemon, or generic subsystem runtime
- do not add a broader command/session abstraction here
- keep the facade as an app-facing composition seam, not a new product architecture layer
- if the facade starts needing new semantics, stop and split a new package instead

## Out Of Scope

- no generic transport layer
- no multi-session manager
- no host protocol redesign
- no new companion semantics

## Affected Modules

- `apps/local_shell`
- `services`
- local-shell companion smoke tests

## Validation

- `.\.venv\Scripts\python.exe -m unittest tests.test_local_shell_live_command_sync tests.test_local_shell_control_cli tests.test_wx_preview_shell`

## Done Criteria

- the wx shell can depend on one bounded app-facing companion composition seam instead of several low-level companion helpers
- the current file-backed baseline remains operationally unchanged
- the package does not widen runtime, transport, or host semantics

## Recommended Follow-Up

- after this facade baseline, derive the next headless or contract slice only from concrete residuals, not from companion cleanup momentum
