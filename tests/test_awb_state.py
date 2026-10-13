# Kept cases:
# test_show_prints_brief_and_state_verbatim: resume prints brief.md and state.md verbatim with a warning per row whose evidence is missing, writes nothing, honours --investigation, lists investigations when none is active, and exits 2 for an unknown one.
# test_run_rows_are_added_kept_and_refreshed: a new result gets a placeholder row; an exact-match rerun leaves state.md and history.md untouched; a changed rerun keeps wording and notes, demotes supported with a history entry, keeps superseded, and demotes provisional silently.
# test_flagged_rerun_always_writes_history: a flagged row returns to provisional, or superseded when it was, with a reset caveat and a history entry naming the flag reason and the exact match.
# test_failed_state_write_removes_new_evidence: evidence is removed only before findings.json is replaced; a failed state replacement names render, and failed history names missing prior rows.
# test_signals_wait_for_the_replacements: SIGINT during the replacements reaches the previous handler only after it is restored.
# test_evidence_commit_cites_verified_commits: HEAD's full SHA for committed unchanged evidence; otherwise the last commit holding a version, verified, or uncommitted.
# test_finding_guards_and_history: missing rows or evidence, stale or unexplained promotion, flagged promotion or caveat, and reserved caveat prefixes are refused; --reason is required exactly when history is due; one entry per call; provisional rewording is silent; no-ops write nothing.
# test_issues_and_next_edit_lists_in_one_call: adds and drops resolve against the original list, ambiguous or missing drops exit 2 listing candidates, only list lines change, numbering continues.
# test_switch_keeps_the_pointer_form: switch rewrites only the pointer in its link, path, backticked or slug form, which collect_status accepts, and prints the view; a missing state.md exits 1 and a customized pointer is refused.
# test_malformed_records_write_nothing: a missing or repeated Last updated or section, a wrong header, a short row, two rows for one result, or a missing history file exit 1 and leave every file byte for byte.
# test_writers_refuse_drift: every findings writer lists each differing row and the render/finding/flag remedies, the flag one conditional; prior_result protects existing evidence and results.
# test_render_restores_rows: render discards hand edits and preserves the rest of state; without findings.json a hand-written row is drift and render empties the table.
# test_kept_notes_explain_only_the_checks_they_were_written_for: after a flagged rerun, kept notes satisfy the promotion guard only if the checks are unchanged; changed checks need --caveat; an entry without notes_checks is refused before a rerun changes anything.
# test_compound_flag_reasons_are_idempotent: a reason containing '; ' is recognized as present and writes nothing.
# test_lists_above_the_table_leave_it_intact: issues and next steps placed before Current findings are edited without touching the table, and later findings writes keep it whole.
# test_render_recovers_malformed_and_stray_rows: render replaces an unescaped pipe, a duplicate row, and a row cut off below the table, which writers refuse as drift.
# test_flags_validate_and_are_idempotent: batches validate before writes, check migrates only in memory, duplicate reasons keep all records byte-identical, and a rerun keeps notes, drops the flag reason, and names only the reason in history.
# test_parsers_read_written_files: collect_status and finding_rows read the files the state command and run.py's helpers write.

from datetime import date
import importlib.util
import json
import re
import os
from pathlib import Path
import shutil
import subprocess

import pytest

if shutil.which("git") is None:
    pytest.skip("git is required", allow_module_level=True)

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / ".agents/skills/awb-init/assets/workbench"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


provenance = load("awb_provenance_state", ".agents/skills/awb-init/assets/awb_provenance.py")
status = load("awb_status_state", ".agents/skills/awb-status/scripts/collect_status.py")

TODAY = date.today().isoformat()
INV = "investigations/churn"
STATE, HISTORY = f"{INV}/state.md", f"{INV}/history.md"
OK = [{"name": "columns", "outcome": "pass", "detail": "Required columns present: 1."}]
GAPS = [{"name": "columns", "outcome": "fail", "detail": "Missing x."},
        {"name": "joins", "outcome": "not-applicable", "detail": "not assessed"}]


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True).stdout.strip()


def commit(root):
    git(root, "add", "-A")
    git(root, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "commit.gpgsign=false",
        "commit", "-qm", "work")
    return git(root, "rev-parse", "HEAD")


def text(root, path):
    return (root / path).read_text()


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*")
            if p.is_file() and ".git" not in p.parts}


@pytest.fixture
def project(tmp_path):
    git(tmp_path, "init")
    readme = (TEMPLATES / "README.md").read_text().replace(
        "Active investigation: none", "Active investigation: [churn](investigations/churn/state.md)")
    (tmp_path / "README.md").write_text(readme)
    (tmp_path / "src").mkdir()
    (tmp_path / "src/ops.py").write_text("x = 1\n")
    for name in ("churn", "pricing"):
        directory = tmp_path / "investigations" / name
        (directory / "queries").mkdir(parents=True)
        for record in ("state.md", "history.md", "brief.md"):
            shutil.copyfile(TEMPLATES / "investigation" / record, directory / record)
        (directory / "settings.toml").write_text(
            "[parameters]\nyear = 2026\n" + "".join(f"\n[results.r{i}]\n" for i in range(1, 6)))
        for i in range(1, 6):
            (directory / f"queries/r{i}.sql").write_text(f"select {i}\n")
    state = tmp_path / STATE
    state.write_text(state.read_text().replace("<!-- use an ISO date -->", "2026-09-01"))
    commit(tmp_path)
    return tmp_path


def produce(project, result_id, table="n\n1\n", checks=OK):
    """What run.py does for one result: capture the prior, replace evidence and table, write the row."""
    prior = provenance.prior_result(project, "churn", result_id)
    (project / INV / "evidence" / f"{result_id}.json").unlink(missing_ok=True)
    (project / INV / "results").mkdir(exist_ok=True)
    (project / INV / "results" / f"{result_id}.csv").write_text(table)
    provenance.record_evidence(project, "churn", result_id, views=[], checks=checks,
                               settings_path=f"{INV}/settings.toml")
    return provenance.record_finding(project, "churn", result_id, checks, prior=prior, today=TODAY)


def set_row(project, result_id, finding=None, row_status=None, caveat=None):
    """Set a recorded finding's cells directly in findings.json and re-render, bypassing the guards."""
    path = project / INV / "findings.json"
    content = json.loads(path.read_text())
    entry = next(e for e in content["findings"] if e["result"] == result_id)
    if finding is not None:
        entry["text"] = finding
    if row_status is not None:
        flagged = re.fullmatch(r"revalidation-needed(?: \(was (.+)\))?", row_status)
        entry["status"], entry["prior_status"] = ("revalidation-needed", flagged[1]) if flagged else (row_status, None)
    if caveat is not None:
        parts = [part for part in caveat.split("; ") if part]
        checks = [part for part in parts if part.startswith(("failed checks: ", "not assessed: "))]
        others = [part for part in parts if part not in checks]
        entry["checks_caveat"] = entry["notes_checks"] = "; ".join(checks)
        flagged_now = entry["status"] == "revalidation-needed"
        entry["notes"], entry["flag_reason"] = ([], "; ".join(others)) if flagged_now else (others, "")
    path.write_text(json.dumps(content, indent=2) + "\n")
    provenance.render_findings(project, "churn")


def run(project, capsys, *argv):
    code = provenance.cli_state(project, list(argv))
    out = capsys.readouterr()
    return code, out.out, out.err


def entries(project):
    return [entry for entry in text(project, HISTORY).split("\n### ")[1:] if entry[:1].isdigit()]


def test_show_prints_brief_and_state_verbatim(project, capsys):
    produce(project, "r1")
    (project / f"{INV}/evidence/r1.json").unlink()
    before = snapshot(project)
    code, out, _ = run(project, capsys)
    assert code == 0 and snapshot(project) == before
    assert f"==> {INV}/brief.md <==\n" + text(project, f"{INV}/brief.md").rstrip() in out
    assert f"==> {STATE} <==\n" + text(project, STATE).rstrip() in out
    assert out.rstrip().endswith("warning: r1 links evidence/r1.json, which does not exist")
    code, out, _ = run(project, capsys, "--investigation", "pricing")
    assert code == 0 and "==> investigations/pricing/state.md <==" in out and "warning" not in out
    assert run(project, capsys, "--investigation", "absent")[0] == 2
    readme = project / "README.md"
    readme.write_text(readme.read_text().replace("[churn](investigations/churn/state.md)", "none"))
    code, out, _ = run(project, capsys)
    assert code == 0 and out.startswith("No active investigation. Investigations: churn, pricing.")
    assert run(project, capsys, "issues", "--add", "x")[0] == 1


def test_run_rows_are_added_kept_and_refreshed(project):
    assert produce(project, "r1") == {"action": "added", "status": "provisional", "history": False}
    row = "| <state the finding from r1> | [r1](evidence/r1.json) | provisional | |"
    assert row in text(project, STATE) and f"Last updated: {TODAY}" in text(project, STATE)
    assert produce(project, "r2", checks=GAPS)["action"] == "added"
    assert "| provisional | failed checks: columns; not assessed: joins |" in text(project, STATE)

    set_row(project, "r1", "Churn rose 3 points", "supported", "joins: one table")
    records = snapshot(project)
    kept = produce(project, "r1")
    assert kept == {"action": "kept", "status": "supported", "history": False}
    assert text(project, STATE).encode() == records[STATE] and text(project, HISTORY).encode() == records[HISTORY]

    refreshed = produce(project, "r1", table="n\n2\n", checks=GAPS)
    assert refreshed == {"action": "refreshed", "status": "provisional", "history": True}
    assert ("| Churn rose 3 points | [r1](evidence/r1.json) | provisional | "
            "failed checks: columns; not assessed: joins; joins: one table |") in text(project, STATE)
    [entry] = entries(project)
    assert entry.startswith(f"{TODAY} — r1 rerun: supported → provisional\n")
    assert "prior row `| Churn rose 3 points | [r1](evidence/r1.json) | supported | joins: one table |`" in entry
    assert "- **Reasoning or decision:** rerun\n" in entry
    assert "- **Impact and caveats:** provisional; re-promote with `awb.py state finding`." in entry

    produce(project, "r1", table="n\n3\n")  # provisional and changed: no history
    assert len(entries(project)) == 1
    set_row(project, "r1", row_status="superseded")
    assert produce(project, "r1", table="n\n4\n")["status"] == "superseded"
    assert len(entries(project)) == 1


def test_flagged_rerun_always_writes_history(project):
    produce(project, "r1", checks=GAPS)
    produce(project, "r2")
    set_row(project, "r1", "Churn rose", "revalidation-needed (was supported)",
            "failed checks: columns; not assessed: joins; joins: one table; Q-004 correction")
    set_row(project, "r2", "Old view", "revalidation-needed (was superseded)", "Q-005 correction")
    head = commit(project)
    cleared = produce(project, "r1", checks=GAPS)
    assert cleared == {"action": "flag cleared", "status": "provisional", "history": True}
    assert "| Churn rose | [r1](evidence/r1.json) | provisional | failed checks: columns; not assessed: joins |" \
        in text(project, STATE)
    entry = entries(project)[-1]
    assert entry.startswith(f"{TODAY} — r1 rerun: revalidation-needed (was supported) → provisional\n")
    assert "; table, checks and settings unchanged." in entry
    assert f"prior evidence at commit {head}." in entry
    assert "- **Reasoning or decision:** rerun; flag reason: joins: one table; Q-004 correction\n" in entry
    assert produce(project, "r2", table="n\n9\n")["status"] == "superseded"
    entry = entries(project)[-1]
    assert "rerun: revalidation-needed (was superseded) → superseded" in entry
    assert "- **Impact and caveats:** superseded; no promotion required." in entry
    assert "unchanged" not in entry and entry.endswith("- **Supersedes or revalidation link:**\n")


def test_failed_state_write_removes_new_evidence(project, monkeypatch):
    produce(project, "r1")
    set_row(project, "r1", "Churn rose", "supported")
    evidence = project / f"{INV}/evidence/r1.json"
    real, calls = os.replace, []

    def failing(source, target):
        calls.append(Path(target).name)
        if Path(target).name == fail_on:
            raise OSError("disk full")
        return real(source, target)

    monkeypatch.setattr(provenance.os, "replace", failing)
    fail_on, before = "findings.json", snapshot(project)
    with pytest.raises(provenance.StateError, match="findings.json not written"):
        produce(project, "r1", table="n\n2\n")
    assert not evidence.exists() and text(project, STATE).encode() == before[STATE]
    assert text(project, f"{INV}/findings.json").encode() == before[f"{INV}/findings.json"]
    fail_on = "state.md"
    with pytest.raises(provenance.StateError, match="table is behind.*state render --investigation churn"):
        produce(project, "r1", table="n\n3\n")
    assert evidence.exists() and text(project, STATE).encode() == before[STATE]
    assert calls[-3:] == ["r1.json", "findings.json", "state.md"]
    assert not [p for p in (project / INV).iterdir() if p.name.endswith(".tmp")]
    fail_on = None
    provenance.render_findings(project, "churn")
    set_row(project, "r1", row_status="supported")
    fail_on = "history.md"
    with pytest.raises(provenance.StateError, match=r"history.md not written .*prior rows it lacks: \| Churn"):
        produce(project, "r1", table="n\n4\n")
    assert evidence.exists() and "| provisional |" in text(project, STATE)
    assert calls[-3:] == ["findings.json", "state.md", "history.md"]


def test_signals_wait_for_the_replacements():
    import signal
    seen = []
    previous = signal.signal(signal.SIGINT, lambda number, frame: seen.append(signal.getsignal(signal.SIGINT)))
    try:
        handler = signal.getsignal(signal.SIGINT)
        with provenance._signals_deferred():
            signal.raise_signal(signal.SIGINT)
            assert seen == [] and signal.getsignal(signal.SIGINT) is not handler
        assert seen == [handler]
    finally:
        signal.signal(signal.SIGINT, previous)


def test_evidence_commit_cites_verified_commits(project):
    path = project / f"{INV}/evidence/r1.json"
    path.parent.mkdir()
    assert provenance.evidence_commit(project, "churn", "r1") == "uncommitted"
    path.write_text("{}\n")
    first = commit(project)
    assert provenance.evidence_commit(project, "churn", "r1") == first and len(first) == 40
    path.write_text('{"rerun": 1}\n')
    assert provenance.evidence_commit(project, "churn", "r1") == f"uncommitted; last committed at {first}"
    path.unlink()
    commit(project)  # a commit that deletes the file holds no version of it
    path.write_text('{"rerun": 2}\n')
    assert provenance.evidence_commit(project, "churn", "r1") == f"uncommitted; last committed at {first}"


def test_finding_guards_and_history(project, capsys):
    produce(project, "r1")
    produce(project, "r2")
    produce(project, "r3", checks=GAPS)
    produce(project, "r4")
    set_row(project, "r4", "Old", "revalidation-needed (was supported)", "Q-004 correction")
    commit(project)

    code, out, _ = run(project, capsys, "finding", "r1", "--text", "Churn | rose 3 points")
    assert code == 0 and out == r"| Churn \| rose 3 points | [r1](evidence/r1.json) | provisional | |" + "\n"
    assert entries(project) == []  # provisional rewording is silent
    before = snapshot(project)
    assert run(project, capsys, "finding", "r1", "--text", "Churn | rose 3 points")[1].startswith("unchanged: r1")
    assert snapshot(project) == before

    refusals = [
        (["finding", "r1", "--status", "supported"], 2, "--reason is required"),
        (["finding", "r9", "--status", "superseded", "--reason", "x"], 1, "no findings row links r9"),
        (["finding", "r3", "--status", "supported", "--reason", "x"], 1, "explain them with --caveat"),
        (["finding", "r4", "--status", "supported", "--reason", "x"], 1, "only a rerun clears the flag"),
        (["finding", "r4", "--caveat", "fine"], 1, "only a rerun clears the flag"),
        (["finding", "r3", "--caveat", "not assessed: none"], 2, "reserved prefixes"),
        (["finding", "r1", "r2", "--text", "x"], 2, "several result IDs"),
        (["finding", "r1"], 2, "give --status"),
        (["finding", "r1", "--status", "done"], 2, "invalid choice"),
    ]
    for argv, expected, message in refusals:
        code, _, err = run(project, capsys, *argv)
        assert (code, message in err) == (expected, True), argv
        assert snapshot(project) == before, argv
    (project / f"{INV}/evidence/r2.json").rename(project / "r2.json")
    assert "evidence/r2.json does not exist" in run(project, capsys, "finding", "r2", "--text", "x")[2]
    (project / "r2.json").rename(project / f"{INV}/evidence/r2.json")
    (project / "src/ops.py").write_text("x = 2\n")
    code, _, err = run(project, capsys, "finding", "r1", "--status", "supported", "--reason", "x")
    assert code == 1 and "is stale" in err and snapshot(project) == {**before, "src/ops.py": b"x = 2\n"}
    (project / "src/ops.py").write_text("x = 1\n")

    assert run(project, capsys, "finding", "r3", "--caveat", "joins: single table")[0] == 0
    head = git(project, "rev-parse", "HEAD")
    code, out, _ = run(project, capsys, "finding", "r1", "r3", "--status", "supported",
                       "--reason", "Checked against the Q3 renewals.")
    assert code == 0 and out.endswith(f"history.md: ### {TODAY} — r1, r3 promoted to supported\n")
    [entry] = entries(project)
    assert "r1 was `| Churn \\| rose 3 points | [r1](evidence/r1.json) | provisional | |`; now " \
           "\"Churn \\| rose 3 points\" (supported)." in entry
    assert f"[r1](evidence/r1.json) at commit {head}; [r3](evidence/r3.json) at commit {head}." in entry
    assert "- **Reasoning or decision:** Checked against the Q3 renewals.\n" in entry
    assert "r3: failed checks: columns; not assessed: joins; joins: single table." in entry

    code, out, _ = run(project, capsys, "finding", "r4", "--text", "Older", "--reason", "Renamed.")
    assert code == 0 and out.startswith("warning: r4 is flagged; package dispositions") and len(entries(project)) == 2
    assert run(project, capsys, "finding", "r4", "--status", "superseded")[0] == 2
    assert run(project, capsys, "finding", "r4", "--status", "superseded", "--reason", "Replaced by r1.")[0] == 0
    assert "| Older | [r4](evidence/r4.json) | superseded | Q-004 correction |" in text(project, STATE)
    assert entries(project)[-1].startswith(f"{TODAY} — r4 set to superseded\n")


def test_issues_and_next_edit_lists_in_one_call(project, capsys):
    original = text(project, STATE)
    code, out, _ = run(project, capsys, "issues", "--add", "Is the  Q3 dip a gap?", "--add", "Tenure coding")
    assert code == 0 and out == "Unresolved issues: added 2, dropped 0\n"
    assert run(project, capsys, "next", "--add", "Explore shifts", "--add", "Explore orders")[0] == 0
    current = text(project, STATE)
    assert "Keep this a short list.\n- Is the Q3 dip a gap?\n- Tenure coding\n\n## Next steps" in current
    assert current.endswith("Keep this a short list.\n- Explore shifts\n- Explore orders\n")

    before = snapshot(project)
    for argv, listed in ((["next", "--drop", "Explore"], "1. Explore shifts; 2. Explore orders"),
                         (["next", "--drop", "explore shifts"], "1. Explore shifts; 2. Explore orders"),
                         (["next", "--drop", "orders", "--drop", "9"], "1. Explore shifts")):
        code, _, err = run(project, capsys, *argv)
        assert code == 2 and listed in err and snapshot(project) == before, argv
    code, out, _ = run(project, capsys, "next", "--drop", "2", "--drop", "shifts", "--add", "Profile tenure")
    assert code == 0 and out == "Next steps: added 1, dropped 2\n  - Explore orders\n  - Explore shifts\n"
    assert text(project, STATE).endswith("Keep this a short list.\n- Profile tenure\n")
    assert run(project, capsys, "next", "--drop", "1")[0] == 0
    assert run(project, capsys, "issues", "--drop", "Q3", "--drop", "Tenure")[0] == 0
    assert text(project, STATE) == original.replace("2026-09-01", TODAY)

    (project / STATE).write_text(original.replace("Keep this a short list.\n\n## Next",
                                                  "Keep this a short list.\n\n1. First\n   continued\n\n## Next"))
    assert run(project, capsys, "issues", "--add", "Second", "--add", "Third")[0] == 0
    assert "1. First\n   continued\n2. Second\n3. Third\n\n## Next" in text(project, STATE)
    assert run(project, capsys, "issues", "--drop", "continued")[1].endswith("  - First continued\n")


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
    original = readme.read_text().replace("[churn](investigations/churn/state.md)", pointer)
    readme.write_text(original)
    code, out, _ = run(project, capsys, "switch", "pricing")
    assert code == 0 and out.startswith("Active investigation: pricing\n==> investigations/pricing/brief.md <==")
    assert readme.read_text() == original.replace(f"Active investigation: {pointer}",
                                                  f"Active investigation: {expected}")
    assert status.collect(project)["active"]["name"] == "pricing"
    assert run(project, capsys, "switch", "pricing")[1].startswith("Already active: pricing")
    assert run(project, capsys, "switch", "absent")[0] == 2
    (project / "investigations/empty").mkdir()
    before = snapshot(project)
    code, _, err = run(project, capsys, "switch", "empty")
    assert code == 1 and "state.md does not exist" in err and snapshot(project) == before
    readme.write_text(original.replace(f"Active investigation: {pointer}", "Active investigation: see the wiki"))
    before = snapshot(project)
    code, _, err = run(project, capsys, "switch", "churn")
    assert code == 1 and "customized" in err and snapshot(project) == before


@pytest.mark.parametrize("record, old, new", [
    (STATE, "Last updated: 2026-09-01\n", ""),
    (STATE, "Last updated: 2026-09-01\n", "Last updated: 2026-09-01\nLast updated: 2026-09-02\n"),
    (STATE, "## Next steps", "## Later"),
    (STATE, "## Unresolved issues", "## Next steps"),
    (STATE, "| Finding | Evidence |", "| Result | Evidence |"),
    (STATE, "| provisional | |", "| provisional |"),
    (STATE, "[r2](evidence/r2.json)", "[r1](evidence/r1.json)"),
    (HISTORY, None, None),
])
def test_malformed_records_write_nothing(project, capsys, record, old, new):
    produce(project, "r1")
    produce(project, "r2")
    path = project / record
    if old is None:
        path.unlink()
        commands = [["finding", "r1", "--status", "superseded", "--reason", "x"]]
    else:
        old, new = old.replace("2026-09-01", TODAY), new.replace("2026-09-01\n", f"{TODAY}\n", 1)
        assert old in path.read_text()
        path.write_text(path.read_text().replace(old, new, 1))
        lists = [["issues", "--add", "x"]] if "Unresolved" in old else [["next", "--add", "x"]]
        commands = lists if "## " in old else [["finding", "r1", "--text", "x"], ["issues", "--add", "x"]]
    before = snapshot(project)
    for argv in commands:
        code, out, err = run(project, capsys, *argv)
        assert code == 1 and not out and len(err.strip().splitlines()) == 1, argv
        assert snapshot(project) == before, argv


def test_parsers_read_written_files(project, capsys):
    produce(project, "r1")
    produce(project, "r2", checks=GAPS)
    produce(project, "r3")
    set_row(project, "r3", row_status="revalidation-needed (was supported)", caveat="Q-004 correction")
    produce(project, "r3")
    assert run(project, capsys, "finding", "r1", "--text", "Churn | rose", "--status", "supported",
               "--reason", "Checked.")[0] == 0
    assert run(project, capsys, "issues", "--add", "Q3 coverage gap")[0] == 0
    assert run(project, capsys, "next", "--add", "Explore shifts")[0] == 0
    result = status.collect(project)
    assert not [u for u in result["uncertainties"] if u["path"] == STATE]
    active = result["active"]
    assert active["last_updated"] == TODAY
    assert active["counts"] == {"supported": 1, "provisional": 2}
    assert {"finding": r"Churn \| rose", "status": "supported", "reason": ""} in active["findings"]
    assert "- Q3 coverage gap" in active["unresolved_issues"] and "- Explore shifts" in active["next_steps"]
    found = provenance.finding_rows(project / STATE)
    assert sorted(found) == ["r1", "r2", "r3"] and all(len(rows) == 1 for rows in found.values())
    assert found["r2"] == ["| <state the finding from r2> | [r2](evidence/r2.json) | provisional | "
                           "failed checks: columns; not assessed: joins |"]


@pytest.mark.parametrize("writer", ["record", "update", "flag", "prior"])
def test_writers_refuse_drift(project, writer):
    produce(project, "r1")
    produce(project, "r2")
    state = project / STATE
    state.write_text(state.read_text().replace("| provisional | |", "| revalidation-needed (was provisional) | Q-004 |", 1)
                     .replace("<state the finding from r2>", "Hand edited finding"))
    before = snapshot(project)
    with pytest.raises(provenance.StateError, match="findings drift") as failure:
        if writer == "record":
            provenance.record_finding(project, "churn", "r1", OK)
        elif writer == "update":
            provenance.update_findings(project, "churn", ["r1"], text="New finding")
        elif writer == "flag":
            provenance.flag_findings(project, "churn", [{"result": "r1", "reason": "Q-005"}])
        else:
            produce(project, "r1", table="n\n99\n")
    message = str(failure.value)
    assert "Q-004" in message and "Hand edited finding" in message
    assert "state render --investigation churn" in message and "state finding" in message
    assert 'state flag --investigation churn, stdin: [{"result": "r1", "reason": "Q-004"}]' in message
    assert "if this flag was added by hand" in message
    if writer == "record":  # This call represents a newly recorded evidence file.
        before.pop(f"{INV}/evidence/r1.json")
    assert snapshot(project) == before


def test_render_restores_rows(project, capsys):
    template = text(project, STATE)
    hand = "| Written by hand | [r9](evidence/r9.json) | supported | |"
    (project / STATE).write_text(template.replace("| --- | --- | --- | --- |\n", "| --- | --- | --- | --- |\n" + hand + "\n"))
    with pytest.raises(provenance.StateError, match="findings drift"):  # no findings.json: the table renders empty
        provenance.update_findings(project, "churn", ["r9"], text="x")
    code, out, _ = run(project, capsys, "render")
    assert code == 0 and out == "discarded: " + hand + "\n" and text(project, STATE) == template
    produce(project, "r1")
    original = text(project, STATE)
    (project / STATE).write_text(original.replace("<state the finding from r1>", "Hand edit")
                                .replace("## Next steps", "A handwritten note.\n\n## Next steps"))
    drift = provenance.findings_drift(project, "churn")
    assert drift == [{"result": "r1", "disk": "| Hand edit | [r1](evidence/r1.json) | provisional | |",
                      "rendered": "| <state the finding from r1> | [r1](evidence/r1.json) | provisional | |"}]
    json_before = text(project, f"{INV}/findings.json")
    code, out, _ = run(project, capsys, "render")
    assert code == 0 and out == "discarded: " + drift[0]["disk"] + "\n"
    assert text(project, STATE) == original.replace("## Next steps", "A handwritten note.\n\n## Next steps")
    assert text(project, f"{INV}/findings.json") == json_before
    assert provenance.findings_drift(project, "churn") == []


def test_flags_validate_and_are_idempotent(project, capsys, monkeypatch):
    produce(project, "r1", checks=GAPS)
    provenance.update_findings(project, "churn", ["r1"], caveat="old note | detail")
    flags = [{"result": "r1", "reason": "Q-004 correction"}]
    before = snapshot(project)
    with pytest.raises(provenance.StateError, match="r9"):
        provenance.flag_findings(project, "churn", flags + [{"result": "r9", "reason": "Q-005"}])
    assert snapshot(project) == before
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO(json.dumps(flags)))
    code, out, _ = run(project, capsys, "flag", "--check")
    assert code == 0 and json.loads(out)["flags"] == [{"result": "r1", "status": "revalidation-needed (was provisional)"}]
    assert snapshot(project) == before
    provenance.flag_findings(project, "churn", flags)
    before = snapshot(project)
    assert provenance.flag_findings(project, "churn", flags, today="2099-01-01") == {
        "flags": [], "unchanged": ["r1"], "rows": []}
    assert snapshot(project) == before
    provenance.flag_findings(project, "churn", [{"result": "r1", "reason": "Q-005"}])
    entry = json.loads(text(project, f"{INV}/findings.json"))["findings"][0]
    assert entry["flag_reason"] == "Q-004 correction; Q-005" and entry["prior_status"] == "provisional"
    produce(project, "r1", checks=GAPS)
    entry = json.loads(text(project, f"{INV}/findings.json"))["findings"][0]
    assert entry["notes"] == ["old note | detail"] and entry["flag_reason"] == "" and entry["prior_status"] is None
    assert r"| provisional | failed checks: columns; not assessed: joins; old note \| detail |" in text(project, STATE)
    assert "flag reason: Q-004 correction; Q-005\n" in text(project, HISTORY)


def test_compound_flag_reasons_are_idempotent(project):
    produce(project, "r1")
    flags = [{"result": "r1", "reason": "Q-004 merges labels; affects counts"}]
    provenance.flag_findings(project, "churn", flags)
    before = snapshot(project)
    assert provenance.flag_findings(project, "churn", flags)["unchanged"] == ["r1"]
    assert snapshot(project) == before


def test_lists_above_the_table_leave_it_intact(project):
    produce(project, "r1")
    state = text(project, STATE)
    lists = state[state.index("## Unresolved issues"):]
    (project / STATE).write_text(state.replace(lists, "").replace("## Current findings", lists + "\n## Current findings"))
    assert provenance.edit_list(project, "churn", "issues", add=["Gap in Q3"])["added"] == ["Gap in Q3"]
    assert provenance.edit_list(project, "churn", "next", add=["Check Q3"])["added"] == ["Check Q3"]
    produce(project, "r2")
    assert sorted(provenance.finding_rows(project / STATE)) == ["r1", "r2"]
    assert text(project, STATE).count("| --- | --- | --- | --- |") == 1
    assert provenance.findings_drift(project, "churn") == []


def test_render_recovers_malformed_and_stray_rows(project, capsys):
    produce(project, "r1")
    produce(project, "r2")
    original = text(project, STATE)
    row2 = "| <state the finding from r2> | [r2](evidence/r2.json) | provisional | |"
    damaged = original.replace("<state the finding from r1>", "a | b").replace(row2, row2 + "\n" + row2)
    damaged = damaged.replace("## Unresolved issues", "\n" + row2 + "\n\n## Unresolved issues")
    (project / STATE).write_text(damaged)
    with pytest.raises(provenance.StateError):
        provenance.flag_findings(project, "churn", [{"result": "r1", "reason": "Q-004"}])
    code, out, _ = run(project, capsys, "render")
    assert code == 0 and "a | b" in out
    assert text(project, STATE) == original.replace("## Unresolved issues", "\n\n## Unresolved issues")
    assert all(len(rows) == 1 for rows in provenance.finding_rows(project / STATE).values())
    assert provenance.findings_drift(project, "churn") == []


def test_kept_notes_explain_only_the_checks_they_were_written_for(project):
    totals = [{"name": "totals", "outcome": "fail", "detail": "Totals differ."}]
    for result_id in ("r1", "r2"):
        produce(project, result_id, checks=GAPS)
        provenance.update_findings(project, "churn", [result_id], caveat="Agency workers excluded")
        provenance.update_findings(project, "churn", [result_id], status="supported", reason="checked")
    provenance.flag_findings(project, "churn", [{"result": "r1", "reason": "Q-004"}, {"result": "r2", "reason": "Q-004"}])
    produce(project, "r1", checks=totals)  # the correction changed r1's checks
    produce(project, "r2", checks=GAPS)
    assert "| provisional | failed checks: totals; Agency workers excluded |" in text(project, STATE)
    before = snapshot(project)
    with pytest.raises(provenance.StateError, match="written for failed checks: columns; not assessed: joins, "
                                                    "so restate those that still hold"):
        provenance.update_findings(project, "churn", ["r1", "r2"], status="supported", reason="rechecked")
    assert snapshot(project) == before
    assert provenance.update_findings(project, "churn", ["r2"], status="supported", reason="rechecked")["rows"]
    provenance.update_findings(project, "churn", ["r1"], caveat="Agency workers excluded; totals checked by hand")
    assert provenance.update_findings(project, "churn", ["r1"], status="supported", reason="rechecked")["rows"]
    path = project / INV / "findings.json"
    content = json.loads(path.read_text())
    del content["findings"][0]["notes_checks"]  # required: a missing field is refused, never defaulted
    path.write_text(json.dumps(content))
    before = snapshot(project)
    with pytest.raises(provenance.StateError, match="invalid finding"):
        produce(project, "r1", table="n\n5\n")
    assert snapshot(project) == before
