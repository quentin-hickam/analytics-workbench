# Kept cases:
# test_scan_reports_candidate_issues_with_counts_and_examples: one call finds parse failures, whitespace, case and spelling variants, text and numeric sentinels, duplicates, impossible and out-of-range dates, orphans and all-null columns; full scan in foundation/scans, compact stdout.
# test_scan_reads_views_through_session_and_changes_no_data: a view loads through the project's session(); landed and view files keep their bytes and only the scan file is written.
# test_text_dates_and_codes_are_typed_conservatively: a day-first text date column is typed by its one covering format, an all-ambiguous one is reported, and leading-zero codes stay text.
# test_rescan_reports_delta_with_stable_ids_and_inherited_options: a rescan after a correction view reports before and after counts by issue, keeps ids, and reuses the baseline's options.
# test_local_query_scan_stays_beside_the_query: a saved exploration query scanned against a view baseline writes its scan beside the query, not in the foundation.
# test_recorded_markers_mark_issues_as_recorded: issues whose `<scan>#<key>` marker is in the quality record are reported as recorded with their quality ID.
# test_record_writes_quality_catalog_and_flags_in_one_call: new quality IDs, issue and correction rows with scan counts and markers, a catalog row, and a revalidation flag that keeps the prior status.
# test_record_updates_recorded_issue_and_continues_numbering: a recorded issue has its judgment cells updated; a new issue continues the existing ID prefix and width.
# test_record_checks_everything_before_writing: an unmatched flag or a correction without findings writes nothing; a dry run prints rows and writes nothing.

import importlib.util
import json
import shutil
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents/skills/awb-clean/scripts"
TEMPLATES = ROOT / ".agents/skills/awb-init/assets/workbench"
TODAY = date(2026, 10, 9)


def load(name):
    spec = importlib.util.spec_from_file_location(f"awb_clean_{name}", SKILL / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


scanner = load("scan_dataset")
recorder = load("record_cleaning")


def write(root, path, text):
    file = root / path
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(text)
    return file


def orders_csv():
    rows = ["order_id,customer_id,dept,amount,age,order_date,zip,note"]
    depts = ["Sales", "Marketing", "Engineering", "Support"]
    for n in range(1, 41):
        rows.append(f"{n},{10 + n % 5},{depts[n % 4]},{10 + n % 7}.5,{25 + n % 30},"
                    f"2024-{1 + n % 12:02d}-{1 + n % 28:02d},0{2100 + n},")
    rows += ["41,11,Sales ,abc,9999,2024-03-05,02141,",          # whitespace, parse failure, sentinel
             "41,11,Sales ,abc,9999,2024-03-05,02141,",          # exact duplicate row
             "42,99,sales,12.5,-1,2031-01-01,02142,",            # case variant, orphan, sentinel, future date
             "43,10,Markting,8.5,40,1900-01-01,02143,",          # spelling variant, placeholder date
             "44,12,N/A,9.5,41,2023-12-31,02144,"]               # text placeholder, out of period
    return "\n".join(rows) + "\n"


@pytest.fixture
def project(tmp_path):
    write(tmp_path, "data/raw/orders/a1/orders.csv", orders_csv())
    write(tmp_path, "data/raw/orders/a1/provenance.json", '{"status": "complete"}')
    write(tmp_path, "data/ref/customers.csv", "customer_id\n" + "\n".join(str(n) for n in range(10, 15)) + "\n")
    return tmp_path


def with_session(root):
    shutil.copyfile(ROOT / ".agents/skills/awb-init/assets/awb_landing.py",
                    write(root, "src/preparation/landing.py", ""))
    write(root, "foundation/views/01_orders.sql",
          "CREATE VIEW orders AS SELECT * FROM read_csv('data/raw/orders/a1/orders.csv', all_varchar = true);\n")


def keys(record):
    return {issue["key"]: issue for issue in record["issues"]}


def test_scan_reports_candidate_issues_with_counts_and_examples(project, capsys):
    pytest.importorskip("duckdb")
    code = scanner.main([str(project), "data/raw/orders/a1", "--key", "order_id",
                         "--ref", "customer_id=data/ref/customers.csv.customer_id",
                         "--range", "order_date=2024-01-01:2024-12-31"])
    assert code == 0
    out = json.loads(capsys.readouterr().out)
    assert out["scan"] == "foundation/scans/orders@a1.json" and out["rows"] == 45
    assert all(len(issue["examples"]) <= 3 for issue in out["issues"])
    record = json.loads((project / out["scan"]).read_text())
    found = keys(record)
    assert found["parse:amount:DOUBLE"]["count"] == 2
    assert found["parse:amount:DOUBLE"]["examples"] == [{"value": "abc", "count": 2}]
    assert found["whitespace:dept"]["count"] == 2
    assert found["variants:dept:sales"]["examples"] == [{"value": "Sales", "count": 12}, {"value": "sales", "count": 1}]
    assert "near-variants:dept:marketing|markting" in found
    assert found['sentinel:dept:"n/a"']["count"] == 1
    assert found["sentinel:age:9999"]["count"] == 2 and found["sentinel:age:-1"]["count"] == 1
    assert found["sentinel:order_date:1900-01-01"]["count"] == 1
    assert found["duplicate-rows"]["count"] == 1
    assert found["duplicate-key:order_id"]["count"] == 1
    assert "future-date:order_date" in found
    assert found["range:order_date:2024-01-01:2024-12-31"]["count"] == 3
    orphans = found["orphans:customer_id:data/ref/customers.csv.customer_id"]
    assert orphans["count"] == 1 and orphans["examples"][0]["value"] == "99"
    assert found["all-null:note"]["count"] == 45
    assert not any(k.startswith("text-typed") for k in found)  # landed CSV is read as text on purpose
    assert [i["id"] for i in record["issues"]] == [f"S{n}" for n in range(1, len(record["issues"]) + 1)]


def test_scan_reads_views_through_session_and_changes_no_data(project):
    pytest.importorskip("duckdb")
    with_session(project)
    before = {p: p.read_bytes() for p in project.rglob("*") if p.is_file()}
    record, path = scanner.scan(project, "orders", today=TODAY)
    after = {p: p.read_bytes() for p in project.rglob("*") if p.is_file()}
    assert set(after) - set(before) == {path} and all(after[p] == before[p] for p in before)
    assert path == project / "foundation/scans/orders.json"
    assert record["target"] == {"kind": "view", "label": "view orders", "path": None}
    found = keys(record)
    assert found["text-typed:amount:DOUBLE"]["count"] == 43
    assert found["text-typed:order_id:BIGINT"]["count"] == 45


def test_text_dates_and_codes_are_typed_conservatively(tmp_path):
    pytest.importorskip("duckdb")
    rows = ["day_first,ambiguous,code"] + [f"{13 + n % 15:02d}/{1 + n % 12:02d}/2024,{1 + n % 12:02d}/0{1 + n % 9}/2024,00{n}"
                                          for n in range(30)]
    write(tmp_path, "data/files/dates.csv", "\n".join(rows) + "\n")
    record, path = scanner.scan(tmp_path, "data/files/dates.csv", today=TODAY)
    assert path == tmp_path / "foundation/scans/dates.json"
    columns, found = record["columns"], keys(record)
    assert columns["day_first"]["typed_as"] == "DATE" and "date-formats:day_first" not in found
    assert "(%d/%m/%Y)" in found["text-typed:day_first:DATE"]["summary"]
    assert "ambiguous" in found["date-formats:ambiguous"]["summary"]
    assert columns["code"]["typed_as"] is None


def test_rescan_reports_delta_with_stable_ids_and_inherited_options(project, capsys):
    pytest.importorskip("duckdb")
    with_session(project)
    first, _ = scanner.scan(project, "orders", keys=["order_id"], today=TODAY)
    ids = {i["key"]: i["id"] for i in first["issues"]}
    write(project, "foundation/views/01_orders.sql",
          "CREATE VIEW orders AS SELECT * REPLACE (trim(dept) AS dept) "
          "FROM read_csv('data/raw/orders/a1/orders.csv', all_varchar = true);\n")
    assert scanner.main([str(project), "orders", "--rescan"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert f"{ids['whitespace:dept']} whitespace:dept: 2 -> 0 resolved" in out["delta"]["issues"]
    assert out["delta"]["rows"] == [45, 45]
    record = json.loads((project / "foundation/scans/orders.json").read_text())
    assert record["options"]["keys"] == ["order_id"]
    assert record["baseline"]["issues"] == first["issues"]
    for issue in record["issues"]:
        assert issue["id"] == ids.get(issue["key"], issue["id"])
    variants = next(d for d in record["delta"]["issues"] if d["key"] == "variants:dept:sales")
    assert variants["before"] == 1 and variants["after"] == 1  # case remains until mapped


def test_local_query_scan_stays_beside_the_query(project):
    pytest.importorskip("duckdb")
    with_session(project)
    scanner.scan(project, "orders", today=TODAY)
    query = write(project, "investigations/churn/exploration/dept_fix.sql",
                  "SELECT * REPLACE (upper(trim(dept)) AS dept) FROM orders -- local assessment\n")
    record, path = scanner.scan(project, str(query.relative_to(project)), rescan="orders", today=TODAY)
    assert path == project / "investigations/churn/exploration/dept_fix.scan.json"
    assert sorted(p.name for p in (project / "foundation/scans").iterdir()) == ["orders.json"]
    change = {d["key"]: d["change"] for d in record["delta"]["issues"]}
    assert change["whitespace:dept"] == "resolved" and change["variants:dept:sales"] == "resolved"


def test_recorded_markers_mark_issues_as_recorded(project, capsys):
    pytest.importorskip("duckdb")
    with_session(project)
    quality = (TEMPLATES / "foundation/quality.md").read_text().replace(
        "| --- | --- | --- | --- | --- | --- |\n",
        "| --- | --- | --- | --- | --- | --- |\n| Q-003 | view `orders` | Trailing spaces; `orders#whitespace:dept` | None | Trimmed | corrected |\n", 1)
    write(project, "foundation/quality.md", quality)
    assert scanner.main([str(project), "orders"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert {"quality": "Q-003", "status": "corrected"}.items() <= out["recorded"][0].items()
    assert all(i["key"] != "whitespace:dept" for i in out["issues"])


def scan_file(root, *, delta=True):
    issue = lambda id_, key, column, count, summary: {
        "id": id_, "key": key, "check": key.split(":")[0], "column": column, "count": count, "of": 45,
        "summary": summary, "examples": [{"value": "Sales ", "count": count}], "detail": None, "recorded": None}
    issues = [issue("S1", "whitespace:dept", "dept", 2, "2 values in dept with leading or trailing whitespace"),
              issue("S2", "sentinel:age:9999", "age", 2, "2 values in age are 9999")]
    record = {"schema": "awb-scan/1", "name": "orders",
              "target": {"kind": "view", "label": "view orders", "path": None},
              "scanned_at": "2026-10-09T10:00:00+00:00", "issues": [issues[1]] if delta else issues,
              "baseline": {"issues": issues} if delta else None,
              "delta": {"issues": [{"id": "S1", "key": "whitespace:dept", "before": 2, "after": 0, "change": "resolved"},
                                   {"id": "S2", "key": "sentinel:age:9999", "before": 2, "after": 2, "change": "unchanged"}]}
              if delta else None}
    write(root, "foundation/scans/orders.json", json.dumps(record))


def state_file(root):
    text = (TEMPLATES / "investigation/state.md").read_text().replace("<!-- use an ISO date -->", "2026-09-01")
    text = text.replace("| --- | --- | --- | --- |\n",
                        "| --- | --- | --- | --- |\n| Sales leads growth | [r-003](evidence/r-003.json) | supported | |\n"
                        "| Age is stable | [r-004](evidence/r-004.json) | provisional | |\n", 1)
    return write(root, "investigations/churn/state.md", text)


def test_record_writes_quality_catalog_and_flags_in_one_call(tmp_path):
    scan_file(tmp_path)
    state = state_file(tmp_path)
    result = recorder.record(tmp_path, "orders", {
        "issues": {"S1": {"impact": "Splits department counts", "treatment": "Trimmed in the view",
                          "status": "corrected", "correction": "Trim department labels; spaces carry no meaning",
                          "change": "`foundation/views/01_orders.sql` trims dept"},
                   "S2": {"impact": "Inflates mean age", "treatment": "Open: meaning unconfirmed", "status": "open"}},
        "flags": [{"investigation": "churn", "result": "r-003", "reason": "{S1} merges department labels"}],
        "catalog": {"name": "orders", "cells": {"Kind": "view", "Preparation rules": "Trims dept ({S1})"}},
    }, today=TODAY)
    assert result["quality_ids"] == {"S1": "Q-001", "S2": "Q-002"} and result["corrections"] == ["Q-001"]
    assert sorted(result["written"]) == ["foundation/catalog.md", "foundation/quality.md",
                                         "investigations/churn/state.md"]
    quality = (tmp_path / "foundation/quality.md").read_text()
    assert ("| Q-001 | view `orders`, column `dept` | 2 values in dept with leading or trailing whitespace "
            "(2 of 45); e.g. \"Sales \" (2); `orders#whitespace:dept` in [scan](scans/orders.json) 2026-10-09 | "
            "Splits department counts | Trimmed in the view | corrected |") in quality
    assert ("| 2026-10-09 | Q-001 | Trim department labels; spaces carry no meaning | "
            "`foundation/views/01_orders.sql` trims dept; rescan 2 -> 0 | churn: r-003 |") in quality
    assert "| Q-002 |" in quality and quality.count("| 2026-10-09 |") == 1
    catalog = (tmp_path / "foundation/catalog.md").read_text()
    assert "| `orders` | view |  |  |  | Trims dept (Q-001) |  |  |" in catalog
    text = state.read_text()
    assert "| Sales leads growth | [r-003](evidence/r-003.json) | revalidation-needed (was supported) | Q-001 merges department labels |" in text
    assert "| Age is stable | [r-004](evidence/r-004.json) | provisional | |" in text
    assert "Last updated: 2026-10-09" in text


def test_record_updates_recorded_issue_and_continues_numbering(tmp_path):
    scan_file(tmp_path, delta=False)
    quality = (TEMPLATES / "foundation/quality.md").read_text().replace(
        "| --- | --- | --- | --- | --- | --- |\n",
        "| --- | --- | --- | --- | --- | --- |\n"
        "| DQ-07 | view `orders` | Spaces; `orders#whitespace:dept` | Splits counts | Open | open |\n", 1)
    write(tmp_path, "foundation/quality.md", quality)
    result = recorder.record(tmp_path, "orders", {
        "issues": {"S1": {"treatment": "Trimmed in the view", "status": "corrected"},
                   "S2": {"impact": "Inflates mean age", "treatment": "Open", "status": "open"}}}, today=TODAY)
    assert result["quality_ids"] == {"S1": "DQ-07", "S2": "DQ-08"}
    assert result["updated"] == ["DQ-07"] and result["added"] == ["DQ-08"]
    text = (tmp_path / "foundation/quality.md").read_text()
    assert "| DQ-07 | view `orders` | Spaces; `orders#whitespace:dept` | Splits counts | Trimmed in the view | corrected |" in text


def test_record_checks_everything_before_writing(tmp_path, capsys, monkeypatch):
    scan_file(tmp_path)
    state = state_file(tmp_path)
    before = state.read_text()
    decision = {"issues": {"S1": {"impact": "x", "treatment": "y", "status": "corrected",
                                  "correction": "Trim", "change": "view"}},
                "flags": [{"investigation": "churn", "result": "r-999", "reason": "{S1}"}]}
    with pytest.raises(recorder.RecordError, match="0 findings match r-999"):
        recorder.record(tmp_path, "orders", decision, today=TODAY)
    del decision["flags"]
    with pytest.raises(recorder.RecordError, match="findings text"):
        recorder.record(tmp_path, "orders", decision, today=TODAY)
    assert not (tmp_path / "foundation/quality.md").exists() and state.read_text() == before
    decision["findings"] = "none: stale listed no finding reading orders"
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO(json.dumps(decision)))
    assert recorder.main([str(tmp_path), "orders", "--dry-run"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["written"] == [] and any("none: stale listed" in row for row in out["rows"])
    assert not (tmp_path / "foundation/quality.md").exists()
