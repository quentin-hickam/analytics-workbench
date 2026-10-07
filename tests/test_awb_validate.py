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


def test_join_missing_key_is_named_even_when_uniqueness_is_disabled():
    checks = validation.validate(pd.DataFrame({"id": [1]}), {"joins": {
        "left_rows": 1, "keys": ["region", "order_date"], "keys_unique": False,
    }})
    assert checks[2] == {"name": "joins", "outcome": "fail",
                         "detail": "Missing join key: region (+1 more)."}


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


def test_null_check_names_missing_columns_and_empty_frame_has_zero_null_rate():
    assert validation.validate(pd.DataFrame(), {"nulls": {"id": 0.0}})[3] == {
        "name": "nulls", "outcome": "fail", "detail": "Missing null-check column: id.",
    }
    assert validation.validate(pd.DataFrame({"id": []}), {"nulls": {"id": 0.0}})[3] == {
        "name": "nulls", "outcome": "pass", "detail": "Null rates: id 0.000.",
    }


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


@pytest.mark.parametrize("name", ["scope", "metrics", "values"])
@pytest.mark.parametrize("judgment", [
    {"outcome": "unknown", "detail": "Inspected."},
    {"outcome": 1, "detail": "Inspected."},
    {"outcome": "pass", "detail": ""},
    {"outcome": "pass", "detail": 1},
    "pass",
])
def test_invalid_judgment_raises_value_error(name, judgment):
    with pytest.raises(ValueError, match=name):
        validation.validate(pd.DataFrame(), {name: judgment})


def test_unknown_spec_key_is_named_in_value_error():
    with pytest.raises(ValueError, match="row_count"):
        validation.validate(pd.DataFrame(), {"row_count": 10})


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


def test_row_count_positive_input_cannot_vanish_without_explicit_minimum():
    assert validation.validate(pd.DataFrame(), {"row_counts": 4})[1] == {
        "name": "row_counts", "outcome": "fail",
        "detail": "result: 4 -> 0 rows, ratio 0.00 violates non-empty result bound.",
    }
    assert validation.validate(pd.DataFrame(), {"row_counts": [
        {"step": "filter", "before": 4, "after": 0, "min_ratio": 0.0},
    ]})[1]["outcome"] == "pass"


def test_row_count_zero_input_passes_only_with_zero_output():
    assert validation.validate(pd.DataFrame(), {"row_counts": [
        {"step": "empty", "before": 0, "after": 0, "min_ratio": 0.5},
    ]})[1] == {"name": "row_counts", "outcome": "pass",
               "detail": "Steps checked: 1; last 0 -> 0 rows."}
    assert validation.validate(pd.DataFrame({"id": [1]}), {"row_counts": 0})[1] == {
        "name": "row_counts", "outcome": "fail",
        "detail": "result: 0 -> 1 rows from an empty input, which must stay empty.",
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


def test_profile_converts_timestamps_and_other_non_json_samples_to_strings():
    from decimal import Decimal

    result = validation.profile(pd.DataFrame({
        "date": [pd.Timestamp("2026-10-07"), pd.NaT],
        "amount": [Decimal("1.25"), None],
    }))
    assert result == {"row_count": 2, "columns": {
        "date": {"dtype": "datetime64[ns]", "null_rate": 0.5, "distinct_count": 1,
                 "sample_values": ["2026-10-07 00:00:00"]},
        "amount": {"dtype": "object", "null_rate": 0.5, "distinct_count": 1,
                   "sample_values": ["1.25"]},
    }}
    json.dumps(result)


@pytest.mark.parametrize("frame", [[], {"id": [1]}, pd.Series([1]), None])
@pytest.mark.parametrize("operation", ["profile", "validate"])
def test_public_functions_reject_non_dataframes(operation, frame):
    with pytest.raises(TypeError, match="pandas.DataFrame"):
        if operation == "profile":
            validation.profile(frame)
        else:
            validation.validate(frame, {})


def test_explicit_empty_mechanical_specs_assess_no_items_successfully():
    checks = validation.validate(pd.DataFrame(), {
        "required_columns": [], "row_counts": [], "joins": {"left_rows": 0, "keys": []},
        "nulls": {},
    })
    assert checks[:4] == [
        {"name": "columns", "outcome": "pass", "detail": "Required columns present: 0."},
        {"name": "row_counts", "outcome": "pass", "detail": "Steps checked: 0."},
        {"name": "joins", "outcome": "pass", "detail": "Join has 0 rows from 0 left rows."},
        {"name": "nulls", "outcome": "pass", "detail": "Null thresholds checked: 0."},
    ]


def test_profile_empty_and_all_null_columns_have_no_samples():
    assert validation.profile(pd.DataFrame({"id": pd.Series([], dtype="Int64")})) == {
        "row_count": 0, "columns": {"id": {"dtype": "Int64", "null_rate": 0.0,
                                          "distinct_count": 0, "sample_values": []}},
    }
    assert validation.profile(pd.DataFrame({"id": [None, None]})) == {
        "row_count": 2, "columns": {"id": {"dtype": "object", "null_rate": 1.0,
                                          "distinct_count": 0, "sample_values": []}},
    }


def test_profile_default_sample_limit_is_twenty_and_zero_limit_has_no_samples():
    # Frequencies 21, 20, ... 1 avoid assuming an order for pandas' tied counts.
    frame = pd.DataFrame({"id": [value for value in range(21) for _ in range(21 - value)]})
    assert validation.profile(frame)["columns"]["id"]["sample_values"] == list(range(20))
    assert validation.profile(frame, max_distinct=0)["columns"]["id"]["sample_values"] == []


def test_join_reports_multiplication_first_and_counts_other_failures():
    assert validation.validate(pd.DataFrame({"id": [1, 1, 2]}), {"joins": {
        "left_rows": 2, "keys": ["id"],
    }})[2] == {"name": "joins", "outcome": "fail",
               "detail": "Join grew from 2 to 3 rows (+1 more)."}


def test_profile_categorical_samples_include_only_observed_non_null_values():
    frame = pd.DataFrame({"region": pd.Categorical(["west", None], categories=["west", "east"])})
    assert validation.profile(frame) == {"row_count": 2, "columns": {
        "region": {"dtype": "category", "null_rate": 0.5, "distinct_count": 1,
                   "sample_values": ["west"]},
    }}


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
