# Common Models

## Purpose

Provides portable, language-friendly data models that can survive the planned Python-to-C# handover.

## Responsibility

- normalized frame metadata
- future-shared ROI definitions
- future-shared focus request and result contracts

## Functions

- `FrameMetadata`
- `FrameData`
- `RoiDefinition`
- `FocusRequest`
- `FocusResult`

## Inputs / Outputs

- inputs: frame and analysis data from integrations and services
- outputs: typed contracts for services, APIs, and future frontends

## Dependencies

- standard library only
