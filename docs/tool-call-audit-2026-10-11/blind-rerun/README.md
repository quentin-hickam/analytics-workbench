# Blind Codex rerun, 2026-10-13

On 2026-10-13 Codex (gpt-6.1-sol, codex-cli 0.159.3) did two blind reruns of the audit. One run used the skills at `2c9d939`, before the fixes. The other run used the skills at `649e41a`, after the fixes. Each run had only these items:

- An installed-skills folder from the revision of that run.
- The same sample data (seed 7).
- A Python interpreter with duckdb.
- [The same brief](BRIEF.template.md).

The brief had 16 user requests and simulated answers. The runs had no repository, no helper source, no tests and no audit documents. The calls are counted from the Codex session records, not from the report of the agent. Each shell command had a `: task=N` tag, so that it was possible to attribute the command to a request.

A first attempt at both runs is void. The Python wrapper was a symlink. As a result, the packages of the venv did not load, and duckdb was missing.

## Counts

Codex batches several shell commands into one tool call. Often, these commands are for two different requests. For this reason, commands are the unit that we can compare. [per-command.tsv](per-command.tsv) attributes each command to its own request. [tool-calls-baseline.tsv](tool-calls-baseline.tsv) and [tool-calls-fixed.tsv](tool-calls-fixed.tsv) give the batched tool calls.

| | Before fixes | After fixes | Change |
| --- | ---: | ---: | ---: |
| Shell commands | 67 | 59 | −8 (−12%) |
| Tool calls (model round trips) | 41 | 40 | −1 |
| Tokens used | 158,172 | 144,888 | −8.4% |
| User questions logged | 11 | 9 | −2 |

The savings occur on the requests that the fixes targeted:

| Request | Before | After | Change |
| --- | ---: | ---: | ---: |
| 8. Package draft | 6 | 3 | −3 |
| 9. First release | 3 | 2 | −1 |
| 10. Correction to a recorded issue | 4 | 3 | −1 |
| 11. Release with a flagged finding | 4 | 3 | −1 |
| 12. Rerun the flagged finding | 4 | 2 | −2 |
| Commits | 12 | 10 | −2 |
| 4. Clean orders | 5 | 7 | +2 |

The +2 on request 4 comes from an agent error: a `--range` on a categorical column. This is noise, not a regression. There is only one run for each arm. As a result, a difference of ±1 on one request is in the normal variation from run to run. We recommend that you rely only on the differences that the reports explain.

## What the reports show

### Fixes confirmed

- **F7, revision of a recorded issue by its quality ID.** Before the fixes, the agent read the `--help` of the scanner and the recorder. It scanned the publication separately to find the hidden `-999` values. Then it added a new issue Q-015, and it superseded Q-004 manually. After the fixes, it updated Q-004 directly, because "record_cleaning explicitly supports addressing a prior issue by its quality ID".
- **F4, release storage.** Before the fixes, the storage question came after release 001, and as a result `copy-releases` was necessary. After the fixes, the location was recorded first, and `release` copied the release itself.
- **F9a, the printed view definition.** After the fixes, the printed `view_sql` and `catalog_row` "supplied the view/publication paths". No lookup was necessary.
- **F3 and F5, flagged releases.** After the fixes, request 11 ran `--result` only. The agent asked one disposition question. This question listed every place where the flagged finding appears. Then the agent released one time.

### Fixes this agent did not need

With the skills from before the fixes, Codex also avoided F1 (release refused for a missing `revalidation_flags`) and F2 (missing display names). Before the first release, it manually wrote `revalidation_flags: "none"` into the manifest. It used this text from the contract: "`none` or one entry per finding". It also reported no export failure for display names. Those fixes protect a less careful agent. The Claude run in the original audit had both problems. F6 did not occur in either run, because both agents created `sources.md` during initialization.

### New problems found in both runs

1. **`record_cleaning.py` refused the first recording attempt of each agent with `several rows are named orders`.** `publish` prints a `catalog_row` named after the dataset. The canonical view uses the same name. As a result, if an agent follows the printed row, it creates two catalog rows that record_cleaning cannot tell apart. To recover, both agents renamed the publication rows to `orders-publication`. **Fixed afterwards:** when a publication row has the same name, `record_cleaning.py` now sets the row of the canonical view.
2. **Status cannot tell when a package is older than a rerun.** After request 12 reran and re-promoted the finding, `awb-status` still reported `draft_vs_release: same_or_older` and no blockers. But the draft and release 002 have the old figures. Both agents found and reported this problem only from the next-steps record. **Fixed afterwards:** `awb-status` reports `rerun_since_draft`, that is, the represented results whose evidence is newer than the draft. On a copy of the project from the post-fix run, it lists `region-rates`.
3. **If you run `install_helpers.py` before the root files exist, it exits with `"workbench": false`.** Both agents ran it before they wrote README and AGENTS.md, and then ran it again. awb-init lists the steps in the correct order. But the output of the installer does not say what is missing.
4. **`check-draft` flagged ordinary prose as a path** (only before the fixes): it read "yes/no" at line 73 as a path. This is a false positive in the internal-name check.

### Not a skill problem

Both agents flagged a conflict between the instruction in `awb-package` to read `run.py` and the rule in the brief that forbids you to open `.py` files. That rule is part of this exercise, not of the skills.

## Reports

- [codex-report-baseline.md](codex-report-baseline.md) and [codex-report-fixed.md](codex-report-fixed.md) are the accounts that each agent wrote itself.
- [roundtrips-baseline.txt](roundtrips-baseline.txt) and [roundtrips-fixed.txt](roundtrips-fixed.txt) list the questions that each agent logged for the user.
- [count_calls.py](count_calls.py) and [per_command.py](per_command.py) count calls and commands from a rollout file under `~/.codex/sessions/`.

The Codex session ids were `01a135b3-97e1-74a0-8db9-4fc14bbc8993` (before the fixes) and `01a135b3-97e1-7301-93c6-bca58e8f4b89` (after).
