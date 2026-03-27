# Status

- maturity: active foundation module
- implemented: shared frame, ROI, focus, and display-overlay model set exists under `src/vision_platform/libraries/common_models`
- implemented: `FrameMetadata`, `FrameData`, `RoiDefinition`, `FocusRequest`, `FocusResult`, `FocusOverlayData`, `FocusPreviewState`, `RoiOverlayData`, and `DisplayOverlayPayload` are importable and used by ROI, focus, and display-adjacent platform modules
- working now: current consumers support the UI-free overlay composition path between preview and snapshot consumers
- prepared but not fully implemented: `FocusMethod` exposes future analysis-method names, but the implemented focus baseline is still Laplace-based only
- prepared but not fully implemented: `RoiShape` includes `freehand` as a target contract shape, but downstream ROI-core and analysis helpers currently support rectangle and ellipse only
- partial: existing legacy services still use `camera_app.models`, so service contracts are not yet fully migrated to `common_models`
- known issues: no feature-status marker exists inside the model types themselves, so support level must currently be documented in module status and roadmap files
- technical debt: duplicate concepts exist intentionally during transition
- risk: model divergence if future changes are applied to only one side
- next: keep future platform-facing contracts aligned to `common_models`, explicitly mark prepared-vs-implemented contract surface in docs, and defer freehand/polygon ROI behavior until a later ROI-core phase
