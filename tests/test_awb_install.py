# Kept cases:
# test_installs_every_missing_helper_and_declares_packages: a bare workbench gets every src/ helper, src/awb.py included, and a requirements.txt; nothing else.
# test_tomllib_fallback_is_a_conditional_requirement: tomli imported for tomllib in an except handler is declared for Python before 3.11; other fallbacks are not declared.
# test_present_helpers_are_classified_and_kept: current, earlier and customized copies are reported and left byte for byte without --upgrade.
# test_check_writes_nothing: --check reports missing helpers and the absent requirements file without writing.
# test_existing_dependency_files_are_only_reported: requirements.txt and pyproject.toml are read for missing entries, never edited.
# test_missing_packages_get_an_install_command: a package that fails to import is reported with a pip command for this interpreter.
# test_needed_packages_follow_helper_imports: stdlib, sibling helpers and src imports are excluded, distribution names mapped, pandas Parquet adds pyarrow.
# test_absent_mapped_asset_is_skipped: installer and record generator skip a recorded asset the skills directory lacks.
# test_refuses_non_workbench_and_old_python: neither case writes anything.
# test_shipped_versions_record_is_current: the committed record matches what the generator derives from history.
# test_upgrade_check_classifies_without_writing: current, earlier, customized copies, retired files and old drafts are reported; nothing changes.
# test_upgrade_replaces_only_earlier_copies: --upgrade rewrites earlier helpers, package formats and guides, and leaves customized ones byte for byte.
# test_upgrade_replace_and_remove_retired: named customized copies are replaced; unmodified retired files are removed with their emptied directory; customized retired files stay.
# test_cli_arguments: --replace repeats one path per flag, needs --upgrade, and rejects an uncopied path with exit 2.

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents/skills"
SCRIPT = SKILLS / "awb-init/scripts/install_helpers.py"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


installer = load("awb_install", SCRIPT)
VERSIONS = json.loads((SKILLS / "awb-init/assets/shipped-versions.json").read_text())
HELPERS = {e["path"]: SKILLS / e["asset"] for e in VERSIONS["copied"]
           if e["path"].startswith("src/") and (SKILLS / e["asset"]).is_file()}
PACKAGES = ["duckdb", "pandas", 'tomli; python_version < "3.11"']


@pytest.fixture
def project(tmp_path):
    (tmp_path / "AGENTS.md").write_text("# Analytics workbench\n")
    return tmp_path


@pytest.fixture
def imports_ok(monkeypatch):
    monkeypatch.setattr(installer.importlib, "import_module", lambda name: None)


def snapshot(root):
    return {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}


def entry(path):
    return next(e for e in VERSIONS["copied"] + VERSIONS["retired"] if e["path"] == path)


def earlier_version(path):
    """An earlier shipped version, recovered from Git by its recorded hash."""
    wanted = set(entry(path).get("previous") or entry(path).get("shipped"))
    log = subprocess.run(["git", "log", "HEAD", "--format=", "--raw", "--no-abbrev", "--", ".agents/skills"],
                         cwd=ROOT, check=True, capture_output=True, text=True).stdout
    for blob in {line.split()[3] for line in log.splitlines() if line.startswith(":")}:
        if set(blob) == {"0"}:
            continue
        data = subprocess.run(["git", "cat-file", "blob", blob], cwd=ROOT, capture_output=True).stdout
        if hashlib.sha256(data).hexdigest() in wanted:
            return data
    raise AssertionError(f"no earlier version of {path} in history")


def write(root, files):
    for path, data in files.items():
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_bytes(data)


def test_installs_every_missing_helper_and_declares_packages(project):
    result = subprocess.run([sys.executable, str(SCRIPT), str(project)], capture_output=True, text=True, check=True)
    assert "\n" not in result.stdout.strip()
    report = json.loads(result.stdout)
    assert "src/awb.py" in HELPERS and report["files"] == {path: "installed" for path in HELPERS}
    for path, asset in HELPERS.items():
        assert (project / path).read_bytes() == asset.read_bytes()
    assert not (project / "package-format").exists() and not (project / "workbench-guides").exists()
    assert report["requirements"] == {"path": "requirements.txt", "status": "written", "packages": PACKAGES}
    lines = (project / "requirements.txt").read_text().splitlines()
    assert lines[0].startswith("#") and lines[1:] == PACKAGES
    expected = {"duckdb", "pandas"} | ({"tomli"} if sys.version_info < (3, 11) else set())
    assert set(report["packages"]) == expected and report["python"]["ok"]


def test_present_helpers_are_classified_and_kept(project, imports_ok):
    files = {"src/awb.py": HELPERS["src/awb.py"].read_bytes(),
             "src/provenance.py": earlier_version("src/provenance.py"),
             "src/exploration/validate.py": b"# our own validation\n",
             "workbench-guides/data.md": earlier_version("workbench-guides/data.md")}
    write(project, files)
    result = installer.install(project)
    assert {path: result["files"][path] for path in files if path.startswith("src/")} == {
        "src/awb.py": "current", "src/provenance.py": "earlier", "src/exploration/validate.py": "customized"}
    assert "workbench-guides/data.md" not in result["files"]
    assert result["customized"] == {"src/exploration/validate.py": str(HELPERS["src/exploration/validate.py"])}
    assert "--upgrade" in result["note"]
    assert all((project / path).read_bytes() == data for path, data in files.items())
    assert result["files"]["src/preparation/landing.py"] == "installed"


def test_check_writes_nothing(project, imports_ok):
    before = snapshot(project)
    result = installer.install(project, check=True)
    assert snapshot(project) == before
    assert set(result["files"].values()) == {"missing"}
    assert result["requirements"]["status"] == "absent"


def test_existing_dependency_files_are_only_reported(project, imports_ok):
    (project / "requirements.txt").write_text("# pinned\nPandas>=2.0  # frames\ntomli>=2\n-r more.txt\n")
    before = snapshot(project)
    result = installer.install(project)
    assert (project / "requirements.txt").read_bytes() == before[project / "requirements.txt"]
    assert result["requirements"] == {"path": "requirements.txt", "status": "incomplete", "missing": ["duckdb"]}
    (project / "requirements.txt").unlink()
    (project / "pyproject.toml").write_text(
        '[project]\nname = "x"\ndependencies = ["pandas[parquet]>=2"]\n'
        '[project.optional-dependencies]\nsql = ["DuckDB==1.1"]\n')
    result = installer.install(project)
    assert result["requirements"] == {"path": "pyproject.toml", "status": "incomplete",
                                      "missing": ['tomli; python_version < "3.11"']}
    assert not (project / "requirements.txt").exists()


def test_missing_packages_get_an_install_command(project, monkeypatch):
    def import_module(name):
        if name == "duckdb":
            raise ImportError(name)
    monkeypatch.setattr(installer.importlib, "import_module", import_module)
    result = installer.install(project, check=True)
    assert result["packages"]["duckdb"] == "missing" and result["packages"]["pandas"] == "ok"
    assert result["install"] == f"{sys.executable} -m pip install duckdb"


def test_needed_packages_follow_helper_imports(tmp_path):
    helper = tmp_path / "awb_thing.py"
    helper.write_text("import json\nimport os.path\nfrom landing import session\nfrom . import x\n"
                      "from src.provenance import record_evidence\n"
                      "import yaml\nfrom sklearn.linear_model import Ridge\nimport pandas as pd\n"
                      "def f():\n    import duckdb\n    return pd.read_parquet('a')\n")
    sources = [("src/thing.py", helper), ("src/preparation/landing.py", helper)]
    assert installer._needed(sources) == {"duckdb": "duckdb", "pandas": "pandas", "pyarrow": "pyarrow",
                                          "sklearn": "scikit-learn", "yaml": "PyYAML"}


def test_tomllib_fallback_is_a_conditional_requirement(tmp_path):
    helper = tmp_path / "helper.py"
    helper.write_text("import duckdb\ntry:\n    import tomllib\nexcept ImportError:\n    import tomli as tomllib\n"
                      "try:\n    import ujson as json\nexcept ImportError:\n    import simplejson as json\n")
    assert installer._needed([("src/helper.py", helper)]) == {
        "duckdb": "duckdb", "tomli": 'tomli; python_version < "3.11"', "ujson": "ujson"}


def test_absent_mapped_asset_is_skipped(project, tmp_path, monkeypatch, imports_ok):
    versions = tmp_path / "versions.json"
    versions.write_text(json.dumps({"copied": [
        {"path": "src/awb.py", "asset": "awb-init/assets/awb_cli.py", "previous": []},
        {"path": "src/packaging/later.py", "asset": "awb-package/assets/awb_not_shipped.py", "previous": []},
    ], "retired": []}))
    monkeypatch.setattr(installer, "VERSIONS", versions)
    assert installer.install(project, upgrade=True)["files"] == {"src/awb.py": "installed"}

    record = load("awb_record", ROOT / "scripts/record-shipped-versions.py")
    monkeypatch.setattr(record, "COPIED", {"src/awb.py": "awb-init/assets/awb_cli.py",
                                           "src/packaging/later.py": "awb-package/assets/awb_not_shipped.py"})
    monkeypatch.setattr(record, "RETIRED", {})
    assert [entry["path"] for entry in record.build()["copied"]] == ["src/awb.py"]


def test_refuses_non_workbench_and_old_python(tmp_path, project, monkeypatch):
    assert installer.install(tmp_path / "missing") == {"project": str((tmp_path / "missing").resolve()),
                                                       "workbench": False}
    monkeypatch.setattr(installer, "PYTHON", (99, 0))
    before = snapshot(project)
    result = installer.install(project)
    assert not result["python"]["ok"] and "error" in result
    assert snapshot(project) == before


def test_shipped_versions_record_is_current():
    result = subprocess.run([sys.executable, str(ROOT / "scripts/record-shipped-versions.py"), "--check"],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


@pytest.fixture
def upgradable(project):
    write(project, {
        "package-format/findings-template.md": (SKILLS / entry("package-format/findings-template.md")["asset"]).read_bytes(),
        "package-format/m365-assembly.md": earlier_version("package-format/m365-assembly.md"),
        "workbench-guides/analysis.md": earlier_version("workbench-guides/analysis.md"),
        "src/provenance.py": b"# our own provenance\n",
        "package-format/journal-template.md": earlier_version("package-format/journal-template.md"),
        "src/presentation/style.py": earlier_version("src/presentation/style.py"),
        "deliveries/churn/review/draft/findings.md": b"# Findings\n\n## Answer\n\nProse.\n",
        "deliveries/churn/review/draft/figures/late.png": b"",
    })
    for path, asset in HELPERS.items():
        if path != "src/provenance.py":
            write(project, {path: asset.read_bytes()})
    (project / "requirements.txt").write_text("".join(f"{p}\n" for p in PACKAGES))
    return project


def test_upgrade_check_classifies_without_writing(upgradable, imports_ok):
    before = snapshot(upgradable)
    result = installer.install(upgradable, check=True, upgrade=True)
    assert snapshot(upgradable) == before
    files = result["files"]
    assert files["package-format/findings-template.md"] == "current"
    assert files["package-format/m365-assembly.md"] == "earlier"
    assert files["workbench-guides/analysis.md"] == "earlier"
    assert files["src/provenance.py"] == "customized"
    assert result["customized"] == {"src/provenance.py": str(SKILLS / "awb-init/assets/awb_provenance.py")}
    assert "package-format/manifest-template.md" not in files
    assert result["retired"] == {"package-format/journal-template.md": "unmodified",
                                 "src/presentation/style.py": "unmodified"}
    assert result["old_format_drafts"] == [{"path": "deliveries/churn/review/draft",
        "reasons": ["figures directory", "findings.md is not a slide outline"]}]


def test_upgrade_replaces_only_earlier_copies(upgradable, imports_ok):
    result = installer.install(upgradable, upgrade=True)
    assert result["files"]["package-format/m365-assembly.md"] == "replaced"
    assert result["files"]["workbench-guides/analysis.md"] == "replaced"
    assert (upgradable / "package-format/m365-assembly.md").read_bytes() == \
        (SKILLS / "awb-package/assets/package-format/m365-assembly.md").read_bytes()
    assert (upgradable / "src/provenance.py").read_bytes() == b"# our own provenance\n"
    assert result["files"]["src/provenance.py"] == "customized"
    assert (upgradable / "src/presentation/style.py").exists()
    assert not (upgradable / "package-format/manifest-template.md").exists()


def test_upgrade_replace_and_remove_retired(upgradable, imports_ok):
    (upgradable / "package-format/executive-summary-template.md").write_text("ours\n")
    result = installer.install(upgradable, upgrade=True, replace=["src/provenance.py"], remove_retired=True)
    assert result["files"]["src/provenance.py"] == "replaced" and "customized" not in result
    assert (upgradable / "src/provenance.py").read_bytes() == (SKILLS / "awb-init/assets/awb_provenance.py").read_bytes()
    assert result["retired"] == {"package-format/journal-template.md": "removed",
                                 "package-format/executive-summary-template.md": "customized",
                                 "src/presentation/style.py": "removed"}
    assert not (upgradable / "src/presentation").exists()
    assert not (upgradable / "package-format/journal-template.md").exists()
    assert (upgradable / "package-format/executive-summary-template.md").exists()


def test_cli_arguments(upgradable):
    def run(*argv):
        return subprocess.run([sys.executable, str(SCRIPT), str(upgradable), *argv], capture_output=True, text=True)
    assert run("--replace", "src/provenance.py").returncode == 2
    assert run("--upgrade", "--replace", "README.md").returncode == 2
    result = run("--upgrade", "--check", "--replace", "src/provenance.py", "--replace",
                 "package-format/m365-assembly.md")
    assert result.returncode == 0
    assert json.loads(result.stdout)["files"]["src/provenance.py"] == "customized"
