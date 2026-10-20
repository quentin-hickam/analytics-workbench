# Kept cases:
# test_show_prints_brief_and_state_verbatim: resume prints brief.md and state.md verbatim with a warning per row whose evidence is missing, writes nothing, honours --investigation, lists investigations when none is active, and exits 2 for an unknown one.
# test_show_prints_each_findings_question: resume prints the question each finding's evidence records, by result ID in table order, after state.md and before missing-evidence warnings.
# test_run_rows_are_added_kept_and_refreshed: a new result gets a placeholder row; an exact-match rerun leaves state.md and history.md untouched; a changed rerun keeps wording and notes, demotes supported with a history entry, keeps superseded, and demotes provisional silently.
# test_flagged_rerun_always_writes_history: a flagged row returns to provisional, or superseded when it was, with a reset caveat and a history entry naming the flag reason and the exact match.
# test_failed_state_write_removes_new_evidence: evidence is removed only before findings.json is replaced; a failed state replacement names render, and failed history names missing prior rows.
# test_signals_wait_for_the_replacements: SIGINT during the replacements reaches the previous handler only after it is restored.
# test_evidence_commit_cites_verified_commits: HEAD's full SHA for committed unchanged evidence; otherwise the last commit holding a version, verified, or uncommitted.
# test_finding_guards_and_history: missing rows or evidence, stale, unexplained, or placeholder-text promotion (unless --text in the same call replaces it), flagged promotion or caveat, and reserved caveat prefixes are refused; --reason is required exactly when history is due; one entry per call; provisional rewording is silent; no-ops write nothing.
# test_issues_and_next_edit_lists_in_one_call: adds and drops resolve against the original list, ambiguous or missing drops exit 2 listing candidates, only list lines change, numbering continues.
# test_switch_keeps_the_pointer_form: switch rewrites only the pointer in its link, path, backticked or slug form, which collect_status accepts, and prints the view; a missing state.md exits 1 and a customized pointer is refused.
# test_malformed_records_write_nothing: a missing or repeated Last updated or section, a wrong header, a short row, two rows for one result, or a missing history file exit 1 and leave every file byte for byte.
# test_writers_refuse_drift: every findings writer lists each differing row and the render/finding/flag remedies, the flag one conditional; prior_result protects existing evidence and results.
# test_drift_hint_drops_a_note_holding_a_bracketed_semicolon: the hand-added flag's suggested reason leaves out the row's notes, one holding "; " inside brackets included.
# test_render_restores_rows: render discards hand edits and preserves the rest of state; without findings.json a hand-written row is drift and render empties the table.
# test_kept_notes_explain_only_the_checks_they_were_written_for: after a flagged rerun, kept notes satisfy the promotion guard only if the checks are unchanged; changed checks need --caveat; an entry without notes_checks is refused before a rerun changes anything.
# test_compound_flag_reasons_are_idempotent: a reason containing '; ' is recognized as present and writes nothing.
# test_lists_above_the_table_leave_it_intact: issues and next steps placed before Current findings are edited without touching the table, and later findings writes keep it whole.
# test_render_recovers_malformed_and_stray_rows: render replaces an unescaped pipe, a duplicate row, and a row cut off below the table, which writers refuse as drift.
# test_flags_validate_and_are_idempotent: batches validate before writes, check migrates only in memory, duplicate reasons keep all records byte-identical, and a rerun keeps notes, drops the flag reason, and names only the reason in history.
# test_parsers_read_written_files: collect_status and finding_rows read the files the state command and run.py's helpers write, and finds the state they leave up to date.
# test_last_updated_is_stamped_after_the_records_written_with_it: a state write stamps Last updated, a local time with its offset, after writing the findings and history files it replaces with it.
# test_a_kept_rerun_leaves_the_state_up_to_date: a kept rerun's table, profile, and evidence, written after the state, leave it up to date; a table edited after its evidence, or without evidence, dates it.
# test_render_stamps_the_state: state render stamps Last updated, so the findings.json it rewrites leaves the state up to date.
# test_claim_strength_is_recorded_and_guarded: a new row is association; --claim causal needs an experiment or natural-experiment basis and a reason; a claim change writes history; a rerun keeps the claim; a flagged finding's claim can only be lowered.
# test_absent_claim_strength_is_refused: a findings.json entry without a valid claim strength makes every writer and the drift check refuse, writing nothing.
# test_finding_text_warns_on_numbers_its_result_does_not_record: with src/packaging/draft.py, --text or --status supported warns on each number the result's table, profile, checks, and settings do not record, still writing; a recorded number at another precision traces; without draft.py nothing is read; a draft.py that does not load is named.
# test_finding_text_warns_on_reconciliation_no_check_records: "sums to", "reconciles", "checked every", or "verified each" wording warns, naming a values or metrics judgment as the place to record the check, unless a passing check's name or detail uses wording of the same kind (sum or add up wording backs only such wording, reconcile wording only reconcile wording, checked or verified wording only such wording), so an unrelated "Checked all date filters" scope judgment does not back "sums to", nor does a reconcile() row count's "reconciled:" detail; a failing check does not back it; the row is still written.
# test_finding_text_with_unreadable_evidence_warns_and_writes: --text on a row whose evidence is not JSON, or not a JSON object, warns that nothing was checked and still writes.
# test_caveat_splits_notes_outside_brackets: --caveat splits at each ; outside parentheses and square brackets, either closer closes the innermost open bracket, a closer with no opener and an unclosed bracket with no ; after it are text, a ; after an unclosed bracket is refused writing nothing, and --help says so.
# test_package_promotion_command_runs: the promotion command awb-package's headline checkpoint gives, filled in, promotes a provisional finding; without --reason it is refused.

from datetime import date
import importlib.util
import json
import re
import shlex
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
            "[parameters]\nyear = 2026\n"
            + "".join(f'\n[results.r{i}]\nquestion = "What is question {i}?"\n' for i in range(1, 6)))
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


def test_show_prints_each_findings_question(project, capsys):
    for result_id in ("r2", "r1", "r3"):
        produce(project, result_id)
    (project / f"{INV}/evidence/r3.json").unlink()
    code, out, _ = run(project, capsys)
    assert code == 0
    view = (f"{text(project, STATE).rstrip()}\n\n==> questions the findings answer, by result <==\n"
            "r2: What is question 2?\nr1: What is question 1?\n\n"
            "warning: r3 links evidence/r3.json, which does not exist")
    assert out.rstrip().endswith(view)


def test_run_rows_are_added_kept_and_refreshed(project):
    assert produce(project, "r1") == {"action": "added", "status": "provisional", "claim": "association", "history": False}
    row = "| <state the finding from r1> | [r1](evidence/r1.json) | provisional | association | |"
    assert row in text(project, STATE) and re.search(rf"\nLast updated: {TODAY}T\d\d:\d\d:\d\d[+-]\d\d:\d\d\n", text(project, STATE))
    assert produce(project, "r2", checks=GAPS)["action"] == "added"
    assert "| provisional | association | failed checks: columns; not assessed: joins |" in text(project, STATE)

    set_row(project, "r1", "Churn rose 3 points", "supported", "joins: one table")
    records = snapshot(project)
    kept = produce(project, "r1")
    assert kept == {"action": "kept", "status": "supported", "claim": "association", "history": False}
    assert text(project, STATE).encode() == records[STATE] and text(project, HISTORY).encode() == records[HISTORY]

    refreshed = produce(project, "r1", table="n\n2\n", checks=GAPS)
    assert refreshed == {"action": "refreshed", "status": "provisional", "claim": "association", "history": True}
    assert ("| Churn rose 3 points | [r1](evidence/r1.json) | provisional | association | "
            "failed checks: columns; not assessed: joins; joins: one table |") in text(project, STATE)
    [entry] = entries(project)
    assert entry.startswith(f"{TODAY} — r1 rerun: supported → provisional\n")
    assert "prior row `| Churn rose 3 points | [r1](evidence/r1.json) | supported | association | joins: one table |`" in entry
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
    assert cleared == {"action": "flag cleared", "status": "provisional", "claim": "association", "history": True}
    assert "| Churn rose | [r1](evidence/r1.json) | provisional | association | failed checks: columns; not assessed: joins |" \
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
    assert evidence.exists() and "| provisional | association |" in text(project, STATE)
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
    assert code == 0 and out == r"| Churn \| rose 3 points | [r1](evidence/r1.json) | provisional | association | |" + "\n"
    assert entries(project) == []  # provisional rewording is silent
    before = snapshot(project)
    assert run(project, capsys, "finding", "r1", "--text", "Churn | rose 3 points")[1].startswith("unchanged: r1")
    assert snapshot(project) == before

    refusals = [
        (["finding", "r1", "--status", "supported"], 2, "--reason is required"),
        (["finding", "r9", "--status", "superseded", "--reason", "x"], 1, "no findings row links r9"),
        (["finding", "r2", "--status", "supported", "--reason", "x"], 1, "placeholder text; state the finding with --text"),
        (["finding", "r3", "--text", "Churn held", "--status", "supported", "--reason", "x"], 1,
         "explain them with --caveat"),
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

    assert run(project, capsys, "finding", "r3", "--text", "Churn held", "--caveat", "joins: single table")[0] == 0
    head = git(project, "rev-parse", "HEAD")
    code, out, _ = run(project, capsys, "finding", "r1", "r3", "--status", "supported",
                       "--reason", "Checked against the Q3 renewals.")
    assert code == 0 and out.endswith(f"history.md: ### {TODAY} — r1, r3 promoted to supported\n")
    [entry] = entries(project)
    assert "r1 was `| Churn \\| rose 3 points | [r1](evidence/r1.json) | provisional | association | |`; now " \
           "\"Churn \\| rose 3 points\" (supported)." in entry
    assert f"[r1](evidence/r1.json) at commit {head}; [r3](evidence/r3.json) at commit {head}." in entry
    assert "- **Reasoning or decision:** Checked against the Q3 renewals.\n" in entry
    assert "r3: failed checks: columns; not assessed: joins; joins: single table." in entry

    code, out, _ = run(project, capsys, "finding", "r4", "--text", "Older", "--reason", "Renamed.")
    assert code == 0 and out.startswith("warning: r4 is flagged; package dispositions") and len(entries(project)) == 2
    assert run(project, capsys, "finding", "r4", "--status", "superseded")[0] == 2
    assert run(project, capsys, "finding", "r4", "--status", "superseded", "--reason", "Replaced by r1.")[0] == 0
    assert "| Older | [r4](evidence/r4.json) | superseded | association | Q-004 correction |" in text(project, STATE)
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
    assert re.sub(r"(?m)^Last updated: \S+$", "Last updated: 2026-09-01", text(project, STATE)) == original

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
    (STATE, "| provisional | association | |", "| provisional | association |"),
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
        stamp = re.search(r"(?m)^Last updated: (\S+)$", text(project, STATE))[1]
        old, new = old.replace("2026-09-01", stamp), new.replace("2026-09-01\n", f"{stamp}\n", 1)
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
    assert re.fullmatch(rf"{TODAY}T\d\d:\d\d:\d\d[+-]\d\d:\d\d", active["last_updated"])
    # Every record these writes left uncommitted predates the state's Last updated.
    assert result["git"]["state_status"] == "up to date"
    assert active["counts"] == {"supported": 1, "provisional": 2}
    assert {"finding": r"Churn \| rose", "status": "supported", "claim": "association", "reason": ""} in active["findings"]
    assert "- Q3 coverage gap" in active["unresolved_issues"] and "- Explore shifts" in active["next_steps"]
    found = provenance.finding_rows(project / STATE)
    assert sorted(found) == ["r1", "r2", "r3"] and all(len(rows) == 1 for rows in found.values())
    assert found["r2"] == ["| <state the finding from r2> | [r2](evidence/r2.json) | provisional | association | "
                           "failed checks: columns; not assessed: joins |"]


def test_last_updated_is_stamped_after_the_records_written_with_it(project, capsys, monkeypatch):
    # findings.json and history.md are written with state.md; a stamp taken before them would make the
    # state look older than its own write.
    produce(project, "r1")
    stamps, stamp = [], provenance._stamp
    monkeypatch.setattr(provenance, "_stamp", lambda: stamps.append(__import__("time").time()) or stamp())
    assert run(project, capsys, "finding", "r1", "--text", "Churn rose", "--status", "supported",
               "--reason", "Checked.")[0] == 0
    assert stamps and all((project / INV / name).stat().st_mtime <= stamps[-1] for name in ("findings.json", "history.md"))
    assert f"Last updated: {stamp()[:10]}T" in text(project, STATE)


def backdate_state(project, seconds=10):
    """Stamp the state `seconds` ago, with every investigation file a second older, as an earlier write leaves them."""
    when = __import__("time").time() - seconds
    state = project / STATE
    state.write_text(re.sub(r"Last updated: \S+", "Last updated: " + __import__("datetime").datetime.fromtimestamp(when)
                            .astimezone().isoformat(timespec="seconds"), state.read_text()))
    for path in (project / INV).rglob("*"):
        if path.is_file():
            os.utime(path, (when - 1, when - 1))
    return when


def test_a_kept_rerun_leaves_the_state_up_to_date(project):
    # run.py rewrites a kept result's table and evidence after the last state write, and writes no state.
    produce(project, "r1")
    produce(project, "r2")
    (project / INV / "results/r2.profile.json").write_text("{}\n")
    backdate_state(project)
    assert produce(project, "r2")["action"] == "kept"
    assert status.collect(project)["git"]["state_status"] == "up to date"
    # A table edited after its evidence, or left without evidence by a failed finding write, still dates the state.
    when = __import__("time").time() + 5
    os.utime(project / INV / "results/r2.csv", (when, when))
    result = status.collect(project)["git"]
    assert (result["state_status"], result["latest_change"]["source"]) == ("out of date", f"{INV}/results/r2.csv")
    os.utime(project / INV / "results/r2.csv", (when - 5, when - 5))
    (project / INV / "evidence/r2.json").unlink()
    result = status.collect(project)["git"]
    assert (result["state_status"], result["latest_change"]["source"]) == ("out of date", f"{INV}/results/r2.csv")


def test_render_stamps_the_state(project):
    produce(project, "r1")
    backdate_state(project)
    before = text(project, STATE)
    provenance.render_findings(project, "churn")
    # Without the stamp, the findings.json render rewrites would postdate the state.
    assert text(project, STATE) != before and status.collect(project)["git"]["state_status"] == "up to date"


@pytest.mark.parametrize("writer", ["record", "update", "flag", "prior"])
def test_writers_refuse_drift(project, writer):
    produce(project, "r1")
    produce(project, "r2")
    state = project / STATE
    state.write_text(state.read_text().replace("| provisional | association | |", "| revalidation-needed (was provisional) | association | Q-004 |", 1)
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


def test_drift_hint_drops_a_note_holding_a_bracketed_semicolon(project):
    produce(project, "r1")
    provenance.update_findings(project, "churn", ["r1"], caveat="a (b; c)")
    state = project / STATE
    state.write_text(state.read_text().replace(
        "| provisional | association | a (b; c) |",
        "| revalidation-needed (was provisional) | association | a (b; c); orders view corrected |"))
    with pytest.raises(provenance.StateError, match="findings drift") as failure:
        provenance.update_findings(project, "churn", ["r1"], text="x")
    assert 'stdin: [{"result": "r1", "reason": "orders view corrected"}]' in str(failure.value)


def test_render_restores_rows(project, capsys):
    template = text(project, STATE)
    hand = "| Written by hand | [r9](evidence/r9.json) | supported | association | |"
    (project / STATE).write_text(template.replace("| --- | --- | --- | --- | --- |\n", "| --- | --- | --- | --- | --- |\n" + hand + "\n"))
    with pytest.raises(provenance.StateError, match="findings drift"):  # no findings.json: the table renders empty
        provenance.update_findings(project, "churn", ["r9"], text="x")
    code, out, _ = run(project, capsys, "render")
    # Render stamps Last updated, and keeps the rest of the state.
    unstamped = lambda value: re.sub(r"Last updated: \S+", "Last updated:", value)
    assert code == 0 and out == "discarded: " + hand + "\n" and unstamped(text(project, STATE)) == unstamped(template)
    produce(project, "r1")
    original = text(project, STATE)
    (project / STATE).write_text(original.replace("<state the finding from r1>", "Hand edit")
                                .replace("## Next steps", "A handwritten note.\n\n## Next steps"))
    drift = provenance.findings_drift(project, "churn")
    assert drift == [{"result": "r1", "disk": "| Hand edit | [r1](evidence/r1.json) | provisional | association | |",
                      "rendered": "| <state the finding from r1> | [r1](evidence/r1.json) | provisional | association | |"}]
    json_before = text(project, f"{INV}/findings.json")
    code, out, _ = run(project, capsys, "render")
    assert code == 0 and out == "discarded: " + drift[0]["disk"] + "\n"
    assert unstamped(text(project, STATE)) == unstamped(original.replace("## Next steps", "A handwritten note.\n\n## Next steps"))
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
    assert provenance.flag_findings(project, "churn", flags) == {
        "flags": [], "unchanged": ["r1"], "rows": []}
    assert snapshot(project) == before
    provenance.flag_findings(project, "churn", [{"result": "r1", "reason": "Q-005"}])
    entry = json.loads(text(project, f"{INV}/findings.json"))["findings"][0]
    assert entry["flag_reason"] == "Q-004 correction; Q-005" and entry["prior_status"] == "provisional"
    produce(project, "r1", checks=GAPS)
    entry = json.loads(text(project, f"{INV}/findings.json"))["findings"][0]
    assert entry["notes"] == ["old note | detail"] and entry["flag_reason"] == "" and entry["prior_status"] is None
    assert r"| provisional | association | failed checks: columns; not assessed: joins; old note \| detail |" in text(project, STATE)
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
    assert text(project, STATE).count("| --- | --- | --- | --- | --- |") == 1
    assert provenance.findings_drift(project, "churn") == []


def test_render_recovers_malformed_and_stray_rows(project, capsys):
    produce(project, "r1")
    produce(project, "r2")
    original = text(project, STATE)
    row2 = "| <state the finding from r2> | [r2](evidence/r2.json) | provisional | association | |"
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
        provenance.update_findings(project, "churn", [result_id], text="Churn held", caveat="Agency workers excluded")
        provenance.update_findings(project, "churn", [result_id], status="supported", reason="checked")
    provenance.flag_findings(project, "churn", [{"result": "r1", "reason": "Q-004"}, {"result": "r2", "reason": "Q-004"}])
    produce(project, "r1", checks=totals)  # the correction changed r1's checks
    produce(project, "r2", checks=GAPS)
    assert "| provisional | association | failed checks: totals; Agency workers excluded |" in text(project, STATE)
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


CAUSAL = "causal (experiment: randomized price test, March 2026)"


def test_claim_strength_is_recorded_and_guarded(project, capsys):
    produce(project, "r1")
    entry = json.loads(text(project, f"{INV}/findings.json"))["findings"][0]
    assert (entry["claim"], entry["claim_basis"]) == ("association", "")
    assert "| provisional | association | |" in text(project, STATE)
    before = snapshot(project)
    for argv, message in [
            (["--claim", "causal", "--reason", "x"], "--claim causal needs --basis"),
            (["--claim", "causal", "--basis", "survey of store managers", "--reason", "x"], "--claim causal needs --basis"),
            (["--basis", "experiment: price test", "--reason", "x"], "give --status, --text, --caveat, or --claim"),
            (["--claim", "descriptive", "--basis", "experiment: price test", "--reason", "x"], "--basis goes only"),
            (["--claim", "causal", "--basis", "experiment: randomized price test, March 2026"], "--reason is required"),
            (["--claim", "strong"], "invalid choice")]:
        code, _, err = run(project, capsys, "finding", "r1", *argv)
        assert code == 2 and message in err, (argv, err)
    assert snapshot(project) == before
    produce(project, "r2")
    before = snapshot(project)
    code, _, err = run(project, capsys, "finding", "r1", "r2", "--claim", "descriptive", "--reason", "x")
    assert code == 2 and "several result IDs take --status only" in err and snapshot(project) == before
    code, out, _ = run(project, capsys, "finding", "r1", "--claim", "causal", "--basis",
                       "experiment:  randomized price test, March 2026", "--reason", "Stores were randomized.")
    assert code == 0 and f"| provisional | {CAUSAL} | |" in out
    assert f"r1 claim set to {CAUSAL}" in text(project, HISTORY)
    assert f'now "<state the finding from r1>" (provisional; claim {CAUSAL}).' in text(project, HISTORY)
    entry = json.loads(text(project, f"{INV}/findings.json"))["findings"][0]
    assert (entry["claim"], entry["claim_basis"]) == ("causal", "experiment: randomized price test, March 2026")
    produce(project, "r1", table="n\n2\n")  # a changed rerun keeps the claim
    assert f"| provisional | {CAUSAL} | |" in text(project, STATE)
    provenance.flag_findings(project, "churn", [{"result": "r1", "reason": "Q-004"}])
    before = snapshot(project)
    with pytest.raises(provenance.StateError, match="stronger claim or another design basis"):
        provenance.update_findings(project, "churn", ["r1"], claim="causal", basis="natural experiment: a store fire",
                                   reason="x")
    assert snapshot(project) == before
    result = provenance.update_findings(project, "churn", ["r1"], claim="association", reason="Randomization failed.")
    assert result["rows"] == ["| <state the finding from r1> | [r1](evidence/r1.json) | revalidation-needed (was "
                              "provisional) | association | Q-004 |"]
    with pytest.raises(provenance.StateError, match="stronger claim"):
        provenance.update_findings(project, "churn", ["r1"], claim="causal", basis="experiment: retest", reason="x")
    assert provenance.update_findings(project, "churn", ["r1"], claim="descriptive", reason="Narrowed.")["rows"]


@pytest.mark.parametrize("change", [
    lambda entry: entry.pop("claim"),
    lambda entry: entry.update(claim=""),
    lambda entry: entry.update(claim="causal"),  # no design basis
    lambda entry: entry.update(claim="association", claim_basis="experiment: price test"),
    lambda entry: entry.pop("claim_basis")])
def test_absent_claim_strength_is_refused(project, change):
    produce(project, "r1")
    path = project / INV / "findings.json"
    content = json.loads(path.read_text())
    change(content["findings"][0])
    path.write_text(json.dumps(content))
    before = snapshot(project)
    for writer in (lambda: provenance.update_findings(project, "churn", ["r1"], text="x"),
                   lambda: provenance.flag_findings(project, "churn", [{"result": "r1", "reason": "Q-004"}]),
                   lambda: provenance.render_findings(project, "churn"),
                   lambda: provenance.findings_drift(project, "churn"),
                   lambda: produce(project, "r1", table="n\n5\n")):
        with pytest.raises(provenance.StateError, match="no valid claim strength"):
            writer()
    assert snapshot(project) == before


DRAFT = ROOT / ".agents/skills/awb-package/assets/awb_draft.py"


def test_finding_text_warns_on_numbers_its_result_does_not_record(project, capsys):
    (project / "src/packaging").mkdir()
    shutil.copyfile(DRAFT, project / "src/packaging/draft.py")
    produce(project, "r1", table="rate,accounts\n0.12483,1204\n")
    produce(project, "r2", table="rate,accounts\n0.5,10\n")
    code, out, _ = run(project, capsys, "finding", "r1", "--text", "Churn reached 12.5% of 1,204 accounts, not 478")
    assert code == 0
    # 12.5% traces to 0.12483 at its written precision, and 1,204 to the table; 478 is recorded nowhere.
    assert out.splitlines()[0] == ("warning: r1: 478 is not a value its table, profile, checks, or settings "
                                   "record; check the number or reword")
    assert len(out.splitlines()) == 2 and "| Churn reached 12.5% of 1,204 accounts, not 478 |" in out
    assert json.loads(text(project, f"{INV}/findings.json"))["findings"][0]["text"].endswith("not 478")
    # Promotion reads the row's text too, warns, and still promotes.
    set_row(project, "r2", "Churn reached 40% in the west")
    code, out, _ = run(project, capsys, "finding", "r2", "--status", "supported", "--reason", "Checked.")
    assert code == 0 and out.startswith("warning: r2: 40% is not a value") and "| supported |" in out
    # Without the package reader the numbers go unread, and provenance still writes.
    (project / "src/packaging/draft.py").unlink()
    code, out, _ = run(project, capsys, "finding", "r1", "--text", "Churn reached 99% of 7 accounts")
    assert code == 0 and not out.startswith("warning")
    (project / "src/packaging/draft.py").write_text("raise ImportError('broken copy')\n")
    code, out, _ = run(project, capsys, "finding", "r1", "--text", "Churn reached 98% of 7 accounts")
    assert code == 0 and out.startswith("warning: numbers not checked: src/packaging/draft.py did not load "
                                        "(ImportError: broken copy)")


SUMS = [{"name": "values", "outcome": "pass", "detail": "Country rows plus aggregates sum to World within 0.1%."}]
SCOPE = [{"name": "scope", "outcome": "pass", "detail": "Checked all date filters are explicit."}]
RECONCILED = [{"name": "row_counts", "outcome": "pass", "detail": "Steps checked: 1; last 5 -> 3 rows; reconciled: "
               "order filter 5 = 3 kept + 2 excluded (cancelled 2)."}]


def test_finding_text_warns_on_reconciliation_no_check_records(project, capsys):
    produce(project, "r1")
    produce(project, "r2", checks=OK + SUMS)
    produce(project, "r3", checks=[{**SUMS[0], "outcome": "fail"}])
    produce(project, "r4", checks=OK + SCOPE)
    produce(project, "r5", checks=OK + RECONCILED)
    wording = "Countries plus regions sums to World"
    for result_id, warned in (("r1", True), ("r2", False), ("r3", True), ("r4", True), ("r5", True)):
        code, out, _ = run(project, capsys, "finding", result_id, "--text", wording)
        assert code == 0 and f"| {wording} | [{result_id}]" in out, result_id
        warning = (f'warning: {result_id}: "sums to" asserts a reconciliation or a completed check that no passing '
                   "check in its evidence records; state the check, with any tolerance the brief or the "
                   "result's settings record, in the detail of a passing values or metrics judgment in "
                   f"[results.{result_id}.validation] and rerun, or reword")
        assert (out.splitlines()[0] == warning) is warned, (result_id, out)
    for phrase, found in (("The totals reconciled with finance", "reconciled"),
                          ("We checked every region", "checked every"), ("Parts ADD UP TO the total", "ADD UP TO"),
                          ("We verified each order", "verified each")):
        code, out, _ = run(project, capsys, "finding", "r1", "--text", phrase)
        assert out.startswith(f'warning: r1: "{found}" asserts'), phrase
    code, out, _ = run(project, capsys, "finding", "r4", "--text", "We checked every region")
    assert code == 0 and not out.startswith("warning"), out
    code, out, _ = run(project, capsys, "finding", "r2", "--text", "We checked every region")
    assert out.startswith('warning: r2: "checked every" asserts'), out
    # A filter's reconciled row count backs reconcile wording only; a sum judgment never backs it.
    code, out, _ = run(project, capsys, "finding", "r5", "--text", "The order filter reconciles")
    assert code == 0 and not out.startswith("warning"), out
    code, out, _ = run(project, capsys, "finding", "r2", "--text", "The order filter reconciles")
    assert out.startswith('warning: r2: "reconciles" asserts'), out
    for phrase in ("Summary of totals", "A check-in rate of half", "Sums of orders rose"):
        code, out, _ = run(project, capsys, "finding", "r1", "--text", phrase)
        assert not out.startswith("warning"), phrase


@pytest.mark.parametrize("content", ["{broken", "[]"])
def test_finding_text_with_unreadable_evidence_warns_and_writes(project, capsys, content):
    produce(project, "r1")
    (project / INV / "evidence/r1.json").write_text(content)
    code, out, _ = run(project, capsys, "finding", "r1", "--text", "West took 2 orders")
    assert code == 0
    assert out.startswith("warning: r1: numbers and wording not checked: evidence/r1.json is unreadable (")
    assert "| West took 2 orders | [r1]" in out
    assert json.loads(text(project, f"{INV}/findings.json"))["findings"][0]["text"] == "West took 2 orders"


@pytest.mark.parametrize("caveat, notes", [
    ("a (b; c); d", ["a (b; c)", "d"]),
    ("x [y; (z; w)]; v", ["x [y; (z; w)]", "v"]),
    ("1) agency staff excluded; 2) March partial", ["1) agency staff excluded", "2) March partial"]),
    ("one note", ["one note"]),
    ("Scale [0, 1); two years", ["Scale [0, 1)", "two years"]),
    ("a (b]; c", ["a (b]", "c"]),
    ("Excludes March (partial month", ["Excludes March (partial month"]),
    ("(a; b) (c", ["(a; b) (c"]),
    ("a (b; c", None),
    ("a (b) [c; d", None),
])
def test_caveat_splits_notes_outside_brackets(project, capsys, caveat, notes):
    produce(project, "r1")
    before = snapshot(project)
    code, _, err = run(project, capsys, "finding", "r1", "--caveat", caveat)
    if notes is None:
        assert code == 2 and "--caveat" in err and "bracket" in err and snapshot(project) == before
    else:
        assert code == 0
        assert json.loads(text(project, f"{INV}/findings.json"))["findings"][0]["notes"] == notes
    code, out, _ = run(project, capsys, "finding", "--help")
    assert code == 0 and "';' outside parentheses and square brackets separates notes" in " ".join(out.split())


def test_package_promotion_command_runs(project, capsys):
    produce(project, "r1")
    set_row(project, "r1", "Churn held")
    skill = " ".join((ROOT / ".agents/skills/awb-package/SKILL.md").read_text(encoding="utf-8").split())
    command = re.search(r"behind an approved headline with `python3 src/awb\.py state ([^`]+)`", skill)[1]
    argv = [{"<result-id>": "r1", "<why>": "The user approved its headline."}.get(word, word)
            for word in shlex.split(command)]
    code, out, _ = run(project, capsys, *argv)
    assert code == 0 and "| supported |" in out
    produce(project, "r2")
    set_row(project, "r2", "Churn fell")
    bare = [{"r1": "r2"}.get(word, word) for word in argv if word not in ("--reason", "The user approved its headline.")]
    code, _, err = run(project, capsys, *bare)
    assert code == 2 and "--reason is required" in err
