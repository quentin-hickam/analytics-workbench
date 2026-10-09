# Kept cases:
# test_names_cover_project_records: names hold investigation/package, created views, sources without CTEs or table functions, top-level settings keys and dotted paths (not bare nested keys), and result IDs from evidence and state links.
# test_check_draft_rewrites_inventory_and_passes: a clean draft passes; the inventory is rewritten and other manifest fields kept; the audit record holds the names set.
# test_check_draft_reports_each_helper_problem: an internal name, a chart without a file, and a missing settings file each fail with the helper's rows unchanged.
# test_verify_only_never_rewrites_inventory: a changed file is reported against the recorded inventory, which stays as recorded.
# test_non_json_manifest_runs_other_checks: findings and chart checks still run; verify is not run and the check fails.
# test_draft_provenance_fills_producing_state: shared commit, inputs, settings, and packaging state are written; export checks pass and other fields stay.
# test_draft_provenance_keeps_differences_and_unknowns: differing commits are listed per result and an unknown keeps its reason.
# test_draft_provenance_blocks_failed_or_missing_evidence: a changed setting blocks exports and a missing evidence file fails; neither writes the manifest.
# test_release_refuses_failed_check_or_pending_disposition: a failing verify or a none/revalidate disposition creates no release.
# test_release_numbers_stamps_and_copies_to_storage: the next number after a gap, stamped copy, untouched draft, storage copy compared.
# test_export_writes_charts_datasets_and_manifest: display names, mapped codes, and rounding shape a saved result into a chart and a dataset; the manifest records charts, selection, and passing export checks.
# test_export_names_every_gap_and_blocks_stale_results: every missing display name is listed at once; a changed setting blocks the export and writes nothing; --no-datasets records none.
# test_release_storage_conflict_and_instructions: an existing destination is never overwritten; none chosen, unrecorded, and URL locations report what to do.

import hashlib
import importlib.util
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

import pytest

if shutil.which("git") is None:
    pytest.skip("git is required", allow_module_level=True)

SKILLS = Path(__file__).resolve().parents[1] / ".agents/skills"
ASSETS = {
    "src/awb.py": SKILLS / "awb-init/assets/awb_cli.py",
    "src/provenance.py": SKILLS / "awb-init/assets/awb_provenance.py",
    "src/packaging/findings.py": SKILLS / "awb-package/assets/awb_findings.py",
    "src/packaging/manifest.py": SKILLS / "awb-package/assets/awb_manifest.py",
    "src/packaging/charts.py": SKILLS / "awb-package/assets/awb_charts.py",
    "src/packaging/draft.py": SKILLS / "awb-package/assets/awb_draft.py",
}
VIEW = b"""-- orders_comment_name stays out
CREATE OR REPLACE VIEW orders_view AS
WITH recent AS (SELECT * FROM read_parquet('data/parquet/orders/p1/*.parquet'))
SELECT r.*, EXTRACT(year FROM r.ordered_at) AS y FROM recent r JOIN main.regions_table g USING (region);
"""
SETTINGS = b'minimum_count = 5\n\n[period]\nstart = 2026-01-01\n'
FINDINGS = "# Order quality\n\n### Late orders rose in the west\n\n**Chart 1.** Bar: late share by region\n"


def git(root, *args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", *args],
                          cwd=root, check=True, capture_output=True, text=True).stdout.strip()


def write(root, path, content):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content if isinstance(content, bytes) else content.encode())


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def project(tmp_path):
    for target, source in ASSETS.items():
        write(tmp_path, target, source.read_bytes())
    write(tmp_path, ".gitignore", "deliveries/\n")
    write(tmp_path, "README.md", "Active investigation: inv\n\nReleased packages are kept at: not yet recorded\n")
    write(tmp_path, "foundation/views/01_orders.sql", VIEW)
    write(tmp_path, "investigations/inv/settings.toml", SETTINGS)
    write(tmp_path, "investigations/inv/run.py", "x = 1\n")
    write(tmp_path, "investigations/inv/state.md", "| r-009 | [r-009](evidence/r-009.json) |\n")
    write(tmp_path, "data/parquet/orders/p1/part-0.parquet", b"parquet bytes")
    write(tmp_path, "data/parquet/orders/p1/publication.json", json.dumps({
        "inputs": [], "conversion_commit": "c1",
        "files": [{"path": "part-0.parquet", "bytes": 13,
                   "sha256": hashlib.sha256(b"parquet bytes").hexdigest()}]}))
    git(tmp_path, "init")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-m", "fixture")
    provenance = load(tmp_path / "src/provenance.py", "provenance_fixture")
    for result_id in ("r-001", "r-002"):
        provenance.record_evidence(
            tmp_path, "inv", result_id, views=["foundation/views/01_orders.sql"],
            publications=["data/parquet/orders/p1"], acquisitions=[],
            settings_path="investigations/inv/settings.toml",
            checks=[{"name": "rows", "outcome": "pass", "detail": "3 rows"}])
    write(tmp_path, "investigations/inv/evidence/r-001-export-checks.json", "[]\n")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-m", "evidence")
    draft = tmp_path / "deliveries/inv/pkg/draft"
    write(draft, "findings.md", FINDINGS)
    write(draft, "methodology.md", "# Method\n")
    write(draft, "charts/chart-1.csv", "Region,Late (%)\nWest,21\n")
    write(draft, "manifest.json", json.dumps({
        "investigation": "inv", "package": "pkg", "status": "draft", "release_number": "",
        "released_at": "", "prior_release": "none", "scope": "west region, 2026",
        "revalidation_flags": "none", "inventory": []}))
    return tmp_path


def run(project, capsys, *argv):
    cli = load(project / "src/awb.py", "awb_cli_fixture")
    code = cli.main(list(argv))
    return code, json.loads(capsys.readouterr().out)


def manifest(project, where="draft"):
    return json.loads((project / "deliveries/inv/pkg" / where / "manifest.json").read_text())


def test_names_cover_project_records(project):
    draft = load(project / "src/packaging/draft.py", "draft_fixture")
    names, problems = draft.project_names(project, "inv", "pkg")
    assert problems == []
    assert {"inv", "pkg", "orders_view", "regions_table", "main.regions_table", "minimum_count",
            "period", "period.start", "r-001", "r-002", "r-009"} <= set(names)
    assert not {"start", "recent", "read_parquet", "ordered_at", "orders_comment_name",
                "r-001-export-checks"} & set(names)


def test_check_draft_rewrites_inventory_and_passes(project, capsys):
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0 and report["passed"]
    assert (report["findings"], report["charts"], report["verify"], report["errors"]) == ([], [], [], [])
    assert report["inventory"] == {"rows": 4, "source": "rewritten"}
    record = manifest(project)
    assert [row["path"] for row in record["inventory"]] == [
        "charts/chart-1.csv", "findings.md", "manifest.json", "methodology.md"]
    assert record["scope"] == "west region, 2026"
    audit = json.loads((project / report["record"]).read_text())
    assert "orders_view" in audit["names_set"] and len(audit["names_set"]) == report["names"]


def test_check_draft_reports_each_helper_problem(project, capsys):
    draft = project / "deliveries/inv/pkg/draft"
    write(draft, "findings.md", FINDINGS + "\nCounts come from orders_view.\n\n**Chart 2.** Line: cases\n")
    (project / "investigations/inv/settings.toml").unlink()
    for path in (project / "investigations/inv/evidence").glob("r-00?.json"):
        path.unlink()
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and not report["passed"]
    assert report["findings"] == [{"line": 7, "kind": "name", "text": "orders_view"}]
    assert report["charts"] == [{"chart": "Chart 2", "problem": "no chart file for this specification"}]
    assert report["names_problems"] == [
        "no settings found: investigations/inv/settings.toml is absent and no evidence records a settings file"]
    assert report["verify"] == []


def test_verify_only_never_rewrites_inventory(project, capsys):
    run(project, capsys, "check-draft", "inv", "pkg")
    recorded = manifest(project)["inventory"]
    write(project / "deliveries/inv/pkg/draft", "methodology.md", "# Method, revised\n")
    code, report = run(project, capsys, "check-draft", "inv", "pkg", "--verify-only")
    assert code == 1 and report["inventory"]["source"] == "recorded"
    assert [(d["path"], d["kind"]) for d in report["verify"]] == [
        ("methodology.md", "size"), ("methodology.md", "checksum")]
    assert manifest(project)["inventory"] == recorded


def test_non_json_manifest_runs_other_checks(project, capsys):
    draft = project / "deliveries/inv/pkg/draft"
    (draft / "manifest.json").rename(draft / "manifest.yaml")
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and report["manifest"] == "manifest.yaml"
    assert report["findings"] == [] and report["charts"] == [] and report["verify"] is None
    assert "only JSON manifests are automated" in report["errors"][0]


def test_draft_provenance_fills_producing_state(project, capsys):
    head = git(project, "rev-parse", "HEAD")
    producing = json.loads((project / "investigations/inv/evidence/r-001.json").read_text())["producing_commit"]
    code, report = run(project, capsys, "draft-provenance", "inv", "pkg", "r-001", "r-002", "--export-checks")
    assert code == 0 and report["written"] and report["export_checks"]["failed"] == []
    record = manifest(project)
    assert record["producing_commit"] == producing != head
    assert record["producing_uncommitted_changes"] == "none"
    assert [v["results"] for v in record["inputs"]["views"]] == [["r-001", "r-002"]]
    assert record["inputs"]["publications"][0]["path"] == "data/parquet/orders/p1"
    assert record["analytical_settings"]["content"] == {"minimum_count": 5, "period": {"start": "2026-01-01"}}
    assert (record["packaging_commit"], record["packaging_uncommitted_changes"]) == (head, "none")
    assert [e["result_id"] for e in record["export_checks"]] == ["r-001", "r-002"]
    assert all(len(e["comparisons"]) == 5 for e in record["export_checks"])
    assert record["scope"] == "west region, 2026" and record["inventory"] == []


def test_draft_provenance_keeps_differences_and_unknowns(project, capsys):
    evidence = project / "investigations/inv/evidence"
    second = json.loads((evidence / "r-002.json").read_text())
    second.update(producing_commit={"unknown": "not a git repository"},
                  producing_uncommitted_changes=[{"path": "src/x.py", "status": "no-vcs", "bytes": None, "sha256": None}])
    (evidence / "r-002.json").write_text(json.dumps(second))
    code, report = run(project, capsys, "draft-provenance", "inv", "pkg", "r-001", "r-002")
    assert code == 0 and report["producing_commit"] == "differs by result"
    record = manifest(project)
    first = json.loads((evidence / "r-001.json").read_text())["producing_commit"]
    assert record["producing_commit"] == [
        {"results": ["r-001"], "value": first},
        {"results": ["r-002"], "value": {"unknown": "not a git repository"}}]
    assert record["producing_uncommitted_changes"] == [
        {"path": "src/x.py", "status": "no-vcs", "bytes": None, "sha256": None, "results": ["r-002"]}]
    assert "export_checks" not in record


def test_draft_provenance_blocks_failed_or_missing_evidence(project, capsys):
    before = (project / "deliveries/inv/pkg/draft/manifest.json").read_text()
    write(project, "investigations/inv/settings.toml", SETTINGS + b"extra = 1\n")
    code, report = run(project, capsys, "draft-provenance", "inv", "pkg", "r-001", "--export-checks")
    assert code == 1 and not report["written"] and "exports_blocked" in report
    assert {(f["result_id"], f["name"]) for f in report["export_checks"]["failed"]} >= {("r-001", "settings")}
    code, report = run(project, capsys, "draft-provenance", "inv", "pkg", "r-404")
    assert code == 1 and report["errors"][0].startswith("missing evidence: investigations/inv/evidence/r-404.json")
    assert (project / "deliveries/inv/pkg/draft/manifest.json").read_text() == before


def test_release_refuses_failed_check_or_pending_disposition(project, capsys):
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 1 and report["refused"] == "check-draft --verify-only does not pass"
    run(project, capsys, "check-draft", "inv", "pkg")
    path = project / "deliveries/inv/pkg/draft/manifest.json"
    record = json.loads(path.read_text())
    record["revalidation_flags"] = [{"finding": "F1", "reason": "late fix", "represented_in": [
        {"place": "findings: Late orders", "disposition": "release_with_caveat"},
        {"place": "chart 1", "disposition": "none"},
        {"place": "methodology", "disposition": "revalidate"}]}]
    path.write_text(json.dumps(record))
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 1 and report["dispositions"] == [
        {"finding": "F1", "place": {"place": "chart 1"}, "problem": "no disposition"},
        {"finding": "F1", "place": {"place": "methodology"}, "problem": "revalidation pending"}]
    assert not (project / "deliveries/inv/pkg/released").exists()


def test_release_numbers_stamps_and_copies_to_storage(project, capsys, tmp_path_factory):
    store = tmp_path_factory.mktemp("store")
    readme = project / "README.md"
    readme.write_text(readme.read_text().replace("not yet recorded", f"`{store}`"))
    run(project, capsys, "check-draft", "inv", "pkg")
    for number in ("001", "003"):
        (project / f"deliveries/inv/pkg/released/{number}").mkdir(parents=True)
    (project / "deliveries/inv/pkg/released/notes").mkdir()
    draft_before = manifest(project)
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 0 and report["released"] and report["release_number"] == "004"
    record = manifest(project, "released/004")
    assert (record["status"], record["release_number"], record["prior_release"]) == ("release", "004", "released/003")
    assert record["released_at"] == report["released_at"]
    assert datetime.fromisoformat(record["released_at"]).utcoffset() is not None
    assert record["inventory"] == draft_before["inventory"] and manifest(project) == draft_before
    assert report["storage"] == {"status": "copied", "copy": str(store / "inv/pkg/released/004"),
                                 "compare_trees": []}
    assert (store / "inv/pkg/released/004/findings.md").read_text() == FINDINGS


def test_release_storage_conflict_and_instructions(project, capsys, tmp_path_factory):
    store = tmp_path_factory.mktemp("store")
    (store / "inv/pkg/released/001").mkdir(parents=True)
    readme = project / "README.md"
    original = readme.read_text()
    run(project, capsys, "check-draft", "inv", "pkg")
    readme.write_text(original.replace("not yet recorded", str(store)))
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 1 and report["released"] and report["storage"]["status"] == "conflict"
    assert list((store / "inv/pkg/released/001").iterdir()) == []

    cases = {"none chosen": "none chosen", "not yet recorded": "unrecorded",
             "https://example.invalid/sites/team": "unreachable"}
    for number, (location, status) in enumerate(cases.items(), start=2):
        readme.write_text(original.replace("not yet recorded", location))
        code, report = run(project, capsys, "release", "inv", "pkg")
        assert code == 0 and report["release_number"] == f"{number:03d}"
        assert report["storage"]["status"] == status
        if status == "none chosen":
            assert "only copy" in report["storage"]["warning"]
        if status == "unrecorded":
            assert report["storage"]["instruction"] == (
                "record where released packages are kept, then copy deliveries/inv/pkg/released/003/ "
                "there as <location>/inv/pkg/released/003/")
    assert report["storage"]["instruction"] == (
        "copy deliveries/inv/pkg/released/004/ to https://example.invalid/sites/team/inv/pkg/released/004/")


DISPLAY = """[columns]
region = "Region"
late_rate = "Closed late (%)"
n = "Cases"

[values.region]
W = "West"
E = "East"

[round]
late_rate = 1
"""


def with_results(project):
    write(project, "investigations/inv/results/r-001.csv", "region,late_rate,n\nW,21.349,10\nE,2.675,8\n")
    write(project, "foundation/display.toml", DISPLAY)


def test_export_writes_charts_datasets_and_manifest(project, capsys):
    pytest.importorskip("pandas")
    with_results(project)
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001:region,late_rate",
                    "--dataset", "late-closures=r-001")
    assert code == 0 and out["written"] and out["export_checks"]["failed"] == []
    draft = project / "deliveries/inv/pkg/draft"
    assert (draft / "charts/chart-1.csv").read_text() == "Region,Closed late (%)\nWest,21.3\nEast,2.7\n"
    assert (draft / "datasets/late-closures.csv").read_text() == \
        "Region,Closed late (%),Cases\nWest,21.3,10\nEast,2.7,8\n"
    record = manifest(project)
    assert record["charts"] == [{"path": "charts/chart-1.csv", "result_id": "r-001"}]
    assert record["dataset_selection"] == ["datasets/late-closures.csv"]
    assert [c["result_id"] for c in record["export_checks"]] == ["r-001"]
    assert record["scope"] == "west region, 2026"
    assert "chart-1: Closed late (%) <- r-001.late_rate" in out["methodology_lines"]
    assert out["check_charts"] == []


def test_export_names_every_gap_and_blocks_stale_results(project, capsys):
    pytest.importorskip("pandas")
    with_results(project)
    write(project, "foundation/display.toml", DISPLAY.replace('n = "Cases"\n', ""))
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001", "--chart", "r-002")
    assert code == 1 and not out["written"]
    assert out["errors"] == [
        "r-001: column 'n' has no display name in foundation/display.toml [columns]",
        "investigations/inv/results/r-002.csv is missing; run the investigation's run.py"]
    with_results(project)
    before = (project / "deliveries/inv/pkg/draft/charts/chart-1.csv").read_bytes()
    write(project, "investigations/inv/settings.toml", SETTINGS + b"minimum_count_2 = 6\n")
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001")
    assert code == 1 and out["exports_blocked"] and out["export_checks"]["failed"]
    assert (project / "deliveries/inv/pkg/draft/charts/chart-1.csv").read_bytes() == before
    write(project, "investigations/inv/settings.toml", SETTINGS)
    write(project, "deliveries/inv/pkg/draft/datasets/old.csv", "a\n1\n")
    code, out = run(project, capsys, "export", "inv", "pkg", "--no-datasets")
    assert code == 0 and manifest(project)["dataset_selection"] == "none"
    assert not (project / "deliveries/inv/pkg/draft/datasets").exists()
