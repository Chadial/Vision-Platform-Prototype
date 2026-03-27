# Hardware Capability Baseline

## Purpose

This document records the capability baseline of the real camera hardware that has been exercised against this repository.

Use it for:

- later feature planning
- understanding which camera-side controls are actually available
- separating generic platform intent from device-specific constraints

This document is not a replacement for `docs/HARDWARE_EVALUATION.md`.
It describes the tested device capability surface, while `docs/HARDWARE_EVALUATION.md` describes validation runs and pass/fail state.

## Tested Device

Snapshot date:

- March 27, 2026

Connected device:

- vendor: `Allied Vision`
- family: `ALVIUM`
- model: `1800 U-1240m`
- camera id: `DEV_1AB22C046D81`
- serial number feature: `067WH`
- `cam.get_serial()` result: `N/A`
- interface id: `VimbaUSBInterface_0x0`

Firmware and transport baseline:

- firmware version: `13.0.71D891FE`
- device version: `14816`
- transport-layer version: `1.1`
- SFNC version: `2.7.1`

Project-side software baseline:

- VmbPy log during hardware runs: `vmbpy 1.2.1`
- VmbC log during hardware runs: `1.3.0`
- VmbImageTransform log during hardware runs: `2.3`

## Capability Summary

The tested camera exposed `200` features through Vimba X during the local capability probe.

Relevant capability groups observed:

- camera identity and firmware features
- sensor and image-format features
- exposure and gain controls, including auto modes
- acquisition-rate control with enable gating
- trigger, line, timer, and counter features
- user sets
- chunk-data controls
- bandwidth / throughput controls
- binning and image-orientation controls

## Sensor And Image Geometry

Sensor geometry:

- `SensorWidth = 4024`
- `SensorHeight = 3036`

Observed ROI-related constraints from previous hardware validation:

- width range: `8 .. 4024`, increment `8`
- height range: `8 .. 3036`, increment `2`
- `OffsetX` and `OffsetY` were constrained to `0` on the tested configuration path

Implication:

- this device currently behaves like a size-only ROI target in the tested mode
- feature work should not assume free ROI panning on this camera without re-validation in another mode

## Pixel Format And Bit Depth

Observed pixel-format entries:

- `Mono8`
- `Mono10`
- `Mono10p`
- `Mono12`
- `Mono12p`

Observed related features:

- `SensorBitDepth`: writable, current value `Bpp10`
- `PixelSize`: read-only, current value `Bpp16`

Validated save-path facts from hardware runs:

- `Mono8` snapshot and recording paths are working
- `Mono10` snapshot save to `.raw` is working
- unsupported `Mono16` fails explicitly on this device because no matching enum entry exists

Implication:

- higher-bit grayscale support is available on the camera
- packed versus unpacked format handling must stay explicit in software
- OpenCV-based higher-bit save/display validation remains a separate follow-up topic

## Exposure And Gain

Observed exposure features:

- `ExposureMode`: writable, currently `Timed`
- `ExposureAuto`: writable, entries `Off`, `Once`, `Continuous`
- `ExposureTime`: writable
  - current probed value: approximately `9973.736`
  - range: `42.278 .. 9999975.403`
  - increment: `40.208`

Observed gain features:

- `Gain`: writable
  - current probed value: `3.0`
  - range: `0.0 .. 27.000001907348633`
  - increment: `0.1`
- `GainAuto`: writable, entries `Off`, `Once`, `Continuous`

Implication:

- exposure and gain are viable camera-side controls for later UI or host integration
- both manual and auto-mode concepts are available on this device

## Acquisition Rate Control

Observed acquisition-rate features:

- `AcquisitionFrameRateEnable`: writable, current value `True` after the latest hardware probe
- `AcquisitionFrameRate`: read/write when enabled
  - current probed value: approximately `4.999088764190674`
  - range: `0.37806829810142517 .. 8.022730827331543`
- `AcquisitionFrameRateMode`: writable, current value `Basic`

Confirmed hardware behavior:

- with `AcquisitionFrameRateEnable = False`, `AcquisitionFrameRate` is read-only
- enabling `AcquisitionFrameRateEnable` makes `AcquisitionFrameRate` writable
- setting a reduced rate such as `5.0` succeeds and reads back approximately `4.9991`

Implication:

- the feature is both a status value and a controllable camera-side limit
- renderer or status-bar code can consume the reported value
- configuration code can also set it, but must treat the enable flag as part of the control path

## Acquisition And Triggering

Observed acquisition features:

- `AcquisitionMode`: writable, entries `SingleFrame`, `MultiFrame`, `Continuous`

Observed trigger-related features:

- `TriggerSelector`: writable
  - entries include `AcquisitionStart`, `AcquisitionEnd`, `AcquisitionActive`, `FrameStart`
- `TriggerSource`: writable
  - entries include `Software`, `Line0`..`Line3`, timer and counter activity sources, `SoftwareSignal0`, `SoftwareSignal1`
- `TriggerMode`: present
  - observed entries `Off`, `On`
  - writability appeared state-dependent across probes

Implication:

- software and line-based trigger foundations exist on the device
- any trigger feature work should assume that some writability may depend on current mode or selector state

## Line, Timer, Counter, And Signal Surface

Observed line features:

- `LineSelector`: writable, entries `Line0`..`Line3`
- `LineMode`: writable, entries `Input`, `Output`
- `LineSource`: present with multiple output source entries, but not available in the probed state

Observed timer and counter features:

- `TimerSelector`: writable, entries `Timer0`, `Timer1`
- `CounterSelector`: writable, entries `Counter0`..`Counter3`

Implication:

- the hardware has a meaningful IO/timing surface for later advanced trigger or automation work
- later line-output or timer-driven features should be treated as device-capability-backed, not hypothetical

## Bandwidth And Throughput

Observed throughput features:

- `DeviceLinkSpeed = 450000000`
- `DeviceLinkThroughputLimit`: writable
  - current value: `200000000`
  - range: `42750000 .. 450000000`
- `DeviceLinkThroughputLimitMode`: writable, entries `On`, `Off`

Implication:

- this device exposes an explicit throughput-limiting control path
- later "run slower on purpose" or USB-bandwidth-stability work should consider camera-side throughput limiting in addition to camera-side frame-rate limiting

## User Sets And Persistence

Observed user-set features:

- `UserSetSelector`: writable, entries `Default`, `UserSet1`, `UserSet2`, `UserSet3`, `UserSet4`
- `UserSetDefault`: writable, current value `Default`

Implication:

- the hardware exposes persistent configuration slots
- later host integration could optionally load or save stable camera presets if the workflow justifies it

## Binning, Orientation, And Image-Processing Surface

Observed image-shaping features:

- `BinningHorizontal`: writable, range `1 .. 8`
- `BinningVertical`: writable, range `1 .. 8`
- `ReverseX`: writable
- `ReverseY`: writable

Observed additional processing-oriented features from the full feature list:

- black level
- gamma
- sharpness
- LUT controls
- contrast controls
- convolution controls
- lens-shading controls

Implication:

- the device has a broader onboard image-conditioning surface than the current repository uses
- any future use of those features should be deliberate because they can alter measurement data semantics

## Chunk Data

Observed chunk features:

- `ChunkModeActive`: writable
- `ChunkSelector` entries include:
  - `LineStatusAll`
  - `Timestamp`
  - `SequencerSetActive`
  - `ExposureTime`
  - `Gain`
  - `Height`
  - `Width`
  - `OffsetX`
  - `OffsetY`

Implication:

- the camera can attach useful metadata to frames
- later metadata-rich acquisition could use chunk features instead of relying only on host-side timing and cached configuration

## Current Planning Guidance

Safe assumptions for later feature work on this exact camera:

- snapshot, preview, interval capture, and recording are already hardware-validated
- exposure, gain, ROI size, pixel format, and acquisition-frame-rate limiting are viable control paths
- camera-side throughput limiting is available
- trigger, line, timer, and counter features exist and are suitable candidates for later advanced control work
- persistent user sets exist

Constraints to keep visible:

- ROI offset freedom was not observed in the tested mode
- trigger writability appears mode-dependent
- packed higher-bit formats need explicit software handling
- image-conditioning features exist, but using them may conflict with measurement-oriented capture goals
