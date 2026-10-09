# Kept cases:
# test_installs_every_missing_helper_and_declares_packages: a bare workbench gets every src/ helper, src/awb.py included, and a requirements.txt; nothing else.
# test_present_helpers_are_classified_and_kept: current, earlier and customized copies are reported and left byte for byte.
# test_check_writes_nothing: --check reports missing helpers and the absent requirements file without writing.
# test_existing_dependency_files_are_only_reported: requirements.txt and pyproject.toml are read for missing entries, never edited.
# test_missing_packages_get_an_install_command: a package that fails to import is reported with a pip command for this interpreter.
# test_needed_packages_follow_helper_imports: stdlib and sibling helpers are excluded, distribution names mapped, pandas Parquet adds pyarrow.
# test_absent_mapped_asset_is_skipped: installer, awb-update plan, and record generator skip a recorded asset the skills directory lacks.
# test_refuses_non_workbench_and_old_python: neither case writes anything.

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
VERSIONS = json.loads((SKILLS / "awb-update/assets/shipped-versions.json").read_text())
HELPERS = {e["path"]: SKILLS / e["asset"] for e in VERSIONS["copied"]
           if e["path"].startswith("src/") and (SKILLS / e["asset"]).is_file()}


@pytest.fixture
def project(tmp_path):
    (tmp_path / "AGENTS.md").write_text("# Analytics workbench\n")
    return tmp_path


@pytest.fixture
def imports_ok(monkeypatch):
    monkeypatch.setattr(installer.importlib, "import_module", lambda name: None)


def snapshot(root):
    return {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}


def earlier_version(path):
    wanted = set(next(e for e in VERSIONS["copied"] if e["path"] == path)["previous"])
    log = subprocess.run(["git", "log", "HEAD", "--format=", "--raw", "--no-abbrev", "--", ".agents/skills"],
                         cwd=ROOT, check=True, capture_output=True, text=True).stdout
    for blob in {line.split()[3] for line in log.splitlines() if line.startswith(":")}:
        data = subprocess.run(["git", "cat-file", "blob", blob], cwd=ROOT, capture_output=True).stdout
        if hashlib.sha256(data).hexdigest() in wanted:
            return data
    raise AssertionError(f"no earlier version of {path} in history")


def test_installs_every_missing_helper_and_declares_packages(project):
    result = subprocess.run([sys.executable, str(SCRIPT), str(project)], capture_output=True, text=True, check=True)
    assert "\n" not in result.stdout.strip()
    report = json.loads(result.stdout)
    assert "src/awb.py" in HELPERS and report["helpers"] == {path: "installed" for path in HELPERS}
    for path, asset in HELPERS.items():
        assert (project / path).read_bytes() == asset.read_bytes()
    assert not (project / "package-format").exists() and not (project / "workbench-guides").exists()
    assert report["requirements"] == {"path": "requirements.txt", "status": "written",
                                      "packages": ["duckdb", "pandas"]}
    lines = (project / "requirements.txt").read_text().splitlines()
    assert lines[0].startswith("#") and lines[1:] == ["duckdb", "pandas"]
    assert set(report["packages"]) == {"duckdb", "pandas"} and report["python"]["ok"]


def test_present_helpers_are_classified_and_kept(project, imports_ok):
    files = {"src/awb.py": HELPERS["src/awb.py"].read_bytes(),
             "src/provenance.py": earlier_version("src/provenance.py"),
             "src/exploration/validate.py": b"# our own validation\n"}
    for path, data in files.items():
        (project / path).parent.mkdir(parents=True, exist_ok=True)
        (project / path).write_bytes(data)
    result = installer.install(project)
    assert {path: result["helpers"][path] for path in files} == {
        "src/awb.py": "present-current", "src/provenance.py": "present-earlier",
        "src/exploration/validate.py": "present-customized"}
    assert "awb-update" in result["helpers_note"]
    assert all((project / path).read_bytes() == data for path, data in files.items())
    assert result["helpers"]["src/preparation/landing.py"] == "installed"


def test_check_writes_nothing(project, imports_ok):
    before = snapshot(project)
    result = installer.install(project, check=True)
    assert snapshot(project) == before
    assert set(result["helpers"].values()) == {"missing"}
    assert result["requirements"]["status"] == "absent"


def test_existing_dependency_files_are_only_reported(project, imports_ok):
    (project / "requirements.txt").write_text("# pinned\nPandas>=2.0  # frames\n-r more.txt\n")
    before = snapshot(project)
    result = installer.install(project)
    assert (project / "requirements.txt").read_bytes() == before[project / "requirements.txt"]
    assert result["requirements"] == {"path": "requirements.txt", "status": "incomplete", "missing": ["duckdb"]}
    (project / "requirements.txt").unlink()
    (project / "pyproject.toml").write_text(
        '[project]\nname = "x"\ndependencies = ["pandas[parquet]>=2"]\n'
        '[project.optional-dependencies]\nsql = ["DuckDB==1.1"]\n')
    result = installer.install(project)
    assert result["requirements"] == {"path": "pyproject.toml", "status": "declared"}
    assert not (project / "requirements.txt").exists()


def test_missing_packages_get_an_install_command(project, monkeypatch):
    def import_module(name):
        if name == "duckdb":
            raise ImportError(name)
    monkeypatch.setattr(installer.importlib, "import_module", import_module)
    result = installer.install(project, check=True)
    assert result["packages"] == {"duckdb": "missing", "pandas": "ok"}
    assert result["install"] == f"{sys.executable} -m pip install duckdb"


def test_needed_packages_follow_helper_imports(tmp_path):
    helper = tmp_path / "awb_thing.py"
    helper.write_text("import json\nimport os.path\nfrom landing import session\nfrom . import x\n"
                      "import yaml\nfrom sklearn.linear_model import Ridge\nimport pandas as pd\n"
                      "def f():\n    import duckdb\n    return pd.read_parquet('a')\n")
    helpers = [("src/thing.py", helper, set()), ("src/preparation/landing.py", helper, set())]
    assert installer._needed(helpers) == {"duckdb": "duckdb", "pandas": "pandas", "pyarrow": "pyarrow",
                                          "sklearn": "scikit-learn", "yaml": "PyYAML"}


def test_absent_mapped_asset_is_skipped(project, tmp_path, monkeypatch, imports_ok):
    versions = tmp_path / "versions.json"
    versions.write_text(json.dumps({"copied": [
        {"path": "src/awb.py", "asset": "awb-init/assets/awb_cli.py", "previous": []},
        {"path": "src/packaging/later.py", "asset": "awb-package/assets/awb_not_shipped.py", "previous": []},
    ], "retired": []}))
    monkeypatch.setattr(installer, "VERSIONS", versions)
    assert installer.install(project)["helpers"] == {"src/awb.py": "installed"}

    plan = load("awb_update_plan", SKILLS / "awb-update/scripts/plan_update.py")
    monkeypatch.setattr(plan, "VERSIONS", versions)
    assert [row["path"] for row in plan.plan(project)["files"]] == ["src/awb.py"]

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
