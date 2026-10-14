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
# test_check_draft_traces_narrative_numbers: numbers in both narratives trace to a represented result's table cells within rounding, check details, settings, and profile rates as percents; an untraced number fails with its file, line, and text in both modes and refuses release; allowed_numbers accepts it and export keeps that field; dropping a result from the represented set untraces its numbers.
# test_check_draft_reports_number_problems: a malformed allowed_numbers value or entry, a malformed results value or result_id, a missing result table, and an unreadable profile are numbers_problems that fail the check.
# test_check_numbers_reads_formats: thousands separators, percents of fractions, scales, multipliers, scientific notation, ranges, and rounding trace; dates, years where their period ends, times with am or pm or seconds, codes, glued names, chart number lists, list markers, footnotes, code, comments, and link targets are skipped; a count beside a month name, a bare or parenthesized year-like count, a fraction, a time without am or pm, and a hash in scientific form are read; allowed texts pass.
# test_check_numbers_reviewed_probes: every narrative probed in review rounds 1 to 3 is reported or skipped as intended, reading fail-safe: a context skips a number only where it marks no quantity, so a count after a punctuation mark, a chart reference, a date, or a year, or a year a word follows, is read; paths and identifiers are skipped whole; joined digits that are not thousands grouping or one decimal are read and never trace; a unit or context split by whitespace or a line wrap still counts; and non-quantities such as a comparison year or a week number are reported.
# test_recorded_text_reviewed_probes: every recorded text probed in review records the magnitudes intended, and an extreme or non-finite cell records nothing or itself without crashing.
# test_check_numbers_allowed_phrases_and_precision: an allowed phrase covers only the number it is written around, a bare allowed text every occurrence; a number traces at every written digit beyond 28 significant digits and not one unit of a further place outside its rounding.
# test_recorded_values_reads_whole_cells_and_quantities: a table cell is a number whole (an exponent too large to round does not crash) or read as narrative text, so an ID's or a path's digits add nothing; evidence text and parsed settings content add scaled and scientific values a narrative can write in full, without dates, booleans, or the settings file's size.
# test_recorded_values_keep_every_json_digit: profile and evidence fractions keep every written digit, so the exact narrative value traces and a value one digit off does not.
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
# test_copy_releases_copies_compares_and_never_overwrites: existing releases copy to newly recorded storage; a rerun reports already copied; a differing copy is a conflict; an unknown package fails; no audit directory is written.

import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from decimal import Decimal
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
RESULT = "region,late_rate,n\nW,21.349,10\nE,2.675,8\n"
FINDINGS = "# Order quality\n\n### Late orders rose in the west\n\n**Chart 1.** Bar: late share by region\n"
METHODOLOGY = "# Methodology\n\n## Findings\n\n### Late orders rose in the west\n"
STATE = """# Current investigation state

Last updated: 2026-10-01

## Current findings

| Finding | Evidence | Status | Revalidation reason or caveat |
| --- | --- | --- | --- |
| Late orders rose in the west | [r-009](evidence/r-009.json) | {status} | {reason} |

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
        match = re.fullmatch(r"\| (.*) \| \[(.+)\]\(evidence/\2\.json\) \| (.*) \| ?(.*?) ?\|", line)
        if match:
            finding, result, status, reason = (part.strip() for part in match.groups())
            flagged = re.fullmatch(r"revalidation-needed(?: \(was (.+)\))?", status)
            entries.append({"result": result, "text": finding, "status": "revalidation-needed" if flagged else status,
                            "prior_status": flagged[1] if flagged else None,
                            "flag_reason": reason if flagged else "", "notes": [] if flagged or not reason else [reason],
                            "checks_caveat": "", "notes_checks": ""})
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
    write(tmp_path, "investigations/inv/results/r-001.csv", RESULT)
    write(draft, "manifest.json", json.dumps({
        "investigation": "inv", "package": "pkg", "status": "draft", "revalidation_flags": "none",
        "results": [{"result_id": "r-001", "evidence": "investigations/inv/evidence/r-001.json"}], "inventory": []}))
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


def set_manifest(project, **fields):
    path = project / "deliveries/inv/pkg/draft/manifest.json"
    path.write_text(json.dumps({**json.loads(path.read_text()), **fields}))


TRACED = """# Order quality, January to June 2026

### Late orders rose in the west

- West closed 21.3% of orders late, against 2.7% in the east.
- Ten checks covered 3 rows; regions needed at least 5 orders.
- Missing regions were 0.0% of rows, and 1,240 orders were reviewed.

**Chart 1.** Bar: late share by region
"""


def test_check_draft_traces_narrative_numbers(project, capsys):
    draft = project / "deliveries/inv/pkg/draft"
    write(project, "investigations/inv/results/r-001.profile.json", json.dumps(
        {"row_count": 2, "columns": {"region": {"dtype": "object", "null_rate": 0.0, "distinct_count": 2}}}))
    write(project, "investigations/inv/results/r-002.csv", "orders\n1240\n")
    set_manifest(project, results=[{"result_id": r, "evidence": f"investigations/inv/evidence/{r}.json"}
                                   for r in ("r-001", "r-002")])
    # Table cells rounded, a check detail, a setting, a profile rate as a percent, a thousands separator.
    write(draft, "findings.md", TRACED)
    write(draft, "methodology.md", METHODOLOGY + "\nSettings `minimum_count = 7` (r-001), release 002, as of "
          "2026-06-30.\n\n- West closed 21.3% late.\n")
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0 and report["passed"] and report["numbers"] == [] and report["numbers_problems"] == []
    # A number no represented result produced fails with its file and line, in both modes and at release.
    write(draft, "findings.md", TRACED.replace("21.3%", "23.1%"))
    write(draft, "methodology.md", METHODOLOGY + "\nAbout 40 stores.\n")
    rows = [{"file": "findings.md", "line": 5, "text": "23.1%"},
            {"file": "methodology.md", "line": 7, "text": "40"}]
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and not report["passed"] and report["numbers"] == rows
    code, report = run(project, capsys, "check-draft", "inv", "pkg", "--verify-only")
    assert code == 1 and report["numbers"] == rows and report["verify"] == []
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 1 and report["refused"] == "check-draft --verify-only does not pass"
    assert report["check"]["numbers"] == rows and not (project / "deliveries/inv/pkg/released").exists()
    # An allowed number passes with its reason; a represented result's table is what makes a number trace.
    set_manifest(project, allowed_numbers=[{"text": "23.1%", "reason": "the prior release's figure"},
                                           {"text": "40", "reason": "store count from the owner"}])
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0 and report["passed"] and report["numbers"] == []
    allowed = manifest(project)["allowed_numbers"]
    code, _ = run(project, capsys, "export", "inv", "pkg", "--result", "r-002")
    assert code == 0 and manifest(project)["allowed_numbers"] == allowed  # export keeps the hand-recorded field
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and {"file": "findings.md", "line": 5, "text": "2.7%"} in report["numbers"]


def test_check_draft_reports_number_problems(project, capsys):
    for fields, problems in [
            ({"allowed_numbers": [{"text": "40", "reason": " "}, "40"]},
             ["allowed_numbers entry 1 is not {text, reason} with both filled in",
              "allowed_numbers entry 2 is not {text, reason} with both filled in"]),
            ({"allowed_numbers": {"text": "40"}}, ["allowed_numbers is not none or a list of {text, reason}"]),
            ({"results": [{"result_id": "../r-001"}]}, ["manifest.json results is not a list of result_id entries; "
                                                         "rerun export"]),
            ({"results": "none"}, ["manifest.json results is not a list of result_id entries; rerun export"]),
            ({"results": [{"result_id": "r-002"}]},
             ["investigations/inv/results/r-002.csv is missing; numbers from r-002 cannot be traced"])]:
        set_manifest(project, allowed_numbers="none",
                     results=[{"result_id": "r-001", "evidence": "investigations/inv/evidence/r-001.json"}])
        set_manifest(project, **fields)
        code, report = run(project, capsys, "check-draft", "inv", "pkg")
        assert code == 1 and report["numbers"] == [] and report["numbers_problems"] == problems
    write(project, "investigations/inv/results/r-002.profile.json", "{not json")
    write(project, "investigations/inv/results/r-002.csv", "n\n1\n")
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and report["numbers_problems"][0].startswith(
        "investigations/inv/results/r-002.profile.json: unreadable")


def test_check_numbers_reads_formats(tmp_path):
    draft = load(ASSETS["src/packaging/draft.py"], "draft_numbers")
    values = sorted({Decimal(v) for v in ("21.349", "0.105", "0.15", "3", "4213000", "12480", "1240", "0.5")})
    path = tmp_path / "findings.md"
    path.write_text("""# Orders, January to June 2026

- n = 1,240 as of June 30, 2026, 30 June 2026, 2026-06-30T14:05:00-04:00, 6/30/2026, and 14:05:30.
- West 21% and 21.35; between 10-15% or 10 and 15%; 3x the east; $4.2M and 12.5 thousand; 0.5 percentage points.
- Release 002, Q-3, chart-1, v1.2.3, COVID-19, FY2026, and Charts 1.
1. A list marker[^2], `code 77`, and [the 7 guide](notes/88.md).
<!-- 66 -->
```
44
```
- Untraced: 21.4%, 1,250, 4.3M, 16%, 2, 3/4 of stores, 14:05, and (2025).
- Skipped: in 2026, Q3 2026, Charts 2 and 3, 9:30am, 9:30 a.m., June 5, June 5-7, 2026, Monday, June 5.
- Traced: 1.24e3, 4.213e6, 1.5e-1 and 5e-1. Untraced: a hash 12345e6, 1e-5, 1.5e6, June 77 orders, 1950 orders.
""")
    assert draft.check_numbers(path, values) == [
        {"file": "findings.md", "line": 6, "text": "7"},
        *({"file": "findings.md", "line": 11, "text": t} for t in ("21.4%", "1,250", "4.3M", "16%", "2", "3/4", "14:05", "2025")),
        *({"file": "findings.md", "line": 13, "text": t} for t in ("12345e6", "1e-5", "1.5e6", "77", "1950"))]
    assert draft.check_numbers(path, values, allowed={"7", "2", "16%", "1,250", "4.3M", "21.4%", "3/4", "14:05", "(2025)",
                                                      "12345e6", "1e-5", "1.5e6", "77", "1950"}) == []


# Each narrative a review probed in rounds 1 to 3, and each case the fail-safe reading settles, with the numbers
# check_numbers reports for it ([] is all skipped or traced), against recorded values [0.5] unless a row gives its own values or allowed texts.
# Reading fails safe, so a number in a doubtful context is reported, never skipped.
SHARE, FIXTURE, SCALED = {"values": ["0.213"]}, {"values": ["21.349", "2.675", "10", "8"]}, \
    {"values": ["4.2", "4.2e6", "0.00001", "1.2e9"]}
REVIEWED_PROBES = [
    ("Probability is 1e-5.", ["1e-5"]), ("Revenue is 1.5e6.", ["1.5e6"]), ("Revenue is 1.5E+06.", ["1.5E+06"]),
    ("12e3 orders", ["12e3"]), ("12.5e3", ["12.5e3"]),  # any mantissa: a hash such as 12345e6 is reported too
    ("In June 77 orders were lost.", ["77"]), ("in June 31 orders", ["31"]), ("June 5, 77 orders", ["77"]),
    ("on June 5 77 orders", ["5", "77"]), ("5 June 77 orders", ["5", "77"]),  # a date ends at punctuation
    ("June 5 we met", ["5"]), ("On June 5, 2026 we met", ["2026"]), ("From June 1, 2026 to June 30, 2026.", []),
    ("As shown in Chart 1, 77 orders were late.", ["77"]), ("As shown in Chart 1; 77 orders were late.", ["77"]),
    ("Chart 1, 2 regions led.", ["2"]), ("See Chart 2 and 40 stores.", ["40"]), ("Chart 3 - 12 regions", ["12"]),
    ("Chart 1: 77 orders", ["77"]), ("Charts 1 and 4 show 77 orders", ["4", "77"]), ("Charts 1 and 4 show it", ["4"]),
    ("Charts 1, 2, and 3 show it", ["2", "3"]), ("Charts 2-3 show it", ["3"]), ("Charts 2-3", []),
    ("Charts 1 and 4.", []), ("Charts 1, 40 stores", ["40"]), ("Charts 1 and 2, 40 stores", ["40"]),
    ("Charts 4,5 show it", ["4,5"]),
    ("in 2025, 2030 orders shipped", ["2030"]), ("since 2019, and 2020", []), ("between 2023 and 2024", []),
    ("in 2023, 2024 and 2025", []), ("We reviewed 1950 orders and 2,000 stores", ["1950", "2,000"]),
    ("an increase in 2000 orders", ["2000"]), ("between 1950 and 2000 stores were affected", ["1950", "2000"]),
    ("late 2000 orders were found", ["2000"]), ("in 2025 and 2026 orders", ["2025", "2026"]), ("mid-2025.", []),
    ("In June 2026 orders were lost", ["2026"]), ("Q3 2025 revenue", ["2025"]), ("In Q3 2000 orders were late", ["2000"]),
    ("Revenue fell in Q3 2025.", []), ("FY 2024 and 2025 orders", ["2024", "2025"]), ("FY 2024 and 2025.", []),
    ("Late orders (2025) exceeded the target.", ["2025"]),
    ("in 2000\norders were lost", ["2000"]),  # a line wrap continues the sentence
    ("Late orders rose 3 points over 2025.", ["3", "2025"]), ("compared with 2024", ["2024"]),
    ("the 2025 baseline", ["2025"]), ("2026 H1", ["2026"]), ("Week 23", ["23"]),
    ("Python 3.12 and DuckDB 1.1.3", ["3.12"]), ("Python 3.11", ["3.11"]), ("Python 3.12.1", []), ("3.12", ["3.12"]),
    ("host 10.0.0.1", []), ("1.234.567 orders", ["1.234.567"]), ("1.234,5 orders", ["1.234,5"]),
    ("?id=42", ["42"]), ("## 2. Sources", []), ("1. 77 orders", ["77"]),
    ("The count rose to\n77. Orders then fell.", ["77"]),  # 77. continues a paragraph; only 1. starts a list
    ("opened at 9:30am", []), ("opened at 14:05", ["14:05"]), ("a 1:20 ratio", ["1:20"]),
    ("-21.3%", ["21.3%"]), ("10–15 percent", ["10", "15 percent"]),
    ("values 1,2,3 and 4, 5", ["1,2,3", "4", "5"]), ("21,3%", ["21,3%"]), ("3/4 of stores", ["3/4"]),
    ("Total,77 orders were late.", ["77"]), ("Total, 77 orders were late.", ["77"]), ("Total;77", ["77"]),
    ("Total:77", ["77"]), ("(77 orders)", ["77"]), ("Rates: West,21.3%; East,2.7%.", ["21.3%", "2.7%"]),
    ("West/21.3%", ["21.3%"]), ("sentence.5 stores", ["5"]), ("_77 orders_", ["77"]), ("late_77", []),
    ("Source: results/r-001-77.csv.", []), ("file data/run-2-45.parquet", []), ("**results/r-001-77.csv**", []),
    ("./run-2-45.csv and results/12-45.csv", []), ("ORD-123-45 and ORD-123", []), ("COVID-19", []),
    ("COVID-19-related 77 orders", ["77"]), ("top-10 stores", ["10"]), ("45/day", ["45"]),
    ("1st place", ["1st"], {"values": []}), ("77th percentile", ["77th"]), ("100ms", ["100ms"]),
    ("1 000 000 orders", ["1 000 000"], {"values": ["1", "0", "1000000"]}), ("5½", ["5½"], {"values": ["5"]}), ("30d window", [], {"values": ["30"]}),
    ("USD4.2M", [], {"values": ["4.2e6"]}),
    ("Late rate (%) <- r-001.late_rate", []), ("chart-1: Late rate (%) <- r-001.late_rate", []),
    ("Share was 21.3 percent.", [], SHARE), ("Share was 21.3  percent.", [], SHARE),
    ("Share was 21.3\npercent.", [], SHARE), ("Share was 21.3 %.", [], SHARE), ("> Share was 21.3\n> percent.", [], SHARE),
    ("> Orders rose in 2025\n> orders 77", ["2025", "77"]), ("> The count rose to\n> 77. Orders fell.", ["77"]),
    ("Revenue was 4.2  million.", [], SCALED), ("Revenue was 1.2 bn.", [], SCALED),
    ("Revenue is 4,200,000.", [], SCALED), ("The threshold is 0.00001.", [], SCALED),
    # Both narratives' numbers are recorded, so the check passes them; whether they agree is the manual item.
    ("### Late orders rose in the west\n\n- West closed 21.3% of orders late.", [], FIXTURE),
    ("### Late orders rose in the west\n\nWest closed 2.7% of orders late (r-001).", [], FIXTURE),
    ("Late orders rose 3 points over 2025; 2025 orders. Week 23 and 23 stores.", ["2025", "23"],
     {"values": ["3"], "allowed": {"over 2025", "Week 23"}}),
    ("Week 23 ran on Python 3.12, up 3 points over 2025; 23 stores and 2025 orders.", ["3", "23", "2025"],
     {"values": [], "allowed": {"Week 23", "Python 3.12", "over 2025"}}),
    ("compared with 2024, the 2025 baseline, 2026 H1", [],
     {"values": [], "allowed": {"compared with 2024", "the 2025 baseline", "2026 H1"}}),
    ("140 and 40%", ["140", "40%"], {"allowed": {"40"}}), ("Week 230", ["230"], {"allowed": {"Week 23"}}),
]


def test_check_numbers_reviewed_probes(tmp_path):
    draft = load(ASSETS["src/packaging/draft.py"], "draft_probes")
    path = tmp_path / "findings.md"
    found = {}
    for line, _, *options in REVIEWED_PROBES:
        option = options[0] if options else {}
        path.write_text(line + "\n")
        values = sorted(Decimal(value) for value in option.get("values", ["0.5"]))
        found[line] = [row["text"] for row in draft.check_numbers(path, values, allowed=option.get("allowed", ()))]
    assert found == {line: expected for line, expected, *_ in REVIEWED_PROBES}


# Each recorded text a review probed, with the magnitudes it records.
REVIEWED_RECORDED = [
    ("Revenue is $4.2M.", ["4.2", "4.2e6"]), ("threshold = 1e-5", ["0.00001"]), ("results/r-001-77.csv", []),
    ("ORD-123", []), ("1e999999999999999999", ["1e999999999999999999"]), ("9e9999999999999999999", []),
    ("sNaN", []), ("Infinity", []), ("-0", ["0"]), ("1,5", []), ("Total,77", ["77"]),
]


def test_recorded_text_reviewed_probes():
    draft = load(ASSETS["src/packaging/draft.py"], "draft_recorded_probes")
    for text, expected in REVIEWED_RECORDED:
        found = set()
        draft._magnitudes(text, found)
        assert sorted(found) == sorted(Decimal(value) for value in expected), text


def test_check_numbers_allowed_phrases_and_precision(tmp_path):
    draft = load(ASSETS["src/packaging/draft.py"], "draft_phrases")
    path = tmp_path / "methodology.md"
    path.write_text("Week 23 ran on Python 3.12, up 3 points over 2025; 23 stores and 2025 orders.\n")
    assert [row["text"] for row in draft.check_numbers(path, [], allowed={"Week 23", "Python 3.12", "over 2025"})] \
        == ["3", "23", "2025"]
    assert [row["text"] for row in draft.check_numbers(path, [], allowed={"23", "3.12", "3", "2025"})] == []
    path.write_text("Share 0.12345678901234567890123456789, or 1.2345678901234567890123456789e-1.\n")
    assert draft.check_numbers(path, [Decimal("0.12345678901234567890123456789")]) == []
    assert [row["text"] for row in draft.check_numbers(path, [Decimal("0.1234567890123456789012345679")])] == [
        "0.12345678901234567890123456789", "1.2345678901234567890123456789e-1"]  # 1E-29 away: outside the rounding


def test_recorded_values_reads_whole_cells_and_quantities(tmp_path):
    draft = load(ASSETS["src/packaging/draft.py"], "draft_recorded")
    write(tmp_path, "investigations/inv/results/r-001.csv",
          "customer_hash,orders,label,source\n4e1234567,3,ORD-123,results/r-001-77.csv\n")
    # settings content is parsed TOML, as awb_provenance records it.
    write(tmp_path, "investigations/inv/evidence/r-001.json", json.dumps(
        {"checks": [{"detail": "Revenue is $4.2M on 2026-06-30"}], "producing_commit": "1234567", "notes": "run 9",
         "settings": {"path": "settings.toml", "bytes": 120, "content": {
             "parameters": {"threshold": 1e-5, "start": "2026-01-01", "flag": True},
             "results": {"r-001": {"window_days": 30}}}}}))
    values, problems = draft.recorded_values(tmp_path, "inv", [{"result_id": "r-001"}])
    assert problems == [] and values == sorted(  # no 123 from ORD-123, no 77 from the path, no overflow
        Decimal(v) for v in ("3", "4e1234567", "4.2", "4.2e6", "0.00001", "30"))
    path = tmp_path / "findings.md"
    path.write_text("Revenue was 4,200,000 against a threshold of 0.00001.\n")
    assert draft.check_numbers(path, values) == []


def test_recorded_values_keep_every_json_digit(tmp_path):
    # Profile and evidence fractions are read as written, not through a binary float.
    draft = load(ASSETS["src/packaging/draft.py"], "draft_exact_json")
    write(tmp_path, "investigations/inv/results/r-001.csv", "label\nwest\n")
    write(tmp_path, "investigations/inv/results/r-001.profile.json",
          '{"value": 0.12345678901234567890123456789, "rate": 0.21300000000000001, "rows": 12345678901234567890}')
    write(tmp_path, "investigations/inv/evidence/r-001.json",
          '{"checks": [{"detail": {"share": 0.30000000000000004}}], "settings": {"content": {"cut": 1e-30}}}')
    values, problems = draft.recorded_values(tmp_path, "inv", [{"result_id": "r-001"}])
    assert problems == [] and values == sorted(Decimal(v) for v in (
        "0.12345678901234567890123456789", "0.21300000000000001", "12345678901234567890", "0.30000000000000004",
        "1e-30"))
    path = tmp_path / "findings.md"
    path.write_text("Shares 0.12345678901234567890123456789 and 0.21300000000000001.\n")
    assert draft.check_numbers(path, values) == []
    path.write_text("Shares 0.12345678901234568000000000000 and 0.21300000000000002.\n")
    assert [row["text"] for row in draft.check_numbers(path, values)] == [
        "0.12345678901234568000000000000", "0.21300000000000002"]


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
    lines = "".join(f"| {finding} | [r-001](evidence/r-001.json) | {status} | {reason} |\n"
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
    content = {"schema": "awb-findings/1", "findings": [
        {"result": "r-009", "text": "Late orders rose in the west", "status": "supported", "prior_status": None,
         "flag_reason": "", "notes": [], "checks_caveat": "", "notes_checks": ""}]}
    write(project, "investigations/inv/findings.json", json.dumps(content, indent=2) + "\n")
    report = draft.check_draft(project, "inv", "pkg", verify_only=verify_only)
    assert report["passed"] and report["errors"] == []
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
