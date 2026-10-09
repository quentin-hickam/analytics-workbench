---
name: awb-eda
description: "Explore one dataset (EDA) for the active analytics workbench investigation. Use when the user asks to explore, profile, or understand a dataset or view for the investigation's question."
---

# Explore a dataset for an investigation

Explore one canonical view or publication at a time, within the investigation's question and scope. This skill carries the analysis rules EDA needs; load `workbench-guides/analysis.md` only to turn a pattern into a finding. EDA writes only under `investigations/<name>/exploration/` and the records in step 5.

## 1. Frame

Use the investigation the user names, otherwise the README's active one. If its `brief.md` and `state.md` are not loaded, read them in one call. Say in a sentence or two which dataset you will explore and why it bears on the question. If several datasets fit, start with the one that holds the question's measure.

## 2. Scan

From the project root, with the interpreter that runs the project's analysis:

```sh
python3 <skill-directory>/scripts/eda_scan.py <project-root> <view-or-publication> [options]
```

Run it as a black box. It reads scope, measure, and dimensions from the investigation's `settings.toml` (`[eda]`, with the period falling back to `[parameters]` `start` and `end`), writes the complete scan to `investigations/<name>/exploration/eda/<dataset>.json`, and prints a compact summary. A new investigation's settings usually name no date column, measure, or dimensions, so pass them in the first run: the brief's population as `--where`, its date column as `--date-column` (with `--start` and `--end` when settings hold no period), and the question's measure and grouping columns as `--measure` and `--dimension` (repeatable). A `not set` or `not applied` line names any option still missing. Pass exploratory choices as options; settings change only when the user settles a population or period choice. `--help` lists the other options, such as `--label` for a second scope, and the settings keys. Exit status 2 prints the fix; apply it and run again.

One scan per dataset and scope is final, and its printed summary is the result. To open one part of the saved file, print it with `--show`, such as `--show columns.<column>.top` or `--show measure.by_dimension.<dimension>.values`; read [the scan file](references/scan-file.md) to find any other section.

## 3. Read the scan

Check in order:

- **Scope.** Are the rows before and after the filters plausible? Does a `not set` or `not applied` line, or an unread settings key, mean the population differs from the brief's? If so, scan again with the missing options and say so.
- **Grain.** Do the candidate keys match the catalog's grain? Check duplicates and any declared-key violation.
- **Anomalies.** Give every printed anomaly one disposition: a shared data problem, confirmed by a follow-up query or the source register before the step 5 hand-off; a local analytical matter; or dismissed with a reason. The `route` column is the scan's guess, not the disposition.
- **Relationships.** Read variance explained, the trend, associations, and **contrary** groups. Variance explained rises with group count, and a trend where a high-variance dimension's shares shift may be mix rather than change. Name candidate explanations and keep every contrary pattern.

Read [reading the scan](references/reading-the-scan.md) for an anomaly kind's confirmation check, or when a data problem and a real pattern are hard to tell apart. Draft three to five observations labeled exploratory, with candidate explanations and contrary patterns, for the report.

## 4. Follow up with saved queries

Run one follow-up for each anomaly you are confirming as a shared data problem and each candidate explanation the user's question turns on; leave the rest as Next steps. The step is done when every observation you report is either settled by a saved query or recorded as a Next step.

Write each follow-up as `investigations/<name>/exploration/<topic>.sql` and run it from the project root with `python3 src/awb.py sql <path>`. Start each file with a comment naming the question it serves and its scope, and copy every printed scope filter, period included, into its `WHERE`. Aggregate, order, and limit in SQL so the printed table stays short. To separate mix from within-group change, compute each group's share and mean per period in one query; a moving overall mean over stable group means is a mix shift. Revise and rerun the same file rather than adding variants; save even a one-off, since the report cites its path and awb-clean reuses it. To profile a result, run `python3 src/awb.py profile <path> --out <file under exploration/>`. Compute every distribution, breakdown, or trend as a saved query or a `profile` call. Draw an exploratory chart only on request, saved under `exploration/`.

## 5. Record what was learned

- **State.** Start from the printed suggested `state.md` lines. Keep the ones you confirmed, edit them, and add them under Unresolved issues or Next steps, replacing items they supersede.
- **History.** An entry only for a limitation or decision that affects the question; a routine scan gets none.
- **Vocabulary.** A term the data settled goes where AGENTS.md records meanings; a term still open is an unresolved issue.
- **Shared data problems.** Record each confirmed problem as an unresolved issue naming the scan path, and hand it over: "Use awb-clean on <dataset> for <problem>". Leave canonical views to awb-clean. When exploration must exclude affected rows, or a question-specific exclusion stays local, do it in a saved query whose comment gives the reason, and say so; an exclusion `run.py` needs goes into settings.
- **Findings.** A pattern becomes a finding only through `run.py` under `workbench-guides/analysis.md`. Until then, record it as a question under Next steps.

Report the dataset and scope, the printed tables cut to the rows that bear on the question, the observations, each anomaly's disposition, the saved query paths, the records changed, and the scan path.
