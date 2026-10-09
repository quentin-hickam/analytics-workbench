# Kept cases:
# test_record_evidence_records_clean_producing_state: evidence JSON schema/key order and clean producing state.
# test_record_evidence_captures_modified_code: uncommitted producing paths retain status, size and checksum.
# test_record_evidence_rejects_invalid_checks: a check outside the validation record shape raises.
# test_compare_evidence_accepts_schema_1_evidence: evidence written before awb-evidence/2, with its figure entry, still compares clean.
# test_compare_evidence_clean_committed_state_passes_five_comparisons: clean state passes all five ordered comparisons in the contract shape.
# test_compare_evidence_detects_view_changed_after_recording: view mutation fails the views comparison.
# test_compare_evidence_names_changed_setting: settings mutation fails the settings comparison.
# test_compare_evidence_detects_missing_input_and_missing_metadata: missing input file or unavailable metadata fails inputs.
# test_compare_evidence_checks_dirty_code_against_recorded_bytes: uncommitted code mutation fails uncommitted-code.
# test_record_evidence_rejects_destination_symlink_outside_root: regression: evidence destination cannot escape through a symlink.
# test_compare_evidence_without_commit_uses_file_checksums: no-commit evidence compares producing file checksums.
# test_compare_evidence_missing_file_fails_all_five_comparisons: missing evidence fails every comparison.
# test_compare_evidence_bad_files_still_return_five_failures: unreadable JSON or wrong-schema evidence fails every comparison.
# test_compare_evidence_detects_code_metadata_and_data_changes: committed-code mutation; publication/acquisition metadata and data mutations fail inputs.
# test_record_evidence_before_first_commit_checksums_every_producing_file: uncommitted evidence state records checksums for all producing files.
# test_compare_evidence_resolves_landing_helper_layout: metadata-relative files and acquisition-relative input paths.
# test_record_evidence_stores_validation_record_unchanged: validation record stored unchanged under checks.
# test_record_evidence_keeps_symlinked_code_at_its_given_path: regression: symlinked producing code keeps its given path.
# test_compare_evidence_reports_current_state_failures_without_missing_evidence: regressions: deleted current view is a mismatch; missing producing commit has precise detail.
# test_compare_evidence_outside_root_returns_five_failures: regression: evidence path outside root returns five failures.
# test_record_evidence_raises_on_git_failure_after_reading_head: regression: a Git failure after HEAD is read raises instead of relabelling the commit uncommitted.
# test_record_evidence_derives_inputs_from_views: omitted publications/acquisitions equal the explicit ones; results/ is not producing code.
# test_views_read_follows_view_references: views read by FROM/JOIN/comma, transitively; a column alias is not a read.
# test_finding_row_reuses_state_text_and_names_check_gaps: the row keeps existing finding text, escapes pipes, names failed and unassessed checks.
# test_cli_stale_lists_changed_results_with_their_findings: stale lists failing results with state.md rows, missing linked evidence, skips non-evidence JSON, rejects an unknown investigation.

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess

import pytest


if shutil.which("git") is None:
    pytest.skip("git is required", allow_module_level=True)

ASSET = Path(__file__).resolve().parents[1] / ".agents/skills/awb-init/assets/awb_provenance.py"
spec = importlib.util.spec_from_file_location("awb_provenance", ASSET)
provenance = importlib.util.module_from_spec(spec)
spec.loader.exec_module(provenance)


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True,
                          text=True).stdout.strip()


def write(root, path, content):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)


@pytest.fixture
def project(tmp_path):
    git(tmp_path, "init")
    write(tmp_path, "src/ops.py", b"x = 1\n")
    write(tmp_path, "investigations/inv/run.py", b"import ops\n")
    write(tmp_path, "investigations/inv/settings.toml", b"threshold = 5\n")
    write(tmp_path, "foundation/views/orders.sql",
          b"select * from read_parquet('data/parquet/orders/p1/*.parquet');\n")
    write(tmp_path, "data/parquet/orders/p1/part-0.parquet", b"parquet bytes")
    write(tmp_path, "data/raw/crm/a1/page-1.json", b"[]\n")
    publication = {
        "inputs": [{"source": "crm", "acquisition_id": "a1", "files": [
            {"path": "page-1.json", "sha256": hashlib.sha256(b"[]\n").hexdigest()}]}],
        "conversion_commit": "conversion-id",
        "files": [{"path": "part-0.parquet", "bytes": 13,
                   "sha256": hashlib.sha256(b"parquet bytes").hexdigest()}],
    }
    acquisition = {
        "request": "fixture", "started_at": "2026-10-07T00:00:00+00:00",
        "completed_at": "2026-10-07T00:00:01+00:00", "status": "complete",
        "files": [{"path": "page-1.json", "bytes": 3,
                   "sha256": hashlib.sha256(b"[]\n").hexdigest(), "records": 0}],
    }
    write(tmp_path, "data/parquet/orders/p1/publication.json", json.dumps(publication).encode())
    write(tmp_path, "data/raw/crm/a1/provenance.json", json.dumps(acquisition).encode())
    git(tmp_path, "add", ".")
    git(tmp_path, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c",
        "commit.gpgsign=false", "commit", "-m", "fixture")
    return tmp_path


CHECKS = [{"name": "scope", "outcome": "pass", "detail": "fixture population"}]


def record(root, **kwargs):
    return provenance.record_evidence(
        root, "inv", "r1", views=["foundation/views/orders.sql"],
        publications=["data/parquet/orders/p1"], acquisitions=["data/raw/crm/a1"],
        settings_path="investigations/inv/settings.toml", checks=CHECKS, **kwargs)


def test_record_evidence_records_clean_producing_state(project):
    path = record(project)
    assert path == project / "investigations/inv/evidence/r1.json"
    raw = path.read_text()
    evidence = json.loads(raw)
    assert list(evidence) == [
        "schema", "investigation", "result_id", "recorded_at", "producing_commit",
        "producing_paths", "producing_uncommitted_changes", "views", "publications",
        "acquisitions", "settings", "checks", "notes",
    ]
    assert raw.endswith("\n") and raw.startswith('{\n  "schema": "awb-evidence/2",')
    assert evidence["producing_commit"] == git(project, "rev-parse", "HEAD")
    assert evidence["producing_paths"] == ["foundation/views/orders.sql",
        "investigations/inv/run.py", "investigations/inv/settings.toml", "src/ops.py"]
    assert evidence["producing_uncommitted_changes"] == []
    assert evidence["views"][0]["publications"] == ["data/parquet/orders/p1"]
    assert evidence["checks"] == CHECKS
    if importlib.util.find_spec("tomllib"):
        assert evidence["settings"]["content"] == {"threshold": 5}
    assert evidence["publications"][0]["files"] == [{"path": "part-0.parquet", "bytes": 13,
        "sha256": hashlib.sha256(b"parquet bytes").hexdigest()}]
    assert evidence["acquisitions"][0]["status"] == "complete"
    assert evidence["notes"] is None


def test_record_evidence_captures_modified_code(project):
    write(project, "src/ops.py", b"x = 2\n")
    evidence = json.loads(record(project).read_text())
    assert evidence["producing_uncommitted_changes"] == [
        {"path": "src/ops.py", "status": "M", "bytes": 6,
         "sha256": hashlib.sha256(b"x = 2\n").hexdigest()}]


def test_record_evidence_rejects_invalid_checks(project):
    with pytest.raises(ValueError):
        provenance.record_evidence(project, "inv", "r1", views=[], publications=[], acquisitions=[],
            settings_path=None, checks=[{"name": "scope", "outcome": "ok", "detail": "wrong"}])


def test_compare_evidence_accepts_schema_1_evidence(project):
    path = record(project)
    evidence = json.loads(path.read_text())
    evidence["schema"] = "awb-evidence/1"
    evidence["figure"] = None
    path.write_text(json.dumps(evidence))
    assert [c["outcome"] for c in provenance.compare_evidence(project, path)] == ["pass"] * 5


NAMES = ["committed-code", "uncommitted-code", "views", "inputs", "settings"]


def test_compare_evidence_clean_committed_state_passes_five_comparisons(project):
    comparisons = provenance.compare_evidence(project, record(project))
    assert [c["name"] for c in comparisons] == NAMES
    assert [c["outcome"] for c in comparisons] == ["pass"] * 5
    assert all(set(c) == {"name", "paths", "outcome", "detail"} for c in comparisons)
    assert comparisons[0]["paths"] == ["foundation/views/orders.sql", "investigations/inv/run.py",
                                        "investigations/inv/settings.toml", "src/ops.py"]
    assert comparisons[1]["paths"] == [] and "nothing to compare" in comparisons[1]["detail"]


def test_compare_evidence_detects_view_changed_after_recording(project):
    path = record(project)
    write(project, "foundation/views/orders.sql", b"select 1;\n")
    view_check = provenance.compare_evidence(project, path)[2]
    assert view_check["outcome"] == "fail"
    assert view_check["paths"] == ["foundation/views/orders.sql"]
    assert "foundation/views/orders.sql" in view_check["detail"]
    assert "sha256" in view_check["detail"] and "publications" in view_check["detail"]


def test_compare_evidence_names_changed_setting(project):
    path = record(project)
    write(project, "investigations/inv/settings.toml", b"threshold = 6\n")
    settings = provenance.compare_evidence(project, path)[4]
    assert settings["outcome"] == "fail"
    assert settings["paths"] == ["investigations/inv/settings.toml"]
    if importlib.util.find_spec("tomllib"):
        assert "threshold" in settings["detail"]


def test_compare_evidence_detects_missing_input_and_missing_metadata(project):
    path = record(project)
    (project / "data/parquet/orders/p1/part-0.parquet").unlink()
    inputs = provenance.compare_evidence(project, path)[3]
    assert inputs["outcome"] == "fail"
    assert "data/parquet/orders/p1/part-0.parquet" in inputs["detail"] and "missing" in inputs["detail"]
    (project / "data/parquet/orders/p1/publication.json").unlink()
    missing = provenance.compare_evidence(project, record(project))[3]
    assert missing["outcome"] == "fail" and missing["detail"].startswith("missing evidence:")


def test_compare_evidence_checks_dirty_code_against_recorded_bytes(project):
    write(project, "src/ops.py", b"x = 2\n")
    path = record(project)
    write(project, "src/ops.py", b"x = 3\n")
    comparisons = provenance.compare_evidence(project, path)
    assert comparisons[0]["outcome"] == "pass"
    assert "src/ops.py" not in comparisons[0]["paths"]
    assert comparisons[1]["outcome"] == "fail"
    assert comparisons[1]["paths"] == ["src/ops.py"]
    assert "src/ops.py" in comparisons[1]["detail"]


def test_record_evidence_rejects_destination_symlink_outside_root(project):
    directory = project / "investigations/inv/evidence"
    directory.symlink_to(project.parent, target_is_directory=True)
    with pytest.raises(ValueError):
        record(project, code_paths=[])


def test_compare_evidence_without_commit_uses_file_checksums(project):
    git(project, "update-ref", "-d", "HEAD")
    path = record(project)
    comparisons = provenance.compare_evidence(project, path)
    assert [c["outcome"] for c in comparisons] == ["pass"] * 5
    assert comparisons[0]["detail"] == "no producing commit; producing files compared under uncommitted-code"
    write(project, "src/ops.py", b"x = 3\n")
    assert provenance.compare_evidence(project, path)[1]["outcome"] == "fail"


def test_compare_evidence_missing_file_fails_all_five_comparisons(project):
    comparisons = provenance.compare_evidence(project, "investigations/inv/evidence/absent.json")
    assert [c["name"] for c in comparisons] == NAMES
    assert [c["outcome"] for c in comparisons] == ["fail"] * 5
    assert all(c["detail"].startswith("missing evidence:") for c in comparisons)


@pytest.mark.parametrize("bad_content", [b"{", b' {"schema": "other"}'])
def test_compare_evidence_bad_files_still_return_five_failures(project, bad_content):
    path = project / "bad.json"
    path.write_bytes(bad_content)
    comparisons = provenance.compare_evidence(project, path)
    assert [c["name"] for c in comparisons] == NAMES
    assert [c["outcome"] for c in comparisons] == ["fail"] * 5
    assert all(c["detail"].startswith("missing evidence:") for c in comparisons)


@pytest.mark.parametrize("path,new_bytes", [
    ("src/ops.py", b"x = 2\n"),
    ("data/parquet/orders/p1/part-0.parquet", b"different"),
    ("data/raw/crm/a1/page-1.json", b"[1]\n"),
    ("data/raw/crm/a1/provenance.json", b"{}"),
    ("data/parquet/orders/p1/publication.json", b"{}"),
])
def test_compare_evidence_detects_code_metadata_and_data_changes(project, path, new_bytes):
    evidence = record(project)
    write(project, path, new_bytes)
    check = provenance.compare_evidence(project, evidence)[0 if path.startswith("src/") else 3]
    assert check["outcome"] == "fail" and path in check["detail"]


def test_record_evidence_before_first_commit_checksums_every_producing_file(project):
    git(project, "update-ref", "-d", "HEAD")
    evidence = json.loads(record(project).read_text())
    assert evidence["producing_commit"] == "uncommitted"
    assert evidence["producing_uncommitted_changes"] == [
        {"path": "foundation/views/orders.sql", "status": "uncommitted", "bytes": 64,
         "sha256": hashlib.sha256(b"select * from read_parquet('data/parquet/orders/p1/*.parquet');\n").hexdigest()},
        {"path": "investigations/inv/run.py", "status": "uncommitted", "bytes": 11,
         "sha256": hashlib.sha256(b"import ops\n").hexdigest()},
        {"path": "investigations/inv/settings.toml", "status": "uncommitted", "bytes": 14,
         "sha256": hashlib.sha256(b"threshold = 5\n").hexdigest()},
        {"path": "src/ops.py", "status": "uncommitted", "bytes": 6,
         "sha256": hashlib.sha256(b"x = 1\n").hexdigest()},
    ]


def test_compare_evidence_resolves_landing_helper_layout(project):
    # The exact provenance.json and publication.json layout that awb_landing.py writes: files[].path
    # is relative to the directory holding the JSON file, and a publication's inputs[].files[].path is
    # copied from the acquisition's provenance, so it is relative to the acquisition directory.
    pages = {"pages/page-1.json": b'[{"id": 1}]\n', "pages/page-2.json": b'[{"id": 2}]\n'}
    parts = {"part/part-0.parquet": b"parquet zero", "part/part-1.parquet": b"parquet one"}
    for name, content in pages.items():
        write(project, f"data/raw/crm/a2/{name}", content)
    for name, content in parts.items():
        write(project, f"data/parquet/orders/p2/{name}", content)
    acquisition_files = [{"path": name, "bytes": len(content),
                          "sha256": hashlib.sha256(content).hexdigest(), "records": 1}
                         for name, content in sorted(pages.items())]
    landed_provenance = {
        "source": "crm", "acquisition_id": "a2", "request": {"endpoint": "orders"},
        "started_at": "2026-10-07T00:00:00+00:00", "completed_at": "2026-10-07T00:00:01+00:00",
        "status": "complete", "files": acquisition_files, "notes": None,
    }
    landed_publication = {
        "dataset": "orders", "publication_id": "p2",
        "inputs": [{"source": "crm", "acquisition_id": "a2",
                    "files": [{"path": f["path"], "sha256": f["sha256"]} for f in acquisition_files]}],
        "conversion_commit": git(project, "rev-parse", "HEAD"),
        "converted_at": "2026-10-07T00:00:02+00:00",
        "files": [{"path": name, "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}
                  for name, content in sorted(parts.items())],
        "notes": None,
    }
    write(project, "data/raw/crm/a2/provenance.json", (json.dumps(landed_provenance, indent=2) + "\n").encode())
    write(project, "data/parquet/orders/p2/publication.json",
          (json.dumps(landed_publication, indent=2) + "\n").encode())
    write(project, "foundation/views/orders.sql",
          b"select * from read_parquet('data/parquet/orders/p2/part/*.parquet');\n")
    path = provenance.record_evidence(
        project, "inv", "r2", views=["foundation/views/orders.sql"], publications=["data/parquet/orders/p2"],
        acquisitions=["data/raw/crm/a2"], settings_path="investigations/inv/settings.toml", checks=CHECKS)
    evidence = json.loads(path.read_text())
    assert evidence["views"][0]["publications"] == ["data/parquet/orders/p2"]
    publication, acquisition = evidence["publications"][0], evidence["acquisitions"][0]
    assert {k: publication[k] for k in ("inputs", "conversion_commit", "files")} == {
        k: landed_publication[k] for k in ("inputs", "conversion_commit", "files")}
    assert acquisition["status"] == "complete" and acquisition["files"] == acquisition_files
    inputs = provenance.compare_evidence(project, path)[3]
    assert inputs["outcome"] == "pass", inputs["detail"]
    assert "data/raw/crm/a2/pages/page-1.json" in inputs["paths"]
    assert "data/parquet/orders/p2/part/part-1.parquet" in inputs["paths"]
    write(project, "data/raw/crm/a2/pages/page-2.json", b"[]\n")
    (project / "data/parquet/orders/p2/part/part-0.parquet").unlink()
    inputs = provenance.compare_evidence(project, path)[3]
    assert inputs["outcome"] == "fail"
    assert "data/raw/crm/a2/pages/page-2.json" in inputs["detail"]
    assert "data/parquet/orders/p2/part/part-0.parquet: missing" in inputs["detail"]


def test_record_evidence_stores_validation_record_unchanged(project):
    # The shape validate() in awb_validate.py returns: seven {name, outcome, detail} checks in order.
    checks = [{"name": "columns", "outcome": "pass", "detail": "Required columns present: 2."},
              {"name": "row_counts", "outcome": "fail", "detail": "Step dedupe lost 3 rows."},
              {"name": "joins", "outcome": "not-applicable", "detail": "not assessed"},
              {"name": "nulls", "outcome": "pass", "detail": "Null rates: amount 0.0%."},
              {"name": "scope", "outcome": "pass", "detail": "Orders placed in 2026."},
              {"name": "metrics", "outcome": "not-applicable", "detail": "not assessed"},
              {"name": "values", "outcome": "pass", "detail": "Totals reconcile with finance."}]
    path = provenance.record_evidence(
        project, "inv", "r1", views=[], publications=[], acquisitions=[], settings_path=None,
        checks=checks, code_paths=[])
    assert json.loads(path.read_text())["checks"] == checks


def test_record_evidence_keeps_symlinked_code_at_its_given_path(project):
    write(project, "shared/lib.py", b"y = 1\n")
    (project / "src/link.py").symlink_to("../shared/lib.py")
    evidence = json.loads(record(project).read_text())
    assert "src/link.py" in evidence["producing_paths"]
    assert "shared/lib.py" not in evidence["producing_paths"]


def test_compare_evidence_reports_current_state_failures_without_missing_evidence(project):
    path = record(project)
    (project / "foundation/views/orders.sql").unlink()
    views = provenance.compare_evidence(project, path)[2]
    assert views["outcome"] == "fail"
    assert views["detail"] == "foundation/views/orders.sql: missing."
    evidence = json.loads(path.read_text())
    evidence["producing_commit"] = "0" * 40
    path.write_text(json.dumps(evidence))
    committed = provenance.compare_evidence(project, path)[0]
    assert committed["outcome"] == "fail"
    assert committed["detail"] == f"producing commit {'0' * 40} is not in this repository."


def test_compare_evidence_outside_root_returns_five_failures(project, tmp_path_factory):
    outside = tmp_path_factory.mktemp("outside") / "r1.json"
    comparisons = provenance.compare_evidence(project, outside)
    assert [c["name"] for c in comparisons] == NAMES
    assert all(c["outcome"] == "fail" and c["detail"].startswith("missing evidence:") for c in comparisons)


def test_record_evidence_raises_on_git_failure_after_reading_head(project):
    (project / ".git/index").write_bytes(b"corrupt")
    with pytest.raises(subprocess.CalledProcessError):
        record(project)
    assert not (project / "investigations/inv/evidence/r1.json").exists()


def test_record_evidence_derives_inputs_from_views(project):
    explicit = json.loads(record(project).read_text())
    write(project, "investigations/inv/results/r1.csv", b"a\n1\n")
    path = provenance.record_evidence(project, "inv", "r1", views=["foundation/views/orders.sql"],
                                      settings_path="investigations/inv/settings.toml", checks=CHECKS)
    derived = json.loads(path.read_text())
    assert [p["path"] for p in derived["publications"]] == ["data/parquet/orders/p1"]
    assert [a["path"] for a in derived["acquisitions"]] == ["data/raw/crm/a1"]
    assert derived["publications"] == explicit["publications"]
    assert derived["acquisitions"] == explicit["acquisitions"]
    assert "investigations/inv/results/r1.csv" not in derived["producing_paths"]
    assert [c["outcome"] for c in provenance.compare_evidence(project, path)] == ["pass"] * 5


def test_views_read_follows_view_references(project):
    write(project, "foundation/views/02_monthly.sql",
          b"CREATE OR REPLACE VIEW monthly AS SELECT month, count(*) AS n FROM main.orders GROUP BY 1;\n")
    write(project, "foundation/views/03_customers.sql", b"create view customers as select 1 as id;\n")
    write(project, "foundation/views/orders.sql", b"create view orders as "
          b"select * from read_parquet('data/parquet/orders/p1/*.parquet');\n")
    write(project, "investigations/inv/queries/a.sql", b"select month, n as customers from monthly;\n")
    write(project, "investigations/inv/queries/b.sql", b'select * from customers c, "monthly" m;\n')
    assert provenance.views_read(project, ["investigations/inv/queries/a.sql"]) == [
        "foundation/views/02_monthly.sql", "foundation/views/orders.sql"]
    assert provenance.views_read(project, [project / "investigations/inv/queries/b.sql"]) == [
        "foundation/views/02_monthly.sql", "foundation/views/03_customers.sql", "foundation/views/orders.sql"]


def test_finding_row_reuses_state_text_and_names_check_gaps(project):
    checks = [{"name": "columns", "outcome": "fail", "detail": "Missing x."},
              {"name": "joins", "outcome": "not-applicable", "detail": "not assessed"},
              {"name": "values", "outcome": "not-applicable", "detail": "No value drives it."}]
    assert provenance.finding_row(project, "inv", "r1", checks, finding="A | B") == (
        r"| A \| B | [r1](evidence/r1.json) | provisional | failed checks: columns; not assessed: joins |")
    write(project, "investigations/inv/state.md",
          b"| Finding | Evidence | Status | Caveat |\n| --- | --- | --- | --- |\n"
          b"| Orders \\| rose 4% | [r1](evidence/r1.json) | supported | |\n")
    assert provenance.finding_row(project, "inv", "r1", checks[2:]) == (
        r"| Orders \| rose 4% | [r1](evidence/r1.json) | provisional |  |")
    assert provenance.finding_row(project, "inv", "r2", []).startswith("| <state the finding from r2> |")


def test_cli_stale_lists_changed_results_with_their_findings(project, capsys):
    record(project)
    provenance.record_evidence(project, "inv", "r2", views=[], checks=CHECKS,
                               settings_path="investigations/inv/settings.toml")
    row = "| Orders are flat | [r1](evidence/r1.json) | supported | |"
    write(project, "investigations/inv/state.md",
          f"| Finding | Evidence | Status | Caveat |\n| --- | --- | --- | --- |\n{row}\n"
          "| Gone | [r9](./evidence/r9.json) | provisional | |\n".encode())
    write(project, "investigations/inv/evidence/r1-export-checks.json", b"[]\n")
    assert provenance.cli_stale(project, []) == 0
    clean = json.loads(capsys.readouterr().out)
    assert clean["checked"] == 3 and clean["skipped"] == ["investigations/inv/evidence/r1-export-checks.json"]
    assert [r["result_id"] for r in clean["results"]] == ["r9"]
    write(project, "foundation/views/orders.sql", b"select 1;\n")
    assert provenance.cli_stale(project, ["--investigation", "inv"]) == 0
    out = json.loads(capsys.readouterr().out)
    stale = {r["result_id"]: r for r in out["results"]}
    assert out["stale"] == 2 and set(stale) == {"r1", "r9"}
    assert stale["r1"]["evidence"] == "investigations/inv/evidence/r1.json"
    assert stale["r1"]["findings"] == [row]
    assert [f["name"] for f in stale["r1"]["failed"]] == ["committed-code", "views"]
    assert "foundation/views/orders.sql" in stale["r1"]["failed"][1]["detail"]
    assert stale["r9"]["failed"][0]["detail"].startswith("missing evidence:")
    assert provenance.cli_stale(project, ["--investigation", "absent"]) == 2
