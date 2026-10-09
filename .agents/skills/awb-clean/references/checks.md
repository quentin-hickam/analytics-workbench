# Scan checks

Read when a candidate's check, threshold, or likely false positive matters to its decision. The scan proposes candidates; none is an error until decided.

## What each key counts

Counts are rows unless noted; `of` is the column's non-null values, or all rows for row-level checks. Text values are compared after trimming leading and trailing whitespace, including non-breaking spaces.

| Key | Counts | Common false positives | Usual class | Who decides |
| --- | --- | --- | --- | --- |
| `duplicate-rows` | rows repeating another row exactly, beyond the first | event data with no timestamp or identifier, where identical rows are separate events | shared rule when the grain says rows are unique | user, unless the grain is recorded |
| `duplicate-key:<cols>` | extra rows for key values that occur more than once. Explicit `--key` or, without one, near-unique columns and columns named like `id`, `*_id`, or `key` | a near-unique attribute such as an email that is not the grain | shared rule once the grain is settled | user picks the winning row or rule |
| `null-key:<cols>` | rows missing part of an explicit key | none | shared limitation | user |
| `parse:<col>:<type>` | non-placeholder values that fail to parse when at least 90% (`--typed-threshold`) parse as the type | free-text columns that are mostly numeric | shared rule | agent for a clear format error; user when a value carries meaning, such as `<5` |
| `date-formats:<col>` | values outside the dominant format when formats mix, or every value when two formats fit them all (day-month order ambiguous) | none | shared rule | user for day-month order |
| `text-typed:<col>:<type>` | values stored as text that parse as the type, for views and publications only; landed CSV is read as text on purpose | codes and identifiers that look numeric. Leading-zero values are never typed as numbers | shared rule, often at conversion | agent |
| `sentinel:<col>:<value>` | text placeholders (`""`, `N/A`, `null`, `none`, `-`, `?`, `unknown`, `missing`, `tbd`, and similar); numbers such as `-1`, `999`, or `9999` that sit outside every other value; placeholder dates such as `1900-01-01` or `9999-12-31` | `none` or `unknown` as a real category answer; `0` is never proposed | shared rule | user: missing, zero, or real |
| `variants:<col>:<normal form>` | rows using a minority spelling among labels equal after case folding and removing punctuation and repeated spaces | codes where case is meaningful | shared rule | agent for case and punctuation only; user when the canonical label is unclear |
| `near-variants:<col>:<a>\|<b>` | rows of the rarer of two labels whose normalized forms are at least 0.92 similar (Jaro-Winkler), ignoring pairs differing only in digits; examples show the normalized forms | genuinely different short labels | shared rule | user |
| `whitespace:<col>` | values with leading or trailing whitespace | fixed-width codes where padding is meaningful | shared rule | agent |
| `negative:<col>` | negative values when at most 1% of values are negative, excluding flagged placeholders | refunds, adjustments, and signed differences | shared rule or not an issue | user |
| `range:<col>:<min>:<max>` | values outside a requested `--range` | none; the range is the user's | shared when the range is a validity rule; local when it is the investigation's period | user |
| `future-date:<col>` | dates after the scan date, excluding placeholder dates | due dates, plans, and expiries | shared rule or not an issue | user |
| `ancient-date:<col>` | dates before 1900, excluding placeholder dates | historical data | shared rule | user |
| `extreme:<col>` | values beyond five interquartile ranges from the quartiles, excluding flagged placeholders; not checked for key-like columns | heavy-tailed quantities such as revenue | usually not an issue or local | user |
| `orphans:<col>:<target>.<col>` | non-null rows whose value has no match in the `--ref` target, compared as text | references to records outside the landed extract | shared limitation; a correction only when the reference is wrong | user |
| `all-null:<col>` | every row null | a column the source never fills | shared limitation | agent |

Text-placeholder and type checks apply to columns DuckDB reads as text. A text column counts as typed when at least the threshold share of its non-placeholder values parse as `BIGINT` (integer text only), `DOUBLE`, `DATE`, `TIMESTAMP`, `BOOLEAN`, or a recognized date format. Numeric and date checks then run on the parsed values. Spelling-variant checks run on untyped text columns with at most 500 distinct values (`--max-categories`). Near-variant checks run on those with at most 200.

Null rates and the commonest co-null column patterns are reported for information, not as issues. A rescan reports null-rate changes so that placeholders converted to null can be confirmed.

## Scan file

`foundation/scans/<name>.json` holds the target, options, row count, per-column type, parsed type, non-null and distinct counts and null rate, candidate keys (complete and unique columns), null patterns, and every issue with up to ten examples. A rescan also holds the `baseline` it compares with and the `delta`. A plain scan starts a new baseline; `--rescan` keeps the earlier one, so repeated rescans still compare with the state before cleaning. `--rescan <name>` takes the baseline from another scan, such as the view's when scanning a local query. The scan name defaults to the view name, `<dataset>@<publication-id>`, `<source>@<acquisition-id>`, or the file stem; `--name` overrides it.

Examples are real values, up to ten per issue and 80 characters each. When the source register records restrictions on copying the source's values, ask before committing the scan file.

An issue whose `<name>#<key>` marker appears in a `foundation/quality.md` row is reported as recorded, with that row's ID and status. `record_cleaning.py` writes the marker into every issue row it adds.
