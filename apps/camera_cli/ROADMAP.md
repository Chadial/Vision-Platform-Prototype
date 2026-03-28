# Roadmap

## Next

- keep the baseline capability grouping explicit as `Capture`, `Camera`, and `Storage`
- add hardware-explicit validation notes once a reproducible hardware CLI path can be rerun
- decide the first follow-up work package after the baseline is stable instead of broadening the CLI by default
- consider whether a stricter machine-facing output shape is needed for later host embedding

## Later

- decide whether ROI commands should be added only after their host-facing workflow is clearer
- decide whether focus-method selection belongs in the CLI surface only after stronger analysis-service backing exists
- add explicit ROI set/clear commands if they map cleanly onto the shared model layer
- add analysis-oriented configuration flags only where the service layer already owns the behavior
- consider a narrower host-facing wrapper once a C# embedding path wants a stable CLI contract

## Deferred

- preview/view controls such as zoom, pan, fit-to-window, or overlay toggles
- browser or desktop UI concerns
- transport/API envelope shaping before a real external transport exists
