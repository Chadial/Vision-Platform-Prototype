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
- May 6, 2026 live rerun:
  - initial CLI hardware `status` succeeded on `tested_camera -> DEV_1AB22C046D81` with model `1800 U-1240m`, serial `067WH`, `capabilities_available=true`, and `capability_probe_error=null`
  - the original fixed exposure default proved state-dependent across live capability probes, so the shared `default` profile now keeps the stable `Mono10` / gain / ROI baseline and leaves exposure unset
  - the wx shell started on hardware with `--configuration-profile default`, published live status, and kept preview running with `Mono10`, gain `3`, ROI `0,0,2000,1500`, and save directory `captures\hardware_smoke\wp103_wx_shell_snapshot`
  - `Camera Settings...` opened through the real menu path in the running hardware shell
  - confirming the dialog completed without `failure_reflection`, left preview running, and preserved the full effective configuration in status
  - the known `vmbpyLog <VmbError.NotAvailable: -30>` residual appeared during successful hardware status/startup attempts and remained non-blocking

## Done Criteria

- either a fresh live pass is recorded, or the package is explicitly deferred because the tested device is not attached
- completed with fresh live evidence on May 6, 2026

## Recommended Follow-Up

- return immediately to the non-hardware structural lane if the device is unavailable
- no new default follow-up is opened by this pass; future hardware work should again be evidence- or residual-driven

