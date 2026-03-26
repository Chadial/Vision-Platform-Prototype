# Status

- maturity: prepared base module
- implemented: minimal ROI helper layer with portable `RoiDefinition`
- working now: bounding-box helper, centroid helper, and shared ROI model definitions for later overlay consumers
- partial: no interactive ROI editing or raster mask generation yet
- known issues: existing preview flow does not yet consume ROI objects
- technical debt: ROI support is architectural groundwork, not yet integrated behavior
- risk: overlay and analysis needs may force richer geometry types soon
