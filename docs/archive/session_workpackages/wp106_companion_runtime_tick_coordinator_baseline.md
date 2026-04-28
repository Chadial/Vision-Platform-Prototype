# WP106 Companion Runtime Tick Coordinator Baseline

## Purpose

Introduce one minimal companion-runtime coordinator seam that orchestrates the already-bounded command polling and status publication steps for an open shell tick.

## Branch

- `refactor/wp106-companion-runtime-tick-coordinator`

## Closure Lane

- headless-kernel preparation after landed `WP104` and `WP105`

## Slice Role

- baseline
- orchestration ownership cleanup

## Scope

- define one small coordinator seam that the wx shell can call from its existing tick/refresh path
- compose the extracted command-polling and status-publication seams without changing the current single-session file-backed baseline
- keep shell-local timing and UI refresh ownership intact while narrowing companion-runtime orchestration ownership

## Guardrails

- keep this package minimal and compositional
- do not turn it into a generic daemon, transport host, or lifecycle framework
- do not widen command/status semantics
- do not move UI refresh or preview ownership out of the shell

## Out Of Scope

- no multi-session runtime model
- no background service process
- no transport abstraction
- no host protocol redesign

## Affected Modules

- `apps/local_shell`
- `services`
- local-shell live-sync tests

## Validation

- `.\.venv\Scripts\python.exe -m unittest tests.test_local_shell_live_command_sync tests.test_local_shell_control_cli tests.test_wx_preview_shell`

## Done Criteria

- the wx shell delegates bounded companion-runtime orchestration to one service seam
- polling and publication composition is explicit and still file-backed
- the package does not introduce runtime or transport widening

## Recommended Follow-Up

- only after this seam lands, decide whether any further headless-preparation extraction is still justified before broader architecture work
