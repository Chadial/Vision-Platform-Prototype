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

