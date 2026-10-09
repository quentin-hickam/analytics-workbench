"""Check, record provenance for, and release an analytics workbench package draft.

awb-init's installer places this file at `src/packaging/draft.py` beside `findings.py`,
`manifest.py`, and `charts.py`. `src/awb.py` runs its commands:

    python3 src/awb.py export <investigation> <package> [--chart RESULT[:COLUMNS]]... [--dataset NAME=RESULT[:COLUMNS]]...
    python3 src/awb.py draft-provenance <investigation> <package> <result-id>... [--export-checks]
    python3 src/awb.py check-draft <investigation> <package> [--verify-only] [--manifest NAME]
    python3 src/awb.py release <investigation> <package> [--manifest NAME]
    python3 src/awb.py copy-releases <investigation> [<package>]

Each prints one line of JSON and keeps its complete record under
`deliveries/<investigation>/<package>/audit/`, outside the draft and its releases. Only JSON
manifests are automated. Standard library only, except that `export` writes chart files through
`charts.py` and so needs pandas; `src/provenance.py` is needed for `draft-provenance` and `export`.
"""

import argparse
import csv
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path

# The dispatcher puts this directory on sys.path; a direct import of this file needs it too.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from charts import check_charts  # noqa: E402
from findings import check  # noqa: E402
from manifest import compare_trees, inventory, verify  # noqa: E402

_SIMPLE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
_EVIDENCE_SCHEMAS = ("awb-evidence/1", "awb-evidence/2", "awb-evidence/3")
_EVIDENCE_LINK = re.compile(r"evidence/([A-Za-z0-9][A-Za-z0-9._-]*)\.json")
_DISPOSITIONS = ("omit", "release_with_caveat")
_STORAGE_LINE = "Released packages are kept at:"
_REASON = "Revalidation reason or caveat"
_BLOCKED = ("the current state differs from the recorded producing state; an export would not serialize "
            "the represented result. Stop: changed results need separately authorized analytical work")
_RECORD_EPILOG = ("Prints one JSON line and writes the complete record under "
                  "deliveries/<investigation>/<package>/audit/, named by its record key.")

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


# ---------------------------------------------------------------- flags and headings

def _cells(line):
    text = line.strip()
    text = text[1:] if text.startswith("|") else text
    text = text[:-1] if text.endswith("|") and not text.endswith("\\|") else text
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", text)]


def _section_table(text, title):
    """Return (header, rows) of the table under `## <title>`, or None when there is none."""
    match = re.search(rf"^## {re.escape(title)}\s*$", text, re.MULTILINE)
    if not match:
        return None
    body = re.split(r"^##? ", text[match.end():], maxsplit=1, flags=re.MULTILINE)[0]
    lines = [line for line in body.splitlines() if line.strip().startswith("|")]
    if len(lines) < 2:
        return None
    header = _cells(lines[0])
    return header, [dict(zip(header, _cells(line))) for line in lines[2:]]


def state_flags(root, investigation) -> list[dict]:
    """Return each finding state.md flags as {finding, reason}; raise ValueError when unreadable."""
    path = Path(root) / "investigations" / investigation / "state.md"
    try:
        table = _section_table(path.read_text(encoding="utf-8"), "Current findings")
    except (OSError, UnicodeError) as error:
        raise ValueError(f"investigations/{investigation}/state.md: unreadable ({error})") from error
    if table is None or not {"Finding", "Status", _REASON} <= set(table[0]):
        raise ValueError(f"investigations/{investigation}/state.md has no Current findings table with "
                         f"Finding, Status, and {_REASON} columns; flags cannot be compared")
    # The status collector's rule: a flagged finding's Status begins with revalidation-needed.
    return [{"finding": row.get("Finding", ""), "reason": row.get(_REASON, "")}
            for row in table[1] if row.get("Status", "").startswith("revalidation-needed")]


def unmatched_flags(record: dict, flags: list[dict]) -> list[dict]:
    """List each current flag whose exact finding and reason no revalidation_flags entry records."""
    recorded = record.get("revalidation_flags")
    recorded = ({(f.get("finding"), f.get("reason")) for f in recorded if isinstance(f, dict)}
                if isinstance(recorded, list) else set())
    return [flag for flag in flags if (flag["finding"], flag["reason"]) not in recorded]


def _headings(path):
    headings, fenced = [], False
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
        elif not fenced and line.startswith("### "):
            headings.append(line[4:].strip().rstrip("#").strip())
    return headings


def heading_problems(draft) -> list[dict]:
    """List each `###` finding heading in findings.md that no methodology.md heading repeats exactly."""
    methodology = set(_headings(Path(draft) / "methodology.md"))
    return [{"heading": heading, "problem": "methodology.md has no ### section with this exact heading"}
            for heading in _headings(Path(draft) / "findings.md") if heading not in methodology]


# ---------------------------------------------------------------- check-draft

def _structure_passed(report):
    return (not report["names_problems"] and not report["errors"] and report["findings"] == []
            and report["charts"] == [] and report["headings"] == [] and report["verify"] == [])


def check_draft(root, investigation, package, *, verify_only=False, manifest_name=None) -> dict:
    """Run every mechanical draft check; unless verify_only, rewrite the JSON manifest's inventory."""
    root = Path(root)
    draft = _package_dir(root, investigation, package) / "draft"
    report = {"draft": _rel(root, draft), "names": 0, "names_problems": [], "findings": None,
              "charts": None, "headings": None, "manifest": None, "inventory": None, "verify": None,
              "unmatched_flags": None, "errors": [], "passed": False}
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
        report["headings"] = heading_problems(draft)
    except (OSError, UnicodeError) as error:
        report["errors"].append(f"headings check: {error}")
    try:
        flags = state_flags(root, investigation)
    except ValueError as error:
        flags = None
        report["errors"].append(f"flags: {error}")

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
        if flags is not None:
            report["unmatched_flags"] = unmatched_flags(record, flags)
    except (OSError, ValueError) as error:
        report["errors"].append(f"manifest: {error}")

    report["passed"] = _structure_passed(report) and report["unmatched_flags"] == []
    report["record"] = _audit(root, investigation, package, "check-draft.json",
                              {**report, "names_set": names})
    return report


def _package_arguments(parser, *, package=True):
    parser.add_argument("investigation", help="investigation name under investigations/")
    if package:
        parser.add_argument("package", help="package name under deliveries/<investigation>/")


def _manifest_argument(parser):
    parser.add_argument("--manifest", help="manifest path inside the draft (default: the draft's single "
                                           "manifest* file, else manifest.json)")


def cli_check_draft(root: Path, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="awb.py check-draft", formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Run every mechanical draft check (internal names in findings.md, chart files, "
                    "matching finding headings, the manifest inventory, and state.md's current flags) "
                    "and rewrite the manifest inventory; --verify-only checks a release candidate.",
        epilog=_RECORD_EPILOG + "\nunmatched_flags lists each finding state.md flags whose exact finding "
               "and reason the manifest's revalidation_flags does not record.\nExit 0 only when "
               "names_problems, findings, charts, headings, verify, unmatched_flags, and errors are all empty.")
    _package_arguments(parser)
    parser.add_argument("--verify-only", action="store_true",
                        help="verify against the recorded inventory without rewriting it (the release gate)")
    _manifest_argument(parser)
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
            report["exports_blocked"] = _BLOCKED
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
    parser = argparse.ArgumentParser(
        prog="awb.py draft-provenance", formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Fill the draft manifest's producing and packaging state from the represented results' "
                    "evidence. Run it once the draft exists.",
        epilog=_RECORD_EPILOG + "\nWrites nothing and exits 1 when an evidence file is missing or a "
               "comparison fails (exports_blocked).")
    _package_arguments(parser)
    parser.add_argument("result_ids", nargs="+", metavar="result-id",
                        help="every result the package represents")
    parser.add_argument("--export-checks", action="store_true",
                        help="for a hand export: record each result's compare_evidence output as export_checks")
    _manifest_argument(parser)
    args = parser.parse_args(argv)
    report = draft_provenance(Path(root), _simple(args.investigation, "investigation"),
                              _simple(args.package, "package"),
                              [_simple(r, "result-id") for r in args.result_ids],
                              export_checks=args.export_checks, manifest_name=args.manifest)
    _print(report)
    return 0 if report["written"] else 1


# ---------------------------------------------------------------- export

_DISPLAY = "foundation/display.toml"


def _load_toml(path):
    try:
        import tomllib
    except ImportError:  # Python 3.10
        try:
            import tomli as tomllib
        except ImportError as error:
            raise ImportError(f"reading {path.name} needs Python 3.11 or the tomli package") from error
    return tomllib.loads(path.read_text(encoding="utf-8"))


def display_names(root) -> dict:
    """Return {columns, values, round} from foundation/display.toml, empty when it is absent."""
    path = Path(root) / _DISPLAY
    record = _load_toml(path) if path.is_file() else {}
    return {"columns": dict(record.get("columns", {})),
            "values": {column: dict(codes) for column, codes in record.get("values", {}).items()},
            "round": dict(record.get("round", {}))}


def _spec(text, what):
    """Parse RESULT[:COL,COL] into (result_id, [columns] or None)."""
    result_id, _, columns = text.partition(":")
    return _simple(result_id, what), [c.strip() for c in columns.split(",") if c.strip()] or None


def _rounded(value, places):
    # Decimal from the saved text rounds half up as a reader would, which binary floats do not.
    try:
        number = Decimal(value)
    except InvalidOperation:
        return value
    return str(number.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP))


def _shape(root, investigation, result_id, columns, display, rounding):
    """Read a saved result table and return (headers, rows, sources, problems) for the audience."""
    path = Path(root) / "investigations" / investigation / "results" / f"{result_id}.csv"
    if not path.is_file():
        return None, None, None, [f"{_rel(root, path)} is missing. Stop: saving a result table needs "
                                  "separately authorized analytical work"]
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        available, rows = list(reader.fieldnames or []), list(reader)
    chosen = columns or available
    problems = [f"{result_id}: no column {c!r} (has {', '.join(available)})" for c in chosen if c not in available]
    problems += [f"{result_id}: column {c!r} has no display name in {_DISPLAY} [columns]"
                 for c in chosen if c in available and c not in display["columns"]]
    if problems:
        return None, None, None, problems
    headers = [display["columns"][c] for c in chosen]
    out = []
    for row in rows:
        cells = []
        for column in chosen:
            value = row[column]
            value = display["values"].get(column, {}).get(value, value)
            if column in rounding and value != "":
                value = _rounded(value, int(rounding[column]))
            cells.append(value)
        out.append(cells)
    sources = [f"{header} <- {result_id}.{column}" for header, column in zip(headers, chosen)]
    return headers, out, sources, []


def export(root, investigation, package, charts, datasets, *, no_datasets=False, rounding=None,
           manifest_name=None) -> dict:
    """Serialize recorded results into the draft's chart and dataset files after the export checks."""
    root = Path(root)
    draft = _package_dir(root, investigation, package) / "draft"
    report = {"charts": [], "datasets": [], "written": False, "errors": []}
    if not draft.is_dir():
        report["errors"].append(f"no draft at {_rel(root, draft)}; create it with awb-package")
        return report
    try:
        name = report["manifest"] = _manifest_name(draft, manifest_name)
        if not name.endswith(".json"):
            raise ValueError(f"only JSON manifests are automated; export {name} by hand")
        record = _read_json(draft / name) if (draft / name).exists() else {}
        display = display_names(root)
    except (OSError, ValueError, ImportError) as error:
        report["errors"].append(str(error))
        return report
    rounding = {**display["round"], **(rounding or {})}

    shaped, sources = [], []
    for kind, label, (result_id, columns) in ([("chart", f"chart-{i}", spec) for i, spec in enumerate(charts, 1)]
                                              + [("dataset", n, spec) for n, spec in datasets]):
        headers, rows, lines, problems = _shape(root, investigation, result_id, columns, display, rounding)
        report["errors"] += problems
        if not problems:
            shaped.append((kind, label, result_id, headers, rows))
            sources += [f"{label}: {line}" for line in lines]
    if report["errors"]:
        return report

    result_ids = list(dict.fromkeys(r for _, _, r, _, _ in shaped))
    try:
        compare = _load_provenance(root).compare_evidence
    except (OSError, ImportError) as error:
        report["errors"].append(str(error))
        return report
    checks = []
    for result_id in result_ids:
        evidence = f"investigations/{investigation}/evidence/{result_id}.json"
        checks.append({"result_id": result_id, "evidence": evidence, "comparisons": compare(root, evidence)})
    failed = [{"result_id": c["result_id"], "name": i["name"], "detail": i["detail"]}
              for c in checks for i in c["comparisons"] if i["outcome"] != "pass"]
    report["export_checks"] = {"results": len(checks), "failed": failed}
    if failed:
        report["exports_blocked"] = _BLOCKED
        report["record"] = _audit(root, investigation, package, "export.json", {**report, "checks": checks})
        return report

    frames = [(headers, rows) for kind, _, _, headers, rows in shaped if kind == "chart"]
    if frames:
        import pandas as pd
        sys.path.insert(0, str(_HERE))
        from charts import write_charts
        try:
            paths = write_charts(draft / "charts", [pd.DataFrame(rows, columns=headers) for headers, rows in frames])
        except (TypeError, ValueError) as error:
            report["errors"].append(f"charts: {error}")
            return report
        chart_ids = [r for kind, _, r, _, _ in shaped if kind == "chart"]
        record["charts"] = [{"path": _rel(draft, p), "result_id": r} for p, r in zip(paths, chart_ids)]
        report["charts"] = record["charts"]
    if datasets or no_datasets:
        directory = draft / "datasets"
        directory.mkdir(exist_ok=True)
        for stale in directory.glob("*.csv"):
            stale.unlink()  # The selection is replaced whole, as write_charts replaces charts.
        for kind, label, result_id, headers, rows in shaped:
            if kind != "dataset":
                continue
            path = directory / f"{label}.csv"
            with path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.writer(stream, lineterminator="\n")
                writer.writerow(headers)
                writer.writerows(rows)
            report["datasets"].append({"path": _rel(draft, path), "result_id": result_id})
        if not any(directory.iterdir()):
            directory.rmdir()
        record["dataset_selection"] = [d["path"] for d in report["datasets"]] or "none"
    kept = [c for c in record.get("export_checks") or [] if isinstance(c, dict)
            and c.get("result_id") not in result_ids] if isinstance(record.get("export_checks"), list) else []
    record["export_checks"] = kept + checks
    _write_json(draft / name, record)
    report["written"] = True
    report["methodology_lines"] = sources
    if (draft / "findings.md").is_file():
        report["check_charts"] = check_charts(draft / "findings.md", draft / "charts")
    report["record"] = _audit(root, investigation, package, "export.json", {**report, "checks": checks})
    return report


def cli_export(root: Path, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="awb.py export", formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Write the draft's chart and dataset files from saved result tables, renamed, mapped, "
                    "and rounded through foundation/display.toml, once compare_evidence passes for every result.",
        epilog=_RECORD_EPILOG + "\nEvery exported column needs a display name in foundation/display.toml; "
               "gaps are listed together and nothing is written.\nWrites nothing when any comparison fails "
               "(exports_blocked).\nExit 0 only when written and check_charts is empty. Writing chart "
               "files needs pandas.")
    _package_arguments(parser)
    parser.add_argument("--chart", action="append", default=[], metavar="RESULT[:COLUMNS]",
                        help="one per chart, in the order of the Chart N specifications; columns comma-separated")
    parser.add_argument("--dataset", action="append", default=[], metavar="NAME=RESULT[:COLUMNS]",
                        help="one per selected dataset; replaces the whole selection")
    parser.add_argument("--no-datasets", action="store_true", help="record an explicit selection of none")
    parser.add_argument("--round", action="append", default=[], metavar="COLUMN=PLACES",
                        help="decimal places for a column, over foundation/display.toml [round]")
    _manifest_argument(parser)
    args = parser.parse_args(argv)
    if args.dataset and args.no_datasets:
        parser.error("--dataset and --no-datasets exclude each other")
    if not (args.chart or args.dataset or args.no_datasets):
        parser.error("name at least one --chart or --dataset, or --no-datasets")
    datasets = []
    for item in args.dataset:
        label, sep, spec = item.partition("=")
        if not sep:
            parser.error(f"--dataset needs NAME=RESULT: {item!r}")
        datasets.append((_simple(label, "dataset name"), _spec(spec, "result-id")))
    rounding = {}
    for item in args.round:
        column, sep, places = item.partition("=")
        if not sep or not places.isdigit():
            parser.error(f"--round needs COLUMN=PLACES: {item!r}")
        rounding[column] = int(places)
    report = export(Path(root), _simple(args.investigation, "investigation"), _simple(args.package, "package"),
                    [_spec(c, "result-id") for c in args.chart], datasets, no_datasets=args.no_datasets,
                    rounding=rounding, manifest_name=args.manifest)
    _print(report)
    return 0 if report["written"] and not report.get("check_charts") else 1


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
        if places == "none":
            continue  # A flagged finding the draft does not represent needs no disposition.
        if not isinstance(places, list) or not places:
            problems.append({"finding": finding, "place": None,
                             "problem": "flag lists no represented_in places; list them or record none"})
            continue
        for place in places:
            disposition = place.get("disposition") if isinstance(place, dict) else None
            if disposition in _DISPOSITIONS:
                continue
            problem = {None: "no disposition", "none": "no disposition",
                       "revalidate": "revalidation pending"}.get(disposition, f"unknown disposition {disposition!r}")
            problems.append({"finding": finding, "place": _place(place), "problem": problem})
    return problems


def _place(place):
    return ({k: v for k, v in place.items() if k not in {"disposition", "disposition_recorded_at"}}
            if isinstance(place, dict) else place)


def _time(value):
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def release_dispositions(record: dict, prior_released_at) -> list[dict]:
    """Each recorded disposition, `new` when recorded after the prior release (or with none before)."""
    since = _time(prior_released_at)
    rows = []
    for flag in record.get("revalidation_flags") if isinstance(record.get("revalidation_flags"), list) else []:
        places = flag.get("represented_in") if isinstance(flag, dict) else None
        for place in places if isinstance(places, list) else []:
            if not isinstance(place, dict):
                continue
            recorded = _time(place.get("disposition_recorded_at"))
            try:
                new = True if since is None else (None if recorded is None else recorded > since)
            except TypeError:  # One timestamp lacks its UTC offset.
                new = None
            rows.append({"finding": flag.get("finding"), "reason": flag.get("reason"), "place": _place(place),
                         "disposition": place.get("disposition"), "new": new})
    return rows


def provenance_gaps(record: dict) -> list[dict]:
    """Each manifest value recorded as unknown, by its dotted field path, with the reason."""
    gaps = []

    def walk(value, path):
        if _is_unknown(value):
            gaps.append({"field": path, "reason": value["unknown"]})
        elif isinstance(value, str) and value.lower().startswith("unknown"):
            gaps.append({"field": path, "reason": value})
        elif isinstance(value, dict):
            for key, item in value.items():
                walk(item, f"{path}.{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, f"{path}[{index}]")

    for key, value in record.items():
        if key not in {"inventory", "export_checks", "revalidation_flags", "caveats"}:
            walk(value, key)
    return gaps


def checkout_only_acquisitions(root, record: dict) -> list[dict]:
    """Each cited acquisition whose Acquisitions row in foundation/sources.md shows no retained copy."""
    inputs = record.get("inputs")
    entries = inputs.get("acquisitions") if isinstance(inputs, dict) else None
    paths = sorted({e["path"] for e in entries if isinstance(e, dict) and isinstance(e.get("path"), str)}
                   if isinstance(entries, list) else set())
    if not paths:
        return []
    try:
        table = _section_table((Path(root) / "foundation/sources.md").read_text(encoding="utf-8"), "Acquisitions")
    except (OSError, UnicodeError):
        table = None
    retained = {}
    for row in table[1] if table else []:
        key = (row.get("Source ID", "").strip("`").strip(), row.get("Acquisition ID", "").strip("`").strip())
        retained[key] = row.get("Retained copy", "").strip("`").strip()
    found = []
    for path in paths:
        parts = Path(path).parts
        cell = retained.get(tuple(parts[-2:])) if len(parts) >= 2 else None
        if cell is None or cell.lower() in {"", "this checkout only"}:
            found.append({"acquisition": path, "retained_copy": cell if cell is not None else "no Acquisitions row"})
    return found


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
    try:
        if target.exists():
            # An identical earlier copy is already in place; anything else is left for the user.
            differences = compare_trees(local, target)
            if not differences:
                return {"status": "already copied", "copy": str(target), "compare_trees": []}
            return {"status": "conflict", "copy": str(target), "compare_trees": differences,
                    "problem": "destination already exists and differs; nothing was overwritten"}
        shutil.copytree(local, target)
        differences = compare_trees(local, target)
    except (OSError, ValueError, shutil.Error) as error:
        return {"status": "copy failed", "copy": str(target), "problem": str(error),
                "instruction": instruction}
    return {"status": "copied" if not differences else "mismatch", "copy": str(target),
            "compare_trees": differences}


_STORAGE_FAILURES = {"conflict", "copy failed", "mismatch"}


def release(root, investigation, package, *, manifest_name=None) -> dict:
    """Verify the draft, copy it to the next numbered release, stamp it, and copy it to storage."""
    root = Path(root)
    package_dir = _package_dir(root, investigation, package)
    check_report = check_draft(root, investigation, package, verify_only=True, manifest_name=manifest_name)
    report = {"released": False, "check": {k: check_report[k] for k in ("passed", "record")}}
    if not _structure_passed(check_report):
        report["refused"] = "check-draft --verify-only does not pass"
        report["check"] = check_report
        return report
    name = check_report["manifest"]
    record = _read_json(package_dir / "draft" / name)
    problems = disposition_problems(record)
    if check_report["unmatched_flags"] or problems:
        report["refused"] = "flagged findings without a release disposition"
        report["unmatched_flags"] = check_report["unmatched_flags"]
        report["dispositions"] = problems
        return report

    released = package_dir / "released"
    existing = [p for p in released.iterdir() if p.is_dir() and p.name.isascii() and p.name.isdigit()] \
        if released.is_dir() else []
    prior = max(existing, key=lambda p: int(p.name), default=None)
    number = f"{int(prior.name) + 1 if prior else 1:03d}"  # Gaps stay unfilled.
    try:
        prior_released_at = _read_json(prior / name).get("released_at") if prior else None
    except (OSError, ValueError):
        prior_released_at = None
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
                  verify=verify(target, record["inventory"], manifest_name=name),
                  datasets=record.get("dataset_selection", {"unknown": "dataset_selection is not recorded"}),
                  dispositions=release_dispositions(record, prior_released_at),
                  provenance_gaps=provenance_gaps(record),
                  checkout_only_acquisitions=checkout_only_acquisitions(root, record),
                  storage=_copy_to_storage(root, target, investigation, package, number))
    report["record"] = _audit(root, investigation, package, f"release-{number}.json", report)
    return report


def cli_release(root: Path, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="awb.py release", formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Copy a draft that passes check-draft --verify-only, with every flagged finding "
                    "recorded and disposed, to the next numbered release and to release storage.",
        epilog=_RECORD_EPILOG + "\nRefuses, creating nothing, unless check-draft --verify-only passes and "
               "every revalidation_flags place is omit or release_with_caveat; a flag refusal lists "
               "unmatched_flags and dispositions.\nOn success it prints the report fields: datasets, "
               "dispositions (new: recorded since the prior release), provenance_gaps, "
               "checkout_only_acquisitions, verify (the local copy), and storage.\nstorage.status is copied or "
               "already copied (empty compare_trees), mismatch or conflict (compare_trees rows), copy failed "
               "(problem), unreachable or unrecorded (instruction), or none chosen (warning).\nExit 1 on "
               "refusal, a verify row, or storage status mismatch, conflict, or copy failed.")
    _package_arguments(parser)
    _manifest_argument(parser)
    args = parser.parse_args(argv)
    report = release(Path(root), _simple(args.investigation, "investigation"),
                     _simple(args.package, "package"), manifest_name=args.manifest)
    _print(report)
    if not report["released"]:
        return 1
    # A failed local verify or storage copy needs attention; the release itself stands.
    return 1 if report["verify"] or report["storage"]["status"] in _STORAGE_FAILURES else 0


# ---------------------------------------------------------------- copy-releases

def copy_releases(root, investigation, package=None) -> dict:
    """Copy every numbered release to the recorded release storage and compare each copy."""
    root = Path(root)
    kind, location = storage_location(root)
    report = {"location": location, "releases": [], "errors": []}
    base = root / "deliveries" / investigation
    if package is not None and not (base / package).is_dir():
        report["errors"].append(f"no package at {_rel(root, base / package)}")
        return report
    packages = [base / package] if package else sorted(p for p in base.iterdir() if p.is_dir()) \
        if base.is_dir() else []
    for directory in packages:
        released = directory / "released"
        numbers = sorted((p for p in released.iterdir() if p.is_dir() and p.name.isascii() and p.name.isdigit()),
                         key=lambda p: int(p.name)) if released.is_dir() else []
        rows = [{"release": _rel(root, p),
                 "storage": _copy_to_storage(root, p, investigation, directory.name, p.name)} for p in numbers]
        if rows:
            _audit(root, investigation, directory.name, "copy-releases.json",
                   {"location": location, "releases": rows})
        report["releases"] += rows
    if not report["releases"]:
        report["errors"].append(f"no numbered releases under {_rel(root, base)}")
    return report


def cli_copy_releases(root: Path, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="awb.py copy-releases", formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Copy every existing numbered release of an investigation (or one package) to the "
                    "README's recorded release storage and compare each copy with compare_trees.",
        epilog="Prints one JSON line with one storage row per release, statuses as release reports them; an "
               "identical existing copy is already copied, a differing one a conflict, never overwritten.\n"
               "Writes each package's complete record to deliveries/<investigation>/<package>/audit/"
               "copy-releases.json.\nExit 1 when no release exists or any storage status is mismatch, "
               "conflict, or copy failed.")
    _package_arguments(parser, package=False)
    parser.add_argument("package", nargs="?", help="package name under deliveries/<investigation>/ "
                                                   "(default: every package)")
    args = parser.parse_args(argv)
    report = copy_releases(Path(root), _simple(args.investigation, "investigation"),
                           _simple(args.package, "package") if args.package else None)
    _print(report)
    failed = report["errors"] or any(r["storage"]["status"] in _STORAGE_FAILURES for r in report["releases"])
    return 1 if failed else 0
