# API Service

Adapter-oriented payload shaping and later API/feed exposure above the shared host-neutral control/application layer.

This module is intended to become an external adapter above the same host-neutral control/application layer used by local tools such as the CLI.

It should not become a parallel business-logic stack separate from the shared service/controller path.

## Current Baseline

- first adapter-facing status payload family
- transport-neutral mapping from `SubsystemStatus` into API-service DTOs
- additive `active_run` polling payload derived from the existing recording and interval-capture status surfaces for active host polling
- first bounded command-envelope payload family reused by the camera CLI for `status`, `snapshot`, bounded `recording`, and bounded `interval-capture`

## Not This Module Yet

- HTTP or IPC framework wiring
- frame/feed streaming
- duplicate command execution logic
- broad command-result contract redesign
