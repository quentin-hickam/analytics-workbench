# Reading the scan

Read this file for the confirmation check of an anomaly kind. Also read it when you cannot see the difference between a shared data problem and a real pattern. The scan reports anomalies mechanically. Each anomaly needs a disposition (SKILL.md step 3) before you record it.

## Anomaly kinds

| Kind | Reported when | Confirmation check |
| --- | --- | --- |
| `duplicate-rows` | Whole rows repeat. | Check the stated grain. An event log can have correct repeated rows, but a dimension table cannot. |
| `key-violated` | The declared key has duplicated or null values. | List the duplicates with a follow-up query. Decide if the key or the data is wrong. |
| `key-missing` | A `--key` column is absent. | Correct the option. |
| `all-null` | Every in-scope row is null. | Scan with `--no-scope --label all`. If the column has values outside the scope, the gap is only in the scope. |
| `constant` | One value in scope. | The cause is usually the scope filter, such as one region. Here, the column cannot explain variation. |
| `high-nulls` | At least 20% null. | Decide if the missing values are important to the question. Look at `null_patterns` for co-missing columns. |
| `null-shift` | The null rate moves 25 points or more across periods. | The cause is often a field that was added or removed in the middle of the history, or a change in the load. Find the change point in `null_patterns.by_period`. |
| `extreme-values` | Values are beyond 3 IQR. | Heavy tails are common in amounts and durations. Check if the extremes are plausible units. Also check if the results change without them. |
| `period-gaps` | Periods with no rows in the date range. | A real absence, such as a closure, is a local matter. Check the acquisitions of the source. A missing load is a coverage limitation (SKILL step 5). |
| `low-periods` | Interior periods with fewer rows than half the median. | Partial loads look like this, and seasonal lows also look like this. The first and last periods are not included, because they are often partial by construction. |
| `contrary-trend` | The mean of a group moved against the overall mean between the halves of the date range, by more than about two standard errors. | Keep these, because they challenge an expected explanation. Confirm them in a follow-up with the series of the group. The reason is that the scan compares halves and does not fit a trend. |

Kinds with the route `awb-clean` that this table does not list: the scan of awb-clean checks them again with its own definitions. Confirm one of these kinds here only when the question depends on it.

## Interpretation checklist

- **Scope first.** When a distribution is unexpected and it is possible that the scope filter causes it, scan again with `--no-scope --label all` and compare.
- **Small groups** make the highest and lowest means unstable. `--min-group` sets the minimum.
- **Correlation** is Pearson. It is linear and sensitive to extremes. When a measure correlates with its own components, the correlation is arithmetic.
