#!/usr/bin/env python3
"""Install the workbench helpers, guides, and references README; declare their packages; upgrade shipped copies;
print a host's registration command and user-level awb MCP server entry.

Run with the interpreter that will run the project's analysis, which it records as README's
`Project interpreter`:
    install_helpers.py [PROJECT_ROOT]                    install missing helpers, workbench guides, and the
                                                         foundation/references/ README; write requirements.txt
                                                         if absent
    install_helpers.py [PROJECT_ROOT] --package-formats  also install missing package formats
    install_helpers.py [PROJECT_ROOT] --upgrade          also replace unmodified earlier copies of helpers,
                                                         package formats, workbench guides, and that README
    install_helpers.py [PROJECT_ROOT] --upgrade --replace PATH [--replace PATH]... [--remove-retired]
    install_helpers.py [PROJECT_ROOT] --check ...        report the same without writing
    install_helpers.py --mcp-config HOST                 print the host's registration command and a
                                                         user-level MCP entry; never run or write them

Accepted input (--mcp-config): argparse accepts the exact, case-sensitive host tokens copilot,
claude, codex, supplied as --mcp-config HOST or --mcp-config=HOST. No project root or install flags
may accompany this mode. Unknown hosts/options, abbreviated options, missing values and mixed modes
are refused on stderr with exit 2 and no configuration on stdout. Output: the entry in the host's
format on stdout; on stderr, any interpreter warning, then the host's own user-level registration
command, quoted for a POSIX shell (claude mcp add-json --scope user, codex mcp add, copilot mcp add),
then the file to merge the entry into as the fallback for other shells or a host without that command.
For Claude Code the fallback says to close every Claude Code session first, since Claude Code rewrites
that file while it runs. Known limits: this prints a merge entry, not a complete replacement config; it
neither reads existing registrations nor detects the host, checks host policies, or imports
credentials. With an awb registration already present, claude mcp add-json and copilot mcp add refuse
it with exit 1 (run claude mcp remove --scope user awb or copilot mcp remove awb first) and codex mcp
add replaces it. Variables belong in env, never envFile. Config destinations use COPILOT_HOME,
CLAUDE_CONFIG_DIR or CODEX_HOME when nonempty, otherwise the host's default home path.

Install/check modes print one line of JSON:
  project, workbench  the project root and whether workbench markers exist; when absent, missing lists
                     the markers and hint explains how to initialize the root or choose another
  files              every src/ helper, workbench guide, and the references README, and with --upgrade or
                     --package-formats every shipped package format the project holds: installed, missing
                     (--check), current, earlier (an unmodified older copy; --upgrade replaces it), replaced,
                     or customized (differs from the asset and has no matching receipt entry; kept unless
                     named by --replace)
  customized         each customized file -> the installed asset to compare it with
  retired            (--upgrade) files the skills no longer ship: unmodified, removed, or customized (kept)
  requirements, python, packages, install   the third-party packages the helpers and the run.py
                     template need, where they are declared, and whether this interpreter imports them;
                     requirements.unread lists the requirements.txt lines and includes the provenance
                     helper's reader could not read, which may declare a package listed as missing;
                     install is `<python> -m pip install <packages>`, or `uv pip install --python <python>
                     <packages>` when this interpreter has no pip and its pyvenv.cfg records uv or uv is
                     on PATH; a written requirements.txt names the same tool in its header
  interpreter        README's `Project interpreter: <path>` line for this interpreter, the path relative
                     to the project inside it (in_project) and absolute outside it, with its status:
                     written, current, replaced (was names the old value, which named no file), missing
                     (--check), unrecorded without a readable README.md, or overridden when $AWB_PYTHON
                     names this interpreter, which leaves the line as it is. A README naming another
                     existing interpreter, or repeating the line, is an error: rerun with that
                     interpreter, or edit the line to switch. So is a project .venv or venv interpreter
                     other than this one while README records none: rerun with it, or name the
                     interpreter to use on the line.
Package formats stay absent until awb-package copies them with --package-formats.
The project's install receipt, .awb-receipt.json, maps each file this script installed or replaced to
its SHA-256: a file matching its entry is unmodified. A file without an entry is customized unless
it equals the shipped asset.
Existing dependency files are only read, and no package is installed. Exit status: 0 done; 1 not a
workbench, Python too old, an unreadable receipt, README naming another interpreter, or a project
venv passed over, nothing written; 2 unusable arguments.
"""

import argparse
import hashlib
import importlib
import importlib.util
import json
import os
import re
import shlex
import shutil
import sys
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2]
# The CLI asset reads README's Project interpreter line; the installer writes it with the same reader.
CLI = Path(__file__).resolve().parents[1] / "assets/awb_cli.py"
RECEIPT = ".awb-receipt.json"
PYTHON = (3, 10)
# Project path -> asset under the skills directory, for every file the skills copy into a project.
# Every path outside package-format/ is installed into each workbench; package formats wait for awb-package.
COPIED = {
    "src/awb.py": "awb-init/assets/awb_cli.py",
    "src/provenance.py": "awb-init/assets/awb_provenance.py",
    "src/preparation/landing.py": "awb-init/assets/awb_landing.py",
    "src/exploration/validate.py": "awb-init/assets/awb_validate.py",
    "src/packaging/draft.py": "awb-package/assets/awb_draft.py",
    "workbench-guides/data.md": "awb-init/assets/workbench/workbench-guides/data.md",
    "workbench-guides/analysis.md": "awb-init/assets/workbench/workbench-guides/analysis.md",
    "foundation/references/README.md": "awb-init/assets/workbench/foundation/references/README.md",
    "package-format/findings-template.md": "awb-package/assets/package-format/findings-template.md",
    "package-format/methodology-template.md": "awb-package/assets/package-format/methodology-template.md",
    "package-format/methodology-note-template.md": "awb-package/assets/package-format/methodology-note-template.md",
    "package-format/deck-rules.md": "awb-package/assets/package-format/deck-rules.md",
    "package-format/assembly/m365.md": "awb-package/assets/package-format/assembly/m365.md",
    "package-format/manifest-template.md": "awb-package/assets/package-format/manifest-template.md",
}
# Project paths the skills once copied and no longer ship; --upgrade reports them and removes unmodified
# ones on request. Add a path here when a shipped file is retired.
RETIRED = []
# Import name -> requirement for the third-party packages the helpers and the run.py template import;
# a test keeps it equal to their imports.
REQUIREMENTS = {"duckdb": "duckdb", "pandas": "pandas", "tomli": 'tomli; python_version < "3.11"'}
# Imports only older interpreters need: the tomllib fallback.
BEFORE = {"tomli": (3, 11)}


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _normalize(name):
    return re.sub(r"[-_.]+", "-", name).lower()


def _distribution(requirement):
    return requirement.split(";")[0].strip()


def _requirements_reader():
    """The provenance helper's requirements file reader, so runtime records and this check agree;
    None when the skills directory lacks that asset."""
    asset = COPIED.get("src/provenance.py")
    if asset is None or not (SKILLS / asset).is_file():
        return None
    spec = importlib.util.spec_from_file_location("awb_asset_provenance", SKILLS / asset)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.read_requirements


def _copies():
    """(project path, asset path) for every copy the installed skills ship."""
    return [(path, SKILLS / asset) for path, asset in COPIED.items() if (SKILLS / asset).is_file()]


def _declared(root):
    """(dependency files present, normalized names they declare or None when a file is unreadable
    or the requirements.txt reader is missing, requirements lines or includes that reader could not read)."""
    files, names, unread = [], set(), []
    requirements = root / "requirements.txt"
    if requirements.is_file():
        files.append("requirements.txt")
        read = _requirements_reader()
        try:
            requirements.read_bytes()
        except OSError:
            read = None
        if read is None:
            return files, None, unread
        found, unread = read(requirements)
        names |= set(found)
    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        files.append("pyproject.toml")
        try:
            import tomllib
            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        except (ImportError, ValueError):
            return files, None, unread
        project = data.get("project", {})
        specs = list(project.get("dependencies", []))
        for group in [*project.get("optional-dependencies", {}).values(), *data.get("dependency-groups", {}).values()]:
            specs += [spec for spec in group if isinstance(spec, str)]
        poetry = data.get("tool", {}).get("poetry", {})
        specs += list(poetry.get("dependencies", {}))
        for group in poetry.get("group", {}).values():
            specs += list(group.get("dependencies", {}))
        names |= {_normalize(re.match(r"\s*([A-Za-z0-9._-]*)", spec).group(1)) for spec in specs}
    return files, names, unread


def _cli():
    spec = importlib.util.spec_from_file_location("awb_asset_cli", CLI)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _interpreter_text(root):
    """This interpreter as README records it, and whether it is inside the project: project-relative
    there, absolute elsewhere. Its directories are resolved, never the file, which in a virtual
    environment links to a base interpreter without the environment's packages."""
    path = Path(os.path.abspath(sys.executable))
    try:
        return (path.parent.resolve() / path.name).relative_to(root).as_posix(), True
    except ValueError:
        return str(path), False


def _interpreter(root, check):
    """(report, error, README text to write or None) for README's Project interpreter line."""
    cli = _cli()
    value, in_project = _interpreter_text(root)
    report = {"line": f"{cli.INTERPRETER_LINE} {value}", "in_project": in_project}
    # AWB_PYTHON overrides README for awb.py and the MCP server, which runs this script under it.
    configured = cli.locate(os.environ["AWB_PYTHON"]) if os.environ.get("AWB_PYTHON") else None
    if configured and cli.same_interpreter(configured):
        return {**report, "status": "overridden"}, None, None
    status, recorded, detail = cli.read_interpreter(root)
    if status == "refused" and recorded is None:
        return report, f"{detail}; keep one, then rerun", None
    if status == "recorded":
        if cli.same_interpreter(detail):
            return {**report, "status": "current"}, None, None
        return report, (f"README's Project interpreter is {recorded}, not this interpreter ({sys.executable}); "
                        "rerun with it, or edit that line to switch"), None
    # With no interpreter recorded, awb.py runs the project's own venv: record that one, not this one.
    venv, _ = cli.project_venv(root)
    if venv is not None and not cli.same_interpreter(venv):
        return report, (f"the project has its own interpreter, {venv.relative_to(root).as_posix()}, and README "
                        "records none; rerun with it, or name the interpreter to use on README's Project "
                        "interpreter line"), None
    was = {"was": recorded} if status == "refused" else {}
    try:
        # Lines keep their endings, so a CRLF README keeps them and untouched lines keep their bytes.
        lines = re.findall(r"[^\n]*\n|[^\n]+", (root / "README.md").read_bytes().decode("utf-8"))
    except (OSError, UnicodeError):
        return {**report, "status": "unrecorded"}, None, None
    if check:
        return {**report, "status": "missing", **was}, None, None
    newline = "\r\n" if lines and lines[0].endswith("\r\n") else "\n"
    entry = report["line"] + newline
    found = [i for i, line in enumerate(lines) if line.startswith(cli.INTERPRETER_LINE)]
    if found:
        lines[found[0]] = entry
    else:
        # A new line goes after the Commits line, else Active investigation, else at the end.
        anchors = [next((i for i, line in enumerate(lines) if line.startswith(label)), None)
                   for label in ("Commits:", "Active investigation:")]
        anchor = next((i for i in anchors if i is not None), None)
        if anchor is None:
            while lines and not lines[-1].strip():
                lines.pop()
            anchor = len(lines) - 1
        if anchor >= 0 and not lines[anchor].endswith("\n"):
            lines[anchor] += newline
        lines[anchor + 1:anchor + 1] = [newline, entry] if anchor >= 0 else [entry]
    return {**report, "status": "replaced" if was else "written", **was}, None, "".join(lines)


def _has_pip():
    return importlib.util.find_spec("pip") is not None


def _made_by_uv(text):
    """Whether pyvenv.cfg text records that uv made the environment.

    Accepted input: one `key = value` per line, read as Python's site module reads it: the key is
    the text before the first `=`, stripped and lowercased, and the value the text after it, stripped.
    True for a line whose key is `uv` with a nonempty value, as uv writes `uv = <version>`. Every
    other line is refused as a record: one without `=`, a comment, another key such as `uvx`, and a
    value that merely names uv.
    """
    for line in text.splitlines():
        key, separator, value = line.partition("=")
        if separator and key.strip().lower() == "uv" and value.strip():
            return True
    return False


def _uses_uv(prefix):
    """Whether packages go in through uv: the interpreter has no pip, and uv made its environment or is
    on PATH."""
    if _has_pip():
        return False
    try:
        recorded = _made_by_uv((Path(prefix) / "pyvenv.cfg").read_text(encoding="utf-8"))
    except (OSError, UnicodeError):
        recorded = False
    return recorded or shutil.which("uv") is not None


def _pip_install(python, prefix):
    """The command that installs packages into `python`, whose environment is `prefix`."""
    return f"uv pip install --python {python}" if _uses_uv(prefix) else f"{python} -m pip install"


def _copy(asset, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(asset, target)


def install(root, *, check=False, upgrade=False, package_formats=False, replace=(), remove_retired=False):
    root = Path(root).resolve()
    python = {"executable": sys.executable, "version": ".".join(map(str, sys.version_info[:3])),
              "ok": sys.version_info >= PYTHON}
    if not python["ok"]:
        return {"project": str(root), "python": python,
                "error": "the helpers need Python 3.10+; rerun with a newer interpreter"}
    if not any((root / name).exists() for name in ("AGENTS.md", "foundation", "investigations")):
        return {"project": str(root), "workbench": False,
                "missing": ["AGENTS.md", "foundation/", "investigations/"],
                "hint": "No workbench markers here. At the project root, first adapt README.md and AGENTS.md "
                        "(awb-init SKILL.md, section 3, item 1); otherwise pass the project root."}
    try:
        receipt = json.loads((root / RECEIPT).read_text()) if (root / RECEIPT).exists() else {}
        if not isinstance(receipt, dict):
            raise ValueError("expected a JSON object")
    except (OSError, ValueError) as error:
        return {"project": str(root), "workbench": True,
                "error": f"{RECEIPT} is unreadable ({error}); restore it from Git"}
    interpreter, error, readme = _interpreter(root, check)
    if error:
        return {"project": str(root), "workbench": True, "interpreter": interpreter, "error": error}
    copies = _copies()
    unknown = set(replace) - {path for path, _ in copies}
    if unknown:
        raise ValueError(f"--replace names files the skills do not copy: {', '.join(sorted(unknown))}")

    def unmodified(path, digest):
        return path in receipt and digest == receipt[path]

    files, customized, written = {}, {}, dict(receipt)
    for path, asset in copies:
        target = root / path
        reported = not path.startswith("package-format/") or package_formats
        if not target.is_file():
            if reported:
                if not check:
                    _copy(asset, target)
                    written[path] = _sha256(asset)
                files[path] = "missing" if check else "installed"
            continue
        if not (reported or upgrade):
            continue
        digest = _sha256(target)
        status = "current" if digest == _sha256(asset) else "earlier" if unmodified(path, digest) else "customized"
        if upgrade and not check and (status == "earlier" or (status == "customized" and path in replace)):
            _copy(asset, target)
            written[path] = _sha256(asset)
            status = "replaced"
        if status == "customized":
            customized[path] = str(asset)
        files[path] = status
    result = {"project": str(root), "workbench": True, "files": files}
    if customized:
        result["customized"] = customized
    if not upgrade and "earlier" in files.values():
        result["note"] = "earlier files are unmodified older copies; awb-init repair replaces them with --upgrade"

    if upgrade:
        retired = {}
        for path in RETIRED:
            target = root / path
            if not target.is_file():
                continue
            status = "unmodified" if unmodified(path, _sha256(target)) else "customized"
            if status == "unmodified" and remove_retired and not check:
                target.unlink()
                if target.parent != root and not any(target.parent.iterdir()):
                    target.parent.rmdir()
                written.pop(path, None)
                status = "removed"
            retired[path] = status
        if retired:
            result["retired"] = retired
    if written != receipt:
        (root / RECEIPT).write_text(json.dumps(dict(sorted(written.items())), indent=2) + "\n")
    if readme is not None:
        (root / "README.md").write_bytes(readme.encode("utf-8"))
    result["interpreter"] = interpreter

    requirements = sorted(REQUIREMENTS.values(), key=str.lower)
    declared_in, declared, unread = _declared(root)
    declared_in = ", ".join(declared_in)
    if not declared_in:
        if not check:
            command = (f"uv pip install --python {_interpreter_text(root)[0]}" if _uses_uv(sys.prefix)
                       else "python3 -m pip install")
            (root / "requirements.txt").write_text(
                f"# Packages the workbench helpers in src/ need; install with {command} -r requirements.txt\n"
                + "".join(f"{requirement}\n" for requirement in requirements))
        result["requirements"] = {"path": "requirements.txt", "status": "absent" if check else "written",
                                  "packages": requirements}
    elif declared is None:
        result["requirements"] = {"path": declared_in, "status": "unchecked", "packages": requirements,
                                  **({"unread": unread} if unread else {})}
    else:
        missing = [item for item in requirements if _normalize(_distribution(item)) not in declared]
        result["requirements"] = {"path": declared_in, "status": "incomplete" if missing else "declared",
                                  **({"missing": missing} if missing else {}),
                                  **({"unread": unread} if unread else {})}

    packages, absent = {}, []
    for name, requirement in REQUIREMENTS.items():
        if name in BEFORE and sys.version_info >= BEFORE[name]:
            continue  # Only older interpreters need the fallback.
        try:
            importlib.import_module(name)
            packages[name] = "ok"
        except Exception:  # A broken install fails in ways other than ImportError.
            packages[name] = "missing"
            absent.append(_distribution(requirement))
    result["python"] = python
    result["packages"] = packages
    if absent:
        result["install"] = f"{_pip_install(sys.executable, sys.prefix)} {' '.join(absent)}"
    return result


def _toml(value):
    """A TOML value for a string, a list of strings, or a table of them; JSON strings are TOML basic strings."""
    if isinstance(value, dict):
        return "{" + ", ".join(f"{_toml(key)} = {_toml(item)}" for key, item in value.items()) + "}"
    return json.dumps(value, ensure_ascii=False)


def _home(variable, default):
    return Path(os.environ.get(variable) or Path.home() / default)


def _json_entry(entry):
    return json.dumps({"mcpServers": {"awb": entry}}, indent=2)


def _codex_entry(entry):
    return "[mcp_servers.awb]\n" + "\n".join(f"{key} = {_toml(entry[key])}" for key in ("command", "args", "env"))


def _claude_command(entry):
    return ["claude", "mcp", "add-json", "--scope", "user", "awb", json.dumps(entry)]


def _add_command(host):
    """codex mcp add and copilot mcp add share one stdio form: the name, --env KEY=VALUE per variable, then --
    and the command line."""
    def command(entry):
        env = [part for key, value in entry["env"].items() for part in ("--env", f"{key}={value}")]
        return [host, "mcp", "add", "awb", *env, "--", entry["command"], *entry["args"]]
    return command


# Host -> (its user-level configuration file, the entry rendered in that file's format, the host's own
# command that writes the same entry to its user-level configuration, a note for the hand-merge fallback).
# The README cites the source checked for each command.
SERVER_HOSTS = {
    "copilot": (lambda: _home("COPILOT_HOME", ".copilot") / "mcp-config.json", _json_entry, _add_command("copilot"),
                ""),
    "claude": (lambda: _home("CLAUDE_CONFIG_DIR", "") / ".claude.json", _json_entry, _claude_command,
               " Close every Claude Code session first, since Claude Code rewrites that file while it runs."),
    "codex": (lambda: _home("CODEX_HOME", ".codex") / "config.toml", _codex_entry, _add_command("codex"), ""),
}


def print_server_entry(host):
    """Print the awb server entry for host's user-level configuration; on stderr, any interpreter warning, then
    the host's own registration command for a POSIX shell, then that file as the fallback merge destination.
    Run and write nothing."""
    destination, render, command, fallback_note = SERVER_HOSTS[host]
    entry = {"type": "stdio", "command": str(Path(sys.executable).absolute()),
             "args": [str(SKILLS / "awb-init/assets/awb_mcp.py")], "env": {}}
    print(render(entry))
    sys.stdout.flush()  # Keep the entry above the guidance when both streams share a terminal.
    # Warnings come first: the command below registers this interpreter as soon as it is pasted.
    old_python = sys.version_info < (3, 10)
    virtual = sys.prefix != sys.base_prefix
    if old_python:
        print("Warning: this interpreter is older than Python 3.10.", file=sys.stderr)
    if virtual:
        print("Warning: this interpreter runs in a virtual environment.", file=sys.stderr)
    if old_python or virtual:
        print("Use a stable Python 3.10+ interpreter outside a project virtual environment.", file=sys.stderr)
    print("Register awb with the host's own command, in a POSIX shell such as bash or zsh:", file=sys.stderr)
    print(" ".join(shlex.quote(part) for part in command(entry)), file=sys.stderr)  # shlex.join needs 3.8.
    print("Fallback, for other shells or when that command is unavailable: merge the printed awb entry into "
          f"{destination()}; preserve other configuration.{fallback_note}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
                                     allow_abbrev=False)
    parser.add_argument("project_root", nargs="?", help="workbench root (default: the current directory)")
    parser.add_argument("--check", action="store_true", help="report without installing, replacing, or writing anything")
    parser.add_argument("--package-formats", action="store_true",
                        help="also install missing package formats and report present ones")
    parser.add_argument("--upgrade", action="store_true",
                        help="also replace unmodified earlier copies and report customized and retired files")
    parser.add_argument("--replace", action="append", default=[], metavar="PATH",
                        help="with --upgrade, also replace this customized copy, by project path; repeat for each")
    parser.add_argument("--remove-retired", action="store_true",
                        help="with --upgrade, delete retired files the project left unmodified")
    parser.add_argument("--mcp-config", choices=tuple(SERVER_HOSTS), metavar="HOST",
                        help="print HOST's registration command and user-level server entry only: "
                             + ", ".join(SERVER_HOSTS))
    args = parser.parse_args()
    if args.mcp_config:
        if (args.project_root is not None or args.check or args.upgrade or args.package_formats
                or args.replace or args.remove_retired):
            parser.error("--mcp-config cannot be combined with a project root or install flags")
        print_server_entry(args.mcp_config)
        return 0
    if (args.replace or args.remove_retired) and not args.upgrade:
        parser.error("--replace and --remove-retired need --upgrade")
    try:
        result = install(args.project_root or ".", check=args.check, upgrade=args.upgrade,
                         package_formats=args.package_formats, replace=args.replace,
                         remove_retired=args.remove_retired)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result))
    return 1 if "error" in result or result.get("workbench") is False else 0


if __name__ == "__main__":
    sys.exit(main())
