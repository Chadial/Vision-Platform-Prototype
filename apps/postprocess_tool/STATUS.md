# Status

- maturity: active baseline
- implemented: thin stored-image focus-report path over `.pgm` / `.ppm` sample directories and saved `.bmp` artifacts, reusing the existing simulator-backed sample-image ingestion path plus a narrow `BMP` loader above `focus_core`
- implemented: the compact offline focus-report path now also reuses saved-artifact traceability metadata when a folder-local traceability log is present, joining rows deterministically by saved image name
- implemented: when focus summary metadata is present, the compact offline report now also surfaces the explicit aggregation-basis field carried with those summary values
- working now: offline focus evaluation can run without a live camera loop and returns one typed per-image report entry for compact reporting over both sample-image and saved-`BMP` directories, with graceful degradation when traceability metadata is absent or partial
- partial: the module currently supports one focus-oriented offline report only; broader metadata joins, stronger focus-summary policy decisions, tracking, richer file formats, export concerns, and any run/session or ROI-explorer behavior remain open
- next use: extend only when another offline slice can reuse the same shared contracts without inventing a second analytics pipeline
