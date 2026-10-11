# Kept cases:
# test_show_prints_the_active_investigation: one call gives brief lines, rows, counts by status, numbered open items, and Last updated; template guidance reads "not recorded"; --investigation overrides; no active investigation exits 1 and an unknown name 2.
# test_run_rows_are_added_refreshed_and_flags_cleared: a new result gets a provisional row; an existing row keeps wording, status, and caveat notes; a flagged row becomes provisional with a history entry citing the prior commit; other bytes are untouched.
# test_finding_change_writes_history: a status or wording change appends a history entry with prior and new text and status, reason, and evidence commit; no change writes nothing; a flagged finding cannot be promoted.
# test_issue_next_and_done: issue and next add bullets; done removes by number or text, restoring the file; an ambiguous or missing match exits 1 and writes nothing; CRLF files keep CRLF.
# test_switch_keeps_the_pointer_form: switch rewrites only the pointer in its link, path, backticked, or slug form and prints the new view; a customized pointer exits 1 unwritten and an unknown investigation 2.
# test_malformed_records_write_nothing: missing or repeated sections and lines, a wrong table, a short row, or a missing history file exit 1 or raise, leaving every file byte for byte.
# test_parsers_read_written_files: collect_status and finding_rows read the files the state command and run.py's helper write.

from datetime import date
import importlib.util
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / ".agents/skills/awb-init/assets/workbench"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


provenance = load("awb_provenance_state", ".agents/skills/awb-init/assets/awb_provenance.py")
status = load("awb_status_state", ".agents/skills/awb-status/scripts/collect_status.py")

TODAY = "2026-10-11"
CHECKS = [{"name": "columns", "outcome": "fail", "detail": "Missing x."},
          {"name": "joins", "outcome": "not-applicable", "detail": "not assessed"},
          {"name": "values", "outcome": "pass", "detail": "Checked."}]
STATE = "investigations/churn/state.md"
HISTORY = "investigations/churn/history.md"


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True).stdout.strip()


def commit(root, message="work"):
    git(root, "add", "-A")
    git(root, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "commit.gpgsign=false",
        "commit", "-qm", message)


def read(root, path):
    return (root / path).read_bytes()


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*")
            if p.is_file() and ".git" not in p.parts}


def rows(*lines):
    return "| --- | --- | --- | --- |\n" + "".join(line + "\n" for line in lines)


@pytest.fixture
def project(tmp_path):
    readme = (TEMPLATES / "README.md").read_text().replace(
        "Active investigation: none", "Active investigation: [churn](investigations/churn/state.md)")
    (tmp_path / "README.md").write_text(readme)
    for name in ("churn", "pricing"):
        directory = tmp_path / "investigations" / name
        directory.mkdir(parents=True)
        for record in ("state.md", "history.md", "brief.md"):
            shutil.copyfile(TEMPLATES / "investigation" / record, directory / record)
    brief = tmp_path / "investigations/churn/brief.md"
    brief.write_text(brief.read_text()
                     .replace("State the question this investigation will answer.",
                              "Why did churn rise in Q3 among annual-plan customers?")
                     .replace("Record the decision this analysis will support, or state that its purpose is "
                              "exploratory.", "Decide whether to fund the retention offer. " + "x" * 200))
    state = tmp_path / STATE
    state.write_text(state.read_text().replace("<!-- use an ISO date -->", "2026-09-01").replace(
        "| --- | --- | --- | --- |\n", rows(
            "| Churn rose 3 points | [r1](evidence/r1.json) | supported | |",
            "| Renewal lag \\| grew | [r2](evidence/r2.json) | revalidation-needed (was supported) | Q-004 correction |",
            "| Early guess | [r0](evidence/r0.json) | superseded | |")))
    return tmp_path


def run(project, capsys, *argv):
    code = provenance.cli_state(project, list(argv))
    out = capsys.readouterr()
    return code, out.out, out.err


def test_show_prints_the_active_investigation(project, capsys):
    provenance.add_item(project, "churn", "Next steps", "Explore the shifts view", today=TODAY)
    code, out, _ = run(project, capsys)
    lines = out.splitlines()
    assert code == 0
    assert lines[0] == f"churn (Last updated: {TODAY})"
    assert lines[1] == "Question: Why did churn rise in Q3 among annual-plan customers?"
    assert lines[2].startswith("Purpose: Decide whether") and lines[2].endswith("…") and len(lines[2]) < 175
    assert lines[3] == "Audience: not recorded"
    assert lines[4] == "Findings: 1 supported, 1 revalidation-needed, 1 superseded"
    assert lines[5] == "| Churn rose 3 points | [r1](evidence/r1.json) | supported | |"
    assert lines[8:] == ["Unresolved issues: none", "Next steps:", "1. Explore the shifts view"]
    assert run(project, capsys, "--investigation", "pricing")[1].splitlines()[4] == "Findings: none"
    assert run(project, capsys, "--investigation", "absent")[0] == 2
    readme = project / "README.md"
    readme.write_text(readme.read_text().replace("[churn](investigations/churn/state.md)", "none"))
    code, out, err = run(project, capsys)
    assert code == 1 and not out and "no active investigation" in err


def test_run_rows_are_added_refreshed_and_flags_cleared(project):
    git(project, "init")
    (project / "investigations/churn/evidence").mkdir()
    (project / "investigations/churn/evidence/r2.json").write_text("{}\n")
    commit(project)
    head = git(project, "rev-parse", "HEAD")
    prior = provenance.evidence_commit(project, "churn", "r2")
    assert prior == head
    (project / "investigations/churn/evidence/r2.json").write_text('{"rerun": true}\n')
    assert provenance.evidence_commit(project, "churn", "r2") == f"uncommitted; last committed at {head}"
    assert provenance.evidence_commit(project, "churn", "r9") == "uncommitted"
    before = read(project, STATE).decode()

    added = provenance.record_finding(project, "churn", "r3", CHECKS, finding="Tenure | matters", today=TODAY)
    assert added == {"action": "added", "status": "provisional", "row":
                     r"| Tenure \| matters | [r3](evidence/r3.json) | provisional | "
                     "failed checks: columns; not assessed: joins |"}
    text = read(project, STATE).decode()
    assert text == before.replace("Last updated: 2026-09-01", f"Last updated: {TODAY}").replace(
        "| Early guess | [r0](evidence/r0.json) | superseded | |\n",
        "| Early guess | [r0](evidence/r0.json) | superseded | |\n" + added["row"] + "\n")
    placeholder = provenance.record_finding(project, "churn", "r4", [], today=TODAY)
    assert placeholder["row"].startswith("| <state the finding from r4> |")

    # An existing row keeps its wording, status, and notes; the checks' caveat is refreshed.
    lines = read(project, STATE).decode().replace(
        "| Churn rose 3 points | [r1](evidence/r1.json) | supported | |",
        "| Churn rose 3 points | [r1](evidence/r1.json) | supported | not assessed: nulls; joins: one table |")
    (project / STATE).write_text(lines)
    refreshed = provenance.record_finding(project, "churn", "r1", CHECKS[:1], finding="ignored", today=TODAY)
    assert refreshed["action"] == "refreshed"
    assert refreshed["row"] == ("| Churn rose 3 points | [r1](evidence/r1.json) | supported | "
                                "failed checks: columns; joins: one table |")
    assert read(project, HISTORY) == (TEMPLATES / "investigation/history.md").read_bytes()

    cleared = provenance.record_finding(project, "churn", "r2", CHECKS[2:], prior_commit=prior, today=TODAY)
    assert cleared == {"action": "flag cleared", "status": "provisional",
                       "row": r"| Renewal lag \| grew | [r2](evidence/r2.json) | provisional | |"}
    history = read(project, HISTORY).decode()
    entry = history[len((TEMPLATES / "investigation/history.md").read_text()):]
    assert entry == (f"\n### {TODAY} — r2 rerun clears its flag\n\n"
                     "- **Change or finding:** \"Renewal lag | grew\" (provisional).\n"
                     f"- **Evidence:** [r2](evidence/r2.json); prior evidence at commit {head}.\n"
                     "- **Reasoning or decision:** rerun for the flag: Q-004 correction.\n"
                     "- **Impact and caveats:** none.\n"
                     "- **Supersedes or revalidation link:** supersedes \"Renewal lag | grew\" "
                     "(revalidation-needed (was supported)).\n")


def test_finding_change_writes_history(project, capsys):
    git(project, "init")
    (project / "investigations/churn/evidence").mkdir()
    (project / "investigations/churn/evidence/r1.json").write_text("{}\n")
    commit(project)
    head = git(project, "rev-parse", "HEAD")
    code, out, _ = run(project, capsys, "finding", "r1", "--status", "superseded", "--text",
                       "Churn rose 2 points", "--reason", "The Q-004 correction removed duplicate cancellations.")
    day = date.today().isoformat()
    assert code == 0
    assert out == ("| Churn rose 2 points | [r1](evidence/r1.json) | superseded | |\n"
                   f"history.md: ### {day} — r1 reworded and set to superseded\n")
    entry = read(project, HISTORY).decode().split("\n### ")[-1]
    assert entry == (f"{day} — r1 reworded and set to superseded\n\n"
                     "- **Change or finding:** \"Churn rose 2 points\" (superseded).\n"
                     f"- **Evidence:** [r1](evidence/r1.json); prior evidence at commit {head}.\n"
                     "- **Reasoning or decision:** The Q-004 correction removed duplicate cancellations.\n"
                     "- **Impact and caveats:** none.\n"
                     "- **Supersedes or revalidation link:** supersedes \"Churn rose 3 points\" (supported).\n")
    assert f"Last updated: {day}" in read(project, STATE).decode()

    before = snapshot(project)
    code, out, _ = run(project, capsys, "finding", "r1", "--status", "superseded")
    assert code == 0 and out.startswith("unchanged: ") and snapshot(project) == before
    # A caveat note changes neither status nor wording, so history stays as it is.
    assert run(project, capsys, "finding", "r1", "--caveat", "joins: one table")[0] == 0
    assert read(project, HISTORY) == before[HISTORY]
    assert "| superseded | joins: one table |" in read(project, STATE).decode()

    before = snapshot(project)
    code, _, err = run(project, capsys, "finding", "r2", "--status", "supported")
    assert code == 1 and "rerun it with run.py" in err and snapshot(project) == before
    assert run(project, capsys, "finding", "r9", "--status", "supported")[0] == 1
    assert run(project, capsys, "finding", "r1")[0] == 2
    assert run(project, capsys, "finding", "r1", "--status", "done")[0] == 2
    assert snapshot(project) == before

    code, _, _ = run(project, capsys, "finding", "r2", "--status", "superseded")
    entry = read(project, HISTORY).decode().split("\n### ")[-1]
    assert code == 0 and "r2 set to superseded" in entry and "prior evidence uncommitted." in entry
    assert "- **Reasoning or decision:** not given." in entry


def test_issue_next_and_done(project, capsys):
    original = read(project, STATE)
    assert run(project, capsys, "issue", "Is the  Q3 dip\na data gap?")[1] == "added Unresolved issues item 1\n"
    assert run(project, capsys, "next", "Explore the shifts view")[1] == "added Next steps item 2\n"
    assert run(project, capsys, "next", "Explore the orders view")[1] == "added Next steps item 3\n"
    text = read(project, STATE).decode()
    assert "Keep this a short list.\n\n- Is the Q3 dip a data gap?\n\n## Next steps" in text
    assert text.endswith("Keep this a short list.\n\n- Explore the shifts view\n- Explore the orders view\n")

    before = snapshot(project)
    code, _, err = run(project, capsys, "done", "explore")
    assert code == 1 and "matches items 2, 3" in err and snapshot(project) == before
    assert run(project, capsys, "done", "nothing like it")[0] == 1
    assert run(project, capsys, "done", "7")[0] == 1
    assert snapshot(project) == before

    assert run(project, capsys, "done", "SHIFTS")[1] == "removed from Next steps: Explore the shifts view\n"
    assert run(project, capsys, "done", "1")[1] == "removed from Unresolved issues: Is the Q3 dip a data gap?\n"
    assert run(project, capsys, "done", "Explore the orders view")[0] == 0
    day = read(project, STATE).decode().split("Last updated: ")[1][:10]
    assert read(project, STATE) == original.replace(b"2026-09-01", day.encode())

    numbered = original.replace(b"Keep this a short list.\n\n## Next", b"Keep this a short list.\n\n1. First\n"
                                b"   continued\n\n## Next").replace(b"\n", b"\r\n")
    (project / STATE).write_bytes(numbered)
    provenance.add_item(project, "churn", "Unresolved issues", "Second", today=TODAY)
    assert b"1. First\r\n   continued\r\n2. Second\r\n\r\n## Next" in read(project, STATE)
    assert provenance.remove_item(project, "churn", "continued", today=TODAY) == ("Unresolved issues", "First continued")


@pytest.mark.parametrize("pointer, expected", [
    ("[churn](investigations/churn/state.md)", "[pricing](investigations/pricing/state.md)"),
    ("[Churn study](./investigations/churn/state.md)", "[pricing](./investigations/pricing/state.md)"),
    ("investigations/churn/state.md", "investigations/pricing/state.md"),
    ("`investigations/churn/state.md`", "`investigations/pricing/state.md`"),
    ("churn", "pricing"),
    ("none", "[pricing](investigations/pricing/state.md)"),
])
def test_switch_keeps_the_pointer_form(project, capsys, pointer, expected):
    readme = project / "README.md"
    text = readme.read_text().replace("[churn](investigations/churn/state.md)", pointer)
    readme.write_text(text)
    code, out, _ = run(project, capsys, "switch", "pricing")
    assert code == 0 and out.startswith("Active investigation now pricing (Last updated:")
    assert readme.read_text() == text.replace(f"Active investigation: {pointer}", f"Active investigation: {expected}")
    assert status.collect(project)["active"]["name"] == "pricing"
    code, out, _ = run(project, capsys, "switch", "pricing")
    assert code == 0 and out.startswith("Already active: pricing")

    assert run(project, capsys, "switch", "absent")[0] == 2
    readme.write_text(text.replace(f"Active investigation: {pointer}", "Active investigation: see the wiki"))
    before = snapshot(project)
    code, _, err = run(project, capsys, "switch", "pricing")
    assert code == 1 and "customized" in err and snapshot(project) == before


@pytest.mark.parametrize("record, old, new", [
    (STATE, "Last updated: 2026-09-01\n", ""),
    (STATE, "Last updated: 2026-09-01\n", "Last updated: 2026-09-01\nLast updated: 2026-09-02\n"),
    (STATE, "## Next steps", "## Later"),
    (STATE, "## Unresolved issues", "## Current findings"),
    (STATE, "| Finding | Evidence |", "| Result | Evidence |"),
    (STATE, "| Early guess | [r0](evidence/r0.json) | superseded | |", "| Early guess | [r0](evidence/r0.json) |"),
    (STATE, "[r0](evidence/r0.json)", "[r1](evidence/r1.json)"),  # two rows link r1: only r1 writes fail
    (HISTORY, None, None),
])
def test_malformed_records_write_nothing(project, capsys, record, old, new):
    path = project / record
    if old is None:
        path.unlink()
    else:
        text = path.read_text()
        assert old in text
        path.write_text(text.replace(old, new, 1))
    before = snapshot(project)
    commands = [["finding", "r1", "--status", "superseded"], ["finding", "r1", "--text", "x"]]
    if old == "[r0](evidence/r0.json)":
        commands += [["finding", "r1", "--caveat", "x"]]
    elif record == STATE:
        commands += [[], ["issue", "x"], ["next", "x"], ["done", "1"], ["switch", "pricing"]]
    for argv in commands:
        if argv[:1] == ["switch"]:  # switch reads the target's records, so break the target.
            shutil.copyfile(path, project / "investigations/pricing/state.md")
            before = snapshot(project)
        code, out, err = run(project, capsys, *argv)
        assert code == 1, argv
        assert len(err.strip().splitlines()) == 1 and not out, argv
        assert snapshot(project) == before, argv
    if record == STATE:
        with pytest.raises(provenance.StateError):
            provenance.record_finding(project, "churn", "r1", CHECKS)
        assert snapshot(project) == before


def test_parsers_read_written_files(project, capsys):
    provenance.record_finding(project, "churn", "r3", CHECKS, finding="Tenure | matters", today=TODAY)
    provenance.record_finding(project, "churn", "r2", CHECKS, today=TODAY)
    assert run(project, capsys, "finding", "r3", "--status", "supported", "--text", "Tenure | matters most")[0] == 0
    assert run(project, capsys, "issue", "Q3 coverage gap")[0] == 0
    assert run(project, capsys, "next", "Explore shifts")[0] == 0
    result = status.collect(project)
    assert not [u for u in result["uncertainties"] if u["path"] == STATE]
    active = result["active"]
    assert active["last_updated"] == read(project, STATE).decode().split("Last updated: ")[1][:10]
    assert active["counts"] == {"supported": 2, "provisional": 1, "superseded": 1}
    assert {"finding": r"Tenure \| matters most", "status": "supported",
            "reason": "failed checks: columns; not assessed: joins"} in active["findings"]
    assert "- Q3 coverage gap" in active["unresolved_issues"] and "- Explore shifts" in active["next_steps"]
    found = provenance.finding_rows(project / STATE)
    assert sorted(found) == ["r0", "r1", "r2", "r3"]
    assert found["r3"] == [r"| Tenure \| matters most | [r3](evidence/r3.json) | supported | "
                           "failed checks: columns; not assessed: joins |"]
