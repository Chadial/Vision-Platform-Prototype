# Roadmap

## Phase 1: Foundation

- create package structure
- define data models
- define `CameraDriver` abstraction
- establish logging and file naming conventions

## Phase 2: Camera Access

### Phase 2a: Discovery and Initialization

- implement `VimbaXCameraDriver`
- discover available cameras
- open camera by explicit id or first available camera
- expose basic `CameraStatus`
- shut down cleanly

### Phase 2b: Configuration

- apply selected camera features through `CameraConfiguration`
- handle unsupported or unavailable camera features defensively
- log applied settings and configuration failures

### Phase 2c: Single-Frame Acquisition

- acquire one frame safely from the camera
- expose frame metadata needed for later preview and saving
- validate error handling for timeout and disconnected-camera cases

### Phase 2d: Snapshot Save Flow

- connect single-frame acquisition to `SnapshotService`
- save one image to an explicit target path
- confirm naming behavior and save result logging

### Phase 2e: End-to-End Smoke Test

- validate `initialize -> configure -> capture -> save -> shutdown`
- keep the first end-to-end path small and reproducible
- use this as the baseline before preview and recording work

## Phase 3: Snapshot Flow

- implement snapshot request validation
- save single image to explicit path
- log save attempts and results

## Phase 4: Preview Flow

- maintain a latest-frame buffer
- expose preview frame metadata without binding to a UI toolkit
- keep preview independent from snapshot and recording

## Phase 5: Recording Flow

- implement producer/consumer acquisition pipeline
- add bounded queue
- add writer service
- support stop by count, duration, or explicit stop

## Phase 6: Host Integration

- implement command controller
- support external save directory changes
- expose consolidated status to AMB or future UI

## Phase 7: Validation

- add tests for naming, validation, queue behavior, and state transitions
- add small run examples or smoke-test scripts

## Initial Deliverables

- package layout under `src/`
- request and status dataclasses
- driver interface
- command controller skeleton
- storage and logging scaffolding
