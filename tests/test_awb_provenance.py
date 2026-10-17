# Kept cases:
# test_record_evidence_records_clean_producing_state: evidence JSON schema/key order and clean producing state.
# test_record_evidence_captures_modified_code: uncommitted producing paths retain status, size and checksum.
# test_record_evidence_rejects_invalid_checks: a check outside the validation record shape raises.
# test_compare_evidence_refuses_evidence_older_than_scoped_3: awb-evidence/1 and unscoped /3 files fail all five comparisons with a rerun instruction.
# test_compare_evidence_clean_committed_state_passes_five_comparisons: clean state passes all five ordered comparisons in the contract shape.
# test_compare_evidence_detects_view_changed_after_recording: view mutation fails the views comparison.
# test_compare_evidence_names_changed_setting: settings mutation fails the settings comparison.
# test_scoped_settings_ignore_other_results_and_tables: recorded without parameters=, evidence keeps [parameters] whole and the result's own table, so another result's table never counts; the file leaves the code comparisons.
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
# test_read_requirements_reports_each_include_of_a_missing_file: a missing file included twice, or by two files, is unread at every include; a readable file included twice is read once.
# test_read_requirements_lists_every_line_it_cannot_read: each line naming no package, an unknown or malformed option, an unbalanced quote, an archive whose #egg= disagrees with its file name (declared by the file name), and an unreadable file are unread with file and line; recognised option lines are not; continued lines are joined.
# test_runtime_records_a_wheel_url_package_and_its_drift: a requirements.txt wheel URL or path, hash-pinned or with extras, continued or not, percent-encoded or holding a ";", a compact -e, a quoted include, and a wheel whose #egg= disagrees (also unread) record their package's installed version, and a changed recorded version is a runtime mismatch.
# test_runtime_records_missing_version_metadata_as_unknown: an installed distribution whose metadata has no Version is unknown, not null (not installed).
# test_cli_stale_reports_runtime_mismatch_as_a_warning: a changed recorded duckdb or Python version, an unread requirements line, or no runtime block, is listed under runtime_mismatches with its findings rows, never under results, and compare_evidence still passes.
# test_record_evidence_requires_the_results_table: settings without the result's table, or unparseable, raise and write no evidence.
# test_producing_paths_are_an_allow_list: producing paths are run.py, the result's queries, its producer module (written or not), its declared code, code_paths, and src/ minus awb.py, provenance.py and packaging/; another result's producer and query, notes, prose, an undeclared file, and the excluded helpers leave it current, committed or not, while each producing path stales it, a producer written later included.
# test_run_py_edit_stales_every_result: an edit to run.py fails committed-code for every result (it passed before the allow list too; kept as its guard).
# test_declared_file_a_query_reads_stales_its_result: a lookup CSV a result's query reads directly, declared in code, stales the result when it changes, committed or not, while an unrelated note leaves it current.
# test_record_evidence_refuses_declared_code_that_does_not_exist: a code path the table declares must exist; nothing is written otherwise.
# test_declared_code_under_an_ignored_directory_is_recorded_by_checksum: a declared file under an ignored directory is recorded as uncommitted, so it passes while unchanged, committed or not, and an edit to it fails uncommitted-code.
# test_evidence_records_only_the_parameters_a_result_reads: with the parameters run.py passes, evidence records the [parameters] its queries name as $name and its table lists; an added parameter leaves both results current, changing one stales only the result that reads it, and a parameter a result starts to read stales it once [parameters] or its table changes.
# test_result_parameters_are_the_names_queries_read_and_the_table_lists: $name in comments counts, $1 names nothing absent from [parameters]; reading another name, with [] or get(), raises KeyError naming the fix, $name only for a name a query can hold; a listed name [parameters] does not set raises with [] and gives get()'s default; a listed name may hold '-'.
# test_evidence_with_every_parameter_compares_on_each_until_rerun: evidence recorded without the parameters its producer received (before scoping, or by an older run.py) records every entry and compares on each; a rerun with them records only those the result reads and keeps its row.
# test_result_ids_name_their_producer_module: an ID maps to producers/<id>.py exactly; an ID outside the grammar is refused by producer_path and result_problems.
# test_settings_fall_back_to_tomli: without tomllib, settings parse through tomli, and without either the content is unknown.
# test_record_evidence_copies_question_and_inputs_verbatim: the settings question and inputs land in the evidence unchanged, and editing the question stales only the settings comparison.
# test_record_evidence_refuses_a_result_without_its_question: a missing, blank, or multi-line question, inputs that are not a list of names, code that is not a list of paths or names a directory or a path outside the project, or parameters that are not a list of names, raise and write no evidence.
# test_run_template_refuses_results_without_a_question: run.py exits 2 naming every wanted result that lacks a question, before opening a session or writing anything; without duckdb.
# test_run_template_loads_each_producer_by_result_id: run.py loads producers/<id>.py by result ID with run() and only the parameters the result reads; an undeclared read, even through get(), fails that result alone; declaring it fixes the run; a module without produce() is named; an ID that cannot name its module exits 2 before anything runs.
# test_run_template_registers_each_producer_module: a producer module defining a dataclass under postponed annotations loads and runs, since run.py registers it by name, and its output is the saved table.
# test_run_template_names_each_producer_module_apart: IDs that differ only in '.', '-', or '_' load their producer modules under distinct names, so one never takes another's sys.modules entry.
# test_run_template_checks_declared_code_before_running: a missing declared code path exits 2 naming it before anything runs, leaving the prior evidence and table unchanged.
# test_investigation_views_are_producing_code_for_every_result: each .sql file in the investigation's views/ is a producing path of every result, recorded or not with a commit; an edit stales them all, and so does a view file added after recording, committed or not, while another file there does not.
# test_result_problems_refuses_views_that_are_not_view_files: a views entry must be a project-relative .sql file directly under foundation/views/ or the investigation's views/; a logical view name, a missing file, a non-.sql file, a nested or outside path, an absolute path, and a non-list are refused, naming the entry.
# test_result_problems_accepts_view_files_and_refuses_a_non_list: a foundation view file, written with ./ or not, and a file in the investigation's views/ pass; views that is not a list of non-empty strings is refused with or without the folder.
# test_run_template_refuses_a_views_entry_that_is_not_a_file: run.py exits 2 naming a views entry that is a view's logical name, before opening a session or writing anything; without duckdb.
# test_run_template_loads_shared_views_on_one_thread: run.py's session loads investigations/<name>/views/*.sql after the foundation views, in name order, on one thread; a producer imports a helper module from the investigation folder by name; evidence records the shared SQL as producing code and the foundation view it reads; an edit to the shared SQL stales the result.
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


SETTINGS = (b'[parameters]\nthreshold = 5\n\n[results.r1]\nquestion = "How many orders cleared the threshold?"\n\n'
            b'[results.r2]\nquestion = "Which regions grew?"\n')


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
        "schema", "investigation", "result_id", "question", "inputs", "recorded_at", "producing_commit",
        "producing_paths", "producing_uncommitted_changes", "views", "publications",
        "acquisitions", "settings", "runtime", "checks", "notes",
    ]
    assert raw.endswith("\n") and raw.startswith('{\n  "schema": "awb-evidence/3",')
    assert evidence["producing_commit"] == git(project, "rev-parse", "HEAD")
    assert evidence["producing_paths"] == ["foundation/views/orders.sql", "investigations/inv/producers/r1.py",
        "investigations/inv/queries/r1.sql", "investigations/inv/run.py", "src/ops.py"]
    assert evidence["producing_uncommitted_changes"] == []
    assert evidence["views"][0]["publications"] == ["data/parquet/orders/p1"]
    assert evidence["checks"] == CHECKS
    assert evidence["settings"]["result"] == "r1"
    assert evidence["settings"]["content"] == {
        "parameters": {"threshold": 5}, "results": {"r1": {"question": "How many orders cleared the threshold?"}}}
    assert (evidence["question"], evidence["inputs"]) == ("How many orders cleared the threshold?", [])
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
    assert comparisons[0]["paths"] == ["foundation/views/orders.sql", "investigations/inv/producers/r1.py",
                                        "investigations/inv/queries/r1.sql", "investigations/inv/run.py", "src/ops.py"]
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


SCOPED = (b'[parameters]\nstart = 2026-01-01\n\n[results.r1]\nquestion = "How many orders each month?"\n'
          b'queries = ["queries/r1.sql"]\n'
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
        {"path": "investigations/inv/producers/r1.py", "status": "uncommitted", "bytes": None, "sha256": None},
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
        "checks": [],
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
        r"| A \| B | [r1](evidence/r1.json) | provisional | association | failed checks: columns; not assessed: joins |")
    assert provenance.finding_row(project, "inv", "r1", [], claim="descriptive").endswith(
        "| provisional | descriptive |  |")
    write(project, "investigations/inv/state.md",
          b"| Finding | Evidence | Status | Claim | Caveat |\n| --- | --- | --- | --- | --- |\n"
          b"| Orders \\| rose 4% | [r1](evidence/r1.json) | supported | causal (experiment: price test) | |\n")
    assert provenance.finding_row(project, "inv", "r1", checks[2:]) == (
        r"| Orders \| rose 4% | [r1](evidence/r1.json) | provisional | causal (experiment: price test) |  |")
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


QUESTION = "Did returns rise after the \u201cspring\u201d price change: yes or no?  "


def test_record_evidence_copies_question_and_inputs_verbatim(project):
    write(project, "investigations/inv/settings.toml", SETTINGS.replace(
        b'question = "How many orders cleared the threshold?"',
        f'question = "{QUESTION}"\ninputs = ["orders", "regions_view"]'.encode()))
    path = record(project)
    evidence = json.loads(path.read_text())
    assert (evidence["question"], evidence["inputs"]) == (QUESTION, ["orders", "regions_view"])
    assert evidence["settings"]["content"]["results"]["r1"]["question"] == QUESTION
    text = (project / "investigations/inv/settings.toml").read_text()
    write(project, "investigations/inv/settings.toml", text.replace("spring", "summer").encode())
    comparisons = provenance.compare_evidence(project, path)
    assert [c["outcome"] for c in comparisons] == ["pass"] * 4 + ["fail"]
    assert "results.r1" in comparisons[4]["detail"]


@pytest.mark.parametrize("table, problem", [
    (b"", "[results.r1] has no question; add question = "),
    (b'question = "   "\n', "[results.r1] has no question"),
    (b'question = 5\n', "[results.r1] has no question"),
    (b'question = """How many\norders?"""\n', "[results.r1] question spans several lines"),
    (b'question = "How many?"\ninputs = "orders"\n', "[results.r1] inputs must be a list of dataset or view names"),
    (b'question = "How many?"\ninputs = ["orders", ""]\n', "[results.r1] inputs must be a list"),
    (b'question = "How many?"\ncode = "helpers.py"\n', "[results.r1] code must be a list of paths"),
    (b'question = "How many?"\ncode = [""]\n', "[results.r1] code must be a list of paths"),
    (b'question = "How many?"\nparameters = "threshold"\n', "[results.r1] parameters must be a list of [parameters] names"),
    (b'question = "How many?"\nparameters = ["a b"]\n', "[results.r1] parameters must be a list of [parameters] names"),
    (b'question = "How many?"\nparameters = ["$threshold"]\n', "[results.r1] parameters must be a list of"),
    (b'question = "How many?"\ncode = ["queries"]\n', "[results.r1] code names queries, a directory; list the files"),
    (b'question = "How many?"\ncode = ["../../../outside.py"]\n',
     "[results.r1] code names ../../../outside.py, which is outside the project"),
])
def test_record_evidence_refuses_a_result_without_its_question(project, table, problem):
    write(project, "investigations/inv/settings.toml", b"[parameters]\nthreshold = 5\n\n[results.r1]\n" + table)
    with pytest.raises(ValueError, match="investigations/inv/settings.toml: ") as error:
        record(project)
    assert problem in str(error.value)
    assert not (project / "investigations/inv/evidence/r1.json").exists()


def commit_all(root, message="work"):
    git(root, "add", "-A")
    git(root, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c",
        "commit.gpgsign=false", "commit", "-qm", message)


def outcomes(root, result_id="r1"):
    return [c["outcome"] for c in provenance.compare_evidence(root, f"investigations/inv/evidence/{result_id}.json")]


def record_r2(root):
    return provenance.record_evidence(root, "inv", "r2", views=[], checks=CHECKS,
                                      settings_path="investigations/inv/settings.toml")


def test_producing_paths_are_an_allow_list(project):
    write(project, "investigations/inv/settings.toml",
          SETTINGS.replace(b"[results.r1]\n", b'[results.r1]\ncode = ["helpers.py"]\n'))
    write(project, "investigations/inv/helpers.py", b"y = 1\n")
    write(project, "investigations/inv/lib.py", b"z = 1\n")
    write(project, "investigations/inv/methodology.md", b"# Method\n")
    for path in ("src/awb.py", "src/provenance.py", "src/packaging/draft.py"):
        write(project, path, b"# helper\n")
    write(project, "shared/extra.sql", b"select 3\n")
    commit_all(project, "more code")
    path = record(project, code_paths=["shared"])
    assert json.loads(path.read_text())["producing_paths"] == [
        "foundation/views/orders.sql", "investigations/inv/helpers.py", "investigations/inv/producers/r1.py",
        "investigations/inv/queries/r1.sql", "investigations/inv/run.py", "shared/extra.sql", "src/ops.py"]
    # What cannot change r1's numbers leaves it current, committed or not: another result's producer
    # and query, prose and notes, an undeclared file, and the helpers that only dispatch, record, or package.
    for changed, content in (("investigations/inv/producers/r2.py", b"def produce(connection, sql, parameters):\n"),
                             ("investigations/inv/notes.md", b"# Notes\n"),
                             ("investigations/inv/methodology.md", b"# Method, revised\n"),
                             ("investigations/inv/lib.py", b"z = 2\n"),
                             ("investigations/inv/queries/r2.sql", b"select 4\n"),
                             ("src/awb.py", b"# changed\n"), ("src/provenance.py", b"# changed\n"),
                             ("src/packaging/draft.py", b"# changed\n")):
        write(project, changed, content)
    assert outcomes(project) == ["pass"] * 5
    commit_all(project, "unrelated edits")
    assert outcomes(project) == ["pass"] * 5
    # Each producing path stales it: run.py, its query, its own producer, its declared code, code_paths, src/.
    for changed in ("investigations/inv/run.py", "investigations/inv/queries/r1.sql",
                    "investigations/inv/producers/r1.py", "investigations/inv/helpers.py", "shared/extra.sql",
                    "src/ops.py"):
        before = (project / changed).read_bytes() if (project / changed).exists() else None
        write(project, changed, b"# changed\n")
        committed = provenance.compare_evidence(project, path)[0]
        assert committed["outcome"] == "fail" and changed in committed["detail"], changed
        if before is None:
            (project / changed).unlink()
        else:
            write(project, changed, before)
        assert outcomes(project) == ["pass"] * 5, changed
    # A producer module written after recording stales its result, untracked or committed.
    write(project, "investigations/inv/producers/r1.py", b"def produce(connection, sql, parameters):\n")
    detail = provenance.compare_evidence(project, path)[0]["detail"]
    assert "investigations/inv/producers/r1.py: created after the producing commit" in detail
    commit_all(project, "r1 producer")
    assert "investigations/inv/producers/r1.py" in provenance.compare_evidence(project, path)[0]["detail"]


def test_investigation_views_are_producing_code_for_every_result(project):
    write(project, "investigations/inv/views/01_screen.sql", b"create view screened as select * from orders;\n")
    write(project, "investigations/inv/views/README.md", b"# Shared SQL\n")
    commit_all(project, "shared sql")
    assert provenance.investigation_views(project, "inv") == ["investigations/inv/views/01_screen.sql"]
    with pytest.raises(ValueError):
        provenance.investigation_views(project, "../inv")
    record(project)
    record_r2(project)
    for result_id in ("r1", "r2"):
        paths = json.loads((project / f"investigations/inv/evidence/{result_id}.json").read_text())["producing_paths"]
        assert "investigations/inv/views/01_screen.sql" in paths and "investigations/inv/views/README.md" not in paths
        assert outcomes(project, result_id) == ["pass"] * 5
    write(project, "investigations/inv/views/README.md", b"# Shared SQL, revised\n")
    assert outcomes(project, "r1") == outcomes(project, "r2") == ["pass"] * 5
    write(project, "investigations/inv/views/01_screen.sql", b"create view screened as select 1;\n")
    for result_id in ("r1", "r2"):
        detail = provenance.compare_evidence(project, f"investigations/inv/evidence/{result_id}.json")[0]["detail"]
        assert detail == "investigations/inv/views/01_screen.sql: differs from producing commit."
    git(project, "checkout", "--", "investigations/inv/views/01_screen.sql")
    # A view file added later loads in every result session, so it stales every result, committed or not.
    write(project, "investigations/inv/views/02_more.sql", b"create view more as select 2;\n")
    for committed in (False, True):
        if committed:
            commit_all(project, "another view")
        for result_id in ("r1", "r2"):
            check = provenance.compare_evidence(project, f"investigations/inv/evidence/{result_id}.json")[0]
            assert check["outcome"] == "fail", committed
            assert "investigations/inv/views/02_more.sql: added after the result was recorded" in check["detail"]
    # Without a commit, every producing path is checksummed, the shared SQL included.
    git(project, "update-ref", "-d", "HEAD")
    path = record(project)
    changes = {e["path"] for e in json.loads(path.read_text())["producing_uncommitted_changes"]}
    assert {"investigations/inv/views/01_screen.sql", "investigations/inv/views/02_more.sql"} <= changes
    write(project, "investigations/inv/views/03_late.sql", b"create view late as select 3;\n")
    assert "03_late.sql: added after the result was recorded" in provenance.compare_evidence(project, path)[0]["detail"]


@pytest.mark.parametrize(("views", "named"), [
    (["orders"], "orders"),
    (["yellow_trips", "foundation/views/orders.sql"], "yellow_trips"),
    (["foundation/views/missing.sql"], "foundation/views/missing.sql"),
    (["foundation/views/notes.txt"], "foundation/views/notes.txt"),
    (["foundation/views/sub/nested.sql"], "foundation/views/sub/nested.sql"),
    (["foundation/../outside.sql"], "foundation/../outside.sql"),
    (["investigations/other/views/x.sql"], "investigations/other/views/x.sql"),
    (["/abs/foundation/views/orders.sql"], "/abs/foundation/views/orders.sql"),
])
def test_result_problems_refuses_views_that_are_not_view_files(project, views, named):
    write(project, "foundation/views/notes.txt", b"not a view\n")
    write(project, "foundation/views/sub/nested.sql", b"select 1;\n")
    write(project, "outside.sql", b"select 1;\n")
    write(project, "investigations/other/views/x.sql", b"select 1;\n")
    folder = project / "investigations/inv"
    table = {"question": "Which?", "views": views}
    problems = provenance.result_problems("r1", table, folder=folder)
    assert len(problems) == 1 and f"views names {named}, which is not a view file" in problems[0], problems
    # record_evidence refuses it too, writing nothing.
    write(project, "investigations/inv/settings.toml",
          SETTINGS.replace(b"[results.r1]\n", f"[results.r1]\nviews = {json.dumps(views)}\n".encode()))
    with pytest.raises(ValueError, match="views names"):
        record(project)
    assert not (project / "investigations/inv/evidence/r1.json").exists()


def test_result_problems_accepts_view_files_and_refuses_a_non_list(project):
    write(project, "investigations/inv/views/01_screen.sql", b"select 1;\n")
    folder = project / "investigations/inv"
    accepted = ["foundation/views/orders.sql", "./foundation/views/orders.sql", "investigations/inv/views/01_screen.sql"]
    assert provenance.result_problems("r1", {"question": "Which?", "views": accepted}, folder=folder) == []
    for views in ("foundation/views/orders.sql", [""], [3]):
        assert provenance.result_problems("r1", {"question": "Which?", "views": views}) == [
            '[results.r1] views must be a list of view files, as views = ["foundation/views/orders.sql"]']


def test_run_py_edit_stales_every_result(project):
    record(project)
    record_r2(project)
    assert outcomes(project, "r1") == outcomes(project, "r2") == ["pass"] * 5
    write(project, "investigations/inv/run.py", b"import ops  # harness changed\n")
    for result_id in ("r1", "r2"):
        committed = provenance.compare_evidence(project, f"investigations/inv/evidence/{result_id}.json")[0]
        assert committed["outcome"] == "fail"
        assert committed["detail"] == "investigations/inv/run.py: differs from producing commit."


def test_declared_file_a_query_reads_stales_its_result(project):
    # A file a result's query reads directly, with no producer module, counts only when its table declares it.
    write(project, "investigations/inv/queries/r1.sql",
          b"select * from read_csv('investigations/inv/region_map.csv')\n")
    write(project, "investigations/inv/region_map.csv", b"region,label\nw,West\n")
    write(project, "investigations/inv/settings.toml",
          SETTINGS.replace(b"[results.r1]\n", b'[results.r1]\ncode = ["region_map.csv"]\n'))
    commit_all(project, "lookup")
    path = record(project)
    assert "investigations/inv/region_map.csv" in json.loads(path.read_text())["producing_paths"]
    commit_all(project, "evidence")
    write(project, "investigations/inv/notes.md", b"# Notes\n")
    commit_all(project, "notes")
    assert outcomes(project) == ["pass"] * 5
    write(project, "investigations/inv/region_map.csv", b"region,label\nw,Western\n")
    committed = provenance.compare_evidence(project, path)[0]
    assert committed["outcome"] == "fail" and "investigations/inv/region_map.csv" in committed["detail"]
    commit_all(project, "lookup changed")
    committed = provenance.compare_evidence(project, path)[0]
    assert committed["outcome"] == "fail" and "investigations/inv/region_map.csv" in committed["detail"]


def test_record_evidence_refuses_declared_code_that_does_not_exist(project):
    write(project, "investigations/inv/settings.toml",
          SETTINGS.replace(b"[results.r1]\n", b'[results.r1]\ncode = ["helpers.py"]\n'))
    with pytest.raises(ValueError, match=r"\[results.r1\] code names helpers.py, which does not exist"):
        record(project)
    assert not (project / "investigations/inv/evidence/r1.json").exists()


def test_declared_code_under_an_ignored_directory_is_recorded_by_checksum(project):
    write(project, ".gitignore", b"/data/cache/\n")
    write(project, "data/cache/lookup.csv", b"code,label\na,1\n")
    write(project, "investigations/inv/settings.toml",
          SETTINGS.replace(b"[results.r1]\n", b'[results.r1]\ncode = ["../../data/cache/lookup.csv"]\n'))
    commit_all(project, "lookup")
    path = record(project)
    evidence = json.loads(path.read_text())
    assert "data/cache/lookup.csv" in evidence["producing_paths"]
    assert [e["path"] for e in evidence["producing_uncommitted_changes"]] == ["data/cache/lookup.csv"]
    assert outcomes(project) == ["pass"] * 5
    commit_all(project, "evidence")
    assert outcomes(project) == ["pass"] * 5
    write(project, "data/cache/lookup.csv", b"code,label\na,2\n")
    assert outcomes(project) == ["pass", "fail", "pass", "pass", "pass"]
    assert "data/cache/lookup.csv" in provenance.compare_evidence(project, path)[1]["detail"]


PARAMETERS = (b'[parameters]\nthreshold = 5\nregion = "west"\n\n'
              b'[results.r1]\nquestion = "How many orders cleared the threshold?"\n\n'
              b'[results.r2]\nquestion = "Which regions grew?"\nparameters = ["region"]\n')


def reads(root, result_id):
    """The parameters run.py passes a result's producer, and so record_evidence: result_parameters()."""
    import tomllib
    settings = tomllib.loads((root / "investigations/inv/settings.toml").read_text())
    table = settings["results"][result_id]
    texts = [(root / "investigations/inv" / query).read_text()
             for query in table.get("queries", [f"queries/{result_id}.sql"])]
    return provenance.result_parameters(texts, table, settings["parameters"])


def parameters_fixture(project):
    write(project, "investigations/inv/settings.toml", PARAMETERS)
    write(project, "investigations/inv/queries/r1.sql", b"select * from orders where amount > $threshold\n")
    commit_all(project, "parameters")


def test_evidence_records_only_the_parameters_a_result_reads(project):
    parameters_fixture(project)
    content = {r: json.loads(p.read_text())["settings"]["content"] for r, p in (
        ("r1", record(project, parameters=reads(project, "r1"))),
        ("r2", provenance.record_evidence(project, "inv", "r2", views=[], checks=CHECKS,
                                          settings_path="investigations/inv/settings.toml",
                                          parameters=reads(project, "r2"))))}
    # r1's query names $threshold; r2 lists region in its table's parameters.
    assert content["r1"]["parameters"] == {"threshold": 5} and content["r2"]["parameters"] == {"region": "west"}
    settings = project / "investigations/inv/settings.toml"
    settings.write_bytes(PARAMETERS.replace(b'region = "west"\n', b'region = "west"\nstart = 2026-01-01\n'))
    assert outcomes(project, "r1") == outcomes(project, "r2") == ["pass"] * 5
    for old, new, stale in ((b'region = "west"', b'region = "east"', "r2"), (b"threshold = 5", b"threshold = 6", "r1")):
        settings.write_bytes(PARAMETERS.replace(old, new))
        for result_id in ("r1", "r2"):
            compared = provenance.compare_evidence(project, f"investigations/inv/evidence/{result_id}.json")[4]
            assert compared["outcome"] == ("fail" if result_id == stale else "pass"), (new, result_id)
            assert result_id != stale or compared["detail"].endswith("settings differ for keys parameters.")
    # A parameter the result starts to read counts before [parameters] holds it.
    settings.write_bytes(PARAMETERS.replace(b'parameters = ["region"]', b'parameters = ["region", "cutoff"]'))
    assert outcomes(project, "r2")[4] == "fail"
    settings.write_bytes(PARAMETERS)
    write(project, "investigations/inv/queries/r1.sql",
          b"select * from orders where amount > $threshold and $cutoff\n")
    settings.write_bytes(PARAMETERS.replace(b"threshold = 5\n", b"threshold = 5\ncutoff = 1\n"))
    assert outcomes(project, "r1")[4] == "fail"


def test_result_parameters_are_the_names_queries_read_and_the_table_lists():
    parameters = {"threshold": 5, "region": "west", "start": "2026-01-01", "unused": 1}
    scoped = provenance.result_parameters(
        ["select * from t where n > $threshold -- since $start\n", "select $1"], {"parameters": ["region"]},
        parameters)
    assert scoped == {"threshold": 5, "region": "west", "start": "2026-01-01"}
    with pytest.raises(KeyError, match="'unused' is not among the parameters this result reads"):
        scoped["unused"]
    with pytest.raises(KeyError, match="parameters = \\[...\\]"):
        scoped.get("unused", 0)
    assert scoped.get("threshold") == 5 and "unused" not in scoped
    assert provenance.result_parameters(["select 1"], {}, parameters) == {}
    # A listed name [parameters] does not set: get() gives its default, and [] says it is not set.
    listed = provenance.result_parameters(["select 1"], {"parameters": ["cutoff"]}, {"threshold": 1})
    assert listed == {} and listed.get("cutoff", 10) == 10 and listed.get("cutoff") is None
    with pytest.raises(KeyError, match=r"'cutoff' is not set in \[parameters\]"):
        listed["cutoff"]
    with pytest.raises(KeyError, match="'threshold' is not among"):
        listed.get("threshold", 0)
    # A TOML bare key may hold '-', which no query can name, so only the table's list reads it.
    hyphen = {"question": "How many?", "parameters": ["min-orders"]}
    assert provenance.result_problems("r1", hyphen) == []
    dashed = provenance.result_parameters(["select * from t where n > $min"], hyphen, {"min-orders": 3, "max-orders": 9})
    assert dashed == {"min-orders": 3} and dashed["min-orders"] == 3
    with pytest.raises(KeyError) as error:
        dashed["max-orders"]
    assert "$" not in str(error.value) and "list it in its settings table's parameters" in str(error.value)


def test_evidence_with_every_parameter_compares_on_each_until_rerun(project):
    # Evidence written before parameters were scoped, or by an older run.py whose producers receive every
    # [parameters] entry, records each one, and each counts until the result is rerun.
    parameters_fixture(project)
    write(project, "investigations/inv/state.md", (ASSET.parent / "workbench/investigation/state.md").read_bytes())
    write(project, "investigations/inv/results/r1.csv", b"n\n1\n")
    path = record(project)
    assert json.loads(path.read_text())["settings"]["content"]["parameters"] == {"threshold": 5, "region": "west"}
    provenance.record_finding(project, "inv", "r1", CHECKS)
    settings = project / "investigations/inv/settings.toml"
    settings.write_bytes(PARAMETERS.replace(b'region = "west"\n', b'region = "west"\nstart = 2026-01-01\n'))
    assert outcomes(project) == ["pass"] * 5
    settings.write_bytes(PARAMETERS.replace(b'region = "west"', b'region = "east"'))
    assert outcomes(project) == ["pass"] * 4 + ["fail"]
    # A rerun through run.py records only what r1 reads, and its unchanged table, checks, and settings keep the row.
    prior = provenance.prior_result(project, "inv", "r1")
    record(project, parameters=reads(project, "r1"))
    assert provenance.record_finding(project, "inv", "r1", CHECKS, prior=prior)["action"] == "kept"
    assert outcomes(project) == ["pass"] * 5
    settings.write_bytes(PARAMETERS.replace(b"threshold = 5", b"threshold = 6"))
    assert outcomes(project) == ["pass"] * 4 + ["fail"]


@pytest.mark.parametrize("result_id, module", [
    ("r1", "producers/r1.py"), ("orders-by-month", "producers/orders-by-month.py"),
    ("r_1.v2", "producers/r_1.v2.py"), ("2026Q1", "producers/2026Q1.py"),
    ("../escape", None), (".hidden", None), ("a/b", None), ("a b", None), ("-r1", None), ("", None),
])
def test_result_ids_name_their_producer_module(result_id, module):
    problems = provenance.result_problems(result_id, {"question": "How many?"})
    if module is None:
        with pytest.raises(ValueError, match="result ID"):
            provenance.producer_path(result_id)
        assert problems and "ID must start with a letter or digit" in problems[0]
    else:
        assert provenance.producer_path(result_id) == module and problems == []


def test_settings_fall_back_to_tomli(project, monkeypatch):
    import tomllib
    monkeypatch.setitem(sys.modules, "tomllib", None)
    monkeypatch.setitem(sys.modules, "tomli", tomllib)
    assert provenance._settings(project, "investigations/inv/settings.toml", "r1")["result"] == "r1"
    monkeypatch.setitem(sys.modules, "tomli", None)
    content = provenance._settings(project, "investigations/inv/settings.toml", "r1")["content"]
    assert "install tomli" in content["unknown"]


def test_run_template_refuses_results_without_a_question(project):
    assets = ASSET.parent
    write(project, "src/provenance.py", (assets / "awb_provenance.py").read_bytes())
    # Stand-ins for the duckdb and pandas helpers: opening a session would leave a marker.
    write(project, "src/exploration/validate.py", b"profile = validate = None\n")
    write(project, "src/preparation/landing.py",
          b"from pathlib import Path\n\ndef session(root, **options):\n    Path(root, 'opened').touch()\n    raise SystemExit(9)\n")
    write(project, "investigations/inv/run.py", (assets / "workbench/investigation/run.py").read_bytes())
    write(project, "investigations/inv/settings.toml",
          SETTINGS + b'\n[results.r3]\n\n[results.r4]\nquestion = "Two\\nlines?"\n')
    run = [sys.executable, str(project / "investigations/inv/run.py")]
    for argv, named in (([], ["r3", "r4"]), (["r1", "r3"], ["r3"])):
        done = subprocess.run(run + argv, capture_output=True, text=True)
        assert (done.returncode, done.stdout) == (2, "")
        assert [line.split("]")[0] for line in done.stderr.splitlines()] == [
            f"settings.toml: [results.{r}" for r in named]
    assert "[results.r3] has no question" in done.stderr
    assert not any((project / p).exists() for p in ("opened", "investigations/inv/results", "investigations/inv/evidence"))
    done = subprocess.run(run + ["r1"], capture_output=True, text=True)
    assert done.returncode == 9 and (project / "opened").exists()  # a result with its question runs


def test_run_template_refuses_a_views_entry_that_is_not_a_file(project):
    assets = ASSET.parent
    write(project, "src/provenance.py", (assets / "awb_provenance.py").read_bytes())
    write(project, "src/exploration/validate.py", b"profile = validate = None\n")
    write(project, "src/preparation/landing.py",
          b"from pathlib import Path\n\ndef session(root, **options):\n    Path(root, 'opened').touch()\n"
          b"    raise SystemExit(9)\n")
    write(project, "investigations/inv/run.py", (assets / "workbench/investigation/run.py").read_bytes())
    # A logical view name passed the run and was recorded as a missing file; it is now refused first.
    write(project, "investigations/inv/settings.toml", SETTINGS.replace(
        b"[results.r1]\n", b'[results.r1]\nviews = ["orders", "foundation/views/orders.sql"]\n'))
    done = subprocess.run([sys.executable, str(project / "investigations/inv/run.py")], capture_output=True, text=True)
    assert (done.returncode, done.stdout) == (2, "")
    assert done.stderr == ("settings.toml: [results.r1] views names orders, which is not a view file under "
                           "foundation/views/ or investigations/inv/views/; list view files by project-relative path\n")
    assert not any((project / p).exists() for p in ("opened", "investigations/inv/results", "investigations/inv/evidence"))


def test_run_template_loads_shared_views_on_one_thread(project):
    pytest.importorskip("duckdb")
    pytest.importorskip("pandas")
    install_run_template(project)
    # The shared SQL reads a foundation view; a second file reads the first, so name order matters.
    write(project, "investigations/inv/views/01_screen.sql", b"create view screened as select n from orders where n > 0;\n")
    write(project, "investigations/inv/views/02_top.sql", b"create view top as select max(n) as n from screened;\n")
    write(project, "investigations/inv/helpers.py", b"LABEL = 'screened'\n")
    write(project, "investigations/inv/queries/r1.sql", b"select n from screened order by n\n")
    write(project, "investigations/inv/producers/r1.py", b"import helpers\n\n"
          b"def produce(connection, sql, parameters):\n"
          b"    threads = connection.execute(\"select current_setting('threads')\").fetchone()[0]\n"
          b"    top = connection.execute('select n from top').fetchone()[0]\n"
          b"    return run(connection, sql[0], parameters).assign(label=helpers.LABEL, threads=threads, top=top), {}\n")
    write(project, "investigations/inv/settings.toml",
          SETTINGS.replace(b"[results.r1]\n", b'[results.r1]\ncode = ["helpers.py"]\n'))
    run = [sys.executable, str(project / "investigations/inv/run.py"), "r1"]
    done = subprocess.run(run, capture_output=True, text=True)
    assert done.returncode == 0, done.stdout + done.stderr
    assert (project / "investigations/inv/results/r1.csv").read_text() == (
        "n,label,threads,top\n1,screened,1,2\n2,screened,1,2\n")
    evidence = json.loads((project / "investigations/inv/evidence/r1.json").read_text())
    assert {"investigations/inv/views/01_screen.sql", "investigations/inv/views/02_top.sql",
            "investigations/inv/helpers.py"} <= set(evidence["producing_paths"])
    # The query names only the shared view; the foundation view it reads is recorded through it.
    assert [view["path"] for view in evidence["views"]] == ["foundation/views/orders.sql"]
    assert outcomes(project) == ["pass"] * 5
    write(project, "investigations/inv/views/01_screen.sql", b"create view screened as select n from orders;\n")
    assert outcomes(project)[:2] != ["pass", "pass"]


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
    assert (line["state"], line["status"], line["claim"]) == ("added", "provisional", "association")
    assert "state_row" not in line
    assert list(provenance.finding_rows(project / "investigations/inv/state.md")) == ["r1"]
    evidence = json.loads((project / line["evidence"]).read_text())
    assert evidence["question"] == "How many orders cleared the threshold?"
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
    # A producer that drops its result's table from settings makes recording fail after the table is written.
    write(project, "investigations/inv/producers/r1.py", b"from pathlib import Path\n\n"
          b"def produce(connection, sql, parameters):\n"
          b"    frame = run(connection, sql[0], parameters)\n"
          b"    Path(__file__).parents[1].joinpath('settings.toml').write_text('[parameters]\\n')\n"
          b"    return frame, {}\n")
    failed = subprocess.run(run, capture_output=True, text=True)
    assert failed.returncode == 1 and "must hold [results.r1]" in failed.stdout
    assert (project / "investigations/inv/results/r1.csv").exists()
    assert not (project / "investigations/inv/evidence/r1.json").exists()


def install_run_template(project):
    assets = ASSET.parent
    for asset, installed in (("awb_provenance.py", "provenance.py"), ("awb_landing.py", "preparation/landing.py"),
                             ("awb_validate.py", "exploration/validate.py")):
        write(project, f"src/{installed}", (assets / asset).read_bytes())
    write(project, "investigations/inv/run.py", (assets / "workbench/investigation/run.py").read_bytes())
    write(project, "investigations/inv/state.md", (assets / "workbench/investigation/state.md").read_bytes())
    write(project, "foundation/views/orders.sql", b"create view orders as select range as n from range(3);\n")


def test_run_template_loads_each_producer_by_result_id(project):
    pytest.importorskip("duckdb")
    pytest.importorskip("pandas")
    install_run_template(project)
    write(project, "investigations/inv/settings.toml", b'[parameters]\nthreshold = 1\nunused = 9\n\n'
          b'[results.r1]\nquestion = "Which orders cleared the threshold?"\n\n'
          b'[results.r2]\nquestion = "How many orders?"\n')
    write(project, "investigations/inv/queries/r1.sql", b"select n from orders where n >= $threshold order by n\n")
    write(project, "investigations/inv/queries/r2.sql", b"select count(*) as n from orders\n")
    # A producer module is found by its result's ID; run.py gives it run() and the parameters the result reads.
    write(project, "investigations/inv/producers/r1.py", b"def produce(connection, sql, parameters):\n"
          b"    frame = run(connection, sql[0], parameters)\n"
          b"    return frame.assign(read=','.join(sorted(parameters))), {}\n")
    write(project, "investigations/inv/producers/r2.py", b"def produce(connection, sql, parameters):\n"
          b"    return run(connection, sql[0], parameters).assign(cut=parameters.get('unused', 0)), {}\n")
    run = [sys.executable, str(project / "investigations/inv/run.py")]
    done = subprocess.run(run + ["r1", "r2"], capture_output=True, text=True)
    first, second = map(json.loads, done.stdout.splitlines())
    assert done.returncode == 1 and first["state"] == "added", done.stderr
    assert (project / "investigations/inv/results/r1.csv").read_text() == "n,read\n1,threshold\n2,threshold\n"
    evidence = json.loads((project / "investigations/inv/evidence/r1.json").read_text())
    assert "investigations/inv/producers/r1.py" in evidence["producing_paths"]
    assert evidence["settings"]["content"]["parameters"] == {"threshold": 1}
    # Reading a parameter the result does not declare fails loudly, even through get().
    assert second["result_id"] == "r2" and second["error"].startswith("KeyError: \"'unused' is not among")
    assert not (project / "investigations/inv/evidence/r2.json").exists()
    settings = project / "investigations/inv/settings.toml"
    settings.write_text(settings.read_text() + 'parameters = ["unused"]\n')
    done = subprocess.run(run + ["r2"], capture_output=True, text=True)
    assert done.returncode == 0, done.stdout + done.stderr
    assert (project / "investigations/inv/results/r2.csv").read_text() == "n,cut\n3,9\n"
    assert json.loads((project / "investigations/inv/evidence/r2.json").read_text())[
        "settings"]["content"]["parameters"] == {"unused": 9}
    # A module that defines no produce() is an error naming the file.
    write(project, "investigations/inv/producers/r2.py", b"value = 1\n")
    done = subprocess.run(run + ["r2"], capture_output=True, text=True)
    assert done.returncode == 1 and "producers/r2.py defines no produce(connection, sql, parameters)" in done.stdout
    # A result ID that cannot name its producer module is refused before anything runs.
    settings.write_text(settings.read_text() + '\n[results."../escape"]\nquestion = "Which?"\n')
    before = (project / "investigations/inv/results/r1.csv").read_bytes()
    done = subprocess.run(run, capture_output=True, text=True)
    assert (done.returncode, done.stdout) == (2, "")
    assert "settings.toml: [results.../escape] ID must start with a letter or digit" in done.stderr
    assert (project / "investigations/inv/results/r1.csv").read_bytes() == before


def test_run_template_registers_each_producer_module(project):
    pytest.importorskip("duckdb")
    pytest.importorskip("pandas")
    install_run_template(project)
    # dataclasses resolves a postponed annotation through sys.modules, as pickle finds a class.
    write(project, "investigations/inv/producers/r1.py", b"from __future__ import annotations\n\n"
          b"from dataclasses import dataclass\n\n\n@dataclass\nclass Cut:\n    low: int\n    high: int = 5\n\n\n"
          b"def produce(connection, sql, parameters):\n"
          b"    return run(connection, sql[0], parameters).assign(high=Cut(1).high), {}\n")
    done = subprocess.run([sys.executable, str(project / "investigations/inv/run.py"), "r1"],
                          capture_output=True, text=True)
    assert done.returncode == 0, done.stdout + done.stderr
    assert json.loads(done.stdout)["state"] == "added"
    assert (project / "investigations/inv/results/r1.csv").read_text().splitlines()[0] == "n,high"


def test_run_template_names_each_producer_module_apart(project):
    pytest.importorskip("duckdb")
    pytest.importorskip("pandas")
    install_run_template(project)
    ids = ("a-b", "a_b", "a.b", "a_2d_b")
    write(project, "investigations/inv/settings.toml", "".join(
        f'[results."{result_id}"]\nquestion = "How many orders?"\n\n' for result_id in ids).encode())
    for result_id in ids:
        write(project, f"investigations/inv/queries/{result_id}.sql", b"select count(*) as n from orders\n")
        write(project, f"investigations/inv/producers/{result_id}.py", b"def produce(connection, sql, parameters):\n"
              b"    return run(connection, sql[0], parameters).assign(module=__name__), {}\n")
    done = subprocess.run([sys.executable, str(project / "investigations/inv/run.py")], capture_output=True, text=True)
    assert done.returncode == 0, done.stdout + done.stderr
    names = {(project / f"investigations/inv/results/{result_id}.csv").read_text().splitlines()[1].split(",")[1]
             for result_id in ids}
    assert len(names) == len(ids), names


def test_run_template_checks_declared_code_before_running(project):
    pytest.importorskip("duckdb")
    pytest.importorskip("pandas")
    install_run_template(project)
    write(project, "investigations/inv/helpers.py", b"y = 1\n")
    run = [sys.executable, str(project / "investigations/inv/run.py"), "r1"]
    assert subprocess.run(run, capture_output=True, text=True).returncode == 0
    kept = {path: (project / path).read_bytes() for path in
            ("investigations/inv/evidence/r1.json", "investigations/inv/results/r1.csv")}
    settings = project / "investigations/inv/settings.toml"
    settings.write_bytes(SETTINGS.replace(b"[results.r1]\n", b'[results.r1]\ncode = ["helpres.py"]\n'))
    done = subprocess.run(run, capture_output=True, text=True)
    assert (done.returncode, done.stdout) == (2, "")
    assert "settings.toml: [results.r1] code names helpres.py, which does not exist under investigations/inv/" \
        in done.stderr
    assert {path: (project / path).read_bytes() for path in kept} == kept


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


def test_read_requirements_reports_each_include_of_a_missing_file(project):
    write(project, "requirements.txt", b"-r missing.txt\n-r missing.txt\n-r sub/a.txt\n-r sub/b.txt\n-r sub/b.txt\n")
    write(project, "sub/a.txt", b"-r ../missing.txt\n")
    write(project, "sub/b.txt", b"numpy\n")
    assert provenance.read_requirements(project / "requirements.txt") == (["numpy"], [
        "requirements.txt:1: -r missing.txt (No such file or directory)",
        "requirements.txt:2: -r missing.txt (No such file or directory)",
        "sub/a.txt:1: -r ../missing.txt (No such file or directory)"])


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
