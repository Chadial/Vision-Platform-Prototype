# Status

- maturity: active baseline
- implemented: thin stored-image focus-report path over `.pgm` / `.ppm` sample directories, using the existing simulator-backed sample-image ingestion path and `focus_core`
- working now: offline focus evaluation can run without a live camera loop and returns one typed per-image report entry for compact reporting
- partial: the module currently supports one focus-oriented offline report only; broader metadata joins, tracking, richer file formats, and export concerns remain open
- next use: extend only when another offline slice can reuse the same shared contracts without inventing a second analytics pipeline
