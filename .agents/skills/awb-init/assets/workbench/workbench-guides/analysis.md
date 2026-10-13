# Analytical implementation, validation, and evidence

The `references/` and `assets/` paths below are in the `awb-init` skill folder: `~/.claude/skills/awb-init/` (Claude Code) or `~/.agents/skills/awb-init/` (Codex).

## Structure

Put reusable operations in `src/`:

- `src/preparation/` for acquisition, landing, conversion, session loading, normalization, and corrections.
- `src/exploration/` for neutral measurements, comparisons, profiles, and graph operations.
- `src/packaging/` for shared package assembly.

Reuse existing operations first. The `run.py` of each investigation selects shared operations, and its `settings.toml` supplies scope and settings. An investigation without `run.py` gets one before its next rerun, adapted from `assets/workbench/investigation/run.py` and `settings.toml`.

## Add a result

A new result is a `[results.<id>]` table in `settings.toml`, its `[results.<id>.validation]` table, and a query in `queries/<id>.sql`. Add a producer to `run.py` only when a result needs more than its query. Read `references/validation.md` only to write a validation spec beyond the keys that the settings comments list. Read `references/provenance.md` only to adapt the evidence recording of `run.py` or to port it.

Specify four mechanical checks:

- Required columns.
- Plausible counts before and after each filter.
- Joins without unexpected multiplication. Whenever counts change, examine key uniqueness.
- Null rates for important fields.

Supply three judgments. Each judgment is an outcome with a one-sentence detail:

- Scope: explicit date filters and grouping dimensions.
- Metrics: definitions, assumptions, and column meanings.
- Values: distinct values that drive business interpretation, examined with `awb.py profile`.

Result queries use a stable total `ORDER BY`, with tie-breakers, so that an unchanged result saves an identical table.

Before you rerun a supported or flagged finding, suggest a commit of its evidence. Run `python3 investigations/<name>/run.py [result-id ...]`. It writes each row. For each result, it prints one JSON line with the evidence path, `failed_checks`, `not_assessed`, and `state`:

- A new result gets a `provisional` placeholder.
- A rerun with an unchanged table, checks, and settings keeps its row.
- Any other rerun makes the row `provisional`, unless it is superseded. If the row was supported, the rerun logs it in history.

Validation is complete when these conditions are true:

- Each `failed_checks` entry is understood and recorded.
- Each `not_assessed` entry is supplied in settings or justified with a caveat.

To word, promote, supersede, or caveat, use `awb.py state finding <id>... --text --status --reason --caveat` in one call. Before you promote a finding again, check the interpretation-driving values, which supported finding text includes. Also check the prior caveats in the history entry of the rerun. Notes explain failed or not-assessed checks only for the checks that they were written against. When a rerun changes those checks, promotion is refused until `--caveat` restates the notes that still apply.

## Rerun flagged findings

`awb-clean` makes shared corrections and flags the findings that they affect. To rerun flagged findings on request, pass their result IDs to `run.py`. Get each result ID from its Evidence link. For each finding, `run.py` does these steps:

- It returns the finding to `provisional`, or to `superseded` if it was superseded.
- It refreshes its check segments.
- It keeps its notes.
- It moves the flag reason to `history.md`.
 If `run.py` cannot reproduce a flagged finding, extend it first.
