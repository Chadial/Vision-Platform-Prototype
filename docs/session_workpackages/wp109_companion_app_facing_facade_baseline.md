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

Each facade method should only:

- delegate to already extracted services
- compose existing service outputs
- reduce wx-shell coupling to low-level helper seams

## Guardrails

- do not turn this facade into a transport host, daemon, or generic subsystem runtime
- do not add a broader command/session abstraction here
- keep the facade as an app-facing composition seam, not a new product architecture layer
- if the facade starts needing new semantics, stop and split a new package instead
- do not use the facade as a dumping ground for unrelated shell helpers
- do not use the facade as a dumping ground for camera domain logic
- do not use the facade as a dumping ground for command-controller logic
- do not use the facade as a dumping ground for status model changes
- do not use the facade as a dumping ground for future transport hooks
- do not use the facade as a dumping ground for LabVIEW-specific mapping
- do not use the facade as a dumping ground for headless runtime lifecycle concepts

The facade must not own:

- command semantics
- status semantics
- failure policy
- session protocol decisions
- transport/runtime lifecycle decisions
- domain workflow decisions

## Out Of Scope

- no generic transport layer
- no multi-session manager
- no host protocol redesign
- no new companion semantics
- no LabVIEW-specific mapping
- no lifecycle concepts beyond bounded service composition

## Affected Modules

- `apps/local_shell`
- `services`
- local-shell companion smoke tests

## Validation

- `.\.venv\Scripts\python.exe -m unittest tests.test_local_shell_live_command_sync tests.test_local_shell_control_cli tests.test_wx_preview_shell`

## Done Criteria

- the wx shell can depend on one bounded app-facing companion composition seam instead of several low-level companion helpers
- the wx shell depends on fewer low-level companion helper objects than before
- each facade method maps clearly to one existing companion use case
- facade methods contain no new business logic beyond service composition
- no existing result, status, failure, or protocol payload changes
- tests verify preserved behavior through the new seam, not new semantics
- the current file-backed baseline remains operationally unchanged
- the package does not widen runtime, transport, or host semantics

## Recommended Follow-Up

- after this facade baseline, derive the next headless or contract slice only from concrete residuals, not from companion cleanup momentum
- after `WP107` through `WP109`, do not derive further companion extraction work from cleanup momentum alone
- any later headless, runtime, host-contract, or LabVIEW-facing slice must be justified by a concrete residual, integration need, test failure, or user-observed workflow friction
- read `WP107` through `WP109` as the final bounded cleanup of the current companion-service extraction lane, not as the start of a broader facade/runtime architecture push
