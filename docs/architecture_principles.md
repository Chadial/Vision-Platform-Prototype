# Architecture Principles

- preserve the working Python baseline while introducing clearer platform boundaries
- separate repository module ownership from temporary physical source-file placement
- keep hardware integration, application services, reusable libraries, and UI/app entry points distinct
- prefer typed request/result objects over ad-hoc dictionaries
- keep reusable analysis foundations independent of OpenCV and UI concerns
- introduce portable contracts early so later C# migration does not depend on Python-specific internals
- treat simulation as a first-class path, not a test-only shortcut
