# The scan file

Read this file to name a section for `--show` other than the `top` of a column or the `values` of a dimension. Each scan replaces `investigations/<name>/exploration/eda/<dataset>[-<label>].json`. `--show` takes dot-separated keys. It names a list item by its `name`, `dimension`, or `kind`, or by its index.

The top-level keys are:

- `format` (`awb-eda/1`), `generated_at`, `investigation`, `dataset` (name, kind, and the view definition file or publication path).
- `scope`: `applied` filters with their sources, `skipped` settings with their reasons, `not_set` choices with the options to give, `rows_before`, `rows`, `settings_path`, `settings_note`, and `settings_unused`.
- `date_column`: name, source, and period.
- `grain`: `duplicate_rows`, `single_column_keys`, `near_unique_columns`, `column_pair_keys`, and `declared_key` (duplicated values, rows in them, rows with a null key).
- `columns`: name, type, kind, nulls, null_rate, distinct, and unique. Numeric columns add min, max, mean, sd, quantiles p1 to p99, zeros, negatives, and outliers beyond 1.5 and 3 IQR. Text columns add blank strings and case-or-space variants with examples. Temporal columns add min, max, and coverage: period, series, gaps, and low periods. Text, boolean, and low-cardinality numeric columns add `top` values, with the share of non-null rows for each value, and `other_share`.
- `null_patterns`: the most common combinations of null columns, and null rates by period of the date column.
- `measure`: overall n, mean, sd, sum, and median. `by_dimension` holds, for each dimension, the group count, the variance explained (`eta_squared`), the group statistics in `values`, and the highest and lowest groups. `over_time` holds the series. `halves` holds the means before and after the midpoint of the date range. `contrary` lists the groups that moved against the overall trend.
- `associations`: when there is a measure, the Pearson correlation of the measure with each of up to 15 other numeric columns, with pair counts.
- `anomalies`: kind, column, detail, and route. The kinds are in [reading the scan](reading-the-scan.md).
