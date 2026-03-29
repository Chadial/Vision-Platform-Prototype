# Status

- maturity: active baseline
- implemented: thin stored-image focus-report path over `.pgm` / `.ppm` sample directories and saved `.bmp` artifacts, reusing the existing simulator-backed sample-image ingestion path plus a narrow `BMP` loader above `focus_core`
- working now: offline focus evaluation can run without a live camera loop and returns one typed per-image report entry for compact reporting over both sample-image and saved-`BMP` directories
- partial: the module currently supports one focus-oriented offline report only; broader metadata joins, tracking, richer file formats, and export concerns remain open
- next use: extend only when another offline slice can reuse the same shared contracts without inventing a second analytics pipeline
