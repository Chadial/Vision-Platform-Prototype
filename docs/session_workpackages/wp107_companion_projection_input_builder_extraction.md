# WP107 Companion Projection Input Builder Extraction

## Purpose

Move explicit companion status-projection input assembly out of the wx shell into one bounded service seam.

## Branch

- `refactor/wp107-companion-projection-input-builder`

## Closure Lane

- headless-kernel preparation after landed `WP100` through `WP106`

## Slice Role

- extraction
- structure-only ownership cleanup

## Scope

- extract assembly of `LocalShellStatusProjectionInput` and its setup/snapshot/recording input subsets from the wx shell
- keep the current projection payload semantics unchanged
- keep shell-owned live timing, rendering, and UI-local text formatting unchanged

## Ownership Boundary

The new builder owns only construction of `LocalShellStatusProjectionInput`.

It must not own:

- shell-local runtime state
- UI text formatting
- timer / tick cadence
- status publication timing
- reflection semantics
- failure policy

The wx shell remains the source of current app-local state.
The builder only converts explicitly supplied state into the existing projection-input structure.

## Guardrails

- treat this package as ownership extraction only
- do not add or rename projection fields
- do not redesign failure, snapshot, setup, or recording reflection meaning
- keep the shell as the caller that supplies current app-local state; move only the input-builder ownership

## Out Of Scope

- no new status semantics
- no new runtime orchestration
- no new transport or session model
- no UI wording changes

## Affected Modules

- `apps/local_shell`
- `services`
- local-shell status and command-result reflection tests

## Validation

- `.\.venv\Scripts\python.exe -m unittest tests.test_local_shell_live_command_sync tests.test_local_shell_control_cli tests.test_wx_preview_shell`

## Done Criteria

- the wx shell no longer assembles `LocalShellStatusProjectionInput` inline
- the new service seam takes explicit state inputs and returns the same projection-input structure as before
- command-result reflection and published status snapshots remain behaviorally unchanged

## Recommended Follow-Up

- extract the bounded failure-reflection state helper next only if that state still blocks further headless narrowing
- after `WP107` through `WP109`, do not derive further companion extraction work from cleanup momentum alone
- any later headless, runtime, host-contract, or LabVIEW-facing slice must be justified by a concrete residual, integration need, test failure, or user-observed workflow friction
- read `WP107` through `WP109` as the final bounded cleanup of the current companion-service extraction lane, not as the start of a broader facade/runtime architecture push
