# Roadmap

## Next

- prepare fan-out hooks for ROI/focus/tracking consumers
- keep hardening the shutdown path for real-hardware preview sessions so stream teardown stays quiet and predictable for UI consumers
- only introduce a framework-neutral viewport/event contract if the OpenCV path proves that one shared stream-facing contract is actually needed

## Later

- feed API and overlay modules from the same acquisition backbone
- support richer stream health metrics

## Deferred

- browser streaming transport
