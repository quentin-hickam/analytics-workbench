# Data acquisition, retention, and preparation

The `references/` and `assets/` paths below are in the `awb-init` skill folder: `~/.claude/skills/awb-init/` (Claude Code) or `~/.agents/skills/awb-init/` (Codex).

Existing project layouts stay authoritative. Read `references/landing.md` only to write a `fetch` callable for `land()` or a `convert` callable for `publish()`.

## Assess and acquire

If the documentation or schema of a candidate settles its relevance and fitness, assess the candidate from that documentation or schema. Examine records only from landed copies. Land only what the assessment needs. Record the assessment and its basis in `foundation/sources.md`, under its Status rules.

Land user-supplied or already-downloaded files:

```
python3 src/awb.py land <source> <acquisition-id> <file-or-directory>... [--request TEXT] [--records NAME=COUNT] [--notes TEXT]
```

For an API or other fetched source, save the fetch as `src/preparation/fetch_<source>.py`. Make this script call `land()` from `src/preparation/landing.py` with a `fetch` callable. Run the script by path. Then run `python3 src/awb.py retain`.

## Retain originals

`data/raw/` is excluded from Git, and it is possible that you cannot fetch acquisitions again. Before the first landing, examine the `Landed data is kept at` line of README. If it is absent or `not yet recorded`, ask for an external retention location and record the location in that line. If the line is missing, insert it directly after `Active investigation`. If the user declines, record `none chosen`. Then, after each landing, warn that the originals exist only in this checkout. Whenever the user gives a location, record it.

`land` and `retain` copy to a reachable filesystem location and write the Acquisitions row themselves. If they print a conflict or discrepancy, report it verbatim. For any other location:

- Tell the user exactly what to copy where.
- After the copy is verified or the user confirms it, record the destination.

After you record or change a location, run `python3 src/awb.py retain`. Fill the Restrictions of each new row yourself.

## Publish and prepare

Save the conversion as `src/preparation/<dataset>.sql`. The conversion is one SELECT that reads landed files by project-relative path. Save its check as `src/preparation/<dataset>-check.sql`. The check is a query over the view `publication`, and each row that it returns is a failure. First, suggest a commit of the two files, so that the `conversion_commit` of the publication holds them. Then publish:

```
python3 src/awb.py publish <dataset> <publication-id> --from <acquisition-dir> --sql <select.sql> --check <check.sql>
```

`--from` names exactly the acquisition directories that the select reads. Each canonical view in `foundation/views/` names its publication. Record it in `foundation/catalog.md`, and start from the printed `view_sql` and `catalog_row`. A change from one publication to a different one is a deliberate preparation change. When no reader needs a superseded publication, remove it.

Sessions load `foundation/views/*.sql` in filename order, so the file of a dependent view sorts after its inputs.

Preparation owns reusable parsing, normalization, checks, and corrections. Their rationale goes in `foundation/quality.md`. EDA uses canonical data, and its population, periods, filters, exclusions, and assumptions are local to the investigation. Preparation and EDA can iterate before cleaning finishes. Deliberately promote a generally valid exploratory rule into preparation, or a saved query into `foundation/views/`.

## Storage

Materialize only publications and cataloged caches of expensive, rebuildable results in `data/cache/`. Normalization and corrections stay in views. A justified alternate backend keeps independent source landing and the preparation/EDA boundary. Add versioning, invalidation, or pipeline machinery only for a concrete need.
