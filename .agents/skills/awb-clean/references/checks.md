# Scan checks

## What each key counts

Counts are rows unless noted; `of` is the column's non-null values, or all rows for row-level checks. Text values are compared after trimming leading and trailing whitespace, including non-breaking spaces.

| Key | Counts | Common false positives |
| --- | --- | --- |
| `duplicate-rows` | rows repeating another row exactly, beyond the first | event data with no timestamp or identifier, where identical rows are separate events |
| `duplicate-key:<cols>` | extra rows for key values that occur more than once. Explicit `--key` or, without one, near-unique columns and columns named like `id`, `*_id`, or `key` | a near-unique attribute such as an email that is not the grain |
| `null-key:<cols>` | rows missing part of an explicit key | none |
| `parse:<col>:<type>` | non-placeholder values that fail to parse when at least 90% parse as the type | free-text columns that are mostly numeric |
| `date-formats:<col>` | values outside the dominant format when formats mix, or every value when two formats fit them all (day-month order ambiguous) | none |
| `text-typed:<col>:<type>` | values stored as text that parse as the type, for views and publications only; landed CSV is read as text on purpose | codes and identifiers that look numeric. Leading-zero values stay text |
| `sentinel:<col>:<value>` | text placeholders (`""`, `N/A`, `null`, `none`, `-`, `?`, `unknown`, `missing`, `tbd`, and similar); numbers such as `-1`, `999`, or `9999` that sit outside every other value; placeholder dates such as `1900-01-01` or `9999-12-31` | `none` or `unknown` as a real category answer; `0` is not a placeholder candidate |
| `variants:<col>:<normal form>` | rows using a minority spelling among labels equal after case folding and removing punctuation and repeated spaces | codes where case is meaningful |
| `near-variants:<col>:<a>\|<b>` | rows of the rarer of two labels whose normalized forms are at least 0.92 similar (Jaro-Winkler), ignoring pairs differing only in digits; examples show the normalized forms | genuinely different short labels |
| `whitespace:<col>` | values with leading or trailing whitespace | fixed-width codes where padding is meaningful |
| `negative:<col>` | negative values when at most 1% of values are negative, excluding values the `sentinel` check reports | refunds, adjustments, and signed differences |
| `range:<col>:<min>:<max>` | values outside a requested `--range` | none; the range is the user's |
| `future-date:<col>` | dates after the scan date, excluding placeholder dates | due dates, plans, and expiries |
| `ancient-date:<col>` | dates before 1900, excluding placeholder dates | historical data |
| `extreme:<col>` | values beyond five interquartile ranges from the quartiles, excluding values the `sentinel` check reports; not checked for key-like columns | heavy-tailed quantities such as revenue |
| `orphans:<col>:<target>.<col>` | non-null rows whose value has no match in the `--ref` target, compared as text | none |
| `all-null:<col>` | every row null | none |

Text-placeholder and type checks apply to columns DuckDB reads as text. A text column counts as typed when at least the threshold share of its non-placeholder values parse as `BIGINT` (integer text only), `DOUBLE`, `DATE`, `TIMESTAMP`, `BOOLEAN`, or a recognized date format. Numeric and date checks then run on the parsed values. Spelling-variant checks run on untyped text columns with at most 500 distinct values. Near-variant checks run on those with at most 200.

Null rates and the commonest co-null column patterns are reported for information only. A rescan reports null-rate changes so that placeholders converted to null can be confirmed.

## Scan file

`foundation/scans/<name>.json` stays local to the checkout. It holds the target, options, row count, per-column type, parsed type, non-null and distinct counts and null rate, candidate keys (complete and unique columns), null patterns, and every issue with up to ten examples. A rescan also holds the `baseline` it compares with and the `delta`. The scan name defaults to the view name, `<dataset>@<publication-id>`, `<source>@<acquisition-id>`, or the file stem; `--name` overrides it.

Examples are real values, up to ten per issue and 80 characters each.

An issue whose `<name>#<key>` marker appears in a `foundation/quality.md` row is reported as recorded, with that row's ID, status, and the count in its `(<count> of <of>)`. `record_cleaning.py` writes the marker into every issue row it adds and refreshes the count when it updates a recorded issue.
