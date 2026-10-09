# Scan options, settings, and output

Read this when you need an option that SKILL.md doesn't name, when the summary prints a `not applied` line, or when the investigation's settings lack a key the scan needs.

## Dataset argument

- A canonical view name, as loaded from `foundation/views/*.sql` by the project's `session()` helper in `src/preparation/landing.py`. If that helper is missing, the scan exits and names the installer.
- A publication, as a project-relative path to a publication directory (every `*.parquet` beneath it) or to one `.parquet` file. Prefer the view. Scan a publication directly only to examine a publication the views don't read yet.

## Settings keys

The scan reads the investigation's `settings.toml`, or the file given with `--settings`. For each key it takes the first match in `[eda.<dataset>]`, then `[eda]`, then `[scope]`, then the top level. A table such as `[eda.shifts]` therefore overrides shared `[eda]` values for one dataset.

| Key | Meaning |
| --- | --- |
| `where` | SQL predicate, or a list of predicates combined with AND, that selects the investigation's population. |
| `date_column` | Date or timestamp column used for the period filter, coverage, trends, and null shifts by period. |
| `period_start`, `period_end` | Inclusive dates; applied to `date_column` cast to a date. |
| `measure` | Numeric column or SQL expression; a boolean gives a rate. |
| `dimensions` | List of grouping columns or SQL expressions. |
| `key` | Column or list of columns giving the expected grain. |
| `period` | `day`, `week`, `month`, `quarter`, or `year` for coverage and trends. |

Every applied filter is printed with its source, such as `scope.where` or `option`. A setting that does not fit the dataset is skipped and printed as `not applied` with the reason: a missing date column, an invalid measure or dimension, or absent key columns. A scope `where` that fails stops the scan, because exploring the wrong population would mislead. Correct it, give the dataset its own `[eda.<dataset>] where`, or pass `--where` or `--no-scope`. Top-level and `[scope]` keys the scan does not read, such as `population = "hourly staff"`, are listed as unread. Check whether they imply a filter the scan should apply.

EDA does not change settings. Pass exploratory choices as options. When the user settles a population or period choice for the investigation, record it in settings under the project rules.

## Options

| Option | Effect |
| --- | --- |
| `--investigation NAME` | Investigation other than the README's active one. |
| `--settings PATH` | Project-relative settings file; TOML is read, and other formats need options. |
| `--where SQL` | Repeatable; replaces the settings `where`. |
| `--date-column COL`, `--start DATE`, `--end DATE` | Replace the settings date column and period. |
| `--no-scope` | Ignore the settings `where` and period; option filters still apply. Use with `--label all` to compare the full dataset with the scoped one. |
| `--measure EXPR`, `--dimension EXPR` | Replace the settings measure and dimensions. With a measure and no dimensions, up to five text or boolean columns with 2 to 20 values are chosen and marked `auto`. |
| `--key COL` | Repeatable; declared grain to check. |
| `--period P` | Coverage and trend period. The default is set by the date span: day up to 92 days, month up to 10 years, year beyond that. |
| `--top N` | Top values kept per column and groups compared for contrary trends (default 10). |
| `--min-group N` | Minimum rows in each half for a contrary-trend group, and for the highest and lowest group means (default 30). |
| `--min-r R` | Smallest absolute correlation printed (default 0.5); the file holds every pair. |
| `--label NAME` | Writes `<dataset>-<NAME>.json`, so a second scope does not replace the first. |
| `--json` | Prints compact JSON instead of Markdown. |

## Output file

Each scan replaces `investigations/<name>/exploration/eda/<dataset>[-<label>].json`. The scan uses one file per dataset and scope for three reasons. EDA proceeds one dataset at a time, follow-ups need a predictable path, and the latest scan of a scope is the one that matters. The file lives with the investigation's other exploration, outside its evidence and records, and the evidence helper's default producing code excludes it. It is exploration, so Git tracks it as an investigation file and no result cites it.

Top-level keys:

- `format` (`awb-eda/1`), `generated_at`, `investigation`, `dataset` (name, kind, and the view definition file or publication path).
- `scope`: `applied` filters with their sources, `skipped` settings with reasons, `rows_before`, `rows`, `settings_path`, `settings_note`, and `settings_unused`.
- `date_column`: name, source, and period.
- `grain`: `duplicate_rows`, `single_column_keys`, `near_unique_columns`, `column_pair_keys`, and `declared_key` (duplicated values, rows in them, rows with a null key).
- `columns`: name, type, kind, nulls, null_rate, distinct, and unique. Numeric columns add min, max, mean, sd, quantiles p1 to p99, zeros, negatives, and outliers beyond 1.5 and 3 IQR. Text columns add blank strings and case-or-space variants with examples. Temporal columns add min, max, and coverage: period, series, gaps, and low periods. Text, boolean, and low-cardinality numeric columns add `top` values with each value's share of non-null rows and `other_share`.
- `null_patterns`: the most common combinations of null columns, and null rates by period of the date column.
- `measure`: overall n, mean, sd, sum, and median. `by_dimension` holds each dimension's group count, variance explained (`eta_squared`), group statistics, and highest and lowest groups. `over_time` holds the series; `halves` holds the means before and after the midpoint of the date range; `contrary` lists the groups that moved against the overall trend.
- `associations`: Pearson correlation for every pair of up to 15 numeric columns plus the measure, with pair counts.
- `anomalies`: kind, column, detail, and route; listed in [reading the scan](reading-the-scan.md).
- `suggested_records`: draft `unresolved_issues` and `next_steps` lines for `state.md`.
