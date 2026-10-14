# Data acquisition, retention, and preparation

`references/` and `assets/` paths below are in the `awb-init` skill folder: `~/.claude/skills/awb-init/` (Claude Code) or `~/.agents/skills/awb-init/` (Codex).

Existing project layouts remain authoritative. Read `references/landing.md` only to write a `fetch` callable for `land()` or a `convert` callable for `publish()`.

## Assess and acquire

Assess a candidate from its documentation or schema when that settles relevance and fitness; inspect records only from landed copies, landing only what the assessment needs. Record the assessment and its basis in `foundation/sources.md` under its Status rules.

Land user-supplied or already-downloaded files:

```
python3 src/awb.py land <source> <acquisition-id> <file-or-directory>... [--request TEXT] [--records NAME=COUNT] [--notes TEXT]
```

For an API or other fetched source, save the fetch as `src/preparation/fetch_<source>.py`, taking the acquisition ID as its argument and calling `land()` from `src/preparation/landing.py` with a `fetch` callable and the upstream URL, without credentials, and validators it receives; run it by path with a new acquisition ID, then run `python3 src/awb.py retain`. Land a changed upstream again under a new acquisition ID, only on request; rerunning analysis never re-lands.

Fetch scripts read credentials from environment variables; local values may sit in the gitignored `.env`, loaded by the shell or a loader the project declares. List each variable's name, without its value, in a tracked `.env.example`, created with the first one. Secrets never go in `settings.toml`, saved SQL, `request` or `notes` values, or foundation ledger rows. Saved SQL names no credential at all; the others record the variable's name instead, as `$NAME`.

## Retain originals

`data/raw/` is excluded from Git, and acquisitions may be impossible to fetch again. Before the first landing, if README's `Landed data is kept at` line is absent or `not yet recorded`, ask for an external retention location and record it there, inserting a missing line directly after `Active investigation`. If the user declines, record `none chosen` and warn after each landing that originals exist only in this checkout. Record a location whenever the user provides one.

`land` and `retain` copy to a reachable filesystem location and write the Acquisitions row themselves; report any conflict or discrepancy they print verbatim. For any other location, tell the user exactly what to copy where, and record the destination once the copy is verified or the user confirms it. After recording or changing a location, run `python3 src/awb.py retain`. Fill each new row's Restrictions yourself.

## Publish and prepare

Save the conversion as `src/preparation/<dataset>.sql`, one SELECT reading landed files by project-relative path. Declare the dataset's checks (columns and types, not-null, key and uniqueness, accepted values, ranges, row count) under `[datasets.<dataset>.checks]` in `foundation/datasets.toml`, starting from `assets/workbench/foundation/datasets.toml`, which documents the keys. Put a check a declaration cannot express in `src/preparation/<dataset>-check.sql`, a query over the view `publication` whose returned rows are failures. Suggest committing these first so the publication's `conversion_commit` holds them. Then publish:

```
python3 src/awb.py publish <dataset> <publication-id> --from <acquisition-dir> --sql <select.sql> [--check <check.sql>]
```

`--from` names exactly the acquisition directories the select reads. `publish` runs the declared checks on every publication of the dataset and records each outcome in `publication.json`; a failing check refuses publication, and `failed_checks` names it. Each canonical view in `foundation/views/` names its publication. Start the view from the printed `view_sql`. In `foundation/catalog.md`, record the publication from the printed `catalog_row`, completing its grain and availability, and give the view its own row (Kind `canonical view`) with the view's grain and the publication it reads under `Inputs`. `awb-clean` reads the grain from the view's row and records corrections there. Switching publications is a deliberate preparation change. Remove a superseded publication, and its catalog row, once no reader needs it.

Sessions load `foundation/views/*.sql` in filename order, so a dependent view's file sorts after its inputs.

Preparation owns reusable parsing, normalization, checks, and corrections; their rationale goes in `foundation/quality.md`. EDA consumes canonical data, with population, periods, filters, exclusions, and assumptions local to the investigation; preparation and EDA may iterate before cleaning finishes. Promote a generally valid exploratory rule into preparation, or a saved query into `foundation/views/`, deliberately.

## Storage

Materialize only publications, under `data/parquet/`, and cataloged caches of expensive, rebuildable results, in `data/cache/`; normalization and corrections stay in views. A justified alternate backend preserves independent source landing and the preparation/EDA boundary. Add versioning, invalidation, or pipeline machinery only for a concrete need.
