# Analytical implementation, validation, and evidence

Paths below that begin with `references/` or `assets/` are in the `awb-init` skill folder: `~/.claude/skills/awb-init/` (Claude Code) or `~/.agents/skills/awb-init/` (Codex).

## Structure

Put reusable operations in `src/`: `src/preparation/` for acquisition, landing, conversion, session loading, normalization, and corrections; `src/exploration/` for neutral measurements, comparisons, profiles, and graph operations; `src/packaging/` for shared package assembly. Reuse existing operations first. Each investigation's `run.py` selects shared operations and its `settings.toml` supplies scope and settings. An investigation without `run.py` gets one adapted from `assets/workbench/investigation/run.py` and `settings.toml` before its next rerun.

## Add a result

A new result is a `[results.<id>]` table in `settings.toml` holding the `question` it answers in the user's own words, never paraphrased; `answers = ["Q-NNN"]` when it answers ledger questions; its `[results.<id>.validation]` table; and a query in `queries/<id>.sql`. Add a producer to `run.py` only when a result needs more than its query. Read `references/validation.md` only to write a validation spec beyond the keys the settings comments list, and `references/provenance.md` only to adapt `run.py`'s evidence recording or to port it.

Specify four mechanical checks: required columns; plausible counts before and after each filter; joins without unexpected multiplication, inspecting key uniqueness whenever counts change; and null rates for important fields. Supply three judgments, each an outcome with a one-sentence detail: scope (explicit date filters and grouping dimensions), metrics (definitions, assumptions, and column meanings), and values (distinct values that drive business interpretation, inspected with `awb.py profile`).

Result queries use a stable total `ORDER BY`, with tie-breakers, so an unchanged result saves an identical table.

Before rerunning a supported or flagged finding, suggest committing its evidence. Run `python3 investigations/<name>/run.py [result-id ...]`. It writes each row and prints one JSON line per result with the evidence path, `failed_checks`, `not_assessed`, and `state`: a new result gets a `provisional` placeholder; a rerun with unchanged table, checks, and settings keeps its row; any other makes it `provisional` unless superseded, logging a supported one in history. When a result declares `answers`, the run marks those ledger questions answered and lists them under `questions`; declaring or changing `answers` computes nothing and makes no result stale, and `awb.py questions answer Q-NNN --result <id>` links one already recorded. Validation is done when each `failed_checks` entry is understood and recorded, and each `not_assessed` entry is either supplied in settings or justified with a caveat. Word, promote, supersede, or caveat with `awb.py state finding <id>... --text --status --reason --caveat` in one call. Before re-promoting, check the interpretation-driving values, which supported finding text includes, and the prior caveats in the rerun's history entry. Notes explain failed or not-assessed checks only for the checks they were written against: when a rerun changes those checks, promotion is refused until `--caveat` restates the notes that still hold.

## Claim strength

Each finding's Claim is the strongest wording it supports, and a new result starts at `association`. Set `descriptive` when the result only describes, such as a level, share, or trend: `awb.py state finding <id> --claim descriptive --reason "<why>"`. Correlations, group differences, and contrary groups from exploration or `run.py` stay `association` at most. Set `causal` only for a result whose design identifies the effect, naming that design: `--claim causal --basis "experiment: <design>"` or `--basis "natural experiment: <design>"`. A claim change writes history; a flagged finding's claim can only be lowered. `check-draft` refuses causal wording above a finding's claim.

## Rerun flagged findings

`awb-clean` makes shared corrections and flags the findings they affect. To rerun flagged findings on request, pass their result IDs, from each Evidence link, to `run.py`; it returns each to `provisional`, or `superseded` if it was, refreshes its check segments, keeps its notes, and moves the flag reason to `history.md`. If `run.py` cannot reproduce a flagged finding, extend `run.py` first.
