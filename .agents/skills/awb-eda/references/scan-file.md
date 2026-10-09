# The scan file

Read this to name a section for `--show` beyond a column's `top` or a dimension's `values`. Each scan replaces `investigations/<name>/exploration/eda/<dataset>[-<label>].json`. `--show` takes dot-separated keys, and names a list item by its `name`, `dimension`, or `kind`, or by index.

Top-level keys:

- `format` (`awb-eda/1`), `generated_at`, `investigation`, `dataset` (name, kind, and the view definition file or publication path).
- `scope`: `applied` filters with their sources, `skipped` settings with reasons, `not_set` choices with the options to pass, `rows_before`, `rows`, `settings_path`, `settings_note`, and `settings_unused`.
- `date_column`: name, source, and period.
- `grain`: `duplicate_rows`, `single_column_keys`, `near_unique_columns`, `column_pair_keys`, and `declared_key` (duplicated values, rows in them, rows with a null key).
- `columns`: name, type, kind, nulls, null_rate, distinct, and unique. Numeric columns add min, max, mean, sd, quantiles p1 to p99, zeros, negatives, and outliers beyond 1.5 and 3 IQR. Text columns add blank strings and case-or-space variants with examples. Temporal columns add min, max, and coverage: period, series, gaps, and low periods. Text, boolean, and low-cardinality numeric columns add `top` values with each value's share of non-null rows and `other_share`.
- `null_patterns`: the most common combinations of null columns, and null rates by period of the date column.
- `measure`: overall n, mean, sd, sum, and median. `by_dimension` holds each dimension's group count, variance explained (`eta_squared`), group statistics in `values`, and highest and lowest groups. `over_time` holds the series; `halves` holds the means before and after the midpoint of the date range; `contrary` lists the groups that moved against the overall trend.
- `associations`: with a measure, its Pearson correlation with each of up to 15 other numeric columns, with pair counts.
- `anomalies`: kind, column, detail, and route; the kinds are in [reading the scan](reading-the-scan.md).
