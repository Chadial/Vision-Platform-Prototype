# Status

- maturity: active baseline module
- implemented: portable focus request/result contracts, a Laplace-based focus evaluator, and read-only overlay-data mapping
- working now: whole-frame manual-focus scoring for `FrameData` and `CapturedFrame`, plus anchor-point derivation for preview/display consumers
- working now: frame evaluation is explicitly consumer-driven through preview-facing consumers such as `FocusPreviewService`
- working now: live preview-adjacent consumers can derive focus state from preview frames, and the OpenCV prototype can carry that state through its preview path without moving analysis into the window code
- partial: ROI is supported as an optional bounded evaluation area, but ROI-driven UX is not wired yet
- known issues: only one numeric score is exposed, and full operator-facing overlay toggles and richer metric selection are not wired yet
- technical debt: edge/detail-oriented second-stage metrics are not implemented yet
- risk: future metric expansion may still require a deliberate NumPy/OpenCV decision
