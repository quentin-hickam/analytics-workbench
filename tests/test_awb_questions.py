# Kept cases:
# test_add_numbers_and_renders: render on an investigation without a ledger writes both files and says so; add allocates Q-NNN in order, renders questions.md whole from questions.json, and refuses empty text, unknown choices, and a parked or declined question without a reason.
# test_hand_edits_are_drift: every writer refuses a hand-edited questions.md and writes nothing; render restores it; questions.md without questions.json is refused by every command, render included, so no ID is reused.
# test_person_answers: an answer needs text with who gave it; a data question refuses one; declined or superseded questions refuse answers; a repeated answer is unchanged; a different answer to an answered question is refused.
# test_run_links_declared_answers: a result declaring answers marks open questions answered on record_finding, links an answered one again, skips declined ones, and reports them; undeclared results return the old shape.
# test_answers_are_validated_before_evidence: answers must be Q-NNN IDs the ledger holds, refused before any evidence is written.
# test_run_checks_answers_before_running: run.py exits 2 on an answers ID the ledger lacks or a person answers, and 1 on an unreadable ledger, before opening a session or replacing evidence.
# test_answers_never_stale_a_result: adding answers to a recorded result leaves stale and the exact-rerun baseline unchanged.
# test_answer_by_result_needs_declaration: linking an existing result needs its findings row and its settings declaration.
# test_linking_reads_the_recorded_settings_file: a result recorded from another settings file is linked from that file, by run and by hand; unreadable evidence refuses a hand link.
# test_results_answer_only_data_questions: answers naming a user or stakeholder question is refused before evidence, by run.py, and by a hand link; link_answers skips one; the person's answer is still taken; a ledger linking results to a person's question is malformed.
# test_status_transitions: answered can only be superseded, keeping its answer; open reopens parked or declined and is a no-op on open; reasons are required; only open or parked questions are edited, and a data question keeps answerer data; a superseded answer stays visible in questions.md and list.
# test_status_collector_reads_the_ledger: collect_status reports counts, the root and must sub-question counts, open questions by answerer, and derived answers awaiting recheck or provisional; null without a ledger; a malformed one, or questions.md without questions.json, is an uncertainty.
# test_resume_and_list_show_finding_status: state shows open questions and answers awaiting recheck or provisional until promoted; list shows each linked finding's current status.

from datetime import date
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

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


def produce(project, result_id, table="n\n1\n", settings_path=f"{INV}/settings.toml"):
    prior = provenance.prior_result(project, "churn", result_id)
    (project / INV / "evidence" / f"{result_id}.json").unlink(missing_ok=True)
    (project / INV / "results").mkdir(exist_ok=True)
    (project / INV / "results" / f"{result_id}.csv").write_text(table)
    provenance.record_evidence(project, "churn", result_id, views=[], checks=OK, settings_path=settings_path)
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
    assert cli(project, capsys, "render")[:2] == (0, "questions.json and questions.md written\n")
    assert ledger(project) == {} and cli(project, capsys, "render")[1] == "questions.md matches questions.json\n"
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


@pytest.mark.parametrize("before_text, after_text", [("open", "answered"), ("Where does churn differ?", "Who left?")])
def test_hand_edits_are_drift(project, capsys, before_text, after_text):
    add(project, "Does churn differ by region?", audience="Where does churn differ?")
    add(project, "Which definition?", "user", kind="context")
    md = project / INV / "questions.md"
    md.write_text(md.read_text().replace(before_text, after_text))
    before = snapshot(project)
    for argv in (["add", "Another?", "--kind", "context", "--answerer", "user", "--origin", "scope"],
                 ["status", "Q-001", "--set", "parked", "--reason", "later"], ["edit", "Q-001", "--text", "New?"],
                 ["edit", "Q-001", "--audience", "New wording?"],
                 ["answer", "Q-002", "--text", "Revenue", "--by", "user"]):
        code, _, err = cli(project, capsys, *argv)
        assert code == 1 and "questions drift" in err and "questions render" in err
    assert snapshot(project) == before
    code, out, _ = cli(project, capsys, "render")
    assert code == 0 and out == "questions.md restored\n" and "| open |" in md.read_text()
    assert cli(project, capsys, "render")[1] == "questions.md matches questions.json\n"
    (project / INV / "questions.json").unlink()
    before = snapshot(project)
    for argv in (["list"], ["render"], ["add", "Another?", "--kind", "context", "--answerer", "user", "--origin", "scope"]):
        code, _, err = cli(project, capsys, *argv)
        assert code == 1 and "exists without" in err
    assert snapshot(project) == before and "| Q-001 |" in md.read_text()


@pytest.mark.parametrize("trouble, diagnostic, repair", [
    ("drift", "questions drift", "python3 src/awb.py questions render --investigation churn discards the hand edit"),
    ("malformed", "questions.json", "repair it or restore it from Git"),
    ("missing", "exists without", "restore questions.json from Git"),
])
@pytest.mark.parametrize("action", ["record", "flag", "update", "render"])
def test_finding_writes_preserve_evidence_under_ledger_trouble(project, trouble, diagnostic, repair, action):
    # These results answer nothing: an unrelated ledger cannot invalidate their writes.
    produce(project, "r1")
    provenance.update_findings(project, "churn", ["r1"], status="supported", text="One account remained",
                               reason="checks passed")
    add(project, "Which segment next?")
    md, data = project / INV / "questions.md", project / INV / "questions.json"
    if trouble == "drift":
        md.write_text(md.read_text() + "Keep this hand edit.\n")
    elif trouble == "malformed":
        data.write_text("{")
    else:
        data.unlink()
    saved_md = md.read_bytes()
    saved_history = (project / INV / "history.md").read_bytes()
    evidence = project / INV / "evidence/r1.json"
    saved_evidence = evidence.read_bytes()
    if action == "record":
        result = produce(project, "r1", table="n\n2\n")
        assert result["action"] == "refreshed" and result["history"]
    elif action == "flag":
        result = provenance.flag_findings(project, "churn", [{"result": "r1", "reason": "source corrected"}])
    elif action == "update":
        result = provenance.update_findings(project, "churn", ["r1"], status="superseded", reason="new scope")
    else:
        result = provenance.render_findings(project, "churn")
    assert diagnostic in result["questions"]["error"] and repair in result["questions"]["error"]
    assert result["questions"]["error"].count("questions render") <= 1
    assert md.read_bytes() == saved_md and evidence.is_file()
    assert json.loads(evidence.read_text())["result_id"] == "r1"
    if action != "record":
        assert evidence.read_bytes() == saved_evidence
    assert provenance.findings_drift(project, "churn") == []
    if action in ("record", "update"):
        assert (project / INV / "history.md").read_bytes() != saved_history
    else:
        assert (project / INV / "history.md").read_bytes() == saved_history


def test_declaring_result_under_ledger_drift_names_the_link(project):
    settings(project, {"r1": ["Q-001"]})
    add(project, "Does churn differ by region?")
    md = project / INV / "questions.md"
    md.write_text(md.read_text() + "Keep this hand edit.\n")
    result = produce(project, "r1")
    assert result["action"] == "added" and (project / INV / "evidence/r1.json").is_file()
    assert result["questions"]["error"].startswith("questions drift:")
    assert result["questions"]["error"].endswith("; then link with `awb.py questions answer <Q-NNN> --result r1`")
    assert ledger(project)["Q-001"]["status"] == "open"
    provenance.cli_questions(project, ["render"])
    assert produce(project, "r1")["questions"] == {"answered": ["Q-001"], "linked": [], "skipped": []}


def test_person_answers(project, capsys):
    add(project, "Which churn definition does finance use?", "stakeholder", kind="context")
    add(project, "Does churn differ by region?")
    with pytest.raises(ValueError, match="--text and --by"):
        provenance.answer_question(project, "churn", "Q-001", text="Logo churn")
    entry = provenance.answer_question(project, "churn", "Q-001", text="Logo churn, monthly", by="CFO", today=TODAY)
    assert entry["changed"] and entry["status"] == "answered"
    assert f"| answered | Logo churn, monthly (CFO, {TODAY}) |" in (project / INV / "questions.md").read_text()
    assert not provenance.answer_question(project, "churn", "Q-001", text="Logo churn, monthly", by="CFO")["changed"]
    before = snapshot(project)
    for text, by in (("Revenue churn", "CFO"), ("Logo churn, monthly", "Analyst")):
        with pytest.raises(provenance.StateError, match="never replaced.*superseded"):
            provenance.answer_question(project, "churn", "Q-001", text=text, by=by)
    code, _, err = cli(project, capsys, "answer", "Q-001", "--text", "60 days", "--by", "Analyst")
    assert code == 1 and "never replaced" in err and snapshot(project) == before
    settings(project, {"r1": ["Q-002"]})
    produce(project, "r1")
    code, _, err = cli(project, capsys, "answer", "Q-002", "--text", "yes", "--by", "user")
    assert code == 1 and "data question" in err
    provenance.set_question(project, "churn", ["Q-002"], "superseded", reason="not needed")
    with pytest.raises(provenance.StateError, match="superseded"):
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
    # Stored answered; displayed provisional while no answering finding is promoted.
    assert "| answered (provisional) | [r1](evidence/r1.json); [r3](evidence/r3.json) |" in (
        project / INV / "questions.md").read_text()
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


def test_run_checks_answers_before_running(project):
    assets = ROOT / ".agents/skills/awb-init/assets"
    (project / "src/exploration").mkdir(parents=True)
    (project / "src/preparation").mkdir()
    shutil.copyfile(assets / "awb_provenance.py", project / "src/provenance.py")
    # Stand-ins for the duckdb and pandas helpers: opening a session would leave a marker.
    (project / "src/exploration/validate.py").write_text("profile = validate = None\n")
    (project / "src/preparation/landing.py").write_text(
        "from pathlib import Path\n\ndef session(root):\n    Path(root, 'opened').touch()\n    raise SystemExit(9)\n")
    shutil.copyfile(TEMPLATES / "investigation/run.py", project / INV / "run.py")
    add(project, "Does churn differ by region?")
    produce(project, "r1")
    saved = (project / INV / "evidence/r1.json").read_bytes()
    settings(project, {"r1": ["Q-001", "Q-999"]})
    run = [sys.executable, str(project / INV / "run.py"), "r1"]
    done = subprocess.run(run, capture_output=True, text=True)
    assert (done.returncode, done.stdout) == (2, "") and "answers Q-999, which questions.json does not hold" in done.stderr
    (project / INV / "questions.json").write_text("{}")
    done = subprocess.run(run, capture_output=True, text=True)
    assert done.returncode == 1 and "questions.json" in done.stderr
    assert not (project / "opened").exists() and (project / INV / "evidence/r1.json").read_bytes() == saved
    for name in ("questions.json", "questions.md"):
        (project / INV / name).unlink()
    add(project, "Does churn differ by region?")
    add(project, "What counts as churn for finance?", "stakeholder", kind="context")
    settings(project, {"r1": ["Q-001", "Q-002"]})
    done = subprocess.run(run, capture_output=True, text=True)
    assert done.returncode == 2 and "answers Q-002 (stakeholder), which a person answers" in done.stderr
    assert not (project / "opened").exists() and (project / INV / "evidence/r1.json").read_bytes() == saved
    done = subprocess.run(run[:-1] + ["r2"], capture_output=True, text=True)
    assert done.returncode == 9 and (project / "opened").exists()  # a result declaring no answers skips the ledger


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


def test_linking_reads_the_recorded_settings_file(project, capsys):
    for text in ("Does churn differ by region?", "Is churn seasonal?", "Is churn tied to price?"):
        add(project, text)
    analysis = project / INV / "analysis.toml"
    analysis.write_text('[results.r2]\nquestion = "Does churn differ by region?"\nanswers = ["Q-001"]\n')
    assert produce(project, "r2", settings_path=f"{INV}/analysis.toml")["questions"] == {
        "answered": ["Q-001"], "linked": [], "skipped": []}
    assert ledger(project)["Q-001"]["results"] == ["r2"]
    analysis.write_text(analysis.read_text().replace('["Q-001"]', '["Q-001", "Q-002"]'))
    code, out, _ = cli(project, capsys, "answer", "Q-002", "--result", "r2")
    assert code == 0 and "| answered | [r2](evidence/r2.json) |" in out
    code, _, err = cli(project, capsys, "answer", "Q-003", "--result", "r2")
    assert code == 1 and f'does not declare answers = ["Q-003"] in {INV}/analysis.toml' in err
    (project / INV / "evidence/r2.json").write_text("{}")
    before = snapshot(project)
    code, _, err = cli(project, capsys, "answer", "Q-003", "--result", "r2")
    assert code == 1 and "evidence/r2.json does not name a readable settings file" in err and snapshot(project) == before


def test_results_answer_only_data_questions(project, capsys):
    add(project, "What counts as churn for finance?", "stakeholder", kind="context")
    add(project, "Is EMEA in scope?", "user", kind="decision")
    settings(project, {"r1": ["Q-001", "Q-002"]})
    with pytest.raises(ValueError, match=r"answers Q-001 \(stakeholder\), Q-002 \(user\), which a person answers"):
        produce(project, "r1")
    assert not (project / INV / "evidence" / "r1.json").exists()
    settings(project, {})
    produce(project, "r1")
    settings(project, {"r1": ["Q-001"]})
    before = snapshot(project)
    code, _, err = cli(project, capsys, "answer", "Q-001", "--result", "r1")
    assert code == 1 and "stakeholder question; only a person's answer settles it" in err
    assert provenance.link_answers(project, "churn", "r1") == {"answered": [], "linked": [], "skipped": ["Q-001 (stakeholder)"]}
    assert snapshot(project) == before
    entry = provenance.answer_question(project, "churn", "Q-001", text="No payment for 60 days", by="CFO")
    assert entry["changed"] and entry["status"] == "answered" and entry["results"] == []
    content = json.loads((project / INV / "questions.json").read_text())
    content["questions"][1]["results"] = ["r1"]
    (project / INV / "questions.json").write_text(json.dumps(content))
    code, _, err = cli(project, capsys, "list")
    assert code == 1 and "only a data question links results" in err


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
    assert "| superseded | scope widened; was answered: Logo churn (user) |" in (project / INV / "questions.md").read_text()
    assert provenance.question_lines(project, "churn", ("superseded",)) == [
        "Q-001 superseded [user, context, should; parent: root] Which churn definition does finance use? -- scope widened; "
        "was answered: Logo churn (user)"]
    with pytest.raises(provenance.StateError):
        provenance.set_question(project, "churn", ["Q-001"], "open")
    assert provenance.set_question(project, "churn", ["Q-002"], "open") == []
    provenance.set_question(project, "churn", ["Q-002"], "parked", reason="after the first cut")
    assert provenance.set_question(project, "churn", ["Q-002"], "open") == ["Q-002"]
    assert ledger(project)["Q-002"]["reason"] == ""
    assert provenance.edit_question(project, "churn", "Q-002", text="Is churn seasonal by quarter?")
    with pytest.raises(provenance.StateError, match="only an open or parked"):
        provenance.edit_question(project, "churn", "Q-001", text="x")
    add(project, "Did churn rise?")
    with pytest.raises(provenance.StateError, match="data question"):
        provenance.edit_question(project, "churn", "Q-003", answerer="user")
    assert provenance.edit_question(project, "churn", "Q-003", text="Did churn rise in Q3?", answerer="data")
    assert provenance.edit_question(project, "churn", "Q-002", answerer="data")


def test_resume_and_list_show_finding_status(project, capsys):
    add(project, "Does churn differ by region?")
    add(project, "Which churn definition does finance use?", "stakeholder", kind="context")
    settings(project, {"r1": ["Q-001"]})
    produce(project, "r1")
    code, out, _ = cli(project, capsys, "list", "--all")
    assert code == 0 and out.splitlines() == [
        "Q-001 answered (provisional) [data, analytical, should; parent: root] Does churn differ by region? -> r1 (provisional)",
        "Q-002 open [stakeholder, context, should; parent: root] Which churn definition does finance use?"]
    view = provenance.state_view(project, "churn")
    assert view.endswith("==> open ledger questions <==\n"
                         "Q-002 open [stakeholder, context, should; parent: root] Which churn definition does finance use?\n"
                         "Q-001 answered (provisional) [data, analytical, should; parent: root] Does churn differ by region? "
                         "-> r1 (provisional)\n")
    provenance.update_findings(project, "churn", ["r1"], status="supported", reason="checked")
    assert "Q-001" not in provenance.state_view(project, "churn").split("==> open ledger questions <==")[1]
    provenance.flag_findings(project, "churn", [{"result": "r1", "reason": "region view corrected"}])
    assert "Q-001 answered (awaiting recheck)" in provenance.state_view(project, "churn")
    assert cli(project, capsys, "list", "--investigation", "absent")[0] == 2


def test_status_collector_reads_the_ledger(project):
    assert status.collect(project)["active"]["questions"] is None
    add(project, "Does churn differ by region?")
    add(project, "Which churn definition does finance use?", "stakeholder", kind="context", parent="Q-001",
        priority="must")
    add(project, "Is EMEA in scope?", "user", kind="decision", status="declined", reason="no", parent="Q-001")
    settings(project, {"r1": ["Q-001"]})
    produce(project, "r1")
    provenance.flag_findings(project, "churn", [{"result": "r1", "reason": "region view corrected"}])
    questions = status.collect(project)["active"]["questions"]
    # The user asked one question, the root; the stakeholder's definition and the decision serve it.
    assert questions == {"counts": {"answered (awaiting recheck)": 1, "open": 1, "declined": 1},
                         "roots": {"answered (awaiting recheck)": 1},
                         "must_subquestions": {"open": 1}, "open_by_answerer": {"stakeholder": 1},
                         "open": ["Q-002 [stakeholder, context] Which churn definition does finance use?"],
                         "awaiting_recheck": ["Q-001 answered (awaiting recheck) [data, analytical] Does churn differ by region? -> r1 (revalidation-needed (was provisional))"],
                         "provisional": []}
    (project / INV / "questions.json").write_text('{"schema": "awb-questions/1", "questions": [1]}')
    result = status.collect(project)
    assert result["active"]["questions"] is None
    assert any("question ledger" in item["reason"] for item in result["uncertainties"])
    (project / INV / "questions.json").unlink()
    result = status.collect(project)
    assert result["active"]["questions"] is None
    assert any("without questions.json" in item["reason"] for item in result["uncertainties"])


def test_cli_tree_priority_and_render(project, capsys):
    def question(text, *options):
        return cli(project, capsys, "add", text, "--kind", "analytical", "--answerer", "data",
                   "--origin", "scope", *options)

    assert question("Root should?")[0] == 0
    assert question("Root must?", "--priority", "must")[0] == 0
    assert question("Child could?", "--parent", "Q-002", "--priority", "could")[0] == 0
    assert question("Child must?", "--parent", "Q-002", "--priority", "must")[0] == 0
    assert question("Grandchild should?", "--parent", "Q-004")[0] == 0
    assert question("Other root should?")[0] == 0
    code, out, err = cli(project, capsys, "list", "--all")
    assert (code, err) == (0, "")
    assert out.splitlines() == [
        "Q-002 open [data, analytical, must; parent: root] Root must?",
        "  Q-004 open [data, analytical, must; parent: Q-002] Child must?",
        "    Q-005 open [data, analytical, should; parent: Q-004] Grandchild should?",
        "  Q-003 open [data, analytical, could; parent: Q-002] Child could?",
        "Q-001 open [data, analytical, should; parent: root] Root should?",
        "Q-006 open [data, analytical, should; parent: root] Other root should?",
    ]
    assert cli(project, capsys, "edit", "Q-003", "--parent", "Q-001", "--priority", "must")[0] == 0
    md = project / INV / "questions.md"
    rendered = md.read_text()
    assert "| Parent | Priority |" in rendered
    assert "| Q-003 | &nbsp;&nbsp;Child could? | analytical | data | | open | | Q-001 | must |" in rendered
    assert rendered.index("| Q-002 |") < rendered.index("| Q-004 |") < rendered.index("| Q-005 |") < rendered.index("| Q-001 |") < rendered.index("| Q-003 |") < rendered.index("| Q-006 |")
    md.write_text("hand edit\n")
    assert cli(project, capsys, "render")[0] == 0
    assert md.read_text() == rendered
    assert cli(project, capsys, "edit", "Q-003", "--parent", "")[0] == 0
    assert "Q-003 open [data, analytical, must; parent: root]" in cli(project, capsys, "list")[1]


@pytest.mark.parametrize("status", ["open", "parked", "declined", "answered", "superseded"])
def test_cli_audience_wording_in_every_status(project, capsys, status):
    assert cli(project, capsys, "add", "Which internal measure?", "--kind", "context", "--answerer", "user",
               "--origin", "scope", "--audience", " Which\n measure   matters? ")[0] == 0
    if status == "answered":
        assert cli(project, capsys, "answer", "Q-001", "--text", "Revenue", "--by", "user")[0] == 0
    elif status != "open":
        assert cli(project, capsys, "status", "Q-001", "--set", status, "--reason", "scope choice")[0] == 0
    assert ledger(project)["Q-001"]["audience"] == "Which measure matters?"
    assert "audience: Which measure matters?" in cli(project, capsys, "list", "--all")[1]
    assert "audience:" not in provenance.state_view(project, "churn")
    assert "| Audience |" in (project / INV / "questions.md").read_text()
    assert "| Which measure matters? |" in (project / INV / "questions.md").read_text()
    assert cli(project, capsys, "edit", "Q-001", "--audience", " What\tmatters\n most? ")[0] == 0
    assert ledger(project)["Q-001"]["audience"] == "What matters most?"
    assert "audience: What matters most?" in cli(project, capsys, "list", "--all")[1]
    assert "| What matters most? |" in (project / INV / "questions.md").read_text()
    rendered = (project / INV / "questions.md").read_bytes()
    assert cli(project, capsys, "render")[0] == 0
    assert (project / INV / "questions.md").read_bytes() == rendered
    assert cli(project, capsys, "edit", "Q-001", "--audience", "")[0] == 0
    entry = ledger(project)["Q-001"]
    assert entry["audience"] == "" and entry["text"] == "Which internal measure?" and entry["status"] == status
    assert "audience:" not in cli(project, capsys, "list", "--all")[1]


def test_cli_tree_sorts_ids_by_number_and_indents_under_listed_parents(project, capsys):
    def question(text, *options):
        return cli(project, capsys, "add", text, "--kind", "analytical", "--answerer", "data",
                   "--origin", "scope", *options)

    assert question("Parked root?", "--status", "parked", "--reason", "later")[0] == 0
    assert question("Open child?", "--parent", "Q-001")[0] == 0
    assert question("Open grandchild?", "--parent", "Q-002")[0] == 0
    # The default open-only list drops the parked root, so its child is not indented under nothing.
    assert cli(project, capsys, "list")[1].splitlines() == [
        "Q-002 open [data, analytical, should; parent: Q-001] Open child?",
        "  Q-003 open [data, analytical, should; parent: Q-002] Open grandchild?"]
    path = project / INV / "questions.json"
    content = json.loads(path.read_text())
    # Two roots of equal priority: Q-999 sorts before Q-1000 by number, not as text.
    content["questions"] = [dict(q, parent="") for q in content["questions"][:2]]
    content["questions"][0]["id"], content["questions"][1]["id"] = "Q-1000", "Q-999"
    path.write_text(json.dumps(content))
    assert cli(project, capsys, "render")[0] == 0
    assert [line.split()[0] for line in cli(project, capsys, "list", "--all")[1].splitlines()] == ["Q-999", "Q-1000"]


@pytest.mark.parametrize("action, options, message", [
    ("add", ["--parent", "Q-999"], "no question Q-999"),
    ("edit", ["--parent", "Q-999"], "no question Q-999"),
    ("edit", ["--parent", "Q-001"], "cycle"),
    ("edit", ["--parent", "Q-003"], "cycle"),
    ("add", ["--parent", "first"], "parent must be"),
    ("add", ["--parent", "Q-\u0660\u0660\u0661"], "parent must be"),
    ("edit", ["--parent", " Q-002 "], "parent must be"),
    ("add", ["--priority", "high"], "invalid choice"),
    ("edit", ["--priority", "MUST"], "invalid choice"),
])
def test_cli_refuses_invalid_tree_without_writes(project, capsys, action, options, message):
    for text, parent in (("Root?", ""), ("Child?", "Q-001"), ("Grandchild?", "Q-002")):
        assert cli(project, capsys, "add", text, "--kind", "analytical", "--answerer", "data",
                   "--origin", "scope", "--parent", parent)[0] == 0
    before = snapshot(project)
    args = ["Q-001"] if action == "edit" else ["Another?", "--kind", "context", "--answerer", "user", "--origin", "scope"]
    code, _, err = cli(project, capsys, action, *args, *options)
    assert code in (1, 2) and message in err
    assert snapshot(project) == before


@pytest.mark.parametrize("finding_status", ["flagged", "superseded"])
def test_cli_derives_awaiting_recheck_and_refreshes_render(project, capsys, finding_status):
    assert cli(project, capsys, "add", "Does churn differ?", "--kind", "analytical", "--answerer", "data",
               "--origin", "scope")[0] == 0
    settings(project, {"r1": ["Q-001"], "r2": ["Q-001"]})
    produce(project, "r1")
    produce(project, "r2")
    saved = (project / INV / "questions.json").read_bytes()
    if finding_status == "flagged":
        provenance.flag_findings(project, "churn", [{"result": "r1", "reason": "region view corrected"}])
    else:
        provenance.update_findings(project, "churn", ["r1"], status="superseded", reason="new scope")
    out = cli(project, capsys, "list", "--all")
    assert out[0] == 0 and "Q-001 answered (awaiting recheck)" in out[1]
    assert "| answered (awaiting recheck) |" in (project / INV / "questions.md").read_text()
    assert (project / INV / "questions.json").read_bytes() == saved
    assert cli(project, capsys, "render")[1] == "questions.md matches questions.json\n"
    # Finding changes keep the generated view current, so an ordinary ledger write is safe.
    assert cli(project, capsys, "add", "Another?", "--kind", "context", "--answerer", "user", "--origin", "scope")[0] == 0
    produce(project, "r1", table="n\n2\n")
    # The rerun leaves r1 provisional (flagged) or superseded, and r2 was never promoted.
    assert "Q-001 answered (" in cli(project, capsys, "list", "--all")[1]
    provenance.update_findings(project, "churn", ["r1"], status="supported", reason="rechecked")
    assert "Q-001 answered [" in cli(project, capsys, "list", "--all")[1]
    assert "awaiting recheck" not in (project / INV / "questions.md").read_text()
    assert "provisional)" not in (project / INV / "questions.md").read_text()


@pytest.mark.parametrize("unrecognized", ["flagged", "revalidation-needed (review pending)", "superseded (was supported)", "revalidation-needed (was unknown)"])
def test_cli_reports_unsupported_answering_finding_status(project, capsys, unrecognized):
    add(project, "Does churn differ?")
    settings(project, {"r1": ["Q-001"]})
    produce(project, "r1")
    path = project / INV / "findings.json"
    findings = json.loads(path.read_text())
    findings["findings"][0]["status"] = unrecognized
    path.write_text(json.dumps(findings))
    before = snapshot(project)
    code, _, err = cli(project, capsys, "list", "--all")
    assert code == 1 and "unrecognized finding status" in err
    assert snapshot(project) == before
