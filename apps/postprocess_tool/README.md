# Postprocess Tool

Thin offline evaluation entry points above the shared analysis and storage contracts.

This module is intended to stay lightweight and reuse the existing platform cores for loading, analysis, and report shaping.

It should not become a second analytics core separate from the shared libraries and services.

## Current Baseline

- stored-image focus report over `.pgm` / `.ppm` sample directories
- stored-image focus report over saved `.bmp` artifacts produced by the dependency-free writer baseline
- reuse of the simulator-backed sample-image ingestion path plus a narrow saved-`BMP` loader above `focus_core`

## Not This Module Yet

- broad offline workstation behavior
- arbitrary file-format loading beyond the current narrow `.pgm` / `.ppm` / `.bmp` baseline
- export pipelines beyond compact text reporting
