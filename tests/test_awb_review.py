# Kept cases:
# test_correction_becomes_a_numbered_rule: add creates foundation/review-rules.md with its header and R-<area>-001, numbers per area after every ID used, retired and hand-numbered ones included, and never renumbers earlier rules.
# test_next_review_reports_against_the_rule: check lists every rule in file order with matched lines from both narratives, no match, no pattern, and retired; matches are capped; nothing is written.
# test_check_without_rules_or_draft: no rule file reports none recorded and exits 0; a missing draft narrative is an error and exits 1.
# test_malformed_rule_file_is_reported_and_blocks_add: a bad heading, a repeated ID or field, missing fields, an unknown severity, and an unusable pattern (one overflowing included) are problems; check exits 1 with the rule unchecked; add refuses and writes nothing.
# test_broken_rule_section_is_reported_not_dropped: a rule under a malformed heading, or field lines outside a rule section, are problems; check exits 1 and add refuses, so no ID is reused.
# test_wrapped_field_line_is_reported: a line inside a rule section that is not a field, such as a wrapped Rule, is a problem rather than lost text.
# test_line_starting_with_hash_never_cuts_a_rule_short: after the first rule, a wrapped line starting with # or a heading that is not a rule's is a problem; check exits 1 and add refuses, so no rule is silently truncated.
# test_rule_file_lines_count_only_newlines: a U+2028, form feed, or lone carriage return in the rule file is a problem at its grep -n line and shifts no later line; add refuses; CRLF endings are no problem.
# test_match_lines_count_only_newlines: a U+2028, form feed, or lone carriage return in a narrative does not shift the reported line numbers away from grep -n's, and CRLF endings still match a pattern anchored with $.
# test_check_through_the_dispatcher_writes_nothing: run as a script with bytecode writes enabled, review-rules check leaves every project file, __pycache__ included, unchanged.
# test_add_to_an_empty_rule_file_writes_the_header: add to an empty rule file writes the header before the first rule.
# test_add_rejects_unusable_arguments: a bad area (one ending in a number included), a text split by any line break the parser recognizes or blank, an unknown severity, or a pattern that does not compile (an overflowing repeat included) exits 2 and writes nothing.
# test_pattern_round_trips_through_backticks: a pattern holding backticks, or the word none, is written in backticks and read back as the same expression.
# test_package_and_release_invoke_the_read_only_review: both skills link the review brief and run it before their final command; the brief has a fresh subagent review in every host with subagents, Codex included, and the writer review only where there are none; it limits the reviewer to read tools and the read-only command, asks one line per rule, ends with a summary line counting violations, narrative problems, and command problems, any of which blocks, defines when a review is stale, and with AGENTS.md says which corrections become rules.

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
        fix="Drop the partial month.", pattern=None):
    argv = ["review-rules", "add", "--area", area, "--severity", severity, "--rule", rule, "--fix", fix]
    return run(project, capsys, *argv, *(["--pattern", pattern] if pattern is not None else []))


def snapshot(root, *, caches=False):
    # In-process runs load src/awb.py through the test's own import, which may cache it; the dispatcher
    # itself writes no cache, which test_check_through_the_dispatcher_writes_nothing checks with caches.
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*")
            if p.is_file() and (caches or "__pycache__" not in p.parts)}


def test_correction_becomes_a_numbered_rule(project, capsys):
    code, out = add(project, capsys, pattern=r"(?i)partial month")
    assert code == 0 and out == {"added": "R-periods-001", "rules_file": RULES, "created": True, "rules": 1}
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
    assert {"rule": "R-periods-001", "problem": "repeated Rule line"} in problems
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


def test_wrapped_field_line_is_reported(project, capsys):
    path = project / RULES
    path.parent.mkdir(parents=True)
    path.write_text("# Review rules\n\n## R-periods-001\n\n- Severity: error\n- Rule: Never compare\n"
                    "  partial months.\n- Pattern: none\n- Fix: Drop it.\n")
    code, out = run(project, capsys, "review-rules", "check", "inv", "pkg")
    assert code == 1 and out["problems"] == [
        {"rule": "R-periods-001", "line": 7, "problem": "line is not a - Severity, Rule, Pattern, Fix, or Added field"}]


@pytest.mark.parametrize("tail, expected", [
    ("- Fix: Replace\n#hashtags with plain words.\n",
     [{"rule": "R-wording-001", "line": 8, "problem": "line is not a - Severity, Rule, Pattern, Fix, or Added field"}]),
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


def test_check_through_the_dispatcher_writes_nothing(project, capsys):
    add(project, capsys, pattern="partial month")
    before = snapshot(project, caches=True)
    env = {k: v for k, v in os.environ.items() if k != "PYTHONDONTWRITEBYTECODE"}
    result = subprocess.run([sys.executable, str(project / "src/awb.py"), "review-rules", "check", "inv", "pkg"],
                            cwd=project, env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["rules"][0]["status"] == "matched"
    assert snapshot(project, caches=True) == before


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
    {"pattern": "x{4294967296}"}])
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
    assert "Run only `python3 src/awb.py review-rules check <investigation> <package>`" in brief
    assert "one line per rule" in brief and "In Codex" in brief
    # The writer reviews its own draft only where the host has no subagents; Codex starts one too.
    assert "so the agent that wrote the draft does not review it" in brief
    assert "start a fresh subagent all the same" in brief
    assert "Only in a host with no subagents, follow **Brief** yourself" in brief
    assert "a fresh subagent, limited to read tools" in package and "**Launch**" in package
    assert "review-rules add --area" in brief
    assert "foundation/review-rules.md" in agents and "`awb-package`" in agents
    # The last line counts every kind of problem, so it never says clean while one blocks.
    assert "`review: clean` when there is no violation, no narrative problem, and the command exited 0" in brief
    assert "`review: <v> violations (<e> error), <n> narrative problems, <c> command problems`" in brief
    assert "no `error` violation, no narrative problem, and no command problem" in brief
    assert "An `error` violation, a narrative problem, or a command problem stops the release" in release
    assert "is passed and not stale" in package and "goes stale" in release
    assert "whether its disposition is `omit`" in brief
    assert "later drafts could repeat" in brief and "later drafts could repeat" in agents

    cli = load(SKILLS / "awb-init/assets/awb_cli.py", "awb_cli_commands")
    assert cli.COMMANDS["review-rules"][:2] == ("packaging/draft.py", "cli_review_rules")
