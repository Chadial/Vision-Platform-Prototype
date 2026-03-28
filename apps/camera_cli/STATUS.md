# Status

- maturity: active baseline
- current implementation: a first `vision_platform.apps.camera_cli` package now provides one unified entry command with `status`, `snapshot`, `recording`, and `interval-capture` subcommands
- working now: simulator-backed CLI runs can initialize a camera source, optionally apply camera configuration, resolve explicit save-directory behavior, save one snapshot, run bounded recording, and run bounded interval capture through the existing command-controller-backed subsystem wiring
- working now: CLI output is emitted as a JSON summary so shell callers can inspect the selected save directory, snapshot path, and consolidated subsystem status without depending on preview/UI code
- working now: the first CLI capability grouping is intentionally limited to `Capture`, `Camera`, and `Storage` concerns through the current `status`, `snapshot`, `recording`, and `interval-capture` commands
- partial: ROI and analysis commands are intentionally out of scope for the first CLI baseline and should only be added once their host-facing workflow is clearer and the underlying service contracts are explicit enough to keep the CLI thin
- partial: hardware-backed execution is wired through the same entry point, but current validation remains simulator-first because the previously used camera hardware is not attached locally
- technical debt: the CLI package currently returns one post-command summary object rather than a richer transport-oriented result contract
- risk: preview-only concerns remain intentionally outside this module, so the CLI does not replace the OpenCV preview path for inspection-driven workflows
- next step: keep the first baseline narrow, add hardware-explicit validation notes when the camera is attached again, and only extend beyond `Capture`, `Camera`, and `Storage` when that can be done without inventing CLI-only business logic
