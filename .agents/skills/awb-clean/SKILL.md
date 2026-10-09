---
name: awb-clean
description: Clean one dataset in an analytics workbench at the shared foundation level. Scans a canonical view, publication, or landed file for candidate issues, decides each one with the user where meaning changes, implements accepted corrections as canonical view definitions, records them in the quality record and catalog, and flags affected findings. Use when the user asks to clean, check the quality of, or correct errors in a dataset or source.
---

# Clean one dataset

Cleaning is the part of data preparation that corrects errors and inconsistencies under explicit, reusable rules. Work on one dataset at a time: a canonical view, a publication, or a landed acquisition. The project `AGENTS.md` and `workbench-guides/data.md` govern; read the data guide before changing a view or publication if it is not already loaded. Landed originals and existing publications are never modified.

Run the bundled scripts by path with the project's Python environment (the scan needs `duckdb`). Execute them without reading their implementation. Each prints compact JSON and keeps complete records in files.

## 1. Scan

```sh
python3 <skill-directory>/scripts/scan_dataset.py <project-root> <dataset> [--key COLS] [--ref COL=TARGET.COL] [--range COL=MIN:MAX] [--columns COLS]
```

`<dataset>` is a view name, a dataset under `data/parquet/` (newest publication), a publication or acquisition directory, a data file, or a saved `.sql` query. Pass the grain from the catalog as `--key`, the joins the question uses as `--ref`, and known valid ranges and the reporting period as `--range` (numbers or ISO dates, one side may be empty); each is repeatable. For a wide dataset, `--columns` limits per-column checks to the columns in scope.

The complete scan goes to `foundation/scans/<name>.json`, beside the quality record that cites it as evidence and tracked with the view definitions. Stdout lists candidate issues as `S<n>` with key, count, and up to three examples. Read the scan file only for the issue being decided. Issues listed under `recorded` already have a quality row; reopen one only when its count changed. When a check's meaning or a likely false positive matters, read [checks.md](references/checks.md).

## 2. Decide

The active question bounds the work: decide issues in the columns the active investigation uses, unless the user asked for broader cleaning. Leave the rest undecided; they stay in the scan file. Put each in-scope candidate in one class:

- **Shared cleaning rule**: an error in the data itself, wrong for every investigation, such as padding, case or spelling variants of one label, a placeholder meaning missing, a known format, or a row landed twice.
- **Investigation-local choice**: correct data the question chooses to exclude or treat specially, such as test accounts, a period, or real outliers. The exclusion goes in that investigation's settings. When the property is worth knowing project-wide, record it as a limitation whose treatment is "none in the foundation; investigations decide".
- **Not an issue**: real values that only look odd. Record one only when a user decision or a non-obvious reason would otherwise be asked again.

Decide meaning-preserving fixes yourself: whitespace, case-only variants, and text that parses completely as one type. The user decides what changes meaning: what a placeholder stands for (missing, zero, or real), which label is canonical when spellings differ beyond case, whether repeated keys are errors and which row wins, whether out-of-range values are wrong, how to treat orphans, and an ambiguous day-month order. Ask all of these in one message, as a table of issue, finding with count and examples, proposed treatment, and the alternative. Ask in sequence only when one answer changes which later questions arise, such as the grain deciding which repeated keys are issues. A question about what a term means follows the glossary rules in `AGENTS.md`.

When the issue came up during an investigation's exploration, assess the correction locally first: save it as `investigations/<name>/exploration/<topic>.sql` selecting from the canonical view and scan that file with `--rescan <view>`. The scan stays beside the query and reports the delta against the view's scan. Promote it only after it is accepted as general.

## 3. Correct

Implement shared rules in the canonical view definition under `foundation/views/` that consumers already read, so every investigation receives the correction. Correct values rather than dropping rows, except for rows that are invalid as a rule, such as exact duplicates. When a view cannot express the correction, publish a corrected dataset with `python3 src/awb.py publish` and point the view at it; switching publications is a deliberate preparation change. Read [correction-views.md](references/correction-views.md) before writing a pattern you have not written in this project.

## 4. Confirm

```sh
python3 <skill-directory>/scripts/scan_dataset.py <project-root> <dataset> --rescan
```

One call reruns the scan with the baseline's options and reports, per issue, before and after counts (`resolved`, `reduced`, `unchanged`, `increased`, `new`), the row count, and null-rate and type changes. Expect addressed issues resolved, rows unchanged unless duplicates were removed, and null increases that match placeholders converted to null. Explain any other change before going on. Use `python3 src/awb.py sql` on a saved query only when the delta leaves a change unexplained, and `python3 src/awb.py profile` only when a decision needs a full distribution.

## 5. Find affected findings

Run `python3 src/awb.py stale`. Every finding whose changed views or inputs include the corrected view or publication, or a view built on it, may be affected. A finding that `stale` lists only for other reasons is not affected by this correction. Do not rerun analyses or revise conclusions.

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

You supply only judgment: impact, treatment, and status for each decided issue; the correction rule, its rationale, and the view change for each corrected one; a flag reason for each affected finding; and the catalog cells that changed (name the new publication in `Definition or location` and `Inputs` when it changed). With no affected finding, add `"findings": "none: stale listed no finding reading <view>"`. The script allocates quality IDs and fills observations, counts, examples, scan markers, the rescan's before and after counts, and each correction's findings. It sets each flagged finding to `revalidation-needed (was <status>)` with its reason and updates `Last updated`. `{S1}` in any text becomes that issue's quality ID. It checks everything before writing; `--dry-run` prints the rows instead. Record shared vocabulary in the glossary yourself.

## Report

Report the dataset, the decided issues by class, the corrections and changed views, the before and after counts, the quality IDs, each flagged finding with its reason, and the in-scope issues left undecided. Say that no analysis was rerun. Commit only when the user asks.
