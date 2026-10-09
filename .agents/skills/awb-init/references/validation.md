# Result validation helper

The [installer](../scripts/install_helpers.py) places this helper at `src/exploration/validate.py` and restores it when missing; run it, never copy by hand. Preserve a customized helper and call the project copy. It requires Python 3.10+ and pandas. A non-Python project ports the same interface and check record.

`profile(frame, *, max_distinct=20) -> dict` accepts a pandas DataFrame and returns `row_count` plus each column's `dtype`, `null_rate`, `distinct_count`, and most frequent `sample_values`. Save the complete profile to a file; inspect relevant columns and expand beyond the sample when the business interpretation depends on other distinct values.

`validate(frame, spec) -> list[dict]` always returns seven checks in order: `columns`, `row_counts`, `joins`, `nulls`, `scope`, `metrics`, `values`. Each check has exactly `name`, `outcome`, `detail` strings; outcomes are `pass`, `fail`, `not-applicable`. Preserve this list unchanged with result evidence. A missing spec key records `not-applicable` with `not assessed`, which is not a pass. Empty mechanical specifications assess zero items and pass; use substantive checks for the actual result.

## Specification

- `required_columns`: list of names that must exist.
- `row_counts`: integer input count (compared with result length), or list of `{step, before, after, min_ratio?, max_ratio?}`. Default maximum ratio is 1.0. A nonzero input must remain nonempty unless an explicit minimum permits zero; zero input must stay zero. Supply observed counts and justified bounds for each relevant operation.
- `joins`: `{keys: [...], left_rows: int, keys_unique: bool}`; uniqueness defaults to true. Checks result length against left rows and inspects duplicate keys. For intentional multiplication, assess the relationship separately and explain it; this check will report the growth.
- `nulls`: mapping from column names to maximum null fractions (0–1).
- `scope`, `metrics`, `values`: each `{outcome, detail}` with a supported outcome and nonempty explanation. These record the analyst's judgment; the helper does not establish it. Document filters/grouping, metric meanings/assumptions, and interpretation-driving values respectively.

## Profile from the command line

Profile a view, a saved query, or SQL text with the command instead of writing a snippet:

```sh
python3 src/awb.py profile orders --out investigations/order-quality/exploration/orders-profile.json
python3 src/awb.py profile investigations/order-quality/exploration/missing-ids.sql --out investigations/order-quality/exploration/missing-ids-profile.json
```

A bare name that matches a view or table in a fresh `session(root)` profiles `select * from` it; otherwise the argument is a query file when it names an existing file (absolute or project-relative), else SQL text. The command prints the row count and, per column, type, null rate, and distinct count. `--out` saves the complete `profile()` result as JSON, including sample values; relative paths are project-relative. It needs DuckDB and `src/preparation/landing.py`. Errors print one line on stderr and exit 1.

A result larger than `--max-rows` (default 1,000,000) is profiled on a repeatable reservoir sample of that many rows, which bounds memory. The summary says so, `row_count` is the sample size, and the JSON adds `sampled_from` with the full row count. Null rates and distinct counts are then sample estimates and distinct counts can be low; for exact figures, raise `--max-rows`, narrow the query, or aggregate in SQL with `python3 src/awb.py sql`.

## Save complete checks, return a compact summary

In the investigation's composition entry, use its actual result DataFrame, observed pre-filter count, and inspected judgments. This illustrative function assumes the scope and metric described in the judgments have been verified; adapt those details and thresholds before use. No join is performed in this example.

```python
import json
from collections import Counter
from pathlib import Path
from src.exploration.validate import profile, validate

def check_orders(frame, before_filter, output_directory):
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    profile_path = output / 'orders-profile.json'
    profile_path.write_text(json.dumps(profile(frame), indent=2) + '\n')
    checks = validate(frame, {
        'required_columns': ['order_id', 'amount'],
        'row_counts': [{'step': 'scope filter', 'before': before_filter,
                        'after': len(frame), 'min_ratio': 0.1, 'max_ratio': 1.0}],
        'nulls': {'order_id': 0, 'amount': 0},
        'scope': {'outcome': 'pass', 'detail': 'US orders in the settings period; one row per order.'},
        'metrics': {'outcome': 'pass', 'detail': 'Amount is booked USD revenue before refunds.'},
        'values': {'outcome': 'not-applicable', 'detail': 'No categorical value drives this result.'},
    })
    checks_path = output / 'orders-checks.json'
    checks_path.write_text(json.dumps(checks, indent=2) + '\n')
    print({'checks': dict(Counter(c['outcome'] for c in checks)),
           'failed_checks': [c['name'] for c in checks if c['outcome'] == 'fail'],
           'profile_path': str(profile_path), 'checks_path': str(checks_path)})
    return checks
```

Read relevant failure details from the saved checks. Understand and record failed checks before promoting a result to a finding. Pass the unchanged `checks` list to [result evidence](provenance.md); storing the summary alone does not satisfy validation.
