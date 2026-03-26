# Status

- maturity: active baseline module
- implemented: portable focus request/result contracts and a Laplace-based focus evaluator
- working now: whole-frame manual-focus scoring for `FrameData` and `CapturedFrame`
- partial: ROI is supported as an optional bounded evaluation area, but ROI-driven UX is not wired yet
- known issues: only one numeric score is exposed and no live preview overlay consumes it yet
- technical debt: edge/detail-oriented second-stage metrics are not implemented yet
- risk: future metric expansion may still require a deliberate NumPy/OpenCV decision
