# Kept cases:
# test_check_draft_checks_findings_drift: synchronized JSON passes, drift fails with state render in both modes, an old helper gets an upgrade hint, and rows with no findings.json are drift.
# test_names_cover_project_records: names hold created views, sources without CTEs or table functions, settings dotted paths (not bare nested keys), and result IDs from evidence and state links; plain words, including plain investigation and package names, are left out.
# test_toml_keys_fall_back_to_tomli_then_key_lines: without tomllib, settings keys parse with tomli (no bare nested keys); without either, table headers and key lines; display.toml then names the missing package.
# test_check_draft_rewrites_inventory_and_passes: a clean draft passes; the inventory is rewritten, revised_at stamped only when it changes, other manifest fields kept; nothing is written outside the draft.
# test_evidence_older_than_scoped_3_is_reported_for_rerun: check-draft and export --result refuse awb-evidence/1 and unscoped /3 with a rerun instruction.
# test_check_draft_reports_each_helper_problem: an internal name, a path under the plain investigation name, a chart without a file, a finding heading methodology lacks, and a missing settings file each fail with the helper's rows unchanged.
# test_check_draft_reports_unmatched_flags: in both modes, a finding state.md flags fails until the manifest records its exact finding and reason; a changed reason reopens it; no findings table is an error.
# test_export_replaces_malformed_flag_entries_before_writing: an entry whose reason is not text matches no flag and is replaced by a fresh entry; the export writes files and manifest together.
# test_check_draft_and_release_refuse_malformed_flag_entries: a missing revalidation_flags, a non-list value, an entry without text finding and reason, and [] or blank places fail check-draft's flag_entries, and release refuses on the check.
# test_verify_only_never_writes: a changed file is reported against the recorded inventory; the manifest stays byte-identical.
# test_missing_manifest_runs_other_checks: without manifest.json the findings and chart checks still run; verify is not run and the check fails.
# test_export_results_records_provenance_only: --result alone writes shared commit, inputs, settings, and packaging state, creates the manifest with its identity fields, leaves chart files untouched, and is not gated by a changed setting.
# test_export_creates_revalidation_flags_from_state: from an absent manifest, export records none when state.md flags nothing, else each flag verbatim with represented_in [] and disposition none, listed in flags_pending.
# test_export_syncs_revalidation_flags_with_state: entries follow state.md row order; exact matches are kept whole; a changed reason starts a fresh entry; a cleared flag drops; flags_pending lists [] places and kept entries at none; no flags left records none.
# test_export_keeps_flags_when_state_is_unreadable: export still writes, reports flags_error, and leaves revalidation_flags as it was.
# test_flag_raised_after_none_fails_until_export_records_it: a flag raised after none fails check-draft and release through unmatched_flags; the next export records it as pending.
# test_export_keeps_differences_and_unknowns: differing commits are listed per result and an unknown keeps its reason.
# test_export_refuses_missing_evidence_or_unnamed_chart_result: a missing evidence file, or a --result call that leaves out a charted result, writes nothing.
# test_export_writes_charts_datasets_and_manifest: display names, mapped codes, and rounding shape a saved result into a chart and a dataset; the manifest records charts, selection, passing export checks for serialized results only, and producing state for every represented result.
# test_export_checks_follow_the_represented_set: a represented result not serialized keeps its entry; a result outside the represented set drops; an export without --chart removes the chart files and records charts none.
# test_export_names_every_gap_and_blocks_stale_results: every missing display name is listed at once; a changed setting blocks a serializing export with a stop message and writes nothing; --no-datasets records none; --chart without a dataset choice is refused.
# test_export_display_stub_names_each_gap_once: missing display names on chart and dataset paths give one quoted [columns] line each, deduplicated, a dotted column kept as one key; a blank name gets its own error and no stub line, so the stub pastes as valid TOML.
# test_release_refuses_failed_check_or_pending_disposition: a failing verify, an unmatched flag, or a none/revalidate disposition creates no release; a missing or unknown disposition or malformed places fail the check's flag_entries; represented_in none needs no disposition.
# test_release_reports_fields_for_the_report: datasets, dispositions marked new against the prior release's manifest (unknown when it is unreadable), provenance gaps, checkout-only acquisitions, and a clean local verify.
# test_release_numbers_stamps_and_copies_to_storage: the next number after a gap, stamped copy, untouched draft, storage copy compared.
# test_release_storage_conflict_and_instructions: an existing destination is never overwritten; none chosen, unrecorded, and URL locations report what to do.
# test_check_draft_refuses_causal_wording_above_claim_strength: causal wording on an association finding's slide fails with a row naming the phrase, line, and claim; a causal finding's slide and the Answer slide under a causal represented finding pass; method and caveat slides, code, comments, and hyphenated words are not read; release refuses on the row.
# test_review_probes_read_markdown_as_it_renders: every reviewer probe of the claim check, one row each: headlines, caveat bullets, fences, comments open or closed, declarations hidden, ambiguous, in a code span, or naming another design, emphasis and other inline markup, commented-out, duplicated, and indented headings, and heading forms the slides cannot take.
# test_names_and_charts_read_the_same_rendered_text: the names scan and the chart check skip comments as CommonMark scopes them.
# test_claim_check_reads_headlines_and_cited_designs: a causal ### headline fails check-draft with a row to reword both files; cited causal results of different designs are refused; a whitespace design is unrecognized.
# test_claim_strength_follows_cited_results_and_records: a slide citing several results takes the weakest claim; one citing none takes the weakest represented; with no causal finding the Answer slide fails too; a missing Claim, a missing results list, and a missing or differing methodology Claim strength line each fail.
# test_copy_releases_copies_compares_and_never_overwrites: existing releases copy to newly recorded storage; a rerun reports already copied; a differing copy is a conflict; an unknown package fails; no audit directory is written.

import hashlib
import importlib.util
import json
import re
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
METHODOLOGY = "# Methodology\n\n## Findings\n\n### Late orders rose in the west\n\n**Claim strength:** association\n"
STATE = """# Current investigation state

Last updated: 2026-10-01

## Current findings

| Finding | Evidence | Status | Claim | Revalidation reason or caveat |
| --- | --- | --- | --- | --- |
| Late orders rose in the west | [r-009](evidence/r-009.json) | {status} | association | {reason} |
| West volume is stable | [r-001](evidence/r-001.json) | supported | association | |
| Discounts cut late orders | [r-002](evidence/r-002.json) | supported | causal (experiment: randomized discount test) | |

## Next steps
"""
FLAGGED = STATE.format(status="revalidation-needed (was supported)", reason="Q-3 corrected west dates")
FLAG = {"finding": "Late orders rose in the west", "reason": "Q-3 corrected west dates"}
PLACES_PROBLEM = "represented_in is not none or a list of places; list them or record none"


def git(root, *args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", *args],
                          cwd=root, check=True, capture_output=True, text=True).stdout.strip()


def write(root, path, content):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content if isinstance(content, bytes) else content.encode())
    if path.endswith("/state.md") and isinstance(content, str):
        findings_for(target, content)


def findings_for(state, text):
    """Write the findings.json a state.md's rows render from, as run.py and `state` would have."""
    entries = []
    for line in text.splitlines():
        match = re.fullmatch(r"\| (.*) \| \[(.+)\]\(evidence/\2\.json\) \| (.*) \| (.*) \| ?(.*?) ?\|", line)
        if match:
            finding, result, status, claim, reason = (part.strip() for part in match.groups())
            claim, _, basis = claim.partition(" (")
            flagged = re.fullmatch(r"revalidation-needed(?: \(was (.+)\))?", status)
            entries.append({"result": result, "text": finding, "status": "revalidation-needed" if flagged else status,
                            "prior_status": flagged[1] if flagged else None,
                            "flag_reason": reason if flagged else "", "notes": [] if flagged or not reason else [reason],
                            "checks_caveat": "", "notes_checks": "", "claim": claim, "claim_basis": basis[:-1]})
    path = state.with_name("findings.json")
    if entries:
        path.write_text(json.dumps({"schema": "awb-findings/1", "findings": entries}, indent=2) + "\n")
    else:
        path.unlink(missing_ok=True)


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
        "revalidation_flags": "none", "inventory": [],
        "results": [{"result_id": "r-009", "evidence": "investigations/inv/evidence/r-009.json"}]}))
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
    write(draft, "findings.md", FINDINGS + "\nCounts come from orders_view, as inv/notes says.\n\n**Chart 2.** Line: cases\n"
          "\n### East held steady\n")
    (project / "investigations/inv/settings.toml").unlink()
    for path in (project / "investigations/inv/evidence").glob("r-00?.json"):
        path.unlink()
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and not report["passed"]
    assert report["findings"] == [{"line": 7, "kind": "name", "text": "orders_view"},
                                  {"line": 7, "kind": "path", "text": "inv/notes"}]
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
    assert any("no Current findings table" in error for error in report["errors"])


def test_check_draft_and_release_refuse_malformed_flag_entries(project, capsys):
    path = project / "deliveries/inv/pkg/draft/manifest.json"
    record = json.loads(path.read_text())
    del record["revalidation_flags"]
    path.write_text(json.dumps(record))
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and report["unmatched_flags"] == [] and report["flag_entries"] == [
        {"finding": None, "problem": "revalidation_flags is missing; rerun export"}]
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 1 and report["refused"] == "check-draft --verify-only does not pass"
    assert report["check"]["flag_entries"][0]["problem"] == "revalidation_flags is missing; rerun export"
    write(project, "investigations/inv/state.md", FLAGGED)
    entry_problem = "entry is not an object with a text finding and reason; rerun export"
    for flags, rows in [
            ({"finding": "x"}, [{"finding": None,
                                 "problem": "revalidation_flags is not none or a list; rerun export"}]),
            (["x", {"finding": "F2", "represented_in": "none"}],
             [{"finding": None, "problem": entry_problem}, {"finding": "F2", "problem": entry_problem}]),
            ([{**FLAG, "represented_in": [], "disposition": "none"}],
             [{"finding": FLAG["finding"], "problem": PLACES_PROBLEM}]),
            # A non-text reason or finding is reported, never hashed into a crash.
            ([{"finding": FLAG["finding"], "reason": [], "represented_in": "none"},
              {"finding": {"a": 1}, "reason": FLAG["reason"], "represented_in": "none"}],
             [{"finding": FLAG["finding"], "problem": entry_problem}, {"finding": None, "problem": entry_problem}]),
            ([{**FLAG, "represented_in": [" "], "disposition": "omit"}],
             [{"finding": FLAG["finding"], "problem": PLACES_PROBLEM}])]:
        set_flags(project, flags)
        for command in ("check-draft", "release"):
            code, report = run(project, capsys, command, "inv", "pkg")
            check = report if command == "check-draft" else report["check"]
            assert code == 1 and not check["passed"] and check["flag_entries"] == rows
    set_flags(project, [{**FLAG, "represented_in": ["chart 1"], "disposition": "revalidate"}])
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0 and report["flag_entries"] == []
    assert not (project / "deliveries/inv/pkg/released").exists()


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
    # A result represented without serialization is still listed with its evidence, for status.
    assert record["results"] == [{"result_id": r, "evidence": f"investigations/inv/evidence/{r}.json"}
                                 for r in ("r-001", "r-002")]
    assert (project / "deliveries/inv/pkg/draft/charts/chart-1.csv").read_bytes() == chart


def state_rows(*rows):
    """A state.md whose Current findings table holds (finding, status, reason) rows."""
    lines = "".join(f"| {finding} | [r-001](evidence/r-001.json) | {status} | association | {reason} |\n"
                    for finding, status, reason in rows)
    return STATE.split("| Late orders")[0] + lines + "\n## Next steps\n"


LONG_REASON = ("Q-3 corrected west dates after the vendor re-sent the March file; the late share was computed "
               "on the uncorrected dates, so the rise in the west may be an artifact of the correction (`Q-3`)")
SECOND = {"finding": "East held steady", "reason": "Q-5 dropped duplicate east rows"}


def test_export_creates_revalidation_flags_from_state(project, capsys):
    path = project / "deliveries/inv/pkg/draft/manifest.json"
    path.unlink()
    code, out = run(project, capsys, "export", "inv", "pkg", "--result", "r-001")
    assert code == 0 and out["created"] and out["flags_pending"] == [] and "flags_error" not in out
    assert manifest(project)["revalidation_flags"] == "none"
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0 and report["flag_entries"] == [] and report["unmatched_flags"] == []
    path.unlink()
    write(project, "investigations/inv/state.md", state_rows(
        (FLAG["finding"], "revalidation-needed (was supported)", LONG_REASON), ("Other finding", "supported", "")))
    code, out = run(project, capsys, "export", "inv", "pkg", "--result", "r-001")
    assert code == 0 and out["created"] and manifest(project)["revalidation_flags"] == [
        {"finding": FLAG["finding"], "reason": LONG_REASON, "represented_in": [], "disposition": "none"}]
    assert out["flags_pending"] == [{"finding": FLAG["finding"], "needs": "represented_in"}]
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and report["unmatched_flags"] == [] and report["flag_entries"] == [
        {"finding": FLAG["finding"], "problem": PLACES_PROBLEM}]


def test_export_replaces_malformed_flag_entries_before_writing(project, capsys):
    with_results(project)
    write(project, "investigations/inv/state.md", FLAGGED)
    set_flags(project, [{"finding": FLAG["finding"], "reason": [], "represented_in": ["chart 1"], "disposition": "omit"}])
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001:region,late_rate", "--no-datasets")
    assert code == 0 and out["written"]
    record = manifest(project)
    assert record["charts"] == [{"path": "charts/chart-1.csv", "result_id": "r-001"}]
    assert record["revalidation_flags"] == [{**FLAG, "represented_in": [], "disposition": "none"}]


def test_export_syncs_revalidation_flags_with_state(project, capsys):
    write(project, "investigations/inv/state.md", state_rows(
        (FLAG["finding"], "revalidation-needed (was supported)", FLAG["reason"]),
        (SECOND["finding"], "revalidation-needed", SECOND["reason"]),
        ("Third finding", "revalidation-needed", "Q-6 new")))
    chosen = {**FLAG, "represented_in": ["chart 1"], "disposition": "release_with_caveat", "note": "kept"}
    waiting = {**SECOND, "represented_in": ["findings: East"], "disposition": "none"}
    cleared = {"finding": "Gone", "reason": "fixed", "represented_in": "none"}
    stale = {"finding": "Third finding", "reason": "Q-6 old", "represented_in": ["chart 1"], "disposition": "omit"}
    set_flags(project, [stale, waiting, cleared, chosen])
    code, out = run(project, capsys, "export", "inv", "pkg", "--result", "r-001")
    assert code == 0 and out["written"]
    # State row order; exact matches kept whole; a changed reason starts fresh; a cleared flag drops.
    assert manifest(project)["revalidation_flags"] == [
        chosen, waiting, {"finding": "Third finding", "reason": "Q-6 new", "represented_in": [], "disposition": "none"}]
    assert out["flags_pending"] == [{"finding": SECOND["finding"], "needs": "disposition"},
                                    {"finding": "Third finding", "needs": "represented_in"}]
    write(project, "investigations/inv/state.md", STATE.format(status="supported", reason=""))
    code, out = run(project, capsys, "export", "inv", "pkg", "--result", "r-001")
    assert code == 0 and manifest(project)["revalidation_flags"] == "none" and out["flags_pending"] == []


def test_export_keeps_flags_when_state_is_unreadable(project, capsys):
    prior = [{**FLAG, "represented_in": ["chart 1"], "disposition": "none"}]
    set_flags(project, prior)
    write(project, "investigations/inv/state.md", b"\xff\xfe not text")
    code, out = run(project, capsys, "export", "inv", "pkg", "--result", "r-001")
    assert code == 0 and out["written"]
    assert out["flags_error"].startswith("investigations/inv/state.md: unreadable")
    record = manifest(project)
    assert record["revalidation_flags"] == prior and "producing_commit" in record
    assert out["flags_pending"] == [{"finding": FLAG["finding"], "needs": "disposition"}]


def test_flag_raised_after_none_fails_until_export_records_it(project, capsys):
    code, out = run(project, capsys, "export", "inv", "pkg", "--result", "r-001")
    assert code == 0 and manifest(project)["revalidation_flags"] == "none"
    run(project, capsys, "check-draft", "inv", "pkg")
    write(project, "investigations/inv/state.md", FLAGGED)
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and report["flag_entries"] == [] and report["unmatched_flags"] == [FLAG]
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 1 and report["refused"] == "flagged findings without a release disposition"
    assert report["unmatched_flags"] == [FLAG]
    code, out = run(project, capsys, "export", "inv", "pkg", "--result", "r-001")
    assert out["flags_pending"] == [{"finding": FLAG["finding"], "needs": "represented_in"}]
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert report["unmatched_flags"] == [] and report["flag_entries"] == [
        {"finding": FLAG["finding"], "problem": PLACES_PROBLEM}]


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


def test_export_display_stub_names_each_gap_once(project, capsys):
    tomllib = pytest.importorskip("tomllib")
    write(project, "investigations/inv/results/r-001.csv", "region,late_rate,n,share.west\nW,21.3,10,0.5\n")
    write(project, "investigations/inv/results/r-002.csv", "region,n\nW,10\n")
    write(project, "foundation/display.toml", '[columns]\nregion = "Region"\nlate_rate = "  "\n')
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001:region,late_rate",
                    "--chart", "r-002", "--dataset", "wide=r-001")
    assert code == 1 and not out["written"]
    assert out["errors"][0] == "r-001: column 'late_rate' has a blank display name in foundation/display.toml [columns]"
    # Deduplicated across the chart and dataset paths; the dotted column stays one quoted key; the
    # blank late_rate already has its key, so the stub leaves it out and pasting it stays valid TOML.
    assert out["display_stub"] == '"n" = ""\n"share.west" = ""'
    assert tomllib.loads('[columns]\nregion = "Region"\nlate_rate = "  "\n' + out["display_stub"])["columns"] == {
        "region": "Region", "late_rate": "  ", "n": "", "share.west": ""}
    write(project, "foundation/display.toml", '[columns]\nregion = "Region"\nlate_rate = "Late"\nn = "Cases"\n')
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-002", "--dataset", "wide=r-001")
    assert code == 1 and out["display_stub"] == '"share.west" = ""'
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-002", "--dataset", "wide=r-001:region,n")
    assert out["written"] and "display_stub" not in out


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
    for flag, problem in [({"disposition": "none"}, "no disposition"),
                          ({"disposition": "revalidate"}, "revalidation pending")]:
        set_flags(project, [{**FLAG, "represented_in": places, **flag}, unrelated])
        code, report = run(project, capsys, "release", "inv", "pkg")
        assert code == 1 and report["unmatched_flags"] == [] and report["dispositions"] == [
            {"finding": FLAG["finding"], "problem": problem}]
    # Malformed entries fail check-draft itself, so release refuses on the check with its flag_entries.
    unknown = "unknown disposition {!r}; record none, revalidate, omit, or release_with_caveat"
    for flag, problem in [({}, unknown.format(None)), ({"disposition": "later"}, unknown.format("later")),
                          ({"represented_in": [], "disposition": "omit"}, PLACES_PROBLEM),
                          ({"represented_in": [{"place": "chart 1"}], "disposition": "omit"}, PLACES_PROBLEM)]:
        set_flags(project, [{**FLAG, "represented_in": places, **flag}, unrelated])
        code, report = run(project, capsys, "release", "inv", "pkg")
        assert code == 1 and report["refused"] == "check-draft --verify-only does not pass"
        assert report["check"]["flag_entries"] == [{"finding": FLAG["finding"], "problem": problem}]
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


@pytest.mark.parametrize("verify_only", [False, True])
def test_check_draft_checks_findings_drift(project, verify_only):
    draft = load(project / "src/packaging/draft.py", "draft_findings_drift")
    assert draft.check_draft(project, "inv", "pkg")["passed"]
    write(project, "investigations/inv/state.md", STATE.format(status="supported", reason=""))
    path = project / "investigations/inv/findings.json"
    content = json.loads(path.read_text())
    assert content["findings"][0] == {
        "result": "r-009", "text": "Late orders rose in the west", "status": "supported", "prior_status": None,
        "flag_reason": "", "notes": [], "checks_caveat": "", "notes_checks": "", "claim": "association",
        "claim_basis": ""}
    report = draft.check_draft(project, "inv", "pkg", verify_only=verify_only)
    assert report["passed"] and report["errors"] == []
    del content["findings"][0]["claim"]  # an absent claim strength fails, never defaulted
    path.write_text(json.dumps(content))
    report = draft.check_draft(project, "inv", "pkg", verify_only=verify_only)
    assert not report["passed"] and "no valid claim strength" in " ".join(report["errors"])
    write(project, "investigations/inv/state.md", STATE.format(status="supported", reason=""))
    state = project / "investigations/inv/state.md"
    state.write_text(state.read_text().replace("Late orders rose in the west", "Hand edited finding"))
    report = draft.check_draft(project, "inv", "pkg", verify_only=verify_only)
    assert not report["passed"]
    assert "Hand edited finding" in " ".join(report["errors"])
    assert "state render --investigation inv" in " ".join(report["errors"])
    write(project, "src/provenance.py", "# old provenance helper\n")
    report = draft.check_draft(project, "inv", "pkg", verify_only=verify_only)
    assert not report["passed"] and "install_helpers.py --upgrade" in " ".join(report["errors"])
    write(project, "src/provenance.py", ASSETS["src/provenance.py"].read_bytes())
    (project / "investigations/inv/findings.json").unlink()  # with no findings.json, any row is drift
    report = draft.check_draft(project, "inv", "pkg", verify_only=verify_only)
    assert not report["passed"] and "state render --investigation inv" in " ".join(report["errors"])


@pytest.mark.parametrize("unusable", ["schema", "unscoped"])
def test_evidence_older_than_scoped_3_is_reported_for_rerun(project, capsys, unusable):
    path = project / "investigations/inv/evidence/r-001.json"
    evidence = json.loads(path.read_text())
    if unusable == "schema":
        evidence["schema"] = "awb-evidence/1"
    else:
        evidence["settings"].pop("result")
    path.write_text(json.dumps(evidence))
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and not report["passed"]
    assert ("investigations/inv/evidence/r-001.json: not awb-evidence/3 with result-scoped settings; rerun the result"
            in report["names_problems"])
    code, out = run(project, capsys, "export", "inv", "pkg", "--result", "r-001")
    assert code == 1 and any("rerun the result" in e for e in out["errors"])


CLAIM_FINDINGS = """# Order quality for the operations team
Operations leads, all regions, January to June 2026

## Answer

**Headline:** Discounts drive 4 points fewer late orders

## Findings

### Late orders rose in the west

- The new carrier drives the rise to 21%, a data-driven view.
- West volume, <!-- causes --> its comment unread, is flat.

**Chart 1.** Bar: late share by region

### Discounts cut late orders by 4 points

- Randomized discounts led to 4 points fewer late orders.

## How we know

**Headline:** Totals reconcile to the ledger

- June is short due to a feed outage.

## Limitations and open caveats

- Late orders may rise because of holiday volume.
"""
CLAIM_METHODOLOGY = """# Methodology

## Findings

### Late orders rose in the west

**Claim strength:** association

Result `r-009`, evidence [r-009](../../../../investigations/inv/evidence/r-009.json).

### Discounts cut late orders by 4 points

**Claim strength:** causal (experiment: randomized discount test)

Result `r-002`.
"""


def claim_draft(project, findings=CLAIM_FINDINGS, methodology=CLAIM_METHODOLOGY, results=("r-009", "r-002")):
    draft = project / "deliveries/inv/pkg/draft"
    write(draft, "findings.md", findings)
    write(draft, "methodology.md", methodology)
    path = draft / "manifest.json"
    record = json.loads(path.read_text())
    record["results"] = [{"result_id": r, "evidence": f"investigations/inv/evidence/{r}.json"} for r in results]
    path.write_text(json.dumps(record))


def test_check_draft_refuses_causal_wording_above_claim_strength(project, capsys):
    claim_draft(project)
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and not report["passed"]
    assert report["claims"] == [{
        "line": 12, "section": "Late orders rose in the west", "phrase": "drives", "claim": "association",
        "results": ["r-009"], "problem": "causal wording above the association claim strength; reword it, since "
        "only an experiment or an identified natural experiment supports a causal claim"}]
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 1 and report["refused"] == "check-draft --verify-only does not pass"
    assert [row["phrase"] for row in report["check"]["claims"]] == ["drives"]
    claim_draft(project, CLAIM_FINDINGS.replace("The new carrier drives the rise", "Late orders rose"))
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0 and report["passed"] and report["claims"] == []


CLEAN_FINDINGS = CLAIM_FINDINGS.replace("The new carrier drives the rise", "Late orders rose")
WEST = "### Late orders rose in the west"
HEADLINE = "The new carrier drives late orders up in the west"
WEST_BULLET = "- Late orders rose to 21%, a data-driven view."
WEST_CLAIM = "**Claim strength:** association"
DISCOUNT_CLAIM = "**Claim strength:** causal (experiment: randomized discount test)"
DISCOUNT_RESULT = "Result `r-002`."
WEST_DISCOUNT = "Late orders rose in the west"
DISCOUNT = "Discounts cut late orders by 4 points"
NO_LINE = "methodology.md's section has no **Claim strength:** line; its results support association"
UNRECOGNIZED = ("methodology.md's **Claim strength:** line is not descriptive, association, or causal with its "
                "design basis; its results support association")
NO_SECTION = ("methodology.md has no ### section with this heading, so no **Claim strength:** line; its results "
              "support association")
STATES_CAUSAL = "methodology.md states causal on its **Claim strength:** line; its results support association"
NESTED = ("a heading inside a list item or block quote, or indented four or more spaces; start each heading at the "
          "beginning of its line")
SETEXT = "text underlined with = or - renders as a heading; write headings with #, or leave a blank line before a rule"
EMPHASIS = ["Price **leads** to sales", "Price **leads to** sales", "Price _leads_ to sales", "Price le**ad**s to sales",
            "Price ~~leads~~ to sales", "Price &#108;eads to sales", "Price lea​ds to sales",
            "Price lea<!-- -->ds to sales", "Price <b>leads</b> to sales", "Price leads<br>to sales",
            "Price \\*leads\\* to sales", "Price \\_leads\\_ to sales", "Price ｌｅａｄｓ ｔｏ sales"]

# Every probe a reviewer ran against the claim check in rounds 1 and 2, and each Markdown form the shared
# reader closes with them: (findings edits, methodology edits, represented results, claims rows, headings rows).
# A claims row is (phrase, line) or its section and problem; a headings row is (heading or file:line, problem).
PROBES = {
    # Round 1: a ### headline is read with its slide (Opus 1, Codex 1).
    "headline": ([(WEST, f"### {HEADLINE}")], [(WEST, f"### {HEADLINE}")], ("r-009", "r-002"), [("drives", 10)], []),
    "headline on the only result": ([(WEST, "### Discounts drive fewer late orders")],
                                    [(WEST, "### Discounts drive fewer late orders")], ("r-009",),
                                    [("drive", 6), ("drive", 10), (DISCOUNT, STATES_CAUSAL), ("led to", 19)], []),
    # Round 1: "contribute to" is causal; the noun "result in" and "affected" are not (Opus 2).
    "contribute to": ([(WEST_BULLET, "- The carrier contribute to late orders.\n- The result in June affected "
                                     "stores.")], [], ("r-009", "r-002"), [("contribute to", 12)], []),
    # Round 1: a **Caveat:** bullet on a finding slide is read (Opus 3).
    "caveat bullet": ([(WEST_BULLET, "- **Caveat:** the rise is due to holiday volume.")], [], ("r-009", "r-002"),
                      [("due to", 12)], []),
    # Round 1: a ~~~ line inside a backtick fence does not close it (Opus 4).
    "tilde in a backtick fence": ([("**Chart 1.**", "```\n~~~\n```\n- The carrier contribute to late orders.\n\n"
                                                    "**Chart 1.**")], [], ("r-009", "r-002"),
                                  [("contribute to", 18)], []),
    # Round 1: only a rendered declaration counts, and it names one strength (Codex 2, 4).
    "declaration in a comment": ([], [(WEST_CLAIM, f"<!--\n{WEST_CLAIM}\n-->")], ("r-009", "r-002"),
                                 [(WEST_DISCOUNT, NO_LINE)], []),
    "declaration in a fence": ([], [(WEST_CLAIM, f"```markdown\n{WEST_CLAIM}\n```")], ("r-009", "r-002"),
                               [(WEST_DISCOUNT, NO_LINE)], []),
    "declaration indented as code": ([], [(WEST_CLAIM, f"    {WEST_CLAIM}")], ("r-009", "r-002"),
                                     [(WEST_DISCOUNT, NO_LINE)], []),
    "two strengths on one line": ([], [(WEST_CLAIM, "**Claim strength:** association / causal")],
                                  ("r-009", "r-002"), [(WEST_DISCOUNT, UNRECOGNIZED)], []),
    "whitespace design": ([], [(WEST_CLAIM, "**Claim strength:** causal (experiment:  )")], ("r-009", "r-002"),
                          [(WEST_DISCOUNT, UNRECOGNIZED)], []),
    "two declarations": ([], [(WEST_CLAIM, f"{WEST_CLAIM}\n\n**Claim strength:** causal (experiment: a test)")],
                         ("r-009", "r-002"), [(WEST_DISCOUNT, "methodology.md's section has 2 **Claim strength:** "
                                                              "lines; its results support association")], []),
    # Round 1: a result ID in a comment is not a citation (Codex 3), nor in a comment left open (round 2 closure).
    "citation in a comment": ([("Randomized discounts led to", "Randomized discounts drive")],
                              [(DISCOUNT_RESULT, "<!-- TODO: compare with r-002 -->")], ("r-009", "r-002"),
                              [(DISCOUNT, STATES_CAUSAL), ("drive", 19)], []),
    "citation in an unclosed comment": ([("Randomized discounts led to", "Randomized discounts drive")],
                                        [(DISCOUNT_RESULT, "<!-- TODO: compare with r-002")], ("r-009", "r-002"),
                                        [(DISCOUNT, STATES_CAUSAL), ("drive", 19)], []),
    # Round 2: the declared design must be the one state.md records (Opus 1).
    "other design": ([], [(DISCOUNT_CLAIM, "**Claim strength:** causal (experiment: some unrelated survey)")],
                     ("r-009", "r-002"),
                     [(DISCOUNT, "methodology.md states causal (experiment: some unrelated survey) on its **Claim "
                                 "strength:** line; state.md records causal (experiment: randomized discount test) "
                                 "for r-002; its results support causal")], []),
    "same design, other spacing and emphasis": ([], [(DISCOUNT_CLAIM, "**Claim strength:** *causal (experiment:  "
                                                                      "randomized discount test)*")],
                                                ("r-009", "r-002"), [], []),
    # Round 2: verbs of change with an agent are a known limit of the list, stated in the contract (Opus 2).
    "verb of change": ([(WEST_BULLET, "- The carrier raised late orders 4 points.")], [], ("r-009", "r-002"), [], []),
    # Round 2: a value in a code span reads as the value (Opus 3).
    "value in a code span": ([], [(WEST_CLAIM, "**Claim strength:** `association`")], ("r-009", "r-002"), [], []),
    # Round 2: emphasis and other inline markup do not hide a phrase (Codex 1).
    **{f"inline markup: {text}": ([(WEST_BULLET, f"- {text}.")], [], ("r-009", "r-002"), [("leads to", 12)], [])
       for text in EMPHASIS},
    # Round 2: a section commented out whole is no section (Codex 2, both closures).
    "methodology section commented out": (
        [], [(f"{WEST}\n", f"<!--\n{WEST}\n"), ("../../../../investigations/inv/evidence/r-009.json).",
                                                "../../../../investigations/inv/evidence/r-009.json).\n-->")],
        ("r-009", "r-002"), [(WEST_DISCOUNT, NO_SECTION)],
        [(WEST_DISCOUNT, "methodology.md has no ### section with this exact heading")]),
    # Round 2: sections sharing a heading pool their evidence and are refused (Codex 3).
    "duplicate methodology heading": (
        [], [(DISCOUNT_RESULT, f"{DISCOUNT_RESULT}\n\n### {DISCOUNT}\n\n{WEST_CLAIM}\n\nResult `r-009`.")],
        ("r-009", "r-002"),
        [(DISCOUNT, "methodology.md's section has 2 **Claim strength:** lines; its results support association"),
         ("led to", 19)],
        [(DISCOUNT, "methodology.md has 2 ### sections with this exact heading; merge them into one")]),
    "duplicate findings heading": ([("## How we know", f"### {DISCOUNT}\n\n- Discounts led to it.\n\n## How we know")],
                                   [], ("r-009", "r-002"), [],
                                   [(DISCOUNT, "findings.md has 2 ### slides with this heading; give each finding "
                                               "its own")]),
    # Round 2: a heading indented up to three spaces is a heading in both files (Codex 4, both closures).
    "indented headline": ([(WEST, f"   ### {HEADLINE}")], [(WEST, f"  ### {HEADLINE}")], ("r-009", "r-002"),
                          [("drives", 10)], []),
    # The reader's other forms: comments as CommonMark scopes them, and headings the slides cannot take.
    "comment open across a blank line": ([(WEST_BULLET, "- Late orders rose <!-- note\n\n- The carrier drives "
                                                        "them -->")], [], ("r-009", "r-002"), [("drives", 14)], []),
    "comment opener in a code span": ([(WEST_BULLET, "- See `<!--`, the carrier drives them `-->`.")], [],
                                      ("r-009", "r-002"), [("drives", 12)], []),
    "text after a comment block": ([(WEST_BULLET, "<!-- note --> The carrier drives them.")], [],
                                   ("r-009", "r-002"), [("drives", 12)], []),
    "heading in a quote or list": ([(WEST_BULLET, f"> ### {HEADLINE}\n- # of stores rose")], [],
                                   ("r-009", "r-002"), [("drives", 12)],
                                   [("findings.md:12", NESTED), ("findings.md:13", NESTED)]),
    "heading indented as code": ([(WEST_BULLET, "\n    ### The carrier rose")], [], ("r-009", "r-002"), [],
                                 [("findings.md:13", NESTED)]),
    "setext heading after an unchecked slide": ([("- June is short", "The carrier drives late orders\n---\n\n"
                                                                     "- June is short")], [], ("r-009", "r-002"), [],
                                                [("findings.md:26", SETEXT)]),
    "title heading after an unchecked slide": ([("## Limitations", "# The carrier drives late orders\n\n"
                                                                   "## Limitations")], [], ("r-009", "r-001"),
                                               [("drive", 6), (DISCOUNT, STATES_CAUSAL), ("led to", 19),
                                                ("drives", 27)], []),
}


@pytest.mark.parametrize("probe", PROBES)
def test_review_probes_read_markdown_as_it_renders(project, probe):
    findings_edits, methodology_edits, results, claims_rows, headings_rows = PROBES[probe]
    findings, methodology = CLEAN_FINDINGS, CLAIM_METHODOLOGY
    for old, new in findings_edits:
        assert old in findings, old
        findings = findings.replace(old, new, 1)
    for old, new in methodology_edits:
        assert old in methodology, old
        methodology = methodology.replace(old, new, 1)
    claim_draft(project, findings, methodology, results)
    draft = load(project / "src/packaging/draft.py", "draft_probes")
    directory = project / "deliveries/inv/pkg/draft"
    rows = draft.claim_problems(directory, list(results), draft.state_claims(project, "inv"))
    assert [(r["phrase"], r["line"]) if "phrase" in r else (r["section"], r["problem"]) for r in rows] == claims_rows
    assert [(r.get("heading") or f"{r['file']}:{r['line']}", r["problem"])
            for r in draft.heading_problems(directory)] == headings_rows


def test_names_and_charts_read_the_same_rendered_text(project):
    draft = load(project / "src/packaging/draft.py", "draft_rendered")
    path = project / "deliveries/inv/pkg/draft/findings.md"
    # A comment opened mid-paragraph ends with the paragraph, so its text shows; one opening a line runs to
    # its -->, here the end of the file, hiding the chart specification.
    path.write_text("# T\n\nSee orders_view <!-- open\n\nThen regions_table -->\n\n<!-- orders_view\n\n"
                    "**Chart 1.** Bar\n")
    assert draft.check_findings(path, names=["orders_view", "regions_table"]) == [
        {"line": 3, "kind": "name", "text": "orders_view"}, {"line": 5, "kind": "name", "text": "regions_table"}]
    assert draft.check_charts(path, path.parent / "charts") == [
        {"chart": "Chart 1", "problem": "chart file has no specification in findings"}]


def test_claim_check_reads_headlines_and_cited_designs(project, capsys):
    draft = load(project / "src/packaging/draft.py", "draft_headlines")
    claims = draft.state_claims(project, "inv")
    directory = project / "deliveries/inv/pkg/draft"
    # A finding slide's ### heading is its headline, read with the slide; the row says to reword both files.
    claim_draft(project, CLEAN_FINDINGS.replace(WEST, f"### {HEADLINE}"), CLAIM_METHODOLOGY.replace(WEST, f"### {HEADLINE}"))
    code, report = run(project, capsys, "check-draft", "inv", "pkg", "--verify-only")
    assert code == 1 and not report["passed"]
    assert report["claims"] == [{
        "line": 10, "section": HEADLINE, "phrase": "drives", "claim": "association", "results": ["r-009"],
        "problem": "causal wording above the association claim strength; reword it, since only an experiment or an "
                   "identified natural experiment supports a causal claim; reword the methodology.md heading to match"}]
    # Causal results recorded with different designs cannot share one causal finding.
    claim_draft(project, CLEAN_FINDINGS, CLAIM_METHODOLOGY.replace(DISCOUNT_RESULT, "Results `r-002` and `r-003`."),
                results=("r-009", "r-002", "r-003"))
    rows = draft.claim_problems(directory, ["r-009", "r-002", "r-003"],
                                {**claims, "r-003": "causal (natural experiment: border policy change)"})
    assert rows == [{"section": DISCOUNT, "problem": (
        "the results it cites record different causal designs (causal (experiment: randomized discount test) for "
        "r-002; causal (natural experiment: border policy change) for r-003); give each design its own finding; its "
        "results support causal")}]
    # A causal Claim cell needs design text, not just spaces.
    state = project / "investigations/inv/state.md"
    state.write_text(state.read_text().replace("(experiment: randomized discount test)", "(experiment:  )"))
    assert draft.state_claims(project, "inv")["r-002"] is None


def test_claim_strength_follows_cited_results_and_records(project, capsys):
    draft = load(project / "src/packaging/draft.py", "draft_claims")
    claims = draft.state_claims(project, "inv")
    assert claims == {"r-009": "association", "r-001": "association",
                      "r-002": "causal (experiment: randomized discount test)"}
    directory = project / "deliveries/inv/pkg/draft"
    clean = CLAIM_FINDINGS.replace("The new carrier drives the rise", "Late orders rose")
    # Citing r-009 too holds the discount slide to the weaker association claim.
    claim_draft(project, clean, CLAIM_METHODOLOGY.replace("Result `r-002`.", "Results `r-002` and `r-009`."))
    rows = draft.claim_problems(directory, ["r-009", "r-002"], claims)
    assert [(r.get("section"), r.get("phrase")) for r in rows] == [
        ("Discounts cut late orders by 4 points", None), ("Discounts cut late orders by 4 points", "led to")]
    assert rows[0]["problem"] == ("methodology.md states causal on its **Claim strength:** line; its results "
                                  "support association")
    # Without a causal represented finding, the Answer slide is held to association as well.
    claim_draft(project, clean, CLAIM_METHODOLOGY, results=("r-009", "r-001"))
    rows = draft.claim_problems(directory, ["r-009", "r-001"], claims)
    assert [(r.get("section"), r.get("phrase"), r.get("line")) for r in rows] == [
        ("Answer", "drive", 6), ("Discounts cut late orders by 4 points", None, None),
        ("Discounts cut late orders by 4 points", "led to", 19)]
    # A phrase across a line break is found at its first line.
    split = clean.replace("Randomized discounts led to", "Late orders fell\nbecause of discounts, by")
    claim_draft(project, split)
    rows = draft.claim_problems(directory, ["r-009", "r-002"], {**claims, "r-002": "association"})
    assert [(r.get("phrase"), r.get("line")) for r in rows if r.get("phrase")] == [("drive", 6), ("because of", 20)]
    # Code spans, fenced blocks, and link text targets are not wording.
    claim_draft(project, clean.replace("Late orders rose to 21%", "Late orders rose to 21% (`drives`)")
                + "\n```\ndrives\n```\n[link](drives.md)\n")
    assert draft.claim_problems(directory, ["r-009", "r-002"], claims) == []
    # A represented result without a recognized Claim, or with no row, fails.
    rows = draft.claim_problems(directory, ["r-009", "r-002", "r-003"], {**claims, "r-002": None})
    assert rows[:2] == [
        {"result": "r-002", "problem": "state.md's Claim cell is not descriptive, association, or causal with its "
                                       "design basis"},
        {"result": "r-003", "problem": "state.md has no findings row with a claim strength for this result"}]
    claim_draft(project, clean, CLAIM_METHODOLOGY.replace("**Claim strength:** association\n", ""))
    rows = draft.claim_problems(directory, ["r-009", "r-002"], claims)
    assert rows == [{"section": "Late orders rose in the west",
                     "problem": "methodology.md's section has no **Claim strength:** line; its results support "
                                "association"}]
    # The rendered table without a Claim column, and a manifest without results, are errors.
    state = project / "investigations/inv/state.md"
    state.write_text(state.read_text().replace("| Claim |", "| Strength |"))
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and any(e.startswith("claims: investigations/inv/state.md has no Current findings table with "
                                          "Evidence and Claim columns") for e in report["errors"])
    write(project, "investigations/inv/state.md", STATE.format(status="supported", reason=""))
    record = json.loads((directory / "manifest.json").read_text())
    del record["results"]
    (directory / "manifest.json").write_text(json.dumps(record))
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and "manifest: manifest.json records no results list; rerun export" in report["errors"]
