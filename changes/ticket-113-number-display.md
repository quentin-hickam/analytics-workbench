### Changed

- Record audience precision and clock format from the user or audience defaults, present them at the headline checkpoint, and take a column's `[round]` places from it. Slide notes explain changes computed before rounding when rounded endpoints do not subtract to the shown change.
- A `[scale]` entry with `files = false` keeps chart and dataset cells in their recorded unit and records a separate `prose_scale` divisor for number tracing. Prose can use a scale word for a rounder approximation; sums still require recorded results.
