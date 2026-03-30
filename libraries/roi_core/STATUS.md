# Status

- maturity: active foundation module
- implemented: portable ROI helper layer with portable `RoiDefinition`, float bounds, centroid, frame-clamped pixel bounds, and rectangle/ellipse mask derivation
- working now: ROI remains a reusable geometry input, while consuming services decide whether to evaluate full-frame or ROI-limited data
- working now: analysis consumers such as focus evaluation can now consume ROI masks without embedding ROI math inside their own module
- working now: service-layer ROI state can carry one active ROI selection without making ROI a window-owned concern
- working now: when the OpenCV preview path is wired to `RoiStateService`, that service is the committed active ROI source shared by preview rendering and ROI-consuming analysis services; the window keeps only in-progress draft interaction state locally
- working now: shared ROI consumer precedence is explicit through `resolve_active_roi(...)`: explicit per-call ROI overrides the shared active ROI; otherwise consumers use the shared active ROI; otherwise they fall back to full-frame behavior
- partial: no interactive ROI editing, ROI collections, or freehand/polygon raster mask generation yet
- partial: canonical artifact-/metadata-level ROI serialization remains documentation-governed here; the intended text forms are `global`, `rectangle(x1,y1,x2,y2)`, `ellipse(x_c,y_c,x_corner,y_corner)`, and later `freehand(x1,y1,x2,y2,...,xn,yn)`, with freehand itself still intentionally post-MVP
- known issues: richer ROI editing and explicit non-OpenCV ROI producers are still not implemented, so the current shared ROI path is intentionally limited to one active ROI
- technical debt: richer ROI collections, serialization, and freehand support are still open
- risk: overlay and analysis needs may still force richer geometry types soon
