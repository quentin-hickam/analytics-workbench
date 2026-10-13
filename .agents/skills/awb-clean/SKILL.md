---
name: awb-clean
description: "Clean one analytics workbench dataset: find its data errors and correct them in the shared canonical views. Use when the user asks to clean or quality-check a dataset or source."
---

# Clean one dataset

Work on one dataset at a time: a canonical view, a publication, or a landed acquisition. This skill and its references contain the cleaning rules of the data guide and the analysis guide. For this reason, a cleaning pass does not read these two guides. Put the corrections into view definitions or into a new publication. Never change the landed originals or the existing publications.

Run the bundled scripts as black boxes, by path, with the Python environment of the project (the scan needs `duckdb`). A typical pass uses six tool calls:

- scan
- read the view definition and the catalog row of the dataset in one call
- edit the view
- rescan
- `stale`
- record

## 1. Scan

```sh
python3 <skill-directory>/scripts/scan_dataset.py <project-root> <dataset> [--key COLS] [--ref COL=TARGET.COL] [--range COL=MIN:MAX] [--columns COLS]
```

`<dataset>` is usually the canonical view. `--help` lists the other targets. If you know the grain from the catalog, give it as `--key`. If not, the scan proposes candidate keys. Give the joins that the question uses as `--ref`. Give the known valid ranges and the reporting period as `--range`. You can repeat each of these options. For a wide dataset, `--columns` limits the per-column checks to the columns in scope.

Stdout shows the scan path (the stem of this path is `<scan-name>` in step 6). Stdout also lists up to 25 unrecorded issues as `S<n>`, each with its key, count, and three examples. `more_issues` gives the number of the other issues, which are in `issues` in the scan file. Open the scan file only for these other issues, or when a decision needs more than three examples. Issues under `recorded` already have a quality row. Reopen a recorded issue if its status is `corrected`, or if its `count` is different from its `recorded_count`. Keep the other recorded issues as recorded. Read [checks.md](references/checks.md) when a decision depends on a probable false positive or on the threshold of a check.

## 2. Decide

The active question sets the limits of the work. Decide the issues in the columns that the active investigation uses, unless the user asked for broader cleaning. The other issues stay in the scan file. Put each in-scope issue in one class. The keys after each class name are the checks that the class usually gets:

- **Shared cleaning rule** (`whitespace`, `variants`, `near-variants`, `sentinel`, `parse`, `date-formats`, `text-typed`, `duplicate-rows`, `duplicate-key`, `ancient-date`, `range` as a validity rule): an error in the data itself, which is wrong for every investigation. Examples are a placeholder that means missing, or a row that was landed two times.
- **Shared limitation** (`null-key`, `orphans`, `all-null`): a real defect that no rule can fix. Examples are orphans from a partial extract, null keys, or a column that the source never fills. Record it with the status `open`. The view stays as it is.
- **Investigation-local choice** (`range` as the reporting period, `extreme`): data that is correct, but that the question chooses to exclude or to treat in a special way. Examples are test accounts, a period, or real outliers. In the report, name the exclusion for the settings of that investigation. When the property is useful to know for all of the project, also record it with the treatment "none in the foundation; investigations decide".
- **Not an issue** (often `negative`, `future-date`, `extreme`): real values that only look strange, such as refunds or due dates. Record one only when, without the record, someone would ask again for a user decision or for a non-obvious reason.

Decide yourself the fixes that change only the representation:

- `whitespace`
- `text-typed`
- `variants` that differ only in case or punctuation
- a clear `parse` format error
- a `date-formats` mix that you can read in only one way
- `duplicate-rows` under a recorded grain

Exception: do not decide these fixes yourself in a code column or an identifier column, because there, case, padding, and numeric form can have a meaning. Ask when the examples or the source context do not make the meaning clear. Record `all-null` as an open limitation yourself.

The user decides every other issue, because each of these issues changes meaning:

- what a placeholder stands for (missing, zero, or real)
- the canonical label
- if repeated rows or repeated keys are errors, and which row wins
- if out-of-range values are wrong
- a parsed value that has a meaning, such as `<5`
- how to treat orphans and null keys
- an ambiguous day-month order

Ask all of these questions in one message, as a table. The table has these columns: issue, observation with count and examples, proposed treatment, and the alternative. Ask the questions one after the other only when one answer changes which later questions occur. For example, the grain decides which repeated keys are issues.

Decide is done when these two conditions are true:

- Every in-scope `S<n>` has a class. This includes each in-scope issue after the first 25, which stdout does not list.
- Every question that you asked has an answer or is recorded as `open`.

## 3. Correct

Put the accepted shared rules into the canonical view under `foundation/views/` that consumers already read. Correct the values and keep the rows, except the rows that are invalid as a rule. Examples are exact duplicates, or the rows that lose under a decided key rule. Read [correction-views.md](references/correction-views.md) before you write a pattern that is new to the views of this project. Also read it when a view cannot express the correction (the publish branch). If the pass changed no view and no publication, skip steps 4 and 5.

## 4. Confirm

```sh
python3 <skill-directory>/scripts/scan_dataset.py <project-root> <dataset> --rescan
```

Every scan after the edit uses `--rescan`. This option keeps the baseline from before the cleaning, and the options of that baseline. A plain scan starts a new baseline. For each issue, stdout gives the count before and the count after. Stdout also gives the row count, and the changes in null rate and in type. Expect these results:

- The addressed issues are resolved.
- The rows do not change, unless duplicates were removed.
- The increases in nulls match the placeholders that were converted to null.

Explain each other change before you continue. Use `python3 src/awb.py sql` on a saved query only when the delta does not explain a change.

## 5. Flag affected findings

Run `python3 src/awb.py stale`. Flag the findings whose `stale` entry names the corrected view or publication, or a view that is built on it. Findings that `stale` lists for other reasons keep their status.

## 6. Record

Record the decided issues, corrections, flags, and catalog changes in one call:

```sh
python3 <skill-directory>/scripts/record_cleaning.py <project-root> <scan-name> <<'EOF'
{"issues": {"S1": {"impact": "...", "treatment": "...", "status": "corrected",
                   "correction": "rule and rationale", "change": "`foundation/views/02_orders.sql` trims dept"},
            "S4": {"impact": "...", "treatment": "...", "status": "open"}},
 "flags": [{"investigation": "churn", "result": "r-003", "reason": "{S1} merges department labels"}],
 "catalog": {"name": "orders", "cells": {"Preparation rules": "...", "Quality constraints": "..."}}}
EOF
```

Flags go through the state flag helper in the `src/provenance.py` of the project. A helper that is older than `findings.json` refuses before it writes. In that case, run the `awb-init` repair (`install_helpers.py --upgrade`).

If no finding is affected, add `"findings": "none: stale listed no finding reading <view>"`. The script does these tasks:

- It fills the IDs, observations, counts, and markers of new rows.
- It keeps the scan links, and the recorded counts and dates, in `foundation/quality.json`.
- It fills the flagged statuses.
- It changes `{S1}` into the quality ID of that issue.

A reopen updates the judgment cells and the link. The observation stays as it was first written. For a decision on a recorded issue that the scan no longer lists, use its quality ID as the key, such as `"Q-004"`. This decision revises the judgment cells, but it keeps the observation and the link. `{Q-004}` placeholders also resolve. Record shared vocabulary in the glossary yourself.

Read the existing catalog row before you set any of its cells. A cell that you set replaces the whole cell. For this reason, give the complete new text of the cell. Keep the text that is still true, and cite quality IDs for the rationale.

## Report

Report these items:

- the dataset
- the decided issues, by class
- the corrections and the changed views
- the delta lines of the rescan, verbatim
- the quality IDs
- each flagged finding, with its reason
- the in-scope issues that are still `open`
- each exclusion that you named for the settings of an investigation

Say that no analysis was rerun. Commit `foundation/quality.json` together with `foundation/quality.md`. The JSON file contains no source values. When `foundation/sources.md` puts limits on copies of the source values, confirm before you commit `foundation/quality.md`. The reason is that its rows quote up to three example values.
