# Analytics workbench

This repository holds a shared data foundation and distinct investigations. Each investigation answers one business question. It reuses preparation logic, canonical data, and neutral analytical operations from the foundation.

Read [AGENTS.md](AGENTS.md) before analytical work. It defines the preparation, exploration, investigation, and packaging boundaries that this project uses.

Active investigation: none

Landed data is kept at: not yet recorded

Released packages are kept at: not yet recorded

## Where work belongs

- `foundation/` records sources, canonical datasets and views, shared data quality, and common vocabulary.
- `investigations/` keeps the brief, current state, meaningful history, settings, `run.py`, and local exploration of each question.
- `src/awb.py` runs the workbench helpers under `src/` as commands. `python3 src/awb.py --help` lists them. `requirements.txt` names the packages that they need, unless the project declares dependencies in a different location. `.awb-receipt.json` records the shipped files that the installer wrote, so that an upgrade can tell them from customized copies.
- `src/preparation/` holds acquisition, landing, conversion, session-loading, and reusable normalization and correction code when such code exists.
- `src/exploration/` holds neutral analytical operations when such code exists.
- `src/packaging/` holds shared package assembly code when such code exists.
- `data/raw/` holds independently landed originals when there is acquired data. It has one directory for each acquisition, with its `provenance.json`. It is excluded from Git, so the originals persist only where the project copies them. The `Landed data is kept at` line above records these locations.
- `data/parquet/` holds validated publications for the default batch workflow, each with its `publication.json`. Each canonical view names the publication that it reads.
- `data/cache/` holds only deliberate, rebuildable expensive results that are recorded in the foundation catalog.
- `deliveries/` holds package drafts and numbered releases, created only on a package request. It is excluded from Git, so the releases persist only where the project copies them. The `Released packages are kept at` line above records these locations.

Directories are created when they are necessary. For this reason, a new workbench can contain only the foundation records, the helpers under `src/`, and its first investigation.

## Data path

Acquired records are landed durably before canonical ingestion. Completed landed inputs are converted into validated Parquet, and the originals do not change. Then Git-managed SQL definitions expose canonical views in a DuckDB session. Each analytical process has its own DuckDB session. Analytical steps keep intermediate computation in the runtime or in views. They do not pass CSV files between steps.

## Resume work

Run `python3 src/awb.py state` to print two files of the active investigation:

- `brief.md` (scope and purpose)
- `state.md` (current and flagged findings, unresolved issues, and next steps)

The `history.md` of the investigation holds meaningful analytical decisions and superseded conclusions. Findings come from the `run.py` of the investigation, run with its `settings.toml`. For this reason, a rerun is a new run of `run.py`. Saved queries are in the `exploration/` of the investigation, and you rerun them by path.

## Asking for things

Name the workbench skill in a plain request:

- `awb-init` sets up the workbench and starts an investigation: "Use awb-init to start an investigation into why overtime rose in Q3."
- `awb-status` reports where things stand and what can be asked for next: "Use awb-status — where are we?"
- `awb-package` creates or revises a package's working draft: "Use awb-package to draft a package for this investigation."
- `awb-release` preserves a numbered release from the draft: "Use awb-release — mark the package delivered."
- `awb-clean` checks one dataset for errors and corrects them in the shared views: "Use awb-clean to clean the orders data."
- `awb-eda` explores one dataset for the active investigation: "Use awb-eda to explore the shifts view."
- `awb-init` repairs the workbench and brings it up to date after newer skills are installed: "Use awb-init to bring this workbench up to date."
