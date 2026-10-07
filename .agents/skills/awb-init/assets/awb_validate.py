"""Shared result validation for an analytics workbench (Python 3.10+, pandas).

Copy this file to the project's src/exploration/validate.py on first use and
import it from there, never from the skill folder. It measures without interpreting.

A validation record is a list of `{name, outcome: "pass"|"fail"|"not-applicable", detail}`; another ticket's `record_evidence(checks=...)` stores that list unchanged, so `validate()` must return exactly that shape. The seven check names are fixed: columns, row_counts, joins, nulls, scope, metrics, values.
"""

import json

import pandas as pd


CHECK_NAMES = ("columns", "row_counts", "joins", "nulls", "scope", "metrics", "values")


def _require_frame(frame):
    if not isinstance(frame, pd.DataFrame):
        raise TypeError("frame must be a pandas.DataFrame")


def _first_failure(failures):
    suffix = f" (+{len(failures) - 1} more)" if len(failures) > 1 else ""
    return failures[0].rstrip(".") + suffix + "."


def _null_rate(series):
    return float(series.isna().mean()) if len(series) else 0.0


def _plain_value(value):
    if hasattr(value, "item"):
        value = value.item()
    try:
        json.dumps(value)
    except (TypeError, ValueError):
        return str(value)
    return value


def profile(frame, *, max_distinct=20) -> dict:
    """Return neutral per-column measurements and frequent non-null samples."""
    _require_frame(frame)
    columns = {}
    for name, series in frame.items():
        counts = series.value_counts()
        # Categorical value_counts includes unused categories; samples must be observed values.
        values = counts[counts > 0].head(max_distinct).index
        samples = [_plain_value(value) for value in values]
        columns[str(name)] = {"dtype": str(series.dtype),
                              "null_rate": round(_null_rate(series), 4),
                              "distinct_count": int(series.nunique(dropna=True)),
                              "sample_values": samples}
    return {"row_count": len(frame), "columns": columns}


def validate(frame, spec) -> list[dict]:
    """Measure mechanical checks and record supplied judgments in fixed order."""
    _require_frame(frame)
    for key in spec:
        if key not in ("required_columns", *CHECK_NAMES[1:]):
            raise ValueError(f"Unknown validation spec key: {key}")
    records = [{"name": name, "outcome": "not-applicable", "detail": "not assessed"}
               for name in CHECK_NAMES]
    if "required_columns" in spec:
        missing = [column for column in spec["required_columns"] if column not in frame.columns]
        records[0].update(outcome="fail" if missing else "pass", detail=(
            f"Missing required columns: {', '.join(missing)}." if missing else
            f"{len(spec['required_columns'])} required columns present."))
    if "row_counts" in spec:
        steps = spec["row_counts"]
        if isinstance(steps, int):
            steps = [{"step": "result", "before": steps, "after": len(frame)}]
        # Supplied empty specs pass with zero assessed items; only absent keys are not assessed.
        failures = []
        for step in steps:
            before, after = step["before"], step["after"]
            if before == 0:
                # Division by zero has no ratio; report it as undefined, not a fabricated number.
                if after != 0:
                    failures.append(f"{step['step']}: {before} -> {after} rows, ratio undefined "
                                    "violates zero-input bound (after must be 0).")
                continue
            ratio = after / before
            maximum = step.get("max_ratio", 1.0)
            if ratio > maximum:
                failures.append(f"{step['step']}: {before} -> {after} rows, ratio {ratio:.2f} "
                                f"exceeds max_ratio {maximum:.2f}.")
            elif "min_ratio" in step and ratio < step["min_ratio"]:
                failures.append(f"{step['step']}: {before} -> {after} rows, ratio {ratio:.2f} "
                                f"below min_ratio {step['min_ratio']:.2f}.")
            elif "min_ratio" not in step and after == 0 < before:
                failures.append(f"{step['step']}: {before} -> {after} rows, ratio {ratio:.2f} "
                                "violates non-empty result bound.")
        records[1].update(outcome="fail" if failures else "pass", detail=(
            _first_failure(failures) if failures else
            f"{len(steps)} steps checked; last {before} -> {after} rows." if steps else
            "0 steps checked."))
    if "joins" in spec:
        join = spec["joins"]
        failures = []
        missing = [key for key in join["keys"] if key not in frame.columns]
        if len(frame) > join["left_rows"]:
            failures.append(f"Join grew from {join['left_rows']} to {len(frame)} rows.")
        failures.extend(f"Missing join key: {key}." for key in missing)
        # An empty key list has no uniqueness to inspect; missing keys prevent inspection.
        if not missing and join["keys"] and join.get("keys_unique", True):
            duplicates = frame.loc[frame.duplicated(join["keys"], keep=False)]
            if len(duplicates):
                count = len(duplicates[join["keys"]].drop_duplicates())
                failures.append(f"{len(duplicates)} duplicated rows across {count} "
                                "distinct duplicated keys.")
        records[2].update(outcome="fail" if failures else "pass", detail=(
            _first_failure(failures) if failures else
            f"Join has {len(frame)} rows from {join['left_rows']} left rows."))
    if "nulls" in spec:
        failures, rates = [], []
        for column, threshold in spec["nulls"].items():
            if column not in frame.columns:
                failures.append(f"Missing null-check column: {column}.")
                continue
            rate = _null_rate(frame[column])
            rates.append(f"{column} {rate:.3f}")
            if rate > threshold:
                failures.append(f"{column} null rate {rate:.3f} exceeds {threshold:.3f}.")
        records[3].update(outcome="fail" if failures else "pass", detail=(
            _first_failure(failures) if failures else f"Null rates: {', '.join(rates)}." if rates else
            "0 null thresholds checked."))
    for record in records[4:]:
        if record["name"] in spec:
            judgment = spec[record["name"]]
            if (judgment.get("outcome") not in ("pass", "fail", "not-applicable")
                    or not isinstance(judgment.get("detail"), str) or not judgment["detail"]):
                raise ValueError(f"Invalid {record['name']} judgment: supply outcome and non-empty detail")
            record.update(outcome=judgment["outcome"], detail=judgment["detail"])
    return records
