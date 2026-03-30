# Current State

This file is a compact repository-state note.

For the authoritative current implementation truth, use:

- `docs/STATUS.md`

For the compact current architecture map, use:

- `docs/ARCHITECTURE_BASELINE.md`

## Current Repository Reading

- the repository now operates from a post-closure Python working baseline
- the preferred platform-facing implementation surface is `src/vision_platform`
- `src/camera_app` remains as a compatibility bridge during incremental physical migration
- the current baseline already includes bounded host control, runtime services, traceability, and tested-camera-path hardware evidence

## Current Practical Summary

What is already real:

- snapshot, preview, bounded recording, and bounded interval capture
- simulation and bounded real-hardware operation on the tested camera path
- one host-neutral command/controller baseline with thin CLI exposure
- traceability, recording-log output, and bounded offline artifact reuse
- optional OpenCV preview/inspection path kept outside the platform core

What remains later:

- broader transport/API surface
- detached recording lifecycle control
- broader frontend breadth
- wider hardware matrix and productization work
