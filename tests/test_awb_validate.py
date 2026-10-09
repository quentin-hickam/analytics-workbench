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
# test_cli_profile_summarizes_a_view_and_saves_the_full_profile: profile through src/awb.py resolves a view name, prints row count and per-column type, null rate and distinct count, and saves profile() unchanged.
# test_cli_profile_samples_results_above_max_rows_repeatably: a result above --max-rows is profiled on a seeded sample and the JSON records sampled_from.
# test_cli_profile_reports_unknown_names_and_missing_landing_helper: an unknown bare name or a project without src/preparation/landing.py prints one stderr line and returns 1.

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


MODULE_PATH = (Path(__file__).resolve().parents[1]
               / ".agents/skills/awb-init/assets/awb_validate.py")
module_spec = importlib.util.spec_from_file_location("awb_validate", MODULE_PATH)
validation = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(validation)
ASSETS = MODULE_PATH.parent


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
        # pandas 3 reports string columns as "str", earlier versions as "object".
        "region": {"dtype": str(frame["region"].dtype), "null_rate": 0.1667, "distinct_count": 3,
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


def profile_project(root):
    for asset, installed in (("awb_cli.py", "awb.py"), ("awb_landing.py", "preparation/landing.py"),
                             ("awb_validate.py", "exploration/validate.py")):
        (root / "src" / installed).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ASSETS / asset, root / "src" / installed)
    views = root / "foundation/views"
    views.mkdir(parents=True)
    (views / "01_orders.sql").write_text(
        "CREATE VIEW orders AS SELECT range AS id, "
        "CASE WHEN range < 2 THEN NULL ELSE 'west' END AS region FROM range(8);")


def test_cli_profile_summarizes_a_view_and_saves_the_full_profile(tmp_path):
    duckdb = pytest.importorskip("duckdb")
    profile_project(tmp_path)
    run = subprocess.run([sys.executable, str(tmp_path / "src/awb.py"), "profile", "Orders",
                          "--out", "profiles/orders.json"],
                         cwd=tmp_path.parent, capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stderr
    lines = run.stdout.splitlines()
    assert lines[0] == "rows: 8"
    assert lines[1:3] == ["| column | type | null rate | distinct |", "|---|---|---|---|"]
    assert lines[3] == "| id | int64 | 0.0 | 8 |"
    assert lines[4].startswith("| region | ") and lines[4].endswith(" | 0.25 | 1 |")
    assert lines[5:] == ["full profile in profiles/orders.json"]
    with duckdb.connect() as connection:
        frame = connection.sql("SELECT range AS id, CASE WHEN range < 2 THEN NULL ELSE 'west' END "
                               "AS region FROM range(8)").df()
    saved = json.loads((tmp_path / "profiles/orders.json").read_text())
    assert saved == validation.profile(frame)


def test_cli_profile_samples_results_above_max_rows_repeatably(tmp_path, capsys):
    pytest.importorskip("duckdb")
    profile_project(tmp_path)
    saved = []
    for name in ("first.json", "second.json"):
        assert validation.cli_profile(tmp_path, ["SELECT range AS n FROM range(500)",
                                                 "--max-rows", "50", "--out", name]) == 0
        saved.append(json.loads((tmp_path / name).read_text()))
    assert capsys.readouterr().out.startswith("rows: 50 profiled of 500 (repeatable sample;")
    assert saved[0] == saved[1]
    assert saved[0]["row_count"] == 50 and saved[0]["sampled_from"] == 500
    assert validation.cli_profile(tmp_path, ["SELECT range AS n FROM range(50)",
                                             "--max-rows", "50", "--out", "all.json"]) == 0
    assert "sampled_from" not in json.loads((tmp_path / "all.json").read_text())


def test_cli_profile_reports_unknown_names_and_missing_landing_helper(tmp_path, capsys):
    pytest.importorskip("duckdb")
    profile_project(tmp_path)
    assert validation.cli_profile(tmp_path, ["order"]) == 1
    captured = capsys.readouterr()
    assert captured.out == "" and captured.err == "profile: no view or query file named order\n"
    (tmp_path / "src/preparation/landing.py").unlink()
    assert validation.cli_profile(tmp_path, ["orders"]) == 1
    error = capsys.readouterr().err
    assert "src/preparation/landing.py" in error and error.count("\n") == 1
