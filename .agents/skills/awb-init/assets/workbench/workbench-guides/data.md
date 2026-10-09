# Data acquisition, retention, and preparation

Existing project layouts remain authoritative. Read `references/landing.md` only to write a `fetch` callable for `land()` or a `convert` callable for `publish()`.

## Assess and acquire

Assess candidate sources from their landed copies only far enough to establish relevance and fitness, and record the assessment in `foundation/sources.md` under its Status rules.

Land user-supplied or already-downloaded files:

```
python3 src/awb.py land <source> <acquisition-id> <file-or-directory>... [--request TEXT] [--records NAME=COUNT] [--notes TEXT]
```

For an API or other fetched source, save the fetch as `src/preparation/fetch_<source>.py`, calling `land()` from `src/preparation/landing.py` with a `fetch` callable; run it by path, then run `python3 src/awb.py retain`.

## Retain originals

`data/raw/` is excluded from Git, and acquisitions may be impossible to fetch again. Before the first landing, if README's `Landed data is kept at` line is absent or `not yet recorded`, ask for an external retention location and record it there, inserting a missing line directly after `Active investigation`. If the user declines, record `none chosen` and warn after each landing that originals exist only in this checkout. Record a location whenever the user provides one.

`land` and `retain` copy to a reachable filesystem location and write the Acquisitions row themselves; report any conflict or discrepancy they print verbatim. For any other location, tell the user exactly what to copy where, and record the destination once the copy is verified or the user confirms it. After recording or changing a location, run `python3 src/awb.py retain`. Fill each new row's Restrictions yourself.

## Publish and prepare

Save the conversion as `src/preparation/<dataset>.sql`, one SELECT reading landed files by project-relative path, and its check as `src/preparation/<dataset>-check.sql`, a query over the view `publication` whose returned rows are failures. Suggest committing both first so the publication's `conversion_commit` holds them. Then publish:

```
python3 src/awb.py publish <dataset> <publication-id> --from <acquisition-dir> --sql <select.sql> --check <check.sql>
```

`--from` names exactly the acquisition directories the select reads. Each canonical view in `foundation/views/` names its publication; record it in `foundation/catalog.md`, starting from the printed `catalog_row`. Switching publications is a deliberate preparation change. Remove a superseded publication once no reader needs it.

Sessions load `foundation/views/*.sql` in filename order, so a dependent view's file sorts after its inputs.

Preparation owns reusable parsing, normalization, checks, and corrections; their rationale goes in `foundation/quality.md`. EDA consumes canonical data, with population, periods, filters, exclusions, and assumptions local to the investigation; preparation and EDA may iterate before cleaning finishes. Promote a generally valid exploratory rule into preparation, or a saved query into `foundation/views/`, deliberately.

## Storage

Materialize only publications and cataloged caches of expensive, rebuildable results in `data/cache/`; normalization and corrections stay in views. A justified alternate backend preserves independent source landing and the preparation/EDA boundary. Add versioning, invalidation, or pipeline machinery only for a concrete need.
