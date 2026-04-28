# WP103 wx Camera Settings Live Path Revalidation

## Purpose

Execute one last narrow live `Camera Settings...` / menu-path check on the current `Mono10` hardware shell when the documented tested camera is physically attached.

## Branch

- `test/wp103-wx-camera-settings-live-path-revalidation`

## Closure Lane

- conditional hardware evidence

## Slice Role

- validation

## Scope

- start the wx shell on the documented tested hardware path
- open `Camera Settings...`
- verify the current dialog/menu path remains usable on the `Mono10` profile baseline
- capture the result in docs if fresh evidence is obtained

## Out Of Scope

- no broad hardware rerun
- no new settings features
- no transport or architecture work

## Affected Modules

- `apps/local_shell`
- central hardware/status docs only if fresh evidence changes current truth

## Validation

- live hardware-backed manual validation on `tested_camera` / `DEV_1AB22C046D81`

## Done Criteria

- either a fresh live pass is recorded, or the package is explicitly deferred because the tested device is not attached

## Recommended Follow-Up

- return immediately to the non-hardware structural lane if the device is unavailable

