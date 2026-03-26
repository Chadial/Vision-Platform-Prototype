# Status

- maturity: prepared base module
- implemented: portable ROI helper layer with portable `RoiDefinition`, float bounds, centroid, frame-clamped pixel bounds, and rectangle/ellipse mask derivation
- working now: ROI remains a reusable geometry input, while consuming services decide whether to evaluate full-frame or ROI-limited data
- working now: analysis consumers such as focus evaluation can now consume ROI masks without embedding ROI math inside their own module
- working now: service-layer ROI state can carry one active ROI selection without making ROI a window-owned concern
- partial: no interactive ROI editing or freehand raster mask generation yet
- known issues: existing preview flow does not yet maintain an ROI state of its own
- technical debt: richer ROI collections, serialization, and freehand support are still open
- risk: overlay and analysis needs may still force richer geometry types soon
