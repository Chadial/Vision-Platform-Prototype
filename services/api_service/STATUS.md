# Status

- maturity: active baseline-preparation module
- implemented: transport-neutral API-service payload dataclasses for `SubsystemStatus` and its nested status/configuration shapes, plus a mapper from host-neutral status into those adapter DTOs
- working now: the adapter-facing status family now also exposes one additive `active_run` polling block for active bounded recording or interval capture, derived from the existing shared status baseline without changing the core status model
- working now: adapter layers no longer need to serialize shared core status models directly to get one stable status payload family
- working now: the first Host Control Closure slices now reuse this status mapper in the camera CLI envelope, so host polling for the selected command slices already consumes the adapter-facing status payload family
- partial: only the status payload family is prepared so far; command-result DTOs, feeds, and framework wiring remain open
- known issues: serialization ownership is only partially unified so far; the CLI now reuses the status payload family for polling, but command-result DTOs still remain adapter-specific follow-up work
- next use: keep status polling additive and narrow, then use `WP23` for post-command confirmed-settings hardening instead of widening this polling slice into broader command-result shaping
