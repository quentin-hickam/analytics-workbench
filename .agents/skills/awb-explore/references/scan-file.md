# The scan file

Read this for the scan file's exact name, or to name a section for `--show` beyond a column's `top` or a dimension's `values`.

## File name

A scan writes `investigations/<name>/exploration/eda/<scan>.json`, or `<scan>-<label>.json` with `--label`, and replaces any file already at that path. `resolve_source()`, `publication_name()`, and `output_path()` in `scripts/eda_scan.py` build `<scan>` in three steps:

1. **Source name.** A view gives its name as passed. A directory or Parquet file is named from its path after symlinks are resolved, which must lie inside the project. A directory gives its last two path parts relative to the project root joined by `-` (`data/parquet/shifts/p1` gives `shifts-p1`, and so does a link `data/parquet/shifts/current` to `p1`), or its one part when it sits directly under the root (`data` gives `data`). A Parquet file gives its file name without `.parquet`. This is the `dataset` name recorded in the scan.
2. **Replace.** Each run of characters outside `[A-Za-z0-9._-]`, which holds ASCII letters and digits only, becomes one `-`: `daily sales` gives `daily-sales`, `Ünïcode_view` gives `-n-code_view`.
3. **Trim.** Leading and trailing `-` and `.` characters are removed, and an empty result becomes `dataset`: `-n-code_view` gives `n-code_view`, `café` gives `caf`, `日本` gives `dataset`.

The label is appended after these steps, unchanged; `--label` accepts only a name that starts with an ASCII letter or digit, followed by any number of `[A-Za-z0-9._-]` (`1` is valid).

Different sources or labels can give the same file name: `sales` with `--label raw` and a view named `sales-raw` both write `sales-raw.json`, and `a + b` and `a/b` both write `a-b.json`. The later scan then overwrites the earlier one.

## Contents

`--show` takes dot-separated keys, and names a list item by its `name`, `dimension`, or `kind`, or by index.

Top-level keys:

- `format` (`awb-explore/1`), `generated_at`, `investigation`, `dataset` (name, kind, and the view definition file or publication path). The name is the source name from step 1 of the file name, before replacement and trimming.
- `scope`: `applied` filters with their sources, `skipped` settings with reasons, `not_set` choices with the options to pass, `rows_before`, `rows`, `settings_path`, `settings_note`, and `settings_unused`.
- `date_column`: name, source, and period, with `integer_years` true for an integer year column, whose period is the year.
- `grain`: `duplicate_rows`, `single_column_keys`, `near_unique_columns`, `column_pair_keys`, and `declared_key` (the columns of the one key that `--key` or the settings `key` declares, then its duplicated values, rows in them, and rows with a null key, or its `missing_columns`).
- `columns`: name, type, kind, nulls, null_rate, distinct, and unique. Numeric columns add min, max, mean, sd, quantiles p1 to p99, zeros, negatives, and outliers beyond 1.5 and 3 IQR. Text columns add blank strings and case-or-space variants with examples. Temporal columns add min, max, and coverage: period, series, gaps, and low periods. An integer year column chosen as the date column adds the same under `temporal`, with `integer_years` true and its periods written as years. Text, boolean, and low-cardinality numeric columns add `top` values with each value's share of non-null rows and `other_share`.
- `null_patterns`: the most common combinations of null columns, and null rates by period of the date column.
- `measure`: overall n, mean, sd, sum, and median. `by_dimension` holds each dimension's group count, variance explained (`eta_squared`), group statistics in `values`, and highest and lowest groups. `over_time` holds the series; `halves` holds the means before and after the midpoint of the date range; `contrary` lists the groups that moved against the overall trend.
- `associations`: with a measure, its Pearson correlation with each of up to 15 other numeric columns, with pair counts.
- `anomalies`: kind, column, detail, and route; the kinds are in [reading the scan](reading-the-scan.md).
