"""Export, check, and release an analytics workbench package draft.

awb-init's installer places this file at `src/packaging/draft.py`. `src/awb.py` runs its commands:

    python3 src/awb.py export <investigation> <package> [--chart RESULT[:COLUMNS]]... [--dataset NAME=RESULT[:COLUMNS]]... [--no-datasets] [--result RESULT]...
    python3 src/awb.py check-draft <investigation> <package> [--verify-only]
    python3 src/awb.py release <investigation> <package>
    python3 src/awb.py copy-releases <investigation> [<package>]

Each prints one line of JSON. The manifest is the draft's `manifest.json`; chart and dataset files
are CSV. Standard library only; `export` also needs the project's `src/provenance.py`.
"""

import argparse
import csv
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path

MANIFEST = "manifest.json"
_SIMPLE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
_EVIDENCE_SCHEMAS = ("awb-evidence/1", "awb-evidence/2", "awb-evidence/3")
_EVIDENCE_LINK = re.compile(r"evidence/([A-Za-z0-9][A-Za-z0-9._-]*)\.json")
_DISPOSITIONS = ("omit", "release_with_caveat")
_STORAGE_LINE = "Released packages are kept at:"
_REASON = "Revalidation reason or caveat"
_BLOCKED = ("the current state differs from the recorded producing state; an export would not serialize "
            "the represented result. Stop: changed results need separately authorized analytical work")
# A plain word is never flagged as a name: it collides with ordinary prose ("claims", "period").
_PLAIN_WORD = re.compile(r"[A-Za-z]+")

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


def _now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _print(report):
    print(json.dumps(report))


def _is_unknown(value):
    return isinstance(value, dict) and set(value) == {"unknown"}


def _toml():
    try:
        import tomllib
    except ImportError:  # Python 3.10
        import tomli as tomllib
    return tomllib


def _evidence_files(root, investigation):
    """Yield (path, evidence or None, problem or None) for each awb-evidence file."""
    directory = root / "investigations" / investigation / "evidence"
    for path in sorted(directory.glob("*.json")) if directory.is_dir() else []:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            yield path, None, f"{_rel(root, path)}: unreadable ({error})"
            continue
        # Export-check lists and other files can sit beside the evidence.
        if isinstance(record, dict) and record.get("schema") in _EVIDENCE_SCHEMAS:
            yield path, record, None


# ---------------------------------------------------------------- internal names in findings.md

_FENCE = re.compile(r" {0,3}(`{3,}|~{3,})")
_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)")
_LINK_TARGET = re.compile(r"\]\([^)]*\)")
_TOKEN = re.compile(r"\S+")

# Wrapping punctuation and Markdown emphasis around a token; leading dots stay so `./x` is a path.
# Underscores are stripped only in matching pairs (`_word_`), so `__init__.py` keeps its own.
_LEADING = "([{<\"'*~!“‘"
_TRAILING = ")]}>\"'*~.,;:!?”’"
_POSSESSIVE = re.compile(r"['’]s$")

_PATH = re.compile(r"\w/\w")
_FRACTION = re.compile(r"[\d.,]+(?:/[\d.,]+)+")  # 3/4, 6/30/2026: numbers, not paths
_FILE_NAME = re.compile(
    r"\.(?:md|py|csv|parquet|json|sql|png|svg|duckdb|db|xlsx|yaml|yml|toml|txt|ipynb)$",
    re.IGNORECASE,
)
_SNAKE = re.compile(r"[A-Za-z0-9]+(?:_[A-Za-z0-9]+)+")
# Segments of two or more characters, so abbreviations such as e.g. and U.S. stay clean.
_DOTTED = re.compile(r"(?<![\w.])[A-Za-z_]\w+(?:\.[A-Za-z_]\w+)+")
_HEX = re.compile(r"[0-9a-fA-F]{7,40}")


def _blank(text, start, end):
    return text[:start] + " " * (end - start) + text[end:]


def _unwrap(token):
    token = _POSSESSIVE.sub("", token.lstrip(_LEADING).rstrip(_TRAILING)).rstrip(_TRAILING)
    pairs = min(len(token) - len(token.lstrip("_")), len(token) - len(token.rstrip("_")))
    if pairs:
        token = _unwrap(token[pairs:-pairs]) if 2 * pairs < len(token) else ""
    return token


def _token_kind(token):
    if token.startswith(("./", "../")) or (_PATH.search(token) and not _FRACTION.fullmatch(token)):
        return "path"
    if _FILE_NAME.search(token):
        return "file"
    if _SNAKE.search(token) or _DOTTED.search(token):
        return "identifier"
    if _HEX.fullmatch(token) and re.search(r"\d", token) and re.search(r"[a-fA-F]", token):
        return "sha"
    return None


def _name_pattern(names):
    names = sorted({name for name in names if name}, key=len, reverse=True)
    if not names:
        return None
    # Whole token: not glued to word characters, hyphens, slashes, or a dotted continuation.
    return re.compile(
        r"(?<![\w./-])(?:" + "|".join(map(re.escape, names)) + r")(?![\w/-]|\.\w)"
    )


def _scan_line(number, line, names):
    found = []
    for match in _CODE_SPAN.finditer(line):
        found.append((match.start(), "code", match.group(0)))
        line = _blank(line, match.start(), match.end())
    for match in _LINK_TARGET.finditer(line):
        line = _blank(line, match.start() + 1, match.end())

    taken = []
    if names is not None:
        for match in names.finditer(line):
            found.append((match.start(), "name", match.group(0)))
            taken.append((match.start(), match.end()))

    for match in _TOKEN.finditer(line):
        token = _unwrap(match.group(0))
        start = match.start() + match.group(0).find(token)
        end = start + len(token)
        if not token or any(start < stop and begin < end for begin, stop in taken):
            continue
        kind = _token_kind(token)
        if kind:
            found.append((start, kind, token))

    return [{"line": number, "kind": kind, "text": text} for _, kind, text in sorted(found)]


def check_findings(path: str | os.PathLike, *, names=()) -> list[dict]:
    """List code, paths, file names, identifiers, SHAs, and given names, by line then column."""
    text = Path(path).read_text(encoding="utf-8")
    text = _COMMENT.sub(lambda match: " " + "\n" * match.group(0).count("\n"), text)
    pattern = _name_pattern(names)

    rows = []
    fence = None
    for number, line in enumerate(text.splitlines(), start=1):
        if fence is not None:
            closing = _FENCE.match(line)
            if (closing and closing.group(1)[0] == fence[0] and len(closing.group(1)) >= len(fence)
                    and not line[closing.end():].strip()):
                fence = None
            continue
        opening = _FENCE.match(line)
        if opening and not (opening.group(1)[0] == "`" and "`" in line[opening.end():]):
            fence = opening.group(1)
            rows.append({"line": number, "kind": "code", "text": line.strip()})
            continue
        rows.extend(_scan_line(number, line, pattern))
    return rows


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
        return _keys(_toml().loads(text))
    except ImportError:  # Python 3.10 without tomli: table headers and key lines are enough for names.
        names = set()
        for header in re.findall(r"^\s*\[\[?\s*([^\]]+?)\s*\]\]?", text, re.MULTILINE):
            parts = [part.strip().strip("\"'") for part in header.split(".")]
            names.update(".".join(parts[:i]) for i in range(1, len(parts) + 1))
        for key in re.findall(r"^\s*([A-Za-z0-9_\-\"'.]+)\s*=", text, re.MULTILINE):
            names.add(".".join(part.strip("\"'") for part in key.split(".")))
        return names


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
    return sorted(name for name in names if name and not _PLAIN_WORD.fullmatch(name)), problems


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


# ---------------------------------------------------------------- inventory and tree comparison

_CHUNK_BYTES = 1024 * 1024  # 1 MiB reads keep memory flat on large datasets


def _scan(directory):
    root = Path(directory)
    if root.is_symlink():
        raise ValueError(f"Symlink in tree: {root}")

    def fail(error):
        raise error

    files = {}
    for current, dirnames, filenames in os.walk(root, onerror=fail):
        for name in dirnames + filenames:
            if Path(current, name).is_symlink():
                raise ValueError(f"Symlink in tree: {Path(current, name)}")
        for name in filenames:
            file = Path(current, name)
            if not file.is_file():
                continue
            digest = hashlib.sha256()
            size = 0
            with file.open("rb") as stream:
                for chunk in iter(lambda: stream.read(_CHUNK_BYTES), b""):
                    size += len(chunk)
                    digest.update(chunk)
            path = file.relative_to(root).as_posix()
            files[path] = {"path": path, "bytes": size, "sha256": digest.hexdigest()}
    return files


def inventory(package_dir: str | os.PathLike) -> list[dict]:
    """List files in path order, reserving a path-only row for manifest.json."""
    files = _scan(package_dir)
    files[MANIFEST] = {"path": MANIFEST}
    return [files[path] for path in sorted(files)]


def _difference(path, kind, expected, actual):
    return {"path": path, "kind": kind, "expected": expected, "actual": actual}


def _compare(expected, actual, manifest_name=None):
    differences = []
    for path in sorted(expected.keys() | actual.keys()):
        if path not in actual:
            recorded = None if path == manifest_name else expected[path]["sha256"]
            differences.append(_difference(path, "missing", recorded, None))
        elif path not in expected:
            differences.append(_difference(path, "extra", None, actual[path]["sha256"]))
        elif path != manifest_name:
            recorded, found = expected[path], actual[path]
            if recorded["bytes"] != found["bytes"]:
                differences.append(_difference(path, "size", recorded["bytes"], found["bytes"]))
            # A size change is also reported as a checksum change, so both kinds always name it.
            if recorded["bytes"] != found["bytes"] or recorded["sha256"].lower() != found["sha256"]:
                differences.append(_difference(path, "checksum", recorded["sha256"], found["sha256"]))
    return differences


def verify(package_dir: str | os.PathLike, inventory: list[dict]) -> list[dict]:
    """Compare a package with the inventory recorded in its manifest; manifest content is excluded."""
    expected = {}
    for row in inventory:
        path = row.get("path")
        if not isinstance(path, str):
            raise ValueError(f"Inventory row without a path: {row!r}")
        if path in expected:
            raise ValueError(f"Duplicate inventory path: {path}")
        expected[path] = dict(row)
        if path != MANIFEST:
            if "bytes" not in row or not isinstance(row.get("sha256"), str):
                raise ValueError(f"Incomplete inventory row: {path}")
            size = row["bytes"]
            if isinstance(size, str) and size.isascii() and size.isdigit():
                size = int(size)
            if type(size) is not int or size < 0:
                raise ValueError(f"Invalid inventory byte size: {path}")
            expected[path]["bytes"] = size
    return _compare(expected, _scan(package_dir), MANIFEST)


def compare_trees(local_dir: str | os.PathLike, copy_dir: str | os.PathLike) -> list[dict]:
    """Compare every file, including the manifest, with the local release as expected."""
    return _compare(_scan(local_dir), _scan(copy_dir))


# ---------------------------------------------------------------- chart files

# A package's charts/ holds one CSV per **Chart N.** specification in findings.md, named chart-N.csv
# in specification order: a header row of display names and the plotted values, nothing else.
_CHART_SPEC = re.compile(r"\*\*Chart (\d+)\.\*\*")
_CHART_FILE = re.compile(r"chart-([1-9]\d*)\.csv")
# An underscore or a dot between letters marks a column name or code, not a display name.
_IDENTIFIER = re.compile(r"[A-Za-z0-9]_[A-Za-z0-9]|[A-Za-z]\.[A-Za-z]")


def _check_chart(number, headers, rows):
    if not rows:
        raise ValueError(f"Chart {number} has no rows")
    if not all(isinstance(header, str) and header.strip() for header in headers):
        raise ValueError(f"Chart {number} has a blank or non-text header")
    if len(set(headers)) != len(headers):
        raise ValueError(f"Chart {number} repeats a header")
    for header in headers:
        if _IDENTIFIER.search(header):
            raise ValueError(f"Chart {number} header is not a display name: {header}")


def write_charts(charts_dir: str | os.PathLike, charts: list) -> list[Path]:
    """Replace the chart files with chart-1.csv, ... from (headers, rows) pairs; none removes them."""
    for number, (headers, rows) in enumerate(charts, start=1):
        _check_chart(number, headers, rows)
    directory = Path(charts_dir)
    if directory.is_dir():
        for stale in directory.iterdir():
            if _CHART_FILE.fullmatch(stale.name):
                stale.unlink()
    if not charts:
        if directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()  # A package without charts has no charts directory.
        return []
    directory.mkdir(parents=True, exist_ok=True)
    paths = []
    for number, (headers, rows) in enumerate(charts, start=1):
        path = directory / f"chart-{number}.csv"
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(headers)
            writer.writerows(rows)
        paths.append(path)
    return paths


def check_charts(findings_path: str | os.PathLike, charts_dir: str | os.PathLike) -> list[dict]:
    """Match the chart specifications in findings.md with the chart files."""
    numbers = [int(match.group(1)) for match in _CHART_SPEC.finditer(
        Path(findings_path).read_text(encoding="utf-8"))]
    rows = []
    for position, number in enumerate(numbers, start=1):
        if number != position:
            rows.append({"chart": f"Chart {number}",
                         "problem": f"specification {position} is numbered {number}"})
    directory = Path(charts_dir)
    files = {}
    if directory.is_dir():
        for path in directory.iterdir():
            match = _CHART_FILE.fullmatch(path.name)
            if match:
                files[int(match.group(1))] = path
            else:
                rows.append({"chart": path.name, "problem": "not a chart file"})
    specified = set(numbers)
    for number in sorted(specified - files.keys()):
        rows.append({"chart": f"Chart {number}", "problem": "no chart file for this specification"})
    for number in sorted(files.keys() - specified):
        rows.append({"chart": f"Chart {number}", "problem": "chart file has no specification in findings"})
    for number in sorted(specified & files.keys()):
        with files[number].open(encoding="utf-8") as stream:
            lines = [line for line, _ in zip(stream, range(2)) if line.strip()]
        if len(lines) < 2:
            rows.append({"chart": f"Chart {number}", "problem": "chart file has no data rows"})
    return rows


# ---------------------------------------------------------------- check-draft

def _structure_passed(report):
    return (not report["names_problems"] and not report["errors"] and report["findings"] == []
            and report["charts"] == [] and report["headings"] == [] and report["verify"] == [])


def check_draft(root, investigation, package, *, verify_only=False) -> dict:
    """Run every mechanical draft check; unless verify_only, rewrite the manifest's inventory."""
    root = Path(root)
    draft = _package_dir(root, investigation, package) / "draft"
    report = {"draft": _rel(root, draft), "names": 0, "names_problems": [], "findings": None,
              "charts": None, "headings": None, "inventory": None, "verify": None,
              "unmatched_flags": None, "errors": [], "passed": False}
    if not draft.is_dir():
        report["errors"].append(f"no draft at {report['draft']}; create it with awb-package")
        return report

    names, report["names_problems"] = project_names(root, investigation, package)
    report["names"] = len(names)
    findings_path = draft / "findings.md"
    try:
        report["findings"] = check_findings(findings_path, names=names)
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
        path = draft / MANIFEST
        if not path.is_file():
            raise ValueError(f"no manifest at {_rel(root, path)}; run export first")
        record = _read_json(path)
        if not verify_only:
            rows = inventory(draft)
            if rows != record.get("inventory"):
                record.update(inventory=rows, revised_at=_now())
                _write_json(path, record)
        elif not isinstance(record.get("inventory"), list):
            raise ValueError(f"{MANIFEST} records no inventory list; run check-draft without --verify-only")
        report["inventory"] = {"rows": len(record["inventory"]),
                               "source": "recorded" if verify_only else "rewritten"}
        report["verify"] = verify(draft, record["inventory"])
        if flags is not None:
            report["unmatched_flags"] = unmatched_flags(record, flags)
    except (OSError, ValueError) as error:
        report["errors"].append(f"manifest: {error}")

    report["passed"] = _structure_passed(report) and report["unmatched_flags"] == []
    return report


def _package_arguments(parser, *, package=True):
    parser.add_argument("investigation", help="investigation name under investigations/")
    if package:
        parser.add_argument("package", help="package name under deliveries/<investigation>/")


def cli_check_draft(root: Path, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="awb.py check-draft", formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Run every mechanical draft check (internal names in findings.md, chart files, "
                    "matching finding headings, the manifest inventory, and state.md's current flags) "
                    "and rewrite the manifest inventory, stamping revised_at when it changes; "
                    "--verify-only checks a release candidate and writes nothing.",
        epilog="Prints one JSON line.\nunmatched_flags lists each finding state.md flags whose exact finding "
               "and reason the manifest's revalidation_flags does not record.\nExit 0 only when "
               "names_problems, findings, charts, headings, verify, unmatched_flags, and errors are all empty.")
    _package_arguments(parser)
    parser.add_argument("--verify-only", action="store_true",
                        help="verify against the recorded inventory without rewriting it (the release gate)")
    args = parser.parse_args(argv)
    report = check_draft(Path(root), _simple(args.investigation, "investigation"),
                         _simple(args.package, "package"), verify_only=args.verify_only)
    _print(report)
    return 0 if report["passed"] else 1


# ---------------------------------------------------------------- producing and packaging state

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


# ---------------------------------------------------------------- export

_DISPLAY = "foundation/display.toml"


def display_names(root) -> dict:
    """Return {columns, values, round} from foundation/display.toml, empty when it is absent."""
    path = Path(root) / _DISPLAY
    try:
        record = _toml().loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    except ImportError as error:
        raise ImportError(f"reading {path.name} needs Python 3.11 or the tomli package") from error
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


def export(root, investigation, package, charts=(), datasets=(), results=(), *, no_datasets=False,
           rounding=None) -> dict:
    """Serialize recorded results into the draft and record the represented results' provenance.

    Any chart, dataset, or no_datasets makes a full export that replaces the chart set and the dataset
    selection; serialized results must pass compare_evidence. Results named only in `results` are
    represented without the check, and with no chart or dataset the exported files stay untouched.
    """
    root = Path(root)
    draft = _package_dir(root, investigation, package) / "draft"
    full = bool(charts or datasets or no_datasets)
    report = {"charts": [], "datasets": [], "written": False, "errors": []}
    if not draft.is_dir():
        report["errors"].append(f"no draft at {_rel(root, draft)}; create it with awb-package")
        return report
    path = draft / MANIFEST
    try:
        report["created"] = not path.exists()
        record = {} if report["created"] else _read_json(path)
        display = display_names(root) if full else None
    except (OSError, ValueError, ImportError) as error:
        report["errors"].append(str(error))
        return report

    shaped, sources = [], []
    if full:
        rounding = {**display["round"], **(rounding or {})}
        for kind, label, (result_id, columns) in (
                [("chart", f"chart-{i}", spec) for i, spec in enumerate(charts, 1)]
                + [("dataset", n, spec) for n, spec in datasets]):
            headers, rows, lines, problems = _shape(root, investigation, result_id, columns, display, rounding)
            report["errors"] += problems
            if not problems:
                shaped.append((kind, label, result_id, headers, rows))
                sources += [f"{label}: {line}" for line in lines]
    else:
        recorded = record.get("charts") if isinstance(record.get("charts"), list) else []
        report["errors"] += [f"{c.get('path')} serializes {c.get('result_id')}, which this call does not name; "
                             "pass it with --result" for c in recorded
                             if isinstance(c, dict) and c.get("result_id") not in results]
    if report["errors"]:
        return report

    serialized = list(dict.fromkeys(r for _, _, r, _, _ in shaped))
    represented = list(dict.fromkeys(serialized + list(results)))
    evidence, evidence_paths = {}, {}
    for result_id in represented:
        evidence_path = root / "investigations" / investigation / "evidence" / f"{result_id}.json"
        evidence_paths[result_id] = _rel(root, evidence_path)
        try:
            evidence[result_id] = _read_json(evidence_path)
            if evidence[result_id].get("schema") not in _EVIDENCE_SCHEMAS:
                raise ValueError("not an awb-evidence file")
        except (OSError, ValueError) as error:
            report["errors"].append(f"missing evidence: {evidence_paths[result_id]}: {error}")
    if report["errors"]:
        return report

    checks = {}
    if serialized:
        try:
            compare = _load_provenance(root).compare_evidence
        except (OSError, ImportError) as error:
            report["errors"].append(str(error))
            return report
        checks = {r: {"result_id": r, "evidence": evidence_paths[r], "comparisons": compare(root, evidence_paths[r])}
                  for r in serialized}
    failed = [{"result_id": c["result_id"], "name": i["name"], "detail": i["detail"]}
              for c in checks.values() for i in c["comparisons"] if i["outcome"] != "pass"]
    report["export_checks"] = {"results": len(checks), "failed": failed}
    if failed:
        report["exports_blocked"] = _BLOCKED
        return report

    if full:
        frames = [(r, headers, rows) for kind, _, r, headers, rows in shaped if kind == "chart"]
        try:
            paths = write_charts(draft / "charts", [(headers, rows) for _, headers, rows in frames])
        except ValueError as error:
            report["errors"].append(f"charts: {error}")
            return report
        report["charts"] = [{"path": _rel(draft, p), "result_id": r} for p, (r, _, _) in zip(paths, frames)]
        record["charts"] = report["charts"] or "none"
        directory = draft / "datasets"
        if directory.is_dir():
            for stale in directory.glob("*.csv"):
                stale.unlink()  # The selection is replaced whole, as write_charts replaces charts.
        for kind, label, result_id, headers, rows in shaped:
            if kind != "dataset":
                continue
            directory.mkdir(exist_ok=True)
            dataset = directory / f"{label}.csv"
            with dataset.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.writer(stream, lineterminator="\n")
                writer.writerow(headers)
                writer.writerows(rows)
            report["datasets"].append({"path": _rel(draft, dataset), "result_id": result_id})
        if directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()
        record["dataset_selection"] = [d["path"] for d in report["datasets"]] or "none"
        report["methodology_lines"] = sources

    if report["created"]:
        record.update(investigation=investigation, package=package, status="draft")
    # A represented result not serialized keeps its entry; entries outside the represented set drop.
    previous = record.get("export_checks") if isinstance(record.get("export_checks"), list) else []
    kept = {c.get("result_id"): c for c in previous if isinstance(c, dict)}
    entries = [checks.get(r) or kept.get(r) for r in represented]
    record["export_checks"] = [e for e in entries if e] or "none"
    fields = producing_state(evidence)
    fields["packaging_commit"], fields["packaging_uncommitted_changes"] = packaging_state(root)
    record.update(fields)
    _write_json(path, record)
    report["written"] = True
    commits, changes = fields["producing_commit"], fields["producing_uncommitted_changes"]
    report["results"] = represented
    report["producing_commit"] = "differs by result" if isinstance(commits, list) else commits
    report["producing_uncommitted_changes"] = len(changes) if isinstance(changes, list) else 0
    report["packaging_commit"] = fields["packaging_commit"]
    report["packaging_uncommitted_changes"] = fields["packaging_uncommitted_changes"]
    if (draft / "findings.md").is_file():
        report["check_charts"] = check_charts(draft / "findings.md", draft / "charts")
    return report


def cli_export(root: Path, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="awb.py export", formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Write the draft's chart and dataset files from saved result tables, renamed, mapped, "
                    "and rounded through foundation/display.toml, once compare_evidence passes for every "
                    "serialized result, and the manifest's producing and packaging state from the evidence "
                    "of every represented result. Creates the manifest when absent.",
        epilog="Prints one JSON line.\nAny --chart, --dataset, or --no-datasets replaces the whole chart set "
               "and dataset selection: no --chart records charts none. With only --result it records "
               "provenance and leaves exported files untouched.\nEvery exported column needs a display name "
               "in foundation/display.toml; gaps are listed together and nothing is written.\nWrites nothing "
               "when an evidence file is missing or any comparison fails (exports_blocked).\nExit 0 only "
               "when written and check_charts is empty.")
    _package_arguments(parser)
    parser.add_argument("--chart", action="append", default=[], metavar="RESULT[:COLUMNS]",
                        help="one per chart, in the order of the Chart N specifications; columns comma-separated")
    parser.add_argument("--dataset", action="append", default=[], metavar="NAME=RESULT[:COLUMNS]",
                        help="one per selected dataset; replaces the whole selection")
    parser.add_argument("--no-datasets", action="store_true", help="record an explicit selection of none")
    parser.add_argument("--result", action="append", default=[], metavar="RESULT",
                        help="a represented result not serialized here; its producing state is recorded "
                             "without the export check")
    parser.add_argument("--round", action="append", default=[], metavar="COLUMN=PLACES",
                        help="decimal places for a column, over foundation/display.toml [round]")
    args = parser.parse_args(argv)
    if args.dataset and args.no_datasets:
        parser.error("--dataset and --no-datasets exclude each other")
    if args.chart and not (args.dataset or args.no_datasets):
        parser.error("--chart replaces the whole export: name every --dataset, or --no-datasets")
    if not (args.chart or args.dataset or args.no_datasets or args.result):
        parser.error("name every represented result: --chart, --dataset or --no-datasets, and --result")
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
                    [_spec(c, "result-id") for c in args.chart], datasets,
                    [_simple(r, "result-id") for r in args.result], no_datasets=args.no_datasets,
                    rounding=rounding)
    _print(report)
    return 0 if report["written"] and not report.get("check_charts") else 1


# ---------------------------------------------------------------- release

def disposition_problems(record: dict) -> list[dict]:
    """List each represented flagged finding whose disposition does not allow release."""
    flags = record.get("revalidation_flags")
    if flags == "none" or flags == []:
        return []
    if not isinstance(flags, list):
        return [{"finding": None, "problem": "revalidation_flags is missing; record none or each flag"}]
    problems = []
    for flag in flags:
        flag = flag if isinstance(flag, dict) else {}
        places, disposition = flag.get("represented_in"), flag.get("disposition")
        if places == "none":
            continue  # A flagged finding the draft does not represent needs no disposition.
        if not isinstance(places, list) or not places or not all(
                isinstance(place, str) and place.strip() for place in places):
            problem = "represented_in is not a list of places; list them or record none"
        elif disposition in _DISPOSITIONS:
            continue
        else:
            problem = {None: "no disposition", "none": "no disposition",
                       "revalidate": "revalidation pending"}.get(disposition, f"unknown disposition {disposition!r}")
        problems.append({"finding": flag.get("finding"), "problem": problem})
    return problems


def release_dispositions(record: dict, prior) -> list[dict]:
    """Each represented flag's disposition, `new` unless the prior release recorded the same one.

    `prior` is the prior release's manifest, None when there is none, or False when it is unreadable
    (then `new` is None: unknown).
    """
    def key(flag):
        return flag.get("finding"), flag.get("reason"), flag.get("disposition")

    before = prior.get("revalidation_flags") if isinstance(prior, dict) else None
    before = {key(f) for f in before if isinstance(f, dict)} if isinstance(before, list) else set()
    rows = []
    for flag in record.get("revalidation_flags") if isinstance(record.get("revalidation_flags"), list) else []:
        if not isinstance(flag, dict) or not isinstance(flag.get("represented_in"), list):
            continue
        rows.append({"finding": flag.get("finding"), "reason": flag.get("reason"),
                     "represented_in": flag["represented_in"], "disposition": flag.get("disposition"),
                     "new": None if prior is False else key(flag) not in before})
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
        if key not in {"inventory", "export_checks", "revalidation_flags"}:
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


def release(root, investigation, package) -> dict:
    """Verify the draft, copy it to the next numbered release, stamp it, and copy it to storage."""
    root = Path(root)
    package_dir = _package_dir(root, investigation, package)
    check_report = check_draft(root, investigation, package, verify_only=True)
    report = {"released": False, "check": {"passed": check_report["passed"]}}
    if not _structure_passed(check_report):
        report["refused"] = "check-draft --verify-only does not pass"
        report["check"] = check_report
        return report
    record = _read_json(package_dir / "draft" / MANIFEST)
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
        prior_record = _read_json(prior / MANIFEST) if prior else None
    except (OSError, ValueError):
        prior_record = False
    target = released / number
    staging = released / f".{number}.{os.getpid()}.tmp"
    released.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copytree(package_dir / "draft", staging)
        record.update({"status": "release", "release_number": number, "released_at": _now(),
                       "prior_release": f"released/{prior.name}" if prior else "none"})
        _write_json(staging / MANIFEST, record)
        os.rename(staging, target)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    report.update(released=True, release=_rel(root, target), release_number=number,
                  released_at=record["released_at"], prior_release=record["prior_release"],
                  verify=verify(target, record["inventory"]),
                  datasets=record.get("dataset_selection", {"unknown": "dataset_selection is not recorded"}),
                  dispositions=release_dispositions(record, prior_record),
                  provenance_gaps=provenance_gaps(record),
                  checkout_only_acquisitions=checkout_only_acquisitions(root, record),
                  storage=_copy_to_storage(root, target, investigation, package, number))
    return report


def cli_release(root: Path, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="awb.py release", formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Copy a draft that passes check-draft --verify-only, with every flagged finding "
                    "recorded and disposed, to the next numbered release and to release storage.",
        epilog="Prints one JSON line.\nRefuses, creating nothing, unless check-draft --verify-only passes and "
               "every represented revalidation_flags entry is omit or release_with_caveat; a flag refusal "
               "lists unmatched_flags and dispositions.\nOn success it prints the report fields: datasets, "
               "dispositions (new: absent from the prior release's manifest), provenance_gaps, "
               "checkout_only_acquisitions, verify (the local copy), and storage.\nstorage.status is copied or "
               "already copied (empty compare_trees), mismatch or conflict (compare_trees rows), copy failed "
               "(problem), unreachable or unrecorded (instruction), or none chosen (warning).\nExit 1 on "
               "refusal, a verify row, or storage status mismatch, conflict, or copy failed.")
    _package_arguments(parser)
    args = parser.parse_args(argv)
    report = release(Path(root), _simple(args.investigation, "investigation"), _simple(args.package, "package"))
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
        report["releases"] += [{"release": _rel(root, p),
                                "storage": _copy_to_storage(root, p, investigation, directory.name, p.name)}
                               for p in numbers]
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
               "Exit 1 when no release exists or any storage status is mismatch, conflict, or copy failed.")
    _package_arguments(parser, package=False)
    parser.add_argument("package", nargs="?", help="package name under deliveries/<investigation>/ "
                                                   "(default: every package)")
    args = parser.parse_args(argv)
    report = copy_releases(Path(root), _simple(args.investigation, "investigation"),
                           _simple(args.package, "package") if args.package else None)
    _print(report)
    failed = report["errors"] or any(r["storage"]["status"] in _STORAGE_FAILURES for r in report["releases"])
    return 1 if failed else 0
