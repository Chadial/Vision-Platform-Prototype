# Roadmap

## Next

- expose stream-service imports consistently through `vision_platform.services.stream_service`
- add smoke coverage for the new namespace
- prepare fan-out hooks for ROI/focus/tracking consumers
- keep hardening the shutdown path for real-hardware preview sessions so stream teardown stays quiet and predictable for UI consumers
- decide whether a small framework-neutral viewport/event contract is worth introducing above the raw stream layer once the OpenCV prototype UI grows further

## Later

- feed API and overlay modules from the same acquisition backbone
- support richer stream health metrics

## Deferred

- browser streaming transport
