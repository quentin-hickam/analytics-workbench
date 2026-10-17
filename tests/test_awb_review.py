# Kept cases:
# test_correction_becomes_a_numbered_rule: add creates foundation/review-rules.md with its header and R-<area>-001, numbers per area after every ID used, retired and hand-numbered ones included, and never renumbers earlier rules.
# test_next_review_reports_against_the_rule: check lists every rule in file order with matched lines from both narratives, no match, no pattern, and retired; matches are capped; nothing is written.
# test_check_without_rules_or_draft: no rule file reports none recorded and exits 0; a missing draft narrative is an error and exits 1.
# test_check_lists_matches_in_the_methodology_note: matches in methodology-note.md are listed with its file; without it nothing is missing; a note that cannot be read is an error.
# test_malformed_rule_file_is_reported_and_blocks_add: a bad heading, a repeated ID or field (at its line), missing fields, an unknown severity, and an unusable pattern (one overflowing included) are problems; check exits 1 with the rule unchecked; add refuses and writes nothing.
# test_broken_rule_section_is_reported_not_dropped: a rule under a malformed heading, or field lines outside a rule section, are problems; check exits 1 and add refuses, so no ID is reused.
# test_preamble_heading_holding_r_dash_is_not_a_rule_heading: a heading before the first rule that only contains R-, such as ## PR-12 follow-ups, is no problem.
# test_wrapped_field_line_is_reported: a line inside a rule section that is not a field, such as a wrapped Rule, is a problem rather than lost text.
# test_line_starting_with_hash_never_cuts_a_rule_short: after the first rule, a wrapped line starting with # or a heading that is not a rule's is a problem; check exits 1 and add refuses, so no rule is silently truncated.
# test_rule_numbers_are_ascii_and_unique: an ID repeating another's number with more zero padding, or a number in non-ASCII digits, is a problem; add refuses.
# test_rule_file_lines_count_only_newlines: a U+2028, form feed, or lone carriage return in the rule file is a problem at its grep -n line and shifts no later line; add refuses; CRLF endings are no problem.
# test_match_lines_count_only_newlines: a U+2028, form feed, or lone carriage return in a narrative does not shift the reported line numbers away from grep -n's, and CRLF endings still match a pattern anchored with $.
# test_lines_end_where_the_file_ends: a narrative has no empty line after its final \n, keeps a \r no \n follows, and reads a byte order mark as no part of line 1.
# test_rule_file_ends_where_the_file_ends: a lone \r as the rule file's last byte is a problem at its line, and add refuses; a rule heading after a byte order mark is sound.
# test_check_through_the_dispatcher_writes_nothing: run as a script with bytecode writes enabled, review-rules check leaves every project file, __pycache__ included, unchanged.
# test_only_review_rules_turns_off_bytecode_writes: the dispatcher sets sys.dont_write_bytecode for review-rules alone, so other commands keep the bytecode cache of the packages they import.
# test_rule_file_that_is_not_a_file_is_an_error: a directory or a dangling symbolic link at the rule file's path is an error, not no rules; check exits 1 and add refuses without a traceback.
# test_add_to_an_empty_rule_file_writes_the_header: add to an empty rule file writes the header before the first rule.
# test_add_rejects_unusable_arguments: a bad area (one ending in a number included), a text split by any line break the parser recognizes, blank, or holding bytes that are not UTF-8, an unknown severity or scope, or a pattern that does not compile (an overflowing repeat included) exits 2 and writes nothing.
# test_pattern_round_trips_through_backticks: a pattern holding backticks, or the word none, is written in backticks and read back as the same expression.
# test_slide_scope_lists_one_entry_per_slide: a Scope: slide rule with three matching bullets on one slide lists one entry with its heading, heading line, and three lines; methodology.md and the note give one entry per #, ##, or ### section.
# test_slide_scope_reads_sections_as_they_render: a # line in fenced code, a block quote, a list item, or an HTML comment opens no section, nor does a #### heading, text before the first heading is an entry with no heading, blank lines or a lone blank line included, and a line holding another break keeps grep -n's numbering.
# test_document_scope_lists_one_entry_per_file: add --scope document writes the Scope field after Pattern; check lists one entry per file, at most 20 lines with more_lines beyond; --scope line is written, an absent scope is not, and both list lines as before with no scope key.
# test_scope_field_accepted_and_refused_forms: Scope line, slide, or document is accepted; any other value, a blank one included, is a problem, the rule is unchecked, and add refuses until it is repaired.
# test_repeated_scope_line_is_reported: a second Scope line in a rule is a problem at its line.
# test_add_refuses_without_the_users_yes: add without --confirmed refuses, exit 1, writing nothing, naming the question to ask; with it the rule is added.
# test_package_rule_holds_for_its_package_alone: add --package <investigation>/<package> writes a Package field after Scope; check lists the rule, with package, for that package only, and a rule without one for every package; --package naming no package is refused and a malformed one exits 2, writing nothing; a malformed Package field is a problem and the rule holds for every package.
# test_add_warns_on_a_number_a_draft_states: add still adds, warning once per number in the rule or fix that a draft narrative states, compared by value (1,240 and 1240.0), naming the first place; --package reads only that package's draft; a number no draft states, or an unreadable narrative's numbers, give no number warning, the latter a read warning instead.
# test_another_packages_rule_leaves_a_review_current: adding or editing a rule kept for another package leaves a package's review current and its snapshot without that rule; a rule for this package or every package makes it stale; a rule file with problems counts whole.
# test_package_and_release_invoke_the_read_only_review: both skills link the review brief and run it before their final command; the brief has a fresh subagent review in every host with subagents, Codex included, and the writer review only where there are none; it limits the reviewer to reads, shell reads included, and the read-only command, running no command that writes, asks one line per rule, ends with a summary line counting violations, narrative problems, and command problems, any of which blocks, defines when a review is stale, and with AGENTS.md says which corrections become rules.
# test_receipt_after_a_clean_review_matches_until_what_it_read_changes: show is none before any record; a clean full review records a receipt (fingerprint, report verbatim, passed) and shows current, writing nothing; an edit to either narrative, the rule file, an added methodology note, or a flag's represented_in shows stale with that input alone in changed and a labelled diff whose hunks carry the current file's line numbers; undoing the edit shows current again.
# test_only_a_disposition_to_or_from_omit_makes_a_review_stale: release_with_caveat or revalidate leaves the review current, omit makes it stale, and an inventory rewrite leaves it current.
# test_failed_review_is_recorded_and_shows_failed: a report with an error violation is recorded with passed false and shows failed with the prior report; a repair makes it stale, and a scoped review that passes makes it current.
# test_accepted_narrative_problem_is_recorded_with_its_reason: a warning violation and a narrative problem, each accepted with the user's reason, pass and are recorded verbatim; fewer or more acceptances do not pass.
# test_acceptance_amends_the_recorded_review_and_refuses_after_a_change: --accept amends the recorded report, keeping its snapshot and time, and refuses, writing nothing, after an edit to what it read or for another report.
# test_scoped_record_needs_a_prior_record: a scoped report with no record to scope against is refused.
# test_represented_results_evidence_is_what_the_review_read: each evidence file the manifest's results name is snapshotted; a changed or dropped one shows stale, named by its path, with its diff.
# test_an_error_violation_or_command_problem_cannot_be_accepted: an --accept never passes a report counting an error violation or a command problem.
# test_unusable_report_is_refused_and_writes_nothing: an empty report, a last line that does not parse or is not last, a --kind its opening contradicts, more errors than violations, and rows the last line undercounts, backticked or numbered rows included, are refused, writing nothing and leaving an earlier record as it was.
# test_clean_review_takes_no_acceptance: --accept on a clean report is refused.
# test_summary_line_probes: backticks, a closing period, singular words, and bulleted rows read the same; the counts decide passed.
# test_snapshot_sits_beside_the_draft_and_is_replaced: the snapshot holds exactly what a review reads, under the package's review/, never in draft/, and each record replaces it, a removed note included.
# test_record_reads_the_report_from_stdin_and_checks_arguments: --report - reads standard input; an unknown kind, a missing or unreadable report, and a blank or multi-line --accept exit 2 and write nothing; a missing draft is refused.
# test_brief_change_makes_a_review_stale: the investigation's brief.md is snapshotted with the review, and an edit to it shows stale with brief.md alone in changed and a diff labelled with its path.
# test_show_reports_an_unreadable_receipt_and_bounds_the_diff: a long diff is cut so the printed line, a long prior report and typographic punctuation included, fits one read result, with a note counting the rest; an unreadable or malformed receipt is an error, exit 1, with status none.

import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents/skills"
ASSETS = {
    "src/awb.py": SKILLS / "awb-init/assets/awb_cli.py",
    "src/packaging/draft.py": SKILLS / "awb-package/assets/awb_draft.py",
}
RULES = "foundation/review-rules.md"
FINDINGS = "# Orders\n\n### Sales rose 4% in the partial month of October\n\n- Up on September.\n"
METHODOLOGY = "# Methodology\n\n### Sales rose 4% in the partial month of October\n\nOctober to the 12th.\n"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def project(tmp_path):
    for target, source in ASSETS.items():
        (tmp_path / target).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / target).write_bytes(source.read_bytes())
    draft = tmp_path / "deliveries/inv/pkg/draft"
    draft.mkdir(parents=True)
    (draft / "findings.md").write_text(FINDINGS)
    (draft / "methodology.md").write_text(METHODOLOGY)
    return tmp_path


def run(project, capsys, *argv):
    cli = load(project / "src/awb.py", "awb_cli_review")
    try:
        code = cli.main(list(argv))
    except SystemExit as exit:
        return exit.code, None
    return code, json.loads(capsys.readouterr().out)


def add(project, capsys, area="periods", severity="error", rule="Compare only complete months.",
        fix="Drop the partial month.", pattern=None, scope=None, package=None, confirmed=True):
    argv = ["review-rules", "add", "--area", area, "--severity", severity, "--rule", rule, "--fix", fix]
    return run(project, capsys, *argv, *(["--pattern", pattern] if pattern is not None else []),
               *(["--scope", scope] if scope is not None else []),
               *(["--package", package] if package is not None else []), *(["--confirmed"] * confirmed))


def snapshot(root, *, caches=False):
    # In-process runs load src/awb.py through the test's own import, which may cache it; the dispatcher
    # itself writes no cache, which test_check_through_the_dispatcher_writes_nothing checks with caches.
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*")
            if p.is_file() and (caches or "__pycache__" not in p.parts)}


def test_correction_becomes_a_numbered_rule(project, capsys):
    code, out = add(project, capsys, pattern=r"(?i)partial month")
    assert code == 0 and out == {"added": "R-periods-001", "rules_file": RULES, "created": True, "rules": 1,
                                 "warnings": []}
    text = (project / RULES).read_text()
    assert text.startswith("# Review rules\n")
    assert "## R-periods-001\n\n- Severity: error\n- Rule: Compare only complete months.\n" \
           "- Pattern: `(?i)partial month`\n- Fix: Drop the partial month.\n- Added: " in text

    assert add(project, capsys, severity="warning")[1]["added"] == "R-periods-002"
    assert add(project, capsys, area="metric-definitions")[1]["added"] == "R-metric-definitions-001"
    # A retired rule keeps its number; a hand-numbered one moves the next number past it.
    path = project / RULES
    path.write_text(path.read_text().replace("- Severity: warning", "- Severity: retired"))
    assert add(project, capsys)[1]["added"] == "R-periods-003"
    path.write_text(path.read_text() + "\n## R-periods-007\n\n- Severity: error\n- Rule: r\n- Pattern: none\n"
                                       "- Fix: f\n")
    code, out = add(project, capsys)
    assert code == 0 and out["added"] == "R-periods-008" and out["created"] is False and out["rules"] == 6
    headings = re.findall(r"^## (R-\S+)$", path.read_text(), re.MULTILINE)
    assert headings == ["R-periods-001", "R-periods-002", "R-metric-definitions-001", "R-periods-003",
                        "R-periods-007", "R-periods-008"]


def test_next_review_reports_against_the_rule(project, capsys):
    code, out = run(project, capsys, "review-rules", "check", "inv", "pkg")
    assert code == 0 and out["rules"] == [] and out["rules_file"] == "none recorded"

    add(project, capsys, pattern=r"(?i)partial month")
    add(project, capsys, area="wording", severity="warning", rule="Say customers, not users.", fix="Rename.",
        pattern=r"\busers\b")
    add(project, capsys, area="wording", severity="warning", rule="Name the period.", fix="Add it.")
    add(project, capsys, area="wording", rule="Retired rule.", fix="None.", pattern="Up")
    path = project / RULES
    path.write_text(path.read_text().replace("## R-wording-003\n\n- Severity: error",
                                            "## R-wording-003\n\n- Severity: retired"))
    before = snapshot(project)
    code, out = run(project, capsys, "review-rules", "check", "inv", "pkg")
    assert code == 0 and snapshot(project) == before
    assert out["rules_file"] == RULES and out["problems"] == [] and out["errors"] == []
    assert out["rules"] == [
        {"id": "R-periods-001", "severity": "error", "status": "matched", "matches": [
            {"file": "findings.md", "line": 3, "text": "### Sales rose 4% in the partial month of October"},
            {"file": "methodology.md", "line": 3, "text": "### Sales rose 4% in the partial month of October"}]},
        {"id": "R-wording-001", "severity": "warning", "status": "no match"},
        {"id": "R-wording-002", "severity": "warning", "status": "no pattern"},
        {"id": "R-wording-003", "severity": "retired", "status": "retired"}]

    findings = project / "deliveries/inv/pkg/draft/findings.md"
    findings.write_text(FINDINGS + "".join(f"- partial month {n}\n" for n in range(25)))
    row = run(project, capsys, "review-rules", "check", "inv", "pkg")[1]["rules"][0]
    assert len(row["matches"]) == 20 and row["more_matches"] == 7  # 25 bullets and both headings


def test_check_without_rules_or_draft(project, capsys):
    (project / "deliveries/inv/pkg/draft/methodology.md").unlink()
    add(project, capsys, pattern="partial")
    code, out = run(project, capsys, "review-rules", "check", "inv", "pkg")
    assert code == 1 and len(out["errors"]) == 1 and "methodology.md" in out["errors"][0]
    assert [m["file"] for m in out["rules"][0]["matches"]] == ["findings.md"]
    code, out = run(project, capsys, "review-rules", "check", "inv", "other")
    assert code == 1 and len(out["errors"]) == 2


def test_check_lists_matches_in_the_methodology_note(project, capsys):
    add(project, capsys, pattern=r"(?i)partial month")
    note = project / "deliveries/inv/pkg/draft/methodology-note.md"
    note.write_text("# How the analysis was done\n\nOctober is a partial month, so it is compared to the 12th.\n")
    code, out = run(project, capsys, "review-rules", "check", "inv", "pkg")
    assert code == 0 and out["errors"] == []
    assert [(m["file"], m["line"]) for m in out["rules"][0]["matches"]] == [
        ("findings.md", 3), ("methodology.md", 3), ("methodology-note.md", 3)]
    # Without the note nothing is missing; a note that cannot be read is an error, never skipped.
    note.unlink()
    code, out = run(project, capsys, "review-rules", "check", "inv", "pkg")
    assert code == 0 and [m["file"] for m in out["rules"][0]["matches"]] == ["findings.md", "methodology.md"]
    note.mkdir()
    code, out = run(project, capsys, "review-rules", "check", "inv", "pkg")
    assert code == 1 and len(out["errors"]) == 1 and "methodology-note.md" in out["errors"][0]


def test_malformed_rule_file_is_reported_and_blocks_add(project, capsys):
    path = project / RULES
    path.parent.mkdir(parents=True)
    path.write_text("# Review rules\n\n"
                    "## R-Periods-001\n\n- Severity: error\n\n"
                    "## R-periods-001\n\n- Severity: error\n- Rule: a\n- Pattern: none\n- Fix: b\n\n"
                    "## R-periods-001\n\n- Severity: error\n- Rule: a\n- Rule: again\n- Pattern: none\n- Fix: b\n\n"
                    "## R-periods-002\n\n- Severity: blocker\n- Rule: a\n- Pattern: (unclosed\n\n"
                    "## R-periods-003\n\n- Severity: warning\n- Rule: a\n- Pattern: `(unclosed`\n- Fix: b\n\n"
                    "## R-periods-004\n\n- Severity: warning\n- Rule: a\n- Pattern: `x{4294967296}`\n- Fix: b\n")
    before = path.read_text()
    code, out = run(project, capsys, "review-rules", "check", "inv", "pkg")
    assert code == 1
    problems = out["problems"]
    assert problems[0] == {"line": 3, "problem": "rule heading is not ## R-<area>-NNN with a lowercase area, its "
                                                 "last part holding a letter, and a three-digit number"}
    assert {"rule": "R-periods-001", "line": 18, "problem": "repeated Rule line"} in problems
    assert {"rule": "R-periods-001", "problem": "rule ID appears more than once"} in problems
    assert {"rule": "R-periods-002", "problem": "missing Fix"} in problems
    assert any(p.get("rule") == "R-periods-002" and "unknown severity 'blocker'" in p["problem"] for p in problems)
    assert {"rule": "R-periods-002", "problem": "Pattern is neither none nor a regular expression in backticks"} \
        in problems
    assert any(p.get("rule") == "R-periods-003" and p["problem"].startswith("Pattern does not compile")
               for p in problems)
    assert any(p.get("rule") == "R-periods-004" and p["problem"].startswith("Pattern does not compile")
               for p in problems)  # OverflowError, not re.error
    assert [row["status"] for row in out["rules"]] == ["no pattern", "no pattern", "unchecked", "unchecked",
                                                       "unchecked"]
    code, out = add(project, capsys)
    assert code == 1 and out["added"] is None and out["problems"] and path.read_text() == before


RULE = "- Severity: error\n- Rule: Compare only complete months.\n- Pattern: none\n- Fix: Drop it.\n"


@pytest.mark.parametrize("text, problem", [
    ("### R-periods-001\n\n" + RULE, {"line": 3, "problem": "rule heading is not ## R-<area>-NNN with a "
                                      "lowercase area, its last part holding a letter, and a three-digit number"}),
    (" ## R-periods-001\n\n" + RULE, {"line": 3, "problem": "rule heading is not ## R-<area>-NNN with a "
                                      "lowercase area, its last part holding a letter, and a three-digit number"}),
    ("## R-periods-001-001\n\n" + RULE, {"line": 3, "problem": "rule heading is not ## R-<area>-NNN with a "
                                         "lowercase area, its last part holding a letter, and a three-digit "
                                         "number"}),
    ("## Corrections\n\n" + RULE, {"line": 5, "problem": "rule field outside a ## R-<area>-NNN section"}),
    ("Severity: error\n", {"line": 3, "problem": "rule field outside a ## R-<area>-NNN section"})])
def test_broken_rule_section_is_reported_not_dropped(project, capsys, text, problem):
    # A rule a hand edit breaks is a problem, never a silently missing rule whose ID add hands out again.
    path = project / RULES
    path.parent.mkdir(parents=True)
    path.write_text("# Review rules\n\n" + text)
    before = path.read_text()
    code, out = run(project, capsys, "review-rules", "check", "inv", "pkg")
    assert code == 1 and out["rules"] == [] and problem in out["problems"]
    code, out = add(project, capsys)
    assert code == 1 and out["added"] is None and path.read_text() == before


def test_preamble_heading_holding_r_dash_is_not_a_rule_heading(project, capsys):
    path = project / RULES
    path.parent.mkdir(parents=True)
    path.write_text("# Review rules\n\n## PR-12 follow-ups\n\nNotes.\n\n## FOR-1 notes\n\n## R-periods-001\n\n" + RULE)
    code, out = run(project, capsys, "review-rules", "check", "inv", "pkg")
    assert code == 0 and out["problems"] == [] and [r["id"] for r in out["rules"]] == ["R-periods-001"]
    assert add(project, capsys)[1]["added"] == "R-periods-002"

def test_wrapped_field_line_is_reported(project, capsys):
    path = project / RULES
    path.parent.mkdir(parents=True)
    path.write_text("# Review rules\n\n## R-periods-001\n\n- Severity: error\n- Rule: Never compare\n"
                    "  partial months.\n- Pattern: none\n- Fix: Drop it.\n")
    code, out = run(project, capsys, "review-rules", "check", "inv", "pkg")
    assert code == 1 and out["problems"] == [
        {"rule": "R-periods-001", "line": 7, "problem": "line is not a - Severity, Rule, Pattern, Scope, Package, Fix, or Added field"}]


@pytest.mark.parametrize("tail, expected", [
    ("- Fix: Replace\n#hashtags with plain words.\n",
     [{"rule": "R-wording-001", "line": 8, "problem": "line is not a - Severity, Rule, Pattern, Scope, Package, Fix, or Added field"}]),
    ("- Fix: Count\n# of customers, not users.\n",
     [{"line": 8, "problem": "heading after the first rule is not a ## R-<area>-NNN rule heading"}]),
    ("- Fix: Rename.\n\n## Notes\n\nSee the style guide.\n",
     [{"line": 9, "problem": "heading after the first rule is not a ## R-<area>-NNN rule heading"}])])
def test_line_starting_with_hash_never_cuts_a_rule_short(project, capsys, tail, expected):
    path = project / RULES
    path.parent.mkdir(parents=True)
    path.write_text("# Review rules\n\n## R-wording-001\n- Severity: error\n- Rule: Avoid jargon.\n"
                    "- Pattern: none\n" + tail)
    before = path.read_text()
    code, out = run(project, capsys, "review-rules", "check", "inv", "pkg")
    assert code == 1 and out["problems"] == expected
    code, out = add(project, capsys, area="wording")
    assert code == 1 and out["added"] is None and path.read_text() == before


@pytest.mark.parametrize("heading, problem", [
    ("## R-periods-0001", "rule ID repeats the number of R-periods-001"),
    ("## R-periods-\u0661\u0662\u0663", "rule heading is not ## R-<area>-NNN with a lowercase area, its last part "
                                     "holding a letter, and a three-digit number")])
def test_rule_numbers_are_ascii_and_unique(project, capsys, heading, problem):
    add(project, capsys)
    path = project / RULES
    path.write_text(path.read_text() + f"\n{heading}\n\n" + RULE)
    before = path.read_bytes()
    code, out = run(project, capsys, "review-rules", "check", "inv", "pkg")
    assert code == 1 and problem in [p["problem"] for p in out["problems"]]
    code, out = add(project, capsys)
    assert code == 1 and out["added"] is None and path.read_bytes() == before


@pytest.mark.parametrize("brk", ["\u2028", "\x0c", "\r"])
def test_rule_file_lines_count_only_newlines(project, capsys, brk):
    path = project / RULES
    path.parent.mkdir(parents=True)
    path.write_bytes(("# Review rules\n\n## R-periods-001\n\n- Severity: error\n"
                      f"- Rule: Never compare{brk}partial months.\n- Pattern: none\n- Fix: Drop it.\n\n"
                      "# Notes\n").encode())
    before = path.read_bytes()
    code, out = run(project, capsys, "review-rules", "check", "inv", "pkg")
    assert code == 1 and out["problems"] == [  # grep -n: the Rule line is 6 and # Notes is 10
        {"line": 6, "problem": f"line holds U+{ord(brk):04X}, a line break other than \\n; replace it with a space "
                               "or a newline"},
        {"line": 10, "problem": "heading after the first rule is not a ## R-<area>-NNN rule heading"}]
    code, out = add(project, capsys)
    assert code == 1 and out["added"] is None and path.read_bytes() == before

    path.write_bytes(b"# Review rules\r\n\r\n## R-periods-001\r\n\r\n" + RULE.replace("\n", "\r\n").encode())
    code, out = run(project, capsys, "review-rules", "check", "inv", "pkg")
    assert code == 0 and out["problems"] == [] and out["rules"][0]["id"] == "R-periods-001"


@pytest.mark.parametrize("brk", ["\u2028", "\x0c", "\r"])
def test_match_lines_count_only_newlines(project, capsys, brk):
    findings = project / "deliveries/inv/pkg/draft/findings.md"
    findings.write_bytes(f"# F\n\nIntro{brk}pasted from Word\n\nSales in the partial month rose\n".encode())
    add(project, capsys, pattern="partial month")
    row = run(project, capsys, "review-rules", "check", "inv", "pkg")[1]["rules"][0]
    assert [(m["file"], m["line"]) for m in row["matches"]] == [("findings.md", 5), ("methodology.md", 3)]

    findings.write_bytes(b"# F\r\n\r\nSales in the partial month\r\n")
    add(project, capsys, pattern="partial month$")
    row = run(project, capsys, "review-rules", "check", "inv", "pkg")[1]["rules"][1]
    assert [(m["file"], m["line"], m["text"]) for m in row["matches"]] == [
        ("findings.md", 3, "Sales in the partial month")]


@pytest.mark.parametrize("text, pattern, lines", [
    (b"Alpha\n", "^$", []),  # grep -n '^$' finds nothing: the file has one line
    (b"", "^$", []),
    (b"\n", "^$", [1]),
    (b"Alpha\nBeta", "^Beta$", [2]),
    (b"Alpha\r", "\\r$", [1]),  # a \r at the end of the file is kept
    (b"Alpha\r\n", "\\r$", []),  # a CRLF ending's \r is not
    (b"\xef\xbb\xbfAlpha\n", "^Alpha", [1])])
def test_lines_end_where_the_file_ends(project, capsys, text, pattern, lines):
    draft = project / "deliveries/inv/pkg/draft"
    (draft / "findings.md").write_bytes(text)
    (draft / "methodology.md").write_bytes(b"")
    add(project, capsys, pattern=pattern)
    code, out = run(project, capsys, "review-rules", "check", "inv", "pkg")
    assert code == 0 and [m["line"] for m in out["rules"][0].get("matches", [])] == lines


def test_rule_file_ends_where_the_file_ends(project, capsys):
    path = project / RULES
    path.parent.mkdir(parents=True)
    path.write_bytes(b"# Review rules\n\n## R-periods-001\n\n" + RULE.rstrip("\n").encode() + b"\r")
    before = path.read_bytes()
    code, out = run(project, capsys, "review-rules", "check", "inv", "pkg")
    assert code == 1 and out["problems"] == [  # the Fix line, 8, ends the file with a lone \r
        {"line": 8, "problem": "line holds U+000D, a line break other than \\n; replace it with a space or a newline"}]
    code, out = add(project, capsys)
    assert code == 1 and out["added"] is None and path.read_bytes() == before

    path.write_bytes(b"\xef\xbb\xbf## R-periods-001\n\n" + RULE.encode())
    code, out = run(project, capsys, "review-rules", "check", "inv", "pkg")
    assert code == 0 and out["problems"] == [] and out["rules"][0]["id"] == "R-periods-001"
    assert add(project, capsys)[1]["added"] == "R-periods-002"


def test_check_through_the_dispatcher_writes_nothing(project, capsys):
    add(project, capsys, pattern="partial month")
    before = snapshot(project, caches=True)
    env = {k: v for k, v in os.environ.items() if k != "PYTHONDONTWRITEBYTECODE"}
    result = subprocess.run([sys.executable, str(project / "src/awb.py"), "review-rules", "check", "inv", "pkg"],
                            cwd=project, env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["rules"][0]["status"] == "matched"
    assert snapshot(project, caches=True) == before


def test_only_review_rules_turns_off_bytecode_writes(project, capsys, monkeypatch):
    # The flag is process-wide; other commands import pandas or duckdb, which keep their bytecode cache.
    (project / "src/provenance.py").write_text("def cli_stale(root, argv):\n    return 0\n")
    monkeypatch.setattr(sys, "dont_write_bytecode", False)
    cli = load(project / "src/awb.py", "awb_cli_bytecode")
    assert cli.main(["stale"]) == 0 and sys.dont_write_bytecode is False
    assert cli.main(["review-rules", "check", "inv", "pkg"]) == 0 and sys.dont_write_bytecode is True


@pytest.mark.parametrize("kind", ["directory", "dangling link"])
def test_rule_file_that_is_not_a_file_is_an_error(project, capsys, kind):
    path = project / RULES
    path.parent.mkdir(parents=True)
    if kind == "directory":
        path.mkdir()
    else:
        path.symlink_to(project / "foundation/missing.md")
    code, out = run(project, capsys, "review-rules", "check", "inv", "pkg")
    assert code == 1 and out["rules_file"] == RULES and len(out["errors"]) == 1
    assert out["errors"][0].startswith(f"{RULES}: ")
    code, out = add(project, capsys)
    assert code == 1 and out["added"] is None and out["refused"].startswith(f"{RULES}: ")
    assert not (project / "foundation/missing.md").exists() and (path.is_dir() or path.is_symlink())

def test_add_to_an_empty_rule_file_writes_the_header(project, capsys):
    (project / RULES).parent.mkdir(parents=True)
    (project / RULES).write_text("\n")
    code, out = add(project, capsys)
    assert code == 0 and out["added"] == "R-periods-001" and out["created"] is False
    assert (project / RULES).read_text().startswith("# Review rules\n")


@pytest.mark.parametrize("change", [
    {"area": "Periods"}, {"area": "periods_x"}, {"area": "-periods"}, {"area": "periods-001"}, {"area": "2024"},
    {"rule": "two\nlines"}, {"rule": "Never compare\u2028partial months."}, {"fix": "a\x85b"},
    {"pattern": "a\vb"}, {"fix": "  "}, {"severity": "retired"}, {"pattern": "(unclosed"}, {"pattern": ""},
    {"scope": "page"}, {"scope": "Slide"}, {"scope": ""},
    {"pattern": "x{4294967296}"}, {"rule": "Never compare\udc85partial months."}, {"fix": "a\udcffb"},
    {"pattern": "a\udc85"}])  # argv holds bytes that are not UTF-8 as lone surrogates
def test_add_rejects_unusable_arguments(project, capsys, change):
    code, out = add(project, capsys, **change)
    assert code == 2 and out is None and not (project / RULES).exists()


def test_pattern_round_trips_through_backticks(project, capsys):
    findings = project / "deliveries/inv/pkg/draft/findings.md"
    findings.write_text("Uses `orders_view` here.\nnone of these\n")
    add(project, capsys, area="code", pattern="`[a-z_]+`")
    add(project, capsys, area="code", pattern="none")
    assert "- Pattern: ``[a-z_]+``\n" in (project / RULES).read_text()
    rows = run(project, capsys, "review-rules", "check", "inv", "pkg")[1]["rules"]
    assert [(r["status"], [m["line"] for m in r.get("matches", [])]) for r in rows] == [
        ("matched", [1]), ("matched", [2])]


DECK = ("# Orders\n\nOctober to the 12th.\n\n## Answer\n\n- Sales rose in the partial month.\n\n## Findings\n\n"
        "### Sales rose 4% in October\n\n- The partial month rose.\n- Returns fell in the partial month.\n"
        "- The partial month is short.\n\n### Returns fell\n\n- Returns fell.\n")


def test_slide_scope_lists_one_entry_per_slide(project, capsys):
    # One wording rule gives one verdict per slide: three bullets on one slide are one entry with three lines.
    draft = project / "deliveries/inv/pkg/draft"
    (draft / "findings.md").write_text(DECK)
    (draft / "methodology-note.md").write_text("# How we measured\n\nThe partial month ends on the 12th.\n\n"
                                               "## Method\n\nNo partial month is compared.\n")
    code, out = add(project, capsys, pattern="partial month", scope="slide")
    assert code == 0 and out["added"] == "R-periods-001"
    code, out = run(project, capsys, "review-rules", "check", "inv", "pkg")
    assert code == 0 and out["problems"] == []
    assert out["rules"] == [{"id": "R-periods-001", "severity": "error", "status": "matched", "scope": "slide",
                             "matches": [
        {"file": "findings.md", "heading": "Answer", "line": 5, "lines": [
            {"line": 7, "text": "- Sales rose in the partial month."}]},
        {"file": "findings.md", "heading": "Sales rose 4% in October", "line": 11, "lines": [
            {"line": 13, "text": "- The partial month rose."},
            {"line": 14, "text": "- Returns fell in the partial month."},
            {"line": 15, "text": "- The partial month is short."}]},
        {"file": "methodology.md", "heading": "Sales rose 4% in the partial month of October", "line": 3, "lines": [
            {"line": 3, "text": "### Sales rose 4% in the partial month of October"}]},
        {"file": "methodology-note.md", "heading": "How we measured", "line": 1, "lines": [
            {"line": 3, "text": "The partial month ends on the 12th."}]},
        {"file": "methodology-note.md", "heading": "Method", "line": 5, "lines": [
            {"line": 7, "text": "No partial month is compared."}]}]}]


def test_slide_scope_reads_sections_as_they_render(project, capsys):
    # A # line in fenced code opens no section; text before the first heading is its own entry with no heading;
    # a line holding another break is not split, so every line is numbered as grep -n numbers it.
    draft = project / "deliveries/inv/pkg/draft"
    (draft / "findings.md").write_text("partial month first\n\n# Orders\n\n```\n# partial month in code\n```\n\n"
                                       "Intro\u2028pasted\n\n## Answer\n\n- partial month again\n")
    add(project, capsys, pattern="partial month", scope="slide")
    matches = run(project, capsys, "review-rules", "check", "inv", "pkg")[1]["rules"][0]["matches"]
    assert [(m["file"], m["heading"], m["line"], [line["line"] for line in m["lines"]]) for m in matches] == [
        ("findings.md", None, 1, [1]), ("findings.md", "Orders", 3, [6]), ("findings.md", "Answer", 11, [13]),
        ("methodology.md", "Sales rose 4% in the partial month of October", 3, [3])]
    # Blank lines before the first heading, or a file that is one blank line, are still that first entry.
    (draft / "methodology.md").unlink()
    add(project, capsys, pattern=r"^\s*$", scope="slide")
    for text, expected in [("\n", [("findings.md", None, 1, [1])]), ("\r\n", [("findings.md", None, 1, [1])]),
                           ("\ufeff\n", [("findings.md", None, 1, [1])]),
                           ("\n\n# Orders\n", [("findings.md", None, 1, [1, 2])])]:
        (draft / "findings.md").write_text(text, newline="")
        matches = run(project, capsys, "review-rules", "check", "inv", "pkg")[1]["rules"][1]["matches"]
        assert [(m["file"], m["heading"], m["line"], [line["line"] for line in m["lines"]])
                for m in matches] == expected
    # A #### heading, and a # line in a block quote, a list item, or an HTML comment, opens no slide: each
    # stays in the slide around it.
    (draft / "findings.md").write_text("# Orders\n\n#### Detail users\n\n> # Quoted users\n\n- # listed users\n\n"
                                       "<!--\n# hidden users\n-->\n\n## Answer\n\n- users again\n", newline="")
    add(project, capsys, pattern="users", scope="slide")
    matches = run(project, capsys, "review-rules", "check", "inv", "pkg")[1]["rules"][2]["matches"]
    assert [(m["file"], m["heading"], m["line"], [line["line"] for line in m["lines"]]) for m in matches] == [
        ("findings.md", "Orders", 1, [3, 5, 7, 10]), ("findings.md", "Answer", 13, [15])]


def test_document_scope_lists_one_entry_per_file(project, capsys):
    code, out = add(project, capsys, pattern="partial month", scope="document")
    assert code == 0 and "- Pattern: `partial month`\n- Scope: document\n- Fix: " in (project / RULES).read_text()
    (project / "deliveries/inv/pkg/draft/findings.md").write_text(DECK)
    row = run(project, capsys, "review-rules", "check", "inv", "pkg")[1]["rules"][0]
    assert row["scope"] == "document" and row["status"] == "matched"
    assert [(m["file"], [line["line"] for line in m["lines"]]) for m in row["matches"]] == [
        ("findings.md", [7, 13, 14, 15]), ("methodology.md", [3])]
    assert "heading" not in row["matches"][0]
    # A document entry lists at most 20 lines and counts the rest.
    (project / "deliveries/inv/pkg/draft/findings.md").write_text("".join(f"partial month {n}\n" for n in range(25)))
    entry = run(project, capsys, "review-rules", "check", "inv", "pkg")[1]["rules"][0]["matches"][0]
    assert len(entry["lines"]) == 20 and entry["more_lines"] == 5
    # Line scope, written or left out, lists lines as before, and a check row names no scope.
    add(project, capsys, pattern="partial month 3", scope="line")
    add(project, capsys, pattern="partial month 4")
    text = (project / RULES).read_text()
    assert "- Pattern: `partial month 3`\n- Scope: line\n" in text and "`partial month 4`\n- Fix" in text
    rows = run(project, capsys, "review-rules", "check", "inv", "pkg")[1]["rules"][1:]
    assert [(r.get("scope"), [m["line"] for m in r["matches"]]) for r in rows] == [(None, [4]), (None, [5])]


@pytest.mark.parametrize("value, problem", [
    ("line", None), ("slide", None), ("document", None), ("slide  ", None),
    ("Slide", "unknown scope 'Slide'; use line, slide, or document"),
    ("slides", "unknown scope 'slides'; use line, slide, or document"),
    ("per slide", "unknown scope 'per slide'; use line, slide, or document"),
    ("`slide`", "unknown scope '`slide`'; use line, slide, or document"),
    ("none", "unknown scope 'none'; use line, slide, or document"),
    ("", "unknown scope ''; use line, slide, or document")])
def test_scope_field_accepted_and_refused_forms(project, capsys, value, problem):
    # Scope is optional; when present it is exactly line, slide, or document. Anything else is a problem:
    # check exits 1 with the rule unchecked, and add refuses until it is repaired, as for other fields.
    path = project / RULES
    path.parent.mkdir(parents=True)
    path.write_text("# Review rules\n\n## R-periods-001\n\n- Severity: error\n- Rule: r\n- Pattern: `partial`\n"
                    f"- Scope: {value}\n- Fix: f\n")
    before = path.read_text()
    code, out = run(project, capsys, "review-rules", "check", "inv", "pkg")
    if problem is None:
        assert code == 0 and out["problems"] == [] and out["rules"][0]["status"] == "matched"
        assert add(project, capsys)[1]["added"] == "R-periods-002"
        return
    assert code == 1 and out["problems"] == [{"rule": "R-periods-001", "problem": problem}]
    assert out["rules"] == [{"id": "R-periods-001", "severity": "error", "status": "unchecked"}]
    code, out = add(project, capsys)
    assert code == 1 and out["added"] is None and path.read_text() == before
    path.write_text(before.replace(f"- Scope: {value}\n", "- Scope: slide\n"))
    assert add(project, capsys)[1]["added"] == "R-periods-002"


def test_repeated_scope_line_is_reported(project, capsys):
    path = project / RULES
    path.parent.mkdir(parents=True)
    path.write_text("# Review rules\n\n## R-periods-001\n\n- Severity: error\n- Rule: r\n- Pattern: none\n"
                    "- Scope: slide\n- Scope: line\n- Fix: f\n")
    code, out = run(project, capsys, "review-rules", "check", "inv", "pkg")
    assert code == 1 and out["problems"] == [{"rule": "R-periods-001", "line": 9, "problem": "repeated Scope line"}]


def test_add_refuses_without_the_users_yes(project, capsys):
    code, out = add(project, capsys, confirmed=False)
    assert code == 1 and out["added"] is None and "ask the user first" in out["refused"]
    assert "--confirmed" in out["refused"] and not (project / RULES).exists()
    assert add(project, capsys)[1]["added"] == "R-periods-001"


def other_package(project):
    draft = project / "deliveries/inv/other/draft"
    draft.mkdir(parents=True)
    (draft / "findings.md").write_text("# Other\n\n- Returns fell 1,240 orders.\n")
    (draft / "methodology.md").write_text("# Methodology\n")
    return draft


def test_package_rule_holds_for_its_package_alone(project, capsys):
    other_package(project)
    add(project, capsys)
    code, out = add(project, capsys, area="wording", scope="slide", package="inv/pkg")
    assert code == 0 and out["added"] == "R-wording-001"
    assert "- Pattern: none\n- Scope: slide\n- Package: inv/pkg\n- Fix: " in (project / RULES).read_text()
    code, out = run(project, capsys, "review-rules", "check", "inv", "pkg")
    assert code == 0 and [(r["id"], r.get("package")) for r in out["rules"]] == [
        ("R-periods-001", None), ("R-wording-001", "inv/pkg")]
    code, out = run(project, capsys, "review-rules", "check", "inv", "other")
    assert code == 0 and [r["id"] for r in out["rules"]] == ["R-periods-001"]

    before = (project / RULES).read_text()
    code, out = add(project, capsys, package="inv/absent")
    assert code == 1 and out["refused"].startswith("no package at deliveries/inv/absent")
    for value in ("pkg", "inv/pkg/extra", "../pkg", "inv/"):
        assert add(project, capsys, package=value)[0] == 2, value
    assert (project / RULES).read_text() == before

    # A typo in the field never hides the rule: it is a problem, and the rule holds for every package.
    (project / RULES).write_text(before.replace("- Package: inv/pkg", "- Package: inv pkg"))
    code, out = run(project, capsys, "review-rules", "check", "inv", "other")
    assert code == 1 and [r["id"] for r in out["rules"]] == ["R-periods-001", "R-wording-001"]
    assert out["problems"] == [{"rule": "R-wording-001", "problem": "Package 'inv pkg' is not "
                                                                    "<investigation>/<package>"}]


def test_add_warns_on_a_number_a_draft_states(project, capsys):
    other_package(project)
    code, out = add(project, capsys, rule="Say that sales rose 4% in October.", fix="Write 1240.0 orders.")
    assert code == 0 and out["added"] == "R-periods-001"
    assert [w.split(",")[0] for w in out["warnings"]] == [
        "the rule names 4", "the rule names 1240.0"]
    assert "deliveries/inv/pkg/draft/findings.md:3 also states" in out["warnings"][0]
    assert "deliveries/inv/other/draft/findings.md:3 also states" in out["warnings"][1]
    assert "reword it in place with the user" in out["warnings"][0]
    # A package rule is compared with that package's draft alone.
    code, out = add(project, capsys, rule="Never say 4% here.", fix="Write 1240.0 orders.", package="inv/other")
    assert code == 0 and [w.split(",")[0] for w in out["warnings"]] == ["the rule names 1240.0"]
    assert add(project, capsys, rule="Name every month in full.", fix="Spell out the month.")[1]["warnings"] == []
    (project / "deliveries/inv/other/draft/methodology-note.md").mkdir()
    out = add(project, capsys, rule="Name the 7 regions.", fix="List them.")[1]
    assert out["added"] and len(out["warnings"]) == 1
    assert out["warnings"][0].startswith("deliveries/inv/other/draft/methodology-note.md not read for numbers")


def test_another_packages_rule_leaves_a_review_current(project, capsys):
    other_package(project)
    add(project, capsys)
    record(project, capsys, CLEAN)
    reviewed = (project / "deliveries/inv/pkg/review/snapshot/review-rules.md").read_bytes()
    add(project, capsys, area="wording", package="inv/other")
    assert show(project, capsys)[1]["status"] == "current"
    path = project / RULES
    path.write_text(path.read_text().replace("- Package: inv/other\n", "- Package: inv/other\n- Scope: slide\n"))
    assert show(project, capsys)[1]["status"] == "current"
    add(project, capsys, area="numbers")  # another rule after it, for every package
    out = show(project, capsys)[1]
    assert out["status"] == "stale" and out["changed"] == [RULES]
    assert "+## R-numbers-001" in out["diff"] and "R-wording-001" not in out["diff"]
    record(project, capsys, "R-periods-001 pass\nR-numbers-001 pass\nreview: clean\n")
    snap = (project / "deliveries/inv/pkg/review/snapshot/review-rules.md").read_bytes()
    assert b"R-wording-001" not in snap and snap.startswith(reviewed.rstrip(b"\n"))
    add(project, capsys, area="wording", package="inv/pkg")
    assert show(project, capsys)[1]["status"] == "stale"
    record(project, capsys, "R-periods-001 pass\nR-numbers-001 pass\nR-wording-002 pass\nreview: clean\n")
    # A file with problems is read whole, so any change to it counts.
    path.write_text(path.read_text() + "- Rule: stray\n")
    assert show(project, capsys)[1]["status"] == "stale"


def test_a_rule_file_with_no_rule_for_the_package_reads_as_absent(project, capsys):
    # No rule file, then one holding only another package's rule: the review stays current.
    other_package(project)
    record(project, capsys, CLEAN)
    add(project, capsys, area="wording", package="inv/other")
    assert show(project, capsys)[1]["status"] == "current"
    assert not (project / "deliveries/inv/pkg/review/snapshot/review-rules.md").exists()
    # The diff of the filtered file says its line numbers count only this package's rules.
    add(project, capsys, area="numbers")
    out = show(project, capsys)[1]
    assert out["status"] == "stale" and out["changed"] == [RULES]
    assert f"+++ {RULES} without rules kept for another package\n" in out["diff"]


def test_package_and_release_invoke_the_read_only_review():
    package = (SKILLS / "awb-package/SKILL.md").read_text()
    release = (SKILLS / "awb-release/SKILL.md").read_text()
    brief = (SKILLS / "awb-package/references/review.md").read_text()
    agents = (SKILLS / "awb-init/assets/workbench/AGENTS.md").read_text()

    assert "](references/review.md)" in package
    assert package.index("## 5. Review") < package.index("## 6. Check") < package.index("check-draft <investigation>")
    assert "](../awb-package/references/review.md)" in release
    assert release.index("## 2. Review") < release.index("## 3. Release")
    assert (SKILLS / "awb-release" / "../awb-package/references/review.md").resolve().is_file()

    for tool in ("`Read`", "`Grep`", "`Glob`", "`Bash`"):
        assert tool in brief
    assert "never fix them, and change no file" in brief
    # The boundary is no command that writes, so a host that reads files through a shell can still read.
    assert "Run no command that writes: the only `awb.py` commands you run are " \
           "`python3 src/awb.py review-rules check <investigation> <package>` and, for a scoped review, " \
           "`python3 src/awb.py review-receipt show <investigation> <package>`, which write nothing" in brief
    # In Claude Code the reviewer takes the awb MCP read tool when the session has it, the shell otherwise.
    assert "When the session has the awb MCP `read` tool, the reviewer runs `review-rules` and `review-receipt` " \
           "through it, with Bash `python3 src/awb.py ...` as the fallback." in brief
    assert "read-only commands such as `cat`, `sed -n`, and `rg` are reads" in brief
    assert "run only" not in brief.lower()
    assert "one line per rule" in brief and "In Codex" in brief
    # The writer reviews its own draft only where the host has no subagents; Codex starts one too.
    assert "so the agent that wrote the draft does not review it" in brief
    assert "start a fresh subagent all the same" in brief
    assert "Only in a host with no subagents, follow **Brief** yourself, changing no file and running no "\
           "command that writes" in brief
    assert "a fresh subagent, limited to read tools" in package and "**Launch**" in package
    assert "review-rules add --confirmed --area" in brief
    assert "foundation/review-rules.md" in agents and "`awb-package`" in agents
    # The last line counts every kind of problem, so it never says clean while one blocks.
    assert "`review: clean` when there is no violation, no narrative problem, and the command exited 0" in brief
    assert "`review: <v> violations (<e> error), <n> narrative problems, <c> command problems`" in brief
    assert "reports no `error` violation and no command problem" in brief
    assert "releasing only once a review is passed" in release
    assert "its `review` row is `current`" in package and "`stale`" in brief and "`stale`" in release
    assert "whether its disposition is `omit`" in brief
    assert "later drafts could repeat" in brief and "later drafts could repeat" in agents

    cli = load(SKILLS / "awb-init/assets/awb_cli.py", "awb_cli_commands")
    assert cli.COMMANDS["review-rules"][:2] == ("packaging/draft.py", "cli_review_rules")


# ---------------------------------------------------------------- review receipt

DRAFT = "deliveries/inv/pkg/draft"
RECEIPT = "deliveries/inv/pkg/review/receipt.json"
CLEAN = "R-periods-001 pass\nreview: clean\n"
FLAGS = [{"finding": "F1", "reason": "dates corrected", "represented_in": ["chart 1"], "disposition": "none"}]
WARNING_AND_NARRATIVE = (
    'R-wording-001 violation warning findings.md:5 "users"\n'
    'narrative methodology.md:5 "to the 12th" does not say which month\n'
    "review: 1 violations (0 error), 1 narrative problems, 0 command problems\n")
ACCEPTED = ['findings.md:5 "users": the audience calls them users',
            'methodology.md:5 "to the 12th": the user says the slide names the month']


def draft_module(project):
    return load(project / "src/packaging/draft.py", "draft_receipt")


def record(project, capsys, report, kind="full", accept=(), first=True):
    """Record a report as review.md says: as it returns, then, with acceptances, again with --accept."""
    path = project.parent / f"report-{project.name}.txt"
    path.write_text(report)
    argv = ["review-receipt", "record", "inv", "pkg", "--kind", kind, "--report", str(path)]
    if accept and first:
        assert run(project, capsys, *argv)[0] == 0
    return run(project, capsys, *argv, *[f"--accept={text}" for text in accept])


def show(project, capsys):
    return run(project, capsys, "review-receipt", "show", "inv", "pkg")


def with_manifest(project, flags=FLAGS):
    (project / DRAFT / "manifest.json").write_text(json.dumps({"revalidation_flags": flags}))


def test_receipt_after_a_clean_review_matches_until_what_it_read_changes(project, capsys):
    assert show(project, capsys) == (0, {"status": "none", "kind": None, "recorded_at": None, "accepted": [],
                                         "report": None, "changed": [], "diff": "", "diff_cut": 0, "errors": []})
    with_manifest(project)
    add(project, capsys)
    code, out = record(project, capsys, CLEAN)
    assert code == 0 and out == {"recorded": True, "receipt": RECEIPT, "kind": "full", "passed": True,
                                 "accepted": []}
    receipt = json.loads((project / RECEIPT).read_text())
    assert receipt["report"] == CLEAN and receipt["passed"] is True and receipt["accepted"] == []
    assert re.fullmatch(r"[0-9a-f]{64}", receipt["fingerprint"]) and receipt["kind"] == "full"
    before = snapshot(project)
    code, out = show(project, capsys)
    assert code == 0 and out["status"] == "current" and out["changed"] == [] and out["diff"] == ""
    assert out["report"] == CLEAN and out["kind"] == "full" and out["recorded_at"] == receipt["recorded_at"]
    assert snapshot(project) == before  # show writes nothing

    rules = project / RULES
    edits = {
        "findings.md": (project / DRAFT / "findings.md", "- Up on September.", "- Up on August."),
        "methodology.md": (project / DRAFT / "methodology.md", "October to the 12th.", "October to the 13th."),
        "foundation/review-rules.md": (rules, "- Rule: Compare only complete months.", "- Rule: Compare only full months."),
    }
    for name, (path, old, new) in edits.items():
        original = path.read_text()
        path.write_text(original.replace(old, new))
        code, out = show(project, capsys)
        assert code == 0 and out["status"] == "stale" and out["changed"] == [name], name
        # The diff runs from what the review read to the file now, labelled, with the current line numbers.
        label = f"{RULES} without rules kept for another package" if name == RULES else f"{DRAFT}/{name}"
        assert f"--- reviewed {label}\n+++ {label}\n" in out["diff"] and f"-{old}" in out["diff"]
        assert f"+{new}" in out["diff"]
        line = path.read_text().splitlines().index(new) + 1
        assert re.search(rf"^@@ -\d+(?:,\d+)? \+{max(line - 3, 1)},", out["diff"], re.MULTILINE), out["diff"]
        path.write_text(original)
        assert show(project, capsys)[1]["status"] == "current"

    note = project / DRAFT / "methodology-note.md"
    note.write_text("# How we worked\n")
    out = show(project, capsys)[1]
    assert out["status"] == "stale" and out["changed"] == ["methodology-note.md"]
    assert f"+++ {DRAFT}/methodology-note.md\n" in out["diff"] and "+# How we worked" in out["diff"]
    note.unlink()

    with_manifest(project, [{**FLAGS[0], "represented_in": ["chart 1", "Answer slide"]}])
    out = show(project, capsys)[1]
    assert out["status"] == "stale" and out["changed"] == ["revalidation_flags"]
    assert f"+++ {DRAFT}/manifest.json revalidation_flags\n" in out["diff"] and '+      "Answer slide"' in out["diff"]


@pytest.mark.parametrize("disposition, status", [
    ("release_with_caveat", "current"), ("revalidate", "current"), ("omit", "stale")])
def test_only_a_disposition_to_or_from_omit_makes_a_review_stale(project, capsys, disposition, status):
    with_manifest(project)
    record(project, capsys, CLEAN)
    with_manifest(project, [{**FLAGS[0], "disposition": disposition}])
    assert show(project, capsys)[1]["status"] == status
    # The rest of the manifest is not what a review reads: an inventory rewrite leaves it current.
    with_manifest(project, [{**FLAGS[0], "disposition": "omit"}])
    record(project, capsys, CLEAN)
    path = project / DRAFT / "manifest.json"
    path.write_text(json.dumps({**json.loads(path.read_text()), "inventory": [{"path": "x"}], "revised_at": "t"}))
    assert show(project, capsys)[1]["status"] == "current"
    with_manifest(project, [{**FLAGS[0], "disposition": "none"}])
    assert show(project, capsys)[1]["changed"] == ["revalidation_flags"]


def test_failed_review_is_recorded_and_shows_failed(project, capsys):
    report = 'R-periods-001 violation error findings.md:3 "partial month"\n' \
             "review: 1 violations (1 error), 0 narrative problems, 0 command problems\n"
    code, out = record(project, capsys, report)
    assert code == 0 and out["recorded"] and out["passed"] is False
    code, out = show(project, capsys)
    assert code == 0 and out["status"] == "failed" and out["report"] == report and out["changed"] == []
    # A repair makes it stale, which a scoped review against it settles.
    path = project / DRAFT / "findings.md"
    path.write_text(path.read_text().replace("partial month of ", ""))
    assert show(project, capsys)[1]["status"] == "stale"
    code, out = record(project, capsys, "R-periods-001 pass\nreview (scoped): clean\n", kind="scoped")
    assert code == 0 and out["passed"] and show(project, capsys)[1] | {"recorded_at": None, "report": None} == {
        "status": "current", "kind": "scoped", "recorded_at": None, "accepted": [], "report": None,
        "changed": [], "diff": "", "diff_cut": 0, "errors": []}


def test_accepted_narrative_problem_is_recorded_with_its_reason(project, capsys):
    code, out = record(project, capsys, WARNING_AND_NARRATIVE, accept=ACCEPTED)
    assert code == 0 and out["passed"] is True and out["accepted"] == ACCEPTED
    assert json.loads((project / RECEIPT).read_text())["accepted"] == ACCEPTED
    out = show(project, capsys)[1]
    assert out["status"] == "current" and out["accepted"] == ACCEPTED
    # Every warning violation and narrative problem needs one acceptance: fewer or more do not pass.
    for accept in (ACCEPTED[:1], ACCEPTED + ["findings.md:6 \"x\": a third"]):
        code, out = record(project, capsys, WARNING_AND_NARRATIVE, accept=accept)
        assert code == 0 and out["passed"] is False and show(project, capsys)[1]["status"] == "failed"


@pytest.mark.parametrize("report", [
    'R-periods-001 violation error findings.md:3 "partial month"\n'
    "review: 1 violations (1 error), 0 narrative problems, 0 command problems\n",
    "command failed: no draft\nreview: 0 violations (0 error), 0 narrative problems, 1 command problems\n"])
def test_an_error_violation_or_command_problem_cannot_be_accepted(project, capsys, report):
    code, out = record(project, capsys, report, accept=['findings.md:3 "partial month": the user accepts it'])
    assert code == 0 and out["passed"] is False


@pytest.mark.parametrize("report, kind, refusal", [
    ("", "full", "the report is empty"),
    ("R-periods-001 pass\nLooks good to me.\n", "full", "the report's last line is not"),
    ("review: 2 violations, 0 narrative problems\n", "full", "the report's last line is not"),
    ("review: clean\nThanks!\n", "full", "the report's last line is not"),
    ("review (scoped): clean\n", "full", "--kind full does not match the report's last line, which opens "
                                         "review (scoped):"),
    ("review: clean\n", "scoped", "--kind scoped does not match the report's last line, which opens review:"),
    ("review: 1 violations (2 error), 0 narrative problems, 0 command problems\n", "full", "more error"),
    ('R-periods-001 violation error findings.md:3 "partial month"\nreview: clean\n', "full", "more than its"),
    ('R-wording-001 violation warning findings.md:5 "users"\n'
     "review: 1 violations (1 error), 0 narrative problems, 0 command problems\n", "full", "more than its"),
    ('narrative findings.md:3 "x" overstated\nnarrative findings.md:4 "y" overstated\n'
     "review: 0 violations (0 error), 1 narrative problems, 0 command problems\n", "full", "more than its"),
    # Rows in backticks or numbered count, as a last line in backticks is read.
    ('`R-periods-001 violation error findings.md:3 "partial month"`\n`review: clean`\n', "full", "more than its"),
    ('1. R-periods-001 violation error findings.md:3 "partial month"\nreview: clean\n', "full", "more than its"),
    ('2) narrative findings.md:3 "x" overstated\nreview: clean\n', "full", "more than its"),
])
def test_unusable_report_is_refused_and_writes_nothing(project, capsys, report, kind, refusal):
    before = snapshot(project)
    code, out = record(project, capsys, report, kind=kind)
    assert code == 1 and out["recorded"] is False and refusal in out["refused"]
    assert snapshot(project) == before
    # A refusal leaves an earlier record as it was.
    record(project, capsys, CLEAN)
    before = snapshot(project)
    assert record(project, capsys, report, kind=kind)[0] == 1 and snapshot(project) == before


def test_clean_review_takes_no_acceptance(project, capsys):
    code, out = record(project, capsys, CLEAN, accept=['findings.md:3 "x": no reason'], first=False)
    assert code == 1 and "nothing to accept" in out["refused"] and not (project / RECEIPT).exists()


@pytest.mark.parametrize("last, passed", [
    ("`review: clean`", True),
    ("review: clean.", True),
    ("review: 1 violation (0 errors), 1 narrative problem, 0 command problems", True),
    ("review: 1 violations (1 error), 1 narrative problems, 0 command problems", False),
    ("review: 0 violations (0 error), 2 narrative problems, 0 command problems", False),
])
def test_summary_line_probes(project, capsys, last, passed):
    # Singular words, backticks, and a closing period read the same; counts decide passed. The rows above it
    # may be listed with bullets and still count.
    severity = "error" if "(1 error)" in last else "warning"
    body = f"- R-wording-001 violation {severity} findings.md:5 \"users\"\n" if "1 violation" in last else ""
    accept = ACCEPTED if "1 narrative" in last else []
    code, out = record(project, capsys, body + last + "\n", accept=accept)
    assert code == 0 and out["passed"] is passed


def test_snapshot_sits_beside_the_draft_and_is_replaced(project, capsys):
    with_manifest(project)
    record(project, capsys, CLEAN)
    snap = project / "deliveries/inv/pkg/review/snapshot"
    assert sorted(p.name for p in snap.iterdir()) == ["findings.md", "methodology.md", "revalidation_flags.json"]
    assert (snap / "findings.md").read_text() == FINDINGS
    assert json.loads((snap / "revalidation_flags.json").read_text()) == [
        {"finding": "F1", "reason": "dates corrected", "represented_in": ["chart 1"], "omit": False}]
    assert not (project / DRAFT / "review").exists() and not (project / DRAFT / "receipt.json").exists()
    add(project, capsys)
    (project / DRAFT / "methodology-note.md").write_text("# Note\n")
    record(project, capsys, CLEAN)
    assert sorted(p.name for p in snap.iterdir()) == ["findings.md", "methodology-note.md", "methodology.md",
                                                      "revalidation_flags.json", "review-rules.md"]
    (project / DRAFT / "methodology-note.md").unlink()
    record(project, capsys, CLEAN)
    assert not (snap / "methodology-note.md").exists() and show(project, capsys)[1]["status"] == "current"


def test_record_reads_the_report_from_stdin_and_checks_arguments(project, capsys, monkeypatch):
    monkeypatch.setattr(sys, "stdin", __import__("io").StringIO(CLEAN))
    code, out = run(project, capsys, "review-receipt", "record", "inv", "pkg", "--kind", "full", "--report", "-")
    assert code == 0 and out["passed"] and json.loads((project / RECEIPT).read_text())["report"] == CLEAN
    before = snapshot(project)
    for argv in (["--kind", "partial", "--report", "-"], ["--kind", "full"],
                 ["--kind", "full", "--report", str(project / "absent.txt")],
                 ["--kind", "full", "--report", "-", "--accept", "  "],
                 ["--kind", "full", "--report", "-", "--accept", "two\nlines"]):
        assert run(project, capsys, "review-receipt", "record", "inv", "pkg", *argv)[0] == 2, argv
    assert snapshot(project) == before
    code, out = run(project, capsys, "review-receipt", "record", "inv", "absent", "--kind", "full", "--report", "-")
    assert code == 1 and out["refused"] == "no draft at deliveries/inv/absent/draft; create it with awb-package"


def test_brief_change_makes_a_review_stale(project, capsys):
    brief = project / "investigations/inv/brief.md"
    brief.parent.mkdir(parents=True)
    brief.write_text("# Investigation brief\n\n## Audience\n\nThe board.\n")
    record(project, capsys, CLEAN)
    snap = project / "deliveries/inv/pkg/review/snapshot"
    assert (snap / "brief.md").read_text() == brief.read_text()
    assert show(project, capsys)[1]["status"] == "current"
    brief.write_text(brief.read_text() + "Methods note length: about 500 words\n")
    out = show(project, capsys)[1]
    assert out["status"] == "stale" and out["changed"] == ["brief.md"]
    assert "--- reviewed investigations/inv/brief.md\n+++ investigations/inv/brief.md\n" in out["diff"]
    assert "+Methods note length: about 500 words" in out["diff"]


def test_show_reports_an_unreadable_receipt_and_bounds_the_diff(project, capsys):
    # A long prior report and typographic punctuation, which JSON prints six characters wide, still leave the
    # printed line within one read result, with diff_cut counting what was cut.
    report = "".join(f'- R-wording-{n:03} pass \u201cquoted\u201d \u2014 dash\n' for n in range(60)) + "review: clean\n"
    record(project, capsys, report)
    path = project / DRAFT / "findings.md"
    path.write_text(FINDINGS + "".join(f"- \u201cAdded\u201d line {n} \u2014 with \"words\".\n" for n in range(600)))
    out = show(project, capsys)[1]
    assert out["status"] == "stale" and out["diff_cut"] > 0 and out["report"] == report
    assert out["diff"].endswith(f"[... {out['diff_cut']} characters cut; read each changed file in full ...]\n")
    assert draft_module(project)._READ_LIMIT - 400 < len(json.dumps(out)) <= draft_module(project)._READ_LIMIT
    cut = out["diff"].rsplit("[...", 1)[0]
    assert cut.endswith("\n") and len(cut) + out["diff_cut"] == len(show_full_diff(project))
    (project / RECEIPT).write_text("not json")
    code, out = show(project, capsys)
    assert code == 1 and out["status"] == "none" and out["errors"][0].startswith(RECEIPT)
    (project / RECEIPT).write_text(json.dumps({"kind": "full"}))
    code, out = show(project, capsys)
    assert code == 1 and out["status"] == "none" and "not a review receipt" in out["errors"][0]


def show_full_diff(project):
    """The whole diff show would give with no bound."""
    module = draft_module(project)
    module._READ_LIMIT = 10 ** 9
    return module.review_receipt(project, "inv", "pkg")["diff"]


def test_acceptance_amends_the_recorded_review_and_refuses_after_a_change(project, capsys):
    code, out = record(project, capsys, WARNING_AND_NARRATIVE)
    assert code == 0 and out["passed"] is False
    before = snapshot(project)
    # An edit between the review and its acceptances is never folded into what the review read.
    path = project / DRAFT / "findings.md"
    path.write_text(FINDINGS + "- Churn doubled because of the price change.\n")
    code, out = record(project, capsys, WARNING_AND_NARRATIVE, accept=ACCEPTED, first=False)
    assert code == 1 and "--accept adds acceptances to the report already recorded" in out["refused"]
    assert "(show reports stale)" in out["refused"]
    assert show(project, capsys)[1]["changed"] == ["findings.md"]
    path.write_text(FINDINGS)
    assert snapshot(project) == before
    # Another report, or another kind, is not the recorded one.
    other = WARNING_AND_NARRATIVE.replace('"users"', '"customers"')
    code, out = record(project, capsys, other, accept=ACCEPTED, first=False)
    assert code == 1 and "for another report" in out["refused"] and snapshot(project) == before
    # Unchanged, only accepted and passed change; the snapshot and recorded_at stay the review's.
    receipt = json.loads((project / RECEIPT).read_text())
    code, out = record(project, capsys, WARNING_AND_NARRATIVE, accept=ACCEPTED, first=False)
    assert code == 0 and out["passed"] is True
    assert json.loads((project / RECEIPT).read_text()) == {**receipt, "passed": True, "accepted": ACCEPTED}
    assert {k: v for k, v in snapshot(project).items() if "/review/snapshot/" in k} == \
        {k: v for k, v in before.items() if "/review/snapshot/" in k}
    assert show(project, capsys)[1]["status"] == "current"


def test_scoped_record_needs_a_prior_record(project, capsys):
    code, out = record(project, capsys, "review (scoped): clean\n", kind="scoped")
    assert code == 1 and out["refused"] == "no recorded review to scope against; the review is full"
    assert not (project / RECEIPT).exists()
    record(project, capsys, CLEAN)
    assert record(project, capsys, "review (scoped): clean\n", kind="scoped")[1]["passed"] is True


def test_represented_results_evidence_is_what_the_review_read(project, capsys):
    evidence = project / "investigations/inv/evidence/r-001.json"
    evidence.parent.mkdir(parents=True)
    evidence.write_text('{\n  "checks": [{"name": "reconciliation", "outcome": "pass", "detail": "Totals agree"}]\n}\n')
    name = "investigations/inv/evidence/r-001.json"
    results = [{"result_id": "r-001", "evidence": name}, {"result_id": "x", "evidence": ["not a path"]}]
    (project / DRAFT / "manifest.json").write_text(json.dumps({"revalidation_flags": [], "results": results}))
    record(project, capsys, CLEAN)
    assert len(list((project / "deliveries/inv/pkg/review/snapshot/evidence").iterdir())) == 1
    assert show(project, capsys)[1]["status"] == "current"
    original = evidence.read_text()
    evidence.write_text(original.replace('"pass", "detail": "Totals agree"', '"fail", "detail": "Totals differ"'))
    out = show(project, capsys)[1]
    assert out["status"] == "stale" and out["changed"] == [name]
    assert f"--- reviewed {name}\n+++ {name}\n" in out["diff"] and "+" in out["diff"] and "Totals differ" in out["diff"]
    evidence.write_text(original)
    assert show(project, capsys)[1]["status"] == "current"
    # A result dropped from the manifest is a change too.
    (project / DRAFT / "manifest.json").write_text(json.dumps({"revalidation_flags": [], "results": []}))
    assert show(project, capsys)[1]["changed"] == [name]
