# WP97 Artifact Reference And Time Context Baseline

## Purpose

This work package defines one narrow follow-up slice for artifact references and minimal time context after the runtime-event baseline.

Closure lane:

- Usable Camera Subsystem / Pre-Product Baseline

Slice role:

- artifact-reference and time-context baseline

Scope level:

- current minimal artifact/time semantics only

Its purpose is to make one small, explicit repository-facing baseline for:

- what counts as an `ArtifactReference`
- which minimal time-context fields should travel with relevant artifacts and artifact-adjacent results

This package should be read as:

- artifact-reference clarification
- minimal time-context clarification
- traceability-boundary tightening

It should not be read as:

- a full logging package
- a full clock-domain architecture
- a broad metadata-expansion wave
- a transport contract freeze

## Branch

- current branch carrying the documentation sequence: `docs/camera-embedding-analysis`
- intended narrow execution branch if split later: `docs/wp97-artifact-reference-time-context-baseline`
- activation state: queued

## Scope

Included:

- define one minimal `ArtifactReference` reading for the current repo phase
- define one minimal time-context baseline for artifact-relevant outputs
- distinguish artifact references from:
  - logging
  - audit
  - event history
  - broader session metadata
- identify the current repo fields and outputs that already provide the best source material

Stable-now artifact-reference target:

- `artifact_path`
- `artifact_kind`
- `file_name`
- optional `run_id`
- optional `frame_id`
- optional `camera_id`
- minimal time context

Excluded:

- full metadata taxonomy
- full clock-domain design
- broad traceability redesign
- system-wide logging policy
- full offline-analysis metadata expansion

What this package does not close:

- final artifact DTO families
- final storage/index model
- cross-module time correlation
- system-wide logging semantics
- complete timestamp provenance architecture

Minimal interpretation rules:

- `run_id` and `frame_id` are valuable reference fields when present
- they are not required for every valid `ArtifactReference`
- their absence does not make an artifact reference invalid by itself
- traceability outputs may provide source material or evidence for an `ArtifactReference`
- traceability outputs are not themselves the definition of `ArtifactReference`

## Session Goal

Leave the repository with one explicit minimal baseline for artifact references and time context so later host integration, logging separation, and event work do not continue to overload existing CSVs and result payloads.

Expected concrete outputs:

- one queued `WP97` session work package
- one repo-near note update that names the minimal `ArtifactReference` baseline
- one repo-near note update that fixes the minimal time-context reading

## Status

- queued as the follow-up after `WP96`

## Sub-Packages

### WP97.A ArtifactReference Baseline

- status: planned
- purpose: define the smallest useful `ArtifactReference` meaning for the current repo phase

### WP97.B Minimal Time Context

- status: planned
- purpose: define the smallest useful time-context field set without opening a broad clock model

### WP97.C Boundary Clarification

- status: planned
- purpose: keep the line explicit between artifact reference, traceability, logging, and event semantics

## Open Questions

- Which current saved-artifact and recording outputs are stable enough to treat as baseline artifact-reference source material now?
- Which minimal time fields are already reliable enough to standardize without overcommitting to a later clock-domain model?
- How should `run_id` and `frame_id` be treated when present but not universal?

## Learned Constraints

- artifact references must not be collapsed into logging.
- minimal time context must stay small or it will drift into premature clock architecture.
- the package stays useful only if it clarifies meaning first and leaves richer metadata growth for later slices.
- traceability files are evidence or source material, not the `ArtifactReference` definition itself.
- `run_id` and `frame_id` must stay optional reference enrichments unless the repo later proves they are universally present.

## Execution Plan

1. Re-read:
   - `docs/STATUS.md`
   - `docs/WORKPACKAGES.md`
   - `docs/BiggerPictureNotes/camera_integration_surface_v0.1.md`
   - `docs/session_workpackages/wp96_runtime_event_family_baseline.md`
2. Inspect the current artifact-adjacent result shapes, traceability outputs, and time-related fields already present in the repo.
3. Define one minimal `ArtifactReference` baseline and one minimal time-context baseline.
4. Keep `run_id` and `frame_id` explicitly optional and `when present`.
5. Record which existing fields and outputs provide the current source material.
6. Keep traceability as evidence/source material, not as the definition of `ArtifactReference`.
7. Keep richer logging, metadata, and clock-correlation semantics deferred.

## Validation

- documentation consistency review against the current artifact, traceability, and time-related repo paths
- confirm artifact reference remains distinct from logging
- confirm time context remains minimal and does not turn into broad clock architecture
- confirm `run_id` and `frame_id` remain optional enrichments only
- confirm traceability remains source material/evidence only

## Documentation Updates

- `docs/BiggerPictureNotes/camera_integration_surface_v0.1.md` or a directly adjacent repo-near camera note if that becomes the clearest home
- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- this work-package file while active

## Expected Commit Shape

1. `docs: add wp97 artifact reference and time context baseline`
2. `docs: define minimal artifact reference and time context baseline`

## Merge Gate

- `WP97` is visible from `docs/WORKPACKAGES.md` as the queued follow-up after `WP96`
- the package keeps artifact reference distinct from logging
- the package keeps the time-context baseline intentionally small
- the package keeps `run_id` and `frame_id` explicitly optional
- the package keeps traceability outputs out of the `ArtifactReference` definition itself
- broad metadata, clock, and logging redesign remain deferred

## Recovery Note

To resume this package later:

1. read `docs/STATUS.md`
2. read `docs/WORKPACKAGES.md`
3. read `docs/session_workpackages/wp96_runtime_event_family_baseline.md`
4. read `docs/BiggerPictureNotes/camera_integration_surface_v0.1.md`
5. continue only with minimal artifact-reference and time-context clarification
