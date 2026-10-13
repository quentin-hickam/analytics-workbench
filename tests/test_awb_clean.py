# Kept cases:
# test_scan_reports_candidate_issues_with_counts_and_examples: one call finds parse failures, whitespace, case and spelling variants, text and numeric sentinels, duplicates, impossible and out-of-range dates, orphans and all-null columns; full scan in foundation/scans, compact stdout.
# test_scan_reads_views_through_session_and_changes_no_data: a view loads through the project's session(); landed and view files keep their bytes and only the scan file is written.
# test_text_dates_and_codes_are_typed_conservatively: a day-first text date column is typed by its one covering format, an all-ambiguous one is reported, and leading-zero codes stay text.
# test_rescan_reports_delta_with_stable_ids_and_inherited_options: a rescan after a correction view reports before and after counts by issue, keeps ids, and reuses the baseline's options.
# test_removed_targets_and_options_are_rejected: a saved .sql query is not a scan target; --rescan takes no scan name; --typed-threshold and --max-categories are gone.
# test_recorded_markers_mark_issues_as_recorded: issues whose `<scan>#<key>` marker is in the quality record are reported as recorded with their quality ID and recorded count beside the current count.
# test_record_sets_the_view_row_when_a_publication_shares_its_name: a publication row named like its canonical view leaves the view row the one record sets; two non-view rows with one name still refuse.
# test_record_writes_quality_catalog_and_flags_in_one_call: linked quality rows and catalog cells exist before flags, corrections are last, and a flag keeps the prior status.
# test_record_updates_recorded_issue_and_continues_numbering: a recorded issue updates its link and judgment cells, keeps its observation, and continues the Markdown ID prefix and width.
# test_record_checks_everything_before_writing: an unmatched flag or a correction without findings writes nothing; a dry run prints rows and writes nothing.
# test_record_uses_one_observation_for_link: baseline count/of/date win together; a new rescan issue uses the current observation.
# test_record_keeps_unexamined_links: recording one scan preserves another scan's links without its scan file.
# test_orphan_links_do_not_claim_reused_ids: deleted rows or missing markers invalidate links, including when Markdown reuses their ID.
# test_ambiguous_quality_rows_block_only_their_links: a marker on two rows or on a row with a repeated ID is unrecorded for scans and refused for recording before any write; an unrelated repeated ID blocks nothing.
# test_markers_outside_the_observation_are_not_links: backticked `x#y` text in other cells, such as a column named PO#line, is not a marker.
# test_legacy_links_backfill_without_scan_writes: both historical date formats and escaped keys migrate, and scanning stays read-only.
# test_recorded_status_follows_header_and_count_follows_json: Markdown status is read by header; JSON alone owns the recorded count.
# test_record_failure_reports_phases_and_retries_once: B or C failure reports completed phases and replaced files; retry appends one correction and keeps flags idempotent.
# test_record_revises_a_row_by_quality_id: a Q- or DQ- key revises its row's judgment cells and keeps the observation, appends a correction row without a rescan suffix, accepts an unmarked row, and resolves {Q-004}; a dry run writes nothing.
# test_record_rejects_bad_quality_id_keys: a foreign scan's marker, two keys naming one row, and an unknown key are rejected and write nothing.
# test_quality_id_revision_keeps_link_and_placeholder_rules: a quality-ID revision keeps the link's original counts and date, works with reordered Markdown columns, and keeps known-prefix placeholder refusals.
# test_record_ignores_unvalidated_recorded_placeholders: saved scan metadata cannot supply a placeholder ID when no row carries the issue's marker; the refusal writes nothing.
# test_quality_id_duplicate_keeps_revision_error: duplicate quality-ID revisions retain their specific refusal message and write nothing.
# test_old_provenance_refuses_before_writes: a project helper without flag_findings refuses with an awb-init repair hint, including dry runs.
# test_flag_retry_keeps_original_quality_id: a phase B failure followed by another issue allocation keeps the original Q-ID on retry and records its correction exactly once.
# test_dry_run_prints_flag_rows_and_writes_nothing: a dry run lists the rendered flagged rows beside the quality rows and writes nothing.
# test_renamed_quality_headers_keep_template_positions: with every Active header renamed, a new row is written in the template's positions, scans read it as recorded, and a reopen sets its status.
# test_quality_json_is_written_only_when_links_change: a call that changes no link leaves quality.json absent or byte-identical.
# test_unlinked_marker_row_is_relinked_and_short_rows_read: with quality.json present, a row carrying the marker but no link is relinked from its prose; a short row reads as blank status.
# test_failed_phase_a_leaves_no_partial_files: a failed replace in phase A removes every prepared temporary file.

import hashlib
import importlib.util
import io
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


def quality_link(root, scan, key):
    digest = hashlib.sha256(f"{scan}\n{key}".encode()).hexdigest()
    return json.loads((root / "foundation/quality.json").read_text())["links"][digest]


def quality_rows(root, rows):
    text = (TEMPLATES / "foundation/quality.md").read_text().replace(
        "| --- | --- | --- | --- | --- | --- |\n",
        "| --- | --- | --- | --- | --- | --- |\n" + "\n".join(rows) + "\n", 1)
    return write(root, "foundation/quality.md", text)


def judgment():
    return {"impact": "Splits counts", "treatment": "Open", "status": "open"}


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


def test_removed_targets_and_options_are_rejected(project, capsys):
    pytest.importorskip("duckdb")
    with_session(project)
    write(project, "investigations/churn/exploration/dept_fix.sql", "SELECT * FROM orders\n")
    assert scanner.main([str(project), "investigations/churn/exploration/dept_fix.sql"]) == 2
    assert "unsupported formats" in capsys.readouterr().err
    assert not (project / "investigations/churn/exploration/dept_fix.scan.json").exists()
    for extra in (["--rescan", "orders"], ["--typed-threshold", "0.5"], ["--max-categories", "9"]):
        with pytest.raises(SystemExit):
            scanner.main([str(project), "orders", *extra])


def test_recorded_markers_mark_issues_as_recorded(project, capsys):
    pytest.importorskip("duckdb")
    with_session(project)
    quality = (TEMPLATES / "foundation/quality.md").read_text().replace(
        "| --- | --- | --- | --- | --- | --- |\n",
        "| --- | --- | --- | --- | --- | --- |\n| Q-003 | view `orders` | Trailing spaces (1 of 45); `orders#whitespace:dept` | None | Trimmed | corrected |\n", 1)
    write(project, "foundation/quality.md", quality)
    assert scanner.main([str(project), "orders"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert {"quality": "Q-003", "status": "corrected", "count": 2, "recorded_count": 1}.items() <= out["recorded"][0].items()
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
              "baseline": {"scanned_at": "2026-10-09T10:00:00+00:00", "issues": issues} if delta else None,
              "delta": {"issues": [{"id": "S1", "key": "whitespace:dept", "before": 2, "after": 0, "change": "resolved"},
                                   {"id": "S2", "key": "sentinel:age:9999", "before": 2, "after": 2, "change": "unchanged"}]}
              if delta else None}
    write(root, "foundation/scans/orders.json", json.dumps(record))


def state_file(root):
    shutil.copyfile(ROOT / ".agents/skills/awb-init/assets/awb_provenance.py",
                    write(root, "src/provenance.py", ""))
    text = (TEMPLATES / "investigation/state.md").read_text().replace("<!-- use an ISO date -->", "2026-09-01")
    text = text.replace("| --- | --- | --- | --- |\n",
                        "| --- | --- | --- | --- |\n| Sales leads growth | [r-003](evidence/r-003.json) | supported | |\n"
                        "| Age is stable | [r-004](evidence/r-004.json) | provisional | |\n", 1)
    return write(root, "investigations/churn/state.md", text)


def test_record_sets_the_view_row_when_a_publication_shares_its_name(tmp_path):
    scan_file(tmp_path)
    catalog = (TEMPLATES / "foundation/catalog.md").read_text().replace(
        "| --- | --- | --- | --- | --- | --- | --- | --- |\n",
        "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        "| orders | Parquet publication |  | `data/raw/erp/a1/` | `data/parquet/orders/p1/` | `src/preparation/orders.sql` |  |  |\n"
        "| orders | canonical view | one row per order |  | `foundation/views/01_orders.sql` |  |  |  |\n", 1)
    write(tmp_path, "foundation/catalog.md", catalog)
    decisions = {"issues": {"S1": {"impact": "Splits counts", "treatment": "Trim", "status": "corrected",
                                   "correction": "Trim dept", "change": "`foundation/views/01_orders.sql` trims dept"}},
                 "findings": "none: stale listed no finding reading orders",
                 "catalog": {"name": "orders", "cells": {"Preparation rules": "Trims dept ({S1})"}}}
    assert recorder.record(tmp_path, "orders", decisions, today=TODAY)["catalog"] == "updated orders"
    text = (tmp_path / "foundation/catalog.md").read_text()
    assert "| orders | canonical view | one row per order |  | `foundation/views/01_orders.sql` | Trims dept (Q-001) |  |  |" in text
    assert "| orders | Parquet publication |  | `data/raw/erp/a1/` | `data/parquet/orders/p1/` | `src/preparation/orders.sql` |  |  |" in text
    # Two rows that are not views stay ambiguous and refuse, writing nothing.
    write(tmp_path, "foundation/catalog.md", catalog.replace("canonical view", "Parquet publication"))
    scan_file(tmp_path)
    with pytest.raises(recorder.RecordError, match="several rows are named orders"):
        recorder.record(tmp_path, "orders", decisions, today=TODAY)


def test_record_writes_quality_catalog_and_flags_in_one_call(tmp_path, monkeypatch):
    scan_file(tmp_path)
    state = state_file(tmp_path)
    replaced = []
    original = recorder.os.replace
    def replace(source, target):
        if not replaced:
            assert all((tmp_path / relative).is_file() for relative in (
                "foundation/quality.json.tmp", "foundation/quality.md.tmp", "foundation/catalog.md.tmp"))
        if Path(target) == state:
            quality = (tmp_path / "foundation/quality.md").read_text()
            assert "| Q-001 |" in quality and "| Q-002 |" in quality
            assert "| 2026-10-09 | Q-001 |" not in quality
        replaced.append(Path(target).relative_to(tmp_path).as_posix())
        original(source, target)
    monkeypatch.setattr(recorder.os, "replace", replace)
    result = recorder.record(tmp_path, "orders", {
        "issues": {"S1": {"impact": "Splits department counts", "treatment": "Trimmed in the view",
                          "status": "corrected", "correction": "Trim department labels; spaces carry no meaning",
                          "change": "`foundation/views/01_orders.sql` trims dept"},
                   "S2": {"impact": "Inflates mean age", "treatment": "Open: meaning unconfirmed", "status": "open"}},
        "flags": [{"investigation": "churn", "result": "r-003", "reason": "{S1} merges department labels"}],
        "catalog": {"name": "orders", "cells": {"Kind": "view", "Preparation rules": "Trims dept ({S1})"}},
    }, today=TODAY)
    assert result["quality_ids"] == {"S1": "Q-001", "S2": "Q-002"} and result["corrections"] == ["Q-001"]
    assert sorted(result["written"]) == ["foundation/catalog.md", "foundation/quality.json", "foundation/quality.md",
                                         "investigations/churn/findings.json", "investigations/churn/state.md"]
    assert replaced == ["foundation/quality.json", "foundation/quality.md", "foundation/catalog.md",
                        "investigations/churn/findings.json", "investigations/churn/state.md", "foundation/quality.md"]
    links = json.loads((tmp_path / "foundation/quality.json").read_text())
    assert links["schema"] == "awb-quality-links/1" and len(links["links"]) == 2
    assert {link["id"] for link in links["links"].values()} == {"Q-001", "Q-002"}
    quality = (tmp_path / "foundation/quality.md").read_text()
    assert ("| Q-001 | view `orders`, column `dept` | 2 values in dept with leading or trailing whitespace "
            "(2 of 45); e.g. \"Sales \" (2); `orders#whitespace:dept` scanned 2026-10-09 | "
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
        "| DQ-07 | view `orders` | Spaces (5 of 45); `orders#whitespace:dept` in [scan](scans/orders.json) 2026-01-02 | Splits counts | Open | open |\n", 1)
    write(tmp_path, "foundation/quality.md", quality)
    result = recorder.record(tmp_path, "orders", {
        "issues": {"S1": {"treatment": "Trimmed in the view", "status": "corrected"},
                   "S2": {"impact": "Inflates mean age", "treatment": "Open", "status": "open"}}}, today=TODAY)
    assert result["quality_ids"] == {"S1": "DQ-07", "S2": "DQ-08"}
    assert result["updated"] == ["DQ-07"] and result["added"] == ["DQ-08"]
    text = (tmp_path / "foundation/quality.md").read_text()
    assert ("| DQ-07 | view `orders` | Spaces (5 of 45); `orders#whitespace:dept` in [scan](scans/orders.json) 2026-01-02 | "
            "Splits counts | Trimmed in the view | corrected |") in text
    assert "`orders#sentinel:age:9999` scanned 2026-10-09 |" in text
    assert quality_link(tmp_path, "orders", "whitespace:dept") == {
        "id": "DQ-07", "scan": "orders", "recorded_count": 2, "recorded_of": 45,
        "observed_at": "2026-10-09"}
    # A plain scan updates the link's count and date, keeping the first observation.
    path = tmp_path / "foundation/scans/orders.json"
    record = json.loads(path.read_text())
    record["scanned_at"] = "2026-11-01T10:00:00+00:00"
    record["issues"][1]["count"] = 3
    path.write_text(json.dumps(record))
    result = recorder.record(tmp_path, "orders", {"issues": {"S2": {"status": "open"}}}, today=TODAY)
    assert result["updated"] == ["DQ-08"] and result["added"] == []
    text = (tmp_path / "foundation/quality.md").read_text()
    assert "2 values in age are 9999 (2 of 45); e.g. \"Sales \" (2); `orders#sentinel:age:9999` scanned 2026-10-09 |" in text
    link = quality_link(tmp_path, "orders", "sentinel:age:9999")
    assert link["recorded_count"] == 3 and link["observed_at"] == "2026-11-01"


def test_record_checks_everything_before_writing(tmp_path, capsys, monkeypatch):
    scan_file(tmp_path)
    state = state_file(tmp_path)
    before = state.read_text()
    decision = {"issues": {"S1": {"impact": "x", "treatment": "y", "status": "corrected",
                                  "correction": "Trim", "change": "view"}},
                "flags": [{"investigation": "churn", "result": "r-999", "reason": "{S1}"}]}
    with pytest.raises(recorder.RecordError, match="no findings row links r-999"):
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
    assert not (tmp_path / "foundation/quality.json").exists()


def quality_file(root, prefix="Q-"):
    rows = (f"| {prefix}003 | view `orders` | Spaces (2 of 45); `orders#whitespace:dept` scanned 2026-10-01 | Splits counts | Trimmed | corrected |\n"
            f"| {prefix}004 | view `orders`, column `amount` | -999 in amount (3 of 45); `orders#sentinel:amount:-999` scanned 2026-10-01 | Skews totals | Nulled in the view | corrected |\n"
            f"| {prefix}005 | view `orders` | Test orders, noted by hand | Inflates counts | Open | open |\n"
            f"| {prefix}006 | view `payments` | Bad codes (4 of 9); `payments#sentinel:code:0` scanned 2026-10-01 | None | Open | open |\n")
    quality = (TEMPLATES / "foundation/quality.md").read_text().replace(
        "| --- | --- | --- | --- | --- | --- |\n", "| --- | --- | --- | --- | --- | --- |\n" + rows, 1)
    return write(root, "foundation/quality.md", quality)


def test_record_revises_a_row_by_quality_id(tmp_path, capsys, monkeypatch):
    scan_file(tmp_path)
    path = quality_file(tmp_path)
    decision = {"issues": {"Q-004": {"treatment": "Test-order rows dropped in the view", "status": "corrected",
                                     "correction": "Drop test orders instead of nulling -999; see {Q-005}",
                                     "change": "`foundation/views/01_orders.sql` drops test orders"},
                           "Q-005": {"status": "corrected", "treatment": "Dropped with {Q-004}"}},
                "findings": "none: stale listed no finding reading orders"}
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO(json.dumps(decision)))
    before = path.read_text()
    assert recorder.main([str(tmp_path), "orders", "--dry-run"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["written"] == [] and path.read_text() == before and len(out["rows"]) == 3
    result = recorder.record(tmp_path, "orders", decision, today=TODAY)
    assert result["quality_ids"] == {"Q-004": "Q-004", "Q-005": "Q-005"} and result["added"] == []
    assert result["updated"] == ["Q-004", "Q-005"] and result["corrections"] == ["Q-004"]
    text = path.read_text()
    assert ("| Q-004 | view `orders`, column `amount` | -999 in amount (3 of 45); `orders#sentinel:amount:-999` scanned 2026-10-01 | "
            "Skews totals | Test-order rows dropped in the view | corrected |") in text
    assert "| Q-005 | view `orders` | Test orders, noted by hand | Inflates counts | Dropped with Q-004 | corrected |" in text
    assert ("| 2026-10-09 | Q-004 | Drop test orders instead of nulling -999; see Q-005 | "
            "`foundation/views/01_orders.sql` drops test orders | none: stale listed no finding reading orders |") in text
    # Another ID prefix works the same way.
    path = quality_file(tmp_path, "DQ-")
    result = recorder.record(tmp_path, "orders", {"issues": {"DQ-004": {"status": "open"}}}, today=TODAY)
    assert result["updated"] == ["DQ-004"]
    assert "-999 in amount (3 of 45); `orders#sentinel:amount:-999` scanned 2026-10-01 | Skews totals | Nulled in the view | open |" in path.read_text()


def test_record_rejects_bad_quality_id_keys(tmp_path):
    scan_file(tmp_path)
    path = quality_file(tmp_path)
    before = path.read_text()
    cases = [({"Q-006": {"status": "corrected"}}, "Q-006 is recorded from scan payments, not orders"),
             ({"S1": {"status": "corrected"}, "Q-003": {"status": "open"}}, "S1 and Q-003 both name Q-003"),
             ({"Q-099": {"status": "open"}, "S7": {"status": "open"}}, "issues not in the scan or the quality record: Q-099, S7")]
    for issues, message in cases:
        with pytest.raises(recorder.RecordError, match=message):
            recorder.record(tmp_path, "orders", {"issues": issues}, today=TODAY)
    assert path.read_text() == before


@pytest.mark.parametrize("prefix", ["Q-", "DQ-"])
def test_quality_id_revision_keeps_link_and_placeholder_rules(tmp_path, prefix):
    scan_file(tmp_path)
    quality_file(tmp_path, prefix)
    recorder.record(tmp_path, "orders", {})  # persist the legacy links before revision
    links = tmp_path / "foundation/quality.json"
    before_links = links.read_bytes()
    quality = tmp_path / "foundation/quality.md"
    lines = quality.read_text().splitlines()
    table = recorder.Table(lines, recorder.ACTIVE, "foundation/quality.md")
    for index in [table.header, *[i for i, _ in table.rows()]]:
        cells = recorder._cells(lines[index])
        cells[0], cells[2] = cells[2], cells[0]
        lines[index] = recorder._row(cells)
    quality.write_text("\n".join(lines) + "\n")
    qid = prefix + "003"  # this row's issue is still listed by the scan
    decisions = {"issues": {qid: {"status": "open", "treatment": "See {" + prefix + "004} and {r-003}",
                                 "correction": "Revise {" + qid + "}", "change": "view"}},
                 "findings": "none"}
    result = recorder.record(tmp_path, "orders", decisions, today=TODAY)
    assert result["quality_ids"] == {qid: qid} and result["updated"] == [qid]
    assert links.read_bytes() == before_links
    text = quality.read_text()
    assert "Spaces (2 of 45); `orders#whitespace:dept` scanned 2026-10-01" in text
    assert f"See {prefix}004 and {{r-003}} | open |" in text
    assert f"| 2026-10-09 | {qid} | Revise {qid} | view | none |" in text
    before = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    for missing in ("S99", "Q-099", prefix + "099"):
        decisions["issues"][qid]["treatment"] = "See {" + missing + "}"
        with pytest.raises(recorder.RecordError, match="names no issue recorded in this call or earlier"):
            recorder.record(tmp_path, "orders", decisions, today=TODAY)
        assert {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()} == before


def test_record_ignores_unvalidated_recorded_placeholders(tmp_path):
    scan_file(tmp_path)
    quality_file(tmp_path)
    write(tmp_path, "foundation/quality.json", json.dumps({"schema": "awb-quality-links/1", "links": {}}))
    scan_path = tmp_path / "foundation/scans/orders.json"
    scan = json.loads(scan_path.read_text())
    scan["issues"][0]["recorded"] = {"id": "Q-003", "count": 2, "status": "corrected"}
    scan_path.write_text(json.dumps(scan))
    before = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    with pytest.raises(recorder.RecordError, match="names no issue recorded in this call or earlier"):
        recorder.record(tmp_path, "orders", {"issues": {"Q-005": {"treatment": "See {S2}"}}})
    assert {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()} == before


def test_quality_id_duplicate_keeps_revision_error(tmp_path):
    scan_file(tmp_path)
    quality_rows(tmp_path, ["| Q-003 | view | First | x | y | open |",
                            "| Q-003 | view | Second | x | y | open |"])
    before = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    with pytest.raises(recorder.RecordError, match="foundation/quality.md: 2 active rows have the ID Q-003"):
        recorder.record(tmp_path, "orders", {"issues": {"Q-003": {"status": "corrected"}}})
    assert {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()} == before


def test_record_uses_one_observation_for_link(tmp_path):
    scan_file(tmp_path)
    path = tmp_path / "foundation/scans/orders.json"
    scan = json.loads(path.read_text())
    scan["scanned_at"] = "2026-11-02T10:00:00+00:00"
    scan["issues"][0].update(count=1, of=40)
    new = {**scan["issues"][0], "id": "S3", "key": "sentinel:dept:n/a", "count": 3, "of": 40}
    scan["issues"].append(new)
    path.write_text(json.dumps(scan))
    recorder.record(tmp_path, "orders", {"issues": {"S2": judgment(), "S3": judgment()}}, today=TODAY)
    assert quality_link(tmp_path, "orders", "sentinel:age:9999") == {
        "id": "Q-001", "scan": "orders", "recorded_count": 2, "recorded_of": 45,
        "observed_at": "2026-10-09"}
    assert quality_link(tmp_path, "orders", "sentinel:dept:n/a") == {
        "id": "Q-002", "scan": "orders", "recorded_count": 3, "recorded_of": 40,
        "observed_at": "2026-11-02"}
    quality = (tmp_path / "foundation/quality.md").read_text()
    assert "`orders#sentinel:age:9999` scanned 2026-10-09" in quality
    assert "`orders#sentinel:dept:n/a` scanned 2026-11-02" in quality
    raw = (tmp_path / "foundation/quality.json").read_text()
    assert "sentinel" not in raw and "Sales" not in raw and "n/a" not in raw
    assert raw == json.dumps(json.loads(raw), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def test_record_keeps_unexamined_links(tmp_path):
    scan_file(tmp_path, delta=False)
    recorder.record(tmp_path, "orders", {"issues": {"S1": judgment(), "S2": judgment()}}, today=TODAY)
    path = tmp_path / "foundation/quality.json"
    document = json.loads(path.read_text())
    bkey = hashlib.sha256(b"other\nwhitespace:dept").hexdigest()
    document["links"][bkey] = {"id": "Q-999", "scan": "other", "recorded_count": 17,
                               "recorded_of": 99, "observed_at": "2025-01-01"}
    unseen = hashlib.sha256(b"orders\nrange:amount:0:100").hexdigest()
    document["links"][unseen] = {**document["links"][bkey], "scan": "orders"}
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    def entry_bytes(key):
        return path.read_bytes().split(f'"{key}": '.encode(), 1)[1].split(b"\n    }", 1)[0]
    before = {key: entry_bytes(key) for key in (bkey, unseen)}
    # Even an invalid link is left alone until its scan and key are examined.
    assert not (tmp_path / "foundation/scans/other.json").exists()
    recorder.record(tmp_path, "orders", {"issues": {"S1": {"status": "corrected"}}}, today=TODAY)
    assert {key: entry_bytes(key) for key in (bkey, unseen)} == before


@pytest.mark.parametrize("deleted", [True, False])
def test_orphan_links_do_not_claim_reused_ids(tmp_path, deleted):
    scan_file(tmp_path, delta=False)
    recorder.record(tmp_path, "orders", {"issues": {"S1": judgment()}}, today=TODAY)
    quality = tmp_path / "foundation/quality.md"
    if deleted:
        quality.write_text("\n".join(line for line in quality.read_text().splitlines()
                                     if not line.startswith("| Q-001 |")) + "\n")
    else:
        quality.write_text(quality.read_text().replace("`orders#whitespace:dept`", "Manual observation"))
    assert scanner._recorded(tmp_path, "orders", ["whitespace:dept"]) == {}
    # This unrelated issue can receive the deleted ID, but cannot inherit its link.
    result = recorder.record(tmp_path, "orders", {"issues": {"S2": judgment()}}, today=TODAY)
    assert result["quality_ids"] == {"S2": "Q-001" if deleted else "Q-002"}
    stale = hashlib.sha256(b"orders\nwhitespace:dept").hexdigest()
    assert stale not in json.loads((tmp_path / "foundation/quality.json").read_text())["links"]
    found = scanner._recorded(tmp_path, "orders", ["whitespace:dept", "sentinel:age:9999"])
    assert "whitespace:dept" not in found and found["sentinel:age:9999"]["id"] == result["quality_ids"]["S2"]


@pytest.mark.parametrize("duplicate", ["id", "marker"])
def test_ambiguous_quality_rows_block_only_their_links(tmp_path, duplicate):
    scan_file(tmp_path, delta=False)
    marker = "`orders#whitespace:dept`"
    quality_rows(tmp_path, [f"| Q-001 | view | Spaces (2 of 45); {marker} | x | y | open |",
                            f"| {'Q-001' if duplicate == 'id' else 'Q-002'} | view | {marker if duplicate == 'marker' else 'Other'} | x | y | open |",
                            "| Q-009 | view | Gap noted by hand | x | y | open |",
                            "| Q-009 | view | Another gap noted by hand | x | y | open |"])
    before = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    for dry_run in [False, True]:
        with pytest.raises(recorder.RecordError, match="no single row and ID to link"):
            recorder.record(tmp_path, "orders", {"issues": {"S1": judgment()}}, dry_run=dry_run)
    assert scanner._recorded(tmp_path, "orders", ["whitespace:dept"]) == {}
    assert {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()} == before
    result = recorder.record(tmp_path, "orders", {"issues": {"S2": judgment()}}, today=TODAY)
    assert result["added"] == ["Q-010"]  # an unrelated repeated ID blocks nothing


def test_markers_outside_the_observation_are_not_links(tmp_path):
    scan_file(tmp_path, delta=False)
    quality_rows(tmp_path, ["| Q-001 | view `orders`, column `PO#line` | Codes (2 of 45) | x | See `sources.md#licensing` | open |",
                            "| Q-002 | view `orders`, column `PO#line` | Gaps (1 of 45) | x | See `sources.md#licensing` | open |"])
    result = recorder.record(tmp_path, "orders", {"issues": {"S1": judgment(), "S2": judgment()}}, today=TODAY)
    assert result["added"] == ["Q-003", "Q-004"]
    assert set(scanner._recorded(tmp_path, "orders", ["whitespace:dept", "sentinel:age:9999"])) == {
        "whitespace:dept", "sentinel:age:9999"}


def test_legacy_links_backfill_without_scan_writes(tmp_path):
    scan_file(tmp_path, delta=False)
    path = tmp_path / "foundation/scans/orders.json"
    scan = json.loads(path.read_text())
    scan["issues"][1]["key"] = "near-variants:dept:a|b"
    path.write_text(json.dumps(scan))
    quality_rows(tmp_path, [
        "| Q-003 | view | Spaces (5 of 45); `orders#whitespace:dept` scanned 2026-01-02 | x | y | corrected |",
        "| Q-004 | view | Variants (7 of 50); `orders#near-variants:dept:a\\|b` in [scan](scans/orders.json) 2026-02-03 | x | y | open |"])
    before = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    expected = {"whitespace:dept": {"id": "Q-003", "status": "corrected", "count": 5},
                "near-variants:dept:a|b": {"id": "Q-004", "status": "open", "count": 7}}
    assert scanner._recorded(tmp_path, "orders") == expected
    assert {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()} == before
    decisions = {"issues": {"S1": {"status": "open"}, "S2": {"status": "corrected"}}}
    result = recorder.record(tmp_path, "orders", decisions, dry_run=True)
    assert result["quality_ids"] == {"S1": "Q-003", "S2": "Q-004"}
    assert not (tmp_path / "foundation/quality.json").exists()
    # A first write without reopening preserves both legacy observations in the backfill.
    recorder.record(tmp_path, "orders", {})
    assert quality_link(tmp_path, "orders", "whitespace:dept")["observed_at"] == "2026-01-02"
    assert quality_link(tmp_path, "orders", "near-variants:dept:a|b") == {
        "id": "Q-004", "scan": "orders", "recorded_count": 7, "recorded_of": 50,
        "observed_at": "2026-02-03"}
    assert scanner._recorded(tmp_path, "orders") == expected
    result = recorder.record(tmp_path, "orders", decisions)
    assert result["updated"] == ["Q-003", "Q-004"]


def test_recorded_status_follows_header_and_count_follows_json(tmp_path):
    scan_file(tmp_path, delta=False)
    recorder.record(tmp_path, "orders", {"issues": {"S1": judgment()}}, today=TODAY)
    quality = tmp_path / "foundation/quality.md"
    lines = quality.read_text().splitlines()
    table = recorder.Table(lines, recorder.ACTIVE, "foundation/quality.md")
    for index in [table.header, *[i for i, _ in table.rows()]]:
        cells = recorder._cells(lines[index])
        cells[3], cells[5] = cells[5], cells[3]
        lines[index] = recorder._row(cells)
    quality.write_text("\n".join(lines).replace("(2 of 45)", "(999 of 999)") + "\n")
    assert scanner._recorded(tmp_path, "orders") == {
        "whitespace:dept": {"id": "Q-001", "status": "open", "count": 2}}


@pytest.mark.parametrize("failed_phase", ["B", "C"])
def test_record_failure_reports_phases_and_retries_once(tmp_path, capsys, monkeypatch, failed_phase):
    scan_file(tmp_path)
    state = state_file(tmp_path)
    state.write_text(state.read_text().replace("| supported | |", "| supported | Prior caveat |"))
    decisions = {"issues": {"S1": {**judgment(), "status": "corrected", "correction": "Trim",
                                   "change": "view"}},
                 "flags": [{"investigation": "churn", "result": "r-003", "reason": "{S1} merges labels | codes"}]}
    original = recorder.os.replace
    quality_replaces = 0
    def replace(source, target):
        nonlocal quality_replaces
        if Path(target).name == "quality.md":
            quality_replaces += 1
        if ((failed_phase == "B" and Path(target).name == "findings.json")
                or (failed_phase == "C" and Path(target).name == "quality.md" and quality_replaces == 2)):
            raise PermissionError("injected write failure")
        original(source, target)
    monkeypatch.setattr(recorder.os, "replace", replace)
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(decisions)))
    assert recorder.main([str(tmp_path), "orders"]) == 2
    out = json.loads(capsys.readouterr().err)
    assert out["phases"] == (["A"] if failed_phase == "B" else ["A", "B"])
    expected = ["foundation/quality.json", "foundation/quality.md"]
    if failed_phase == "C":
        expected += ["investigations/churn/findings.json", "investigations/churn/state.md"]
    assert out["written"] == expected
    quality = (tmp_path / "foundation/quality.md").read_text()
    assert "| Q-001 |" in quality and "| Q-001 | Trim |" not in quality
    monkeypatch.setattr(recorder.os, "replace", original)
    result = recorder.record(tmp_path, "orders", decisions, today=TODAY)
    assert result["updated"] == ["Q-001"] and result["added"] == []
    quality = (tmp_path / "foundation/quality.md").read_text()
    assert quality.count("| Q-001 | Trim |") == 1
    text = state.read_text()
    assert text.count("Q-001 merges labels") == 1 and "Prior caveat; Q-001 merges labels \\| codes |" in text
    assert "\\\\|" not in text and not list(tmp_path.rglob("*.tmp"))
    assert "revalidation-needed (was supported)" in text


def test_renamed_quality_headers_keep_template_positions(tmp_path):
    scan_file(tmp_path, delta=False)
    path = quality_file(tmp_path)
    path.write_text(path.read_text().replace("| ID | Affected source or catalog object | Observation and evidence |",
                                              "| Key | Object | Evidence |", 1).replace(
        "| Analytical impact | Current treatment | Status |", "| Impact | Treatment | State |", 1))
    result = recorder.record(tmp_path, "orders", {"issues": {"S2": judgment()}}, today=TODAY)
    assert result["added"] == ["Q-007"]
    row = next(line for line in path.read_text().splitlines() if line.startswith("| Q-007 |"))
    cells = recorder._cells(row)
    assert "`orders#sentinel:age:9999`" in cells[2] and cells[-1] == "open"
    assert scanner._recorded(tmp_path, "orders", ["sentinel:age:9999"]) == {
        "sentinel:age:9999": {"id": "Q-007", "status": "open", "count": 2}}
    assert recorder.record(tmp_path, "orders", {"issues": {"S2": {"status": "corrected"}}})["updated"] == ["Q-007"]
    assert recorder._cells(next(line for line in path.read_text().splitlines()
                                if line.startswith("| Q-007 |")))[-1] == "corrected"

@pytest.mark.parametrize("dry_run", [False, True])
def test_old_provenance_refuses_before_writes(tmp_path, dry_run):
    scan_file(tmp_path)
    state_file(tmp_path)
    write(tmp_path, "src/provenance.py", "# old helper\n")
    before = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    with pytest.raises(recorder.RecordError, match="awb-init repair: install_helpers.py --upgrade"):
        recorder.record(tmp_path, "orders", {"issues": {"S1": judgment()},
                        "flags": [{"investigation": "churn", "result": "r-003", "reason": "{S1}"}]}, dry_run=dry_run)
    assert before == {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}


def test_flag_retry_keeps_original_quality_id(tmp_path, monkeypatch):
    scan_file(tmp_path)
    state = state_file(tmp_path)
    helper = recorder._load_provenance(tmp_path)
    real_flag = helper.flag_findings
    def fail(root, investigation, flags, **kwargs):
        if kwargs.get("check"):
            return real_flag(root, investigation, flags, **kwargs)
        raise ValueError("injected flag failure")
    monkeypatch.setattr(helper, "flag_findings", fail)
    monkeypatch.setattr(recorder, "_load_provenance", lambda root: helper)
    decisions = {"issues": {"S1": {**judgment(), "correction": "Trim", "change": "view"}},
                 "flags": [{"investigation": "churn", "result": "r-003", "reason": "{S1} merges labels"}]}
    with pytest.raises(recorder.RecordError, match="investigations already flagged: none") as failure:
        recorder.record(tmp_path, "orders", decisions, today=TODAY)
    assert failure.value.phases == ["A"]
    assert recorder.record(tmp_path, "orders", {"issues": {"S2": judgment()}}, today=TODAY)["added"] == ["Q-002"]
    monkeypatch.setattr(helper, "flag_findings", real_flag)
    result = recorder.record(tmp_path, "orders", decisions, today=TODAY)
    assert result["quality_ids"] == {"S1": "Q-001"} and result["added"] == []
    assert "Q-001 merges labels" in state.read_text() and "Q-002 merges labels" not in state.read_text()
    recorder.record(tmp_path, "orders", decisions, today=TODAY)
    assert (tmp_path / "foundation/quality.md").read_text().count("| Q-001 | Trim |") == 1



def test_quality_json_is_written_only_when_links_change(tmp_path):
    scan_file(tmp_path, delta=False)
    assert recorder.record(tmp_path, "orders", {})["written"] == []
    assert not (tmp_path / "foundation/quality.json").exists()
    recorder.record(tmp_path, "orders", {"issues": {"S1": judgment()}}, today=TODAY)
    links = (tmp_path / "foundation/quality.json").read_bytes()
    result = recorder.record(tmp_path, "orders", {"issues": {"Q-001": {"treatment": "Trim in the view"}}})
    assert result["written"] == ["foundation/quality.md"]
    assert (tmp_path / "foundation/quality.json").read_bytes() == links


def test_unlinked_marker_row_is_relinked_and_short_rows_read(tmp_path):
    scan_file(tmp_path, delta=False)
    write(tmp_path, "foundation/quality.json", json.dumps({"schema": "awb-quality-links/1", "links": {}}))
    quality_rows(tmp_path, ["| Q-004 | view | Spaces (2 of 45); `orders#whitespace:dept` scanned 2026-10-01 |"])
    assert scanner._recorded(tmp_path, "orders", ["whitespace:dept"]) == {
        "whitespace:dept": {"id": "Q-004", "status": "", "count": 2}}
    result = recorder.record(tmp_path, "orders", {"issues": {"S1": {"status": "corrected"}}}, today=TODAY)
    assert result["updated"] == ["Q-004"] and result["added"] == []
    assert "Q-004" in (tmp_path / "foundation/quality.json").read_text()


def test_failed_phase_a_leaves_no_partial_files(tmp_path, monkeypatch):
    scan_file(tmp_path, delta=False)
    original = recorder.os.replace
    def replace(source, target):
        if Path(target).name == "quality.json":
            raise PermissionError("injected write failure")
        original(source, target)
    monkeypatch.setattr(recorder.os, "replace", replace)
    with pytest.raises(recorder.RecordError) as failure:
        recorder.record(tmp_path, "orders", {"issues": {"S1": judgment()}}, today=TODAY)
    assert failure.value.phases == [] and failure.value.written == []
    assert not list(tmp_path.rglob("*.tmp"))


def test_dry_run_prints_flag_rows_and_writes_nothing(tmp_path):
    scan_file(tmp_path)
    state_file(tmp_path)
    write(tmp_path, "src/provenance.py", (ROOT / ".agents/skills/awb-init/assets/awb_provenance.py").read_text())
    before = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    result = recorder.record(tmp_path, "orders", {"issues": {"S1": judgment()},
                             "flags": [{"investigation": "churn", "result": "r-003", "reason": "{S1} merges labels"}]},
                             dry_run=True, today=TODAY)
    assert "| Sales leads growth | [r-003](evidence/r-003.json) | revalidation-needed (was supported) | Q-001 merges labels |" in result["rows"]
    assert {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()} == before
