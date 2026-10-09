#!/usr/bin/env python3
"""Install the workbench helpers under src/, declare the packages they need, and upgrade shipped copies.

Run with the interpreter that will run the project's analysis:
    install_helpers.py [PROJECT_ROOT]              install missing helpers; write requirements.txt if absent
    install_helpers.py [PROJECT_ROOT] --upgrade    also replace unmodified earlier copies of helpers,
                                                   package formats, and workbench guides
    install_helpers.py [PROJECT_ROOT] --upgrade --replace PATH [--replace PATH]... [--remove-retired]
    install_helpers.py [PROJECT_ROOT] --check ...  report the same without writing

Prints one line of JSON:
  files              every src/ helper, and with --upgrade every shipped package format and workbench
                     guide the project holds: installed, missing (--check), current, earlier (an
                     unmodified older copy; --upgrade replaces it), replaced, or customized (matches no
                     shipped version: the project's own code, kept unless named by --replace)
  customized         each customized file -> the installed asset to compare it with
  retired            (--upgrade) files the skills no longer ship: unmodified, removed, or customized (kept)
  old_format_drafts  (--upgrade) package drafts in an earlier format, with reasons
  requirements, python, packages, install   the third-party packages the helpers and the run.py
                     template need, where they are declared, and whether this interpreter imports them
Package formats stay absent until awb-package copies them; awb-init copies missing workbench guides.
Existing dependency files are only read, and no package is installed. The shipped-version record,
assets/shipped-versions.json, says which copies are earlier versions. Exit status: 0 done; 1 not a
workbench or Python too old, nothing written; 2 unusable arguments.
"""

import argparse
import ast
import hashlib
import importlib
import json
import re
import shutil
import sys
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2]
VERSIONS = Path(__file__).resolve().parents[1] / "assets/shipped-versions.json"
PYTHON = (3, 10)
# Shipped project files that import packages but are copied by a skill step, not by this script.
TEMPLATES = ["awb-init/assets/workbench/investigation/run.py"]
# Import names whose pip distribution is named differently.
DISTRIBUTIONS = {"yaml": "PyYAML", "PIL": "Pillow", "sklearn": "scikit-learn"}
# Fallback imports for an older Python, declared for the versions that need them.
FALLBACKS = {"tomli": (3, 11)}
# Packages a helper needs without importing them: pandas reads and writes Parquet through pyarrow.
IMPLICIT = {"pyarrow": re.compile(r"\b(?:pd|pandas)\.read_parquet\(|\.to_parquet\(")}


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _normalize(name):
    return re.sub(r"[-_.]+", "-", name).lower()


def _distribution(requirement):
    return requirement.split(";")[0].strip()


def _copies(versions):
    """(project path, asset path, earlier hashes) for every copy the installed skills ship."""
    return [(entry["path"], SKILLS / entry["asset"], set(entry["previous"])) for entry in versions["copied"]
            if (SKILLS / entry["asset"]).is_file()]


def _needed(sources):
    """Import name -> requirement for every third-party package these (project path, asset) files use.

    A fallback import inside an except handler, such as tomli for tomllib, is declared only for the
    Python versions FALLBACKS names; any other fallback is not a requirement.
    """
    project = {Path(path).stem for path, _ in sources} | {"src"}
    needed = {}
    for _, asset in sources:
        source = asset.read_text(encoding="utf-8")
        tree = ast.parse(source)
        fallbacks = {id(inner) for handler in ast.walk(tree) if isinstance(handler, ast.ExceptHandler)
                     for statement in handler.body for inner in ast.walk(statement)}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and not node.level:
                names = [node.module]
            else:
                continue
            for name in (name.split(".")[0] for name in names):
                if name in sys.stdlib_module_names or name in project:
                    continue
                if id(node) not in fallbacks:
                    needed[name] = DISTRIBUTIONS.get(name, name)
                elif name in FALLBACKS:
                    major, minor = FALLBACKS[name]
                    needed.setdefault(name, f'{DISTRIBUTIONS.get(name, name)}; python_version < "{major}.{minor}"')
        needed.update({name: name for name, pattern in IMPLICIT.items() if pattern.search(source)})
    return dict(sorted(needed.items()))


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


def _old_format_drafts(root):
    drafts = []
    for draft in sorted(root.glob("deliveries/*/*/draft")):
        findings = draft / "findings.md"
        reasons = []
        if (draft / "figures").is_dir():
            reasons.append("figures directory")
        if findings.is_file() and "**Headline:**" not in findings.read_text(encoding="utf-8", errors="replace"):
            reasons.append("findings.md is not a slide outline")
        for name in ("journal.md", "executive-summary.md"):
            if (draft / name).exists():
                reasons.append(name)
        if reasons:
            drafts.append({"path": draft.relative_to(root).as_posix(), "reasons": reasons})
    return drafts


def _copy(asset, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(asset, target)


def install(root, *, check=False, upgrade=False, replace=(), remove_retired=False):
    root = Path(root).resolve()
    python = {"executable": sys.executable, "version": ".".join(map(str, sys.version_info[:3])),
              "ok": sys.version_info >= PYTHON}
    if not python["ok"]:
        return {"project": str(root), "python": python,
                "error": "the helpers need Python 3.10+; rerun with a newer interpreter"}
    if not any((root / name).exists() for name in ("AGENTS.md", "foundation", "investigations")):
        return {"project": str(root), "workbench": False}
    versions = json.loads(VERSIONS.read_text())
    copies = _copies(versions)
    unknown = set(replace) - {path for path, _, _ in copies}
    if unknown:
        raise ValueError(f"--replace names files the skills do not copy: {', '.join(sorted(unknown))}")

    files, customized = {}, {}
    for path, asset, previous in copies:
        target, helper = root / path, path.startswith("src/")
        if not target.is_file():
            if helper:
                if not check:
                    _copy(asset, target)
                files[path] = "missing" if check else "installed"
            continue
        if not (helper or upgrade):
            continue
        digest = _sha256(target)
        status = "current" if digest == _sha256(asset) else "earlier" if digest in previous else "customized"
        if upgrade and not check and (status == "earlier" or (status == "customized" and path in replace)):
            _copy(asset, target)
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
        for entry in versions["retired"]:
            target = root / entry["path"]
            if not target.is_file():
                continue
            status = "unmodified" if _sha256(target) in set(entry["shipped"]) else "customized"
            if status == "unmodified" and remove_retired and not check:
                target.unlink()
                if target.parent != root and not any(target.parent.iterdir()):
                    target.parent.rmdir()
                status = "removed"
            retired[entry["path"]] = status
        if retired:
            result["retired"] = retired
        drafts = _old_format_drafts(root)
        if drafts:
            result["old_format_drafts"] = drafts

    sources = [(path, asset) for path, asset, _ in copies if path.startswith("src/")]
    sources += [(Path(template).name, SKILLS / template) for template in TEMPLATES if (SKILLS / template).is_file()]
    needed = _needed(sources)
    requirements = sorted(needed.values(), key=str.lower)
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
    for name, requirement in needed.items():
        if name in FALLBACKS and sys.version_info >= FALLBACKS[name]:
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
        result = install(args.project_root, check=args.check, upgrade=args.upgrade, replace=args.replace,
                         remove_retired=args.remove_retired)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result))
    return 1 if "error" in result or result.get("workbench") is False else 0


if __name__ == "__main__":
    sys.exit(main())
