#!/usr/bin/env python3
"""Install every missing workbench helper under src/ and declare the packages they need.

Run with the interpreter that will run the project's analysis:
    install_helpers.py [PROJECT_ROOT]           # install missing helpers, write requirements.txt if absent
    install_helpers.py [PROJECT_ROOT] --check   # report the same without writing
Emits compact JSON. Existing helpers and dependency files are never changed, and no package
is installed. The helper list is awb-update's record of the files the skills copy verbatim;
package formats and workbench guides in that record belong to other steps and are skipped.
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
VERSIONS = SKILLS / "awb-update/assets/shipped-versions.json"
PYTHON = (3, 10)
# Import names whose pip distribution is named differently.
DISTRIBUTIONS = {"yaml": "PyYAML", "PIL": "Pillow", "sklearn": "scikit-learn"}
# Packages a helper needs without importing them: pandas reads and writes Parquet through pyarrow.
IMPLICIT = {"pyarrow": re.compile(r"\b(?:pd|pandas)\.read_parquet\(|\.to_parquet\(")}


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _normalize(name):
    return re.sub(r"[-_.]+", "-", name).lower()


def _helpers():
    """(project path, asset path, earlier hashes) for every src/ helper the installed skills ship."""
    entries = json.loads(VERSIONS.read_text())["copied"]
    return [(entry["path"], SKILLS / entry["asset"], set(entry["previous"])) for entry in entries
            if entry["path"].startswith("src/") and (SKILLS / entry["asset"]).is_file()]


def _needed(helpers):
    """Import name -> distribution name for every third-party package the shipped helpers use."""
    siblings = {Path(path).stem for path, _, _ in helpers}
    needed = {}
    for _, asset, _ in helpers:
        source = asset.read_text(encoding="utf-8")
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and not node.level:
                names = [node.module]
            else:
                continue
            for name in (name.split(".")[0] for name in names):
                if name not in sys.stdlib_module_names and name not in siblings:
                    needed[name] = DISTRIBUTIONS.get(name, name)
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


def install(root, *, check=False):
    root = Path(root).resolve()
    python = {"executable": sys.executable, "version": ".".join(map(str, sys.version_info[:3])),
              "ok": sys.version_info >= PYTHON}
    if not python["ok"]:
        return {"project": str(root), "python": python,
                "error": "the helpers need Python 3.10+; rerun with a newer interpreter"}
    if not any((root / name).exists() for name in ("AGENTS.md", "foundation", "investigations")):
        return {"project": str(root), "workbench": False}
    helpers = _helpers()

    files = {}
    for path, asset, previous in helpers:
        target = root / path
        if not target.is_file():
            if not check:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(asset, target)
            files[path] = "missing" if check else "installed"
        elif _sha256(target) == _sha256(asset):
            files[path] = "present-current"
        elif _sha256(target) in previous:
            files[path] = "present-earlier"
        else:
            files[path] = "present-customized"
    result = {"project": str(root), "workbench": True, "helpers": files}
    if "present-earlier" in files.values():
        result["helpers_note"] = "present-earlier files are unmodified older copies; awb-update refreshes them"

    needed = _needed(helpers)
    distributions = sorted(needed.values(), key=str.lower)
    declared_in, declared = _declared(root)
    declared_in = ", ".join(declared_in)
    if not declared_in:
        if not check:
            (root / "requirements.txt").write_text(
                "# Packages the workbench helpers in src/ need; install with python3 -m pip install -r requirements.txt\n"
                + "".join(f"{name}\n" for name in distributions))
        result["requirements"] = {"path": "requirements.txt", "status": "absent" if check else "written",
                                  "packages": distributions}
    elif declared is None:
        result["requirements"] = {"path": declared_in, "status": "unchecked", "packages": distributions}
    else:
        missing = [name for name in distributions if _normalize(name) not in declared]
        result["requirements"] = {"path": declared_in, "status": "incomplete" if missing else "declared",
                                  **({"missing": missing} if missing else {})}

    packages, absent = {}, []
    for name, distribution in needed.items():
        try:
            importlib.import_module(name)
            packages[name] = "ok"
        except Exception:  # A broken install fails in ways other than ImportError.
            packages[name] = "missing"
            absent.append(distribution)
    result["python"] = python
    result["packages"] = packages
    if absent:
        result["install"] = f"{sys.executable} -m pip install {' '.join(absent)}"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("project_root", nargs="?", default=".")
    parser.add_argument("--check", action="store_true", help="report without installing or writing anything")
    args = parser.parse_args()
    print(json.dumps(install(args.project_root, check=args.check)))


if __name__ == "__main__":
    main()
