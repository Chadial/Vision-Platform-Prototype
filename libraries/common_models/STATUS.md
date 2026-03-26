# Status

- maturity: active foundation module
- implemented: shared frame, ROI, focus, and display-overlay model set under `src/vision_platform/libraries/common_models`
- working now: models are importable and support UI-free display composition between preview and snapshot consumers
- partial: existing legacy services still use `camera_app.models`
- known issues: no full migration of service contracts yet
- technical debt: duplicate concepts exist intentionally during transition
- risk: model divergence if future changes are applied to only one side
