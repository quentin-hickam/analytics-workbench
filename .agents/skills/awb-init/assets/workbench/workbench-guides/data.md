# Data acquisition, retention, and preparation

Paths are relative to the workbench root; existing project layouts remain authoritative. For helper setup, signatures, and examples, read the installed `awb-init` skill's `references/landing.md`. Import the project helper, preserving customizations; inspect its implementation only when adapting or debugging it.

## Assess and acquire

Assess candidate sources from their landed copies only far enough to establish relevance and fitness; record the assessment in `foundation/sources.md`. For an irrelevant source, record why and stop.

Acquire through `land()` in `src/preparation/landing.py`; source-specific code is the `fetch` callable. The default directory is `data/raw/<source>/<acquisition-id>/`, holding every original file or page byte for byte plus `provenance.json`. The helper stages in `<acquisition-id>.partial/`, records checksums and caller-supplied record counts, and renames only on completion. Failed attempts retain the suffix or are deleted, receive no Acquisitions row, and are noted in the source row. User-supplied files are acquisitions too; CSV and JSON are valid landed formats.

## Retain originals

`data/raw/` is excluded from Git, and acquisitions may be impossible to fetch again. Before the first landing, if README's `Landed data is kept at` line is absent or `not yet recorded`, ask for an external retention location and record it there. Insert a missing line directly after `Active investigation`, preserving other lines. If declined, record `none chosen`; warn after each landing that originals exist only in this checkout. Record a location whenever the user provides one.

After each landing, call `retain()` when that location is a reachable filesystem path; it copies to `<location>/data/raw/<source>/<acquisition-id>/` without overwriting and reports conflicts and file-list/checksum discrepancies. Report conflicts. Otherwise specify exactly what to copy and where. The acquisition's `foundation/sources.md` row records the destination after discrepancy-free verification, or `this checkout only` until verified or the user confirms copying. When a location is recorded or changed, retain every acquisition missing a retained copy.

## Publish and prepare

Use `publish()` to convert landed inputs into validated Parquet. It stages in `data/parquet/<dataset>/<publication-id>.partial/`, runs supplied validation, records the conversion commit and cited acquisition checksums in `publication.json`, then renames beside existing publications. Each canonical DuckDB view names its publication; record it in the catalog. Switching publications is a deliberate preparation change. Remove superseded publications only when no reader needs them.

`session()` opens each process's own DuckDB session and loads `foundation/views/*.sql` in filename order; dependent definitions must sort after their inputs. `python3 src/awb.py sql <query.sql | "SQL">` runs a query in such a session and prints the first rows and the row count.

Preparation owns reusable parsing, normalization, checks, and corrections; record limitations and correction rationale in `foundation/quality.md`. EDA consumes canonical data, with population, periods, filters, exclusions, and assumptions local to the investigation. Preparation and EDA may iterate before cleaning finishes. Generally valid exploratory rules can be promoted into preparation and saved queries into `foundation/views/`.

For source profiling, run `python3 src/awb.py profile <view | query.sql | "SQL"> --out <path>.json` rather than ad hoc counting queries; it applies `profile()` from `src/exploration/validate.py`, and the installed `awb-init` skill's `references/validation.md` describes its output and large-result sampling.

## Storage and output

`data/cache/` is only for expensive, rebuildable results described in `foundation/catalog.md`. Audience-facing package exports are separate from intermediate computation. Parquet is a storage boundary, not a requirement to materialize every transformation; normalization and corrections may remain in views. Persistent DuckDB tables require a deliberate cataloged cache, preventing uncontrolled storage growth.

A justified alternate backend must preserve independent source landing and the preparation/EDA boundary. Add versioning, invalidation, or pipeline machinery only for a concrete need. Save complete inventories and verification details in files; surface counts, failures, and paths in chat.
