"""Shared result validation for an analytics workbench project (Python 3.10+, pandas only).

Copy this file to the project's src/exploration/validate.py on first use and import it from there;
never from the skill folder. It measures without interpreting.

validate() returns the validation record: a list of checks {name, outcome, detail}, one per name in
CHECK_NAMES and in that order, with outcome one of OUTCOMES and every value a str. Store the list
unchanged with the result's evidence. profile() reports the counts and values to inspect.
src/awb.py runs cli_profile() as `python3 src/awb.py profile`; it also needs DuckDB and the
project's src/preparation/landing.py for its session.
"""

import argparse
import importlib.util
import json
import numbers
import re
import sys
from pathlib import Path

import pandas as pd

CHECK_NAMES = ("columns", "row_counts", "joins", "nulls", "scope", "metrics", "values")
OUTCOMES = ("pass", "fail", "not-applicable")
JUDGMENTS = ("scope", "metrics", "values")  # supplied by the analyst as {outcome, detail}


def _require_frame(frame) -> None:
    if not isinstance(frame, pd.DataFrame):
        raise TypeError("frame must be a pandas.DataFrame")


def _null_rate(series) -> float:
    return float(series.isna().mean()) if len(series) else 0.0


def _plain_value(value):
    """Return a strict-JSON sample: numpy scalars via .item(); non-JSON values and inf via str."""
    if hasattr(value, "item"):
        value = value.item()
    try:
        json.dumps(value, allow_nan=False)
    except (TypeError, ValueError):
        return str(value)
    return value


def profile(frame, *, max_distinct=20) -> dict:
    """Return row count and per-column dtype, null rate, distinct count, and frequent samples."""
    _require_frame(frame)
    if max_distinct < 0:
        raise ValueError("max_distinct must be 0 or more")
    columns = {}
    for name, series in frame.items():
        counts = series.value_counts()
        counts = counts[counts > 0]  # categorical counts list unused categories; keep observed ones
        columns[str(name)] = {
            "dtype": str(series.dtype),
            "null_rate": round(_null_rate(series), 4),
            "distinct_count": int(series.nunique(dropna=True)),
            "sample_values": [_plain_value(value) for value in counts.head(max_distinct).index],
        }
    return {"row_count": len(frame), "columns": columns}


# Each mechanical check returns (failures, pass_detail). A supplied but empty spec assesses
# zero items and passes; only an absent key is recorded as not assessed.

def _columns(frame, required):
    missing = [column for column in required if column not in frame.columns]
    failures = [f"Missing required columns: {', '.join(missing)}."] if missing else []
    return failures, f"Required columns present: {len(required)}."


def _row_counts(frame, steps):
    # A count read back from a query result is often a numpy integer; a bool is not a count.
    if isinstance(steps, numbers.Integral) and not isinstance(steps, bool):
        steps = [{"step": "result", "before": int(steps), "after": len(frame)}]
    failures = []
    for step in steps:
        before, after = step["before"], step["after"]
        counts = f"{step['step']}: {before} -> {after} rows"
        if before == 0:
            if after != 0:  # no ratio exists; an empty input must stay empty
                failures.append(f"{counts} from an empty input, which must stay empty.")
            continue
        ratio = after / before
        maximum = step.get("max_ratio", 1.0)
        minimum = step.get("min_ratio")
        if ratio > maximum:
            failures.append(f"{counts}, ratio {ratio:.2f} exceeds max_ratio {maximum:.2f}.")
        elif minimum is not None and ratio < minimum:
            failures.append(f"{counts}, ratio {ratio:.2f} below min_ratio {minimum:.2f}.")
        elif minimum is None and after == 0:
            failures.append(f"{counts}, ratio 0.00 violates non-empty result bound.")
    if not steps:
        return failures, "Steps checked: 0."
    last = steps[-1]
    return failures, f"Steps checked: {len(steps)}; last {last['before']} -> {last['after']} rows."


def _joins(frame, join):
    keys, left_rows = join["keys"], join["left_rows"]
    failures = []
    if len(frame) > left_rows:  # row multiplication is reported before key duplication
        failures.append(f"Join grew from {left_rows} to {len(frame)} rows.")
    missing = [key for key in keys if key not in frame.columns]
    failures += [f"Missing join key: {key}." for key in missing]
    # Uniqueness needs every key present; an empty key list has nothing to inspect.
    if keys and not missing and join.get("keys_unique", True):
        duplicated = frame.loc[frame.duplicated(keys, keep=False), keys]
        if len(duplicated):
            distinct = len(duplicated.drop_duplicates())
            failures.append(f"{len(duplicated)} duplicated rows across {distinct} "
                            "distinct duplicated keys.")
    return failures, f"Join has {len(frame)} rows from {left_rows} left rows."


def _nulls(frame, thresholds):
    failures, rates = [], []
    for column, threshold in thresholds.items():
        if column not in frame.columns:
            failures.append(f"Missing null-check column: {column}.")
            continue
        rate = _null_rate(frame[column])
        rates.append(f"{column} {rate:.3f}")
        if rate > threshold:
            failures.append(f"{column} null rate {rate:.3f} exceeds {threshold:.3f}.")
    return failures, f"Null rates: {', '.join(rates)}." if rates else "Null thresholds checked: 0."


MECHANICAL = {"columns": ("required_columns", _columns), "row_counts": ("row_counts", _row_counts),
              "joins": ("joins", _joins), "nulls": ("nulls", _nulls)}
SPEC_KEYS = (*(key for key, _ in MECHANICAL.values()), *JUDGMENTS)


def _judgment(name, supplied) -> dict:
    if (not isinstance(supplied, dict) or supplied.get("outcome") not in OUTCOMES
            or not isinstance(supplied.get("detail"), str) or not supplied["detail"]):
        raise ValueError(f"Invalid {name} judgment: supply an outcome in {OUTCOMES} "
                         "and a non-empty detail")
    return {"name": name, "outcome": supplied["outcome"], "detail": supplied["detail"]}


def _measured(name, failures, pass_detail) -> dict:
    if not failures:
        return {"name": name, "outcome": "pass", "detail": pass_detail}
    more = f" (+{len(failures) - 1} more)" if len(failures) > 1 else ""
    return {"name": name, "outcome": "fail", "detail": failures[0].rstrip(".") + more + "."}


def validate(frame, spec) -> list[dict]:
    """Run the mechanical checks in spec, record its judgments, and return all seven checks."""
    _require_frame(frame)
    for key in spec:
        if key not in SPEC_KEYS:
            raise ValueError(f"Unknown validation spec key: {key}")
    checks = []
    for name in CHECK_NAMES:
        key, measure = MECHANICAL.get(name, (name, None))
        if key not in spec:
            checks.append({"name": name, "outcome": "not-applicable", "detail": "not assessed"})
        elif measure is None:
            checks.append(_judgment(name, spec[key]))
        else:
            checks.append(_measured(name, *measure(frame, spec[key])))
    return checks


PROFILE_MAX_ROWS = 1_000_000
_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _landing(root):
    """Load the project's landing helper by path; awb.py puts only this folder on sys.path."""
    path = Path(root) / "src/preparation/landing.py"
    if not path.is_file():
        raise FileNotFoundError(f"profile needs {path} for its session")
    spec = importlib.util.spec_from_file_location("awb_profile_landing", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cli_profile(root: Path, argv: list[str]) -> int:
    """Profile a view, query file, or SQL text in a fresh session; print a per-column summary."""
    parser = argparse.ArgumentParser(prog="awb.py profile", description=cli_profile.__doc__)
    parser.add_argument("source",
                        help="view name, query file (absolute or project-relative), or SQL text")
    parser.add_argument("--out", help="write the full profile JSON to this file")
    parser.add_argument("--max-rows", type=int, default=PROFILE_MAX_ROWS,
                        help="profile a repeatable sample of this many rows when the result is "
                             f"larger (default {PROFILE_MAX_ROWS})")
    args = parser.parse_args(argv)
    if args.max_rows < 1:
        parser.error("--max-rows must be 1 or more")
    out = None
    try:
        landing = _landing(root)
        out = landing._under(root, args.out) if args.out else None
        with landing.session(root) as connection:
            if _IDENTIFIER.fullmatch(args.source) and connection.execute(
                    "SELECT 1 FROM information_schema.tables WHERE lower(table_name) = lower(?)",
                    [args.source]).fetchall():
                text = f'SELECT * FROM "{args.source}"'
            else:
                text = landing._sql_argument(root, args.source)
                if text == args.source and _IDENTIFIER.fullmatch(text):
                    raise ValueError(f"no view or query file named {args.source}")
            relation = connection.sql(text)
            if relation is None:
                raise ValueError("the SQL returns no rows; end it with a query")
            total = relation.aggregate("count(*)").fetchone()[0]
            if total > args.max_rows:
                # A seeded reservoir sample bounds memory and repeats across runs.
                relation = relation.query("awb_profiled", "SELECT * FROM awb_profiled USING SAMPLE "
                                          f"reservoir({args.max_rows} ROWS) REPEATABLE (0)")
            result = profile(relation.df())
        if total > result["row_count"]:
            result["sampled_from"] = total
        if out is not None:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    except Exception as error:
        message = f"{error}: {error.__cause__}" if error.__cause__ else str(error)
        print(f"profile: {' '.join(message.split())}", file=sys.stderr)
        return 1
    if "sampled_from" in result:
        print(f"rows: {result['row_count']} profiled of {total} (repeatable sample; null rates and "
              "distinct counts are estimates)")
    else:
        print(f"rows: {total}")
    print(landing._markdown_table(
        ["column", "type", "null rate", "distinct"],
        [(name, column["dtype"], column["null_rate"], column["distinct_count"])
         for name, column in result["columns"].items()]))
    if out is not None:
        print(f"full profile in {args.out}")
    return 0
