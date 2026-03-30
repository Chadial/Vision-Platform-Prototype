# Status

- maturity: active baseline
- current implementation: a first `vision_platform.apps.camera_cli` package now provides one unified entry command with `status`, `snapshot`, `recording`, and `interval-capture` subcommands
- working now: simulator-backed CLI runs can initialize a camera source, optionally apply camera configuration, resolve explicit save-directory behavior, save one snapshot, run bounded recording, and run bounded interval capture through the existing command-controller-backed subsystem wiring
- working now: the selected host-control slice now emits a stable machine-readable command envelope for `status`, `snapshot`, and bounded `recording`, with successful command JSON on stdout and machine-readable error JSON on stderr
- working now: the `status` portion of that envelope now routes through the transport-neutral API-service status payload mapper, so host polling no longer depends on direct serialization of the shared core status model
- working now: host polling now also receives one additive `active_run` subset for active bounded recording or interval capture, keeping current-work observability separate from later command-confirmation follow-ups
- working now: command results now expose a small confirmed-settings subset for host-side logging and experiment traceability, including camera id, pixel format, exposure, resolved save directory, resolved file stem / extension, and accepted recording bounds where relevant
- working now: `snapshot` and bounded `recording` results now also expose one deterministic `run_id` aligned with the traceability logs, while bounded-recording polling exposes that identity only during active work
- working now: the first CLI capability grouping is intentionally limited to `Capture`, `Camera`, and `Storage` concerns through the current `status`, `snapshot`, `recording`, and `interval-capture` commands
- partial: ROI and analysis commands are intentionally out of scope for the first CLI baseline and should only be added once their host-facing workflow is clearer and the underlying service contracts are explicit enough to keep the CLI thin
- partial: hardware-backed execution is wired through the same entry point, but current validation remains simulator-first because the previously used camera hardware is not attached locally
- partial: `recording` in this host-control slice is explicitly bounded and in-process; detached multi-invocation recording lifecycle control remains deferred for later closure work
- technical debt: only the selected `status`/`snapshot`/`recording` slice is normalized so far; `interval-capture` has not yet been pulled into the same host-envelope contract
- risk: preview-only concerns remain intentionally outside this module, so the CLI does not replace the OpenCV preview path for inspection-driven workflows
- next step: keep the exposed `run_id` narrow and linkage-oriented, use `WP25` for recovery validation instead of widening this slice into broader history or explorer behavior, add hardware-explicit validation notes when the camera is attached again, and only extend beyond `Capture`, `Camera`, and `Storage` when that can be done without inventing CLI-only business logic
