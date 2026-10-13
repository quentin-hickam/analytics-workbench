# Data quality

Record shared limitations, errors, checks, and accepted corrections that affect canonical data. Investigation-specific filters belong in the settings of that investigation. Do not record execution mistakes. When `foundation/sources.md` restricts copies of the values of the source, confirm before you commit this file, because its rows quote up to three example values.

## Active limitations and issues

| ID | Affected source or catalog object | Observation and evidence | Analytical impact | Current treatment | Status |
| --- | --- | --- | --- | --- | --- |

A confirmed coverage gap is an `open` row under the next ID, and that row cites the scan that found it. Examples of a coverage gap are a missing or low period, and a field that stops getting values.

`awb-clean` keeps scan links in `foundation/quality.json`. Do not edit that file by hand.

## Correction record

| Date | Issue ID | Accepted correction and rationale | Preparation or view change | Findings that may need revalidation |
| --- | --- | --- | --- | --- |

Only `awb-clean` records corrections here. It records each correction with the findings that it flagged in the `state.md` of their investigations. Prior conclusions stay in the history of each investigation.
