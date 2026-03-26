# Target Structure

## Repository Layout

```text
apps/
  opencv_prototype/
  postprocess_tool/
  desktop_app/
integrations/
  camera/
services/
  stream_service/
  recording_service/
  api_service/
libraries/
  common_models/
  roi_core/
  focus_core/
  tracking_core/
configs/
docs/
src/
  camera_app/
  vision_platform/
tests/
tools/
```

## Role Of The Main Areas

- `apps/`: runnable frontends and prototype entry points
- `integrations/`: hardware and external-system adapters
- `services/`: orchestration and application workflows
- `libraries/`: reusable core contracts and analysis foundations
- `src/camera_app/`: stable legacy implementation during migration
- `src/vision_platform/`: new platform-facing namespace and migration surface

## Migration Rule

During this round, implementation stability has priority over physical code relocation. The platform shape is made explicit first through module ownership, documentation, and new import surfaces. Future rounds can move implementation files behind those stable module boundaries with lower risk.
