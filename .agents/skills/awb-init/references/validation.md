# Result validation helper

Call the project copy at `src/exploration/validate.py`.

`validate(frame, spec) -> list[dict]` always returns seven checks in order: `columns`, `row_counts`, `joins`, `nulls`, `scope`, `metrics`, `values`. Each check has exactly `name`, `outcome`, `detail` strings; outcomes are `pass`, `fail`, `not-applicable`. A missing spec key records `not-applicable` with `not assessed`, which is not a pass. Empty mechanical specifications assess zero items and pass; use substantive checks for the actual result.

`profile(frame, *, max_distinct=20) -> dict` returns `row_count` plus each column's `dtype`, `null_rate`, `distinct_count`, and most frequent `sample_values`. Expand beyond the sample when the business interpretation depends on other distinct values.

## Specification in settings

`run.py` builds each result's spec from `[results.<id>.validation]` in `settings.toml`, extended by run-time entries a producer returns (`row_counts`, `joins.left_rows`), saves the profile under `results/`, and stores the checks in the evidence file. Read failure details there and record them before promoting a finding.

- `required_columns`: list of names that must exist.
- `row_counts`: integer input count (compared with result length), or list of `{step, before, after, min_ratio?, max_ratio?}`. Default maximum ratio is 1.0. A nonzero input must remain nonempty unless an explicit minimum permits zero; zero input must stay zero. Supply observed counts and justified bounds for each relevant operation.
- `joins`: `{keys: [...], left_rows: int, keys_unique: bool}`; uniqueness defaults to true. Checks result length against left rows and inspects duplicate keys. For intentional multiplication, assess the relationship separately and explain it; this check will report the growth.
- `nulls`: mapping from column names to maximum null fractions (0–1).
- `scope`, `metrics`, `values`: each `{outcome, detail}` with a supported outcome and nonempty explanation. These record the analyst's judgment; the helper does not establish it. Document filters and grouping, metric meanings and assumptions, and interpretation-driving values respectively.
