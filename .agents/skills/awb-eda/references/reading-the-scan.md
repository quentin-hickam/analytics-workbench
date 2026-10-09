# Reading the scan

Read this for an anomaly kind's confirmation check, or when you cannot tell a shared data problem from a real pattern. The scan reports anomalies mechanically; each needs a disposition (SKILL.md step 3) before you record it.

## Anomaly kinds

| Kind | Reported when | Confirmation check |
| --- | --- | --- |
| `duplicate-rows` | Whole rows repeat. | Check the stated grain. An event log can repeat legitimately; a dimension table cannot. |
| `key-violated` | The declared key has duplicated or null values. | List the duplicates with a follow-up query. Decide whether the key or the data is wrong. |
| `key-missing` | A `--key` column is absent. | Correct the option. |
| `all-null` | Every in-scope row is null. | Scan with `--no-scope --label all`. If the column is populated outside scope, the gap is in scope only. |
| `constant` | One value in scope. | Usually the scope filter, such as one region. The column cannot explain variation here. |
| `high-nulls` | At least 20% null. | Decide whether missingness matters to the question. Look at `null_patterns` for co-missing columns. |
| `null-shift` | The null rate moves 25 points or more across periods. | Often a field introduced or dropped mid-history, or a load change. Find the change point in `null_patterns.by_period`. |
| `case-or-space-variants` | Values differ only by case or surrounding spaces. | The examples show the spellings. Normalizing them is a shared correction. |
| `blank-strings` | Blank strings sit beside nulls. | Two encodings of missing. |
| `rare-negatives` | Under 1% of values are negative. | Reversals or adjustments can be real; check the source's meaning. |
| `extreme-values` | Values lie beyond 3 IQR. | Heavy tails are common in amounts and durations. Check whether the extremes are plausible units, and whether results change without them. |
| `future-dates`, `sentinel-dates` | Dates after today, or before 1901. | Placeholders such as 1900-01-01 or 9999-12-31 are data problems; scheduled future events may be real. |
| `period-gaps` | Periods with no rows inside the date range. | A real absence, such as a closure, is a local matter; a missing load is a shared problem. Check the source's acquisitions. |
| `low-periods` | Interior periods under half the median rows. | Partial loads look like this, as do seasonal lows. The first and last periods are excluded, because they are often partial by construction. |
| `near-duplicate-columns` | Absolute correlation of 0.98 or more. | One column may be derived from the other; count the pair as one piece of evidence. |
| `contrary-trend` | A group's mean moved against the overall mean between the halves of the date range, by more than about two standard errors. | Keep these: they challenge an expected explanation. Confirm with the group's own series in a follow-up, since the scan compares halves rather than fitting a trend. |

## Interpretation checklist

- **Scope first.** When a distribution is surprising and the scope filter could produce it, scan again with `--no-scope --label all` and compare.
- **Small groups** make the highest and lowest means unstable; `--min-group` sets the minimum.
- **Correlation** is Pearson: linear, and sensitive to extremes. A strong correlation between a measure and its own components is arithmetic, not explanation.
