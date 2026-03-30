# Postprocess Tool

Thin offline evaluation entry points above the shared analysis and storage contracts.

This module is intended to stay lightweight and reuse the existing platform cores for loading, analysis, and report shaping.

It should not become a second analytics core separate from the shared libraries and services.

## Current Baseline

- stored-image focus report over `.pgm` / `.ppm` sample directories
- stored-image focus report over saved `.bmp` artifacts produced by the dependency-free writer baseline
- reuse of the simulator-backed sample-image ingestion path plus a narrow saved-`BMP` loader above `focus_core`
- compact metadata-aware offline reuse of saved artifacts when a folder-local traceability log is present, with deterministic join by saved image name
- compact folder-level stable-context reuse from the same traceability log header when that header is present, while keeping the report text-oriented and narrow
- when focus-summary metadata is present in that traceability log, the compact report now also surfaces its explicit aggregation-basis field instead of treating summary values as standalone
- one additive compact report-summary line now exposes entry count, traceability-join count, and the current highest-score image without widening into export or explorer behavior

## Not This Module Yet

- broad offline workstation behavior
- arbitrary file-format loading beyond the current narrow `.pgm` / `.ppm` / `.bmp` baseline
- run/session or ROI explorer behavior
- export pipelines beyond compact text reporting
