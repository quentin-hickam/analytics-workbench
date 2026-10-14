# Kept cases:
# test_record_evidence_records_clean_producing_state: evidence JSON schema/key order and clean producing state.
# test_record_evidence_captures_modified_code: uncommitted producing paths retain status, size and checksum.
# test_record_evidence_rejects_invalid_checks: a check outside the validation record shape raises.
# test_compare_evidence_refuses_evidence_older_than_scoped_3: awb-evidence/1 and unscoped /3 files fail all five comparisons with a rerun instruction.
# test_compare_evidence_clean_committed_state_passes_five_comparisons: clean state passes all five ordered comparisons in the contract shape.
# test_compare_evidence_detects_view_changed_after_recording: view mutation fails the views comparison.
# test_compare_evidence_names_changed_setting: settings mutation fails the settings comparison.
# test_scoped_settings_ignore_other_results_and_tables: only [parameters] and the result's own table count; the file leaves the code comparisons.
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
# test_record_evidence_records_runtime: the runtime block holds this interpreter's Python and platform, the versions of duckdb, pandas, and each requirements.txt name, null when not installed, and the requirements lines it could not read.
# test_requirement_name_reads_names_and_direct_references: every line the review rounds 1-5 probed: names with extras, versions, markers, or @ URL; wheel or sdist file names, winning over a disagreeing #egg=, and #egg= of other direct references (URL, percent-encoded or holding a ";", POSIX or Windows path), -e included, attached, quoted, or after =, with or without trailing extras, with trailing --hash or other per-requirement options and a continuation backslash ignored; options, comments, and references naming no package give none.
# test_read_requirements_follows_includes_and_byte_order_marks: -r and --requirement includes, quoted or not, are read relative to the including file, once each; -c constraints add nothing; a UTF-8, UTF-16 or UTF-32 BOM is decoded; a URL include and a missing include are unread, an absent file is neither.
# test_read_requirements_lists_every_line_it_cannot_read: each line naming no package, an unknown or malformed option, an unbalanced quote, an archive whose #egg= disagrees with its file name (declared by the file name), and an unreadable file are unread with file and line; recognised option lines are not; continued lines are joined.
# test_runtime_records_a_wheel_url_package_and_its_drift: a requirements.txt wheel URL or path, hash-pinned or with extras, continued or not, percent-encoded or holding a ";", a compact -e, a quoted include, and a wheel whose #egg= disagrees (also unread) record their package's installed version, and a changed recorded version is a runtime mismatch.
# test_runtime_records_missing_version_metadata_as_unknown: an installed distribution whose metadata has no Version is unknown, not null (not installed).
# test_cli_stale_reports_runtime_mismatch_as_a_warning: a changed recorded duckdb or Python version, an unread requirements line, or no runtime block, is listed under runtime_mismatches with its findings rows, never under results, and compare_evidence still passes.
# test_record_evidence_requires_the_results_table: settings without the result's table, or unparseable, raise and write no evidence.
# test_producing_paths_follow_the_result: run.py, the result's queries, other investigation code, src/ minus awb.py, provenance.py and packaging/, plus code_paths; other results' queries and the excluded helpers never stale it.
# test_settings_fall_back_to_tomli: without tomllib, settings parse through tomli, and without either the content is unknown.
# test_run_template_records_evidence_and_drops_it_before_rewriting_the_table: prior_result checks the state before unlink; the run.py template records a result and writes its state.md row, keeps it on an identical rerun, and refuses before touching evidence when state.md is missing or drifts; a run failing after the table is rewritten leaves no evidence.

import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

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


SETTINGS = b"[parameters]\nthreshold = 5\n\n[results.r1]\n\n[results.r2]\n"


@pytest.fixture
def project(tmp_path):
    git(tmp_path, "init")
    write(tmp_path, "src/ops.py", b"x = 1\n")
    write(tmp_path, "investigations/inv/run.py", b"import ops\n")
    write(tmp_path, "investigations/inv/settings.toml", SETTINGS)
    write(tmp_path, "investigations/inv/queries/r1.sql", b"select * from orders\n")
    write(tmp_path, "investigations/inv/queries/r2.sql", b"select 2\n")
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
        "acquisitions", "settings", "runtime", "checks", "notes",
    ]
    assert raw.endswith("\n") and raw.startswith('{\n  "schema": "awb-evidence/3",')
    assert evidence["producing_commit"] == git(project, "rev-parse", "HEAD")
    assert evidence["producing_paths"] == ["foundation/views/orders.sql",
        "investigations/inv/queries/r1.sql", "investigations/inv/run.py", "src/ops.py"]
    assert evidence["producing_uncommitted_changes"] == []
    assert evidence["views"][0]["publications"] == ["data/parquet/orders/p1"]
    assert evidence["checks"] == CHECKS
    assert evidence["settings"]["result"] == "r1"
    assert evidence["settings"]["content"] == {"parameters": {"threshold": 5}, "results": {"r1": {}}}
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
            settings_path="investigations/inv/settings.toml",
            checks=[{"name": "scope", "outcome": "ok", "detail": "wrong"}])


def test_compare_evidence_refuses_evidence_older_than_scoped_3(project):
    path = record(project)
    evidence = json.loads(path.read_text())
    for schema, settings in (("awb-evidence/1", evidence["settings"]),
                             ("awb-evidence/3", {k: v for k, v in evidence["settings"].items() if k != "result"})):
        path.write_text(json.dumps({**evidence, "schema": schema, "settings": settings}))
        comparisons = provenance.compare_evidence(project, path)
        assert [c["outcome"] for c in comparisons] == ["fail"] * 5
        assert all("not awb-evidence/3 with result-scoped settings; rerun the result" in c["detail"]
                   for c in comparisons)


NAMES = ["committed-code", "uncommitted-code", "views", "inputs", "settings"]


def test_compare_evidence_clean_committed_state_passes_five_comparisons(project):
    comparisons = provenance.compare_evidence(project, record(project))
    assert [c["name"] for c in comparisons] == NAMES
    assert [c["outcome"] for c in comparisons] == ["pass"] * 5
    assert all(set(c) == {"name", "paths", "outcome", "detail"} for c in comparisons)
    assert comparisons[0]["paths"] == ["foundation/views/orders.sql", "investigations/inv/queries/r1.sql",
                                        "investigations/inv/run.py", "src/ops.py"]
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
    write(project, "investigations/inv/settings.toml", SETTINGS.replace(b"5", b"6"))
    settings = provenance.compare_evidence(project, path)[4]
    assert settings["outcome"] == "fail"
    assert settings["paths"] == ["investigations/inv/settings.toml"]
    assert "parameters" in settings["detail"]


SCOPED = (b'[parameters]\nstart = 2026-01-01\n\n[results.r1]\nqueries = ["queries/r1.sql"]\n'
          b'[results.r1.validation]\nrequired_columns = ["month"]\n')


@pytest.mark.parametrize("edit, fails", [
    (b'\n[results.r2]\nqueries = ["queries/r2.sql"]\n', False),
    (b'\n[eda]\nmax_rows = 10\n', False),
    (b'\n[results.r1.validation.nulls]\nmonth = 0.0\n', True),
    (None, True),
])
def test_scoped_settings_ignore_other_results_and_tables(project, edit, fails):
    if not importlib.util.find_spec("tomllib"):
        pytest.skip("scoping parses TOML")
    write(project, "investigations/inv/settings.toml", SCOPED + b'\n[results.r0]\nqueries = []\n')
    git(project, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c",
        "commit.gpgsign=false", "commit", "-qam", "results layout")
    evidence = json.loads(record(project).read_text())
    assert evidence["settings"]["result"] == "r1"
    assert set(evidence["settings"]["content"]) == {"parameters", "results"}
    assert "investigations/inv/settings.toml" not in evidence["producing_paths"]
    text = (project / "investigations/inv/settings.toml").read_bytes()
    if edit is None:
        text = text.replace(b"2026-01-01", b"2026-02-01")
        text = text.replace(b"[results.r0]\nqueries = []", b"[results.r0]\nqueries = [\"x\"]")
    else:
        text += edit
    write(project, "investigations/inv/settings.toml", text)
    comparisons = provenance.compare_evidence(project, project / "investigations/inv/evidence/r1.json")
    assert [c["outcome"] for c in comparisons[:4]] == ["pass"] * 4
    assert comparisons[4]["outcome"] == ("fail" if fails else "pass")
    if edit is None:
        assert "parameters" in comparisons[4]["detail"] and "r0" not in comparisons[4]["detail"]
    elif fails:
        assert "results.r1" in comparisons[4]["detail"]


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
        record(project)


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


@pytest.mark.parametrize("bad_content, prefix", [(b"{", "missing evidence:"),
                                                 (b' {"schema": "other"}', "unusable evidence:")])
def test_compare_evidence_bad_files_still_return_five_failures(project, bad_content, prefix):
    path = project / "bad.json"
    path.write_bytes(bad_content)
    comparisons = provenance.compare_evidence(project, path)
    assert [c["name"] for c in comparisons] == NAMES
    assert [c["outcome"] for c in comparisons] == ["fail"] * 5
    assert all(c["detail"].startswith(prefix) for c in comparisons)


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
        {"path": "investigations/inv/queries/r1.sql", "status": "uncommitted", "bytes": 21,
         "sha256": hashlib.sha256(b"select * from orders\n").hexdigest()},
        {"path": "investigations/inv/run.py", "status": "uncommitted", "bytes": 11,
         "sha256": hashlib.sha256(b"import ops\n").hexdigest()},
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
        project, "inv", "r1", views=[], publications=[], acquisitions=[],
        settings_path="investigations/inv/settings.toml", checks=checks)
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


@pytest.mark.parametrize("settings, reason", [
    (b"[parameters]\nthreshold = 5\n", "no such table"),
    (b"threshold = \n", "Invalid"),
])
def test_record_evidence_requires_the_results_table(project, settings, reason):
    write(project, "investigations/inv/settings.toml", settings)
    with pytest.raises(ValueError, match=r"must hold \[results\.r1\]") as error:
        record(project)
    assert reason in str(error.value)
    assert not (project / "investigations/inv/evidence/r1.json").exists()


def test_producing_paths_follow_the_result(project):
    write(project, "investigations/inv/lib.py", b"y = 1\n")
    for path in ("src/awb.py", "src/provenance.py", "src/packaging/draft.py"):
        write(project, path, b"# helper\n")
    write(project, "shared/extra.sql", b"select 3\n")
    git(project, "add", ".")
    git(project, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c",
        "commit.gpgsign=false", "commit", "-qm", "more code")
    path = record(project, code_paths=["shared"])
    assert json.loads(path.read_text())["producing_paths"] == [
        "foundation/views/orders.sql", "investigations/inv/lib.py", "investigations/inv/queries/r1.sql",
        "investigations/inv/run.py", "shared/extra.sql", "src/ops.py"]
    for changed in ("investigations/inv/queries/r2.sql", "src/awb.py", "src/provenance.py",
                    "src/packaging/draft.py"):
        write(project, changed, b"-- changed\n")
    assert [c["outcome"] for c in provenance.compare_evidence(project, path)] == ["pass"] * 5
    for changed in ("investigations/inv/queries/r1.sql", "investigations/inv/lib.py", "shared/extra.sql"):
        write(project, changed, b"-- changed\n")
        assert changed in provenance.compare_evidence(project, path)[0]["detail"]


def test_settings_fall_back_to_tomli(project, monkeypatch):
    import tomllib
    monkeypatch.setitem(sys.modules, "tomllib", None)
    monkeypatch.setitem(sys.modules, "tomli", tomllib)
    assert provenance._settings(project, "investigations/inv/settings.toml", "r1")["result"] == "r1"
    monkeypatch.setitem(sys.modules, "tomli", None)
    content = provenance._settings(project, "investigations/inv/settings.toml", "r1")["content"]
    assert "install tomli" in content["unknown"]


def test_run_template_records_evidence_and_drops_it_before_rewriting_the_table(project):
    pytest.importorskip("duckdb")
    pytest.importorskip("pandas")
    assets = ASSET.parent
    for asset, installed in (("awb_provenance.py", "provenance.py"), ("awb_landing.py", "preparation/landing.py"),
                             ("awb_validate.py", "exploration/validate.py")):
        write(project, f"src/{installed}", (assets / asset).read_bytes())
    write(project, "investigations/inv/run.py", (assets / "workbench/investigation/run.py").read_bytes())
    write(project, "investigations/inv/state.md", (assets / "workbench/investigation/state.md").read_bytes())
    write(project, "foundation/views/orders.sql", b"create view orders as select range as n from range(3);\n")
    run = [sys.executable, str(project / "investigations/inv/run.py"), "r1"]
    done = subprocess.run(run, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    line = json.loads(done.stdout)
    assert (line["state"], line["status"]) == ("added", "provisional") and "state_row" not in line
    assert list(provenance.finding_rows(project / "investigations/inv/state.md")) == ["r1"]
    evidence = json.loads((project / line["evidence"]).read_text())
    assert "investigations/inv/queries/r1.sql" in evidence["producing_paths"]
    assert evidence["views"][0]["path"] == "foundation/views/orders.sql"
    state = (project / "investigations/inv/state.md").read_bytes()
    again = subprocess.run(run, capture_output=True, text=True)
    assert json.loads(again.stdout)["state"] == "kept"
    assert (project / "investigations/inv/state.md").read_bytes() == state
    saved_table = (project / "investigations/inv/results/r1.csv").read_bytes()
    saved_evidence = (project / "investigations/inv/evidence/r1.json").read_bytes()
    write(project, "investigations/inv/state.md", state.replace(b"<state the finding from r1>", b"Hand edit"))
    drifted = subprocess.run(run, capture_output=True, text=True)
    assert drifted.returncode == 1 and "state render --investigation inv" in drifted.stdout
    assert (project / "investigations/inv/results/r1.csv").read_bytes() == saved_table
    assert (project / "investigations/inv/evidence/r1.json").read_bytes() == saved_evidence
    (project / "investigations/inv/state.md").unlink()
    unwritten = subprocess.run(run, capture_output=True, text=True)
    assert unwritten.returncode == 1 and "state.md does not exist" in json.loads(unwritten.stdout)["error"]
    assert (project / "investigations/inv/evidence/r1.json").exists()  # prior_result refuses before unlink
    write(project, "investigations/inv/state.md", state)
    write(project, "investigations/inv/settings.toml", SETTINGS.replace(
        b"[results.r1]\n", b'[results.r1]\nviews = ["../outside.sql"]\n'))
    failed = subprocess.run(run, capture_output=True, text=True)
    assert failed.returncode == 1 and "outside the project root" in failed.stdout
    assert (project / "investigations/inv/results/r1.csv").exists()
    assert not (project / "investigations/inv/evidence/r1.json").exists()


def installed(name):
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def test_record_evidence_records_runtime(project):
    evidence = json.loads(record(project).read_text())
    interpreter = {"python": platform.python_version(), "platform": f"{platform.system()}-{platform.machine()}"}
    assert evidence["runtime"] == {**interpreter, "packages": {"duckdb": installed("duckdb"),
                                                               "pandas": installed("pandas")},
                                   "unread_requirements": []}
    write(project, "requirements.txt", b"# comment\nPyTest>=7  # the runner\n-r other.txt\n"
                                       b"awb_fixture.absent; python_version < '4'\nduckdb\n")
    runtime = json.loads(record(project).read_text())["runtime"]
    packages = runtime["packages"]
    assert packages == {"awb-fixture-absent": None, "duckdb": installed("duckdb"),
                        "pandas": installed("pandas"), "pytest": installed("pytest")}
    assert packages["pytest"] is not None
    assert runtime["unread_requirements"] == ["requirements.txt:3: -r other.txt (No such file or directory)"]


def test_requirement_name_reads_names_and_direct_references():
    # Every requirements.txt line the review rounds probed, with the package it names or None.
    digest = "--hash=sha256:" + "0" * 64
    cases = {
        # Names, with extras, versions, markers, @ URL, comments, and trailing options.
        "PyTest>=7  # the runner": "pytest", "pkg[extra]==1 ; python_version < '4'": "pkg",
        "awb_fixture.absent; python_version < '4'": "awb-fixture-absent",
        "pkg --hash=sha256:ab": "pkg", "pkg>=1 --hash=sha256:ab": "pkg", "pkg\t--hash=sha256:ab": "pkg",
        "pkg==1.0 \\": "pkg", "pkg\t# c": "pkg", "foo (>=1.0)": "foo",
        "pkg===1.0": "pkg", "pkg~=1.4": "pkg", "pkg==1.0+local.1": "pkg",
        "Name @ https://example.invalid/y.zip": "name", "pkg@git+https://example.invalid/r.git": "pkg",
        "requests[security] @ https://example.invalid/r.whl": "requests",
        "requests[security] @ https://example.invalid/requests-2.32.3-py3-none-any.whl": "requests",
        # VCS references by #egg=, wherever it sits in the fragment.
        "git+https://example.invalid/org/realpkg.git#egg=Real_Pkg": "real-pkg",
        "git+https://example.invalid/r.git@v1#egg=bar&subdirectory=x": "bar",
        "-e git+https://example.invalid/r.git#subdirectory=x&egg=baz": "baz",
        "-e git+https://example.invalid/r.git#egg=ed": "ed", "--editable=./src/x#egg=edx": "edx",
        "-e git+https://example.invalid/r.git#egg=cfg --config-settings k=v": "cfg",
        "--editable git+ssh://git@example.invalid/r.git#egg=sshpkg": "sshpkg",
        # Round 4: -e with its value attached or quoted, as pip's option parser reads it.
        "-egit+https://example.invalid/repo.git#egg=requests": "requests",
        '-e "git+https://example.invalid/r.git#egg=quoted"': "quoted",
        # Wheel and sdist file names: URL, file URL, bare, relative, and Windows paths.
        "https://example.invalid/wheels/otherpkg-1.0-py3-none-any.whl": "otherpkg",
        "https://example.invalid/scipy-1.14.1-py3-none-any.whl": "scipy",
        "https://example.invalid/scipy-1.14.1-py3-none-any.whl#sha256=ab": "scipy",
        "file:///tmp/foo-1.0-py3-none-any.whl": "foo", "file:///tmp/foo-1.0.tar.gz": "foo",
        "https://example.invalid/foo-1.0.zip?x=1": "foo",
        # Round 4: a ";" inside a URL is part of it (pip ends a URL's marker only at "; "), and the
        # file name is percent-decoded.
        "https://example.invalid/path;param/requests-2.32.3-py3-none-any.whl": "requests",
        "https://example.invalid/requests%2D2.32.3%2Dpy3%2Dnone%2Dany.whl": "requests",
        'https://example.invalid/foo-1.0-py3-none-any.whl ; python_version < "4"': "foo",
        "proj-name-1.0.tar.gz": "proj-name",
        "numpy-1.26.0-cp312-cp312-macosx_11_0_arm64.whl": "numpy", "./dist/foo_bar-2.0.tar.gz": "foo-bar",
        "foo-bar_baz-1.0rc1.tar.gz": "foo-bar-baz",
        r"C:\wheels\foo-1.0-py3-none-any.whl": "foo", r"C:\dist\win_sdist-2.0.tar.gz": "win-sdist",
        # Archives with --hash, other per-requirement options, or a continuation backslash.
        "numpy-1.26.0-cp312-cp312-macosx_11_0_arm64.whl --hash=sha256:ab": "numpy",
        "./dist/numpy-1.26.0.tar.gz --hash=sha256:ab": "numpy",
        "https://example.invalid/numpy-1.26.0.tar.gz --hash=sha256:ab --hash=sha256:cd": "numpy",
        "https://example.invalid/numpy-1.26.0-py3-none-any.whl --hash=sha256:ab": "numpy",
        "https://example.invalid/numpy-1.26.0-py3-none-any.whl --hash=sha256:ab \\": "numpy",
        f"https://example.invalid/scipy-1.14.1-py3-none-any.whl {digest}": "scipy",
        # Archives with extras.
        "requests-2.32.3-py3-none-any.whl[security]": "requests",
        "./dist/requests-2.32.3-py3-none-any.whl[security]": "requests",
        "./dist/requests-2.32.3.tar.gz[security]": "requests",
        f"./dist/requests-2.32.3-py3-none-any.whl[security] {digest}": "requests",
        # Round 5: an archive's file name wins over an #egg= naming another package, as pip installs
        # what the archive is; a matching #egg= or one on a non-archive reference is read as before.
        "https://example.invalid/requests-2.32.3-py3-none-any.whl#egg=urllib3": "requests",
        "https://example.invalid/requests-2.32.3-py3-none-any.whl#egg=Requests": "requests",
        "./dist/requests-2.32.3.tar.gz#egg=urllib3": "requests",
        "-e ./dist/requests-2.32.3.tar.gz#egg=urllib3": "requests",
        "https://example.invalid/o/r/archive/main.zip#egg=foo": "foo",
        # A limit requirement_name() documents: a forge tag archive's file name is not name-version.
        "https://example.invalid/o/r/archive/refs/tags/release-1.0.tar.gz": "release",
        "https://example.invalid/o/r/archive/refs/tags/release-1.0.tar.gz#egg=foo": "release",
        "foo @ https://example.invalid/o/r/archive/refs/tags/release-1.0.tar.gz": "foo",
        # References naming no package, option lines, continued hashes, and comments.
        "src/mypkg": None, "-e .": None, "-e ./local": None, "git+https://example.invalid/r.git": None,
        "https://example.invalid/x/foo.whl": None, "jaraco.zip": None,
        "https://example.invalid/o/r/archive/main.zip": None,
        "-r other.txt": None, '-r "deps/base.txt"': None, "--pre": None, "--no-binary :all:": None, "-c constraints.txt": None, "--index-url https://example.invalid": None,
        "-i https://example.invalid": None, "--extra-index-url=https://example.invalid": None,
        "-f ./wheels": None, "--only-binary :all:": None,
        "    --hash=sha256:ab": None, f"    {digest} \\": None, "    # via pandas": None,
        "# comment": None, "": None,
    }
    assert {line: provenance.requirement_name(line) for line in cases} == cases


def test_read_requirements_follows_includes_and_byte_order_marks(project):
    write(project, "requirements.txt", b"\xef\xbb\xbfscipy\n-r deps/base.txt\n--requirement=missing.txt\n"
                                       b"-r https://example.invalid/remote.txt\n-c constraints.txt\n"
                                       b"-r \"deps/a b.txt\"\n--requirement 'deps/quoted.txt'\n")
    write(project, "deps/base.txt", b"-rmore.txt\nnumpy  # base\n-r ../requirements.txt\n")
    write(project, "deps/more.txt", "pandas\nrequests[security]\n".encode("utf-16"))
    write(project, "deps/a b.txt", b"tomli\n")
    write(project, "deps/quoted.txt", b"pyarrow\n")
    write(project, "constraints.txt", b"constrained==1\n")
    assert provenance.read_requirements(project / "requirements.txt") == (
        ["scipy", "pandas", "requests", "numpy", "tomli", "pyarrow"],
        ["requirements.txt:3: --requirement=missing.txt (No such file or directory)",
         "requirements.txt:4: -r https://example.invalid/remote.txt (a URL include is not fetched)"])
    for encoding in ("utf-16-le", "utf-16-be", "utf-32-le", "utf-32-be"):
        write(project, "requirements.txt", "\ufeffscipy\nnumpy\n".encode(encoding))
        assert provenance.read_requirements(project / "requirements.txt") == (["scipy", "numpy"], []), encoding
    assert provenance.read_requirements(project / "absent.txt") == ([], [])


def test_read_requirements_lists_every_line_it_cannot_read(project):
    write(project, "requirements.txt", (
        "# options and comments are not unread\n-i https://example.invalid\n--pre --no-index\n"
        "-c constraints.txt\n    --hash=sha256:ab\n\n"
        "-e .\nsrc/mypkg\ngit+https://example.invalid/r.git\n--unknown-option x\n-r \"unbalanced.txt\n"
        "\"requests\"\n-e\n--pre=1\n"
        "pkg==1.0 \\\n    --hash=sha256:ab\n-r deps/inner.txt\n").encode())
    write(project, "deps/inner.txt", b"named\n./local/dir\n"
                                     b"https://example.invalid/requests-2.32.3-py3-none-any.whl#egg=urllib3\n")
    names, unread = provenance.read_requirements(project / "requirements.txt")
    assert names == ["pkg", "named", "requests"]
    assert unread == [
        "requirements.txt:7: -e .", "requirements.txt:8: src/mypkg",
        "requirements.txt:9: git+https://example.invalid/r.git", "requirements.txt:10: --unknown-option x",
        'requirements.txt:11: -r "unbalanced.txt', 'requirements.txt:12: "requests"',
        "requirements.txt:13: -e", "requirements.txt:14: --pre=1", "deps/inner.txt:2: ./local/dir",
        "deps/inner.txt:3: https://example.invalid/requests-2.32.3-py3-none-any.whl#egg=urllib3 "
        "(#egg=urllib3 disagrees with the file name; recorded requests)"]
    if sys.platform != "win32" and getattr(os, "geteuid", lambda: 1)() != 0:
        (project / "requirements.txt").chmod(0)
        try:
            assert provenance.read_requirements(project / "requirements.txt") == (
                [], ["requirements.txt (Permission denied)"])
        finally:
            (project / "requirements.txt").chmod(0o644)


def test_runtime_records_a_wheel_url_package_and_its_drift(project, capsys):
    digest = "--hash=sha256:" + "0" * 64
    write(project, "requirements.txt", (
        f"https://example.invalid/pytest-0.0.1-py3-none-any.whl {digest}\n"
        f"./wheels/pluggy-0.0.1-py3-none-any.whl[dev] {digest} \\\n    {digest}\n"
        f"iniconfig-0.0.1-py3-none-any.whl[dev]\n").encode())
    path = record(project)
    evidence = json.loads(path.read_text())
    assert set(evidence["runtime"]["packages"]) == {"duckdb", "iniconfig", "pandas", "pluggy", "pytest"}
    for name in ("iniconfig", "pytest", "pluggy"):
        assert evidence["runtime"]["packages"][name] == installed(name) is not None
        evidence["runtime"]["packages"][name] = "0.0.1-fixture"
    path.write_text(json.dumps(evidence))
    provenance.cli_stale(project, [])
    assert json.loads(capsys.readouterr().out)["runtime_mismatches"][0]["details"] == [
        f"{name} 0.0.1-fixture recorded, {installed(name)} now" for name in ("iniconfig", "pluggy", "pytest")]
    # Round 4's forms: a compact -e, a URL holding ";" or percent-encoding, and a quoted include.
    write(project, "requirements.txt", (
        "-egit+https://example.invalid/repo.git#egg=pytest\n"
        "https://example.invalid/path;param/pluggy-0.0.1-py3-none-any.whl\n"
        "https://example.invalid/iniconfig%2D0.0.1%2Dpy3%2Dnone%2Dany.whl\n"
        '-r "deps/more reqs.txt"\n').encode())
    write(project, "deps/more reqs.txt", b"packaging\n")
    path = record(project)
    evidence = json.loads(path.read_text())
    assert evidence["runtime"]["unread_requirements"] == []
    assert set(evidence["runtime"]["packages"]) == {"duckdb", "iniconfig", "packaging", "pandas", "pluggy", "pytest"}
    for name in ("iniconfig", "packaging", "pluggy", "pytest"):
        assert evidence["runtime"]["packages"][name] == installed(name) is not None
        evidence["runtime"]["packages"][name] = "0.0.1-fixture"
    path.write_text(json.dumps(evidence))
    provenance.cli_stale(project, [])
    assert json.loads(capsys.readouterr().out)["runtime_mismatches"][0]["details"] == [
        f"{name} 0.0.1-fixture recorded, {installed(name)} now"
        for name in ("iniconfig", "packaging", "pluggy", "pytest")]
    # Round 5: a wheel whose #egg= names another package records the wheel's package and its drift,
    # and its line is unread.
    line = "https://example.invalid/pluggy-0.0.1-py3-none-any.whl#egg=iniconfig"
    write(project, "requirements.txt", f"{line}\n".encode())
    path = record(project)
    evidence = json.loads(path.read_text())
    assert set(evidence["runtime"]["packages"]) == {"duckdb", "pandas", "pluggy"}
    evidence["runtime"]["packages"]["pluggy"] = "0.0.1-fixture"
    path.write_text(json.dumps(evidence))
    provenance.cli_stale(project, [])
    assert json.loads(capsys.readouterr().out)["runtime_mismatches"][0]["details"] == [
        f"pluggy 0.0.1-fixture recorded, {installed('pluggy')} now",
        f"requirements not read, packages unrecorded: requirements.txt:1: {line} "
        "(#egg=iniconfig disagrees with the file name; recorded pluggy)"]


@pytest.mark.filterwarnings("ignore:Implicit None:DeprecationWarning")
def test_runtime_records_missing_version_metadata_as_unknown(project, tmp_path, monkeypatch):
    info = tmp_path / "site/broken_package-0.dist-info"
    info.mkdir(parents=True)
    (info / "METADATA").write_text("Metadata-Version: 2.1\nName: broken-package\n")
    monkeypatch.syspath_prepend(str(tmp_path / "site"))
    write(project, "requirements.txt", b"broken-package\n")
    packages = provenance.runtime(project)["packages"]
    assert provenance._is_unknown(packages["broken-package"])
    assert packages["broken-package"]["unknown"].startswith("broken-package: ")


def test_cli_stale_reports_runtime_mismatch_as_a_warning(project, capsys):
    path = record(project)
    row = "| Orders are flat | [r1](evidence/r1.json) | supported | |"
    write(project, "investigations/inv/state.md",
          f"| Finding | Evidence | Status | Caveat |\n| --- | --- | --- | --- |\n{row}\n".encode())
    assert provenance.cli_stale(project, []) == 0
    assert json.loads(capsys.readouterr().out)["runtime_mismatches"] == []
    evidence = json.loads(path.read_text())
    current = evidence["runtime"]["packages"]["duckdb"]
    evidence["runtime"]["packages"]["duckdb"] = "0.0.1-fixture"
    path.write_text(json.dumps(evidence))
    assert provenance.cli_stale(project, []) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["stale"] == 0 and out["results"] == []
    assert out["runtime_mismatches"] == [{
        "investigation": "inv", "result_id": "r1", "evidence": "investigations/inv/evidence/r1.json",
        "details": [f"duckdb 0.0.1-fixture recorded, {current or 'not installed'} now"], "findings": [row]}]
    assert [c["outcome"] for c in provenance.compare_evidence(project, path)] == ["pass"] * 5
    evidence["runtime"]["python"] = "2.7.18"
    path.write_text(json.dumps(evidence))
    provenance.cli_stale(project, [])
    details = json.loads(capsys.readouterr().out)["runtime_mismatches"][0]["details"]
    assert details[:2] == [f"python 2.7.18 recorded, {platform.python_version()} now",
                           f"duckdb 0.0.1-fixture recorded, {current or 'not installed'} now"]
    # A requirements line the runtime could not read is reported verbatim, never dropped: the
    # trailing "." of -e . and a marker's "; " stay the line's own.
    write(project, "requirements.txt", b"-e .\n./vendor/mypkg ; sys_platform == 'linux'\n")
    path = record(project)
    unread = ["requirements.txt:1: -e .", "requirements.txt:2: ./vendor/mypkg ; sys_platform == 'linux'"]
    assert json.loads(path.read_text())["runtime"]["unread_requirements"] == unread
    provenance.cli_stale(project, [])
    out = json.loads(capsys.readouterr().out)
    assert out["stale"] == 0 and out["runtime_mismatches"][0]["details"] == [
        "requirements not read, packages unrecorded: " + line for line in unread]
    evidence = json.loads(path.read_text())
    del evidence["runtime"]
    path.write_text(json.dumps(evidence))
    provenance.cli_stale(project, [])
    out = json.loads(capsys.readouterr().out)
    assert out["stale"] == 0 and out["runtime_mismatches"][0]["details"] == ["evidence records no runtime"]
