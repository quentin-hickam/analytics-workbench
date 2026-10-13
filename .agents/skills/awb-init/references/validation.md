# Result validation helper

Call the project copy at `src/exploration/validate.py`.

`validate(frame, spec) -> list[dict]` always returns seven checks in this order: `columns`, `row_counts`, `joins`, `nulls`, `scope`, `metrics`, `values`. Each check has exactly the `name`, `outcome`, and `detail` strings. The outcomes are `pass`, `fail`, and `not-applicable`. If a spec key is missing, the check records `not-applicable` with `not assessed`, and this is not a pass. Empty mechanical specifications assess zero items and pass. Use substantive checks for the actual result.

`profile(frame, *, max_distinct=20) -> dict` returns `row_count`, and for each column the `dtype`, `null_rate`, `distinct_count`, and most frequent `sample_values`. When the business interpretation depends on other distinct values, examine more values than the sample.

## Specification in settings

`run.py` builds the spec of each result from `[results.<id>.validation]` in `settings.toml`. Run-time entries that a producer returns (`row_counts`, `joins.left_rows`) extend that spec. `run.py` saves the profile under `results/` and stores the checks in the evidence file. Read the failure details in the evidence file, and record them before you promote a finding.

- `required_columns`: a list of names that must exist.
- `row_counts`: an integer input count (compared with the result length), or a list of `{step, before, after, min_ratio?, max_ratio?}`. The default maximum ratio is 1.0. A nonzero input must stay nonempty, unless an explicit minimum permits zero. A zero input must stay zero. For each relevant operation, supply the observed counts and justified bounds.
- `joins`: `{keys: [...], left_rows: int, keys_unique: bool}`. Uniqueness defaults to true. The check compares the result length with the left rows and examines duplicate keys. For intentional multiplication, assess the relationship separately and explain it. This check will report the growth.
- `nulls`: a mapping from column names to maximum null fractions (0–1).
- `scope`, `metrics`, `values`: each is `{outcome, detail}`, with a supported outcome and a nonempty explanation. These record the judgment of the analyst. The helper does not establish that judgment. Document these items:
  - In `scope`: filters and grouping.
  - In `metrics`: metric meanings and assumptions.
  - In `values`: interpretation-driving values.
