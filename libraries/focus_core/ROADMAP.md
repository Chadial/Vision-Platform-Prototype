# Roadmap

## Next

- document baseline-versus-optional method guidance now that preview/snapshot consumers can already select `laplace` or `tenengrad`
- keep `laplace` as the default path while documenting when `tenengrad` should be chosen instead
- keep results portable enough for later C# DTOs

## Later

- add metric comparison support
- add ROI-first edge/detail analysis as a second-stage metric family
- add local/global aggregation helpers
- document one narrow artifact-metadata mapping baseline for focus results without widening this module into storage or reporting ownership
- if artifact metadata carries `focus_value_mean` and `focus_value_stddev`, freeze them against an explicit moving-window field such as `focus_score_frame_interval` before downstream consumers depend on them

## Deferred

- advanced autofocus or drift coupling
