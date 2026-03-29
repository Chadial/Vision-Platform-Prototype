# Status

- maturity: active baseline module
- implemented: portable focus request/result contracts, Laplace- and Tenengrad-based focus evaluators, explicit method dispatch, and read-only overlay-data mapping
- working now: whole-frame manual-focus scoring for `FrameData` and `CapturedFrame`, plus anchor-point derivation for preview/display consumers
- working now: `evaluate_focus(...)` now honors `FocusRequest.method`, with `laplace` remaining the default path and `tenengrad` available as a second implemented metric
- working now: frame evaluation is explicitly consumer-driven through preview-facing consumers such as `FocusPreviewService`
- working now: live preview-adjacent consumers can derive focus state from preview frames, and the OpenCV prototype can carry that state through its preview path without moving analysis into the window code
- working now: preview- and snapshot-side focus consumers can now select `laplace` or `tenengrad` through a small service-level method-selection path while still allowing evaluator injection for local composition
- partial: ROI is supported as an optional bounded evaluation area, but ROI-driven UX is not wired yet
- known issues: consumers still default to Laplace unless they opt into another method, and full operator-facing overlay toggles and richer metric selection are not wired yet
- technical debt: broader edge/detail-oriented second-stage metrics and explicit consumer-side method selection are not implemented yet
- risk: future metric expansion may still require a deliberate NumPy/OpenCV decision
