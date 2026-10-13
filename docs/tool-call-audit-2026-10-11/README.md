# Tool-call audit, 2026-10-11

This audit counts the agent tool calls that each standard workbench task takes when the agent follows its skill or guide as written. The tasks go from `awb-init` through a second release and a revalidation. The run used one synthetic project. The audit measures tool calls, failed runs, and user round trips. It does not measure tokens.

## Method

- **Dataset.** [make_sample_data.py](make_sample_data.py) (seed 7) writes `orders.csv` (2,412 rows) and `customers.csv` (400 rows). These files have seeded defects:
  - 12 exact duplicate rows
  - 83 `MM/DD/YYYY` dates among ISO dates
  - 35 `-999` amount sentinels
  - region case and whitespace variants
  - 24 orphan customer IDs
  - a `Y`/`N` text flag

  Return rates are different for each region by design, and West has the highest rate.
- **Question.** "Which regions drive the H1 2026 order return rate, and is West's return rate materially higher than the others?" The audience is operations leadership.
- **Execution.** The run used a fresh project under a scratch directory. The skills came from this repository's `.agents/skills/`. The run used Python 3.13 with duckdb 1.5.6 and pandas 3.0.6. Every helper ran for real. One shell call stood for one agent tool call. Each call was logged to [ledger.tsv](ledger.tsv) with its task and kind. `retry` rows mark a failed or refused run. These rows are not calls themselves.
- **Counting rules.** A skill load counts as one call. When one shell call writes more than one file, the writes count once under **calls**. The **per-file** column counts them as separate Write calls, which is what most hosts do. A read of a file that is already in context does not count. The Read-before-Edit that hosts make mandatory in a fresh session is not counted. User questions are counted separately in [user-round-trips.txt](user-round-trips.txt). The user's answers were simulated.
- **Session assumption.** The run is one long session. For this reason, each guide is read once, as AGENTS.md directs. The rerun task adds one read of `analysis.md` to model a new session.

## Results

| # | Task (entry point) | Calls | Per-file | Failed runs | User round trips | Avoidable calls |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | New project with a question (`awb-init`) | 13 | 13 | 0 | 1 | 0 |
| 2 | Land a user-supplied extract (data guide) | 8 | 8 | 1 | 1 | 2 |
| 3 | Publish two datasets, views, catalog (data guide) | 8 | 12 | 0 | 0 | 1 |
| 4 | Clean `orders`, first pass (`awb-clean`) | 8 | 8 | 0 | 1 | 1 |
| 5 | Explore `orders` (`awb-eda`) | 9 | 9 | 0 | 0 | 3 |
| 6 | Add a result, run, validate, promote (analysis guide) | 9 | 9 | 0 | 0 | 1 |
| 7 | Status (`awb-status`) | 2 | 2 | 0 | 0 | 0 |
| 8 | New package draft (`awb-package`) | 16 | 16 | 2 | 1 | 4 |
| 9 | First release, storage unrecorded (`awb-release`) | 7 | 7 | 1 | 1 | 4 |
| 10 | User-reported correction that flags a finding (`awb-clean`) | 9 | 9 | 0 | 0 | 2 |
| 11 | Narrative revision for the new flag (`awb-package`) | 9 | 12 | 1 | 0 | 2 |
| 12 | Release with a flagged finding (`awb-release`) | 5 | 5 | 0 | 1 | 2 |
| 13 | Rerun the flagged finding (analysis guide) | 4 | 4 | 0 | 0 | 0 |
| 14 | Resume (`state`) | 1 | 1 | 0 | 0 | 0 |
| 15 | Status after release (`awb-status`) | 2 | 2 | 0 | 0 | 0 |
| 16 | Repair, no upgrade pending (`awb-init`) | 5 | 5 | 0 | 0 | 0 |
| 17 | Start a related investigation (`awb-init`) | 8 | 8 | 0 | 1 | 0 |
| | User-requested commits | 10 | 10 | | | |
| | **Total** | **133** | **140** | **6** | **7** | **22** |

The 123 workflow calls (commits not included) average 7.2 per task. About 22 of them (18%) came from instruction gaps or helper behavior that the Findings section covers. Without those calls, the lifecycle takes about 101 calls.

Calls cluster in three places:

- **Packaging and release (tasks 8, 9, 11, 12): 37 calls, 30% of the workflow calls.** Four of the six failed runs occurred here. Also, 12 of the 22 avoidable calls occurred here.
- **Helpers that work in one call:** status (2), resume (1), rerun (4), and repair (5) stay small because a single collector or command does the work.
- **Cleaning matches its own estimate.** The skill says "a typical pass is six tool calls". The first pass took 8: the six steps, the skill load, and the first-time read of `correction-views.md`.

## Findings

The findings are in order of calls saved. Each finding gives the observed cost and a proposed fix.

### F1. A release with no flags is refused because `revalidation_flags` is missing (task 9, 3 calls)

`export` creates the manifest without `revalidation_flags`. `awb-package` step 4 says to record every flagged finding. With no flags, there is nothing to record. `check-draft` printed `passed: true`. Then `release` refused with `flagged findings without a release disposition` and `revalidation_flags is missing; record none or each flag`. But `state.md` flagged nothing. Recovery took three calls: read the manifest, edit it, and rerun `release`. The refusal names the wrong cause. This makes the problem look more serious than it is.

**Fix:** do one of these:

- When `state.md` flags nothing, have `export` write `revalidation_flags: "none"`.
- Have `check-draft` fail on the missing field, so that the problem is caught inside `awb-package`.

### F2. Display names are discovered only when `export` fails (task 8, 4 calls)

For every exported column, `export` needs a display name in `foundation/display.toml`. No step creates that file or shows its format. Also, the glossary that is the intended source for that file did not exist yet. Recovery took four calls: the failed export, a format lookup through `--help`, the file write, and the rerun. The skill's sequence also writes `findings.md` before `export`. As a result, the chart's **Data:** line names columns before their display headers exist. `check-draft` then flagged `return_rate`, `ci_low`, and `ci_high` as internal names. This cost an edit and a second `check-draft`.

**Fix:** add a step that settles display names in `display.toml` before the agent writes. Give a two-line example of `[columns]` in this step. Have the export error print a ready-to-paste stub for the missing names.

### F3. A revision for a flagged finding is told to stop on `exports_blocked` (task 11, 1 call plus a possible dead end)

Step 4 says to pass one `--chart` for each chart specification. It also says to stop and report when `export` reports `exports_blocked`. With a flagged result, `--chart` is always blocked. The route that works is `export --result <id>`. This route refreshes provenance and keeps the chart files. That route appears only as a clause in the middle of a paragraph. An agent that follows the stop instruction ends the revision, and the release can never proceed.

**Fix:** state the branch directly: when a represented result is flagged, run `export` with `--result` only.

### F4. The release storage question comes after the release (task 9, 1 call)

The README says that `awb-release` asks where releases are kept before the first release. But the skill asks after `release` runs. As a result, `copy-releases` is necessary as one more call. In task 12, the location was already recorded, and `release` copied the release itself.

**Fix:** check the README storage line in step 1, and ask at that time. Then the first `release` also copies.

### F5. The disposition is asked only after another refused release (task 12, 2 calls)

The revision recorded the flag with disposition `none`. Then release refused, the user was asked, the manifest was edited, and release ran again. The user is present during the revision.

**Fix:** have `awb-package` ask for the disposition when it records a represented flag. As a separate change, prefill `revalidation_flags` entries from `state.md` in `export`. In this run, the `reason` string had 240 characters, and it was necessary to copy it verbatim by hand. An exact match decides if the release proceeds.

### F6. `land` fails its ledger write when `foundation/sources.md` is absent (task 2, 2 calls)

The guide puts the assessment (recorded in `sources.md`) before landing. When a user hands over files, it is natural to skip the assessment. `land` copied and retained the files. But it exited 1 with `Missing …/foundation/sources.md`, and the message did not say how to recover. After the file was created, `retain` wrote the row. But it reported `conflict: true` for the identical copy that `land` already made. This cost a `diff` to verify. `retain --help` documents that a matching destination can still report a conflict. But the output does not say so.

**Fix:** if `sources.md` is missing, have `land` create it from the template. Have `retain` compare an existing destination and report `matched`, not `conflict`.

### F7. No path for a correction the scan no longer surfaces (task 10, 2 calls)

The user changed the decision on an issue that was already corrected (Q-004: the old decision set `-999` values to null, and the new decision drops the test-order rows). The rescan shows only open and recorded issues with counts. As a result, Q-004 had no `S<n>`. `record_cleaning.py` accepted a flags-only payload, and this payload correctly flagged the finding. But the quality row could not be updated. The update needed a `--help` lookup and a hand edit of `quality.md`.

**Fix:** let `record_cleaning.py` accept `Q-<n>` keys to revise a recorded row and append a correction row.

### F8. The `state` list subcommands are undocumented where they are used (task 5, 3 calls)

`awb-eda` step 5 says to add Unresolved issues and Next steps items, but it does not name the commands. AGENTS.md names `state issues` and `state next` without arguments. Two `--help` calls were necessary. Then the update of both lists took two calls, because each subcommand edits one list.

**Fix:** show `state next --add TEXT --drop N` and `state issues --add TEXT` in the eda step. Optionally, accept both lists in one call.

### F9. Minor single calls

- **Publish (task 3):** neither `publish` nor the data guide shows a view definition. The one-line `CREATE VIEW … read_parquet(…)` pattern is only in `awb-clean`'s `correction-views.md`. A `view_sql` line printed next to `catalog_row` will remove the lookup.
- **Clean (task 4):** step 5 runs `stale` even when no investigation has findings. It is possible to skip this step when every `state.md` findings table is empty.
- **Analysis (task 6):** `analysis.md` names `--text --status --reason` together, but it gives `--caveat` separately. As a result, one `state finding --help` call was spent to confirm that all four combine in one call.

## What worked

- **Single-call helpers do their job.** `collect_status.py`, `state`, `run.py`, `record_cleaning.py`, `check-draft`, and `release` each did the work of several reads and edits. Status took 2 calls in both states.
- **The cleaning scan.** It found every seeded defect in one call. The rescan's delta resolved all eleven corrected issues and did not change the two decided issues.
- **Flag and rerun.** The flag-to-rerun loop (tasks 10 and 13) worked as specified. `stale` named the changed view. The flag went into `state.md`, and `run.py` cleared it with a history entry.
- **Narrow reads.** Reads stayed narrow. No task read another investigation's conclusions, a helper's source, or a guide twice.

## Limits

- **Single run.** This is one run by one agent that knew the repository. It is not the matched baseline-versus-revised comparison in [token-efficiency.md](../token-efficiency.md). An agent that is new to the skills will probably use more lookup calls. No token, cache, or reasoning telemetry was recorded.
- **Simulated user.** User answers were simulated. Each round trip assumed an immediate, complete answer.
- **Counting assumptions.** Counts assume that calls are batched where a skill says "in one call". Per-file Write calls increase the total from 133 to 140.
- **Out of scope.** The run did not exercise API acquisition through `fetch`, a dataset selection other than `none`, an upgrade with customized files, or M365 assembly.

## Reproduce

```sh
python3 docs/tool-call-audit-2026-10-11/make_sample_data.py <inbox-dir>
```

Then follow the tasks in the order of [ledger.tsv](ledger.tsv). Use the project's interpreter, with duckdb and pandas in it.
