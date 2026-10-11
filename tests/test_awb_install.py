# Kept cases:
# test_installs_every_missing_helper_and_guide: a bare workbench gets every src/ helper, src/awb.py included, both workbench guides, a requirements.txt and a receipt of what was installed; no package format.
# test_requirements_match_helper_imports: the static requirements list equals the third-party imports of the shipped helpers and the run.py template, fallbacks included.
# test_present_helpers_are_classified_and_kept: current, earlier and customized copies are reported and left byte for byte without --upgrade.
# test_receipt_decides_before_the_legacy_list: a file matching its receipt entry is earlier; a file whose entry differs is customized even when the frozen list knows it.
# test_package_formats_install_on_request: --package-formats installs missing formats into the receipt; without it present formats go unreported.
# test_check_writes_nothing: --check reports missing helpers and the absent requirements file without writing.
# test_existing_dependency_files_are_only_reported: requirements.txt and pyproject.toml are read for missing entries, never edited.
# test_missing_packages_get_an_install_command: a package that fails to import is reported with a pip command for this interpreter.
# test_absent_mapped_asset_is_skipped: the installer skips a copied asset the skills directory lacks.
# test_refuses_non_workbench_old_python_and_unreadable_receipt: none of these writes anything.
# test_upgrade_check_classifies_without_writing: current, earlier, customized copies and retired files, the merged packaging helpers included, are reported; nothing changes.
# test_upgrade_replaces_only_earlier_copies: --upgrade rewrites earlier helpers, package formats and guides, records them in the receipt, and leaves customized ones byte for byte.
# test_upgrade_replace_and_remove_retired: named customized copies are replaced; unmodified retired files are removed with their emptied directory and receipt entry; customized retired files stay.
# test_cli_arguments: --replace repeats one path per flag, needs --upgrade, and rejects an uncopied path with exit 2.

import ast
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
LEGACY = json.loads(installer.LEGACY.read_text())
ASSETS = {path: SKILLS / asset for path, asset in installer.COPIED.items() if (SKILLS / asset).is_file()}
INSTALLED = {path: asset for path, asset in ASSETS.items() if not path.startswith("package-format/")}
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


def sha(data):
    return hashlib.sha256(data).hexdigest()


def earlier_version(path):
    """A version shipped before receipts other than the current asset, recovered from Git by its frozen hash."""
    wanted = set(LEGACY[path]) - ({sha(ASSETS[path].read_bytes())} if path in ASSETS else set())
    log = subprocess.run(["git", "log", "HEAD", "--format=", "--raw", "--no-abbrev", "--", ".agents/skills"],
                         cwd=ROOT, check=True, capture_output=True, text=True).stdout
    for blob in {line.split()[3] for line in log.splitlines() if line.startswith(":")}:
        if set(blob) == {"0"}:
            continue
        data = subprocess.run(["git", "cat-file", "blob", blob], cwd=ROOT, capture_output=True).stdout
        if sha(data) in wanted:
            return data
    raise AssertionError(f"no earlier version of {path} in history")


def write(root, files):
    for path, data in files.items():
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_bytes(data)


def receipt(root):
    return json.loads((root / ".awb-receipt.json").read_text())


def test_installs_every_missing_helper_and_guide(project):
    result = subprocess.run([sys.executable, str(SCRIPT), str(project)], capture_output=True, text=True, check=True)
    assert "\n" not in result.stdout.strip()
    report = json.loads(result.stdout)
    assert "src/awb.py" in INSTALLED and "workbench-guides/analysis.md" in INSTALLED
    assert report["files"] == {path: "installed" for path in INSTALLED}
    for path, asset in INSTALLED.items():
        assert (project / path).read_bytes() == asset.read_bytes()
    assert receipt(project) == {path: sha(asset.read_bytes()) for path, asset in sorted(INSTALLED.items())}
    assert not (project / "package-format").exists()
    assert report["requirements"] == {"path": "requirements.txt", "status": "written", "packages": PACKAGES}
    lines = (project / "requirements.txt").read_text().splitlines()
    assert lines[0].startswith("#") and lines[1:] == PACKAGES
    expected = {"duckdb", "pandas"} | ({"tomli"} if sys.version_info < (3, 11) else set())
    assert set(report["packages"]) == expected and report["python"]["ok"]


def test_requirements_match_helper_imports():
    sources = [asset for path, asset in ASSETS.items() if path.endswith(".py")]
    sources.append(SKILLS / "awb-init/assets/workbench/investigation/run.py")
    project = {Path(path).stem for path in [*installer.COPIED, *installer.RETIRED]} | {"src"}
    imported = set()
    for source in sources:
        for node in ast.walk(ast.parse(source.read_text())):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and not node.level:
                names = [node.module]
            else:
                continue
            imported |= {name.split(".")[0] for name in names}
    assert {name for name in imported if name not in sys.stdlib_module_names and name not in project} == \
        set(installer.REQUIREMENTS)


def test_present_helpers_are_classified_and_kept(project, imports_ok):
    files = {"src/awb.py": ASSETS["src/awb.py"].read_bytes(),
             "src/provenance.py": earlier_version("src/provenance.py"),
             "src/exploration/validate.py": b"# our own validation\n",
             "workbench-guides/data.md": earlier_version("workbench-guides/data.md")}
    write(project, files)
    result = installer.install(project)
    assert {path: result["files"][path] for path in files} == {
        "src/awb.py": "current", "src/provenance.py": "earlier", "src/exploration/validate.py": "customized",
        "workbench-guides/data.md": "earlier"}
    assert result["customized"] == {"src/exploration/validate.py": str(ASSETS["src/exploration/validate.py"])}
    assert "--upgrade" in result["note"]
    assert all((project / path).read_bytes() == data for path, data in files.items())
    assert result["files"]["src/preparation/landing.py"] == "installed"
    assert set(receipt(project)) == set(INSTALLED) - set(files)


def test_receipt_decides_before_the_legacy_list(project, imports_ok):
    edited, legacy = b"# installed by a later skills version\n", earlier_version("src/provenance.py")
    write(project, {"src/preparation/landing.py": edited, "src/provenance.py": legacy,
                    ".awb-receipt.json": json.dumps({"src/preparation/landing.py": sha(edited),
                                                     "src/provenance.py": sha(b"another copy")}).encode()})
    result = installer.install(project, check=True, upgrade=True)
    assert result["files"]["src/preparation/landing.py"] == "earlier"
    assert result["files"]["src/provenance.py"] == "customized"


def test_package_formats_install_on_request(project, imports_ok):
    formats = {path for path in ASSETS if path.startswith("package-format/")}
    write(project, {"package-format/m365-assembly.md": earlier_version("package-format/m365-assembly.md")})
    assert not formats & set(installer.install(project)["files"])
    result = installer.install(project, package_formats=True)
    assert {path: result["files"][path] for path in formats} == {
        path: "earlier" if path == "package-format/m365-assembly.md" else "installed" for path in formats}
    assert {path: receipt(project)[path] for path in formats - {"package-format/m365-assembly.md"}} == {
        path: sha(ASSETS[path].read_bytes()) for path in formats - {"package-format/m365-assembly.md"}}
    assert "package-format/m365-assembly.md" not in receipt(project)


def test_check_writes_nothing(project, imports_ok):
    before = snapshot(project)
    result = installer.install(project, check=True, package_formats=True)
    assert snapshot(project) == before
    assert set(result["files"].values()) == {"missing"} and len(result["files"]) == len(ASSETS)
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


def test_absent_mapped_asset_is_skipped(project, monkeypatch, imports_ok):
    monkeypatch.setattr(installer, "COPIED", {"src/awb.py": "awb-init/assets/awb_cli.py",
                                              "src/packaging/later.py": "awb-package/assets/awb_not_shipped.py"})
    assert installer.install(project, upgrade=True)["files"] == {"src/awb.py": "installed"}


def test_refuses_non_workbench_old_python_and_unreadable_receipt(tmp_path, project, monkeypatch):
    assert installer.install(tmp_path / "missing") == {"project": str((tmp_path / "missing").resolve()),
                                                       "workbench": False}
    (project / ".awb-receipt.json").write_text("{")
    before = snapshot(project)
    result = installer.install(project, upgrade=True)
    assert "restore it from Git" in result["error"] and snapshot(project) == before
    monkeypatch.setattr(installer, "PYTHON", (99, 0))
    result = installer.install(project)
    assert not result["python"]["ok"] and "error" in result
    assert snapshot(project) == before


@pytest.fixture
def upgradable(project):
    write(project, {
        "package-format/findings-template.md": ASSETS["package-format/findings-template.md"].read_bytes(),
        "package-format/m365-assembly.md": earlier_version("package-format/m365-assembly.md"),
        "workbench-guides/analysis.md": earlier_version("workbench-guides/analysis.md"),
        "src/provenance.py": b"# our own provenance\n",
        "package-format/journal-template.md": earlier_version("package-format/journal-template.md"),
        "src/presentation/style.py": earlier_version("src/presentation/style.py"),
        "src/packaging/findings.py": earlier_version("src/packaging/findings.py"),
        "src/packaging/charts.py": b"# our own charts\n",
    })
    for path, asset in INSTALLED.items():
        if path not in {"src/provenance.py", "workbench-guides/analysis.md"}:
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
                                 "src/presentation/style.py": "unmodified",
                                 "src/packaging/findings.py": "unmodified",
                                 "src/packaging/charts.py": "customized"}
    assert "old_format_drafts" not in result


def test_upgrade_replaces_only_earlier_copies(upgradable, imports_ok):
    result = installer.install(upgradable, upgrade=True)
    assert result["files"]["package-format/m365-assembly.md"] == "replaced"
    assert result["files"]["workbench-guides/analysis.md"] == "replaced"
    assert (upgradable / "package-format/m365-assembly.md").read_bytes() == \
        ASSETS["package-format/m365-assembly.md"].read_bytes()
    assert receipt(upgradable) == {path: sha(ASSETS[path].read_bytes()) for path in
                                   ("package-format/m365-assembly.md", "workbench-guides/analysis.md")}
    assert (upgradable / "src/provenance.py").read_bytes() == b"# our own provenance\n"
    assert result["files"]["src/provenance.py"] == "customized"
    assert (upgradable / "src/presentation/style.py").exists()
    assert not (upgradable / "package-format/manifest-template.md").exists()


def test_upgrade_replace_and_remove_retired(upgradable, imports_ok):
    (upgradable / "package-format/executive-summary-template.md").write_text("ours\n")
    write(upgradable, {".awb-receipt.json": json.dumps(
        {"src/presentation/style.py": sha((upgradable / "src/presentation/style.py").read_bytes())}).encode()})
    result = installer.install(upgradable, upgrade=True, replace=["src/provenance.py"], remove_retired=True)
    assert result["files"]["src/provenance.py"] == "replaced" and "customized" not in result
    assert (upgradable / "src/provenance.py").read_bytes() == ASSETS["src/provenance.py"].read_bytes()
    assert result["retired"] == {"package-format/journal-template.md": "removed",
                                 "package-format/executive-summary-template.md": "customized",
                                 "src/presentation/style.py": "removed",
                                 "src/packaging/findings.py": "removed",
                                 "src/packaging/charts.py": "customized"}
    assert not (upgradable / "src/presentation").exists()
    assert not (upgradable / "package-format/journal-template.md").exists()
    assert (upgradable / "package-format/executive-summary-template.md").exists()
    assert (upgradable / "src/packaging/charts.py").exists()
    assert "src/presentation/style.py" not in receipt(upgradable)
    assert receipt(upgradable)["src/provenance.py"] == sha(ASSETS["src/provenance.py"].read_bytes())


def test_cli_arguments(upgradable):
    def run(*argv):
        return subprocess.run([sys.executable, str(SCRIPT), str(upgradable), *argv], capture_output=True, text=True)
    assert run("--replace", "src/provenance.py").returncode == 2
    assert run("--upgrade", "--replace", "README.md").returncode == 2
    result = run("--upgrade", "--check", "--replace", "src/provenance.py", "--replace",
                 "package-format/m365-assembly.md")
    assert result.returncode == 0
    assert json.loads(result.stdout)["files"]["src/provenance.py"] == "customized"
