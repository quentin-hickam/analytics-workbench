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


def test_file_checksums_preserves_order_and_reports_missing_files(tmp_path):
    (tmp_path / "abc").write_bytes(b"abc")
    assert provenance.file_checksums(["missing", "abc"], root=tmp_path) == [
        {"path": "missing", "bytes": None, "sha256": None},
        {"path": "abc", "bytes": 3,
         "sha256": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"},
    ]
    with pytest.raises(ValueError):
        provenance.file_checksums([tmp_path])


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
        "acquisitions", "settings", "checks", "figure", "notes",
    ]
    assert raw.endswith("\n") and raw.startswith('{\n  "schema": "awb-evidence/1",')
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
    assert evidence["figure"] is None and evidence["notes"] is None


def test_record_evidence_captures_modified_code(project):
    write(project, "src/ops.py", b"x = 2\n")
    evidence = json.loads(record(project).read_text())
    assert evidence["producing_uncommitted_changes"] == [
        {"path": "src/ops.py", "status": "M", "bytes": 6,
         "sha256": hashlib.sha256(b"x = 2\n").hexdigest()}]


def test_record_evidence_rejects_invalid_checks_and_records_figure(project):
    with pytest.raises(ValueError):
        provenance.record_evidence(project, "inv", "r1", views=[], publications=[], acquisitions=[],
            settings_path=None, checks=[{"name": "scope", "outcome": "ok", "detail": "wrong"}])
    write(project, "investigations/inv/figures/result.png", b"figure bytes")
    evidence = json.loads(record(project, figure="investigations/inv/figures/result.png").read_text())
    assert evidence["figure"] == {"path": "investigations/inv/figures/result.png", "bytes": 12,
                                 "sha256": hashlib.sha256(b"figure bytes").hexdigest()}


def test_record_evidence_names_missing_publication_as_unknown(project):
    (project / "data/parquet/orders/p1/publication.json").unlink()
    publication = json.loads(record(project).read_text())["publications"][0]
    assert set(publication["files"]) == {"unknown"}
    assert "data/parquet/orders/p1/publication.json" in publication["files"]["unknown"]
    assert publication["publication_file"] == {
        "path": "data/parquet/orders/p1/publication.json", "bytes": None, "sha256": None}


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


def test_record_evidence_default_discovery_without_code_has_no_producing_paths(tmp_path):
    path = provenance.record_evidence(tmp_path, "inv", "r1", views=[], publications=[],
        acquisitions=[], settings_path=None, checks=[])
    assert json.loads(path.read_text())["producing_paths"] == []


@pytest.mark.skipif(importlib.util.find_spec("tomllib") is None, reason="parsed settings require tomllib")
def test_compare_evidence_parsed_settings_can_have_unknown_key(project):
    write(project, "investigations/inv/settings.toml", b'unknown = "value"\nthreshold = 5\n')
    path = record(project)
    write(project, "investigations/inv/settings.toml", b'threshold=5\nunknown="value" # comment\n')
    assert provenance.compare_evidence(project, path)[4]["outcome"] == "pass"


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


@pytest.mark.parametrize("investigation,result_id", [("../escape", "r1"), ("inv", "bad/id"), ("", "r1")])
def test_record_evidence_rejects_invalid_identifiers(project, investigation, result_id):
    with pytest.raises(ValueError):
        provenance.record_evidence(project, investigation, result_id, views=[], publications=[],
            acquisitions=[], settings_path=None, checks=[])


def test_record_evidence_without_vcs_uses_recursive_code_and_no_vcs_checksums(tmp_path):
    write(tmp_path, "src/ops.py", b"abc")
    write(tmp_path, "investigations/inv/run.py", b"abc")
    write(tmp_path, "investigations/inv/state.md", b"excluded")
    path = provenance.record_evidence(tmp_path, "inv", "r1", views=[], publications=[],
        acquisitions=[], settings_path=None, checks=[])
    evidence = json.loads(path.read_text())
    assert evidence["producing_commit"] == {"unknown": "not a git repository"}
    assert evidence["producing_paths"] == ["investigations/inv/run.py", "src/ops.py"]
    assert [c["status"] for c in evidence["producing_uncommitted_changes"]] == ["no-vcs"] * 2
    assert [c["sha256"] for c in evidence["producing_uncommitted_changes"]] == [
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"] * 2


@pytest.mark.parametrize("field,index", [("producing_commit", 0), ("producing_uncommitted_changes", 1),
                                        ("views", 2), ("publications", 3), ("settings", 4)])
def test_compare_evidence_needed_unknowns_fail_with_reason(project, field, index):
    path = record(project)
    evidence = json.loads(path.read_text())
    evidence[field] = {"unknown": "fixture reason"}
    path.write_text(json.dumps(evidence))
    comparisons = provenance.compare_evidence(project, path)
    assert [c["name"] for c in comparisons] == NAMES
    assert comparisons[index]["outcome"] == "fail"
    assert comparisons[index]["detail"].startswith("missing evidence:")
    assert "fixture reason" in comparisons[index]["detail"]


def test_compare_evidence_views_need_publication_identity_only(project):
    (project / "data/parquet/orders/p1/publication.json").unlink()
    comparisons = provenance.compare_evidence(project, record(project))
    assert comparisons[2]["outcome"] == "pass"
    assert comparisons[3]["outcome"] == "fail"


@pytest.mark.parametrize("target", ["view", "input", "settings"])
def test_compare_evidence_missing_recorded_digest_is_missing_evidence(project, target):
    path = record(project)
    evidence = json.loads(path.read_text())
    if target == "view":
        evidence["views"][0]["sha256"] = None
        index = 2
    elif target == "input":
        evidence["publications"][0]["files"][0]["sha256"] = None
        index = 3
    else:
        evidence["settings"]["sha256"] = None
        evidence["settings"]["content"] = {"unknown": "parse failed"}
        index = 4
    path.write_text(json.dumps(evidence))
    check = provenance.compare_evidence(project, path)[index]
    assert check["outcome"] == "fail" and check["detail"].startswith("missing evidence:")


def test_compare_evidence_committed_paths_do_not_need_dirty_checksums(project):
    write(project, "src/ops.py", b"x = 2\n")
    path = record(project)
    evidence = json.loads(path.read_text())
    evidence["producing_uncommitted_changes"][0]["sha256"] = {"unknown": "lost checksum"}
    path.write_text(json.dumps(evidence))
    comparisons = provenance.compare_evidence(project, path)
    assert comparisons[0]["outcome"] == "pass"
    assert comparisons[1]["outcome"] == "fail"


def test_compare_evidence_reports_every_view_mismatch(project):
    write(project, "foundation/views/second.sql", b"select 2;\n")
    path = provenance.record_evidence(project, "inv", "r1",
        views=["foundation/views/orders.sql", "foundation/views/second.sql"],
        publications=["data/parquet/orders/p1"], acquisitions=[], settings_path=None, checks=[])
    (project / "foundation/views/orders.sql").unlink()
    write(project, "foundation/views/second.sql", b"select 3;\n")
    detail = provenance.compare_evidence(project, path)[2]["detail"]
    assert "foundation/views/orders.sql" in detail and "foundation/views/second.sql" in detail


def test_compare_evidence_empty_comparisons_pass_without_unneeded_values(tmp_path):
    path = provenance.record_evidence(tmp_path, "inv", "r1", views=[], publications=[],
        acquisitions=[], settings_path=None, checks=[], code_paths=[])
    evidence = json.loads(path.read_text())
    evidence["publications"] = {"unknown": "unneeded by empty views"}
    path.write_text(json.dumps(evidence))
    comparisons = provenance.compare_evidence(tmp_path, path)
    assert [c["outcome"] for c in comparisons[:3]] == ["pass"] * 3
    assert all("nothing to compare" in c["detail"] for c in comparisons[:3])


@pytest.mark.skipif(importlib.util.find_spec("tomllib") is None, reason="parsed settings require tomllib")
def test_record_evidence_serializes_toml_dates_consistently(project):
    write(project, "investigations/inv/settings.toml", b"as_of = 2026-10-07\n")
    path = record(project)
    assert json.loads(path.read_text())["settings"]["content"] == {"as_of": "2026-10-07"}
    assert provenance.compare_evidence(project, path)[4]["outcome"] == "pass"


@pytest.mark.parametrize("bad_content", [b"{", b' {"schema": "other"}', b' {"schema": "awb-evidence/1", "settings": []}'])
def test_compare_evidence_bad_files_still_return_five_failures(project, bad_content):
    path = project / "bad.json"
    path.write_bytes(bad_content)
    comparisons = provenance.compare_evidence(project, path)
    assert [c["name"] for c in comparisons] == NAMES
    assert [c["outcome"] for c in comparisons] == ["fail"] * 5
    assert all(c["detail"].startswith("missing evidence:") for c in comparisons)


@pytest.mark.parametrize("kind,index", [("views", 2), ("inputs", 3), ("dirty", 1)])
def test_compare_evidence_reports_unknown_and_later_mismatch(project, kind, index):
    write(project, "src/second.py", b"second code\n")
    write(project, "src/ops.py", b"x = 2\n")
    write(project, "foundation/views/second.sql", b"select 2;\n")
    write(project, "data/parquet/orders/p1/second.parquet", b"second data")
    publication_path = project / "data/parquet/orders/p1/publication.json"
    publication = json.loads(publication_path.read_text())
    publication["files"].append({"path": "second.parquet", "bytes": 11,
        "sha256": hashlib.sha256(b"second data").hexdigest()})
    publication_path.write_text(json.dumps(publication))
    path = provenance.record_evidence(project, "inv", "r1",
        views=["foundation/views/orders.sql", "foundation/views/second.sql"],
        publications=["data/parquet/orders/p1"], acquisitions=[], settings_path=None, checks=[])
    evidence = json.loads(path.read_text())
    if kind == "views":
        evidence["views"][0]["sha256"] = {"unknown": "lost checksum"}
        write(project, "foundation/views/second.sql", b"select 3;\n")
        later = "foundation/views/second.sql"
    elif kind == "inputs":
        evidence["publications"][0]["files"][0]["sha256"] = {"unknown": "lost checksum"}
        write(project, "data/parquet/orders/p1/second.parquet", b"changed data")
        later = "data/parquet/orders/p1/second.parquet"
    else:
        evidence["producing_uncommitted_changes"][0]["sha256"] = {"unknown": "lost checksum"}
        write(project, "src/second.py", b"changed code\n")
        later = "src/second.py"
    path.write_text(json.dumps(evidence))
    check = provenance.compare_evidence(project, path)[index]
    assert check["outcome"] == "fail" and check["detail"].startswith("missing evidence:")
    assert "lost checksum" in check["detail"] and later in check["detail"]


def test_record_evidence_git_subdirectory_expands_code_and_strips_status_prefix(project):
    root = project / "nested"
    write(root, ".gitignore", b"src/ignored.py\n")
    write(root, "src/ops.py", b"abc")
    write(root, "src/ignored.py", b"ignored")
    write(root, "investigations/inv/run.py", b"abc")
    write(root, "investigations/inv/brief.md", b"excluded")
    git(project, "add", "nested")
    git(project, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c",
        "commit.gpgsign=false", "commit", "-m", "nested fixture")
    git(root, "mv", "src/ops.py", "src/renamed.py")
    write(root, "src/new.py", b"abc")
    path = provenance.record_evidence(root, "inv", "r1", views=[], publications=[],
        acquisitions=[], settings_path=None, checks=[])
    evidence = json.loads(path.read_text())
    assert evidence["producing_paths"] == ["investigations/inv/run.py", "src/new.py", "src/renamed.py"]
    path = provenance.record_evidence(root, "inv", "r1", views=[], publications=[],
        acquisitions=[], settings_path=None, checks=[],
        code_paths=["src/ops.py", "src/renamed.py", "src/new.py"])
    evidence = json.loads(path.read_text())
    assert evidence["producing_uncommitted_changes"] == [
        {"path": "src/renamed.py", "status": "R", "bytes": 3,
         "sha256": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"},
        {"path": "src/new.py", "status": "??", "bytes": 3,
         "sha256": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"},
    ]
    assert "src/renamed.py" not in provenance.compare_evidence(root, path)[0]["paths"]


def test_record_evidence_explicit_code_and_ignored_paths_have_current_checksums(project):
    write(project, ".gitignore", b"src/ignored.py\n")
    write(project, "src/ignored.py", b"abc")
    path = record(project, code_paths=["src/ignored.py", "src/ignored.py"])
    evidence = json.loads(path.read_text())
    assert evidence["producing_paths"] == ["foundation/views/orders.sql",
        "investigations/inv/settings.toml", "src/ignored.py"]
    assert evidence["producing_uncommitted_changes"] == [{"path": "src/ignored.py", "status": "!!",
        "bytes": 3, "sha256": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"}]


def test_file_checksums_absolute_paths_relativize_and_outside_paths_are_rejected(project):
    assert provenance.file_checksums([project / "src/ops.py"], root=project) == [{
        "path": "src/ops.py", "bytes": 6, "sha256": hashlib.sha256(b"x = 1\n").hexdigest()}]
    with pytest.raises(ValueError):
        provenance.file_checksums([project.parent / "outside"], root=project)
    with pytest.raises(ValueError):
        record(project, code_paths=[project.parent / "outside"])


@pytest.mark.parametrize("metadata", ["data/parquet/orders/p1/publication.json", "data/raw/crm/a1/provenance.json"])
def test_record_evidence_malformed_metadata_has_named_unknowns_and_null_checksums(project, metadata):
    write(project, metadata, b"{")
    evidence = json.loads(record(project).read_text())
    entry = evidence["publications" if metadata.endswith("publication.json") else "acquisitions"][0]
    assert metadata in entry["files"]["unknown"]
    assert entry["publication_file" if metadata.endswith("publication.json") else "provenance_file"] == {
        "path": metadata, "bytes": None, "sha256": None}


def test_record_evidence_overwrites_same_id_without_hashing_data_at_record_time(project):
    (project / "data/parquet/orders/p1/part-0.parquet").unlink()
    path = record(project, notes="first")
    assert record(project, notes="second") == path
    evidence = json.loads(path.read_text())
    assert evidence["notes"] == "second"
    assert evidence["publications"][0]["files"][0]["sha256"] == hashlib.sha256(b"parquet bytes").hexdigest()
    assert list(path.parent.iterdir()) == [path]


def test_compare_evidence_both_absent_dirty_files_are_equal(project):
    (project / "src/ops.py").unlink()
    comparisons = provenance.compare_evidence(project, record(project))
    assert comparisons[0]["outcome"] == comparisons[1]["outcome"] == "pass"


def test_compare_evidence_unlisted_publication_reference_fails_views(project):
    path = provenance.record_evidence(project, "inv", "r1", views=["foundation/views/orders.sql"],
        publications=[], acquisitions=[], settings_path=None, checks=[])
    check = provenance.compare_evidence(project, path)[2]
    assert check["outcome"] == "fail" and "data/parquet/orders/p1" in check["detail"]


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


def test_compare_evidence_unknown_view_references_name_missing_evidence(project):
    path = record(project)
    evidence = json.loads(path.read_text())
    evidence["views"][0]["publications"] = {"unknown": "lost references"}
    path.write_text(json.dumps(evidence))
    check = provenance.compare_evidence(project, path)[2]
    assert check["outcome"] == "fail" and check["detail"].startswith("missing evidence:")
    assert "foundation/views/orders.sql" in check["detail"] and "lost references" in check["detail"]


def test_record_evidence_missing_view_records_unknown_references(project):
    (project / "foundation/views/orders.sql").unlink()
    path = record(project)
    view = json.loads(path.read_text())["views"][0]
    assert view["sha256"] is None and view["bytes"] is None
    assert "foundation/views/orders.sql" in view["publications"]["unknown"]
    assert provenance.compare_evidence(project, path)[2]["outcome"] == "fail"


def test_compare_evidence_unknown_metadata_does_not_hide_later_input_mismatch(project):
    path = record(project)
    evidence = json.loads(path.read_text())
    evidence["publications"][0]["publication_file"] = {"unknown": "lost metadata"}
    path.write_text(json.dumps(evidence))
    write(project, "data/raw/crm/a1/page-1.json", b"[1]\n")
    check = provenance.compare_evidence(project, path)[3]
    assert check["outcome"] == "fail" and check["detail"].startswith("missing evidence:")
    assert "lost metadata" in check["detail"] and "data/raw/crm/a1/page-1.json" in check["detail"]


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
