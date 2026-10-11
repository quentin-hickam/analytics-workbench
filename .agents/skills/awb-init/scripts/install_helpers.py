#!/usr/bin/env python3
"""Install the workbench helpers and guides, declare the packages they need, and upgrade shipped copies.

Run with the interpreter that will run the project's analysis:
    install_helpers.py [PROJECT_ROOT]                    install missing helpers and workbench guides;
                                                         write requirements.txt if absent
    install_helpers.py [PROJECT_ROOT] --package-formats  also install missing package formats
    install_helpers.py [PROJECT_ROOT] --upgrade          also replace unmodified earlier copies of helpers,
                                                         package formats, and workbench guides
    install_helpers.py [PROJECT_ROOT] --upgrade --replace PATH [--replace PATH]... [--remove-retired]
    install_helpers.py [PROJECT_ROOT] --check ...        report the same without writing

Prints one line of JSON:
  files              every src/ helper and workbench guide, and with --upgrade or --package-formats every
                     shipped package format the project holds: installed, missing (--check), current,
                     earlier (an unmodified older copy; --upgrade replaces it), replaced, or customized
                     (matches no shipped version: the project's own code, kept unless named by --replace)
  customized         each customized file -> the installed asset to compare it with
  retired            (--upgrade) files the skills no longer ship: unmodified, removed, or customized (kept)
  requirements, python, packages, install   the third-party packages the helpers and the run.py
                     template need, where they are declared, and whether this interpreter imports them
Package formats stay absent until awb-package copies them with --package-formats.
The project's install receipt, .awb-receipt.json, maps each file this script installed or replaced to
its SHA-256: a file matching its entry is unmodified. A file without an entry is unmodified when it
matches assets/legacy-shipped-hashes.json, the versions shipped before receipts, which is frozen.
Existing dependency files are only read, and no package is installed. Exit status: 0 done; 1 not a
workbench, Python too old, or an unreadable receipt, nothing written; 2 unusable arguments.
"""

import argparse
import hashlib
import importlib
import json
import re
import shutil
import sys
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2]
LEGACY = Path(__file__).resolve().parents[1] / "assets/legacy-shipped-hashes.json"
RECEIPT = ".awb-receipt.json"
PYTHON = (3, 10)
# Project path -> asset under the skills directory, for every file the skills copy into a project.
COPIED = {
    "src/awb.py": "awb-init/assets/awb_cli.py",
    "src/provenance.py": "awb-init/assets/awb_provenance.py",
    "src/preparation/landing.py": "awb-init/assets/awb_landing.py",
    "src/exploration/validate.py": "awb-init/assets/awb_validate.py",
    "src/packaging/draft.py": "awb-package/assets/awb_draft.py",
    "workbench-guides/data.md": "awb-init/assets/workbench/workbench-guides/data.md",
    "workbench-guides/analysis.md": "awb-init/assets/workbench/workbench-guides/analysis.md",
    "package-format/findings-template.md": "awb-package/assets/package-format/findings-template.md",
    "package-format/methodology-template.md": "awb-package/assets/package-format/methodology-template.md",
    "package-format/m365-assembly.md": "awb-package/assets/package-format/m365-assembly.md",
    "package-format/manifest-template.md": "awb-package/assets/package-format/manifest-template.md",
}
# Project paths the skills once copied and no longer ship.
RETIRED = [
    "package-format/journal-template.md",
    "package-format/executive-summary-template.md",
    "src/presentation/style.py",
    "src/packaging/findings.py",
    "src/packaging/manifest.py",
    "src/packaging/charts.py",
]
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


def _copies():
    """(project path, asset path) for every copy the installed skills ship."""
    return [(path, SKILLS / asset) for path, asset in COPIED.items() if (SKILLS / asset).is_file()]


def _declared(root):
    """(dependency files present, normalized names they declare, or None when unreadable)."""
    files, names = [], set()
    requirements = root / "requirements.txt"
    if requirements.is_file():
        files.append("requirements.txt")
        for line in requirements.read_text(encoding="utf-8", errors="replace").splitlines():
            match = re.match(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)", line.split("#")[0])
            if match and not line.lstrip().startswith("-"):
                names.add(_normalize(match.group(1)))
    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        files.append("pyproject.toml")
        try:
            import tomllib
            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        except (ImportError, ValueError):
            return files, None
        project = data.get("project", {})
        specs = list(project.get("dependencies", []))
        for group in [*project.get("optional-dependencies", {}).values(), *data.get("dependency-groups", {}).values()]:
            specs += [spec for spec in group if isinstance(spec, str)]
        poetry = data.get("tool", {}).get("poetry", {})
        specs += list(poetry.get("dependencies", {}))
        for group in poetry.get("group", {}).values():
            specs += list(group.get("dependencies", {}))
        names |= {_normalize(re.match(r"\s*([A-Za-z0-9._-]*)", spec).group(1)) for spec in specs}
    return files, names


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
        return {"project": str(root), "workbench": False}
    try:
        receipt = json.loads((root / RECEIPT).read_text()) if (root / RECEIPT).exists() else {}
        if not isinstance(receipt, dict):
            raise ValueError("expected a JSON object")
    except (OSError, ValueError) as error:
        return {"project": str(root), "workbench": True,
                "error": f"{RECEIPT} is unreadable ({error}); restore it from Git"}
    legacy = json.loads(LEGACY.read_text())
    copies = _copies()
    unknown = set(replace) - {path for path, _ in copies}
    if unknown:
        raise ValueError(f"--replace names files the skills do not copy: {', '.join(sorted(unknown))}")

    def unmodified(path, digest):
        return digest == receipt[path] if path in receipt else digest in legacy.get(path, ())

    files, customized, written = {}, {}, dict(receipt)
    for path, asset in copies:
        target = root / path
        reported = path.startswith(("src/", "workbench-guides/")) or package_formats
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

    requirements = sorted(REQUIREMENTS.values(), key=str.lower)
    declared_in, declared = _declared(root)
    declared_in = ", ".join(declared_in)
    if not declared_in:
        if not check:
            (root / "requirements.txt").write_text(
                "# Packages the workbench helpers in src/ need; install with python3 -m pip install -r requirements.txt\n"
                + "".join(f"{requirement}\n" for requirement in requirements))
        result["requirements"] = {"path": "requirements.txt", "status": "absent" if check else "written",
                                  "packages": requirements}
    elif declared is None:
        result["requirements"] = {"path": declared_in, "status": "unchecked", "packages": requirements}
    else:
        missing = [item for item in requirements if _normalize(_distribution(item)) not in declared]
        result["requirements"] = {"path": declared_in, "status": "incomplete" if missing else "declared",
                                  **({"missing": missing} if missing else {})}

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
        result["install"] = f"{sys.executable} -m pip install {' '.join(absent)}"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("project_root", nargs="?", default=".", help="workbench root (default: the current directory)")
    parser.add_argument("--check", action="store_true", help="report without installing, replacing, or writing anything")
    parser.add_argument("--package-formats", action="store_true",
                        help="also install missing package formats and report present ones")
    parser.add_argument("--upgrade", action="store_true",
                        help="also replace unmodified earlier copies and report customized and retired files")
    parser.add_argument("--replace", action="append", default=[], metavar="PATH",
                        help="with --upgrade, also replace this customized copy, by project path; repeat for each")
    parser.add_argument("--remove-retired", action="store_true",
                        help="with --upgrade, delete retired files the project left unmodified")
    args = parser.parse_args()
    if (args.replace or args.remove_retired) and not args.upgrade:
        parser.error("--replace and --remove-retired need --upgrade")
    try:
        result = install(args.project_root, check=args.check, upgrade=args.upgrade,
                         package_formats=args.package_formats, replace=args.replace,
                         remove_retired=args.remove_retired)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result))
    return 1 if "error" in result or result.get("workbench") is False else 0


if __name__ == "__main__":
    sys.exit(main())
