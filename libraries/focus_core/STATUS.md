# Status

- maturity: active baseline module
- implemented: portable focus request/result contracts, Laplace- and Tenengrad-based focus evaluators, explicit method dispatch, and read-only overlay-data mapping
- working now: whole-frame manual-focus scoring for `FrameData` and `CapturedFrame`, plus anchor-point derivation for preview/display consumers
- working now: `evaluate_focus(...)` now honors `FocusRequest.method`, with `laplace` remaining the default path and `tenengrad` available as a second implemented metric
- working now: frame evaluation is explicitly consumer-driven through preview-facing consumers such as `FocusPreviewService`
- working now: live preview-adjacent consumers can derive focus state from preview frames, and the OpenCV prototype can carry that state through its preview path without moving analysis into the window code
- working now: preview- and snapshot-side focus consumers can now select `laplace` or `tenengrad` through a small service-level method-selection path while still allowing evaluator injection for local composition
- partial: focus results are now close enough to downstream artifact metadata use that this module should be treated as the semantic source for fields such as `focus_method`, `focus_value_mean`, `focus_value_stddev`, `focus_roi_type`, and `focus_roi_data`, while storage/traceability ownership still belongs elsewhere
- partial: if artifact metadata uses `focus_value_mean` and `focus_value_stddev`, they should be interpreted against an explicit aggregation basis such as `focus_score_frame_interval`, but exact defaults, bounds, and stronger policy rules still need later testing and definition
- partial: ROI is supported as an optional bounded evaluation area, but ROI-driven UX is not wired yet
- known issues: consumers still default to Laplace unless they opt into another method, and full operator-facing overlay toggles and richer metric selection are not wired yet
- technical debt: broader edge/detail-oriented second-stage metrics and explicit consumer-side method selection are not implemented yet
- risk: future metric expansion may still require a deliberate NumPy/OpenCV decision
