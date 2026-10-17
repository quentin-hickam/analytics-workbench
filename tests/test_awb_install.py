# Kept cases:
# test_installs_every_missing_helper_and_guide: a bare workbench gets every src/ helper, src/awb.py included, both workbench guides, the references README, a requirements.txt and a receipt of what was installed; no package format.
# test_fresh_workbench_gets_the_references_folder_and_guide_text: a fresh install creates foundation/references/ with its README, whose link resolves to the data guide that says what the folder keeps.
# test_repair_adds_the_references_folder: --upgrade on a workbench that lacks foundation/references/ installs its README into the receipt and leaves existing records alone.
# test_requirements_match_helper_imports: the static requirements list equals the third-party imports of the shipped helpers and the run.py template, fallbacks included.
# test_present_helpers_are_classified_and_kept: current, earlier and customized copies are reported and left byte for byte without --upgrade.
# test_receipt_alone_decides_earlier: a file matching its receipt entry is earlier; a file whose entry differs, or without an entry such as one installed before receipts, is customized.
# test_converted_line_endings_keep_the_status: a shipped or earlier copy checked out with CRLF line endings is still current or earlier, not customized.
# test_package_formats_install_on_request: --package-formats installs missing formats into the receipt; without it present formats go unreported.
# test_every_package_format_ships: every file under awb-package's package-format assets, the methodology note template included, is a copied package format at the same path.
# test_check_writes_nothing: --check reports missing helpers and the absent requirements file without writing.
# test_existing_dependency_files_are_only_reported: requirements.txt and pyproject.toml are read for missing entries, never edited; a wheel URL declares its package, not its scheme; a UTF-16 file and its quoted -r include are read, and a wheel path with extras declares its package; lines and includes the reader cannot read are listed as unread beside the status.
# test_unreadable_requirements_are_unchecked: a requirements.txt that exists but cannot be read is unchecked, not incomplete with every package missing.
# test_unchecked_requirements_keep_unread: when pyproject.toml cannot be parsed, for want of tomllib or as malformed TOML, the unchecked status still lists the requirements.txt lines the reader could not read.
# test_missing_packages_get_an_install_command: a package that fails to import is reported with a pip command for this interpreter.
# test_pyvenv_cfg_records_uv_accepted_and_refused_forms: a pyvenv.cfg records uv only on a `uv = <version>` line, key matched in any case; other keys, comments, and an empty value do not.
# test_uv_environment_without_pip_gets_a_uv_hint: an interpreter without pip whose pyvenv.cfg records uv, or with uv on PATH, gets `uv pip install --python <interpreter>` as its hint and requirements header; with pip, or with neither, the pip hint and header are unchanged.
# test_readme_gains_the_project_interpreter_line: the installer writes `Project interpreter: <path>` over `not yet recorded`, reports it current on a rerun, and inserts a missing line after Commits, else Active investigation, else at the end, keeping a CRLF README's line endings; --check reports it missing and writes nothing.
# test_project_interpreter_inside_the_project_is_recorded_relative: a virtual environment's interpreter inside the project is recorded by its project-relative path and reported in_project.
# test_recorded_interpreter_is_kept_or_replaced: a README naming another existing interpreter, or repeating the line, refuses with exit 1 and writes nothing, with or without --check; a recorded interpreter that no longer exists is replaced and named under was; a link to this interpreter outside any virtual environment is this interpreter.
# test_project_venv_is_kept_while_readme_records_none: a project with its own .venv or venv interpreter, run under another while README records none, refuses with exit 1 and writes nothing, with or without --check; README naming this interpreter lets it run.
# test_hardlinked_interpreter_in_another_prefix_is_refused: outside a virtual environment, a hard link to this interpreter's binary in another directory is another interpreter: README naming it refuses, and so does a project .venv that is such a link while README records none; nothing is written.
# test_awb_python_naming_this_interpreter_leaves_the_readme_line: with AWB_PYTHON naming this interpreter, by path or by name on PATH, the line is reported overridden and neither refused nor written, over another recorded interpreter or a project venv; AWB_PYTHON naming another interpreter changes nothing.
# test_absent_mapped_asset_is_skipped: the installer skips a copied asset the skills directory lacks; without the provenance asset an existing requirements.txt is reported unchecked, not a crash.
# test_refuses_non_workbench_old_python_and_unreadable_receipt: none of these writes anything.
# test_refuses_readme_only_directory: README.md is not a marker; reports missing markers and initialization guidance with exit 1, without writing.
# test_upgrade_check_classifies_without_writing: current, earlier, customized copies and retired files, the merged packaging helpers included, are reported; nothing changes.
# test_upgrade_replaces_only_earlier_copies: --upgrade rewrites earlier helpers, package formats and guides, records them in the receipt, and leaves customized ones byte for byte.
# test_upgrade_replace_and_remove_retired: named customized copies are replaced; unmodified retired files are removed with their emptied directory and receipt entry; customized retired files stay.
# test_cli_arguments: --replace repeats one path per flag, needs --upgrade, and rejects an uncopied path with exit 2.
# test_print_json_server_entry_without_writing: copilot and claude print the same JSON stdio entry with their own destination (COPILOT_HOME moves only copilot's, CLAUDE_CONFIG_DIR only claude's); both option spellings print without writing.
# test_print_server_entry_interpreter_warnings: old Python, down to one without shlex.join, or a virtual environment warns only on stderr before the registration lines, with unchanged host entry and no writes; a stable Python 3.10+ emits no warning.
# test_print_codex_server_entry_with_quoted_unicode_paths: native TOML with absolute paths and safe quoting; default/overridden destination, without writing.
# test_print_host_registration_command: each host's own registration command prints on stderr, POSIX-quoted with absolute interpreter and server paths that hold spaces, quotes and Unicode, before the fallback merge line, which for claude says to close Claude Code first; the entry still prints on stdout; nothing is written or run.
# test_server_entry_refusals_write_nothing: exact host choices and print-only mode refuse unknown/missing values, unknown/abbreviated options, and install arguments with exit 2 and no stdout or writes.
# test_awb_init_installs_agents_mapping_and_resolving_guides: adapting the root template then running the installer preserves one MCP/CLI rule and both resolving guide links.
# test_instruction_and_reviewer_tools_exist_in_server_tools_list: the single rule names every server tool, valid script command enums, run.py, and the same project advice; reviewer tools remain read-only.
# test_every_shipped_skill_script_has_an_instruction_route: all shipped skill script commands, including the shared installer, have a route in the rule.
# test_contract_scanners: inline code and Python target scanners accept their documented grammar and refuse other forms.

import ast
import hashlib
import importlib.util
import json
import os
import re
import shlex
import shutil
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
    """Content standing in for a version an earlier install shipped; earlier() records it in the receipt."""
    return f"# {path} as an earlier skills version shipped it\n".encode()


def write(root, files):
    for path, data in files.items():
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_bytes(data)


def earlier(root, files):
    """Write earlier shipped copies and their receipt entries, as the install that wrote them would have."""
    write(root, files)
    entries = json.loads((root / ".awb-receipt.json").read_text()) if (root / ".awb-receipt.json").exists() else {}
    entries.update({path: sha(data) for path, data in files.items()})
    (root / ".awb-receipt.json").write_text(json.dumps(entries))


def receipt(root):
    return json.loads((root / ".awb-receipt.json").read_text())


def test_installs_every_missing_helper_and_guide(project):
    result = subprocess.run([sys.executable, str(SCRIPT), str(project)], capture_output=True, text=True, check=True)
    assert "\n" not in result.stdout.strip()
    report = json.loads(result.stdout)
    assert {"src/awb.py", "workbench-guides/analysis.md", "foundation/references/README.md"} <= set(INSTALLED)
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


def test_fresh_workbench_gets_the_references_folder_and_guide_text(project, imports_ok):
    result = installer.install(project)
    assert result["files"]["foundation/references/README.md"] == "installed"
    readme = (project / "foundation/references/README.md").read_text()
    link = re.search(r"\[data guide\]\(([^)]+)\)", readme)[1]
    guide = (project / "foundation/references" / link).resolve()
    assert guide == (project / "workbench-guides/data.md").resolve() and guide.is_file()
    text = guide.read_text()
    assert "foundation/references/<source-id>/" in text and "SHA-256" in text
    assert "references/<source-id>/" in (SKILLS / "awb-init/assets/workbench/foundation/sources.md").read_text()


def test_repair_adds_the_references_folder(project, imports_ok):
    shipped = {path: asset.read_bytes() for path, asset in INSTALLED.items() if path != "foundation/references/README.md"}
    earlier(project, shipped)
    write(project, {"foundation/sources.md": b"# Source register\n"})
    before = snapshot(project)
    result = installer.install(project, upgrade=True)
    assert result["files"]["foundation/references/README.md"] == "installed"
    assert {path for path, status in result["files"].items() if status != "current"} == {"foundation/references/README.md"}
    assert (project / "foundation/references/README.md").read_bytes() == INSTALLED["foundation/references/README.md"].read_bytes()
    assert receipt(project)["foundation/references/README.md"] == sha(INSTALLED["foundation/references/README.md"].read_bytes())
    assert all(path.read_bytes() == data for path, data in before.items() if path.name != ".awb-receipt.json")


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
    shipped = {"src/provenance.py": earlier_version("src/provenance.py"),
               "workbench-guides/data.md": earlier_version("workbench-guides/data.md")}
    files = {"src/awb.py": ASSETS["src/awb.py"].read_bytes(),
             "src/exploration/validate.py": b"# our own validation\n", **shipped}
    earlier(project, shipped)
    write(project, files)
    result = installer.install(project)
    assert {path: result["files"][path] for path in files} == {
        "src/awb.py": "current", "src/provenance.py": "earlier", "src/exploration/validate.py": "customized",
        "workbench-guides/data.md": "earlier"}
    assert result["customized"] == {"src/exploration/validate.py": str(ASSETS["src/exploration/validate.py"])}
    assert "--upgrade" in result["note"]
    assert all((project / path).read_bytes() == data for path, data in files.items())
    assert result["files"]["src/preparation/landing.py"] == "installed"
    assert set(receipt(project)) == set(INSTALLED) - {"src/awb.py", "src/exploration/validate.py"}


def test_receipt_alone_decides_earlier(project, imports_ok):
    edited, other = b"# installed by a later skills version\n", earlier_version("src/provenance.py")
    write(project, {"src/preparation/landing.py": edited, "src/provenance.py": other,
                    "workbench-guides/data.md": earlier_version("workbench-guides/data.md"),
                    ".awb-receipt.json": json.dumps({"src/preparation/landing.py": sha(edited),
                                                     "src/provenance.py": sha(b"another copy")}).encode()})
    result = installer.install(project, check=True, upgrade=True)
    assert result["files"]["src/preparation/landing.py"] == "earlier"
    assert result["files"]["src/provenance.py"] == "customized"
    assert result["files"]["workbench-guides/data.md"] == "customized"  # installed before receipts


def test_converted_line_endings_keep_the_status(project, imports_ok):
    shipped = earlier_version("src/provenance.py")
    earlier(project, {"src/provenance.py": shipped})
    write(project, {"src/provenance.py": shipped.replace(b"\n", b"\r\n"),
                    "src/awb.py": ASSETS["src/awb.py"].read_bytes().replace(b"\n", b"\r\n")})
    result = installer.install(project, check=True, upgrade=True)
    assert result["files"]["src/provenance.py"] == "earlier" and result["files"]["src/awb.py"] == "current"


def test_package_formats_install_on_request(project, imports_ok):
    formats = {path for path in ASSETS if path.startswith("package-format/")}
    earlier(project, {"package-format/deck-rules.md": earlier_version("package-format/deck-rules.md")})
    assert not formats & set(installer.install(project)["files"])
    result = installer.install(project, package_formats=True)
    assert {path: result["files"][path] for path in formats} == {
        path: "earlier" if path == "package-format/deck-rules.md" else "installed" for path in formats}
    assert {path: receipt(project)[path] for path in formats - {"package-format/deck-rules.md"}} == {
        path: sha(ASSETS[path].read_bytes()) for path in formats - {"package-format/deck-rules.md"}}
    assert receipt(project)["package-format/deck-rules.md"] == sha(earlier_version("package-format/deck-rules.md"))


def test_every_package_format_ships():
    # Each template awb-package writes a draft from, the methodology note's included, installs with --package-formats.
    shipped = SKILLS / "awb-package/assets/package-format"
    assets = {"package-format/" + path.relative_to(shipped).as_posix() for path in shipped.rglob("*") if path.is_file()}
    assert "package-format/methodology-note-template.md" in assets
    assert assets == {path for path in installer.COPIED if path.startswith("package-format/")}
    assert all(installer.COPIED[path] == "awb-package/assets/" + path for path in assets)


def test_check_writes_nothing(project, imports_ok):
    before = snapshot(project)
    result = installer.install(project, check=True, package_formats=True)
    assert snapshot(project) == before
    assert set(result["files"].values()) == {"missing"} and len(result["files"]) == len(ASSETS)
    assert result["requirements"]["status"] == "absent"


def test_existing_dependency_files_are_only_reported(project, imports_ok):
    (project / "requirements.txt").write_text("# pinned\nPandas>=2.0  # frames\ntomli>=2\n-r more.txt\n"
                                              "https://example.invalid/duckdb-1.0-py3-none-any.whl\n")
    before = snapshot(project)
    result = installer.install(project)
    assert (project / "requirements.txt").read_bytes() == before[project / "requirements.txt"]
    assert result["requirements"] == {"path": "requirements.txt", "status": "declared",
                                      "unread": ["requirements.txt:4: -r more.txt (No such file or directory)"]}
    (project / "requirements.txt").write_bytes("Pandas>=2.0\n-r \"deps/more reqs.txt\"\n".encode("utf-16"))
    (project / "deps").mkdir()
    (project / "deps/more reqs.txt").write_text("tomli>=2\n./wheels/duckdb-1.0-py3-none-any.whl[all]\n")
    assert installer.install(project)["requirements"] == {"path": "requirements.txt", "status": "declared"}
    shutil.rmtree(project / "deps")
    (project / "requirements.txt").write_text("Pandas>=2.0\ntomli>=2\n-e .\n-r deps/gone.txt\n")
    result = installer.install(project)
    assert result["requirements"] == {
        "path": "requirements.txt", "status": "incomplete", "missing": ["duckdb"],
        "unread": ["requirements.txt:3: -e .", "requirements.txt:4: -r deps/gone.txt (No such file or directory)"]}
    (project / "requirements.txt").unlink()
    (project / "pyproject.toml").write_text(
        '[project]\nname = "x"\ndependencies = ["pandas[parquet]>=2"]\n'
        '[project.optional-dependencies]\nsql = ["DuckDB==1.1"]\n')
    result = installer.install(project)
    assert result["requirements"] == {"path": "pyproject.toml", "status": "incomplete",
                                      "missing": ['tomli; python_version < "3.11"']}
    assert not (project / "requirements.txt").exists()


@pytest.mark.skipif(sys.platform == "win32" or getattr(os, "geteuid", lambda: 1)() == 0,
                    reason="file modes do not stop this user reading")
def test_unreadable_requirements_are_unchecked(project, imports_ok):
    (project / "requirements.txt").write_text('duckdb\npandas\ntomli; python_version < "3.11"\n')
    (project / "requirements.txt").chmod(0)
    try:
        result = installer.install(project, check=True)
    finally:
        (project / "requirements.txt").chmod(0o644)
    assert result["requirements"] == {"path": "requirements.txt", "status": "unchecked", "packages": PACKAGES}


def test_unchecked_requirements_keep_unread(project, imports_ok, monkeypatch):
    (project / "requirements.txt").write_text("duckdb\n-e .\n-r missing.txt\n")
    (project / "pyproject.toml").write_text('[project]\nname = "x"\ndependencies = ["pandas"]\n')
    expected = {"path": "requirements.txt, pyproject.toml", "status": "unchecked", "packages": PACKAGES,
                "unread": ["requirements.txt:2: -e .", "requirements.txt:3: -r missing.txt (No such file or directory)"]}
    with monkeypatch.context() as patch:
        patch.setitem(sys.modules, "tomllib", None)  # As on Python 3.10.
        assert installer.install(project, check=True)["requirements"] == expected
    (project / "pyproject.toml").write_text("[project\n")
    assert installer.install(project, check=True)["requirements"] == expected


def test_missing_packages_get_an_install_command(project, monkeypatch):
    def import_module(name):
        if name == "duckdb":
            raise ImportError(name)
    monkeypatch.setattr(installer.importlib, "import_module", import_module)
    result = installer.install(project, check=True)
    assert result["packages"]["duckdb"] == "missing" and result["packages"]["pandas"] == "ok"
    assert result["install"] == f"{sys.executable} -m pip install duckdb"


def no_duckdb(name):
    if name == "duckdb":
        raise ImportError(name)


def executable(path, text="#!/bin/sh\n"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    path.chmod(0o755)
    return path


@pytest.mark.parametrize("text, expected", [
    ("home = /usr/bin\nuv = 0.5.1\nversion_info = 3.12.3\n", True),
    ("uv=0.4.18", True),
    ("  UV = 0.4.18  \n", True),
    ("home = /usr/bin\ninclude-system-site-packages = false\n", False),
    ("uv =\n", False),
    ("uvx = 1\n", False),
    ("# uv = 0.5.1\n", False),
    ("uv\n", False),
    ("home = /opt/uv/python\n", False),
    ("command = uv venv\n", False),
])
def test_pyvenv_cfg_records_uv_accepted_and_refused_forms(text, expected):
    assert installer._made_by_uv(text) is expected


def test_uv_environment_without_pip_gets_a_uv_hint(project, tmp_path, monkeypatch):
    monkeypatch.setattr(installer.importlib, "import_module", no_duckdb)
    monkeypatch.setattr(installer, "_has_pip", lambda: False)
    monkeypatch.setenv("PATH", str(tmp_path / "empty-bin"))
    venv = tmp_path / "uv-venv"
    venv.mkdir()
    (venv / "pyvenv.cfg").write_text("home = /usr/bin\nimplementation = CPython\nuv = 0.5.1\n")
    python = str(venv / "bin/python")
    assert installer._pip_install(python, str(venv)) == f"uv pip install --python {python}"
    # Without pip and with no uv record or uv on PATH, the hint is the pip one, unchanged.
    (venv / "pyvenv.cfg").write_text("home = /usr/bin\n")
    assert installer._pip_install(python, str(venv)) == f"{python} -m pip install"
    assert installer.install(project)["install"] == f"{sys.executable} -m pip install duckdb"
    assert "install with python3 -m pip install -r requirements.txt" in (project / "requirements.txt").read_text()
    # uv on PATH serves an interpreter without pip, and the requirements header names the same command.
    executable(tmp_path / "empty-bin/uv")
    (project / "requirements.txt").unlink()
    result = installer.install(project)
    assert result["install"] == f"uv pip install --python {sys.executable} duckdb"
    header = (project / "requirements.txt").read_text().splitlines()[0]
    assert header.endswith(f"install with uv pip install --python {os.path.abspath(sys.executable)} -r requirements.txt")
    # An interpreter with pip keeps the pip hint even where uv is on PATH.
    monkeypatch.setattr(installer, "_has_pip", lambda: True)
    assert installer.install(project, check=True)["install"] == f"{sys.executable} -m pip install duckdb"


def template_readme(root, text=None):
    path = root / "README.md"
    path.write_text((SKILLS / "awb-init/assets/workbench/README.md").read_text() if text is None else text)
    return path


def interpreter_lines(root):
    return [line for line in (root / "README.md").read_text().splitlines() if line.startswith("Project interpreter:")]


def test_readme_gains_the_project_interpreter_line(project, imports_ok):
    running = os.path.abspath(sys.executable)
    template_readme(project)
    assert interpreter_lines(project) == ["Project interpreter: not yet recorded"]
    before = snapshot(project)
    result = installer.install(project, check=True)
    assert result["interpreter"] == {"line": f"Project interpreter: {running}", "in_project": False, "status": "missing"}
    assert snapshot(project) == before
    result = installer.install(project)
    assert result["interpreter"] == {"line": f"Project interpreter: {running}", "in_project": False, "status": "written"}
    assert interpreter_lines(project) == [f"Project interpreter: {running}"]
    assert installer.install(project)["interpreter"]["status"] == "current"
    # A README without the line gains it directly after the Commits line, else after Active investigation.
    for text, after in (("# P\n\nActive investigation: none\n\nCommits: on request\n\nMore.\n", "Commits: on request"),
                        ("# P\n\nActive investigation: none\n\nMore.\n", "Active investigation: none"),
                        ("# P\n", "# P")):
        template_readme(project, text)
        assert installer.install(project)["interpreter"]["status"] == "written"
        lines = (project / "README.md").read_text().splitlines()
        at = lines.index(after)
        assert lines[at + 1:at + 3] == ["", f"Project interpreter: {running}"]
        assert interpreter_lines(project) == [f"Project interpreter: {running}"]
    # A CRLF README keeps its line endings.
    (project / "README.md").write_bytes(b"# P\r\n\r\nCommits: on request\r\n")
    installer.install(project)
    assert (project / "README.md").read_bytes() == \
        f"# P\r\n\r\nCommits: on request\r\n\r\nProject interpreter: {running}\r\n".encode()


def test_project_interpreter_inside_the_project_is_recorded_relative(project, imports_ok, monkeypatch):
    template_readme(project)
    venv_python = executable(project / ".venv/bin/python")
    monkeypatch.setattr(sys, "executable", str(venv_python))
    result = installer.install(project)
    assert result["interpreter"] == {"line": "Project interpreter: .venv/bin/python", "in_project": True,
                                     "status": "written"}
    assert interpreter_lines(project) == ["Project interpreter: .venv/bin/python"]


def test_recorded_interpreter_is_kept_or_replaced(project, tmp_path, imports_ok):
    running = os.path.abspath(sys.executable)
    other = executable(tmp_path / "other/bin/python")
    readme = template_readme(project, f"# P\n\nCommits: on request\n\nProject interpreter: `{other}`\n")
    before = snapshot(project)
    for check in (False, True):
        result = installer.install(project, check=check)
        assert "Project interpreter" in result["error"] and str(other) in result["error"]
        assert snapshot(project) == before
    completed = subprocess.run([sys.executable, str(SCRIPT), str(project)], capture_output=True, text=True)
    assert completed.returncode == 1 and "error" in json.loads(completed.stdout) and snapshot(project) == before
    # A repeated line is refused the same way.
    readme.write_text(f"Project interpreter: {running}\nProject interpreter: {running}\n")
    assert "repeats" in installer.install(project)["error"]
    # A recorded interpreter that no longer exists is replaced, and the result names it.
    readme.write_text("# P\n\nProject interpreter: .venv/bin/python\n")
    result = installer.install(project)
    assert result["interpreter"] == {"line": f"Project interpreter: {running}", "in_project": False,
                                     "status": "replaced", "was": ".venv/bin/python"}
    assert interpreter_lines(project) == [f"Project interpreter: {running}"]
    # Another name for this interpreter's binary, outside any virtual environment, is this interpreter.
    if os.name != "nt" and sys.prefix == sys.base_prefix:
        alias = tmp_path / "alias/bin/python"
        alias.parent.mkdir(parents=True)
        os.symlink(sys.executable, alias)
        readme.write_text(f"# P\n\nProject interpreter: {alias}\n")
        assert installer.install(project)["interpreter"]["status"] == "current"


@pytest.mark.parametrize("folder", [".venv", "venv"])
def test_project_venv_is_kept_while_readme_records_none(project, imports_ok, folder):
    running = os.path.abspath(sys.executable)
    template_readme(project)
    executable(project / folder / "bin/python")
    before = snapshot(project)
    for check in (False, True):
        result = installer.install(project, check=check)
        assert result["error"] == (f"the project has its own interpreter, {folder}/bin/python, and README records "
                                   "none; rerun with it, or name the interpreter to use on README's Project "
                                   "interpreter line")
        assert snapshot(project) == before
    completed = subprocess.run([sys.executable, str(SCRIPT), str(project)], capture_output=True, text=True,
                               env={k: v for k, v in os.environ.items() if k != "AWB_PYTHON"})
    assert completed.returncode == 1 and "error" in json.loads(completed.stdout) and snapshot(project) == before
    # Naming this interpreter on the line is the choice to use it over the project's own.
    template_readme(project, f"# P\n\nProject interpreter: {running}\n")
    assert installer.install(project)["interpreter"]["status"] == "current"


@pytest.mark.skipif(os.name == "nt", reason="POSIX file modes")
def test_hardlinked_interpreter_in_another_prefix_is_refused(project, tmp_path, imports_ok, monkeypatch):
    # This interpreter runs from one prefix; a package manager linked the same binary into another.
    base = executable(tmp_path / "base/bin/python3")
    monkeypatch.setattr(sys, "executable", str(base))
    monkeypatch.setattr(sys, "prefix", str(tmp_path / "base"))
    monkeypatch.setattr(sys, "base_prefix", str(tmp_path / "base"))
    monkeypatch.delenv("AWB_PYTHON", raising=False)
    env = tmp_path / "env/bin/python3"
    env.parent.mkdir(parents=True)
    os.link(base, env)
    template_readme(project, f"# P\n\nProject interpreter: {env}\n")
    before = snapshot(project)
    result = installer.install(project)
    assert "rerun with it" in result["error"] and str(env) in result["error"] and snapshot(project) == before
    # The project's own environment linked the same way is kept while README records none.
    template_readme(project)
    (project / ".venv/bin").mkdir(parents=True)
    os.link(base, project / ".venv/bin/python")
    before = snapshot(project)
    result = installer.install(project)
    assert "the project has its own interpreter, .venv/bin/python" in result["error"] and snapshot(project) == before


def test_awb_python_naming_this_interpreter_leaves_the_readme_line(project, tmp_path, imports_ok, monkeypatch):
    running = os.path.abspath(sys.executable)
    other = executable(tmp_path / "other/bin/python")
    readme = template_readme(project, f"# P\n\nProject interpreter: {other}\n")
    overridden = {"line": f"Project interpreter: {running}", "in_project": False, "status": "overridden"}
    for configured, path in ((sys.executable, None), (os.path.basename(sys.executable), os.path.dirname(sys.executable))):
        monkeypatch.setenv("AWB_PYTHON", configured)
        if path:
            monkeypatch.setenv("PATH", path)
        for check in (False, True):
            result = installer.install(project, check=check)
            assert "error" not in result and result["interpreter"] == overridden
            assert interpreter_lines(project) == [f"Project interpreter: {other}"]
    completed = subprocess.run([sys.executable, str(SCRIPT), str(project)], capture_output=True, text=True,
                               env={**os.environ, "AWB_PYTHON": sys.executable})
    assert completed.returncode == 0 and json.loads(completed.stdout)["interpreter"]["status"] == "overridden"
    # A project venv is passed over the same way, and README keeps its line.
    template_readme(project)
    executable(project / ".venv/bin/python")
    assert installer.install(project)["interpreter"] == overridden
    assert interpreter_lines(project) == ["Project interpreter: not yet recorded"]
    # AWB_PYTHON naming another interpreter changes nothing: README's still refuses this one.
    monkeypatch.setenv("AWB_PYTHON", str(other))
    readme.write_text(f"# P\n\nProject interpreter: {other}\n")
    assert "rerun with it" in installer.install(project)["error"]


def test_absent_mapped_asset_is_skipped(project, monkeypatch, imports_ok):
    monkeypatch.setattr(installer, "COPIED", {"src/awb.py": "awb-init/assets/awb_cli.py",
                                              "src/packaging/later.py": "awb-package/assets/awb_not_shipped.py"})
    assert installer.install(project, upgrade=True)["files"] == {"src/awb.py": "installed"}
    assert installer.install(project, check=True)["requirements"] == {
        "path": "requirements.txt", "status": "unchecked", "packages": PACKAGES}


def test_refuses_non_workbench_old_python_and_unreadable_receipt(tmp_path, project, monkeypatch):
    assert installer.install(tmp_path / "missing") == {"project": str((tmp_path / "missing").resolve()),
                                                       "workbench": False,
                                                       "missing": ["AGENTS.md", "foundation/", "investigations/"],
                                                       "hint": "No workbench markers here. At the project root, first adapt "
                                                               "README.md and AGENTS.md (awb-init SKILL.md, section 3, "
                                                               "item 1); otherwise pass the project root."}
    (project / ".awb-receipt.json").write_text("{")
    before = snapshot(project)
    result = installer.install(project, upgrade=True)
    assert "restore it from Git" in result["error"] and snapshot(project) == before
    monkeypatch.setattr(installer, "PYTHON", (99, 0))
    result = installer.install(project)
    assert not result["python"]["ok"] and "error" in result
    assert snapshot(project) == before


def test_refuses_readme_only_directory(tmp_path):
    (tmp_path / "README.md").write_text("# Project\n")
    before = list(tmp_path.iterdir())
    report = installer.install(tmp_path)
    assert report["workbench"] is False
    assert report["missing"] == ["AGENTS.md", "foundation/", "investigations/"]
    assert report["hint"] == "No workbench markers here. At the project root, first adapt README.md and AGENTS.md " \
        "(awb-init SKILL.md, section 3, item 1); otherwise pass the project root."
    result = subprocess.run([sys.executable, str(SCRIPT), str(tmp_path)], capture_output=True, text=True)
    assert result.returncode == 1 and json.loads(result.stdout) == report
    assert list(tmp_path.iterdir()) == before


RETIRED = ["package-format/journal-template.md", "package-format/executive-summary-template.md",
           "src/presentation/style.py", "src/packaging/findings.py", "src/packaging/charts.py"]


@pytest.fixture
def upgradable(project, monkeypatch):
    monkeypatch.setattr(installer, "RETIRED", RETIRED)  # the skills retire none today
    earlier(project, {
        "package-format/deck-rules.md": earlier_version("package-format/deck-rules.md"),
        "workbench-guides/analysis.md": earlier_version("workbench-guides/analysis.md"),
        "package-format/journal-template.md": earlier_version("package-format/journal-template.md"),
        "src/presentation/style.py": earlier_version("src/presentation/style.py"),
        "src/packaging/findings.py": earlier_version("src/packaging/findings.py"),
    })
    write(project, {
        "package-format/findings-template.md": ASSETS["package-format/findings-template.md"].read_bytes(),
        "src/provenance.py": b"# our own provenance\n",
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
    assert files["package-format/deck-rules.md"] == "earlier"
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
    assert result["files"]["package-format/deck-rules.md"] == "replaced"
    assert result["files"]["workbench-guides/analysis.md"] == "replaced"
    assert (upgradable / "package-format/deck-rules.md").read_bytes() == \
        ASSETS["package-format/deck-rules.md"].read_bytes()
    assert receipt(upgradable) == {
        **{path: sha(ASSETS[path].read_bytes()) for path in ("package-format/deck-rules.md", "workbench-guides/analysis.md")},
        **{path: sha(earlier_version(path)) for path in
           ("package-format/journal-template.md", "src/presentation/style.py", "src/packaging/findings.py")}}
    assert (upgradable / "src/provenance.py").read_bytes() == b"# our own provenance\n"
    assert result["files"]["src/provenance.py"] == "customized"
    assert (upgradable / "src/presentation/style.py").exists()
    assert not (upgradable / "package-format/manifest-template.md").exists()


def test_upgrade_replace_and_remove_retired(upgradable, imports_ok):
    (upgradable / "package-format/executive-summary-template.md").write_text("ours\n")
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
                 "package-format/deck-rules.md")
    assert result.returncode == 0
    assert json.loads(result.stdout)["files"]["src/provenance.py"] == "customized"


@pytest.mark.parametrize("arguments, config_dirs, destination", [
    (["--mcp-config", "copilot"], {}, "home/.copilot/mcp-config.json"),
    (["--mcp-config=copilot"], {}, "home/.copilot/mcp-config.json"),
    (["--mcp-config", "copilot"], {"COPILOT_HOME": "copilot config"}, "copilot config/mcp-config.json"),
    (["--mcp-config", "copilot"], {"CLAUDE_CONFIG_DIR": "claude config"}, "home/.copilot/mcp-config.json"),
    (["--mcp-config", "claude"], {}, "home/.claude.json"),
    (["--mcp-config", "claude"], {"COPILOT_HOME": "copilot config"}, "home/.claude.json"),
    (["--mcp-config", "claude"], {"CLAUDE_CONFIG_DIR": "claude config"}, "claude config/.claude.json"),
])
def test_print_json_server_entry_without_writing(tmp_path, arguments, config_dirs, destination):
    env = {**os.environ, "HOME": str(tmp_path / "home"), "PYTHONDONTWRITEBYTECODE": "1"}
    env.pop("COPILOT_HOME", None)
    env.pop("CLAUDE_CONFIG_DIR", None)
    env.update({variable: str(tmp_path / directory) for variable, directory in config_dirs.items()})
    before = snapshot(tmp_path)
    result = subprocess.run([sys.executable, str(SCRIPT), *arguments],
                            cwd=tmp_path, env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"mcpServers": {"awb": {
        "type": "stdio", "command": sys.executable,
        "args": [str(SKILLS / "awb-init/assets/awb_mcp.py")], "env": {}}}}
    assert str(tmp_path / destination) in result.stderr
    assert snapshot(tmp_path) == before


# Host -> what the fallback merge line adds after "preserve other configuration."
FALLBACK_NOTES = {
    "claude": " Close every Claude Code session first, since Claude Code rewrites that file while it runs.",
    "codex": "",
    "copilot": "",
}


@pytest.mark.parametrize("host, destination", [
    ("copilot", ".copilot/mcp-config.json"),
    ("claude", ".claude.json"),
    ("codex", ".codex/config.toml"),
])
@pytest.mark.parametrize("version, virtual, warnings", [
    ((3, 10), False, []),
    ((3, 9), False, ["Warning: this interpreter is older than Python 3.10."]),
    ((3, 7), False, ["Warning: this interpreter is older than Python 3.10."]),
    ((3, 14), True, ["Warning: this interpreter runs in a virtual environment."]),
    ((3, 9), True, ["Warning: this interpreter is older than Python 3.10.",
                    "Warning: this interpreter runs in a virtual environment."]),
])
def test_print_server_entry_interpreter_warnings(tmp_path, monkeypatch, capsys, host, destination,
                                               version, virtual, warnings):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("COPILOT_HOME", raising=False)
    monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
    monkeypatch.delenv("CODEX_HOME", raising=False)
    monkeypatch.setattr(sys, "version_info", (3, 10))
    monkeypatch.setattr(sys, "base_prefix", str(tmp_path / "stable-python"))
    monkeypatch.setattr(sys, "prefix", str(tmp_path / "stable-python"))
    before = snapshot(tmp_path)
    installer.print_server_entry(host)
    stable = capsys.readouterr()
    lines = stable.err.splitlines(keepends=True)
    assert len(lines) == 3
    assert lines[0] == "Register awb with the host's own command, in a POSIX shell such as bash or zsh:\n"
    assert lines[1].startswith(("claude mcp add-json --scope user awb ", f"{host} mcp add awb -- "))
    assert lines[2] == ("Fallback, for other shells or when that command is unavailable: merge the printed awb "
                        f"entry into {tmp_path / destination}; preserve other configuration."
                        f"{FALLBACK_NOTES[host]}\n")
    destination_line = stable.err

    monkeypatch.setattr(sys, "version_info", version)
    if version < (3, 8):
        monkeypatch.delattr(shlex, "join")  # Added in Python 3.8.
    if virtual:
        monkeypatch.setattr(sys, "prefix", str(tmp_path / "project/.venv"))
    installer.print_server_entry(host)
    actual = capsys.readouterr()
    assert actual.out == stable.out
    expected_stderr = ""
    if warnings:
        expected_stderr += "\n".join(warnings) + "\n"
        expected_stderr += "Use a stable Python 3.10+ interpreter outside a project virtual environment.\n"
    expected_stderr += destination_line
    assert actual.err == expected_stderr
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize("codex_home, destination", [
    (None, "home/.codex/config.toml"),
    ("codex config", "codex config/config.toml"),
])
def test_print_codex_server_entry_with_quoted_unicode_paths(tmp_path, codex_home, destination):
    tomllib = pytest.importorskip("tomllib")
    # A worked install path exercises TOML escaping without shell quoting.
    skills = tmp_path / 'skills "shared" 🐍'
    script = skills / "awb-init/scripts/install_helpers.py"
    server = skills / "awb-init/assets/awb_mcp.py"
    script.parent.mkdir(parents=True)
    server.parent.mkdir(parents=True)
    shutil.copyfile(SCRIPT, script)
    shutil.copyfile(SKILLS / "awb-init/assets/awb_mcp.py", server)
    env = {**os.environ, "HOME": str(tmp_path / "home"), "PYTHONDONTWRITEBYTECODE": "1"}
    env.pop("CODEX_HOME", None)
    if codex_home is not None:
        env["CODEX_HOME"] = str(tmp_path / codex_home)
    before = snapshot(tmp_path)
    result = subprocess.run([sys.executable, str(script), "--mcp-config", "codex"],
                            cwd=tmp_path, env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert tomllib.loads(result.stdout) == {"mcp_servers": {"awb": {
        "command": sys.executable, "args": [str(server)], "env": {}}}}
    assert str(tmp_path / destination) in result.stderr
    assert snapshot(tmp_path) == before


# Host -> the registration command tokens expected for an interpreter, a server path and the entry's JSON.
REGISTRATION_COMMANDS = {
    "claude": lambda python, server, entry: ["claude", "mcp", "add-json", "--scope", "user", "awb", entry],
    "codex": lambda python, server, entry: ["codex", "mcp", "add", "awb", "--", python, server],
    "copilot": lambda python, server, entry: ["copilot", "mcp", "add", "awb", "--", python, server],
}


@pytest.mark.parametrize("host, destination", [
    ("claude", "home/.claude.json"),
    ("codex", "home/.codex/config.toml"),
    ("copilot", "home/.copilot/mcp-config.json"),
])
def test_print_host_registration_command(tmp_path, host, destination):
    # Spaces, both quote characters and Unicode in both paths exercise POSIX shell quoting.
    skills = tmp_path / "skills \"shared\" it's 🐍"
    script = skills / "awb-init/scripts/install_helpers.py"
    server = skills / "awb-init/assets/awb_mcp.py"
    script.parent.mkdir(parents=True)
    server.parent.mkdir(parents=True)
    shutil.copyfile(SCRIPT, script)
    shutil.copyfile(SKILLS / "awb-init/assets/awb_mcp.py", server)
    python = tmp_path / "stable \"py\" it's 🐍" / "python3"
    python.parent.mkdir()
    python.symlink_to(Path(sys.executable).resolve())
    env = {**os.environ, "HOME": str(tmp_path / "home"), "PYTHONDONTWRITEBYTECODE": "1"}
    env.pop("COPILOT_HOME", None)
    env.pop("CLAUDE_CONFIG_DIR", None)
    env.pop("CODEX_HOME", None)
    before = snapshot(tmp_path)
    result = subprocess.run([str(python), str(script), "--mcp-config", host],
                            cwd=tmp_path, env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    entry = {"type": "stdio", "command": str(python), "args": [str(server)], "env": {}}
    if host == "codex":
        tomllib = pytest.importorskip("tomllib")
        assert tomllib.loads(result.stdout) == {"mcp_servers": {"awb": {
            key: entry[key] for key in ("command", "args", "env")}}}
    else:
        assert json.loads(result.stdout) == {"mcpServers": {"awb": entry}}
    label, command, fallback = result.stderr.splitlines()
    assert label == "Register awb with the host's own command, in a POSIX shell such as bash or zsh:"
    tokens = shlex.split(command)
    if host == "claude":
        assert json.loads(tokens[-1]) == entry
        assert command.endswith(" " + shlex.quote(tokens[-1]))
        tokens[-1] = "entry"
    else:
        assert command.endswith(f" -- {shlex.quote(str(python))} {shlex.quote(str(server))}")
    assert tokens == REGISTRATION_COMMANDS[host](str(python), str(server), "entry")
    assert fallback == ("Fallback, for other shells or when that command is unavailable: merge the printed awb "
                        f"entry into {tmp_path / destination}; preserve other configuration.{FALLBACK_NOTES[host]}")
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize("arguments, diagnostic", [
    (["--mcp-config", "other"], "invalid choice"),
    (["--mcp-config", "Copilot"], "invalid choice"),
    (["--mcp-config", ""], "invalid choice"),
    (["--mcp-config"], "expected one argument"),
    (["--mcp-con", "copilot"], "unrecognized arguments"),
    (["--mcp-config", "copilot", "--unknown"], "unrecognized arguments"),
    (["--mcp-config", "copilot", "--check"], "cannot be combined"),
    (["--mcp-config", "claude", "--upgrade"], "cannot be combined"),
    (["--mcp-config", "codex", "--package-formats"], "cannot be combined"),
    (["--mcp-config", "copilot", "--replace", "src/awb.py"], "cannot be combined"),
    (["--mcp-config", "claude", "--remove-retired"], "cannot be combined"),
    (["--mcp-config", "codex", "."], "cannot be combined"),
])
def test_server_entry_refusals_write_nothing(tmp_path, arguments, diagnostic):
    (tmp_path / "AGENTS.md").write_text("# Existing project\n")
    home = tmp_path / "home"
    home.mkdir()
    (home / ".claude.json").write_text('{"keep": true}\n')
    before = snapshot(tmp_path)
    result = subprocess.run([sys.executable, str(SCRIPT), *arguments], cwd=tmp_path,
                            env={**os.environ, "HOME": str(home), "PYTHONDONTWRITEBYTECODE": "1"},
                            capture_output=True, text=True)
    assert result.returncode == 2
    assert not result.stdout and diagnostic in result.stderr
    assert snapshot(tmp_path) == before


def test_awb_init_installs_agents_mapping_and_resolving_guides(tmp_path):
    # awb-init adapts the root template first, then invokes the helper installer (section 3).
    shutil.copyfile(SKILLS / "awb-init/assets/workbench/AGENTS.md", tmp_path / "AGENTS.md")
    subprocess.run([sys.executable, str(SCRIPT), str(tmp_path)], check=True, capture_output=True, text=True)
    agents = (tmp_path / "AGENTS.md").read_text()
    rules = [line for line in agents.splitlines() if line.startswith("When the host offers the `awb` MCP server")]
    assert len(rules) == 1
    rule = rules[0]
    for phrase in ("and the CLI otherwise", "Each tool's description lists its commands",
                   "Pass the absolute project root as `project`"):
        assert phrase in rule
    for guide in ("workbench-guides/data.md", "workbench-guides/analysis.md"):
        assert f"]({guide})" in agents and (tmp_path / guide).is_file()


def code_spans(line):
    """Accepted input: one line of prose with zero or more nonempty single-backtick
    spans; span contents have no backtick or newline. Raise ValueError for multiline,
    unpaired or empty spans. Limits: no Markdown fences, escapes or nested code;
    prose and span contents are returned literally, without interpreting Markdown.
    """
    if "\n" in line or "\r" in line:
        raise ValueError("Expected one line of single-backtick code spans")
    pieces = line.split("`")
    if len(pieces) % 2 == 0 or any(not value for value in pieces[1::2]):
        raise ValueError("Expected nonempty paired single-backtick code spans")
    return pieces[1::2]


def skill_script_commands(text):
    """Accepted input: text whose literal python3 command targets are src/awb.py,
    <project-root>/src/awb.py, investigations/<name>/run.py, or
    <skill-directory>/scripts/NAME.py / <awb-init skill directory>/scripts/NAME.py,
    where NAME is [a-z][a-z0-9_]*. One ASCII space follows python3; target ends
    at whitespace, a backtick or end of text. Return skill directory/script pairs;
    explicitly allow the three non-skill targets without returning them. Raise
    ValueError for every other python3 target or spacing. Limits: scans literal
    python3 words only, not shell aliases, expansions or wrapped commands; arguments
    after the target are opaque and are not parsed as shell or Markdown.
    """
    scripts = []
    target = re.compile(r" (?:"
                        r"(?P<directory><skill-directory>|<awb-init skill directory>)/scripts/"
                        r"(?P<script>[a-z][a-z0-9_]*\.py)"
                        r"|src/awb\.py|<project-root>/src/awb\.py|investigations/<name>/run\.py)"
                        r"(?=\s|`|$)")
    for command in re.finditer(r"\bpython3\b", text):
        match = target.match(text, command.end())
        if not match:
            raise ValueError(f"Unsupported python3 target: {text[command.start():].splitlines()[0]}")
        if match["script"]:
            scripts.append((match["directory"], match["script"]))
    return scripts


@pytest.mark.parametrize("line, expected", [
    ("plain prose", []),
    ("Use `read` for `status`.", ["read", "status"]),
    ("`investigations/<name>/run.py`", ["investigations/<name>/run.py"]),
])
def test_code_span_scanner_accepts(line, expected):
    assert code_spans(line) == expected


@pytest.mark.parametrize("line", ["`read", "read`", "``", "``read``", "`read`\n`data`", "a\rb"])
def test_code_span_scanner_refuses(line):
    with pytest.raises(ValueError):
        code_spans(line)


@pytest.mark.parametrize("text, expected", [
    ("ordinary prose", []),
    ("python3 src/awb.py state", []),
    ("`python3 <project-root>/src/awb.py questions list`", []),
    ("python3 investigations/<name>/run.py", []),
    ("python3 <skill-directory>/scripts/collect_status.py <project-root>",
     [("<skill-directory>", "collect_status.py")]),
    ("`python3 <awb-init skill directory>/scripts/install_helpers.py . --package-formats`",
     [("<awb-init skill directory>", "install_helpers.py")]),
    ("python3 <skill-directory>/scripts/eda_scan.py\n",
     [("<skill-directory>", "eda_scan.py")]),
])
def test_skill_script_scanner_accepts(text, expected):
    assert skill_script_commands(text) == expected


@pytest.mark.parametrize("text", [
    "python3 other.py", "python3  src/awb.py", "python3\tsrc/awb.py",
    "python3 <other-directory>/scripts/scan.py", "python3 <skill-directory>/scripts/scan.py.bak",
    "python3 <skill-directory>/scripts/nested/scan.py", "python3 <skill-directory>/scripts/Scan.py",
    "python3 <skill-directory>/scripts/scan-dataset.py", "python3 <skill-directory>/scripts/scan",
])
def test_skill_script_scanner_refuses(text):
    with pytest.raises(ValueError):
        skill_script_commands(text)


@pytest.fixture
def server_tools(tmp_path):
    server = SKILLS / "awb-init/assets/awb_mcp.py"
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
            "protocolVersion": "2025-11-25", "capabilities": {},
            "clientInfo": {"name": "install-contract", "version": "1"}}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
    ]
    result = subprocess.run([sys.executable, str(server)], cwd=tmp_path, capture_output=True, text=True,
                            input="".join(json.dumps(request) + "\n" for request in requests), check=True)
    response = [json.loads(line) for line in result.stdout.splitlines()]
    return {tool["name"]: tool for tool in response[1]["result"]["tools"]}


@pytest.fixture
def instruction_rule():
    agents = (SKILLS / "awb-init/assets/workbench/AGENTS.md").read_text()
    rules = [line for line in agents.splitlines() if line.startswith("When the host offers the `awb` MCP server")]
    assert len(rules) == 1
    return rules[0]


# (skill, script): [(what the rule routes, tool, command)]
SCRIPT_ROUTES = {
    ("awb-status", "collect_status.py"): [("collect_status.py", "read", "status")],
    ("awb-explore", "eda_scan.py"): [("eda_scan.py", "data", "eda-scan"), ("--show", "read", "eda-show")],
    ("awb-clean", "scan_dataset.py"): [("scan_dataset.py", "data", "clean-scan")],
    ("awb-clean", "record_cleaning.py"): [("record_cleaning.py", "records", "clean-record")],
    ("awb-init", "install_helpers.py"): [("install_helpers.py", "setup", None)],
}


def test_instruction_and_reviewer_tools_exist_in_server_tools_list(server_tools, instruction_rule):
    tools = server_tools
    reserved = {"awb", "project", "awb.py", "investigations/<name>/run.py", "--show"}
    reserved.update(script for _, script in SCRIPT_ROUTES)
    reserved.update(command for routes in SCRIPT_ROUTES.values() for _, _, command in routes if command)
    named = set(code_spans(instruction_rule)) - reserved
    assert named == tools.keys()
    assert "`awb.py` commands" in instruction_rule
    assert "`investigations/<name>/run.py` through `run`" in instruction_rule
    assert "`--show` through `read` command `eda-show`" in instruction_rule
    assert "Pass the absolute project root as `project` on every call" in instruction_rule
    for tool in tools.values():
        description = tool["inputSchema"]["properties"]["project"]["description"]
        assert "Pass it on every call" in description
        assert "otherwise omit" not in description
    for routes in SCRIPT_ROUTES.values():
        for subject, tool, command in routes:
            route = f"`{tool}`" + (f" command `{command}`" if command else "")
            assert f"`{subject}` through {route}" in instruction_rule
            if command:
                assert command in tools[tool]["inputSchema"]["properties"]["command"]["enum"]

    reviewer = (SKILLS / "awb-package/assets/awb-package-reviewer.agent.md").read_text()
    frontmatter = reviewer.split("---", 2)[1]
    tool_line = next(line for line in frontmatter.splitlines() if line.startswith("tools:"))
    reviewer_tools = json.loads(tool_line.removeprefix("tools:").strip())
    assert reviewer_tools == ["read/readFile", "search/fileSearch", "search/listDirectory", "search/textSearch", "awb/read"]
    for tool in reviewer_tools:
        if tool.startswith("awb/"):
            name = tool.removeprefix("awb/")
            assert name in tools and tools[name]["annotations"]["readOnlyHint"] is True


def test_every_shipped_skill_script_has_an_instruction_route(instruction_rule):
    seen = set()
    for skill in sorted(SKILLS.glob("*/SKILL.md")):
        for directory, script in skill_script_commands(skill.read_text()):
            owner = "awb-init" if directory == "<awb-init skill directory>" else skill.parent.name
            assert (owner, script) in SCRIPT_ROUTES, f"Missing route for {skill}: {script}"
            assert f"`{script}` through " in instruction_rule
            seen.add((owner, script))
    assert seen == SCRIPT_ROUTES.keys()
