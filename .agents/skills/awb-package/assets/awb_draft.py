"""Check, record provenance for, and release an analytics workbench package draft.

Copy this file to `src/packaging/draft.py` beside `findings.py`, `manifest.py`, and `charts.py`;
do not import it from the skill folder. `src/awb.py` runs its commands:

    python3 src/awb.py check-draft <investigation> <package> [--verify-only] [--manifest NAME]
    python3 src/awb.py draft-provenance <investigation> <package> <result-id>... [--export-checks]
    python3 src/awb.py release <investigation> <package> [--manifest NAME]

Each prints one line of JSON and keeps its complete record under
`deliveries/<investigation>/<package>/audit/`, outside the draft and its releases. Only JSON
manifests are automated. Standard library only; `src/provenance.py` is needed for
`draft-provenance`.
"""

import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# The dispatcher puts this directory on sys.path; a direct import of this file needs it too.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from charts import check_charts  # noqa: E402
from findings import check  # noqa: E402
from manifest import compare_trees, inventory, verify  # noqa: E402

_SIMPLE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
_EVIDENCE_SCHEMAS = ("awb-evidence/1", "awb-evidence/2")
_EVIDENCE_LINK = re.compile(r"evidence/([A-Za-z0-9][A-Za-z0-9._-]*)\.json")
_DISPOSITIONS = ("omit", "release_with_caveat")
_STORAGE_LINE = "Released packages are kept at:"

# SQL names: comments and string literals are blanked first so paths and prose never count.
_SQL_NOISE = re.compile(r"--[^\n]*|/\*.*?\*/|'(?:[^']|'')*'", re.DOTALL)
_IDENT = r'(?:"[^"]+"|[A-Za-z_][\w$]*)(?:\s*\.\s*(?:"[^"]+"|[A-Za-z_][\w$]*))*'
_CREATE = re.compile(r"\bCREATE\s+(?:OR\s+REPLACE\s+)?(?:(?:TEMP|TEMPORARY|MATERIALIZED)\s+)?"
                     rf"(?:VIEW|TABLE)\s+(?:IF\s+NOT\s+EXISTS\s+)?({_IDENT})", re.IGNORECASE)
# A source not followed by `(` (a table function) or `)` (EXTRACT(year FROM column)).
_SOURCE = re.compile(rf"\b(?:FROM|JOIN)\s+({_IDENT})(?![\w$\"])(?!\s*[.()])", re.IGNORECASE)
_CTE = re.compile(rf"(?:\bWITH(?:\s+RECURSIVE)?|,)\s*({_IDENT})\s*(?:\([^)]*\)\s*)?AS\s*"
                  r"(?:NOT\s+)?(?:MATERIALIZED\s+)?\(", re.IGNORECASE)
_NOT_TABLES = {"lateral", "unnest", "values", "select"}


# ---------------------------------------------------------------- shared paths and records

def _simple(value, what):
    if not _SIMPLE.fullmatch(value):
        raise SystemExit(f"{what} must be a simple name (letters, digits, '.', '_', '-'): {value!r}")
    return value


def _rel(root, path):
    try:
        return Path(path).relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _package_dir(root, investigation, package):
    return root / "deliveries" / investigation / package


def _manifest_name(draft, requested):
    if requested:
        return requested
    found = sorted(p.name for p in draft.iterdir() if p.is_file() and p.name.startswith("manifest"))
    if len(found) > 1:
        raise ValueError(f"several manifest files ({', '.join(found)}); name one with --manifest")
    return found[0] if found else "manifest.json"


def _read_json(path):
    record = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(record, dict):
        raise ValueError(f"{path.name} is not a JSON object")
    return record


def _write_json(path, record):
    # Atomic, so an interrupted write never leaves a half manifest in the draft.
    path = Path(path)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        temporary.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _audit(root, investigation, package, name, record):
    directory = _package_dir(root, investigation, package) / "audit"
    directory.mkdir(parents=True, exist_ok=True)
    _write_json(directory / name, record)
    return _rel(root, directory / name)


def _print(report):
    print(json.dumps(report))


def _is_unknown(value):
    return isinstance(value, dict) and set(value) == {"unknown"}


def _evidence_files(root, investigation):
    """Yield (path, evidence or None, problem or None) for each awb-evidence file."""
    directory = root / "investigations" / investigation / "evidence"
    for path in sorted(directory.glob("*.json")) if directory.is_dir() else []:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            yield path, None, f"{_rel(root, path)}: unreadable ({error})"
            continue
        # Export-check lists and other audit files can sit beside the evidence.
        if isinstance(record, dict) and record.get("schema") in _EVIDENCE_SCHEMAS:
            yield path, record, None


# ---------------------------------------------------------------- the names set

def _sql_names(text):
    text = _SQL_NOISE.sub("''", text)
    ctes = {_unquote(name) for name in _CTE.findall(text)}
    names = set()
    for name in _CREATE.findall(text) + [
            source for source in _SOURCE.findall(text)
            if _unquote(source) not in ctes and _unquote(source).lower() not in _NOT_TABLES]:
        name = _unquote(name)
        names.update({name, name.rsplit(".", 1)[-1]})
    return names


def _unquote(name):
    return ".".join(part.strip().strip('"') for part in name.split("."))


def _keys(value, prefix=""):
    names = set()
    if isinstance(value, dict) and not _is_unknown(value):
        for key, item in value.items():
            # A nested key alone is often a plain word ("start"); only its dotted path is a name.
            dotted = f"{prefix}.{key}" if prefix else str(key)
            names.update({dotted}, _keys(item, dotted))
    elif isinstance(value, list):
        for item in value:
            names.update(_keys(item, prefix))
    return names


def _toml_keys(text):
    try:
        import tomllib
    except ImportError:  # Python 3.10: table headers and key lines are enough for names.
        names = set()
        for header in re.findall(r"^\s*\[\[?\s*([^\]]+?)\s*\]\]?", text, re.MULTILINE):
            parts = [part.strip().strip("\"'") for part in header.split(".")]
            names.update(".".join(parts[:i]) for i in range(1, len(parts) + 1))
        for key in re.findall(r"^\s*([A-Za-z0-9_\-\"'.]+)\s*=", text, re.MULTILINE):
            names.add(".".join(part.strip("\"'") for part in key.split(".")))
        return names
    return _keys(tomllib.loads(text))


def project_names(root, investigation, package):
    """Return the findings-check names the project records, and problems that leave it incomplete."""
    root = Path(root)
    names, problems = {investigation, package}, []
    view_files = set((root / "foundation/views").rglob("*.sql")) if (root / "foundation/views").is_dir() else set()
    settings_files = {root / "investigations" / investigation / "settings.toml"}
    settings_found = False

    for path, evidence, problem in _evidence_files(root, investigation):
        if problem:
            problems.append(problem)
            continue
        names.update({path.stem, str(evidence.get("result_id") or path.stem)})
        views = evidence.get("views")
        for entry in views if isinstance(views, list) else []:
            if isinstance(entry, dict) and isinstance(entry.get("path"), str):
                view_files.add(root / entry["path"])
        settings = evidence.get("settings")
        if isinstance(settings, dict) and not _is_unknown(settings):
            if isinstance(settings.get("path"), str):
                settings_files.add(root / settings["path"])
            if isinstance(settings.get("content"), dict) and not _is_unknown(settings["content"]):
                names.update(_keys(settings["content"]))
                settings_found = True

    for record in ("brief.md", "state.md", "history.md"):
        try:
            names.update(_EVIDENCE_LINK.findall(
                (root / "investigations" / investigation / record).read_text(encoding="utf-8")))
        except FileNotFoundError:
            pass
        except (OSError, UnicodeError) as error:
            problems.append(f"investigations/{investigation}/{record}: unreadable ({error})")

    for path in sorted(view_files):
        try:
            names.update(_sql_names(path.read_text(encoding="utf-8")))
        except FileNotFoundError:
            pass  # A view cited by old evidence and since removed has nothing left to read.
        except (OSError, UnicodeError) as error:
            problems.append(f"{_rel(root, path)}: unreadable ({error})")

    for path in sorted(settings_files):
        if not path.is_file():
            continue
        settings_found = True
        try:
            text = path.read_text(encoding="utf-8")
            if path.suffix == ".toml":
                names.update(_toml_keys(text))
            elif path.suffix == ".json":
                names.update(_keys(json.loads(text)))
            else:
                problems.append(f"{_rel(root, path)}: only TOML and JSON settings are read; "
                                "add its keys by hand")
        except (OSError, UnicodeError, ValueError) as error:
            problems.append(f"{_rel(root, path)}: unparsed ({error})")
    if not settings_found:
        problems.append(f"no settings found: investigations/{investigation}/settings.toml is absent "
                        "and no evidence records a settings file")
    names.discard("")
    return sorted(names), problems


# ---------------------------------------------------------------- check-draft

def check_draft(root, investigation, package, *, verify_only=False, manifest_name=None) -> dict:
    """Run every mechanical draft check; unless verify_only, rewrite the JSON manifest's inventory."""
    root = Path(root)
    draft = _package_dir(root, investigation, package) / "draft"
    report = {"draft": _rel(root, draft), "names": 0, "names_problems": [], "findings": None,
              "charts": None, "manifest": None, "inventory": None, "verify": None, "errors": [],
              "passed": False}
    if not draft.is_dir():
        report["errors"].append(f"no draft at {report['draft']}; create it with awb-package")
        return report

    names, report["names_problems"] = project_names(root, investigation, package)
    report["names"] = len(names)
    findings_path = draft / "findings.md"
    try:
        report["findings"] = check(findings_path, names=names)
    except (OSError, UnicodeError) as error:
        report["errors"].append(f"findings check: {error}")
    try:
        report["charts"] = check_charts(findings_path, draft / "charts")
    except (OSError, UnicodeError) as error:
        report["errors"].append(f"charts check: {error}")

    try:
        name = report["manifest"] = _manifest_name(draft, manifest_name)
        if not name.endswith(".json"):
            raise ValueError(f"only JSON manifests are automated; build the inventory of {name} "
                             "and run verify from src/packaging/manifest.py")
        path = draft / name
        if not path.is_file():
            raise ValueError(f"no manifest at {_rel(root, path)}; write it from "
                             "package-format/manifest-template.md first")
        record = _read_json(path)
        if not verify_only:
            record["inventory"] = inventory(draft, manifest_name=name)
            _write_json(path, record)
        elif not isinstance(record.get("inventory"), list):
            raise ValueError(f"{name} records no inventory list; run check-draft without --verify-only")
        report["inventory"] = {"rows": len(record["inventory"]),
                               "source": "recorded" if verify_only else "rewritten"}
        report["verify"] = verify(draft, record["inventory"], manifest_name=name)
    except (OSError, ValueError) as error:
        report["errors"].append(f"manifest: {error}")

    report["passed"] = (not report["names_problems"] and not report["errors"]
                        and report["findings"] == [] and report["charts"] == [] and report["verify"] == [])
    report["record"] = _audit(root, investigation, package, "check-draft.json",
                              {**report, "names_set": names})
    return report


def cli_check_draft(root: Path, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="awb.py check-draft", description=(
        "Check a package draft: findings names, charts, and the manifest inventory."))
    parser.add_argument("investigation")
    parser.add_argument("package")
    parser.add_argument("--verify-only", action="store_true",
                        help="verify the recorded inventory without rewriting it (release verification)")
    parser.add_argument("--manifest", help="manifest path inside the draft (default: its manifest file)")
    args = parser.parse_args(argv)
    report = check_draft(Path(root), _simple(args.investigation, "investigation"),
                         _simple(args.package, "package"),
                         verify_only=args.verify_only, manifest_name=args.manifest)
    _print(report)
    return 0 if report["passed"] else 1


# ---------------------------------------------------------------- draft-provenance

def _git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE).stdout.decode()


def packaging_state(root, paths=("src", "package-format")) -> tuple:
    """Return the packaging checkout's commit and its uncommitted package-source paths."""
    try:
        if _git(root, "rev-parse", "--is-inside-work-tree").strip() != "true":
            raise ValueError
    except (OSError, ValueError, subprocess.CalledProcessError):
        unknown = {"unknown": "the project is not a git repository"}
        return unknown, unknown
    try:
        commit = _git(root, "rev-parse", "--verify", "HEAD").strip()
    except subprocess.CalledProcessError:
        commit = {"unknown": "the checkout has no commit yet"}
    prefix = _git(root, "rev-parse", "--show-prefix").strip()
    changes = []
    entries = iter(_git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all",
                        "--", *paths).split("\0"))
    for entry in entries:
        if not entry:
            continue
        status, path = entry[:2], entry[3:]
        if "R" in status or "C" in status:
            next(entries, None)
        changes.append({"path": path.removeprefix(prefix), "status": status.strip()})
    return commit, changes or "none"


def _single(values):
    """One value when every result agrees; otherwise each distinct value with its results."""
    groups = {}
    for result_id, value in values.items():
        groups.setdefault(json.dumps(value, sort_keys=True), (value, []))[1].append(result_id)
    if len(groups) == 1:
        return next(iter(groups.values()))[0]
    return [{"results": results, "value": value} for value, results in groups.values()]


def _union(values):
    """Every distinct entry across results, each naming the results that recorded it."""
    rows = {}
    for result_id, entries in values.items():
        for entry in [entries] if not isinstance(entries, list) else entries:
            key = json.dumps(entry, sort_keys=True)
            rows.setdefault(key, {**entry, "results": []} if isinstance(entry, dict)
                            else {"value": entry, "results": []})["results"].append(result_id)
    return list(rows.values())


def producing_state(evidence: dict) -> dict:
    """Map {result_id: awb-evidence record} to the manifest's producing-state fields."""
    field = lambda key: {r: e.get(key, {"unknown": f"evidence lacks {key}"}) for r, e in evidence.items()}
    commits = field("producing_commit")
    changes = {r: v for r, v in field("producing_uncommitted_changes").items() if v != []}
    return {
        "producing_commit": _single(commits),
        "producing_uncommitted_changes": _union(changes) if changes else "none",
        "inputs": {"publications": _union(field("publications")),
                   "acquisitions": _union(field("acquisitions")),
                   "views": _union(field("views"))},
        "analytical_settings": _single(field("settings")),
    }


def _load_provenance(root):
    path = Path(root) / "src/provenance.py"
    if not path.is_file():
        raise FileNotFoundError("src/provenance.py is missing; install it from the awb-init skill")
    spec = importlib.util.spec_from_file_location("awb_project_provenance", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def draft_provenance(root, investigation, package, result_ids, *, export_checks=False,
                     manifest_name=None) -> dict:
    """Write the producing and packaging state, and optionally export checks, into the JSON manifest."""
    root = Path(root)
    draft = _package_dir(root, investigation, package) / "draft"
    report = {"manifest": None, "results": list(result_ids), "written": False, "errors": []}
    if not draft.is_dir():
        report["errors"].append(f"no draft at {_rel(root, draft)}; create it with awb-package")
        return report
    try:
        name = report["manifest"] = _manifest_name(draft, manifest_name)
        if not name.endswith(".json"):
            raise ValueError(f"only JSON manifests are automated; fill the producing state of {name} by hand")
        path = draft / name
        report["created"] = not path.exists()
        record = {} if report["created"] else _read_json(path)
    except (OSError, ValueError) as error:
        report["errors"].append(f"manifest: {error}")
        return report

    evidence, evidence_paths = {}, {}
    for result_id in result_ids:
        evidence_path = root / "investigations" / investigation / "evidence" / f"{result_id}.json"
        evidence_paths[result_id] = _rel(root, evidence_path)
        try:
            evidence[result_id] = _read_json(evidence_path)
            if evidence[result_id].get("schema") not in _EVIDENCE_SCHEMAS:
                raise ValueError("not an awb-evidence file")
        except (OSError, ValueError) as error:
            report["errors"].append(f"missing evidence: {_rel(root, evidence_path)}: {error}")
    if report["errors"]:
        return report

    fields = producing_state(evidence)
    fields["packaging_commit"], fields["packaging_uncommitted_changes"] = packaging_state(root)
    if export_checks:
        try:
            compare = _load_provenance(root).compare_evidence
        except (OSError, ImportError) as error:
            report["errors"].append(str(error))
            return report
        fields["export_checks"] = [{"result_id": r, "evidence": evidence_paths[r],
                                    "comparisons": compare(root, evidence_paths[r])} for r in result_ids]
        failed = [{"result_id": entry["result_id"], "name": item["name"], "detail": item["detail"]}
                  for entry in fields["export_checks"] for item in entry["comparisons"]
                  if item["outcome"] != "pass"]
        report["export_checks"] = {"comparisons": sum(len(e["comparisons"]) for e in fields["export_checks"]),
                                   "failed": failed}
        if failed:
            report["exports_blocked"] = ("the current state differs from the recorded producing state; "
                                         "an export would not serialize the represented result")
    commits, changes = fields["producing_commit"], fields["producing_uncommitted_changes"]
    report["producing_commit"] = "differs by result" if isinstance(commits, list) else commits
    report["producing_uncommitted_changes"] = len(changes) if isinstance(changes, list) else 0
    report["packaging_commit"] = fields["packaging_commit"]
    report["packaging_uncommitted_changes"] = fields["packaging_uncommitted_changes"]
    report["record"] = _audit(root, investigation, package, "draft-provenance.json",
                              {**report, "fields": fields})
    if report.get("exports_blocked"):
        return report  # Nothing is written, so no failing check is mistaken for a recorded export.
    record.update(fields)
    _write_json(draft / name, record)
    report["written"] = True
    return report


def cli_draft_provenance(root: Path, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="awb.py draft-provenance", description=(
        "Fill the draft manifest's producing and packaging state from the results' evidence."))
    parser.add_argument("investigation")
    parser.add_argument("package")
    parser.add_argument("result_ids", nargs="+", metavar="result-id",
                        help="every result the package represents")
    parser.add_argument("--export-checks", action="store_true",
                        help="run compare_evidence for each result and record export_checks")
    parser.add_argument("--manifest", help="manifest path inside the draft (default: its manifest file)")
    args = parser.parse_args(argv)
    report = draft_provenance(Path(root), _simple(args.investigation, "investigation"),
                              _simple(args.package, "package"),
                              [_simple(r, "result-id") for r in args.result_ids],
                              export_checks=args.export_checks, manifest_name=args.manifest)
    _print(report)
    return 0 if report["written"] else 1


# ---------------------------------------------------------------- release

def disposition_problems(record: dict) -> list[dict]:
    """List each revalidation-flag place whose disposition does not allow release."""
    flags = record.get("revalidation_flags")
    if flags == "none" or flags == []:
        return []
    if not isinstance(flags, list):
        return [{"finding": None, "place": None,
                 "problem": "revalidation_flags is missing; record none or each flag"}]
    problems = []
    for flag in flags:
        places = flag.get("represented_in") if isinstance(flag, dict) else None
        finding = flag.get("finding") if isinstance(flag, dict) else None
        if not isinstance(places, list) or not places:
            problems.append({"finding": finding, "place": None, "problem": "flag lists no represented_in places"})
            continue
        for place in places:
            disposition = place.get("disposition") if isinstance(place, dict) else None
            if disposition in _DISPOSITIONS:
                continue
            problem = {None: "no disposition", "none": "no disposition",
                       "revalidate": "revalidation pending"}.get(disposition, f"unknown disposition {disposition!r}")
            where = ({k: v for k, v in place.items() if k not in {"disposition", "disposition_recorded_at"}}
                     if isinstance(place, dict) else place)
            problems.append({"finding": finding, "place": where, "problem": problem})
    return problems


def storage_location(root) -> tuple:
    """Return (kind, location) from the README: path, unreachable, none-chosen, or unrecorded."""
    try:
        lines = (Path(root) / "README.md").read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        lines = []
    values = [line[len(_STORAGE_LINE):].strip().strip("`").strip()
              for line in lines if line.startswith(_STORAGE_LINE)]
    value = values[0] if len(values) == 1 else ""
    if not value or value.lower() in {"not yet recorded", "unknown"}:
        return "unrecorded", None
    if value.lower() in {"none", "none chosen"}:
        return "none-chosen", value
    # A URL or prose needs the user's own copy, never a speculative network call.
    if "://" in value or not value.startswith(("/", "~", "./", "../")):
        return "unreachable", value
    return "path", value


def _copy_to_storage(root, local, investigation, package, number):
    kind, location = storage_location(root)
    if kind == "none-chosen":
        return {"status": "none chosen",
                "warning": f"no release storage was chosen; {_rel(root, local)} in this checkout is the only copy"}
    destination = f"{location}/{investigation}/{package}/released/{number}/" if location else None
    instruction = (f"copy {_rel(root, local)}/ to {destination}" if destination else
                   f"record where released packages are kept, then copy {_rel(root, local)}/ there "
                   f"as <location>/{investigation}/{package}/released/{number}/")
    if kind != "path":
        return {"status": kind, "location": location, "instruction": instruction}
    base = Path(location).expanduser()
    base = base if base.is_absolute() else Path(root) / base
    if not base.is_dir():
        return {"status": "unreachable", "location": location, "instruction": instruction}
    target = base / investigation / package / "released" / number
    if target.exists():
        return {"status": "conflict", "copy": str(target),
                "problem": "destination already exists; nothing was overwritten"}
    try:
        shutil.copytree(local, target)
        differences = compare_trees(local, target)
    except (OSError, ValueError, shutil.Error) as error:
        return {"status": "copy failed", "copy": str(target), "problem": str(error),
                "instruction": instruction}
    return {"status": "copied" if not differences else "mismatch", "copy": str(target),
            "compare_trees": differences}


def release(root, investigation, package, *, manifest_name=None) -> dict:
    """Verify the draft, copy it to the next numbered release, stamp it, and copy it to storage."""
    root = Path(root)
    package_dir = _package_dir(root, investigation, package)
    check_report = check_draft(root, investigation, package, verify_only=True, manifest_name=manifest_name)
    report = {"released": False, "check": {k: check_report[k] for k in ("passed", "record")}}
    if not check_report["passed"]:
        report["refused"] = "check-draft --verify-only does not pass"
        report["check"] = check_report
        return report
    name = check_report["manifest"]
    record = _read_json(package_dir / "draft" / name)
    problems = disposition_problems(record)
    if problems:
        report["refused"] = "revalidation flags without a release disposition"
        report["dispositions"] = problems
        return report

    released = package_dir / "released"
    existing = [p for p in released.iterdir() if p.is_dir() and p.name.isascii() and p.name.isdigit()] \
        if released.is_dir() else []
    prior = max(existing, key=lambda p: int(p.name), default=None)
    number = f"{int(prior.name) + 1 if prior else 1:03d}"  # Gaps stay unfilled.
    target = released / number
    staging = released / f".{number}.{os.getpid()}.tmp"
    released.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copytree(package_dir / "draft", staging)
        record.update({"status": "release", "release_number": number,
                       "released_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                       "prior_release": f"released/{prior.name}" if prior else "none"})
        _write_json(staging / name, record)
        os.rename(staging, target)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    report.update(released=True, release=_rel(root, target), release_number=number,
                  released_at=record["released_at"], prior_release=record["prior_release"],
                  storage=_copy_to_storage(root, target, investigation, package, number))
    report["record"] = _audit(root, investigation, package, f"release-{number}.json", report)
    return report


def cli_release(root: Path, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="awb.py release", description=(
        "Copy a verified draft to its next numbered release and to release storage."))
    parser.add_argument("investigation")
    parser.add_argument("package")
    parser.add_argument("--manifest", help="manifest path inside the draft (default: its manifest file)")
    args = parser.parse_args(argv)
    report = release(Path(root), _simple(args.investigation, "investigation"),
                     _simple(args.package, "package"), manifest_name=args.manifest)
    _print(report)
    if not report["released"]:
        return 1
    # A conflict, failed copy, or compare_trees mismatch needs attention; the release itself stands.
    return 1 if report["storage"]["status"] in {"conflict", "copy failed", "mismatch"} else 0
