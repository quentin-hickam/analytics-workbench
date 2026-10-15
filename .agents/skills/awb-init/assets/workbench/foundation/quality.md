# Data quality

Record shared limitations, errors, checks, and accepted corrections that affect canonical data. Investigation-specific filters belong in that investigation's settings; execution mistakes go unrecorded. When `foundation/sources.md` restricts copying the source's values, confirm before committing this file: its rows quote up to three example values.

`awb-clean`'s `record_cleaning.py` reads the two sections below, **Active limitations and issues** and **Correction record**: keep each heading and table as written, with any guidance above the table and every row directly under the table's last row. Quality IDs are `DQ-NNN`, distinct from the ledger's question IDs; a project already numbering rows another way keeps its prefix. `awb-clean` keeps scan links in `foundation/quality.json`; don't edit it by hand.

## Active limitations and issues

A confirmed coverage gap, such as a missing or low period or a field that stops being filled, is an `open` row under the next ID, citing the scan or saved query that found it.

| ID | Affected source or catalog object | Observation and evidence | Analytical impact | Current treatment | Status |
| --- | --- | --- | --- | --- | --- |

## Correction record

`awb-clean` alone records corrections here, each with the findings the correction flagged in their investigations' `state.md`; prior conclusions stay in each investigation's history.

| Date | Issue ID | Accepted correction and rationale | Preparation or view change | Findings that may need revalidation |
| --- | --- | --- | --- | --- |
