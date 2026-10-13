---
name: awb-eda
description: "Explore one dataset (EDA) for the active analytics workbench investigation. Use when the user asks to explore, profile, or understand a dataset or view for the investigation's question."
---

# Explore a dataset for an investigation

Explore one canonical view or publication at a time, in the limits of the question and scope of the investigation. This skill contains the analysis rules that EDA needs. Load `workbench-guides/analysis.md` only to turn a pattern into a finding. EDA writes only under `investigations/<name>/exploration/` and to the records in step 5.

## 1. Frame

Use the investigation that the user names. If the user names none, use the active investigation in the README. If its `brief.md` and `state.md` are not loaded, read them in one call. In one or two sentences, say which dataset you will explore and why it is related to the question. If more than one dataset fits, start with the dataset that holds the measure of the question.

## 2. Scan

Run this command from the project root, with the interpreter that runs the analysis of the project:

```sh
python3 <skill-directory>/scripts/eda_scan.py <project-root> <view-or-publication> [options]
```

Run this script, but do not read it. The script does these tasks:

- It reads the scope, measure, and dimensions from the `settings.toml` of the investigation (`[eda]`). For the period, it uses `[parameters]` `start` and `end` if `[eda]` has no period.
- It writes the complete scan to `investigations/<name>/exploration/eda/<dataset>.json`.
- It prints a compact summary.

The settings of a new investigation usually name no date column, measure, or dimensions. For this reason, give them in the first run:

- the population of the brief as `--where`
- the date column of the brief as `--date-column` (with `--start` and `--end` when the settings hold no period)
- the measure and grouping columns of the question as `--measure` and `--dimension` (you can repeat these options)

A `not set` or `not applied` line names each option that is still missing. Give exploratory choices as options. The settings change only when the user settles a population choice or a period choice. `--help` lists the other options (such as `--label` for a second scope) and the settings keys. Exit status 2 prints the fix. Apply the fix and run the script again.

One scan for each dataset and scope is final, and its printed summary is the result. To open one part of the saved file, print it with `--show`, such as `--show columns.<column>.top` or `--show measure.by_dimension.<dimension>.values`. To find a different section, read [the scan file](references/scan-file.md).

## 3. Read the scan

Do these checks in this order:

- **Scope.** Are the rows before and after the filters plausible? Does a `not set` or `not applied` line, or an unread settings key, show that the population is different from the population of the brief? If yes, scan again with the missing options and say so.
- **Grain.** Do the candidate keys match the grain in the catalog? Check the duplicates and each declared-key violation.
- **Anomalies.** Give each printed anomaly one of these dispositions:
  - a shared data problem, which a follow-up query or the source register confirms before the hand-off in step 5
  - a local analytical matter
  - dismissed, with a reason

  The `route` column is the guess of the scan, not the disposition.
- **Relationships.** Read the variance explained, the trend, the correlations of the measure, and the **contrary** groups. Variance explained increases with the group count. When the shares of a high-variance dimension shift, it is possible that the trend is mix and not change. Name the candidate explanations and keep every contrary pattern.

Read [reading the scan](references/reading-the-scan.md) for the confirmation check of an anomaly kind. Also read it when it is difficult to see the difference between a data problem and a real pattern. For the report, write a draft of the observations that are related to the question. Label them as exploratory, and give the candidate explanations and contrary patterns.

## 4. Follow up with saved queries

Run one follow-up for each anomaly that you confirm as a shared data problem. Also run one follow-up for each candidate explanation that the question of the user depends on. Leave the other items as Next steps. This step is done when each observation that you report is settled by a saved query or recorded as a Next step.

Write each follow-up as `investigations/<name>/exploration/<topic>.sql`. Run it from the project root with `python3 src/awb.py sql <path>`. Start each file with a comment that names its question and its scope. Copy every printed scope filter (the period also) into the `WHERE` of the file. Aggregate, order, and limit in SQL, so that the printed table stays short.

To separate mix from within-group change, calculate the share and the mean of each group for each period in one query. If the overall mean moves but the group means are stable, this is a mix shift. Revise the same file and run it again. Do not add variants of it. Save even a query that you use one time only, because the report cites its path. Draw an exploratory chart only on request, and save it under `exploration/`.

## 5. Record what was learned

- **State.** Under Unresolved issues, add each confirmed shared data problem or coverage limitation, and name the scan path. Under Next steps, add each important pattern or candidate explanation that `run.py` did not test yet. Write it as a question for `run.py`, because a pattern becomes a finding only there. Replace the items that they supersede. Change each list in one call: `python3 src/awb.py state issues --add "<text>"` and `state next --add "<text>" --drop <number>`.
- **History.** Add an entry only for a limitation or decision that affects the question. A routine scan gets no entry.
- **Vocabulary.** Put a term that the data settled where AGENTS.md records meanings. A term that is still open is an unresolved issue.
- **Shared data problems.** Except for the coverage limitations in the next item, hand the confirmed shared data problems to awb-clean: "Use awb-clean on <dataset> for <problem>". Leave canonical views to awb-clean. When exploration must exclude affected rows, or a question-specific exclusion stays local, do the exclusion in a saved query. Give the reason in the comment of that query, and say so. Put an exclusion that `run.py` needs into the settings.
- **Coverage limitations.** Record a confirmed shared limitation in time coverage or field availability as an `open` row in `foundation/quality.md`. Cite the scan. This limitation needs no awb-clean pass.

Report these items:

- the dataset and the scope
- the printed tables, cut to the rows that are related to the question
- the observations
- the disposition of each anomaly
- the paths of the saved queries
- the records that you changed
- the scan path
