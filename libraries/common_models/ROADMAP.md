# Roadmap

## Next

- align future service additions with the new common model set first
- keep `common_models` as the target platform contract surface even when some fields or enum members are only roadmap-visible and not yet implemented end-to-end
- mark contract readiness explicitly in module `STATUS.md` whenever the exposed model surface intentionally runs ahead of implementation
- map legacy `camera_app.models` types progressively where it reduces duplication
- decide which model set becomes the long-term source of truth during the next refactor phase
- decide whether future overlay payloads stay as fixed fields or move to a more generic layer collection

## Later

- expand focus-method support beyond Laplace only when the next analysis phase actually needs those methods
- add polygon or freehand ROI support as a later ROI-core capability instead of treating `freehand` as currently executable behavior
- add typed analysis result envelopes
- add transport-safe serialization helpers when needed

## Deferred

- executable freehand ROI mask generation and downstream analysis support
- full DTO versioning
