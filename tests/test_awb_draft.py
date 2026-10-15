# Kept cases:
# test_check_draft_checks_findings_drift: synchronized JSON passes, drift fails with state render in both modes, an old helper gets an upgrade hint, and rows with no findings.json are drift.
# test_names_cover_project_records: names hold created views, sources without CTEs or table functions, settings dotted paths (not bare nested keys), and result IDs from evidence and state links; plain words, including plain investigation and package names, are left out.
# test_toml_keys_fall_back_to_tomli_then_key_lines: without tomllib, settings keys parse with tomli (no bare nested keys); without either, table headers and key lines; display.toml then names the missing package.
# test_check_draft_rewrites_inventory_and_passes: a clean draft passes; the inventory is rewritten, revised_at stamped only when it changes, other manifest fields kept; nothing is written outside the draft.
# test_evidence_older_than_scoped_3_is_reported_for_rerun: check-draft and export --result refuse awb-evidence/1 and unscoped /3 with a rerun instruction.
# test_check_draft_reports_each_helper_problem: an internal name, a path under the plain investigation name, a chart without a file, a finding heading methodology lacks, and a missing settings file each fail with the helper's rows unchanged.
# test_check_draft_reports_outline_and_chart_spec_rows: a headline over 15 words, a chart form outside the seven, a Data column the chart file lacks, and a file column no Data role names fail check-draft with outline and charts rows in both modes, and release refuses on them.
# test_check_draft_requires_each_question_in_methodology: export's questions pass once methodology repeats them; a question methodology lacks or rewords, a results entry without a question, and a manifest without results fail check-draft's questions, and release refuses on the check.
# test_questions_check_reads_methodology_as_it_renders: a question wrapped, emphasized, linked, escaped, in a code span, heading, or list item, or after a comment block on its line matches; one only in a comment, inline or a block, in fenced code, split over two paragraphs, or reworded does not.
# test_questions_check_matches_a_code_span_as_written: a question holding brackets, a tilde, an edge underscore, an asterisk, a character reference, or a backslash matches when a code span shows it exactly as written.
# test_questions_check_refuses_a_commented_question: the issue's probe, a question only inside an HTML comment, fails check-draft's questions; a manifest question with inline markup matches as it renders.
# test_check_draft_help_and_references_agree_on_the_rendered_reading: the check-draft help text, helpers.md, and the comment above _view name numbers as the only check that does not read the rendered view, and the help states how questions are read.
# test_check_draft_reports_unmatched_flags: in both modes, a finding state.md flags fails until the manifest records its exact finding and reason; a changed reason reopens it; no findings table is an error.
# test_export_replaces_malformed_flag_entries_before_writing: an entry whose reason is not text matches no flag and is replaced by a fresh entry; the export writes files and manifest together.
# test_check_draft_and_release_refuse_malformed_flag_entries: a missing revalidation_flags, a non-list value, an entry without text finding and reason, and [] or blank places fail check-draft's flag_entries, and release refuses on the check.
# test_check_draft_traces_narrative_numbers: numbers in both narratives trace to a represented result's table cells within rounding, check details, settings, and profile rates as percents; an untraced number fails with its file, line, and text in both modes and refuses release; allowed_numbers accepts it and export keeps that field; dropping a result from the represented set untraces its numbers.
# test_check_draft_reports_number_problems: a malformed allowed_numbers value or entry, a malformed results value or result_id, a missing result table, and an unreadable profile are numbers_problems that fail the check.
# test_check_numbers_reads_formats: thousands separators, percents of fractions, scales, multipliers, scientific notation, ranges, and rounding trace; dates, years where their period ends, times with am or pm or seconds, codes, glued names, chart number lists, list markers, footnotes, code, comments, and link targets are skipped; a count beside a month name, a bare or parenthesized year-like count, a fraction, a time without am or pm, and a hash in scientific form are read; allowed texts pass.
# test_check_numbers_reviewed_probes: every narrative probed in review rounds 1 to 4 is reported or skipped as intended, reading fail-safe: a context skips a number only where it marks no quantity, so a count after a punctuation mark, a chart reference, a date, or a year, or a year a word follows, is read; paths and identifiers are skipped whole; joined digits that are not thousands grouping or one decimal are read and never trace; a unit or context split by whitespace or a line wrap still counts; a number wrapping a list item's text is read, and a row's text allowed exactly covers it across a wrap; a leading- or trailing-point scientific mantissa is one number; and non-quantities such as a comparison year or a week number are reported.
# test_recorded_text_reviewed_probes: every recorded text probed in review records the magnitudes intended, and an extreme or non-finite cell records nothing or itself without crashing.
# test_check_numbers_allowed_phrases_and_precision: an allowed phrase covers only the number it is written around, a bare allowed text every occurrence; a row's text copied exactly covers its number after a line wrap or extra spaces; a number traces at every written digit beyond 28 significant digits and not one unit of a further place outside its rounding.
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
# test_release_manifest_lists_runtime_per_result: export copies each represented result's runtime block into its results entry, unknown when the evidence has none or a null one, as stale reads it, and the release manifest keeps them; each unread requirements line is a provenance gap.
# test_release_numbers_stamps_and_copies_to_storage: the next number after a gap, stamped copy, untouched draft, storage copy compared.
# test_release_storage_conflict_and_instructions: an existing destination is never overwritten; none chosen, unrecorded, and URL locations report what to do.
# test_check_draft_refuses_causal_wording_above_claim_strength: causal wording on an association finding's slide fails with a row naming the phrase, line, and claim; a causal finding's slide and the Answer slide under a causal represented finding pass; method and caveat slides, code, comments, and hyphenated words are not read; release refuses on the row.
# test_review_probes_read_markdown_as_it_renders: every reviewer probe of the claim check from rounds 1 to 3, one row each with its claims, headings, and markdown rows: headlines, caveat bullets, fences, comments open, closed, or in a list, declarations hidden, ambiguous, in a code span, in a list or quote, or naming another design, emphasis, links, hard breaks, and other inline markup, commented-out, duplicated, and indented headings, headings continuing a list item, and every form outside the Markdown subset.
# test_unsupported_markdown_fails_check_draft: a heading continuing a list item fails check-draft and release with its markdown row, and the wording below it is read on the finding slide.
# test_names_and_charts_read_the_same_rendered_text: the names scan and the chart check skip comments as CommonMark scopes them, and read escaped, character-reference, zero-width, and emphasized names and chart numbers as they render.
# test_claim_check_reads_headlines_and_cited_designs: a causal ### headline fails check-draft with a row to reword both files; cited causal results of different designs are refused; a whitespace design is unrecognized.
# test_claim_strength_follows_cited_results_and_records: a slide citing several results takes the weakest claim; one citing none takes the weakest represented; with no causal finding the Answer slide fails too; a missing Claim, a missing results list, and a missing or differing methodology Claim strength line each fail.
# test_numbers_skip_a_claim_strength_line_the_claims_check_accepts: numbers on a causal Claim strength line that repeats its result's Claim cell give no numbers row, while a line continuing its paragraph is read; a line the claims check refuses, another design or no experiment named, keeps its numbers; check_numbers skips only the claim_lines it is given.
# test_numbers_count_lines_as_the_claims_check_does_after_a_comment: a comment holding a line break that str.splitlines() sees (U+2028, form feed, NEL) keeps the numbers check's line numbers on the claims check's, so the accepted-claim skip cannot land on the next line.
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
SETTINGS = (b"[parameters]\nminimum_count = 5\nstart = 2026-01-01\n\n"
            b'[results.r-001]\nquestion = "How many claims closed late?"\n\n'
            b'[results.r-002]\nquestion = "Which regions close claims late?"\n')
STALE_SETTINGS = SETTINGS.replace(b"minimum_count = 5", b"minimum_count = 6")
RESULT = "region,late_rate,n\nW,21.349,10\nE,2.675,8\n"
CHART_SPEC = "**Chart 1.** Horizontal bar: late share by region\n- **Data:** category: Region; value: Closed late (%)\n"
FINDINGS = ("# Order quality\nOperations leads, all regions\n\n## Findings\n\n### Late orders rose in the west\n\n"
            + CHART_SPEC + "\n**Notes:** The west leads the regions.\n")
QUESTIONS = {"r-001": "How many claims closed late?", "r-002": "Which regions close claims late?"}
METHODOLOGY = ("# Methodology\n\n## Findings\n\n### Late orders rose in the west\n\n"
               "**Claim strength:** association\n\n"
               "Question (r-001): How many claims closed late?\nQuestion (r-002): Which regions close\nclaims late?\n")
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
    write(draft, "charts/chart-1.csv", "Region,Closed late (%)\nWest,21\n")
    write(tmp_path, "investigations/inv/results/r-001.csv", RESULT)
    write(tmp_path, "investigations/inv/results/r-002.csv", "region\nW\n")
    write(draft, "manifest.json", json.dumps({
        "investigation": "inv", "package": "pkg", "status": "draft",
        "revalidation_flags": "none", "inventory": [],
        "results": [{"result_id": r, "evidence": f"investigations/inv/evidence/{r}.json", "question": q}
                    for r, q in QUESTIONS.items()]}))
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
                                      "results", "results.r-001", "results.r-001.question",
                                      "results.r-002", "results.r-002.question"}
    monkeypatch.setitem(sys.modules, "tomli", None)
    assert {"parameters", "results.r-001", "minimum_count"} <= draft._toml_keys(text)
    write(project, "foundation/display.toml", "[columns]\n")
    with pytest.raises(ImportError, match="tomli"):
        draft.display_names(project)


def test_check_draft_rewrites_inventory_and_passes(project, capsys):
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0 and report["passed"] and "record" not in report
    assert (report["findings"], report["charts"], report["verify"], report["errors"]) == ([], [], [], [])
    assert report["questions"] == []  # r-002's question is wrapped across two lines and still matches
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
    assert report["findings"] == [{"line": 13, "kind": "name", "text": "orders_view"},
                                  {"line": 13, "kind": "path", "text": "inv/notes"}]
    assert report["charts"] == [{"chart": "Chart 2", "problem": "no chart file for this specification"},
                                {"chart": "Chart 2", "problem": "no **Data:** line under the specification"}]
    assert report["headings"] == [
        {"heading": "East held steady", "problem": "methodology.md has no ### section with this exact heading"}]
    assert report["markdown"] == []
    assert report["names_problems"] == [
        "no settings found: investigations/inv/settings.toml is absent and no evidence records a settings file"]
    assert report["verify"] == []


def test_check_draft_reports_outline_and_chart_spec_rows(project, capsys):
    draft = project / "deliveries/inv/pkg/draft"
    long = "Late orders rose in the west, the region with the most stores and the busiest carrier"
    write(draft, "findings.md", FINDINGS.replace("Horizontal bar", "Pie").replace("Closed late (%)", "Late share"))
    write(draft, "methodology.md", METHODOLOGY.replace("Late orders rose in the west", long))
    write(draft, "findings.md", (draft / "findings.md").read_text().replace("Late orders rose in the west", long))
    for argv in (("check-draft", "inv", "pkg"), ("check-draft", "inv", "pkg", "--verify-only")):
        code, report = run(project, capsys, *argv)
        assert code == 1 and not report["passed"]
        assert report["outline"] == [{"slide": long, "line": 6, "problem": "the headline has 16 words; keep it to 15"}]
        assert report["charts"] == [
            {"chart": "Chart 1", "problem": "names no chart form (Pie); open the specification with one of: "
                                            "Horizontal bar, Bar with intervals, Line, Column, Stacked bar, Scatter, "
                                            "Table"},
            {"chart": "Chart 1", "problem": "chart-1.csv has no column 'Late share', which **Data:** names"},
            {"chart": "Chart 1", "problem": "chart-1.csv column 'Closed late (%)' is named by no **Data:** role; "
                                            "name it, or export the chart without it"}]
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 1 and report["refused"] == "check-draft --verify-only does not pass"
    assert len(report["check"]["outline"]) == 1 and len(report["check"]["charts"]) == 3


def set_results(project, results):
    path = project / "deliveries/inv/pkg/draft/manifest.json"
    record = json.loads(path.read_text())
    if results is None:
        record.pop("results")
    else:
        record["results"] = results
    path.write_text(json.dumps(record))


NOT_REPEATED = ("methodology.md does not repeat this question verbatim in text that renders, within one paragraph "
                "or heading")


def test_check_draft_requires_each_question_in_methodology(project, capsys):
    draft = project / "deliveries/inv/pkg/draft"
    write(draft, "methodology.md", METHODOLOGY.split("Question (r-002)")[0])
    code, report = run(project, capsys, "export", "inv", "pkg", "--result", "r-001")
    assert code == 0 and report["questions"] == {"r-001": QUESTIONS["r-001"]}
    assert run(project, capsys, "check-draft", "inv", "pkg")[1]["passed"]
    assert run(project, capsys, "export", "inv", "pkg", "--result", "r-001", "--result", "r-002")[1]["written"]
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and not report["passed"] and report["questions"] == [
        {"result_id": "r-002", "question": QUESTIONS["r-002"],
         "problem": NOT_REPEATED}]
    write(draft, "methodology.md", METHODOLOGY.replace("Which regions close", "Which regions closed"))
    assert run(project, capsys, "check-draft", "inv", "pkg")[1]["questions"][0]["result_id"] == "r-002"
    write(draft, "methodology.md", METHODOLOGY)
    run(project, capsys, "check-draft", "inv", "pkg")
    no_question = "the manifest records no question for this result; run export, or copy its question " \
                  "from settings into a hand-added entry"
    for results, problems in (
            ([{"result_id": "r-001", "evidence": "investigations/inv/evidence/r-001.json"}],
             [{"result_id": "r-001", "problem": no_question}]),
            ([{"result_id": "r-001", "question": {"unknown": "evidence lacks question"}}],
             [{"result_id": "r-001", "problem": no_question}]),
            (None, [{"result_id": None, "problem": "the manifest records no results list; run export"}])):
        set_results(project, results)
        code, report = run(project, capsys, "release", "inv", "pkg")
        assert code == 1 and report["refused"] == "check-draft --verify-only does not pass"
        assert report["check"]["questions"] == problems
    assert not (project / "deliveries/inv/pkg/released").exists()


# Where methodology.md writes r-002's question, and whether the questions check finds it there.
QUESTION_PLACES = {
    "only in a comment block": ("<!-- Which regions close claims late? -->", False),
    "in a comment within a paragraph": ("Question (r-002): <!-- Which regions close claims late? --> to come.", False),
    "in fenced code": ("```\nWhich regions close claims late?\n```", False),
    "split over two paragraphs": ("Which regions close\n\nclaims late?", False),
    "reworded": ("Which regions closed claims late?", False),
    "wrapped": ("Question (r-002): Which regions\nclose claims\nlate?", True),
    "emphasized": ("Question (r-002): **Which regions** close _claims_ late?", True),
    "linked": ("Question (r-002): [Which regions](https://example.com/r-002) close claims late?", True),
    "escaped and referenced": ("Question (r-002): Which regions close claims late\\? See&#32;notes.", True),
    "in a code span": ("Question (r-002): `Which regions close claims late?`", True),
    "in a heading": ("#### Which regions close claims late?", True),
    "in a list item": ("- r-002: Which regions close\n  claims late?", True),
    "after a comment block on its line": ("<!-- r-002 --> Which regions close claims late?", True),
}


@pytest.mark.parametrize("place", QUESTION_PLACES)
def test_questions_check_reads_methodology_as_it_renders(project, place):
    draft = load(project / "src/packaging/draft.py", "draft_questions")
    directory = project / "deliveries/inv/pkg/draft"
    body, found = QUESTION_PLACES[place]
    write(directory, "methodology.md", METHODOLOGY.split("Question (r-002)")[0] + "\n" + body + "\n")
    record = json.loads((directory / "manifest.json").read_text())
    assert draft.question_problems(directory, record) == ([] if found else [
        {"result_id": "r-002", "question": QUESTIONS["r-002"],
         "problem": NOT_REPEATED}])


# A question holding a markup character, written exactly inside a code span, which shows it as written.
MARKUP_QUESTIONS = (
    "Which regions [excluding test] close late?",
    "Did ~5% of orders close late?",
    "Which _id values repeat?",
    "Is churn above 5*baseline?",
    "Which AT&amp;T orders close late?",
    "Which regions close late\\?",
)


@pytest.mark.parametrize("question", MARKUP_QUESTIONS)
def test_questions_check_matches_a_code_span_as_written(project, question):
    draft = load(project / "src/packaging/draft.py", "draft_markup_questions")
    directory = project / "deliveries/inv/pkg/draft"
    before = METHODOLOGY.split("Question (r-002)")[0]
    write(directory, "methodology.md", before + f"\nQuestion (r-002): `{question}`\n")
    record = json.loads((directory / "manifest.json").read_text())
    for entry in record["results"]:
        if entry["result_id"] == "r-002":
            entry["question"] = question
    assert draft.question_problems(directory, record) == []
    # Without the code span r-002 fails, so the pass above is the code span's.
    write(directory, "methodology.md", before + "\nQuestion (r-002): to come.\n")
    assert [row["result_id"] for row in draft.question_problems(directory, record)] == ["r-002"]


def test_questions_check_refuses_a_commented_question(project, capsys):
    # The issue's probe: a question only inside an HTML comment never renders, so check-draft fails.
    draft = project / "deliveries/inv/pkg/draft"
    write(draft, "methodology.md", METHODOLOGY.replace("Question (r-002): Which regions close\nclaims late?",
                                                      "<!-- Which regions close claims late? -->"))
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and [row["result_id"] for row in report["questions"]] == ["r-002"]
    # A question the manifest records with inline markup is compared as it renders, as methodology.md is.
    record = json.loads((draft / "manifest.json").read_text())
    record["results"][1]["question"] = "Which **regions** close claims late?"
    (draft / "manifest.json").write_text(json.dumps(record))
    write(draft, "methodology.md", METHODOLOGY)
    assert run(project, capsys, "check-draft", "inv", "pkg")[1]["questions"] == []


def test_check_draft_help_and_references_agree_on_the_rendered_reading(project, capsys):
    cli = load(project / "src/awb.py", "awb_cli_help")
    with pytest.raises(SystemExit):
        cli.main(["check-draft", "--help"])
    help_text = " ".join(capsys.readouterr().out.split())
    assert "Every check but numbers reads both files as they render." in help_text
    assert "a question in a comment or fenced code does not count" in help_text
    helpers = (SKILLS / "awb-package/references/helpers.md").read_text()
    assert "Every draft check but `numbers` reads" in helpers and "`questions` rows" in helpers
    source = ASSETS["src/packaging/draft.py"].read_text()
    assert "# Every draft check but numbers reads findings.md and methodology.md through `_view`" in source


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
Operations leads, all regions

## Findings

### Late orders rose in the west

- West closed 21.3% of orders late, against 2.7% in the east.
- Ten checks covered 3 rows; regions needed at least 5 orders.
- Missing regions were 0.0% of rows, and 1,240 orders were reviewed.

""" + CHART_SPEC + """
**Notes:** The west leads the regions.
"""


def test_check_draft_traces_narrative_numbers(project, capsys):
    draft = project / "deliveries/inv/pkg/draft"
    write(project, "investigations/inv/results/r-001.profile.json", json.dumps(
        {"row_count": 2, "columns": {"region": {"dtype": "object", "null_rate": 0.0, "distinct_count": 2}}}))
    write(project, "investigations/inv/results/r-002.csv", "orders\n1240\n")
    set_manifest(project, results=[{"result_id": r, "evidence": f"investigations/inv/evidence/{r}.json",
                                    "question": QUESTIONS[r]} for r in ("r-001", "r-002")])
    # Table cells rounded, a check detail, a setting, a profile rate as a percent, a thousands separator.
    write(draft, "findings.md", TRACED)
    write(draft, "methodology.md", METHODOLOGY + "\nSettings `minimum_count = 7` (r-001), release 002, as of "
          "2026-06-30.\n\n- West closed 21.3% late.\n")
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0 and report["passed"] and report["numbers"] == [] and report["numbers_problems"] == []
    # A number no represented result produced fails with its file and line, in both modes and at release.
    write(draft, "findings.md", TRACED.replace("21.3%", "23.1%"))
    write(draft, "methodology.md", METHODOLOGY + "\nAbout 40 stores.\n")
    rows = [{"file": "findings.md", "line": 8, "text": "23.1%"},
            {"file": "methodology.md", "line": 13, "text": "40"}]
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
    assert code == 1 and {"file": "findings.md", "line": 8, "text": "2.7%"} in report["numbers"]


def test_check_draft_reports_number_problems(project, capsys):
    (project / "investigations/inv/results/r-002.csv").unlink()
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


# Each narrative a review probed in rounds 1 to 4, and each case the fail-safe reading settles, with the numbers
# check_numbers reports for it ([] is all skipped or traced), against recorded values [0.5] unless a row gives its own values or allowed texts.
# Reading fails safe, so a number in a doubtful context is reported, never skipped.
SHARE, FIXTURE, SCALED = {"values": ["0.213"]}, {"values": ["21.349", "2.675", "10", "8"]}, \
    {"values": ["4.2", "4.2e6", "0.00001", "1.2e9"]}
REVIEWED_PROBES = [
    ("Probability is 1e-5.", ["1e-5"]), ("Revenue is 1.5e6.", ["1.5e6"]), ("Revenue is 1.5E+06.", ["1.5E+06"]),
    ("12e3 orders", ["12e3"]), ("12.5e3", ["12.5e3"]),  # any mantissa: a hash such as 12345e6 is reported too
    ("Failure probability was .5e-3.", [".5e-3"], {"values": ["0.5", "3"]}),  # one number, never its pieces
    ("Failure probability was 5.e-3.", ["5.e-3"], {"values": ["5", "3"]}),
    ("Failure rate was .5e-3.", [], {"values": ["0.0005"]}), ("Failure rate was 5.e-3.", [], {"values": ["0.005"]}),
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
    # Inside a list item or a quote, an indented number wraps the item's text unless a list item above has its indent.
    ("- Orders in the West rose to\n  77. Returns fell.", ["77"]), ("* Orders rose to\n  77. Then fell.", ["77"]),
    ("1. Orders in the West rose to\n   77. Returns fell.", ["77"]), ("> - The count rose to\n>   77. Orders then fell.", ["77"]),
    ("- Orders rose\n  steadily to\n  77. Then fell.", ["77"]), ("- Orders rose to\n77. Then fell.", []),
    ("  1. Orders rose\n  2. Orders fell", []), ("- Orders\n  - rose\n  77. Then fell.", []), ("- Orders\n  1. rose", []),
    ("1. Orders rose\n   steadily\n2. Orders fell", []),
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
    # A row's text copied exactly covers its number across extra spaces or a wrap; a bare number does not cover its unit.
    ("Share was 18.2\npercent last year.", [], {"values": [], "allowed": {"18.2 percent"}}),
    ("Share was 18.2  percent last year.", [], {"values": [], "allowed": {"18.2 percent"}}),
    ("> Share was 18.2\n> percent.", [], {"values": [], "allowed": {"18.2 percent"}}),
    ("- Share was 18.2\n  percent.", [], {"values": [], "allowed": {"18.2 percent"}}),
    ("Share was 18.2\npercent this year.", ["18.2 percent"], {"values": [], "allowed": {"18.2"}}),
    ("Ran in Week\n23 of the year.", [], {"values": [], "allowed": {"Week 23"}}),
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
    ("threshold = .5e-3", ["0.0005"]), ("rate 5.e-3", ["0.005"]),
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
    for text in ("Share was 23.1\npercent.\n", "Share was 23.1  percent.\n", "Share was 23.1 \n  percent.\n"):
        path.write_text(text)  # the row's text, copied exactly, covers it after a wrap or extra spaces
        assert [row["text"] for row in draft.check_numbers(path, [])] == ["23.1 percent"]
        assert draft.check_numbers(path, [], allowed={"23.1 percent"}) == []
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
    # A result represented without serialization is still listed with its evidence, for status, the
    # question its evidence recorded, verbatim, for methodology.md, and the runtime it recorded.
    assert record["results"] == [
        {"result_id": r, "evidence": f"investigations/inv/evidence/{r}.json", "question": QUESTIONS[r],
         "runtime": json.loads((project / f"investigations/inv/evidence/{r}.json").read_text())["runtime"]}
        for r in ("r-001", "r-002")]
    assert report["questions"] == QUESTIONS
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
    write(project / "deliveries/inv/pkg/draft", "findings.md", FINDINGS.replace(CHART_SPEC, ""))
    code, out = run(project, capsys, "export", "inv", "pkg", "--no-datasets", "--result", "r-002")
    assert code == 0 and out["charts"] == [] and out["check_charts"] == []
    record = manifest(project)
    assert (record["charts"], record["dataset_selection"], record["export_checks"]) == ("none", "none", "none")
    assert not (project / "deliveries/inv/pkg/draft/charts").exists()


def test_export_names_every_gap_and_blocks_stale_results(project, capsys):
    (project / "investigations/inv/results/r-002.csv").unlink()
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
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001:region,late_rate", "--no-datasets")
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


def test_release_manifest_lists_runtime_per_result(project, capsys):
    evidence = project / "investigations/inv/evidence"
    first = json.loads((evidence / "r-001.json").read_text())["runtime"]
    assert set(first) == {"python", "platform", "packages", "unread_requirements"}
    second = json.loads((evidence / "r-002.json").read_text())
    second["runtime"]["packages"]["duckdb"] = "0.0.1-fixture"
    (evidence / "r-002.json").write_text(json.dumps(second))
    code, report = run(project, capsys, "export", "inv", "pkg", "--result", "r-001", "--result", "r-002")
    assert code == 0 and report["written"]
    run(project, capsys, "check-draft", "inv", "pkg")
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 0 and report["released"] and report["provenance_gaps"] == []
    assert [(r["result_id"], r["runtime"]) for r in manifest(project, "released/001")["results"]] == [
        ("r-001", first), ("r-002", second["runtime"])]
    second["runtime"]["unread_requirements"] = ["requirements.txt:2: -e ."]
    (evidence / "r-002.json").write_text(json.dumps(second))
    run(project, capsys, "export", "inv", "pkg", "--result", "r-001", "--result", "r-002")
    run(project, capsys, "check-draft", "inv", "pkg")
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 0 and report["released"] and report["provenance_gaps"] == [
        {"field": "results[1].runtime.unread_requirements[0]",
         "reason": "requirements not read, packages unrecorded: requirements.txt:2: -e ."}]
    del second["runtime"]
    (evidence / "r-002.json").write_text(json.dumps(second))
    run(project, capsys, "export", "inv", "pkg", "--result", "r-001", "--result", "r-002")
    run(project, capsys, "check-draft", "inv", "pkg")
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 0 and report["provenance_gaps"] == [
        {"field": "results[1].runtime", "reason": "evidence lacks runtime"}]
    assert manifest(project, "released/003")["results"][1]["runtime"] == {"unknown": "evidence lacks runtime"}
    second["runtime"] = None
    (evidence / "r-002.json").write_text(json.dumps(second))
    run(project, capsys, "export", "inv", "pkg", "--result", "r-001", "--result", "r-002")
    assert manifest(project, "draft")["results"][1]["runtime"] == {"unknown": "evidence lacks runtime"}


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
    # Each represented result's question, repeated in a section of its own so it cites no result, and the
    # table the findings' numbers trace to: the questions and numbers checks pass, leaving claims to judge.
    questions = {r: {**QUESTIONS, "r-009": "Did west late orders rise?"}.get(r, "What did this result record?")
                 for r in results}
    write(draft, "findings.md", findings)
    write(draft, "methodology.md", methodology + "\n## Result questions\n\n" + "\n\n".join(questions.values()) + "\n")
    write(project, "investigations/inv/results/r-009.csv", "region,late_rate,change\nW,21,4\n")
    path = draft / "manifest.json"
    record = json.loads(path.read_text())
    record["results"] = [{"result_id": r, "evidence": f"investigations/inv/evidence/{r}.json", "question": questions[r]}
                         for r in results]
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
    claim_draft(project, DECK_FINDINGS)
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0 and report["passed"] and report["claims"] == [] and report["outline"] == []


CLEAN_FINDINGS = CLAIM_FINDINGS.replace("The new carrier drives the rise", "Late orders rose")
# CLEAN_FINDINGS with every slide's notes and the chart's Data line, so the whole draft passes.
DECK_FINDINGS = """# Order quality for the operations team
Operations leads, all regions, January to June 2026

## Answer

**Headline:** Discounts drive 4 points fewer late orders

**Notes:** The discount test is the answer.

## Findings

### Late orders rose in the west

- Late orders rose to 21%, a data-driven view.
- West volume, <!-- causes --> its comment unread, is flat.

""" + CHART_SPEC + """
**Notes:** The west leads the regions.

### Discounts cut late orders by 4 points

- Randomized discounts led to 4 points fewer late orders.

**Notes:** Stores were assigned at random.

## How we know

**Headline:** Totals reconcile to the ledger

- June is short due to a feed outage.

**Notes:** The ledger is the finance team's.

## Limitations and open caveats

**Headline:** Holiday volume may move late orders

- Late orders may rise because of holiday volume.

**Notes:** Holiday weeks are in the period.
"""
WEST = "### Late orders rose in the west"
HEADLINE = "The new carrier drives late orders up in the west"
WEST_BULLET = "- Late orders rose to 21%, a data-driven view."
WEST_CLAIM = "**Claim strength:** association"
DISCOUNT_CLAIM = "**Claim strength:** causal (experiment: randomized discount test)"
DISCOUNT_RESULT = "Result `r-002`."
WEST_DISCOUNT = "Late orders rose in the west"
DISCOUNT = "Discounts cut late orders by 4 points"
NO_LINE = ("methodology.md's section has no **Claim strength:** line opening a top-level paragraph; its results "
           "support association")
UNRECOGNIZED = ("methodology.md's **Claim strength:** line is not descriptive, association, or causal with its "
                "design basis; its results support association")
NO_SECTION = ("methodology.md has no ### section with this heading, so no **Claim strength:** line; its results "
              "support association")
STATES_CAUSAL = "methodology.md states causal on its **Claim strength:** line; its results support association"
# What a markdown row refuses, as `unsupported Markdown: <what> at line N; rewrite as <how>` names it.
HEADING_IN_LIST = "a heading inside a list item or block quote"
INDENTED_CODE = "text indented four or more spaces, which renders as code"
SETEXT = "text underlined with = or -, which renders as a heading"
FENCE_IN_LIST = "a code fence inside a list item or block quote"
FENCE_INDENTED = "a code fence indented from the start of its line"
FENCE_OPEN = "a code fence never closed"
COMMENT_IN_LIST = "a comment inside a list item or block quote"
COMMENT_INDENTED = "a comment indented from the start of its line"
COMMENT_OPEN = "a comment never closed"
HTML_BLOCK = "an HTML block"
INLINE_TAG = "an inline HTML tag"
DEFINITION = "a link reference or footnote definition"
CLAIM_IN_LIST = "a **Claim strength:** line inside a list item or block quote"
CLAIM_INDENTED = "a **Claim strength:** line indented from the start of its line"
CLAIM_IN_PARAGRAPH = "a **Claim strength:** line inside a paragraph"
CHART = "**Chart 1.** Bar: late share by region"
# Round 2: emphasis and other inline markup do not hide a phrase (Codex 1).
EMPHASIS = ["Price **leads** to sales", "Price **leads to** sales", "Price _leads_ to sales", "Price le**ad**s to sales",
            "Price ~~leads~~ to sales", "Price &#108;eads to sales", "Price lea​ds to sales",
            "Price lea<!-- -->ds to sales", "Price leads<br>to sales",
            "Price \\*leads\\* to sales", "Price \\_leads\\_ to sales", "Price ｌｅａｄｓ ｔｏ sales"]
# Round 3: a link's text joins the words around it, and a backslash hard break is whitespace (both reviews).
LINKS_AND_BREAKS = {"Price leads [to](https://example.com) sales": "leads to",
                    "Price due [to the outage](https://x.io)": "due to",
                    "This [lea](https://x.io)ds to churn": "leads to",
                    "The carrier [dri](https://x.io)ves late orders": "drives",
                    "Price [leads to](https://example.com) sales": "leads to",
                    "Price leads\\\n  to sales": "leads to",
                    "Price led\\\n  to churn": "led to",
                    # Round 4: a reference link never resolves, so its label shows; the phrase is found with the
                    # label read (Codex 2 nit in the Opus review) and with it dropped.
                    "See [a][drives] sales": "drives",
                    "Price [leads][x] to sales": "leads to"}

# Every probe a reviewer ran against the claim check in rounds 1 to 3, and each Markdown form the shared
# reader refuses or reads with them: (findings edits, methodology edits, represented results, claims rows,
# headings rows, markdown rows). A claims row is (phrase, line) or its section and problem; a headings row
# is (heading, problem); a markdown row is (file:line, what it refuses).
PROBES = {
    # Round 1: a ### headline is read with its slide (Opus 1, Codex 1).
    "headline": ([(WEST, f"### {HEADLINE}")], [(WEST, f"### {HEADLINE}")], ("r-009", "r-002"), [("drives", 10)], [],
                 []),
    "headline on the only result": ([(WEST, "### Discounts drive fewer late orders")],
                                    [(WEST, "### Discounts drive fewer late orders")], ("r-009",),
                                    [("drive", 6), ("drive", 10), (DISCOUNT, STATES_CAUSAL), ("led to", 19)], [], []),
    # Round 1: "contribute to" is causal; the noun "result in" and "affected" are not (Opus 2).
    "contribute to": ([(WEST_BULLET, "- The carrier contribute to late orders.\n- The result in June affected "
                                     "stores.")], [], ("r-009", "r-002"), [("contribute to", 12)], [], []),
    # Round 1: a **Caveat:** bullet on a finding slide is read (Opus 3).
    "caveat bullet": ([(WEST_BULLET, "- **Caveat:** the rise is due to holiday volume.")], [], ("r-009", "r-002"),
                      [("due to", 12)], [], []),
    # Round 1: a ~~~ line inside a backtick fence does not close it (Opus 4).
    "tilde in a backtick fence": ([("**Chart 1.**", "```\n~~~\n```\n- The carrier contribute to late orders.\n\n"
                                                    "**Chart 1.**")], [], ("r-009", "r-002"),
                                  [("contribute to", 18)], [], []),
    # Round 1: only a rendered declaration counts, and it names one strength (Codex 2, 4).
    "declaration in a comment": ([], [(WEST_CLAIM, f"<!--\n{WEST_CLAIM}\n-->")], ("r-009", "r-002"),
                                 [(WEST_DISCOUNT, NO_LINE)], [], []),
    "declaration in a fence": ([], [(WEST_CLAIM, f"```markdown\n{WEST_CLAIM}\n```")], ("r-009", "r-002"),
                               [(WEST_DISCOUNT, NO_LINE)], [], []),
    "declaration indented as code": ([], [(WEST_CLAIM, f"    {WEST_CLAIM}")], ("r-009", "r-002"),
                                     [(WEST_DISCOUNT, NO_LINE)], [], [("methodology.md:7", INDENTED_CODE)]),
    "two strengths on one line": ([], [(WEST_CLAIM, "**Claim strength:** association / causal")],
                                  ("r-009", "r-002"), [(WEST_DISCOUNT, UNRECOGNIZED)], [], []),
    "whitespace design": ([], [(WEST_CLAIM, "**Claim strength:** causal (experiment:  )")], ("r-009", "r-002"),
                          [(WEST_DISCOUNT, UNRECOGNIZED)], [], []),
    "two declarations": ([], [(WEST_CLAIM, f"{WEST_CLAIM}\n\n**Claim strength:** causal (experiment: a test)")],
                         ("r-009", "r-002"), [(WEST_DISCOUNT, "methodology.md's section has 2 **Claim strength:** "
                                                              "lines; its results support association")], [], []),
    # Round 1: a result ID in a comment is not a citation (Codex 3); a comment left open is refused (round 2
    # closure), and so is one inside a list item or quote, whose end CommonMark ties to the container (round 3
    # closure). A refused form is read as text, so the check fails on the markdown row.
    "citation in a comment": ([("Randomized discounts led to", "Randomized discounts drive")],
                              [(DISCOUNT_RESULT, "<!-- TODO: compare with r-002 -->")], ("r-009", "r-002"),
                              [(DISCOUNT, STATES_CAUSAL), ("drive", 19)], [], []),
    "citation in an unclosed comment": ([("Randomized discounts led to", "Randomized discounts drive")],
                                        [(DISCOUNT_RESULT, "<!-- TODO: compare with r-002")], ("r-009", "r-002"),
                                        [(DISCOUNT, STATES_CAUSAL), ("drive", 19)], [],
                                        [("methodology.md:15", COMMENT_OPEN)]),
    # Round 4: a reference link renders as written, since its definition is refused, so its label is a
    # citation (both closures); a plain citation is the control.
    "citation in a reference label": ([("Randomized discounts led to", "Randomized discounts drive")],
                                      [(DISCOUNT_RESULT, "Result r-002; also see [carrier comparison][r-009].")],
                                      ("r-009", "r-002"), [(DISCOUNT, STATES_CAUSAL), ("drive", 19)], [], []),
    "citation in plain text": ([("Randomized discounts led to", "Randomized discounts drive")],
                               [(DISCOUNT_RESULT, "Result r-002; also see carrier comparison r-009.")],
                               ("r-009", "r-002"), [(DISCOUNT, STATES_CAUSAL), ("drive", 19)], [], []),
    "citation in a comment in a list item": ([("Randomized discounts led to", "Randomized discounts drive")],
                                             [(DISCOUNT_RESULT, "- <!-- TODO: compare with r-002")], ("r-009", "r-002"),
                                             [], [], [("methodology.md:15", COMMENT_IN_LIST)]),
    "citation in a comment in a quote": ([("Randomized discounts led to", "Randomized discounts drive")],
                                         [(DISCOUNT_RESULT, "> <!-- TODO: compare with r-002")], ("r-009", "r-002"),
                                         [], [], [("methodology.md:15", COMMENT_IN_LIST)]),
    # Round 2: the declared design must be the one state.md records (Opus 1).
    "other design": ([], [(DISCOUNT_CLAIM, "**Claim strength:** causal (experiment: some unrelated survey)")],
                     ("r-009", "r-002"),
                     [(DISCOUNT, "methodology.md states causal (experiment: some unrelated survey) on its **Claim "
                                 "strength:** line; state.md records causal (experiment: randomized discount test) "
                                 "for r-002; its results support causal")], [], []),
    "same design, other spacing and emphasis": ([], [(DISCOUNT_CLAIM, "**Claim strength:** *causal (experiment:  "
                                                                      "randomized discount test)*")],
                                                ("r-009", "r-002"), [], [], []),
    # Round 2: verbs of change with an agent are a known limit of the list, stated in the contract (Opus 2).
    "verb of change": ([(WEST_BULLET, "- The carrier raised late orders 4 points.")], [], ("r-009", "r-002"), [], [],
                       []),
    # Round 2: a value in a code span reads as the value (Opus 3).
    "value in a code span": ([], [(WEST_CLAIM, "**Claim strength:** `association`")], ("r-009", "r-002"), [], [], []),
    **{f"inline markup: {text}": ([(WEST_BULLET, f"- {text}.")], [], ("r-009", "r-002"), [("leads to", 12)], [], [])
       for text in EMPHASIS},
    # An inline tag other than <br> is refused, since its attributes can hide text; its words are still read.
    "inline markup: Price <b>leads</b> to sales": ([(WEST_BULLET, "- Price <b>leads</b> to sales.")], [],
                                                   ("r-009", "r-002"), [("leads to", 12)], [],
                                                   [("findings.md:12", INLINE_TAG)]),
    "citation in a hidden span": ([], [(DISCOUNT_RESULT, '<span hidden>Result `r-002`.</span>')], ("r-009", "r-002"),
                                  [], [], [("methodology.md:15", INLINE_TAG)]),
    **{f"link or break: {text}": ([(WEST_BULLET, f"- {text}.")], [], ("r-009", "r-002"), [(phrase, 12)], [], [])
       for text, phrase in LINKS_AND_BREAKS.items()},
    # Round 2: a section commented out whole is no section (Codex 2, both closures).
    "methodology section commented out": (
        [], [(f"{WEST}\n", f"<!--\n{WEST}\n"), ("../../../../investigations/inv/evidence/r-009.json).",
                                                "../../../../investigations/inv/evidence/r-009.json).\n-->")],
        ("r-009", "r-002"), [(WEST_DISCOUNT, NO_SECTION)],
        [(WEST_DISCOUNT, "methodology.md has no ### section with this exact heading")], []),
    # Round 2: sections sharing a heading pool their evidence and are refused (Codex 3), compared as they
    # render, so a link in one heading does not set it apart (round 3 Codex closure).
    "duplicate methodology heading": (
        [], [(DISCOUNT_RESULT, f"{DISCOUNT_RESULT}\n\n### {DISCOUNT}\n\n{WEST_CLAIM}\n\nResult `r-009`.")],
        ("r-009", "r-002"),
        [(DISCOUNT, "methodology.md's section has 2 **Claim strength:** lines; its results support association"),
         ("led to", 19)],
        [(DISCOUNT, "methodology.md has 2 ### sections with this exact heading; merge them into one")], []),
    "duplicate methodology heading with a link": (
        [], [(DISCOUNT_RESULT, f"{DISCOUNT_RESULT}\n\n### Discounts cut late orders [by 4 points](https://example.com)"
                               f"\n\n{WEST_CLAIM}\n\nResult `r-009`.")],
        ("r-009", "r-002"),
        [(DISCOUNT, "methodology.md's section has 2 **Claim strength:** lines; its results support association"),
         ("led to", 19)],
        [(DISCOUNT, "methodology.md has 2 ### sections with this exact heading; merge them into one")], []),
    # Round 4: a code span in one heading does not set it apart either (Codex closure).
    "duplicate methodology heading with a code span": (
        [], [(DISCOUNT_RESULT, f"{DISCOUNT_RESULT}\n\n### Discounts cut late orders by `4` points"
                               f"\n\n{WEST_CLAIM}\n\nResult `r-009`.")],
        ("r-009", "r-002"),
        [(DISCOUNT, "methodology.md's section has 2 **Claim strength:** lines; its results support association"),
         ("led to", 19)],
        [(DISCOUNT, "methodology.md has 2 ### sections with this exact heading; merge them into one")], []),
    "duplicate findings heading": ([("## How we know", f"### {DISCOUNT}\n\n- Discounts led to it.\n\n## How we know")],
                                   [], ("r-009", "r-002"), [],
                                   [(DISCOUNT, "findings.md has 2 ### slides with this heading; give each finding "
                                               "its own")], []),
    # Round 2: a heading indented up to three spaces is a heading in both files (Codex 4, both closures).
    "indented headline": ([(WEST, f"   ### {HEADLINE}")], [(WEST, f"  ### {HEADLINE}")], ("r-009", "r-002"),
                          [("drives", 10)], [], []),
    # Round 3: a heading continuing a list item is refused and starts no slide, so an unchecked title cannot
    # switch the check off and the wording below it is read on the finding slide (both closures).
    "heading continuing a list item": ([(WEST_BULLET, "- Context\n\n  ## How we know\n\n  The carrier drives late "
                                                      "orders.")], [], ("r-009", "r-002"), [("drives", 16)], [],
                                       [("findings.md:14", HEADING_IN_LIST)]),
    "heading continuing a list item, other title": ([(WEST_BULLET, "- Context\n\n  ## Details\n\n  The carrier drives "
                                                                   "late orders.")], [], ("r-009", "r-002"),
                                                    [("drives", 16)], [], [("findings.md:14", HEADING_IN_LIST)]),
    "heading in a quote or list": ([(WEST_BULLET, f"> ### {HEADLINE}\n- # of stores rose")], [],
                                   ("r-009", "r-002"), [("drives", 12)], [],
                                   [("findings.md:12", HEADING_IN_LIST), ("findings.md:13", HEADING_IN_LIST)]),
    "heading indented as code": ([(WEST_BULLET, "\n    ### The carrier rose")], [], ("r-009", "r-002"), [], [],
                                 [("findings.md:13", INDENTED_CODE)]),
    "setext heading after an unchecked slide": ([("- June is short", "The carrier drives late orders\n---\n\n"
                                                                     "- June is short")], [], ("r-009", "r-002"), [],
                                                [], [("findings.md:26", SETEXT)]),
    "title heading after an unchecked slide": ([("## Limitations", "# The carrier drives late orders\n\n"
                                                                   "## Limitations")], [], ("r-009", "r-001"),
                                               [("drive", 6), (DISCOUNT, STATES_CAUSAL), ("led to", 19),
                                                ("drives", 27)], [], []),
    # Round 3: a declaration counts only as its own top-level paragraph at column 0; elsewhere it is refused
    # (Opus 3, and the fence in a list item of the Codex closure).
    "declaration in a fence in a list item": ([], [(WEST_CLAIM, f"- ```markdown\n  {WEST_CLAIM}\n  ```")],
                                              ("r-009", "r-002"), [(WEST_DISCOUNT, NO_LINE)], [],
                                              [("methodology.md:7", FENCE_IN_LIST), ("methodology.md:8", CLAIM_IN_LIST),
                                               ("methodology.md:9", FENCE_IN_LIST)]),
    "declaration as a list item": ([], [(WEST_CLAIM, f"- {WEST_CLAIM}")], ("r-009", "r-002"),
                                   [(WEST_DISCOUNT, NO_LINE)], [], [("methodology.md:7", CLAIM_IN_LIST)]),
    "declaration in a quote": ([], [(WEST_CLAIM, f"> {WEST_CLAIM}")], ("r-009", "r-002"),
                               [(WEST_DISCOUNT, NO_LINE)], [], [("methodology.md:7", CLAIM_IN_LIST)]),
    "declaration indented two spaces": ([], [(WEST_CLAIM, f"  {WEST_CLAIM}")], ("r-009", "r-002"),
                                        [(WEST_DISCOUNT, NO_LINE)], [], [("methodology.md:7", CLAIM_INDENTED)]),
    # Round 4: a declaration opening a paragraph counts, with text continuing it (Opus 3).
    "declaration opening a paragraph": ([], [(WEST_CLAIM, f"{WEST_CLAIM}\nResult `r-009` shows it.")],
                                        ("r-009", "r-002"), [], [], []),
    "declaration inside a paragraph": ([], [(WEST_CLAIM, f"The claim follows.\n{WEST_CLAIM}")], ("r-009", "r-002"),
                                       [(WEST_DISCOUNT, NO_LINE)], [], [("methodology.md:8", CLAIM_IN_PARAGRAPH)]),
    # The other forms outside the subset: indented code, an indented or unclosed fence, an indented comment,
    # and an HTML block are refused and read as text.
    "citation in indented code": ([], [(DISCOUNT_RESULT, f"    {DISCOUNT_RESULT}")], ("r-009", "r-002"), [], [],
                                  [("methodology.md:15", INDENTED_CODE)]),
    "fence never closed": ([(CHART, f"```\n{CHART}")], [], ("r-009", "r-002"), [], [],
                           [("findings.md:15", FENCE_OPEN)]),
    "fence indented two spaces": ([(CHART, f"{CHART}\n\n  ~~~\n  The carrier drives them.\n  ~~~")], [],
                                  ("r-009", "r-002"), [("drives", 18)], [],
                                  [("findings.md:17", FENCE_INDENTED), ("findings.md:19", FENCE_INDENTED)]),
    "comment indented two spaces": ([(CHART, f"{CHART}\n\n  <!-- The carrier drives them. -->")], [],
                                    ("r-009", "r-002"), [], [], [("findings.md:17", COMMENT_INDENTED)]),
    "citation in a link reference definition": ([], [(DISCOUNT_RESULT, "[r-002]: ../evidence/r-002.json")],
                                                ("r-009", "r-002"), [], [], [("methodology.md:15", DEFINITION)]),
    "HTML block": ([(CHART, f"<details>\nThe carrier drives late orders.\n</details>\n\n{CHART}")], [],
                   ("r-009", "r-002"), [("drives", 16)], [],
                   [("findings.md:15", HTML_BLOCK), ("findings.md:17", HTML_BLOCK)]),
    # Forms a differential run against a CommonMark parser turned up: an unmatched marker or an escaped
    # backtick or `<` shows as a character, so the word beside it is read; a numbered item ends the one
    # before it; an item opened empty ends at a blank line, so what follows indented four spaces is code.
    "unmatched marker": ([(WEST_BULLET, "- The carrier*drives late orders.")], [], ("r-009", "r-002"),
                         [("drives", 12)], [], []),
    "escaped backtick": ([(WEST_BULLET, "- See \\`the carrier drives them\\`.")], [], ("r-009", "r-002"),
                         [("drives", 12)], [], []),
    "escaped comment opener": ([(WEST_BULLET, "- The carrier \\<!-- x -->drives them.")], [], ("r-009", "r-002"),
                               [("drives", 12)], [], []),
    "heading in a second numbered item": ([(WEST_BULLET, "1. Late orders rose.\n2. ### The carrier drives late "
                                                         "orders")], [], ("r-009", "r-002"), [("drives", 13)], [],
                                          [("findings.md:13", HEADING_IN_LIST)]),
    "indented code after an empty item": ([(WEST_BULLET, "-\n\n    The carrier drives them.")], [],
                                          ("r-009", "r-002"), [("drives", 14)], [], [("findings.md:14", INDENTED_CODE)]),
    # Comments as CommonMark scopes them.
    "comment open across a blank line": ([(WEST_BULLET, "- Late orders rose <!-- note\n\n- The carrier drives "
                                                        "them -->")], [], ("r-009", "r-002"), [("drives", 14)], [],
                                         [("findings.md:12", COMMENT_OPEN)]),
    "comment opener in a code span": ([(WEST_BULLET, "- See `<!--`, the carrier drives them `-->`.")], [],
                                      ("r-009", "r-002"), [("drives", 12)], [], []),
    "text after a comment block": ([(WEST_BULLET, "<!-- note --> The carrier drives them.")], [],
                                   ("r-009", "r-002"), [("drives", 12)], [], []),
}


@pytest.mark.parametrize("probe", PROBES)
def test_review_probes_read_markdown_as_it_renders(project, probe):
    findings_edits, methodology_edits, results, claims_rows, headings_rows, markdown_rows = PROBES[probe]
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
    assert [(r["heading"], r["problem"]) for r in draft.heading_problems(directory)] == headings_rows
    refused = draft.markdown_problems(directory)
    assert [(f"{r['file']}:{r['line']}", r["problem"].split(" at line ")[0]) for r in refused] == [
        (place, f"unsupported Markdown: {what}") for place, what in markdown_rows]
    assert all(r["problem"].startswith(f"unsupported Markdown: {r['problem'][22:].split(' at line ')[0]} at line "
                                       f"{r['line']}; rewrite as ") for r in refused)


def test_unsupported_markdown_fails_check_draft(project, capsys):
    # The round-3 list-continuation heading: refused, and its wording read on the finding slide.
    claim_draft(project, CLEAN_FINDINGS.replace(WEST_BULLET, "- Context\n\n  ## How we know\n\n  Price drives sales."))
    code, report = run(project, capsys, "check-draft", "inv", "pkg", "--verify-only")
    assert code == 1 and not report["passed"]
    assert report["markdown"] == [{"file": "findings.md", "line": 14, "problem": (
        "unsupported Markdown: a heading inside a list item or block quote at line 14; rewrite as a heading at the "
        "start of its own line, outside lists and quotes")}]
    assert [(row["phrase"], row["line"]) for row in report["claims"]] == [("drives", 16)]
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 1 and report["check"]["markdown"] == [{"file": "findings.md", "line": 14, "problem": (
        "unsupported Markdown: a heading inside a list item or block quote at line 14; rewrite as a heading at the "
        "start of its own line, outside lists and quotes")}]


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
    # Escapes, character references, zero-width characters, and emphasis render a name or a chart number
    # whole, so the names scan and the chart check read it as the claims check does (round 3, both reviews):
    # chart-1.csv now has its specification.
    path.write_text("Read from orders\\_view, orders&#95;view, orders​_view, and orders_**view**.\n"
                    "Result r\\-009, r&#45;009, and [r-009](../evidence/r-009.json).\n\n"
                    + CHART_SPEC.replace("Chart 1.", "Chart &#49;."))
    assert draft.check_findings(path, names=["orders_view", "r-009"]) == (
        [{"line": 1, "kind": "name", "text": "orders_view"}] * 4 + [{"line": 2, "kind": "name", "text": "r-009"}] * 3)
    assert draft.check_charts(path, path.parent / "charts") == []
    # A reference link renders as written, since its definition is refused, so its label is visible (round 4,
    # both reviews); a code span crossing a line break is code, reported at its opening line (round 4, Codex 2).
    path.write_text("See [the view][orders_view] and [calculation][orders_view].\n\n"
                    "The calculation `COUNT(*)\nFILTER (WHERE late)` rose, and so did `x`.\n")
    assert draft.check_findings(path, names=["orders_view"]) == [
        {"line": 1, "kind": "name", "text": "orders_view"}, {"line": 1, "kind": "name", "text": "orders_view"},
        {"line": 3, "kind": "code", "text": "`COUNT(*) FILTER (WHERE late)`"}, {"line": 4, "kind": "code", "text": "`x`"}]
    path.write_text("The calculation `COUNT(*) FILTER (WHERE late)` rose.\n")
    assert draft.check_findings(path) == [{"line": 1, "kind": "code", "text": "`COUNT(*) FILTER (WHERE late)`"}]


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
                     "problem": "methodology.md's section has no **Claim strength:** line opening a top-level "
                                "paragraph; its results support association"}]
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


HOLDOUT = "causal (experiment: randomized holdout of 2024 Q3, 50/50 split)"


def test_numbers_skip_a_claim_strength_line_the_claims_check_accepts(project, capsys):
    # A causal **Claim strength:** line repeats state.md's Claim cell, design basis included, so once the claims
    # check accepts it its numbers trace to the record and the numbers check skips that line.
    write(project, "investigations/inv/state.md", STATE.format(status="supported", reason="").replace(
        "causal (experiment: randomized discount test)", HOLDOUT))
    claim_draft(project, DECK_FINDINGS, CLAIM_METHODOLOGY.replace(DISCOUNT_CLAIM, f"**Claim strength:** {HOLDOUT}"))
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert report["claims"] == [] and report["numbers"] == [] and code == 0 and report["passed"]
    # Only that source line is skipped: a number on the line continuing its paragraph is read.
    claim_draft(project, DECK_FINDINGS, CLAIM_METHODOLOGY.replace(
        DISCOUNT_CLAIM, f"**Claim strength:** {HOLDOUT}\nacross 77 stores"))
    report = run(project, capsys, "check-draft", "inv", "pkg")[1]
    assert report["claims"] == [] and report["numbers"] == [{"file": "methodology.md", "line": 14, "text": "77"}]
    # A line the claims check refuses keeps its numbers: another design, or the issue's line, which names no
    # experiment or natural experiment.
    for declared in (HOLDOUT.replace("Q3", "Q4"), "causal (randomized holdout of 2024 Q3, 50/50 split)"):
        claim_draft(project, DECK_FINDINGS, CLAIM_METHODOLOGY.replace(DISCOUNT_CLAIM, f"**Claim strength:** {declared}"))
        code, report = run(project, capsys, "check-draft", "inv", "pkg")
        assert code == 1 and [row["section"] for row in report["claims"]] == [DISCOUNT]
        assert report["numbers"] == [{"file": "methodology.md", "line": 13, "text": text} for text in ("2024", "50/50")]
    # Without the claims check's accepted lines, check_numbers reads every line.
    draft = load(project / "src/packaging/draft.py", "draft_claim_numbers")
    path = project / "deliveries/inv/pkg/draft/methodology.md"
    assert [row["text"] for row in draft.check_numbers(path, [Decimal(4)])] == ["2024", "50/50"]
    assert draft.check_numbers(path, [Decimal(4)], claim_lines={13}) == []


@pytest.mark.parametrize("brk", ["\u2028", "\x0c", "\x85"])
def test_numbers_count_lines_as_the_claims_check_does_after_a_comment(project, capsys, brk):
    # A comment holding a line break that str.splitlines() sees but "\n" does not must not shift the numbers
    # check's line numbers off the claims check's, or the skip lands on the line after the accepted claim.
    comment = f"## Findings\n<!-- note{brk}more -->"
    claim_draft(project, DECK_FINDINGS, CLAIM_METHODOLOGY.replace("## Findings", comment)
                .replace(DISCOUNT_CLAIM, f"{DISCOUNT_CLAIM}\nacross 77 stores"))
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and report["claims"] == []
    assert report["numbers"] == [{"file": "methodology.md", "line": 16, "text": "77"}]
    write(project, "investigations/inv/state.md", STATE.format(status="supported", reason="").replace(
        "causal (experiment: randomized discount test)", HOLDOUT))
    claim_draft(project, DECK_FINDINGS, CLAIM_METHODOLOGY.replace("## Findings", comment)
                .replace(DISCOUNT_CLAIM, f"**Claim strength:** {HOLDOUT}\nacross 77 stores"))
    report = run(project, capsys, "check-draft", "inv", "pkg")[1]
    assert report["claims"] == [] and report["numbers"] == [{"file": "methodology.md", "line": 16, "text": "77"}]


def storyline_fixture(project):
    state = project / "investigations/inv/state.md"
    write(project, "investigations/inv/state.md", state.read_text().replace("causal (experiment: randomized discount test)", "association"))
    provenance = load(project / "src/provenance.py", "ledger_story_fixture")
    for text, parent, priority in [
        ("How large is the change?", "", "should"),
        ("Where is the change?", "Q-001", "must"),
        ("Which customers changed?", "", "must"),
        ("Which detail helps?", "", "could"),
    ]:
        provenance.add_question(project, "inv", text, kind="analytical", answerer="data", origin="scope",
                                parent=parent, priority=priority)
    settings = project / "investigations/inv/settings.toml"
    settings.write_text(settings.read_text().replace('[results.r-001]', '[results.r-001]\nanswers = ["Q-001", "Q-002"]')
                        .replace('[results.r-002]', '[results.r-002]\nanswers = ["Q-003"]'))
    for question, result in (("Q-001", "r-001"), ("Q-002", "r-001"), ("Q-003", "r-002")):
        provenance.answer_question(project, "inv", question, results=[result])
    draft = project / "deliveries/inv/pkg/draft"
    shutil.rmtree(draft / "charts")
    write(draft, "methodology.md", "# Methodology\n\n## Findings\n\n"
          "### Customer rates differ\n\n**Claim strength:** association\n\n[r-002](../../../../investigations/inv/evidence/r-002.json)\n\n"
          "### Regional rates differ\n\n**Claim strength:** association\n\nResult: r-001\n\n"
          "### Coverage remains limited\n\n**Claim strength:** association\n\nNo recorded answer is claimed here.\n\n"
          "How many claims closed late?\n\nWhich regions close claims late?\n")
    return draft


# Only slides outside the longest run already in order are reported, so one moved slide is one row.
@pytest.mark.parametrize("headlines, misplaced", [
    (["Customer rates differ", "Regional rates differ", "Coverage remains limited"], []),
    (["Regional rates differ", "Customer rates differ", "Coverage remains limited"],
     [("Regional rates differ", "Q-002", 2)]),
    (["Coverage remains limited", "Customer rates differ", "Regional rates differ"],
     [("Coverage remains limited", None, 3)]),
    (["Coverage remains limited", "Regional rates differ", "Customer rates differ"],
     [("Coverage remains limited", None, 3), ("Regional rates differ", "Q-002", 2)]),
])
def test_check_draft_orders_findings_from_priority_then_tree(project, capsys, headlines, misplaced):
    draft = storyline_fixture(project)
    write(draft, "findings.md", "# Order quality\nOperations leads, all regions\n\n## Findings\n\n" +
          "".join(f"### {headline}\n\n- Rates vary across groups.\n\n**Notes:** Compare the groups.\n\n" for headline in headlines))
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert [(row["slide"], row["question"], row["expected_position"]) for row in report["storyline"]] == misplaced
    assert report["unlinked_findings"] == ["Coverage remains limited"]
    assert report["passed"] is (not misplaced), report
    assert code == (1 if misplaced else 0)
    # Read-only verification uses the same checks and reports the same rows.
    _, verified = run(project, capsys, "check-draft", "inv", "pkg", "--verify-only")
    assert verified["storyline"] == report["storyline"]


@pytest.mark.parametrize("required, body, placement, problem, text, audience", [
    (*case, "What caused the delay?", "") for case in [
    (False, None, "after", None),
    (False, "- What caused the delay?", "after", "no unanswered must"),
    (True, None, "after", "missing Open questions"),
    (True, "- What caused the delay?", "after", None),
    (True, "* What **caused** the delay?", "after", None),
    (True, "1. What [caused](https://example.invalid) the delay?", "after", None),
    (True, "- What caused\n  the delay?", "after", None),
    (True, "- Why were orders late?", "after", "missing question"),
    (True, "- Q-001: What caused the delay?", "after", "unexpected question"),
    (True, "- What caused the delay?\n- What caused the delay?", "after", "repeated question"),
    (True, "- What caused the delay?\n  - Ask the owner", "after", "nested bullets"),
    (True, "- What caused the delay?", "before", "after Limitations"),
    (True, "- What caused the delay?", "late", "before What changed"),
    (True, "- What caused the delay?", "twice", "exactly one"),
    (True, "What caused the delay?", "after", "missing question"),
    (True, "- What caused the delay?\n\n**Chart 2.** Table: supporting rates\n- **Data:** column: Rate", "after", "takes no chart"),
]] + [
    (True, "- Why were orders late?", "after", None, "What caused the delay?", "Why were orders late?"),
    (True, "- Why were orders late?", "after", None, "What caused the delay?", "Why were **orders** late?"),
    (True, "- What caused the delay?", "after", "missing question", "What caused the delay?", "Why were orders late?"),
    (True, "- Does late_rate differ?", "after", 'questions edit Q-001 --audience "<wording>"', "Does late_rate differ?", ""),
    (True, "- Does performance differ?", "after", 'questions edit Q-001 --audience "<wording>"', "Does late_rate differ?", ""),
    (True, "- Do orders differ?", "after", None, "Does orders_view differ?", "Do orders differ?"),
    (True, "- Does orders_view differ?", "after", 'questions edit Q-001 --audience "<wording>"', "Does orders_view differ?", ""),
])
def test_check_draft_open_questions_rows(project, capsys, required, body, placement, problem, text, audience):
    provenance = load(project / "src/provenance.py", "ledger_open_fixture")
    provenance.add_question(project, "inv", text, kind="context", answerer="user",
                            origin="scope", priority="must" if required else "could", audience=audience)
    # A parked must remains unresolved; set-aside and settled questions are excluded.
    for text, state in (("Which period?", "declined"), ("Which definition?", "superseded"), ("Which scope?", "answered")):
        entry = provenance.add_question(project, "inv", text, kind="context", answerer="user", origin="scope", priority="must")
        if state == "answered":
            provenance.answer_question(project, "inv", entry["id"], text="Current scope", by="user")
        else:
            provenance.set_question(project, "inv", [entry["id"]], state, reason="Set aside")
    draft = project / "deliveries/inv/pkg/draft"
    limitations = "\n## Limitations and open caveats\n\n**Headline:** Coverage remains limited\n\n**Notes:** Interpret with care.\n"
    changed = "\n## What changed since the last version\n\n**Headline:** Coverage is clearer\n\n**Notes:** Definitions are clearer.\n"
    opened = ("\n## Open questions\n\n**Headline:** Some questions remain\n\n" + body +
              "\n\n**Notes:** These answers matter.\n") if body is not None else ""
    parts = {"after": limitations + opened + changed, "before": opened + limitations + changed,
             "late": limitations + changed + opened, "twice": limitations + opened + opened + changed}
    write(draft, "findings.md", FINDINGS + parts[placement])
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    if problem:
        assert code == 1 and any(problem in row["problem"] for row in report["open_questions"]), report
    else:
        assert report["open_questions"] == [] and code == 0 and report["passed"], report
    _, verified = run(project, capsys, "check-draft", "inv", "pkg", "--verify-only")
    assert verified["open_questions"] == report["open_questions"]


def test_open_questions_includes_parked_and_recheck_without_truncation(project, capsys):
    provenance = load(project / "src/provenance.py", "ledger_complete_fixture")
    questions = ["Which regions need review?", "Which period applies?", "Which owner decides?",
                 "Which population matters?", "Which definition applies?", "Which caveat matters?"]
    for index, text in enumerate(questions):
        provenance.add_question(project, "inv", "Which regions in orders_view need review?" if index == 0 else text, kind="context", answerer="data" if index == 0 else "user",
                                origin="scope", priority="must")
    settings = project / "investigations/inv/settings.toml"
    settings.write_text(settings.read_text().replace('[results.r-001]', '[results.r-001]\nanswers = ["Q-001"]'))
    provenance.answer_question(project, "inv", "Q-001", results=["r-001"])
    provenance.set_question(project, "inv", ["Q-002"], "parked", reason="Waiting on owner")
    provenance.flag_findings(project, "inv", [{"result": "r-001", "reason": "Changed input"}])
    assert provenance.question_tree(project, "inv")[0]["display_status"] == "answered (awaiting recheck)"
    provenance.edit_question(project, "inv", "Q-001", audience="Which regions need review?")
    draft = project / "deliveries/inv/pkg/draft"
    record = manifest(project)
    record["revalidation_flags"] = [{"finding": "West volume is stable", "reason": "Changed input", "represented_in": "none", "disposition": "none"}]
    write(draft, "manifest.json", json.dumps(record))
    before_open = FINDINGS + "\n## Limitations and open caveats\n\n**Headline:** Coverage remains limited\n\n**Notes:** Interpret carefully.\n"
    opened = "\n## Open questions\n\n**Headline:** These answers still matter\n\n" + "\n".join("- " + text for text in questions) + "\n\n**Notes:** Confirm the unanswered questions.\n"
    write(draft, "findings.md", before_open + opened)
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert report["open_questions_count"] == 6
    assert report["open_questions"] == [] and report["outline"] == [] and code == 0, report
    assert report["findings"] == [] and report["passed"], report
    entry = provenance.question_tree(project, "inv")[0]
    assert entry["text"] == "Which regions in orders_view need review?" and entry["priority"] == "must"
    assert entry["status"] == "answered"
    write(draft, "findings.md", before_open + opened.replace("- Which regions need review?\n", ""))
    _, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert any(row.get("question") == "Which regions need review?" and row["problem"] == "missing question"
               for row in report["open_questions"])


@pytest.mark.parametrize("citation, unlinked", [
    ("Result: r-001", ["Coverage remains limited"]),
    ("Result: `r-001`", ["Coverage remains limited"]),
    ("[Evidence](../../../../investigations/inv/evidence/r-001.json)", ["Coverage remains limited"]),
    ("Result (r-001).", ["Coverage remains limited"]),
    ("Result: r-001-extra", ["Regional rates differ", "Coverage remains limited"]),
    ("<!-- Result: r-001 -->", ["Regional rates differ", "Coverage remains limited"]),
    ("The regional result", ["Regional rates differ", "Coverage remains limited"]),
    (None, ["Regional rates differ", "Coverage remains limited"]),
])
def test_storyline_citation_grammar_reports_unlinked_text(project, capsys, citation, unlinked):
    draft = storyline_fixture(project)
    write(draft, "findings.md", "# Order quality\nOperations leads, all regions\n\n## Findings\n\n"
          "### Customer rates differ\n\n**Notes:** Compare customers.\n\n"
          "### Regional rates differ\n\n**Notes:** Compare regions.\n\n"
          "### Coverage remains limited\n\n**Notes:** Interpret carefully.\n")
    path = draft / "methodology.md"
    if citation is None:
        (project / "investigations/inv/evidence/r-001.json").unlink()
    else:
        path.write_text(path.read_text().replace("Result: r-001", citation))
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert report["unlinked_findings"] == unlinked and report["storyline"] == []
    assert code == 0, report


@pytest.mark.parametrize("settings_text, empty_ledger, expected", [
    ('[results.r-001]\nquestion = "Which regions?"\nanswers = "Q-001"\n', False, "answers must be a list"),
    ('[results.r-001]\nquestion = "Which regions?"\nanswers = ["Q-999"]\n', False, "questions.json does not hold"),
    ('[results.r-001]\nquestion = "Which regions?"\nanswers = ["Q-999"]\n', True, "questions.json does not hold"),
    ('[parameters]\nscope = "current"\n', False, "settings"),
    ('[results.r-001\n', False, "settings"),
])
def test_storyline_refuses_unreadable_or_invalid_declared_answers(project, capsys, settings_text, empty_ledger, expected):
    draft = storyline_fixture(project)
    write(draft, "findings.md", "# Order quality\nOperations leads, all regions\n\n## Findings\n\n"
          "### Regional rates differ\n\n**Notes:** Compare the regions.\n")
    # Use the alternative settings file named in the evidence, rather than assume settings.toml.
    evidence = project / "investigations/inv/evidence/r-001.json"
    recorded = json.loads(evidence.read_text())
    recorded["settings"]["path"] = "investigations/inv/analysis.toml"
    evidence.write_text(json.dumps(recorded))
    write(project, "investigations/inv/analysis.toml", settings_text)
    if empty_ledger:
        write(project, "investigations/inv/questions.json", '{"schema": "awb-questions/1", "questions": []}')
        (project / "investigations/inv/questions.md").unlink()
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and any("storyline check:" in error and expected in error for error in report["errors"]), report


def test_storyline_should_precedes_could_and_ties_keep_order(project, capsys):
    draft = storyline_fixture(project)
    path = project / "investigations/inv/settings.toml"
    path.write_text(path.read_text().replace('answers = ["Q-001", "Q-002"]', 'answers = ["Q-001"]')
                    .replace('answers = ["Q-003"]', 'answers = ["Q-004"]'))
    write(draft, "findings.md", "# Order quality\nOperations leads, all regions\n\n## Findings\n\n"
          "### Customer rates differ\n\n**Notes:** Compare customers.\n\n"
          "### Regional rates differ\n\n**Notes:** Compare regions.\n")
    _, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert [(row["slide"], row["question"], row["expected_position"]) for row in report["storyline"]] == [
        ("Customer rates differ", "Q-004", 2)]
    # Equal question priority and position leave the author's ordering intact.
    path.write_text(path.read_text().replace('answers = ["Q-004"]', 'answers = ["Q-001"]'))
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert report["storyline"] == [] and code == 0, report
