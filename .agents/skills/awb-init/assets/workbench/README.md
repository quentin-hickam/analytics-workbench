# Analytics workbench

This repository holds a shared data foundation and distinct investigations. Each investigation answers one business question while reusing preparation logic, canonical data, and neutral analytical operations from the foundation.

Read [AGENTS.md](AGENTS.md) before analytical work. It defines the preparation, exploration, investigation, and packaging boundaries used in this project.

Active investigation: none

Landed data is kept at: not yet recorded

Released packages are kept at: not yet recorded

Commits: on request

Code history: Git

Project interpreter: not yet recorded

## Where work belongs

- `foundation/` records sources, canonical datasets and views, shared data quality, common vocabulary, and the review rules every package review checks. `foundation/references/` keeps the third-party documentation those records rely on.
- `investigations/` keeps each question's brief, current state, question ledger (`questions.md`, rendered from `questions.json`), meaningful history, settings, `run.py` with a producer module for each result that needs more than its query, and local exploration.
- `src/awb.py` runs the workbench helpers under `src/` as commands: `python3 src/awb.py --help` lists them. `requirements.txt` names the packages they need unless the project declares dependencies elsewhere. `.awb-receipt.json` records the shipped files the installer wrote, so an upgrade can tell them from customized copies.
- `src/preparation/` holds acquisition, landing, conversion, session-loading, and reusable normalization and correction code when such code exists.
- `src/exploration/` holds neutral analytical operations when such code exists.
- `src/packaging/` holds shared package assembly code when such code exists.
- `data/raw/` holds independently landed originals when data has been acquired, one directory per acquisition with its `provenance.json`. It is excluded from Git, so originals persist only where the project copies them, recorded in the `Landed data is kept at` line above.
- `data/parquet/` holds validated publications for the default batch workflow, each with its `publication.json`; each canonical view names the publication it reads.
- `data/cache/` holds only deliberate, rebuildable expensive results recorded in the foundation catalog.
- `deliveries/` holds package drafts and numbered releases, created only on a package request. It is excluded from Git, so releases persist only where the project copies them, recorded in the `Released packages are kept at` line above.

Directories are created when needed, so a new workbench may contain only the foundation records and `foundation/references/`, the helpers under `src/`, and its first investigation.

## Data path

Acquired records are landed durably before canonical ingestion. Completed landed inputs are converted into validated Parquet without changing the originals, then Git-managed SQL definitions expose canonical views in each analytical process's own DuckDB session. Analytical steps keep intermediate computation in the runtime or views rather than passing CSV files between steps.

## Resume work

Run `python3 src/awb.py state` to print the active investigation's `brief.md` (scope and purpose), `state.md` (current and flagged findings, unresolved issues, and next steps), and its open ledger questions; `python3 src/awb.py questions list --all` prints every question it has raised, answered or not. Its `history.md` holds meaningful analytical decisions and superseded conclusions. Findings come from the investigation's `run.py` run with its `settings.toml`, so a rerun is running `run.py` again; saved queries live in the investigation's `exploration/` and are rerun by path.

## Asking for things

Name the workbench skill in a plain request:

- `awb-init` sets up the workbench for a first question: "Use awb-init to set up this project. The question is why overtime rose in Q3."
- `awb-scope` starts an investigation, digs into its question and the open questions behind it, or changes its scope: "Use awb-scope to start an investigation into why overtime rose in Q3." or "Use awb-scope — let's work through the open questions."
- `awb-brainstorm` proposes new questions from those already asked and answered: "Use awb-brainstorm — what else should we ask?"
- `awb-status` reports where things stand and what can be asked for next: "Use awb-status — where are we?"
- `awb-package` creates or revises a package's working draft: "Use awb-package to draft a package for this investigation."
- `awb-release` preserves a numbered release from the draft: "Use awb-release — mark the package delivered."
- `awb-clean` checks one dataset for errors and corrects them in the shared views: "Use awb-clean to clean the orders data."
- `awb-explore` explores one dataset for the active investigation: "Use awb-explore to explore the shifts view."
- `awb-init` repairs the workbench and brings it up to date after newer skills are installed: "Use awb-init to bring this workbench up to date."

The `Commits` line at the top says when the agent commits: `on request`, the default, means only when you ask, with a reminder at most once a session while analytical code is uncommitted; `as I go` means it commits analytical code as it works. Say "commit as you go" to switch. The `Code history` line reads `none (<reason>)` when the project has no Git repository; the agent then makes and suggests no commits, and evidence records file checksums instead of a commit.

The `Project interpreter` line names the Python that runs every workbench command, written by the helper installer; `python3` in the commands here means it, and `src/awb.py` switches to it when started by another. To switch interpreters, edit the line.
