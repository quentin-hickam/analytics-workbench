# Kept cases:
# test_shipped_versions_record_is_current: the committed record matches what the generator derives from history.
# test_plan_classifies_without_writing: current, earlier, customized and absent copies, retired files and old drafts are reported; nothing changes.
# test_apply_replaces_only_earlier_copies: --apply rewrites earlier copies and leaves customized ones byte for byte.
# test_replace_and_remove_retired: named customized copies are replaced; unmodified retired files are removed with their emptied directory; customized retired files stay.
# test_non_workbench_and_unknown_replace: a directory without workbench files reports workbench false; --replace of an uncopied path exits.

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents/skills"
SCRIPT = SKILLS / "awb-update/scripts/plan_update.py"
spec = importlib.util.spec_from_file_location("awb_update", SCRIPT)
update = importlib.util.module_from_spec(spec)
spec.loader.exec_module(update)
VERSIONS = json.loads((SKILLS / "awb-update/assets/shipped-versions.json").read_text())


def entry(path):
    return next(e for e in VERSIONS["copied"] + VERSIONS["retired"] if e["path"] == path)


def earlier_text(path):
    """An earlier shipped version, recovered from Git by its recorded hash."""
    wanted = set(entry(path).get("previous") or entry(path).get("shipped"))
    log = subprocess.run(["git", "log", "HEAD", "--format=", "--raw", "--no-abbrev", "--", ".agents/skills"],
                         cwd=ROOT, check=True, capture_output=True, text=True).stdout
    for line in log.splitlines():
        blob = line.split()[3] if line.startswith(":") else None
        if blob and set(blob) != {"0"}:
            data = subprocess.run(["git", "cat-file", "blob", blob], cwd=ROOT, capture_output=True).stdout
            if hashlib.sha256(data).hexdigest() in wanted:
                return data
    raise AssertionError(f"no earlier version of {path} in history")


@pytest.fixture
def project(tmp_path):
    (tmp_path / "AGENTS.md").write_text("# Analytics workbench\n")
    files = {
        "package-format/findings-template.md": (SKILLS / entry("package-format/findings-template.md")["asset"]).read_bytes(),
        "package-format/m365-assembly.md": earlier_text("package-format/m365-assembly.md"),
        "src/provenance.py": b"# our own provenance\n",
        "package-format/journal-template.md": earlier_text("package-format/journal-template.md"),
        "src/presentation/style.py": earlier_text("src/presentation/style.py"),
        "deliveries/churn/review/draft/findings.md": b"# Findings\n\n## Answer\n\nProse.\n",
        "deliveries/churn/review/draft/figures/late.png": b"",
    }
    for path, data in files.items():
        (tmp_path / path).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / path).write_bytes(data)
    return tmp_path


def snapshot(root):
    return {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}


def by_path(rows):
    return {row["path"]: row for row in rows}


def test_shipped_versions_record_is_current():
    result = subprocess.run([sys.executable, str(ROOT / "scripts/record-shipped-versions.py"), "--check"],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_plan_classifies_without_writing(project):
    before = snapshot(project)
    result = update.plan(project)
    assert snapshot(project) == before
    files = by_path(result["files"])
    assert files["package-format/findings-template.md"]["status"] == "current"
    assert files["package-format/m365-assembly.md"] == {
        "path": "package-format/m365-assembly.md", "status": "earlier", "action": "replace with --apply"}
    assert files["src/provenance.py"]["status"] == "customized" and files["src/provenance.py"]["action"] == "ask"
    assert files["src/packaging/charts.py"]["status"] == "absent"
    assert by_path(result["retired"]) == {
        "package-format/journal-template.md": {"path": "package-format/journal-template.md",
            "status": "unmodified", "action": "remove with --remove-retired"},
        "src/presentation/style.py": {"path": "src/presentation/style.py",
            "status": "unmodified", "action": "remove with --remove-retired"},
    }
    assert result["old_format_drafts"] == [{"path": "deliveries/churn/review/draft",
        "reasons": ["figures directory", "findings.md is not a slide outline"]}]


def test_apply_replaces_only_earlier_copies(project):
    customized = (project / "src/provenance.py").read_bytes()
    result = update.plan(project, apply=True)
    assert by_path(result["files"])["package-format/m365-assembly.md"]["action"] == "replaced"
    assert (project / "package-format/m365-assembly.md").read_bytes() == \
        (SKILLS / "awb-package/assets/package-format/m365-assembly.md").read_bytes()
    assert (project / "src/provenance.py").read_bytes() == customized


def test_replace_and_remove_retired(project):
    (project / "package-format/executive-summary-template.md").write_text("ours\n")
    result = update.plan(project, replace=["src/provenance.py"], remove_retired=True)
    assert by_path(result["files"])["src/provenance.py"]["action"] == "replaced"
    assert (project / "src/provenance.py").read_bytes() == (SKILLS / "awb-init/assets/awb_provenance.py").read_bytes()
    retired = by_path(result["retired"])
    assert retired["src/presentation/style.py"]["action"] == "removed"
    assert not (project / "src/presentation").exists()
    assert not (project / "package-format/journal-template.md").exists()
    assert retired["package-format/executive-summary-template.md"] == {
        "path": "package-format/executive-summary-template.md", "status": "customized", "action": "ask"}
    assert (project / "package-format/executive-summary-template.md").exists()


def test_non_workbench_and_unknown_replace(tmp_path, project):
    assert update.plan(tmp_path / "missing") == {"project": str((tmp_path / "missing").resolve()), "workbench": False}
    with pytest.raises(SystemExit):
        update.plan(project, replace=["README.md"])
