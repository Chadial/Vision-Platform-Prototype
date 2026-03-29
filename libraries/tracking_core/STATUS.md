# Status

- maturity: active baseline module
- implemented: directional edge-profile analysis with portable request/result contracts and dominant-edge extraction over full-frame or ROI-bounded image data
- working now: `tracking_core` can analyze one horizontal or vertical intensity profile from `FrameData` or `CapturedFrame` and report the dominant edge transition as a small transport-neutral result
- working now: the baseline stays aligned with existing ROI/frame model boundaries and does not depend on UI, stream, or host layers
- partial: no drift indication, crack-tip heuristics, or multi-frame feature tracking yet
- known issues: the first baseline only reports one dominant edge transition and does not yet express confidence bands, continuity, or multi-peak candidates
- technical debt: image decoding logic is currently local to the baseline kernel and may want later convergence with other analysis modules if more kernels appear
