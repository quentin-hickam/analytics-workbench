# Kept cases:
# test_settings_lookup_prefers_dataset_then_eda_then_scope_and_lists_unread_keys: settings key resolution order and unread keys.
# test_active_investigation_reads_link_path_or_slug: README pointer forms resolve to the investigation name.
# test_missing_session_helper_exits_with_installer_remedy: no src/preparation/landing.py exits 2 naming the installer.
# test_scan_applies_settings_scope_and_writes_only_its_exploration_file: settings filters applied with sources; one file written; compact stdout.
# test_shared_data_problems_route_to_clean_and_contrary_trends_stay_local: duplicates, variants, gaps, null shift route to awb-clean; contrary group flagged.
# test_variance_explained_matches_hand_computation: eta squared and group means for a two-group measure.
# test_options_override_settings_and_unfit_settings_are_skipped: options replace settings; unfit settings print as not applied; a bad option or empty scope exits 2.
# test_publication_path_with_label_and_float_columns_keep_distributions: publication directory scanned to a labelled file; unique floats are not keys.
# test_template_settings_take_the_period_from_parameters_and_name_unset_choices: [parameters] start/end scope the period; unset scope, measure, and dimensions print the options to pass.
# test_show_prints_one_saved_section_and_lists_keys_for_an_unknown_one: --show walks keys and named list items without rescanning; a miss exits 2 listing what is there.

import importlib.util
import json
from pathlib import Path
import shutil

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents/skills/awb-eda/scripts/eda_scan.py"
LANDING = ROOT / ".agents/skills/awb-init/assets/awb_landing.py"
spec = importlib.util.spec_from_file_location("awb_eda_scan", SCRIPT)
eda = importlib.util.module_from_spec(spec)
spec.loader.exec_module(eda)

SETTINGS = """population = "hourly staff"
[scope]
where = "region <> 'EU'"
date_column = "shift_date"
period_start = 2025-01-01
period_end = 2025-12-31
[eda]
measure = "overtime_hours"
dimensions = ["site"]
key = ["shift_id"]
"""

# One row per site per day of 2025 except June. North rises and South falls after June, so South
# moves against the overall rise; West alternates spellings; note is null before April; every
# fourth day is EU; shift_id 4 repeats.
SHIFTS = """
COPY (
    WITH days AS (SELECT CAST(d AS DATE) AS day, row_number() OVER (ORDER BY d) AS n
                  FROM range(DATE '2025-01-01', DATE '2026-01-01', INTERVAL 1 DAY) t(d)
                  WHERE month(d) <> 6),
    sites AS (SELECT * FROM (VALUES ('North', 2.0), ('South', -1.5), ('West', 0.5)) s(site, shift))
    SELECT CASE WHEN row_number() OVER (ORDER BY day, site) = 6 THEN 4
                ELSE row_number() OVER (ORDER BY day, site) - 1 END AS shift_id,
           day AS shift_date,
           CASE WHEN site = 'West' AND n % 2 = 1 THEN 'west ' ELSE site END AS site,
           CASE WHEN n % 4 = 0 THEN 'EU' ELSE 'US' END AS region,
           5 + CASE WHEN month(day) > 6 THEN shift ELSE 0 END + ((n % 5) - 2) * 0.1 AS overtime_hours,
           CASE WHEN month(day) < 4 THEN NULL ELSE 'x' END AS note
    FROM days, sites)
TO '{path}' (FORMAT parquet)
"""


def write(root, path, text):
    file = root / path
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(text)
    return file


def project(tmp_path, settings=SETTINGS):
    write(tmp_path, "README.md", "Active investigation: [overtime](investigations/overtime/state.md)\n")
    write(tmp_path, "investigations/overtime/state.md", "# Current investigation state\n")
    write(tmp_path, "investigations/overtime/settings.toml", settings)
    (tmp_path / "src/preparation").mkdir(parents=True)
    shutil.copyfile(LANDING, tmp_path / "src/preparation/landing.py")
    return tmp_path


@pytest.fixture
def shifts(tmp_path):
    duckdb = pytest.importorskip("duckdb")
    root = project(tmp_path)
    publication = root / "data/parquet/shifts/p1"
    publication.mkdir(parents=True)
    duckdb.connect().execute(SHIFTS.format(path=publication / "shifts.parquet"))
    write(root, "foundation/views/01_shifts.sql",
          "CREATE VIEW shifts AS SELECT * FROM read_parquet('data/parquet/shifts/p1/*.parquet');\n")
    return root


def run(root, *args, capsys):
    status = eda.main([str(root), *args])
    captured = capsys.readouterr()
    return status, captured.out, captured.err


def test_settings_lookup_prefers_dataset_then_eda_then_scope_and_lists_unread_keys():
    data = {"population": "nurses", "where": "top",
            "scope": {"where": "scope", "date_column": "d", "owner": "ops"},
            "eda": {"measure": "eda", "shifts": {"measure": "dataset"}}}
    found, unused = eda.resolve_settings(data, "shifts")
    assert found["measure"] == ("dataset", "eda.shifts.measure")
    assert found["where"] == ("scope", "scope.where")
    assert found["date_column"] == ("d", "scope.date_column")
    assert unused == ["population", "where", "scope.owner"]
    assert eda.resolve_settings(data, "other")[0]["measure"] == ("eda", "eda.measure")
    template = {"parameters": {"start": "2025-01-01", "end": "2025-06-30", "region": "US"},
                "results": {"r1": {"queries": []}}, "eda": {"period_end": "2025-03-31"}}
    found, unused = eda.resolve_settings(template, "shifts")
    assert found["period_start"] == ("2025-01-01", "parameters.start")
    assert found["period_end"] == ("2025-03-31", "eda.period_end")
    assert unused == ["parameters.end", "parameters.region"]  # end is shadowed by eda.period_end


def test_active_investigation_reads_link_path_or_slug(tmp_path):
    for line, expected in [("[q3](investigations/q3-overtime/state.md)", "q3-overtime"),
                           ("investigations/q3-overtime/state.md", "q3-overtime"),
                           ("`q3-overtime`", "q3-overtime"), ("none", None)]:
        write(tmp_path, "README.md", f"# Workbench\n\nActive investigation: {line}\n")
        assert eda.active_investigation(tmp_path) == expected


def test_missing_session_helper_exits_with_installer_remedy(tmp_path, capsys):
    root = project(tmp_path)
    (root / "src/preparation/landing.py").unlink()
    status, out, err = run(root, "shifts", capsys=capsys)
    assert status == 2 and out == ""
    assert "src/preparation/landing.py" in err and "install_helpers.py" in err


def test_scan_applies_settings_scope_and_writes_only_its_exploration_file(shifts, capsys):
    before = {p for p in shifts.rglob("*") if p.is_file()}
    status, out, _ = run(shifts, "shifts", capsys=capsys)
    assert status == 0
    path = shifts / "investigations/overtime/exploration/eda/shifts.json"
    assert {p for p in shifts.rglob("*") if p.is_file()} - before == {path}
    scan = json.loads(path.read_text())
    assert scan["format"] == "awb-eda/1" and scan["dataset"]["definition"] == "foundation/views/01_shifts.sql"
    assert [f["source"] for f in scan["scope"]["applied"]] == ["scope.where", "scope.period_start",
                                                               "scope.period_end"]
    assert scan["scope"]["rows_before"] == 335 * 3
    assert scan["rows"] == sum(3 for n in range(1, 336) if n % 4) == 756
    assert scan["scope"]["settings_unused"] == ["population"]
    assert scan["date_column"] == {"name": "shift_date", "source": "scope.date_column", "period": "month"}
    assert "investigations/overtime/exploration/eda/shifts.json" in out
    assert "settings keys not read by the scan: population" in out
    # Compact: tables stay within the column and row limits.
    tables = [line for line in out.splitlines() if line.startswith("| ")]
    assert all(line.count(" | ") <= 5 for line in tables)
    assert len(out.splitlines()) < 80


def test_shared_data_problems_route_to_clean_and_contrary_trends_stay_local(shifts, capsys):
    status, out, _ = run(shifts, "shifts", "--no-scope", "--json", capsys=capsys)
    assert status == 0
    summary = json.loads(out)
    routes = {(a["kind"], a["column"]): a["route"] for a in summary["anomalies"]}
    assert routes[("key-violated", "shift_id")] == "awb-clean"
    assert routes[("case-or-space-variants", "site")] == "awb-clean"
    assert routes[("period-gaps", "shift_date")] == "awb-clean"
    assert routes[("null-shift", "note")] == "awb-clean"
    assert routes[("contrary-trend", "site")] == "investigation"
    contrary = [a["detail"] for a in summary["anomalies"] if a["kind"] == "contrary-trend"]
    assert len(contrary) == 1 and contrary[0].startswith("South:")
    variants = next(a for a in summary["anomalies"] if a["kind"] == "case-or-space-variants")
    assert 'West / "west "' in variants["detail"]
    issues = summary["suggested_records"]["unresolved_issues"]
    assert any("shifts.site" in line and "awb-clean" in line for line in issues)
    assert any("site South" in line for line in summary["suggested_records"]["next_steps"])


def test_variance_explained_matches_hand_computation(tmp_path, capsys):
    pytest.importorskip("duckdb")
    root = project(tmp_path, settings="")
    write(root, "foundation/views/01_scores.sql",
          "CREATE VIEW scores AS SELECT * FROM (VALUES ('a', 1), ('a', 1), ('a', 3), ('a', 3), "
          "('b', 5), ('b', 5), ('b', 7), ('b', 7)) v(grp, x);\n")
    status, _, _ = run(root, "scores", "--measure", "x", "--dimension", "grp", "--min-group", "1",
                       capsys=capsys)
    assert status == 0
    scan = json.loads((root / "investigations/overtime/exploration/eda/scores.json").read_text())
    by = scan["measure"]["by_dimension"][0]
    assert by["eta_squared"] == pytest.approx(32 / 40)
    assert [(v["group"], v["mean"]) for v in by["values"]] == [("a", 2.0), ("b", 6.0)]
    assert by["highest"]["group"] == "b" and by["lowest"]["group"] == "a"
    assert scan["scope"]["settings_note"] is None and scan["scope"]["applied"] == []


def test_options_override_settings_and_unfit_settings_are_skipped(shifts, capsys):
    write(shifts, "foundation/views/02_sites.sql",
          "CREATE VIEW sites AS SELECT DISTINCT trim(site) AS site_name FROM shifts;\n")
    status, out, _ = run(shifts, "shifts", "--where", "region = 'EU'", "--start", "2025-07-01",
                         "--measure", "overtime_hours * 60", "--label", "eu", capsys=capsys)
    assert status == 0
    scan = json.loads((shifts / "investigations/overtime/exploration/eda/shifts-eu.json").read_text())
    assert [(f["sql"], f["source"]) for f in scan["scope"]["applied"]][:2] == [
        ("region = 'EU'", "option"), ('CAST("shift_date" AS DATE) >= CAST(\'2025-07-01\' AS DATE)', "option")]
    assert scan["measure"]["expression"] == "overtime_hours * 60"
    # The settings filter references columns the sites view lacks, so it stops the scan.
    status, _, err = run(shifts, "sites", capsys=capsys)
    assert status == 2 and "--no-scope" in err
    status, out, _ = run(shifts, "sites", "--no-scope", capsys=capsys)
    assert status == 0
    assert "not applied: eda.measure: overtime_hours is not valid here" in out
    assert "not applied: eda.key: key columns not in this dataset: shift_id" in out
    assert "not applied: scope.date_column" in out
    status, _, err = run(shifts, "shifts", "--measure", "no_such_column", capsys=capsys)
    assert status == 2 and "no_such_column" in err
    status, _, err = run(shifts, "shifts", "--where", "FALSE", capsys=capsys)
    assert status == 2 and "scope selects 0 of" in err


def test_publication_path_with_label_and_float_columns_keep_distributions(shifts, capsys):
    status, _, _ = run(shifts, "data/parquet/shifts/p1", "--no-scope", "--label", "raw", capsys=capsys)
    assert status == 0
    scan = json.loads((shifts / "investigations/overtime/exploration/eda/shifts-p1-raw.json").read_text())
    assert scan["dataset"] == {"name": "shifts-p1", "kind": "publication", "path": "data/parquet/shifts/p1"}
    columns = {c["name"]: c for c in scan["columns"]}
    assert columns["overtime_hours"]["numeric"]["quantiles"]["p50"] is not None
    assert not columns["overtime_hours"]["unique"]
    near = [n["column"] for n in scan["grain"]["near_unique_columns"]]
    assert near == ["shift_id"]
    assert all("shift_id" not in pair for pair in scan["grain"]["column_pair_keys"])


TEMPLATE = """[parameters]
start = 2025-07-01
end = 2025-12-31

[results.overtime-by-site]
queries = ["queries/overtime-by-site.sql"]
"""


def test_template_settings_take_the_period_from_parameters_and_name_unset_choices(shifts, capsys):
    write(shifts, "investigations/overtime/settings.toml", TEMPLATE)
    status, out, _ = run(shifts, "shifts", capsys=capsys)
    assert status == 0
    assert "not applied: parameters.start: no date column is set; pass --date-column" in out
    assert "not set: measure, dimensions: no breakdown, trend, or contrary groups; pass --measure" in out
    assert "not set: where, period" not in out and "settings keys not read" not in out
    status, out, _ = run(shifts, "shifts", "--date-column", "shift_date", "--measure", "overtime_hours",
                         capsys=capsys)
    assert status == 0
    scan = json.loads((shifts / "investigations/overtime/exploration/eda/shifts.json").read_text())
    assert [f["source"] for f in scan["scope"]["applied"]] == ["parameters.start", "parameters.end"]
    assert scan["rows"] == 3 * sum(1 for n in range(1, 336) if n > 151)
    assert scan["scope"]["not_set"] == [{"keys": "dimensions",
                                         "detail": "chose site, region automatically; pass --dimension (repeatable)"}]
    write(shifts, "investigations/overtime/settings.toml", "")
    status, out, _ = run(shifts, "shifts", "--measure", "overtime_hours", "--dimension", "site", capsys=capsys)
    assert status == 0 and "not set: where, period: the scan covers every row; pass --where" in out
    assert "not set: measure" not in out and "not set: dimensions" not in out


def test_show_prints_one_saved_section_and_lists_keys_for_an_unknown_one(shifts, capsys):
    status, _, err = run(shifts, "shifts", "--show", "columns", capsys=capsys)
    assert status == 2 and "no saved scan at investigations/overtime/exploration/eda/shifts.json" in err
    assert run(shifts, "shifts", capsys=capsys)[0] == 0
    path = shifts / "investigations/overtime/exploration/eda/shifts.json"
    scan = json.loads(path.read_text())
    path.write_text(path.read_text().replace('"format"', '"saved": true, "format"', 1))
    status, out, _ = run(shifts, "shifts", "--show", "columns.region.top", capsys=capsys)
    assert status == 0 and len(out.splitlines()) == 1
    region = next(c for c in scan["columns"] if c["name"] == "region")
    assert json.loads(out) == region["top"]
    status, out, _ = run(shifts, "shifts", "--show", "measure.by_dimension.site.values", capsys=capsys)
    assert status == 0 and json.loads(out) == scan["measure"]["by_dimension"][0]["values"]
    status, out, _ = run(shifts, "shifts", "--show", "saved", capsys=capsys)
    assert status == 0 and out.strip() == "true"  # read from the file, not a fresh scan
    status, _, err = run(shifts, "shifts", "--show", "columns.nope", capsys=capsys)
    assert status == 2 and "no nope under columns; there:" in err and "shift_id" in err
    status, _, err = run(shifts, "shifts", "--show", "grain.nope", capsys=capsys)
    assert status == 2 and "duplicate_rows" in err
