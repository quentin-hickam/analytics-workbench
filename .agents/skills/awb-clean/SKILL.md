---
name: awb-clean
description: "Clean one analytics workbench dataset: find its data errors and correct them in the shared canonical views. Use when the user asks to clean or quality-check a dataset or source."
---

# Clean one dataset

Work on one dataset at a time: a canonical view, a publication, or a landed acquisition. This skill and its references hold the data and analysis guides' cleaning rules, so a cleaning pass reads neither guide. Corrections go into view definitions or a new publication; landed originals and existing publications are never modified.

Run the bundled scripts as black boxes, by path, with the project's Python environment (the scan needs `duckdb`). A typical pass is six tool calls: scan, read the view definition, edit it, rescan, `stale`, record.

## 1. Scan

```sh
python3 <skill-directory>/scripts/scan_dataset.py <project-root> <dataset> [--key COLS] [--ref COL=TARGET.COL] [--range COL=MIN:MAX] [--columns COLS]
```

`<dataset>` is a view name, a dataset under `data/parquet/` (newest publication), a publication or acquisition directory, a data file, or a saved `.sql` query. Pass the catalog's grain as `--key` when you know it; otherwise the scan proposes candidate keys. Pass the joins the question uses as `--ref`, and known valid ranges and the reporting period as `--range` (numbers or ISO dates, one side may be empty); each is repeatable. For a wide dataset, `--columns` limits per-column checks to the columns in scope.

Stdout prints the scan path (its stem is `<scan-name>` in step 6) and lists up to 25 unrecorded issues as `S<n>` with key, count, and three examples; `more_issues` counts the rest, which are in the scan file's `issues`. Open the scan file only for those, or when a decision needs more than three examples. Issues under `recorded` already have a quality row: reopen one when its `count` differs from its `recorded_count`, and leave the rest as recorded. Read [checks.md](references/checks.md) when a likely false positive or a check's threshold bears on a decision.

## 2. Decide

The active question bounds the work: decide issues in the columns the active investigation uses, unless the user asked for broader cleaning; the rest stay in the scan file. Put each in-scope issue in one class; the keys are the checks each class usually takes:

- **Shared cleaning rule** (`whitespace`, `variants`, `near-variants`, `sentinel`, `parse`, `date-formats`, `text-typed`, `duplicate-rows`, `duplicate-key`, `ancient-date`, `range` as a validity rule): an error in the data itself, wrong for every investigation, such as a placeholder meaning missing or a row landed twice.
- **Shared limitation** (`null-key`, `orphans`, `all-null`): a real defect no rule can fix, such as orphans from a partial extract, null keys, or a column the source never fills. Record it with status `open`; the view stays as it is.
- **Investigation-local choice** (`range` as the reporting period, `extreme`): correct data the question chooses to exclude or treat specially, such as test accounts, a period, or real outliers. Name the exclusion for that investigation's settings in the report. When the property is worth knowing project-wide, also record it with treatment "none in the foundation; investigations decide".
- **Not an issue** (often `negative`, `future-date`, `extreme`): real values that only look odd, such as refunds or due dates. Record one only when a user decision or a non-obvious reason would otherwise be asked again.

Decide meaning-preserving fixes yourself: `whitespace`, `text-typed`, `all-null`, case- or punctuation-only `variants`, a clear `parse` format error, a `date-formats` mix with one reading, and `duplicate-rows` under a recorded grain. The user decides every other issue, because each changes meaning: what a placeholder stands for (missing, zero, or real), the canonical label, whether repeated rows or keys are errors and which row wins, whether out-of-range values are wrong, a parsed value that carries meaning such as `<5`, how to treat orphans and null keys, and an ambiguous day-month order. Ask all of these in one message, as a table of issue, observation with count and examples, proposed treatment, and the alternative. Ask in sequence only when one answer changes which later questions arise, such as the grain deciding which repeated keys are issues.

Decide is done when every in-scope `S<n>`, including any past stdout's 25, has a class and every question asked has an answer or is recorded as `open`.

## 3. Correct

If the issue arose in an investigation's exploration, first save the correction as `investigations/<name>/exploration/<topic>.sql` over the canonical view and scan it with `--rescan <view>`; the delta stays beside the query.

Implement accepted shared rules in the canonical view under `foundation/views/` that consumers already read. Correct values and keep rows, except rows invalid as a rule, such as exact duplicates or a decided key rule's losing rows. Read [correction-views.md](references/correction-views.md) before writing a pattern new to this project's views, or when a view cannot express the correction (the publish branch).

## 4. Confirm

```sh
python3 <skill-directory>/scripts/scan_dataset.py <project-root> <dataset> --rescan
```

Every scan after the edit uses `--rescan`, which keeps the pre-cleaning baseline and its options; a plain scan starts a new baseline. Stdout reports, per issue, before and after counts (`resolved`, `reduced`, `unchanged`, `increased`, `new`), the row count, and null-rate and type changes. Expect addressed issues resolved, rows unchanged unless duplicates were removed, and null increases that match placeholders converted to null. Explain any other change before going on. Use `python3 src/awb.py sql` on a saved query only when the delta leaves a change unexplained, and `python3 src/awb.py profile` only when a decision needs a full distribution.

## 5. Flag affected findings

Run `python3 src/awb.py stale`. Flag the findings whose `stale` entry names the corrected view or publication, or a view built on it; findings `stale` lists for other reasons keep their status.

## 6. Record

Write every record in one call from the dataset's foundation scan:

```sh
python3 <skill-directory>/scripts/record_cleaning.py <project-root> <scan-name> <<'EOF'
{"issues": {"S1": {"impact": "...", "treatment": "...", "status": "corrected",
                   "correction": "rule and rationale", "change": "`foundation/views/02_orders.sql` trims dept"},
            "S4": {"impact": "...", "treatment": "...", "status": "open"}},
 "flags": [{"investigation": "churn", "result": "r-003", "reason": "{S1} merges department labels"}],
 "catalog": {"name": "orders", "cells": {"Preparation rules": "...", "Quality constraints": "..."}}}
EOF
```

You supply only judgment: impact, treatment, and status per decided issue; rule, rationale, and view change per correction; a reason per flagged finding; changed catalog cells. With no affected finding, add `"findings": "none: stale listed no finding reading <view>"`. The script fills IDs, observations, counts, markers, and flagged statuses, and turns `{S1}` into that issue's quality ID. Record shared vocabulary in the glossary yourself.

## Report

Report the dataset, the decided issues by class, the corrections and changed views, the rescan's delta lines verbatim, the quality IDs, each flagged finding with its reason, the in-scope issues still `open`, and any exclusion named for an investigation's settings. Say that no analysis was rerun. When the user asks for a commit and `foundation/sources.md` restricts copying the source's values, confirm before committing the scan file: it holds real example values.
