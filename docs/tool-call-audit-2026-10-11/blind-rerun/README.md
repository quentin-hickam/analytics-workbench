# Blind Codex rerun, 2026-10-13

On 2026-10-13 the audit was rerun blind, twice, by Codex (gpt-6.1-sol, codex-cli 0.159.3). One run used the skills at `2c9d939`, before the fixes. The other used them at `649e41a`, after the fixes. Each run had only an installed-skills folder from its revision, the same sample data (seed 7), a Python interpreter with duckdb, and [the same brief](BRIEF.template.md). The brief held 16 user requests and simulated answers. The runs had no repository, helper source, tests, or audit documents. Calls are counted from the Codex session records, not from the agent's own report. Each shell command carried a `: task=N` tag so it could be attributed to a request.

A first attempt at both runs is void. The Python wrapper was a symlink, so the venv's packages did not load and duckdb was missing.

## Counts

Codex batches several shell commands into one tool call, often across two requests. Commands are therefore the comparable unit. [per-command.tsv](per-command.tsv) attributes each command to its own request, and [tool-calls-baseline.tsv](tool-calls-baseline.tsv) and [tool-calls-fixed.tsv](tool-calls-fixed.tsv) give the batched tool calls.

| | Before fixes | After fixes | Change |
| --- | ---: | ---: | ---: |
| Shell commands | 67 | 59 | −8 (−12%) |
| Tool calls (model round trips) | 41 | 40 | −1 |
| Tokens used | 158,172 | 144,888 | −8.4% |
| User questions logged | 11 | 9 | −2 |

The savings fall on the requests the fixes targeted:

| Request | Before | After | Change |
| --- | ---: | ---: | ---: |
| 8. Package draft | 6 | 3 | −3 |
| 9. First release | 3 | 2 | −1 |
| 10. Correction to a recorded issue | 4 | 3 | −1 |
| 11. Release with a flagged finding | 4 | 3 | −1 |
| 12. Rerun the flagged finding | 4 | 2 | −2 |
| Commits | 12 | 10 | −2 |
| 4. Clean orders | 5 | 7 | +2 |

The +2 on request 4 comes from an agent error: a `--range` on a categorical column. It is noise rather than a regression. With one run per arm, a difference of ±1 on a single request is within run-to-run variation. Only the differences that the reports explain should be relied on.

## What the reports show

### Fixes confirmed

- **F7, revising a recorded issue by its quality ID.** Before the fixes, the agent consulted the scanner and recorder `--help`, scanned the publication separately to find the hidden `-999` values, added a new issue Q-015, and superseded Q-004 by hand. After the fixes it updated Q-004 directly, because "record_cleaning explicitly supports addressing a prior issue by its quality ID".
- **F4, release storage.** Before the fixes, the storage question came after release 001, so `copy-releases` was needed. After the fixes the location was recorded first, and `release` copied the release itself.
- **F9a, the printed view definition.** After the fixes, the printed `view_sql` and `catalog_row` "supplied the view/publication paths". No lookup was needed.
- **F3 and F5, flagged releases.** After the fixes, request 11 ran `--result` only. The agent asked one disposition question that listed every place the flagged finding appears, then released once.

### Fixes this agent did not need

Codex avoided F1 (release refused for a missing `revalidation_flags`) and F2 (missing display names) on the pre-fix skills as well. Before the first release it wrote `revalidation_flags: "none"` into the manifest by hand, reading the contract's "`none` or one entry per finding". It also reported no export failure for display names. Those fixes protect a less careful agent; the Claude run in the original audit hit both. F6 did not arise in either run, because both agents created `sources.md` during initialization.

### New problems found in both runs

1. **`record_cleaning.py` refused both first recording attempts with `several rows are named orders`.** `publish` prints a `catalog_row` named after the dataset, and the canonical view uses the same name, so following the printed row creates two catalog rows that record_cleaning cannot tell apart. Both agents recovered by renaming the publication rows to `orders-publication`. **Fixed afterwards:** `record_cleaning.py` now sets the canonical view's row when a publication row has the same name.
2. **Status cannot tell when a package predates a rerun.** After request 12 reran and re-promoted the finding, `awb-status` still reported `draft_vs_release: same_or_older` and no blockers, although the draft and release 002 carry the old figures. Both agents noticed and reported it from the next-steps record only. **Fixed afterwards:** `awb-status` reports `rerun_since_draft`, the represented results whose evidence is newer than the draft. On a copy of the post-fix run's project, it lists `region-rates`.
3. **`install_helpers.py` exits with `"workbench": false` when run before the root files exist.** Both agents ran it before writing README and AGENTS.md, then reran it. awb-init lists the steps in the right order, but the installer's output does not say what is missing.
4. **`check-draft` flagged ordinary prose as a path** (before the fixes only): "yes/no" at line 73 was read as one. This is a false positive in the internal-name check.

### Not a skill problem

Both agents flagged a conflict between `awb-package`'s instruction to read `run.py` and the brief's rule against opening `.py` files. That rule belongs to this exercise, not to the skills.

## Reports

- [codex-report-baseline.md](codex-report-baseline.md) and [codex-report-fixed.md](codex-report-fixed.md) are each agent's own account.
- [roundtrips-baseline.txt](roundtrips-baseline.txt) and [roundtrips-fixed.txt](roundtrips-fixed.txt) list the questions each agent logged for the user.
- [count_calls.py](count_calls.py) and [per_command.py](per_command.py) count calls and commands from a rollout file under `~/.codex/sessions/`.

The Codex session ids were `01a135b3-97e1-74a0-8db9-4fc14bbc8993` (before the fixes) and `01a135b3-97e1-7301-93c6-bca58e8f4b89` (after).
