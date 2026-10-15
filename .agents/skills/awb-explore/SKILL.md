---
name: awb-explore
description: "Explore one dataset for the active analytics workbench investigation. Use for \"look at this data\", \"explore this dataset\", \"profile this view\", or \"help me understand this data\" within the investigation's question."
---

# Explore a dataset for an investigation

Explore one canonical view or publication at a time, within the investigation's question and scope. This skill carries the analysis rules EDA needs; load `workbench-guides/analysis.md` only to turn a pattern into a finding. EDA writes only under `investigations/<name>/exploration/` and the records in step 5.

## 1. Frame

Use the investigation the user names, otherwise the README's active one; for one other than the active one, pass `--investigation <name>` to every `awb.py state` and `awb.py questions` command below. If its brief, state, and open ledger questions are not loaded, print them with `python3 src/awb.py state`. Say in a sentence or two which dataset you will explore and why it bears on the question. If several datasets fit, start with the one that holds the question's measure.

## 2. Scan

From the project root, with the interpreter that runs the project's analysis:

```sh
python3 <skill-directory>/scripts/eda_scan.py <project-root> <view-or-publication> [options]
```

Run this script unread. It reads scope, measure, and dimensions from the investigation's `settings.toml` (`[eda]`, with the period falling back to `[parameters]` `start` and `end`), writes the complete scan to `investigations/<name>/exploration/eda/<scan>[-<label>].json`, and prints a compact summary that names the file. `<scan>` is the dataset's name made safe for a file name, such as `shifts-p1` for `data/parquet/shifts/p1`; [the scan file](references/scan-file.md) gives the exact rule. A new investigation's settings usually name no date column, measure, or dimensions, so pass them in the first run: the brief's population as `--where`, its date column as `--date-column` (with `--start` and `--end` when settings hold no period), the question's measure and grouping columns as `--measure` and `--dimension` (repeatable), and the grain on the dataset's catalog row (the view's row for a canonical view) as `--key`, given once, as one comma-separated value for a composite grain. When the brief's population is held open by ledger ID, scan with `--no-scope` and without `--where`, and report the population as unsettled. A `not set` line names any scope or measure option still missing, and a `not applied` line names a setting that does not fit the dataset. Pass exploratory choices as options; settings change only when the user settles a population or period choice. `--help` lists the other options, such as `--label` for a second scope, and the settings keys. Exit status 2 prints the fix; apply it and run again.

One scan per dataset and scope is final, and its printed summary is the result. To open one part of the saved file, print it with `--show`, such as `--show columns.<column>.top` or `--show measure.by_dimension.<dimension>.values`; read [the scan file](references/scan-file.md) to find any other section.

## 3. Read the scan

Check in order:

- **Scope.** Are the rows before and after the filters plausible? Does a `not set` or `not applied` line, or an unread settings key, mean the population differs from the brief's? If so, scan again with the missing options and say so.
- **Grain.** Do the candidate keys match the grain on the dataset's catalog row, the declared key passed in step 2? Check duplicates and any declared-key violation or missing column.
- **Anomalies.** Give every printed anomaly one disposition: a shared data problem, confirmed by a follow-up query or the source register before the step 5 hand-off; a local analytical matter; or dismissed with a reason. The `route` column is the scan's guess, not the disposition.
- **Relationships.** Read variance explained, the trend, the measure's correlations, and **contrary** groups. Variance explained rises with group count, and a trend where a high-variance dimension's shares shift may be mix rather than change. Name candidate explanations and keep every contrary pattern. These are associations: a finding built on them is worded as one, never as a cause.

Read [reading the scan](references/reading-the-scan.md) for an anomaly kind's confirmation check, or when a data problem and a real pattern are hard to tell apart. Draft the observations that bear on the question, labeled exploratory, with candidate explanations and contrary patterns, for the report.

## 4. Follow up with saved queries

Run one follow-up for each anomaly you are confirming as a shared data problem and each candidate explanation the user's question turns on; leave the rest as ledger questions. The step is done when every observation you report is either settled by a saved query or recorded as a ledger question.

Write each follow-up as `investigations/<name>/exploration/<topic>.sql` and run it from the project root with `python3 src/awb.py sql <path>`. Start each file with a comment naming the question it serves and its scope, and copy every printed scope filter, period included, into its `WHERE`. Aggregate, order, and limit in SQL so the printed table stays short. To separate mix from within-group change, compute each group's share and mean per period in one query; a moving overall mean over stable group means is a mix shift. Revise and rerun the same file rather than adding variants; save even a one-off, since the report cites its path. Draw an exploratory chart only on request, saved under `exploration/`.

## 5. Record what was learned

- **Questions.** Add each consequential pattern or candidate explanation not yet tested through `run.py` to the ledger as a data question, unless an open one already asks it: `python3 src/awb.py questions add "<question>" --kind analytical --answerer data --origin eda --unblocks "<what it bears on>"`. A pattern becomes a finding, and its question answered, only through `run.py`. A question only the user or a stakeholder can settle, such as whether a pattern is expected, takes `--answerer user` or `stakeholder` and `--kind context`.
- **State.** Under Unresolved issues, add each confirmed shared data problem or coverage limitation, naming the scan path; under Next steps, add the action that tests each new question, citing its ID. Replace items they supersede, each list in one call: `python3 src/awb.py state issues --add "<text>"` and `state next --add "<text>" --drop <number>`.
- **History.** An entry only for a limitation or decision that affects the question; a routine scan gets none.
- **Vocabulary.** A term the data settled goes where AGENTS.md records meanings; a term still open is a ledger question for whoever owns its meaning, added as under Questions above, not an unresolved issue.
- **Shared data problems.** Except for coverage limitations recorded below, hand confirmed shared data problems to awb-clean: "Use awb-clean on <dataset> for <problem>". Leave canonical views to awb-clean. When exploration must exclude affected rows, or a question-specific exclusion stays local, do it in a saved query whose comment gives the reason, and say so; an exclusion `run.py` needs goes into settings.
- **Coverage limitations.** Record a confirmed shared limitation in time coverage or field availability as an `open` row in `foundation/quality.md`, citing the scan; it needs no awb-clean pass.

## 6. Report

Report the dataset and scope, the observations and values that bear on the question, each anomaly's disposition, the saved query paths, the ledger questions added, the records changed, and the scan path.
