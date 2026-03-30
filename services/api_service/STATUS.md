# Status

- maturity: active baseline-preparation module
- implemented: transport-neutral API-service payload dataclasses for `SubsystemStatus` and its nested status/configuration shapes, plus a mapper from host-neutral status into those adapter DTOs
- implemented: transport-neutral command-envelope payload dataclasses plus bounded success/error builders now exist above the same shared host-neutral command baseline
- working now: the adapter-facing status family now also exposes one additive `active_run` polling block for active bounded recording or interval capture, derived from the existing shared status baseline without changing the core status model
- working now: bounded-recording status payloads now also carry the current narrow `run_id` when a run is active, so adapter-facing polling can align with the same traceability identity used in saved artifact logs
- working now: adapter layers no longer need to serialize shared core status models directly to get one stable status payload family
- working now: the first Host Control Closure slices now reuse this status mapper in the camera CLI envelope, so host polling for the selected command slices already consumes the adapter-facing status payload family
- working now: the camera CLI now also reuses this module's bounded command-envelope builders, so both polling payloads and the narrow current command envelope family share adapter-facing ownership
- partial: the bounded command-envelope family now exists, but broader command-result DTO families, feeds, and framework wiring remain open
- local direction: keep command and status shaping narrow and adapter-facing; only add more payload families when a concrete transport or host need exists
