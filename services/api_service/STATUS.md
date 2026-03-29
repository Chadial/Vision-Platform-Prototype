# Status

- maturity: active baseline-preparation module
- implemented: transport-neutral API-service payload dataclasses for `SubsystemStatus` and its nested status/configuration shapes, plus a mapper from host-neutral status into those adapter DTOs
- working now: adapter layers no longer need to serialize shared core status models directly to get one stable status payload family
- partial: only the status payload family is prepared so far; command-result DTOs, feeds, and framework wiring remain open
- known issues: serialization ownership between the existing CLI path and the new adapter DTO layer is still intentionally conservative and not yet unified
- next use: extend from this DTO baseline only when a real external adapter lane is opened or when `WP09` identifies a small contract hardening slice that clearly belongs above the shared command surface
