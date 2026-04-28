# WP99 Live Sync Service Extraction

## Purpose

Move the file-backed local-shell live-sync/session mechanics out of the wx app package into a service-layer seam while preserving the current bounded behavior and compatibility imports.

## Branch

- `refactor/wp99-live-sync-service-extraction`

## Closure Lane

- Headless-preparation follow-up after `WP86` and `WP98`

## Slice Role

- structural extraction
- compatibility-preserving ownership cleanup

## Scope Level

- current bounded local-shell live-sync/session bridge only

## Producer / Consumer / Structure Impact

- producer-facing: no behavioral change to the file-backed command/status/result flow
- consumer-facing: the wx shell and `local_shell control` CLI keep their existing interface and imports
- structure impact: the service layer now owns the file-backed session mechanics, while the app package keeps a thin compatibility wrapper

## What This Package Does Not Close

- no new transport
- no multi-session redesign
- no detached lifecycle semantics
- no preview/command protocol expansion
- no renderer or bitmap-presentation refactor

## Which Policy Questions Remain Open

- when the later headless kernel starts, whether this file-backed path should be replaced by a host-neutral runtime/session seam
- whether one broader companion/host session abstraction is justified beyond the current local-shell path

## Scope

- add one service-layer module for the current file-backed session bridge
- re-point local-shell runtime code to that service-layer module
- keep `vision_platform.apps.local_shell.live_command_sync` as a compatibility import surface
- update focused tests to cover both the new service ownership and the compatibility wrapper
- update central and local docs for the new ownership boundary

## Session Goal

Land the smallest headless-preparation cleanup after `WP98`: the wx shell should no longer own the file-backed live-sync/session mechanics directly, but the current shell and control CLI should behave exactly as before.

## Execution Plan

1. Create a service-layer home for the current `LocalShellLiveSync*` types and helpers.
2. Turn the app-level module into a thin compatibility wrapper.
3. Update the wx shell, startup path, and control CLI to consume the service-layer seam directly.
4. Add focused test coverage for the new ownership boundary.
5. Record the new structure in central and module docs.

## Validation

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_local_shell_live_command_sync tests.test_local_shell_control_cli
```

## Documentation Updates

- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- `apps/local_shell/README.md`
- `apps/local_shell/STATUS.md`

## Expected Commit Shape

- `refactor:` move bounded local-shell session bridge ownership into `vision_platform.services`
- `test:` cover the service seam plus compatibility import
- `docs:` record `WP99` and the updated local-shell ownership boundary

## Merge Gate

- focused live-sync and control-CLI tests pass
- no behavior drift in the bounded `local_shell control` path
- central and module docs reflect the new ownership boundary

## Recovery Note

If later work needs the previous path during bisecting or compatibility checking, `vision_platform.apps.local_shell.live_command_sync` remains as the legacy import surface and can continue to forward to the service implementation.
