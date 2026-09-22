# Analytics workbench

This repository holds a shared data foundation and distinct investigations. Each investigation answers one business question while reusing preparation logic, canonical data, and neutral analytical operations from the foundation.

Read [AGENTS.md](AGENTS.md) before analytical work. It defines the preparation, exploration, investigation, and delivery boundaries used in this project.

Active investigation: none

## Where work belongs

- `foundation/` records sources, canonical datasets and views, shared data quality, and common vocabulary.
- `investigations/` keeps each question's brief, current state, meaningful history, settings, and local exploration.
- `src/preparation/` holds reusable normalization and correction logic when such code exists.
- `src/exploration/` holds neutral analytical operations when such code exists.
- `src/packaging/` holds shared package assembly code when such code exists.
- `data/raw/` holds independently landed originals and acquisition provenance when data has been acquired.
- `data/parquet/` holds validated published datasets for the default batch workflow.
- `data/cache/` holds only deliberate, rebuildable expensive results recorded in the foundation catalog.
- `deliveries/` is created only through an explicit packaging request. It is excluded from Git, so numbered releases persist only where the project copies them; record that location here once chosen.

Directories are created when needed, so a new workbench may contain only the foundation records and its first investigation.

## Data path

Acquired records are landed durably before canonical ingestion. Completed landed inputs are converted into validated Parquet without changing the originals, then Git-managed SQL definitions expose canonical views in each analytical process's own DuckDB session. Analytical steps keep intermediate computation in the runtime or views rather than passing CSV files between steps.

## Resume work

Open the active investigation's `state.md` for current findings, unresolved issues, revalidation flags, and next steps. Use its `brief.md` for scope and purpose, and `history.md` for meaningful analytical decisions and superseded conclusions.
