# Reading the scan

Read this when an anomaly kind is unfamiliar, or when you cannot tell a shared data problem from a real pattern. The scan flags mechanically, and each flag needs your judgment before you record it.

## Anomaly kinds

| Kind | Flagged when | Route | Confirm before routing |
| --- | --- | --- | --- |
| `duplicate-rows` | Whole rows repeat. | awb-clean | Check the stated grain. An event log can repeat legitimately; a dimension table cannot. |
| `key-violated` | The declared key has duplicated or null values. | awb-clean | List the duplicates with a follow-up query. Decide whether the key or the data is wrong. |
| `key-missing` | A `--key` column is absent. | investigation | Correct the option. |
| `all-null` | Every in-scope row is null. | awb-clean | Rerun with `--no-scope`. If the column is populated outside scope, the gap is in scope only. |
| `constant` | One value in scope. | investigation | Usually the scope filter, such as one region. The column cannot explain variation here. |
| `high-nulls` | At least 20% null. | investigation | Decide whether missingness matters to the question. Look at `null_patterns` for co-missing columns. |
| `null-shift` | The null rate moves 25 points or more across periods. | awb-clean | Often a field introduced or dropped mid-history, or a load change. Find the change point in `null_patterns.by_period`. |
| `case-or-space-variants` | Values differ only by case or surrounding spaces. | awb-clean | The examples show the spellings. Normalizing them is a shared correction, not a local fix. |
| `blank-strings` | Blank strings sit beside nulls. | awb-clean | Two encodings of missing. |
| `rare-negatives` | Under 1% of values are negative. | awb-clean | Reversals or adjustments can be real; check the source's meaning. |
| `extreme-values` | Values lie beyond 3 IQR. | investigation | Heavy tails are common in amounts and durations. Check whether the extremes are plausible units, and whether results change without them. |
| `future-dates`, `sentinel-dates` | Dates after today, or before 1901. | awb-clean | Placeholders such as 1900-01-01 or 9999-12-31 are data problems; scheduled future events may be real. |
| `period-gaps` | Periods with no rows inside the date range. | awb-clean | A real absence, such as a closure, is not a data problem. A missing load is. Check the source's acquisitions. |
| `low-periods` | Interior periods under half the median rows. | awb-clean | Partial loads look like this, as do seasonal lows. The first and last periods are not flagged, because they are often partial by construction. |
| `near-duplicate-columns` | Absolute correlation of 0.98 or more. | investigation | One column may be derived from the other. Do not treat the pair as independent evidence. |
| `contrary-trend` | A group's mean moved against the overall mean between the halves of the date range, by more than about two standard errors. | investigation | Keep these. They are results that challenge an expected explanation. |

Route `awb-clean` means a possible shared data problem, and a problem in the canonical data affects every investigation. Confirm it with a follow-up query or the source register before handing it over. If it turns out to be a question-specific exclusion, it stays local in a saved query and does not go to awb-clean.

## Interpretation checklist

- **Scope first.** A surprising distribution is often the filter. Compare the scoped scan with a `--no-scope --label all` scan before attributing a pattern to the population.
- **Variance explained** (`eta_squared`) is the share of the measure's variance that group means account for. It rises with the number of groups, so compare a 40-group dimension with a 3-group one cautiously. Small groups make the highest and lowest means unstable; `--min-group` sets the minimum.
- **Composition.** An overall trend can come from a shift in group mix rather than within-group change. When a dimension explains much variance and the group shares change over time, cross the dimension with the period in a follow-up before reading the overall trend.
- **Correlation** is Pearson: linear, and sensitive to extremes. A strong correlation between a measure and its own components is arithmetic, not explanation.
- **Contrary trends** compare the halves of the date range, not a fitted trend. Confirm with the group's own series in a follow-up.
- **Candidate explanations** stay candidates until the composition entry computes them with the investigation's settings and validation. Phrase them as questions in Next steps, not as findings.
