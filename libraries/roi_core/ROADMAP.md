# Roadmap

## Next

- integrate ROI objects into snapshot and preview overlays without mixing UI and analysis logic
- decide how shared ROI state should enter focus-preview and later snapshot analysis workflows

## Later

- define freehand ROI payload shape that stays portable to C#
- keep this module as the source of truth for canonical artifact-/metadata-level ROI text serialization:
  - `global`
  - `rectangle(x1,y1,x2,y2)`
  - `ellipse(x_c,y_c,x_corner,y_corner)`
  - `freehand(x1,y1,x2,y2,...,xn,yn)`
- freeze the freehand text form before any artifact-metadata or offline consumer depends on it
- add ROI serialization/import helpers
- add ROI collections and visibility rules

## Deferred

- full interactive ROI editor
