# Status

- maturity: active baseline-preparation module
- implemented: transport-neutral API-service payload dataclasses for `SubsystemStatus` and its nested status/configuration shapes, plus a mapper from host-neutral status into those adapter DTOs
- working now: adapter layers no longer need to serialize shared core status models directly to get one stable status payload family
- working now: the first Host Control Closure slice now reuses this status mapper in the camera CLI envelope, so host polling for that selected command slice already consumes the adapter-facing status payload family
- partial: only the status payload family is prepared so far; command-result DTOs, feeds, and framework wiring remain open
- known issues: serialization ownership is only partially unified so far; the CLI now reuses the status payload family for the selected host-control slice, but command-result DTOs still remain adapter-specific follow-up work
- next use: extend from this DTO baseline only when a real external adapter lane is opened or when `WP09` identifies a small contract hardening slice that clearly belongs above the shared command surface
