# Postprocess Tool

Thin offline evaluation entry points above the shared analysis and storage contracts.

This module is intended to stay lightweight and reuse the existing platform cores for loading, analysis, and report shaping.

It should not become a second analytics core separate from the shared libraries and services.

## Current Baseline

- stored-image focus report over `.pgm` / `.ppm` sample directories
- reuse of the simulator-backed sample-image ingestion path plus `focus_core`

## Not This Module Yet

- broad offline workstation behavior
- arbitrary file-format loading
- export pipelines beyond compact text reporting
