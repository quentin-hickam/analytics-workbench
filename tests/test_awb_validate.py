# Kept cases:
# test_empty_spec_records_all_seven_checks_as_not_assessed: seven check names in order, fixed record shape and not-applicable for absent checks.
# test_required_columns_names_every_missing_column_and_counts_present: columns fails on missing columns and passes when present.
# test_join_row_multiplication_reports_both_counts: joins fails on row multiplication.
# test_join_key_uniqueness_reports_rows_and_distinct_duplicate_keys: joins fails on duplicate keys unless uniqueness is disabled.
# test_null_threshold_reports_rate_and_threshold_and_summarizes_failures: nulls fails above the threshold and passes at the bound.
# test_judgments_preserve_supplied_outcome_and_detail: scope, metrics and values judgments pass through unchanged.
# test_invalid_judgment_raises_value_error: regression: non-dict judgment raises ValueError naming the check.
# test_row_counts_integer_uses_result_length_and_default_upper_bound: row_counts integer form passes or fails at the default upper bound.
# test_row_count_steps_apply_custom_bounds_and_summarize_first_failure: row_counts steps fail at explicit upper and lower bounds.
# test_profile_reports_type_nulls_distincts_and_capped_frequent_samples: profile contract shape, null rates and capped sample values.
# test_absent_judgments_are_not_assessed_beside_measured_checks: regression: absent judgments remain not-applicable beside measured checks.
# test_row_counts_accepts_numpy_integer_and_rejects_bool: regression: numpy integer row count accepted and bool rejected.
# test_profile_rejects_negative_limit_and_keeps_samples_strict_json: regressions: negative max_distinct rejected and inf samples serialize as strict JSON.

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


MODULE_PATH = (Path(__file__).resolve().parents[1]
               / ".agents/skills/awb-init/assets/awb_validate.py")
module_spec = importlib.util.spec_from_file_location("awb_validate", MODULE_PATH)
validation = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(validation)


def test_empty_spec_records_all_seven_checks_as_not_assessed():
    checks = validation.validate(pd.DataFrame(), {})
    names = ("columns", "row_counts", "joins", "nulls", "scope", "metrics", "values")
    assert validation.CHECK_NAMES == names
    assert checks == [
        {"name": name, "outcome": "not-applicable", "detail": "not assessed"}
        for name in names
    ]
    json.dumps(checks)


def test_required_columns_names_every_missing_column_and_counts_present():
    frame = pd.DataFrame({"order_id": [1]})
    assert validation.validate(frame, {
        "required_columns": ["order_id", "region", "order_date"],
    })[0] == {"name": "columns", "outcome": "fail",
              "detail": "Missing required columns: region, order_date."}
    assert validation.validate(frame, {"required_columns": ["order_id"]})[0] == {
        "name": "columns", "outcome": "pass", "detail": "Required columns present: 1.",
    }


def test_join_row_multiplication_reports_both_counts():
    frame = pd.DataFrame({"id": [1, 2, 3]})
    assert validation.validate(frame, {"joins": {"left_rows": 2, "keys": ["id"]}})[2] == {
        "name": "joins", "outcome": "fail", "detail": "Join grew from 2 to 3 rows.",
    }


def test_join_key_uniqueness_reports_rows_and_distinct_duplicate_keys():
    frame = pd.DataFrame({"id": [1, 1, 2, 2, 3]})
    assert validation.validate(frame, {"joins": {"left_rows": 5, "keys": ["id"]}})[2] == {
        "name": "joins", "outcome": "fail",
        "detail": "4 duplicated rows across 2 distinct duplicated keys.",
    }
    assert validation.validate(frame, {"joins": {
        "left_rows": 5, "keys": ["id"], "keys_unique": False,
    }})[2]["outcome"] == "pass"


def test_null_threshold_reports_rate_and_threshold_and_summarizes_failures():
    frame = pd.DataFrame({"customer_id": [None, 2, 3, 4, 5, 6, 7, 8],
                          "region": [None] * 8})
    assert validation.validate(frame, {"nulls": {
        "customer_id": 0.05, "region": 0.5,
    }})[3] == {"name": "nulls", "outcome": "fail",
              "detail": "customer_id null rate 0.125 exceeds 0.050 (+1 more)."}
    assert validation.validate(frame, {"nulls": {
        "customer_id": 0.125, "region": 1.0,
    }})[3] == {"name": "nulls", "outcome": "pass",
              "detail": "Null rates: customer_id 0.125, region 1.000."}


def test_judgments_preserve_supplied_outcome_and_detail():
    spec = {
        "scope": {"outcome": "pass", "detail": "2026 orders grouped by region."},
        "metrics": {"outcome": "fail", "detail": "Net revenue excludes unknown refunds."},
        "values": {"outcome": "not-applicable", "detail": "No categorical values used."},
    }
    assert validation.validate(pd.DataFrame(), spec)[4:] == [
        {"name": "scope", "outcome": "pass", "detail": "2026 orders grouped by region."},
        {"name": "metrics", "outcome": "fail", "detail": "Net revenue excludes unknown refunds."},
        {"name": "values", "outcome": "not-applicable", "detail": "No categorical values used."},
    ]


def test_invalid_judgment_raises_value_error():
    with pytest.raises(ValueError, match="scope"):
        validation.validate(pd.DataFrame(), {"scope": "pass"})


def test_row_counts_integer_uses_result_length_and_default_upper_bound():
    frame = pd.DataFrame({"id": [1, 2, 3]})
    assert validation.validate(frame, {"row_counts": 4})[1] == {
        "name": "row_counts", "outcome": "pass", "detail": "Steps checked: 1; last 4 -> 3 rows.",
    }
    assert validation.validate(frame, {"row_counts": 2})[1] == {
        "name": "row_counts", "outcome": "fail",
        "detail": "result: 2 -> 3 rows, ratio 1.50 exceeds max_ratio 1.00.",
    }


def test_row_count_steps_apply_custom_bounds_and_summarize_first_failure():
    steps = [
        {"step": "expand", "before": 4, "after": 6, "max_ratio": 1.25},
        {"step": "filter", "before": 6, "after": 1, "min_ratio": 0.5},
    ]
    assert validation.validate(pd.DataFrame(), {"row_counts": steps})[1] == {
        "name": "row_counts", "outcome": "fail",
        "detail": "expand: 4 -> 6 rows, ratio 1.50 exceeds max_ratio 1.25 (+1 more).",
    }
    assert validation.validate(pd.DataFrame(), {"row_counts": steps[1:]})[1] == {
        "name": "row_counts", "outcome": "fail",
        "detail": "filter: 6 -> 1 rows, ratio 0.17 below min_ratio 0.50.",
    }


def test_profile_reports_type_nulls_distincts_and_capped_frequent_samples():
    frame = pd.DataFrame({"region": ["west", "east", "west", None, "east", "north"],
                          7: [3, 3, 2, 3, 2, 1]})
    result = validation.profile(frame, max_distinct=2)
    assert result == {"row_count": 6, "columns": {
        "region": {"dtype": "object", "null_rate": 0.1667, "distinct_count": 3,
                   "sample_values": ["west", "east"]},
        "7": {"dtype": "int64", "null_rate": 0.0, "distinct_count": 3,
              "sample_values": [3, 2]},
    }}
    assert all(type(value) is int for value in result["columns"]["7"]["sample_values"])
    json.dumps(result)


def test_absent_judgments_are_not_assessed_beside_measured_checks():
    checks = validation.validate(pd.DataFrame({"id": [1]}), {"required_columns": ["id"]})
    assert checks[0]["outcome"] == "pass"
    assert checks[4:] == [{"name": name, "outcome": "not-applicable", "detail": "not assessed"}
                          for name in ("scope", "metrics", "values")]


def test_row_counts_accepts_numpy_integer_and_rejects_bool():
    frame = pd.DataFrame({"id": [1, 2, 3]})
    assert validation.validate(frame, {"row_counts": np.int64(4)})[1]["detail"] == (
        "Steps checked: 1; last 4 -> 3 rows.")
    with pytest.raises(TypeError):
        validation.validate(frame, {"row_counts": True})


def test_profile_rejects_negative_limit_and_keeps_samples_strict_json():
    with pytest.raises(ValueError, match="max_distinct"):
        validation.profile(pd.DataFrame({"id": [1]}), max_distinct=-1)
    result = validation.profile(pd.DataFrame({"x": [float("inf"), 1.5]}))
    assert result["columns"]["x"]["sample_values"] == ["inf", 1.5]
    json.dumps(result, allow_nan=False)
