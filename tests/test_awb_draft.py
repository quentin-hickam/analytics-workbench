# Kept cases:
# test_names_cover_project_records: names hold created views, sources without CTEs or table functions, settings dotted paths (not bare nested keys), and result IDs from evidence and state links; plain words, including plain investigation and package names, are left out.
# test_toml_keys_fall_back_to_tomli_then_key_lines: without tomllib, settings keys parse with tomli (no bare nested keys); without either, table headers and key lines; display.toml then names the missing package.
# test_check_draft_rewrites_inventory_and_passes: a clean draft passes; the inventory is rewritten, revised_at stamped only when it changes, other manifest fields kept; nothing is written outside the draft.
# test_check_draft_reports_each_helper_problem: an internal name, a chart without a file, a finding heading methodology lacks, and a missing settings file each fail with the helper's rows unchanged.
# test_check_draft_reports_unmatched_flags: in both modes, a finding state.md flags fails until the manifest records its exact finding and reason; a changed reason reopens it; no findings table is an error.
# test_verify_only_never_writes: a changed file is reported against the recorded inventory; the manifest stays byte-identical.
# test_missing_manifest_runs_other_checks: without manifest.json the findings and chart checks still run; verify is not run and the check fails.
# test_export_results_records_provenance_only: --result alone writes shared commit, inputs, settings, and packaging state, creates the manifest with its identity fields, leaves chart files untouched, and is not gated by a changed setting.
# test_export_keeps_differences_and_unknowns: differing commits are listed per result and an unknown keeps its reason.
# test_export_refuses_missing_evidence_or_unnamed_chart_result: a missing evidence file, or a --result call that leaves out a charted result, writes nothing.
# test_export_writes_charts_datasets_and_manifest: display names, mapped codes, and rounding shape a saved result into a chart and a dataset; the manifest records charts, selection, passing export checks for serialized results only, and producing state for every represented result.
# test_export_checks_follow_the_represented_set: a represented result not serialized keeps its entry; a result outside the represented set drops; an export without --chart removes the chart files and records charts none.
# test_export_names_every_gap_and_blocks_stale_results: every missing display name is listed at once; a changed setting blocks a serializing export with a stop message and writes nothing; --no-datasets records none; --chart without a dataset choice is refused.
# test_release_refuses_failed_check_or_pending_disposition: a failing verify, an unmatched flag, a none/revalidate/missing disposition, or malformed places creates no release; represented_in none needs no disposition.
# test_release_reports_fields_for_the_report: datasets, dispositions marked new against the prior release's manifest (unknown when it is unreadable), provenance gaps, checkout-only acquisitions, and a clean local verify.
# test_release_numbers_stamps_and_copies_to_storage: the next number after a gap, stamped copy, untouched draft, storage copy compared.
# test_release_storage_conflict_and_instructions: an existing destination is never overwritten; none chosen, unrecorded, and URL locations report what to do.
# test_copy_releases_copies_compares_and_never_overwrites: existing releases copy to newly recorded storage; a rerun reports already copied; a differing copy is a conflict; an unknown package fails; no audit directory is written.

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest

if shutil.which("git") is None:
    pytest.skip("git is required", allow_module_level=True)

SKILLS = Path(__file__).resolve().parents[1] / ".agents/skills"
ASSETS = {
    "src/awb.py": SKILLS / "awb-init/assets/awb_cli.py",
    "src/provenance.py": SKILLS / "awb-init/assets/awb_provenance.py",
    "src/packaging/draft.py": SKILLS / "awb-package/assets/awb_draft.py",
}
VIEW = b"""-- orders_comment_name stays out
CREATE OR REPLACE VIEW orders_view AS
WITH recent AS (SELECT * FROM read_parquet('data/parquet/orders/p1/*.parquet'))
SELECT r.*, EXTRACT(year FROM r.ordered_at) AS y FROM recent r JOIN main.regions_table g USING (region);
"""
SETTINGS = b"[parameters]\nminimum_count = 5\nstart = 2026-01-01\n\n[results.r-001]\n\n[results.r-002]\n"
STALE_SETTINGS = SETTINGS.replace(b"minimum_count = 5", b"minimum_count = 6")
FINDINGS = "# Order quality\n\n### Late orders rose in the west\n\n**Chart 1.** Bar: late share by region\n"
METHODOLOGY = "# Methodology\n\n## Findings\n\n### Late orders rose in the west\n"
STATE = """# Current investigation state

## Current findings

| Finding | Evidence | Status | Revalidation reason or caveat |
| --- | --- | --- | --- |
| Late orders rose in the west | [r-009](evidence/r-009.json) | {status} | {reason} |

## Next steps
"""
FLAGGED = STATE.format(status="revalidation-needed (was supported)", reason="Q-3 corrected west dates")
FLAG = {"finding": "Late orders rose in the west", "reason": "Q-3 corrected west dates"}


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
    write(tmp_path, "investigations/inv/state.md", STATE.format(status="supported", reason=""))
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
    write(draft, "methodology.md", METHODOLOGY)
    write(draft, "charts/chart-1.csv", "Region,Late (%)\nWest,21\n")
    write(draft, "manifest.json", json.dumps({
        "investigation": "inv", "package": "pkg", "status": "draft",
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
    assert {"orders_view", "regions_table", "main.regions_table", "parameters.minimum_count",
            "parameters.start", "results.r-001", "r-001", "r-002", "r-009"} <= set(names)
    assert not {"inv", "pkg", "parameters", "results", "start", "minimum_count", "recent", "read_parquet",
                "ordered_at", "orders_comment_name", "r-001-export-checks"} & set(names)
    hyphenated, _ = draft.project_names(project, "inv-2026", "churn-q3")
    assert {"inv-2026", "churn-q3"} <= set(hyphenated)


def test_toml_keys_fall_back_to_tomli_then_key_lines(project, monkeypatch):
    tomllib = pytest.importorskip("tomllib")
    draft = load(project / "src/packaging/draft.py", "draft_toml")
    text = SETTINGS.decode()
    monkeypatch.setitem(sys.modules, "tomllib", None)
    monkeypatch.setitem(sys.modules, "tomli", tomllib)
    assert draft._toml_keys(text) == {"parameters", "parameters.minimum_count", "parameters.start",
                                      "results", "results.r-001", "results.r-002"}
    monkeypatch.setitem(sys.modules, "tomli", None)
    assert {"parameters", "results.r-001", "minimum_count"} <= draft._toml_keys(text)
    write(project, "foundation/display.toml", "[columns]\n")
    with pytest.raises(ImportError, match="tomli"):
        draft.display_names(project)


def test_check_draft_rewrites_inventory_and_passes(project, capsys):
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0 and report["passed"] and "record" not in report
    assert (report["findings"], report["charts"], report["verify"], report["errors"]) == ([], [], [], [])
    assert report["inventory"] == {"rows": 4, "source": "rewritten"}
    record = manifest(project)
    assert [row["path"] for row in record["inventory"]] == [
        "charts/chart-1.csv", "findings.md", "manifest.json", "methodology.md"]
    assert record["revalidation_flags"] == "none"
    assert datetime.fromisoformat(record["revised_at"]).utcoffset() is not None
    path = project / "deliveries/inv/pkg/draft/manifest.json"
    path.write_text(json.dumps({**record, "revised_at": "2026-01-01T00:00:00+00:00"}))
    run(project, capsys, "check-draft", "inv", "pkg")
    assert manifest(project)["revised_at"] == "2026-01-01T00:00:00+00:00"
    write(project / "deliveries/inv/pkg/draft", "methodology.md", METHODOLOGY + "Revised.\n")
    run(project, capsys, "check-draft", "inv", "pkg")
    assert manifest(project)["revised_at"] != "2026-01-01T00:00:00+00:00"
    assert sorted(p.name for p in (project / "deliveries/inv/pkg").iterdir()) == ["draft"]


def test_check_draft_reports_each_helper_problem(project, capsys):
    draft = project / "deliveries/inv/pkg/draft"
    write(draft, "findings.md", FINDINGS + "\nCounts come from orders_view.\n\n**Chart 2.** Line: cases\n"
          "\n### East held steady\n")
    (project / "investigations/inv/settings.toml").unlink()
    for path in (project / "investigations/inv/evidence").glob("r-00?.json"):
        path.unlink()
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and not report["passed"]
    assert report["findings"] == [{"line": 7, "kind": "name", "text": "orders_view"}]
    assert report["charts"] == [{"chart": "Chart 2", "problem": "no chart file for this specification"}]
    assert report["headings"] == [
        {"heading": "East held steady", "problem": "methodology.md has no ### section with this exact heading"}]
    assert report["names_problems"] == [
        "no settings found: investigations/inv/settings.toml is absent and no evidence records a settings file"]
    assert report["verify"] == []


def set_flags(project, flags):
    path = project / "deliveries/inv/pkg/draft/manifest.json"
    record = json.loads(path.read_text())
    record["revalidation_flags"] = flags
    path.write_text(json.dumps(record))


def test_check_draft_reports_unmatched_flags(project, capsys):
    write(project, "investigations/inv/state.md", FLAGGED)
    for argv in ((), ("--verify-only",)):
        code, report = run(project, capsys, "check-draft", "inv", "pkg", *argv)
        assert code == 1 and not report["passed"] and report["unmatched_flags"] == [FLAG]
        assert report["errors"] == [] and report["verify"] == []
    set_flags(project, [{**FLAG, "reason": "an older reason", "represented_in": "none"}])
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and report["unmatched_flags"] == [FLAG]
    set_flags(project, [{**FLAG, "represented_in": ["findings: Late orders"], "disposition": "none"}])
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0 and report["passed"] and report["unmatched_flags"] == []
    write(project, "investigations/inv/state.md", "# Current investigation state\n")
    code, report = run(project, capsys, "check-draft", "inv", "pkg", "--verify-only")
    assert code == 1 and report["unmatched_flags"] is None
    assert "no Current findings table" in report["errors"][0]


def test_verify_only_never_writes(project, capsys):
    run(project, capsys, "check-draft", "inv", "pkg")
    before = (project / "deliveries/inv/pkg/draft/manifest.json").read_bytes()
    write(project / "deliveries/inv/pkg/draft", "methodology.md", METHODOLOGY + "Revised.\n")
    code, report = run(project, capsys, "check-draft", "inv", "pkg", "--verify-only")
    assert code == 1 and report["inventory"]["source"] == "recorded"
    assert [(d["path"], d["kind"]) for d in report["verify"]] == [
        ("methodology.md", "size"), ("methodology.md", "checksum")]
    assert (project / "deliveries/inv/pkg/draft/manifest.json").read_bytes() == before
    assert sorted(p.name for p in (project / "deliveries/inv/pkg").iterdir()) == ["draft"]


def test_missing_manifest_runs_other_checks(project, capsys):
    draft = project / "deliveries/inv/pkg/draft"
    (draft / "manifest.json").rename(draft / "manifest.yaml")
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and "manifest" not in report
    assert report["findings"] == [] and report["charts"] == [] and report["verify"] is None
    assert report["errors"] == ["manifest: no manifest at deliveries/inv/pkg/draft/manifest.json; run export first"]


def test_export_results_records_provenance_only(project, capsys):
    head = git(project, "rev-parse", "HEAD")
    producing = json.loads((project / "investigations/inv/evidence/r-001.json").read_text())["producing_commit"]
    (project / "deliveries/inv/pkg/draft/manifest.json").unlink()
    chart = (project / "deliveries/inv/pkg/draft/charts/chart-1.csv").read_bytes()
    write(project, "investigations/inv/settings.toml", STALE_SETTINGS)
    code, report = run(project, capsys, "export", "inv", "pkg", "--result", "r-001", "--result", "r-002")
    assert code == 0 and report["written"] and report["created"] and report["export_checks"]["results"] == 0
    record = manifest(project)
    assert (record["investigation"], record["package"], record["status"]) == ("inv", "pkg", "draft")
    assert record["producing_commit"] == producing != head
    assert record["producing_uncommitted_changes"] == "none"
    assert [v["results"] for v in record["inputs"]["views"]] == [["r-001", "r-002"]]
    assert record["inputs"]["publications"][0]["path"] == "data/parquet/orders/p1"
    # Scoped settings differ by result table, so each result keeps its own value.
    assert [(s["results"], s["value"]["content"]["parameters"]) for s in record["analytical_settings"]] == [
        (["r-001"], {"minimum_count": 5, "start": "2026-01-01"}),
        (["r-002"], {"minimum_count": 5, "start": "2026-01-01"})]
    assert record["packaging_commit"] == head and record["packaging_uncommitted_changes"] == "none"
    assert record["export_checks"] == "none" and "charts" not in record and "dataset_selection" not in record
    assert (project / "deliveries/inv/pkg/draft/charts/chart-1.csv").read_bytes() == chart


def test_export_keeps_differences_and_unknowns(project, capsys):
    evidence = project / "investigations/inv/evidence"
    second = json.loads((evidence / "r-002.json").read_text())
    second.update(producing_commit={"unknown": "not a git repository"},
                  producing_uncommitted_changes=[{"path": "src/x.py", "status": "no-vcs", "bytes": None, "sha256": None}])
    (evidence / "r-002.json").write_text(json.dumps(second))
    code, report = run(project, capsys, "export", "inv", "pkg", "--result", "r-001", "--result", "r-002")
    assert code == 0 and report["producing_commit"] == "differs by result"
    record = manifest(project)
    first = json.loads((evidence / "r-001.json").read_text())["producing_commit"]
    assert record["producing_commit"] == [
        {"results": ["r-001"], "value": first},
        {"results": ["r-002"], "value": {"unknown": "not a git repository"}}]
    assert record["producing_uncommitted_changes"] == [
        {"path": "src/x.py", "status": "no-vcs", "bytes": None, "sha256": None, "results": ["r-002"]}]


def test_export_refuses_missing_evidence_or_unnamed_chart_result(project, capsys):
    path = project / "deliveries/inv/pkg/draft/manifest.json"
    before = path.read_text()
    code, report = run(project, capsys, "export", "inv", "pkg", "--result", "r-001", "--result", "r-404")
    assert code == 1 and not report["written"]
    assert report["errors"][0].startswith("missing evidence: investigations/inv/evidence/r-404.json")
    assert path.read_text() == before
    path.write_text(json.dumps({**json.loads(before), "charts": [{"path": "charts/chart-1.csv", "result_id": "r-001"}]}))
    before = path.read_text()
    code, report = run(project, capsys, "export", "inv", "pkg", "--result", "r-002")
    assert code == 1 and report["errors"] == [
        "charts/chart-1.csv serializes r-001, which this call does not name; pass it with --result"]
    assert path.read_text() == before


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
    with_results(project)
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001:region,late_rate",
                    "--dataset", "late-closures=r-001", "--result", "r-002")
    assert code == 0 and out["written"] and out["export_checks"] == {"results": 1, "failed": []}
    draft = project / "deliveries/inv/pkg/draft"
    assert (draft / "charts/chart-1.csv").read_text() == "Region,Closed late (%)\nWest,21.3\nEast,2.7\n"
    assert (draft / "datasets/late-closures.csv").read_text() == \
        "Region,Closed late (%),Cases\nWest,21.3,10\nEast,2.7,8\n"
    record = manifest(project)
    assert record["charts"] == [{"path": "charts/chart-1.csv", "result_id": "r-001"}]
    assert record["dataset_selection"] == ["datasets/late-closures.csv"]
    assert [c["result_id"] for c in record["export_checks"]] == ["r-001"]
    assert all(len(c["comparisons"]) == 5 for c in record["export_checks"])
    assert [v["results"] for v in record["inputs"]["views"]] == [["r-001", "r-002"]]
    assert out["results"] == ["r-001", "r-002"] and record["revalidation_flags"] == "none"
    assert "chart-1: Closed late (%) <- r-001.late_rate" in out["methodology_lines"]
    assert out["check_charts"] == []


def test_export_checks_follow_the_represented_set(project, capsys):
    with_results(project)
    run(project, capsys, "export", "inv", "pkg", "--chart", "r-001:region,late_rate", "--no-datasets")
    checks = manifest(project)["export_checks"]
    write(project, "investigations/inv/settings.toml", STALE_SETTINGS)
    code, out = run(project, capsys, "export", "inv", "pkg", "--result", "r-001", "--result", "r-002")
    assert code == 0 and manifest(project)["export_checks"] == checks
    write(project, "investigations/inv/settings.toml", SETTINGS)
    write(project / "deliveries/inv/pkg/draft", "findings.md", FINDINGS.replace("**Chart 1.** Bar: late share by region\n", ""))
    code, out = run(project, capsys, "export", "inv", "pkg", "--no-datasets", "--result", "r-002")
    assert code == 0 and out["charts"] == [] and out["check_charts"] == []
    record = manifest(project)
    assert (record["charts"], record["dataset_selection"], record["export_checks"]) == ("none", "none", "none")
    assert not (project / "deliveries/inv/pkg/draft/charts").exists()


def test_export_names_every_gap_and_blocks_stale_results(project, capsys):
    with_results(project)
    write(project, "foundation/display.toml", DISPLAY.replace('n = "Cases"\n', ""))
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001", "--chart", "r-002", "--no-datasets")
    assert code == 1 and not out["written"]
    assert out["errors"] == [
        "r-001: column 'n' has no display name in foundation/display.toml [columns]",
        "investigations/inv/results/r-002.csv is missing. Stop: saving a result table needs separately "
        "authorized analytical work"]
    with_results(project)
    before = (project / "deliveries/inv/pkg/draft/charts/chart-1.csv").read_bytes()
    write(project, "investigations/inv/settings.toml", STALE_SETTINGS)
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001", "--no-datasets")
    assert code == 1 and out["export_checks"]["failed"]
    assert out["exports_blocked"].endswith("Stop: changed results need separately authorized analytical work")
    assert (project / "deliveries/inv/pkg/draft/charts/chart-1.csv").read_bytes() == before
    write(project, "investigations/inv/settings.toml", SETTINGS)
    write(project, "deliveries/inv/pkg/draft/datasets/old.csv", "a\n1\n")
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001", "--no-datasets")
    assert code == 0 and manifest(project)["dataset_selection"] == "none"
    assert not (project / "deliveries/inv/pkg/draft/datasets").exists()
    with pytest.raises(SystemExit):
        run(project, capsys, "export", "inv", "pkg", "--chart", "r-001")


def test_release_refuses_failed_check_or_pending_disposition(project, capsys):
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 1 and report["refused"] == "check-draft --verify-only does not pass"
    run(project, capsys, "check-draft", "inv", "pkg")
    write(project, "investigations/inv/state.md", FLAGGED)
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 1 and report["refused"] == "flagged findings without a release disposition"
    assert report["unmatched_flags"] == [FLAG]
    unrelated = {"finding": "F2", "reason": "unrelated", "represented_in": "none"}
    places = ["findings: Late orders", "chart 1"]
    for flag, problem in [({"disposition": "none"}, "no disposition"), ({}, "no disposition"),
                          ({"disposition": "revalidate"}, "revalidation pending"),
                          ({"disposition": "later"}, "unknown disposition 'later'"),
                          ({"represented_in": [], "disposition": "omit"},
                           "represented_in is not a list of places; list them or record none"),
                          ({"represented_in": [{"place": "chart 1"}], "disposition": "omit"},
                           "represented_in is not a list of places; list them or record none")]:
        set_flags(project, [{**FLAG, "represented_in": places, **flag}, unrelated])
        code, report = run(project, capsys, "release", "inv", "pkg")
        assert code == 1 and report["unmatched_flags"] == [] and report["dispositions"] == [
            {"finding": FLAG["finding"], "problem": problem}]
    assert not (project / "deliveries/inv/pkg/released").exists()


SOURCES = """# Source register

## Acquisitions

| Acquisition ID | Source ID | Acquired at | Source version, query, or request | Landed directory | Retained copy | Integrity or completeness check | Restrictions | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| a1 | crm | 2026-01-02 | export | data/raw/crm/a1 | this checkout only | rows | none | |
| a2 | crm | 2026-01-03 | export | data/raw/crm/a2 | `/backup/raw` | rows | none | |
"""


def test_release_reports_fields_for_the_report(project, capsys):
    write(project, "investigations/inv/state.md", FLAGGED)
    write(project, "foundation/sources.md", SOURCES)
    path = project / "deliveries/inv/pkg/draft/manifest.json"
    record = json.loads(path.read_text())
    record.update(dataset_selection=["datasets/late.csv"], producing_commit={"unknown": "not a git repository"},
                  inputs={"acquisitions": [{"path": f"data/raw/crm/{a}", "results": ["r-001"]}
                                           for a in ("a1", "a2", "a3")]},
                  revalidation_flags=[{**FLAG, "represented_in": ["chart 1"], "disposition": "release_with_caveat"},
                                      {"finding": "F2", "reason": "unrelated", "represented_in": "none"}])
    path.write_text(json.dumps(record))
    write(project, "deliveries/inv/pkg/draft/datasets/late.csv", "Region\nWest\n")
    run(project, capsys, "check-draft", "inv", "pkg")
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 0 and report["verify"] == [] and report["datasets"] == ["datasets/late.csv"]
    assert report["dispositions"] == [{**FLAG, "represented_in": ["chart 1"],
                                       "disposition": "release_with_caveat", "new": True}]
    assert report["provenance_gaps"] == [{"field": "producing_commit", "reason": "not a git repository"}]
    assert report["checkout_only_acquisitions"] == [
        {"acquisition": "data/raw/crm/a1", "retained_copy": "this checkout only"},
        {"acquisition": "data/raw/crm/a3", "retained_copy": "no Acquisitions row"}]
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 0 and report["release_number"] == "002" and report["dispositions"][0]["new"] is False
    set_flags(project, [{**FLAG, "represented_in": ["chart 1"], "disposition": "omit"}])
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 0 and report["dispositions"][0]["new"] is True
    (project / "deliveries/inv/pkg/released/003/manifest.json").write_text("not json")
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 0 and report["release_number"] == "004" and report["dispositions"][0]["new"] is None


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
    assert record["revised_at"] == draft_before["revised_at"]
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
    assert {row["kind"] for row in report["storage"]["compare_trees"]} == {"missing"}
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


def test_copy_releases_copies_compares_and_never_overwrites(project, capsys, tmp_path_factory):
    run(project, capsys, "check-draft", "inv", "pkg")
    for _ in range(2):
        code, report = run(project, capsys, "release", "inv", "pkg")
        assert code == 0 and report["storage"]["status"] == "unrecorded"
    store = tmp_path_factory.mktemp("store")
    readme = project / "README.md"
    readme.write_text(readme.read_text().replace("not yet recorded", str(store)))
    code, report = run(project, capsys, "copy-releases", "inv")
    assert code == 0 and report["location"] == str(store) and report["errors"] == []
    assert [(r["release"], r["storage"]["status"], r["storage"]["compare_trees"]) for r in report["releases"]] == [
        ("deliveries/inv/pkg/released/001", "copied", []), ("deliveries/inv/pkg/released/002", "copied", [])]
    assert (store / "inv/pkg/released/002/findings.md").read_text() == FINDINGS
    assert not (project / "deliveries/inv/pkg/audit").exists()
    (store / "inv/pkg/released/001/findings.md").write_text("changed\n")
    code, report = run(project, capsys, "copy-releases", "inv", "pkg")
    assert code == 1 and [r["storage"]["status"] for r in report["releases"]] == ["conflict", "already copied"]
    assert (store / "inv/pkg/released/001/findings.md").read_text() == "changed\n"
    code, report = run(project, capsys, "copy-releases", "inv", "other")
    assert code == 1 and report["errors"] == ["no package at deliveries/inv/other"]
