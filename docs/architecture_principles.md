# Architecture Principles

- preserve the working Python baseline while introducing clearer platform boundaries
- separate repository module ownership from temporary physical source-file placement
- keep hardware integration, application services, reusable libraries, and UI/app entry points distinct
- prefer typed request/result objects over ad-hoc dictionaries
- keep reusable analysis foundations independent of OpenCV and UI concerns
- introduce portable contracts early so later C# migration does not depend on Python-specific internals
- treat simulation as a first-class path, not a test-only shortcut
- treat focus evaluation as consumer-driven: stream layers expose frames, while dedicated consumers decide when focus is computed
- treat ROI as reusable geometry and selection data: ROI helpers provide bounds and centroid, while consuming services decide whether to use full-frame or ROI-limited evaluation
- treat viewport fitting, zoom, pan, window sizing, and display-space overlay transforms as UI/display concerns rather than camera-core responsibilities
