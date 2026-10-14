# Kept cases:
# test_add_numbers_and_renders: add allocates Q-NNN in order, renders questions.md whole from questions.json, and refuses empty text, unknown choices, and a parked or declined question without a reason.
# test_hand_edits_are_drift: every writer refuses a hand-edited questions.md and writes nothing; render restores it; questions.md without questions.json is refused.
# test_person_answers: an answer needs text with who gave it; a data question refuses one; declined or superseded questions refuse answers; a repeated answer is unchanged.
# test_run_links_declared_answers: a result declaring answers marks open questions answered on record_finding, links an answered one again, skips declined ones, and reports them; undeclared results return the old shape.
# test_answers_are_validated_before_evidence: answers must be Q-NNN IDs the ledger holds, refused before any evidence is written.
# test_answers_never_stale_a_result: adding answers to a recorded result leaves stale and the exact-rerun baseline unchanged.
# test_answer_by_result_needs_declaration: linking an existing result needs its findings row and its settings declaration.
# test_status_transitions: answered can only be superseded, keeping its answer; open reopens parked or declined and is a no-op on open; reasons are required; only open or parked questions are edited.
# test_status_collector_reads_the_ledger: collect_status reports counts, open questions by answerer, and answers resting only on flagged findings; null without a ledger; a malformed one is an uncertainty.
# test_resume_and_list_show_finding_status: state shows open questions and those answered only by flagged findings; list shows each linked finding's current status.

from datetime import date
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess

import pytest

if shutil.which("git") is None:
    pytest.skip("git is required", allow_module_level=True)

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / ".agents/skills/awb-init/assets/workbench"
spec = importlib.util.spec_from_file_location("awb_provenance_questions",
                                              ROOT / ".agents/skills/awb-init/assets/awb_provenance.py")
provenance = importlib.util.module_from_spec(spec)
spec.loader.exec_module(provenance)
spec = importlib.util.spec_from_file_location("awb_status_questions",
                                              ROOT / ".agents/skills/awb-status/scripts/collect_status.py")
status = importlib.util.module_from_spec(spec)
spec.loader.exec_module(status)

TODAY = date.today().isoformat()
INV = "investigations/churn"
OK = [{"name": "columns", "outcome": "pass", "detail": "Required columns present: 1."}]


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True).stdout.strip()


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*")
            if p.is_file() and ".git" not in p.parts}


@pytest.fixture
def project(tmp_path):
    git(tmp_path, "init")
    readme = (TEMPLATES / "README.md").read_text().replace(
        "Active investigation: none", "Active investigation: [churn](investigations/churn/state.md)")
    (tmp_path / "README.md").write_text(readme)
    directory = tmp_path / INV
    (directory / "queries").mkdir(parents=True)
    for record in ("state.md", "history.md", "brief.md"):
        shutil.copyfile(TEMPLATES / "investigation" / record, directory / record)
    state = directory / "state.md"
    state.write_text(state.read_text().replace("<!-- use an ISO date -->", "2026-09-01"))
    settings(tmp_path, {})
    for i in range(1, 4):
        (directory / f"queries/r{i}.sql").write_text(f"select {i}\n")
    git(tmp_path, "add", "-A")
    git(tmp_path, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "commit.gpgsign=false",
        "commit", "-qm", "work")
    return tmp_path


def settings(root, answers):
    """Write settings.toml with results r1-r3, each declaring the answers given for it."""
    text = "[parameters]\nyear = 2026\n"
    for i in range(1, 4):
        text += f'\n[results.r{i}]\nquestion = "What is question {i}?"\n'
        if f"r{i}" in answers:
            text += f"answers = {json.dumps(answers[f'r{i}'])}\n"
    (root / INV / "settings.toml").write_text(text)


def produce(project, result_id, table="n\n1\n"):
    prior = provenance.prior_result(project, "churn", result_id)
    (project / INV / "evidence" / f"{result_id}.json").unlink(missing_ok=True)
    (project / INV / "results").mkdir(exist_ok=True)
    (project / INV / "results" / f"{result_id}.csv").write_text(table)
    provenance.record_evidence(project, "churn", result_id, views=[], checks=OK, settings_path=f"{INV}/settings.toml")
    return provenance.record_finding(project, "churn", result_id, OK, prior=prior, today=TODAY)


def add(project, text, answerer="data", **options):
    return provenance.add_question(project, "churn", text, kind=options.pop("kind", "analytical"),
                                   answerer=answerer, origin=options.pop("origin", "scope"), today=TODAY, **options)


def ledger(project):
    return {e["id"]: e for e in json.loads((project / INV / "questions.json").read_text())["questions"]}


def cli(project, capsys, *argv):
    code = provenance.cli_questions(project, list(argv))
    out = capsys.readouterr()
    return code, out.out, out.err


def test_add_numbers_and_renders(project, capsys):
    assert add(project, "Does  churn differ\nby region?", unblocks="the regional cut")["id"] == "Q-001"
    assert add(project, "Which churn definition does finance use?", "stakeholder", kind="context")["id"] == "Q-002"
    code, out, _ = cli(project, capsys, "add", "Is EMEA in scope?", "--kind", "decision", "--answerer", "user",
                       "--origin", "brainstorm", "--status", "declined", "--reason", "outside the decision")
    assert code == 0 and out == "Q-003 declined: Is EMEA in scope?\n"
    md = (project / INV / "questions.md").read_text()
    assert md.startswith("# Question ledger\n")
    assert "| Q-001 | Does churn differ by region? | analytical | data | the regional cut | open | |" in md
    assert "| Q-003 | Is EMEA in scope? | decision | user | | declined | outside the decision |" in md
    assert ledger(project)["Q-001"]["text"] == "Does churn differ by region?"
    before = snapshot(project)
    for options in ({"text": " "}, {"kind": "other"}, {"status": "parked"}, {"status": "open", "reason": "x"}):
        text = options.pop("text", "A question?")
        with pytest.raises(ValueError):
            provenance.add_question(project, "churn", text, kind=options.pop("kind", "context"), answerer="user",
                                    origin="scope", **options)
    assert snapshot(project) == before
    assert cli(project, capsys, "add", "x", "--kind", "context")[0] == 2
    assert cli(project, capsys)[0] == 2 and cli(project, capsys, "--help")[0] == 0


def test_hand_edits_are_drift(project, capsys):
    add(project, "Does churn differ by region?")
    md = project / INV / "questions.md"
    md.write_text(md.read_text().replace("open", "answered"))
    before = snapshot(project)
    for argv in (["add", "Another?", "--kind", "context", "--answerer", "user", "--origin", "scope"],
                 ["status", "Q-001", "--set", "parked", "--reason", "later"], ["edit", "Q-001", "--text", "New?"]):
        code, _, err = cli(project, capsys, *argv)
        assert code == 1 and "questions drift" in err and "questions render" in err
    assert snapshot(project) == before
    code, out, _ = cli(project, capsys, "render")
    assert code == 0 and out == "questions.md restored\n" and "| open |" in md.read_text()
    assert cli(project, capsys, "render")[1] == "questions.md matches questions.json\n"
    (project / INV / "questions.json").unlink()
    code, _, err = cli(project, capsys, "list")
    assert code == 1 and "exists without" in err


def test_person_answers(project, capsys):
    add(project, "Which churn definition does finance use?", "stakeholder", kind="context")
    add(project, "Does churn differ by region?")
    with pytest.raises(ValueError, match="--text and --by"):
        provenance.answer_question(project, "churn", "Q-001", text="Logo churn")
    entry = provenance.answer_question(project, "churn", "Q-001", text="Logo churn, monthly", by="CFO", today=TODAY)
    assert entry["changed"] and entry["status"] == "answered"
    assert f"| answered | Logo churn, monthly (CFO, {TODAY}) |" in (project / INV / "questions.md").read_text()
    assert not provenance.answer_question(project, "churn", "Q-001", text="Logo churn, monthly", by="CFO")["changed"]
    code, _, err = cli(project, capsys, "answer", "Q-002", "--text", "yes", "--by", "user")
    assert code == 1 and "data question" in err
    provenance.set_question(project, "churn", ["Q-002"], "declined", reason="not needed")
    with pytest.raises(provenance.StateError, match="declined"):
        provenance.answer_question(project, "churn", "Q-002", results=["r1"])


def test_run_links_declared_answers(project):
    for text in ("Does churn differ by region?", "Is churn seasonal?", "Is churn tied to price?"):
        add(project, text)
    provenance.set_question(project, "churn", ["Q-003"], "declined", reason="out of scope")
    assert produce(project, "r2") == {"action": "added", "status": "provisional", "claim": "association",
                                      "history": False}
    settings(project, {"r1": ["Q-001", "Q-003"], "r3": ["Q-001", "Q-002"]})
    first = produce(project, "r1")
    assert first["questions"] == {"answered": ["Q-001"], "linked": [], "skipped": ["Q-003 (declined)"]}
    second = produce(project, "r3")
    assert second["questions"] == {"answered": ["Q-002"], "linked": ["Q-001"], "skipped": []}
    entries = ledger(project)
    assert entries["Q-001"]["results"] == ["r1", "r3"] and entries["Q-003"]["status"] == "declined"
    assert "| answered | [r1](evidence/r1.json); [r3](evidence/r3.json) |" in (project / INV / "questions.md").read_text()
    before = snapshot(project)
    assert produce(project, "r1")["questions"] == {"answered": [], "linked": [], "skipped": ["Q-003 (declined)"]}
    assert (project / INV / "questions.json").read_bytes() == before[f"{INV}/questions.json"]


def test_answers_are_validated_before_evidence(project):
    settings(project, {"r1": ["Q-001"]})
    with pytest.raises(ValueError, match="questions.json does not hold"):
        produce(project, "r1")
    settings(project, {"r1": ["first"]})
    assert provenance.result_problems("r1", {"question": "q", "answers": ["first"]}) == [
        '[results.r1] answers must be a list of question IDs, as answers = ["Q-001"]']
    with pytest.raises(ValueError, match="answers must be a list"):
        produce(project, "r1")
    assert not (project / INV / "evidence" / "r1.json").exists()


def test_answers_never_stale_a_result(project):
    add(project, "Does churn differ by region?")
    produce(project, "r1")
    evidence = project / INV / "evidence" / "r1.json"
    settings(project, {"r1": ["Q-001"]})
    assert all(c["outcome"] == "pass" for c in provenance.compare_evidence(project, evidence)
               if c["name"] == "settings")
    rerun = produce(project, "r1")
    assert rerun["action"] == "kept" and rerun["questions"]["answered"] == ["Q-001"]
    (project / INV / "settings.toml").write_text((project / INV / "settings.toml").read_text()
                                                 .replace("year = 2026", "year = 2025"))
    assert [c["outcome"] for c in provenance.compare_evidence(project, evidence) if c["name"] == "settings"] == ["fail"]


def test_answer_by_result_needs_declaration(project, capsys):
    add(project, "Does churn differ by region?")
    code, _, err = cli(project, capsys, "answer", "Q-001", "--result", "r1")
    assert code == 1 and "no findings row" in err
    produce(project, "r1")
    code, _, err = cli(project, capsys, "answer", "Q-001", "--result", "r1")
    assert code == 1 and 'does not declare answers = ["Q-001"]' in err
    settings(project, {"r1": ["Q-001"]})
    code, out, _ = cli(project, capsys, "answer", "Q-001", "--result", "r1")
    assert code == 0 and "| answered | [r1](evidence/r1.json) |" in out
    assert cli(project, capsys, "answer", "Q-001", "--result", "r1")[1].startswith("unchanged: ")


def test_status_transitions(project):
    add(project, "Which churn definition does finance use?", "user", kind="context")
    add(project, "Is churn seasonal?", "user", kind="decision")
    provenance.answer_question(project, "churn", "Q-001", text="Logo churn", by="user")
    for status in ("open", "parked", "declined"):
        with pytest.raises(provenance.StateError, match="supersede it"):
            provenance.set_question(project, "churn", ["Q-001"], status, reason="x")
    with pytest.raises(ValueError, match="--reason"):
        provenance.set_question(project, "churn", ["Q-001"], "superseded")
    assert provenance.set_question(project, "churn", ["Q-001"], "superseded", reason="scope widened") == ["Q-001"]
    assert ledger(project)["Q-001"]["answer"] == "Logo churn"
    with pytest.raises(provenance.StateError):
        provenance.set_question(project, "churn", ["Q-001"], "open")
    assert provenance.set_question(project, "churn", ["Q-002"], "open") == []
    provenance.set_question(project, "churn", ["Q-002"], "parked", reason="after the first cut")
    assert provenance.set_question(project, "churn", ["Q-002"], "open") == ["Q-002"]
    assert ledger(project)["Q-002"]["reason"] == ""
    assert provenance.edit_question(project, "churn", "Q-002", text="Is churn seasonal by quarter?")
    with pytest.raises(provenance.StateError, match="only an open or parked"):
        provenance.edit_question(project, "churn", "Q-001", text="x")


def test_resume_and_list_show_finding_status(project, capsys):
    add(project, "Does churn differ by region?")
    add(project, "Which churn definition does finance use?", "stakeholder", kind="context")
    settings(project, {"r1": ["Q-001"]})
    produce(project, "r1")
    code, out, _ = cli(project, capsys, "list", "--all")
    assert code == 0 and out.splitlines() == [
        "Q-001 answered [data, analytical] Does churn differ by region? -> r1 (provisional)",
        "Q-002 open [stakeholder, context] Which churn definition does finance use?"]
    view = provenance.state_view(project, "churn")
    assert view.endswith("==> open ledger questions <==\n"
                         "Q-002 open [stakeholder, context] Which churn definition does finance use?\n")
    provenance.flag_findings(project, "churn", [{"result": "r1", "reason": "region view corrected"}])
    assert "Q-001 answered by r1 (revalidation-needed (was provisional))" in provenance.state_view(project, "churn")
    assert cli(project, capsys, "list", "--investigation", "absent")[0] == 2


def test_status_collector_reads_the_ledger(project):
    assert status.collect(project)["active"]["questions"] is None
    add(project, "Does churn differ by region?")
    add(project, "Which churn definition does finance use?", "stakeholder", kind="context")
    add(project, "Is EMEA in scope?", "user", kind="decision", status="declined", reason="no")
    settings(project, {"r1": ["Q-001"]})
    produce(project, "r1")
    provenance.flag_findings(project, "churn", [{"result": "r1", "reason": "region view corrected"}])
    questions = status.collect(project)["active"]["questions"]
    assert questions == {"counts": {"answered": 1, "open": 1, "declined": 1}, "open_by_answerer": {"stakeholder": 1},
                         "open": ["Q-002 [stakeholder, context] Which churn definition does finance use?"],
                         "answered_by_unsettled": ["Q-001 answered by r1 (revalidation-needed (was provisional))"]}
    (project / INV / "questions.json").write_text('{"schema": "awb-questions/1", "questions": [1]}')
    result = status.collect(project)
    assert result["active"]["questions"] is None
    assert any("question ledger" in item["reason"] for item in result["uncertainties"])
