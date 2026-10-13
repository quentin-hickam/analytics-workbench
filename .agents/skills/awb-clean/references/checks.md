# Scan checks

## What each key counts

Counts are rows, unless the table says something different. `of` is the non-null values of the column, or all rows for row-level checks. Text values are compared after the leading and trailing whitespace is trimmed. This includes non-breaking spaces.

| Key | Counts | Common false positives |
| --- | --- | --- |
| `duplicate-rows` | rows that repeat another row exactly, after the first one | event data that has no timestamp or identifier, where identical rows are separate events |
| `duplicate-key:<cols>` | extra rows for key values that occur more than one time. The key is an explicit `--key` or, if there is none, near-unique columns and columns with names like `id`, `*_id`, or `key` | a near-unique attribute, such as an email, that is not the grain |
| `null-key:<cols>` | rows that are missing part of an explicit key | none |
| `parse:<col>:<type>` | non-placeholder values that do not parse, when at least 90% parse as the type | free-text columns that are mostly numeric |
| `date-formats:<col>` | when formats mix, the values that are not in the dominant format. When two formats fit all values, every value (the day-month order is ambiguous) | none |
| `text-typed:<col>:<type>` | values stored as text that parse as the type. This check is only for views and publications. Landed CSV is read as text on purpose | codes and identifiers that look numeric. Values with leading zeros stay text |
| `sentinel:<col>:<value>` | text placeholders (`""`, `N/A`, `null`, `none`, `-`, `?`, `unknown`, `missing`, `tbd`, and similar values). Numbers such as `-1`, `999`, or `9999` that are outside all other values. Placeholder dates such as `1900-01-01` or `9999-12-31` | `none` or `unknown` as a real category answer. `0` is not a placeholder candidate |
| `variants:<col>:<normal form>` | rows that use a minority spelling, among labels that are equal after case folding and after the removal of punctuation and repeated spaces | codes where case has a meaning |
| `near-variants:<col>:<a>\|<b>` | rows of the less frequent of two labels whose normalized forms have a similarity of at least 0.92 (Jaro-Winkler). Pairs that differ only in digits are ignored. The examples show the normalized forms | short labels that are really different |
| `whitespace:<col>` | values with leading or trailing whitespace | fixed-width codes where padding has a meaning |
| `negative:<col>` | negative values, when at most 1% of values are negative. Values that the `sentinel` check reports are not included | refunds, adjustments, and signed differences |
| `range:<col>:<min>:<max>` | values outside a requested `--range` | none. The range comes from the user |
| `future-date:<col>` | dates after the scan date, but not placeholder dates | due dates, plans, and expiry dates |
| `ancient-date:<col>` | dates before 1900, but not placeholder dates | historical data |
| `extreme:<col>` | values beyond five interquartile ranges from the quartiles. Values that the `sentinel` check reports are not included. Key-like columns do not get this check | heavy-tailed quantities such as revenue |
| `orphans:<col>:<target>.<col>` | non-null rows whose value has no match in the `--ref` target. The values are compared as text | none |
| `all-null:<col>` | every row is null | none |

The text-placeholder checks and the type checks apply to the columns that DuckDB reads as text. A text column counts as typed when at least the threshold share of its non-placeholder values parse as `BIGINT` (integer text only), `DOUBLE`, `DATE`, `TIMESTAMP`, `BOOLEAN`, or a recognized date format. Then the numeric checks and the date checks run on the parsed values. The spelling-variant checks run on untyped text columns that have at most 500 distinct values. The near-variant checks run on the untyped text columns that have at most 200 distinct values.

The scan reports null rates and the most common co-null column patterns only for information. A rescan reports changes in null rates, so that the conversion of placeholders to null can be confirmed.

## Scan file

`foundation/scans/<name>.json` stays local to the checkout. It contains these items:

- the target and the options
- the row count
- the type of each column, the parsed type, the non-null and distinct counts, and the null rate
- the candidate keys (complete and unique columns)
- the null patterns
- every issue, with up to ten examples

A rescan also contains the `baseline` that it compares with, and the `delta`. The default scan name is the view name, `<dataset>@<publication-id>`, `<source>@<acquisition-id>`, or the file stem. `--name` overrides the default name.

Examples are real values. Each issue has up to ten examples, and each example has up to 80 characters.

The scan reports an issue as recorded when `foundation/quality.json` links it to a `foundation/quality.md` row whose observation has the `<name>#<key>` marker of the issue. The report then gives the ID and status of that row, and the recorded count of the link. If a marker is on exactly one row and has no link, the link is made from the `(<count> of <of>)` of that row. `record_cleaning.py` writes the marker into every issue row that it adds. When it updates a recorded issue, it moves the count and date of the link to the reopened values. The observation keeps its first count.
