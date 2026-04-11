# Hardware Enumeration And Startup Residual Narrowing

## Purpose

This work package defines the next residual-driven real-device follow-up if hardware is available.

Closure lane:

- Post-Closure Python Baseline / Hardening

Slice role:

- residual narrowing and evidence clarification

Scope level:

- current startup and enumeration residuals on the tested camera path

Its purpose is to narrow the remaining real-device ambiguity around duplicate SDK-visible camera entries and the still-observed non-blocking `VmbError.NotAvailable: -30` startup log line.

This package should be read as:

- residual-driven hardware hardening
- not broad hardware exploration
- not a new validation campaign

## Branch

- intended branch: `test/hardware-enumeration-startup-residual-narrowing`
- activation state: active lane

## Scope

Included:

- reproduce and classify the duplicate SDK visibility behavior for `DEV_1AB22C046D81`
- narrow whether the current `NotAvailable: -30` line correlates with any actual startup-state degradation
- document the current interpretation more sharply
- implement one small fix only if the residual proves actionable and narrowly localized

Excluded:

- camera matrix testing
- broad hardware benchmarking
- unrelated host-surface changes

What this package does not close:

- full hardware reliability closure across wider environments
- all future SDK quirks

## Session Goal

Leave the repository with one more explicit answer about whether the remaining startup and enumeration observations are actionable defects or bounded residual noise on the tested path.

## Validation

- bounded real-hardware reruns on the tested camera path
- update `docs/HARDWARE_EVALUATION.md` if the interpretation changes

## Landed Outcome

Observed result on March 30, 2026:

- raw Vimba X enumeration still exposed duplicate SDK-visible entries for `DEV_1AB22C046D81`
- the duplicate pair remained:
  - one entry with serial `067WH`
  - one entry with serial `N/A`
- direct real-hardware CLI `status` reruns still emitted `vmbpyLog <VmbError.NotAvailable: -30>` on stderr without failing startup

Implemented narrowing:

- the repository now resolves duplicate SDK-visible entries by camera id and prefers the richer identity candidate during camera selection
- the hardware driver now preserves that richer pre-open camera identity for host-visible status fields when the opened camera object degrades fields such as `camera_serial` to `N/A`

Current interpretation after landing:

- duplicate SDK visibility remains an SDK-level residual under observation
- the repository no longer needs to surface that duplicate ambiguity as degraded host-visible camera identity on the tested path
- the `NotAvailable: -30` line remains classified as non-blocking SDK / logging residual unless later evidence ties it to actual startup or capability degradation

