"""Result evidence for an analytics workbench (Python 3.10+, standard library).

Copy this file to `src/provenance.py` and import the project copy.

Schema awb-evidence/3, in order: schema, investigation, result_id, recorded_at
(local ISO time), producing_commit (SHA/uncommitted/unknown), producing_paths
(sorted), producing_uncommitted_changes (path/status/bytes/sha256), views
(path/bytes/sha256/publications), publications (path/publication_file/inputs/
conversion_commit/files), acquisitions (path/provenance_file/status/files),
settings (path/bytes/sha256/[result]/content), checks (name/outcome/detail), notes (text or null).
Unknowns are {"unknown": reason}.
Settings are scoped: the settings file must hold a [results.<id>] table for the result; settings
carries "result", content holds only [parameters] and that table (less its `finding` wording,
which is not a setting), and the settings file is left
out of producing_paths, so other results' tables and other top-level tables never make this
result stale. Producing paths are the investigation's code (run.py and other files outside its
records, queries/ and settings), the result's own queries, and src/ except the helpers that only
dispatch, record, or package (awb.py, provenance.py, packaging/), so a repair replacing those
stales nothing. compare_evidence also reads awb-evidence/1 and /2 files, and /3 files written
before scoping was required: those record whole-file settings, and /1 files carry a figure
entry, which it ignores.
Paths are project-relative POSIX, except that a files[].path copied from publication.json or
provenance.json is relative to the directory holding that file, and a publication's
inputs[].files[].path to its acquisition directory.
Data hashes are copied when recording and verified when comparing; TOML date/time
values use ISO strings in JSON, consistently during comparison.

record_evidence derives omitted publications from the views' data/parquet references and
omitted acquisitions from those publications' publication.json inputs. cli_stale backs
`python3 src/awb.py stale`, which compares every recorded result with the current state.

record_finding writes a recorded result's state.md findings row for run.py, and cli_state backs
`python3 src/awb.py state`, which shows and updates investigation state. Both keep the Markdown
records' shipped format, change only the lines they touch, and write history.md entries for
status and wording changes.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path


def file_checksums(paths: Iterable[str | os.PathLike], *,
                   root: str | os.PathLike | None = None) -> list[dict]:
    """Hash files in input order; missing files have null size and digest."""
    base = Path(root).resolve() if root is not None else None
    entries = []
    for path in paths:
        path = _relative(base, path) if base is not None else Path(path).as_posix()
        file = base / path if base is not None else Path(path)
        if file.is_dir():
            raise ValueError(f"directory is not a file: {path}")
        digest, size = hashlib.sha256(), 0
        try:
            with file.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
                    size += len(chunk)
            checksum = {"path": path, "bytes": size, "sha256": digest.hexdigest()}
        except FileNotFoundError:
            checksum = {"path": path, "bytes": None, "sha256": None}
        entries.append(checksum)
    return entries


def _checksum(root, path):
    return file_checksums([path], root=root)[0]


def _relative(root, path):
    # Lexical first so a symlink keeps its own path; resolved second for an aliased absolute root.
    for candidate in (Path(os.path.normpath(root / path)), (root / path).resolve()):
        if candidate.is_relative_to(root):
            return candidate.relative_to(root).as_posix()
    raise ValueError(f"path outside the project root: {path}")


def _git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode()


def _expand(root, paths):
    expanded = []
    for path in paths:
        path = _relative(root, path)
        if not (root / path).is_dir():
            expanded.append(path)
            continue
        try:
            files = _git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard",
                         "--", path).split("\0")
            expanded.extend(_relative(root, f) for f in files if f)
        except (OSError, subprocess.CalledProcessError):
            expanded.extend(_relative(root, f) for f in (root / path).rglob("*") if f.is_file())
    return expanded


def _view_publications(root, path):
    try:
        return sorted({f"data/parquet/{dataset}/{publication}" for dataset, publication in
                       re.findall(r"data/parquet/([^/\s'\"]+)/([^/\s'\"*]+)/", (root / path).read_text())})
    except (OSError, ValueError) as error:
        return {"unknown": f"{path}: {error}"}


_SCHEMAS = ("awb-evidence/1", "awb-evidence/2", "awb-evidence/3")
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
_DEFINES = re.compile(r"\bcreate\s+(?:or\s+replace\s+)?(?:temp(?:orary)?\s+)?(?:view|table)\s+"
                      r"(?:if\s+not\s+exists\s+)?((?:\"[^\"]+\"|\w+)(?:\.(?:\"[^\"]+\"|\w+))*)", re.I)


def _publication_acquisitions(root, publications):
    # landing.py records each input as {source, acquisition_id}: data/raw/<source>/<acquisition_id>.
    found = set()
    for publication in publications:
        try:
            content = json.loads((root / _relative(root, publication) / "publication.json").read_text())
            for item in content["inputs"]:
                names = (item["source"], item["acquisition_id"])
                if all(isinstance(n, str) and _ID.fullmatch(n) for n in names):
                    found.add(f"data/raw/{names[0]}/{names[1]}")
        except (OSError, ValueError, KeyError, TypeError):
            continue  # The publication's own record names the problem, and compare_evidence fails it.
    return sorted(found)


def _mentions(text, name):
    # A relation name follows FROM, JOIN, or a comma, optionally schema-qualified or quoted.
    pattern = rf"(?:\b(?:from|join)\s+|,\s*)(?:(?:\"[^\"]+\"|\w+)\.)*\"?{re.escape(name)}\"?(?![\w\"])"
    return re.search(pattern, text, re.I) is not None


def views_read(project_root, sql_paths: Iterable[str | os.PathLike], *,
               views_dir: str | os.PathLike = "foundation/views") -> list[str]:
    """Return the view files the SQL files read by name, plus the view files those read.

    A view file defines the names in its CREATE VIEW and CREATE TABLE statements. A name counts as
    read where FROM, JOIN, or a comma precedes it, case-insensitively, so a select-list column
    sharing a view's name after a comma also records that view: detection errs toward recording.
    """
    root = Path(project_root).resolve()
    files = {}
    for path in sorted((root / _relative(root, views_dir)).glob("*.sql")):
        text = path.read_text()
        files[_relative(root, path)] = (text, {m.split(".")[-1].strip('"') for m in _DEFINES.findall(text)})
    pending = [(root / _relative(root, path)).read_text() for path in sql_paths]
    found = set()
    while pending:
        text = pending.pop()
        for path, (view_text, names) in files.items():
            if path not in found and any(_mentions(text, name) for name in names):
                found.add(path)
                pending.append(view_text)
    return sorted(found)


def _input_record(root, path, filename, keys):
    path = _relative(root, path)
    entry = _checksum(root, f"{path}/{filename}")
    try:
        content = json.loads((root / entry["path"]).read_text())
        if not isinstance(content, dict):
            raise ValueError("expected a JSON object")
    except (OSError, ValueError) as error:
        content = {key: {"unknown": f"{entry['path']}: {error}"} for key in keys}
        entry.update(bytes=None, sha256=None)
    copied = {key: content.get(key, {"unknown": f"{entry['path']}: missing {key}"}) for key in keys}
    return {"path": path, filename.removesuffix(".json") + "_file": entry, **copied}


def _scoped(content, result_id):
    """The part of parsed settings one result reads: [parameters] and its own [results.<id>].

    The table's `finding` key is the first wording of the result's findings row, not a setting.
    """
    results = content.get("results")
    table = results.get(result_id) if isinstance(results, dict) else None
    if isinstance(table, dict):
        table = {key: value for key, value in table.items() if key != "finding"}
    return {**({"parameters": content["parameters"]} if "parameters" in content else {}),
            "results": {result_id: table}}


def _settings(root, path, result_id=None):
    """Checksum and parsed content of a settings file, scoped to result_id when it names one.

    With result_id, a file whose `results` table holds that ID is recorded with "result" and only
    what that result reads; any other layout is recorded whole.
    """
    entry = _checksum(root, path)
    try:
        import tomllib
    except ImportError:  # Python 3.10
        try:
            import tomli as tomllib
        except ImportError:
            tomllib = None
    if tomllib is None:
        entry["content"] = {"unknown": "tomllib unavailable; install tomli on Python 3.10"}
    else:
        try:
            content = tomllib.loads((root / entry["path"]).read_text())
            content = json.loads(json.dumps(content, default=lambda value: value.isoformat()))
        except (OSError, ValueError) as error:
            entry["content"] = {"unknown": str(error)}
        else:
            if result_id is not None and isinstance(content.get("results"), dict) \
                    and result_id in content["results"]:
                entry["result"] = result_id
                content = _scoped(content, result_id)
            entry["content"] = content
    return entry


def _settings_keys(content, result_id):
    """Top-level settings keys to compare, naming a scoped result's table results.<id>."""
    if result_id is None:
        return content
    return {**{k: v for k, v in content.items() if k != "results"},
            f"results.{result_id}": content.get("results", {}).get(result_id)}


# Investigation entries that are records or outputs, or that other results own, not producing code.
_NOT_CODE = {"brief.md", "state.md", "history.md", "evidence", "figures", "exploration", "results", "queries"}
# Helpers that dispatch, record evidence, or package; replacing them changes no result.
_NOT_PRODUCING = ("src/awb.py", "src/provenance.py", "src/packaging/")


def record_evidence(project_root, investigation: str, result_id: str, *, views: list[str],
                    publications: list[str] | None = None, acquisitions: list[str] | None = None,
                    settings_path: str, checks: list[dict], notes: str | None = None,
                    code_paths: list[str] | None = None) -> Path:
    """Write one result's complete producing state atomically, replacing the same id.

    The settings file must hold the result's [results.<id>] table; its `queries` (default
    queries/<id>.sql, relative to the investigation) are producing code. code_paths adds further
    producing files or directories. Omitted publications are those the views read; omitted
    acquisitions are the inputs recorded in those publications' publication.json.
    """
    root = Path(project_root).resolve()
    if not all(isinstance(v, str) and _ID.fullmatch(v) for v in (investigation, result_id)):
        raise ValueError("investigation and result_id must be simple identifiers")
    for check in checks:
        if (not isinstance(check, dict) or set(check) != {"name", "outcome", "detail"}
                or not all(isinstance(check[k], str) for k in check)
                or check["outcome"] not in {"pass", "fail", "not-applicable"}):
            raise ValueError("checks require name, outcome (pass/fail/not-applicable), and detail strings")
    settings = _settings(root, settings_path, result_id)
    if settings.get("result") != result_id:
        reason = settings["content"]["unknown"] if _is_unknown(settings["content"]) else "no such table"
        raise ValueError(f"{settings_path} must hold [results.{result_id}]: {reason}")
    table = settings["content"]["results"][result_id]
    queries = table.get("queries", [f"queries/{result_id}.sql"]) if isinstance(table, dict) else []
    prefix = f"investigations/{investigation}/"
    code = [p for p in _expand(root, [p for p in ("src", prefix) if (root / p).is_dir()])
            if not p.startswith(_NOT_PRODUCING)
            # figures/ is excluded for investigations laid out before awb-evidence/2.
            and not (p.startswith(prefix) and p[len(prefix):].split("/")[0] in _NOT_CODE)]
    code += _expand(root, [prefix + query for query in queries] + list(code_paths or []))
    view_entries = [{**e, "publications": _view_publications(root, e["path"])}
                    for e in file_checksums(views, root=root)]
    if publications is None:
        publications = sorted({p for e in view_entries if not _is_unknown(e["publications"])
                               for p in e["publications"]})
    if acquisitions is None:
        acquisitions = _publication_acquisitions(root, publications)
    # Scoped settings are compared by content alone, so other results' tables never count.
    paths = sorted(set(code + [_relative(root, p) for p in views]) - {settings["path"]})
    try:
        in_git = _git(root, "rev-parse", "--is-inside-work-tree").strip() == "true"
    except (OSError, subprocess.CalledProcessError, ValueError):
        in_git = False
    try:
        commit = _git(root, "rev-parse", "--verify", "HEAD").strip() if in_git else None
    except subprocess.CalledProcessError:
        commit = None
    if commit:
        changes = []
        prefix = _git(root, "rev-parse", "--show-prefix").strip()
        statuses = iter(_git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all",
                             "--ignored=matching", "--", *paths).split("\0") if paths else [])
        for entry in statuses:
            if not entry:
                continue
            status, path = entry[:2], entry[3:]
            if "R" in status or "C" in status:
                next(statuses, None)
            path = path.removeprefix(prefix)
            if path in paths:
                changes.append({"path": path, "status": status.strip(), **_checksum(root, path)})
    else:
        commit = "uncommitted" if in_git else {"unknown": "not a git repository"}
        changes = [{"path": e["path"], "status": "uncommitted" if in_git else "no-vcs", **e}
                   for e in file_checksums(paths, root=root)]
    evidence = {
        "schema": "awb-evidence/3", "investigation": investigation, "result_id": result_id,
        "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "producing_commit": commit, "producing_paths": paths, "producing_uncommitted_changes": changes,
        "views": view_entries,
        "publications": [_input_record(root, p, "publication.json", ["inputs", "conversion_commit", "files"])
                         for p in publications],
        "acquisitions": [_input_record(root, p, "provenance.json", ["status", "files"]) for p in acquisitions],
        "settings": settings,
        "checks": checks, "notes": notes,
    }
    path = root / _relative(root, f"investigations/{investigation}/evidence/{result_id}.json")
    if not path.parent.resolve().is_relative_to(root):
        raise ValueError(f"evidence directory resolves outside the project root: {path.parent}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        temporary.write_text(json.dumps(evidence, indent=2) + "\n")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
    return path


def _is_unknown(value):
    return isinstance(value, dict) and set(value) == {"unknown"}


def _known(value, *, deep=True):
    """Return value, raising ValueError with the reason when it, or a nested value, is unknown."""
    if _is_unknown(value):
        raise ValueError(value["unknown"])
    if deep and isinstance(value, (dict, list)):
        for item in value.values() if isinstance(value, dict) else value:
            _known(item)
    return value


def _file_diff(root, entry, keys=("sha256",), *, absent_ok=False):
    try:
        _known({k: entry[k] for k in ("path", *keys)})
        path = entry["path"]
        current = _checksum(root, path)
        problems = []
        for key in keys:
            if entry[key] is None and not absent_ok:
                problems.append(f"missing evidence: {path}: missing {key}")
            elif current[key] != entry[key]:
                problems.append(f"{path}: {key} differs" if current["sha256"] is not None else f"{path}: missing")
        return problems
    except (OSError, ValueError, KeyError, TypeError) as error:
        return [f"missing evidence: {entry.get('path', 'file')}: {error}"]


def compare_evidence(project_root, evidence_path) -> list[dict]:
    """Return the five export comparisons in order, with paths and one-sentence details."""
    root = Path(project_root).resolve()
    evidence_path = Path(evidence_path).as_posix()
    names = ("committed-code", "uncommitted-code", "views", "inputs", "settings")
    try:
        evidence_path = _relative(root, evidence_path)
        evidence = json.loads((root / evidence_path).read_text())
        if evidence["schema"] not in _SCHEMAS:
            raise ValueError("wrong schema")
    except (OSError, ValueError, KeyError, TypeError) as error:
        return [{"name": name, "paths": [evidence_path], "outcome": "fail",
                 "detail": f"missing evidence: {evidence_path}: {str(error).rstrip('.')}."} for name in names]
    comparisons = []
    for name in names:
        paths, mismatches = [], []
        try:
            if name == "committed-code":
                dirty = {_known(e["path"]) for e in _known(evidence["producing_uncommitted_changes"], deep=False)}
                paths = [p for p in _known(evidence["producing_paths"]) if p not in dirty]
                sha = evidence["producing_commit"]
                if paths and sha != "uncommitted":
                    _known(sha)
                    try:
                        _git(root, "cat-file", "-e", f"{sha}^{{commit}}")
                    except subprocess.CalledProcessError:
                        mismatches = [f"producing commit {sha} is not in this repository"]
                    else:
                        changed = _git(root, "diff", "--name-only", "-z", "--relative", sha, "--", *paths)
                        mismatches = [f"{p}: differs from producing commit" for p in changed.split("\0") if p]
            elif name == "uncommitted-code":
                paths = [e["path"] for e in _known(evidence["producing_uncommitted_changes"], deep=False)]
                for entry in evidence["producing_uncommitted_changes"]:
                    mismatches.extend(_file_diff(root, entry, ("bytes", "sha256"), absent_ok=True))
            elif name == "views":
                paths = [e["path"] for e in _known(evidence["views"], deep=False)]
                publications = ({_known(e["path"]) for e in _known(evidence["publications"], deep=False)}
                                if paths else set())
                for entry in evidence["views"]:
                    path = entry["path"]
                    mismatches.extend(_file_diff(root, entry))
                    try:
                        _known(entry["publications"])
                    except (ValueError, KeyError) as error:
                        mismatches.append(f"missing evidence: {path}: {error}")
                        continue
                    references = _view_publications(root, path)
                    if _is_unknown(references):
                        # A deleted view is already reported missing by _file_diff.
                        if (root / path).exists():
                            mismatches.append(f"{path}: unreadable ({references['unknown']})")
                        continue
                    if references != entry["publications"]:
                        mismatches.append(f"{path}: publications differ")
                    mismatches.extend(f"{path}: publication {p} has no recorded publication"
                                      for p in references if p not in publications)
            elif name == "inputs":
                inputs = _known(evidence["publications"], deep=False) + _known(evidence["acquisitions"], deep=False)
                paths = [e["path"] for e in inputs]
                for entry in inputs:
                    directory = entry["path"]
                    try:
                        metadata = _known(entry.get("publication_file", entry.get("provenance_file")), deep=False)
                        directory = Path(metadata["path"]).parent
                        paths.append(metadata["path"])
                        mismatches.extend(_file_diff(root, metadata))
                    except (ValueError, KeyError, TypeError) as error:
                        mismatches.append(f"missing evidence: {entry['path']}: {error}")
                    try:
                        for file in _known(entry["files"], deep=False):
                            path = _relative(root, Path(directory) / file["path"])
                            paths.append(path)
                            mismatches.extend(_file_diff(root, {**file, "path": path}, ("bytes", "sha256")))
                    except (ValueError, KeyError, TypeError) as error:
                        mismatches.append(f"missing evidence: {entry['path']}: {error}")
            else:
                entry = evidence["settings"]
                _known({k: v for k, v in entry.items() if k != "content"})
                paths = [entry["path"]]
                scope = entry.get("result")
                current = _settings(root, entry["path"])
                old, new = entry["content"], current["content"]
                if not _is_unknown(old) and not _is_unknown(new):
                    if scope is not None:
                        old, new = _settings_keys(old, scope), _settings_keys(_scoped(new, scope), scope)
                    keys = sorted(k for k in old.keys() | new.keys()
                                  if k not in old or k not in new or old[k] != new[k])
                    if keys:
                        mismatches.append(f"{entry['path']}: settings differ for keys {', '.join(keys)}")
                else:
                    mismatches.extend(_file_diff(root, entry))
        except (OSError, ValueError, KeyError, TypeError, AttributeError, subprocess.CalledProcessError) as error:
            mismatches.append(f"missing evidence: {evidence_path}: {str(error).rstrip('.')}")
        if mismatches:
            prefix = "missing evidence: " if any(m.startswith("missing evidence:") for m in mismatches) else ""
            text = "; ".join(m.rstrip(".") for m in mismatches) + "."
            detail = text if text.startswith(prefix) else prefix + text
        elif name == "committed-code" and evidence["producing_commit"] == "uncommitted":
            detail = "no producing commit; producing files compared under uncommitted-code"
        else:
            detail = "current state matches recorded evidence." if paths else "nothing to compare."
        comparisons.append({"name": name, "paths": paths,
                            "outcome": "fail" if mismatches else "pass", "detail": detail})
    return comparisons


_EVIDENCE_LINK = re.compile(r"\]\((?:\./)?evidence/([A-Za-z0-9][A-Za-z0-9._-]*)\.json\)")


def finding_rows(state_path: str | os.PathLike) -> dict[str, list[str]]:
    """Map each result ID to the state.md table rows, as text, that link its evidence file."""
    rows = {}
    try:
        lines = Path(state_path).read_text().splitlines()
    except OSError:
        return rows
    for line in lines:
        if line.lstrip().startswith("|"):
            for result_id in dict.fromkeys(_EVIDENCE_LINK.findall(line)):
                rows.setdefault(result_id, []).append(line.strip())
    return rows


def _cell(text):
    return " ".join(str(text).split()).replace("|", r"\|")


# Caveat segments that run.py writes from the checks; any other segment is a note an agent added.
_CHECK_LABELS = ("failed checks: ", "not assessed: ")


def _check_caveat(checks):
    failed = [c["name"] for c in checks if c["outcome"] == "fail"]
    unassessed = [c["name"] for c in checks if c["outcome"] == "not-applicable" and c["detail"] == "not assessed"]
    return "; ".join(f"{label}{', '.join(names)}" for label, names in zip(_CHECK_LABELS, (failed, unassessed))
                     if names)


def finding_row(project_root, investigation: str, result_id: str, checks: list[dict], *,
                finding: str | None = None, status: str = "provisional") -> str:
    """Return the state.md Current findings row for a recorded result, without writing it.

    The Finding cell keeps the text of a row already linking this result's evidence, else uses
    `finding`, else a placeholder to replace. The caveat names failed and not-assessed checks.
    record_finding writes the row; this stays for run.py copies that print it.
    """
    existing = finding_rows(Path(project_root) / "investigations" / investigation / "state.md")
    if result_id in existing:
        # Split on unescaped pipes; the first cell is the finding text, already escaped.
        text = re.split(r"(?<!\\)\|", existing[result_id][0])[1].strip()
    else:
        text = _cell(finding or f"<state the finding from {result_id}>")
    return f"| {text} | [{result_id}](evidence/{result_id}.json) | {_cell(status)} | {_cell(_check_caveat(checks))} |"


# Investigation state: state.md, history.md, and README's Active investigation line.
# Every write rewrites only the lines it changes and replaces the file atomically; a missing or
# malformed record raises StateError before anything is written.

class StateError(ValueError):
    """A record is missing or not in the shipped format; nothing was written."""


_COLUMNS = ["Finding", "Evidence", "Status", "Revalidation reason or caveat"]
_STATUSES = ("provisional", "supported", "superseded")
_FLAGGED = "revalidation-needed"
_ITEM = re.compile(r"([-*+]|(\d+)([.)]))[ \t]+(.*)")
# Opening words of the shipped templates' guidance, shown as "not recorded" or left out of lists.
_GUIDANCE = ("State the question this investigation will answer", "Record the decision this analysis will support",
             "Record who will read the", "List open analytical questions", "List the smallest concrete steps")


def _read(path, label):
    try:
        with open(path, encoding="utf-8", newline="") as stream:
            text = stream.read()
    except FileNotFoundError:
        raise StateError(f"{label} does not exist") from None
    except (OSError, UnicodeError) as error:
        raise StateError(f"{label} is unreadable: {error}") from None
    lines = [line + "\n" for line in text.split("\n")]
    lines[-1] = lines[-1][:-1]
    return lines if lines[-1] else lines[:-1]


def _write(path, lines):
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with open(temporary, "w", encoding="utf-8", newline="") as stream:
            stream.write("".join(lines))
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _bare(line):
    return line.rstrip("\r\n")


def _cells(line):
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", _bare(line).strip().strip("|"))]


def _row(cells):
    return "|" + "|".join(f" {cell} " if cell else " " for cell in cells) + "|"


def _unescape(cell):
    return cell.replace(r"\|", "|")


class _Record:
    """A Markdown record's lines, edited in place so untouched lines keep their bytes."""

    def __init__(self, path, label):
        self.path, self.label = path, label
        self.lines = _read(path, label)
        self.newline = "\r\n" if self.lines and self.lines[0].endswith("\r\n") else "\n"

    def section(self, title):
        """Return (heading index, end index) of the one `## title` section."""
        found = [i for i, line in enumerate(self.lines) if re.fullmatch(rf"## {re.escape(title)}\s*", _bare(line))]
        if len(found) != 1:
            raise StateError(f"{self.label}: {'no' if not found else 'repeated'} '## {title}' section")
        end = next((i for i in range(found[0] + 1, len(self.lines)) if re.match(r"#{1,2} ", self.lines[i])),
                   len(self.lines))
        return found[0], end

    def insert(self, index, new_lines):
        if index and not self.lines[index - 1].endswith("\n"):
            self.lines[index - 1] += self.newline
        self.lines[index:index] = [line + self.newline for line in new_lines]

    def text(self, title):
        """First content line of a section, without template guidance; None when absent."""
        start, end = self.section(title)
        for line in self.lines[start + 1:end]:
            line = _bare(line).strip()
            if line and not re.fullmatch(r"<!--.*-->", line):
                return None if line.startswith(_GUIDANCE) else line
        return None


class _State(_Record):
    def __init__(self, root, investigation):
        super().__init__(root / "investigations" / investigation / "state.md",
                         f"investigations/{investigation}/state.md")
        updated = [i for i, line in enumerate(self.lines) if line.startswith("Last updated:")]
        if len(updated) != 1:
            raise StateError(f"{self.label}: {'no' if not updated else 'repeated'} 'Last updated:' line")
        self.updated = updated[0]
        self.section("Unresolved issues"), self.section("Next steps")  # the shipped layout, checked before any write
        start, end = self.section("Current findings")
        header = next((i for i in range(start + 1, end) if self.lines[i].lstrip().startswith("|")), None)
        if header is None or header + 1 >= end or _cells(self.lines[header]) != _COLUMNS \
                or not all(re.fullmatch(r":?-+:?", c) for c in _cells(self.lines[header + 1])):
            raise StateError(f"{self.label}: Current findings needs a table with columns {' | '.join(_COLUMNS)}")
        self.rows_start = self.rows_end = header + 2
        while self.rows_end < end and self.lines[self.rows_end].lstrip().startswith("|"):
            if len(_cells(self.lines[self.rows_end])) != len(_COLUMNS):
                raise StateError(f"{self.label}: findings row {self.rows_end + 1} does not have four cells")
            self.rows_end += 1

    def rows(self):
        return [(i, _cells(self.lines[i])) for i in range(self.rows_start, self.rows_end)]

    def row_for(self, result_id):
        """The one row whose Evidence cell links this result's evidence file, or None."""
        found = [(i, cells) for i, cells in self.rows() if result_id in _EVIDENCE_LINK.findall(cells[1])]
        if len(found) > 1:
            raise StateError(f"{self.label}: {len(found)} findings rows link {result_id}")
        return found[0] if found else None

    def set_row(self, index, cells):
        ending = self.lines[index][len(_bare(self.lines[index])):] or self.newline
        self.lines[index] = _row(cells) + ending

    def add_row(self, cells):
        self.insert(self.rows_end, [_row(cells)])
        self.rows_end += 1

    def touch(self, today):
        line = self.lines[self.updated]
        self.lines[self.updated] = f"Last updated: {today}" + line[len(_bare(line)):]

    def items(self, title):
        """The list items of a section as (first line, end line, text), and its other lines."""
        start, end = self.section(title)
        items, notes, i = [], [], start + 1
        while i < end:
            line = _bare(self.lines[i])
            match = _ITEM.fullmatch(line)
            if match:
                j, parts = i + 1, [match[4].strip()]
                while j < end and self.lines[j].strip() and self.lines[j][0] in " \t":
                    parts.append(self.lines[j].strip())
                    j += 1
                items.append((i, j, " ".join(parts)))
                i = j
                continue
            line = line.strip()
            if line and not line.startswith(_GUIDANCE) and not re.fullmatch(r"<!--.*-->", line):
                notes.append(line)
            i += 1
        return items, notes

    def add_item(self, title, text):
        start, end = self.section(title)
        items, _ = self.items(title)
        if items:
            match = _ITEM.fullmatch(_bare(self.lines[items[-1][0]]))
            marker = f"{int(match[2]) + 1}{match[3]}" if match[2] else match[1]
            self.insert(items[-1][1], [f"{marker} {text}"])
        else:
            last = max((i for i in range(start, end) if self.lines[i].strip()), default=start)
            self.insert(last + 1, ["", f"- {text}"])

    def remove_item(self, first, stop):
        del self.lines[first:stop]
        # Drop the blank line left doubled, so removing the only bullet undoes adding it.
        if first and not self.lines[first - 1].strip() and (first >= len(self.lines) or not self.lines[first].strip()):
            del self.lines[first - 1]


def _pointer(value):
    """Parse an Active investigation value: (slug or 'none', rewrite function), or None if customized."""
    value = value.strip()
    match = re.fullmatch(r"\[[^\]]*\]\((\./)?investigations/([A-Za-z0-9][A-Za-z0-9._-]*)/state\.md\)", value)
    if match:
        return match[2], lambda new: f"[{new}]({match[1] or ''}investigations/{new}/state.md)"
    match = re.fullmatch(r"(`?)(\./)?investigations/([A-Za-z0-9][A-Za-z0-9._-]*)/state\.md\1", value)
    if match:
        return match[3], lambda new: f"{match[1]}{match[2] or ''}investigations/{new}/state.md{match[1]}"
    if value == "none":
        return value, lambda new: f"[{new}](investigations/{new}/state.md)"
    if _ID.fullmatch(value):
        return value, lambda new: new
    return None


def _readme_pointer(root):
    readme = _Record(root / "README.md", "README.md")
    found = [i for i, line in enumerate(readme.lines) if line.startswith("Active investigation:")]
    if len(found) != 1:
        raise StateError(f"README.md: {'no' if not found else 'repeated'} 'Active investigation:' line")
    value = _bare(readme.lines[found[0]])[len("Active investigation:"):]
    parsed = _pointer(value)
    if parsed is None:
        raise StateError(f"README.md: customized Active investigation line ({value.strip()}); edit it by hand")
    return readme, found[0], parsed


def _active(root):
    """README's active investigation; StateError when it names none or a missing directory."""
    _, _, (name, _) = _readme_pointer(root)
    if name == "none":
        raise StateError("README.md names no active investigation; run `awb.py state switch <name>`")
    if not (root / "investigations" / name).is_dir():
        raise StateError(f"README.md names {name}, which has no directory under investigations/")
    return name


def evidence_commit(project_root, investigation: str, result_id: str) -> str:
    """The commit holding a result's current evidence file: HEAD when it is committed and unchanged.

    Otherwise `uncommitted`, followed by `; last committed at <sha>` when an earlier version is
    committed, as after a rerun that replaced committed evidence.
    """
    root = Path(project_root).resolve()
    path = f"investigations/{investigation}/evidence/{result_id}.json"
    try:
        _git(root, "ls-files", "--error-unmatch", "--", path)
        _git(root, "diff", "--quiet", "HEAD", "--", path)
        return _git(root, "rev-parse", "--verify", "HEAD").strip()
    except (OSError, subprocess.CalledProcessError):
        pass
    try:
        last = _git(root, "log", "-1", "--format=%H", "--", path).strip()
    except (OSError, subprocess.CalledProcessError):
        last = ""
    return f"uncommitted; last committed at {last}" if last else "uncommitted"


def _history_entry(today, title, result_id, now, was, reason, caveat, commit):
    (text, status), (old_text, old_status) = now, was
    return ["", f"### {today} — {title}", "",
            f"- **Change or finding:** \"{_unescape(text)}\" ({status}).",
            f"- **Evidence:** [{result_id}](evidence/{result_id}.json); prior evidence "
            + (f"{commit}." if commit.startswith("uncommitted") else f"at commit {commit}."),
            f"- **Reasoning or decision:** {' '.join(reason.split()) if reason else 'not given.'}",
            f"- **Impact and caveats:** {_unescape(caveat) or 'none.'}",
            f"- **Supersedes or revalidation link:** supersedes \"{_unescape(old_text)}\" ({old_status})."]


def _append_history(root, investigation, entry):
    history = _Record(root / "investigations" / investigation / "history.md",
                      f"investigations/{investigation}/history.md")
    history.insert(len(history.lines), entry)
    return history


def record_finding(project_root, investigation: str, result_id: str, checks: list[dict], *,
                   finding: str | None = None, prior_commit: str = "uncommitted", today: str | None = None) -> dict:
    """Write a recorded result's state.md findings row, matched by its evidence link.

    A new result gets a provisional row with `finding` or a placeholder. An existing row keeps its
    wording and status and gets the checks' caveat, keeping caveat notes an agent added. A flagged
    row becomes provisional, and history.md records the cleared flag, citing prior_commit, the
    commit holding the evidence before this rerun (evidence_commit, taken before it changed).
    Sets Last updated. Returns {action: added|refreshed|flag cleared, status, row}.
    """
    root = Path(project_root).resolve()
    today = today or datetime.now().date().isoformat()
    state = _State(root, investigation)
    caveat, link = _cell(_check_caveat(checks)), f"[{result_id}](evidence/{result_id}.json)"
    found, history = state.row_for(result_id), None
    if found is None:
        cells = [_cell(finding or f"<state the finding from {result_id}>"), link, "provisional", caveat]
        state.add_row(cells)
        action = "added"
    else:
        index, old = found
        if old[2].startswith(_FLAGGED):
            cells, action = [old[0], old[1], "provisional", caveat], "flag cleared"
            history = _append_history(root, investigation, _history_entry(
                today, f"{result_id} rerun clears its flag", result_id, (old[0], "provisional"),
                (old[0], old[2]), "rerun for the flag" + (f": {_unescape(old[3])}" if old[3] else "") + ".",
                caveat, prior_commit))
        else:
            notes = [s for s in old[3].split("; ") if s and not s.startswith(_CHECK_LABELS)]
            cells, action = [old[0], old[1], old[2], "; ".join(([caveat] if caveat else []) + notes)], "refreshed"
        state.set_row(index, cells)
    state.touch(today)
    if history is not None:
        _write(history.path, history.lines)
    _write(state.path, state.lines)
    return {"action": action, "status": cells[2], "row": _row(cells)}


def update_finding(project_root, investigation: str, result_id: str, *, status: str | None = None,
                   text: str | None = None, caveat: str | None = None, reason: str | None = None,
                   today: str | None = None) -> dict:
    """Change a findings row's status, wording, or caveat note; history.md records a status or wording change.

    The history entry cites the commit holding the current evidence file (evidence_commit). A
    flagged row can be superseded or reworded but not promoted: rerun it with run.py. Returns
    {changed, row, history (the entry's heading, or None)}.
    """
    root = Path(project_root).resolve()
    today = today or datetime.now().date().isoformat()
    if status is not None and status not in _STATUSES:
        raise ValueError(f"status must be one of {', '.join(_STATUSES)}")
    if text is not None and not text.strip():
        raise ValueError("the finding text is empty")
    state = _State(root, investigation)
    found = state.row_for(result_id)
    if found is None:
        raise StateError(f"{state.label}: no findings row links {result_id}; record it with run.py first")
    index, old = found
    flagged = old[2].startswith(_FLAGGED)
    if flagged and status in ("provisional", "supported"):
        raise StateError(f"{result_id} is flagged ({old[2]}); rerun it with run.py before promoting it")
    if flagged and caveat is not None:
        raise StateError(f"{result_id} is flagged; its caveat holds the flag reason, which stays until a rerun")
    cells = list(old)
    if text is not None:
        cells[0] = _cell(text)
    if status is not None:
        cells[2] = status
    if caveat is not None:
        generated = [s for s in old[3].split("; ") if s.startswith(_CHECK_LABELS)]
        cells[3] = "; ".join(generated + ([_cell(caveat)] if caveat.strip() else []))
    if cells == old:
        return {"changed": False, "row": _bare(state.lines[index]).strip(), "history": None}
    history = heading = None
    if cells[:3] != old[:3]:
        changes = (["reworded"] if cells[0] != old[0] else []) + (
            [f"{'promoted' if status == 'supported' else 'set'} to {status}"] if cells[2] != old[2] else [])
        entry = _history_entry(today, f"{result_id} {' and '.join(changes)}", result_id, (cells[0], cells[2]),
                               (old[0], old[2]), reason, cells[3], evidence_commit(root, investigation, result_id))
        history, heading = _append_history(root, investigation, entry), entry[1]
    state.set_row(index, cells)
    state.touch(today)
    if history is not None:
        _write(history.path, history.lines)
    _write(state.path, state.lines)
    return {"changed": True, "row": _row(cells), "history": heading}


def _brief_line(root, investigation, title):
    try:
        line = _Record(root / "investigations" / investigation / "brief.md", "brief.md").text(title)
    except StateError as error:
        return f"({error})"
    if line is None:
        return "not recorded"
    return line if len(line) <= 160 else line[:159].rstrip() + "…"


def state_view(project_root, investigation: str) -> str:
    """The compact resume view: brief lines, findings rows and counts, open lists, and Last updated."""
    root = Path(project_root).resolve()
    state = _State(root, investigation)
    rows = state.rows()
    counts = {}
    for _, cells in rows:
        status = _FLAGGED if cells[2].startswith(_FLAGGED) else cells[2] or "blank"
        counts[status] = counts.get(status, 0) + 1
    updated = _bare(state.lines[state.updated])[len("Last updated:"):].strip()
    out = [f"{investigation} (Last updated: {updated or 'blank'})"]
    out += [f"{label}: {_brief_line(root, investigation, title)}" for label, title in
            (("Question", "Business question"), ("Purpose", "Purpose"), ("Audience", "Audience"))]
    out.append("Findings: " + (", ".join(f"{n} {s}" for s, n in counts.items()) or "none"))
    out += [_bare(state.lines[i]).strip() for i, _ in rows]
    number = 0
    for title in ("Unresolved issues", "Next steps"):
        items, notes = state.items(title)
        out.append(f"{title}:" + ("" if items or notes else " none"))
        for _, _, text in items:
            number += 1
            out.append(f"{number}. {text}")
        out += [f"   {note}" for note in notes]
    return "\n".join(out)


def _open_items(state):
    """Unresolved issues then Next steps, numbered together as state_view shows them."""
    return [(title, *item) for title in ("Unresolved issues", "Next steps") for item in state.items(title)[0]]


def add_item(project_root, investigation: str, title: str, text: str, *, today: str | None = None) -> int:
    """Add one bullet to Unresolved issues or Next steps; return its number in state_view."""
    root = Path(project_root).resolve()
    text = " ".join(text.split())
    if not text:
        raise ValueError("the text is empty")
    state = _State(root, investigation)
    state.add_item(title, text)
    state.touch(today or datetime.now().date().isoformat())
    number = [i for i, (t, *_rest) in enumerate(_open_items(state), 1) if t == title][-1]
    _write(state.path, state.lines)
    return number


def remove_item(project_root, investigation: str, which: str, *, today: str | None = None) -> tuple[str, str]:
    """Remove the Unresolved issues or Next steps bullet numbered `which`, or the one bullet whose
    text contains it (case-insensitively; an exact match wins). Returns (section, text)."""
    root = Path(project_root).resolve()
    state = _State(root, investigation)
    items = _open_items(state)
    if which.strip().isdigit():
        number = int(which)
        if not 1 <= number <= len(items):
            raise StateError(f"no open item {number}; there are {len(items)}")
        chosen = [items[number - 1]]
    else:
        wanted = " ".join(which.split()).casefold()
        chosen = [item for item in items if item[3].casefold() == wanted] or \
                 [item for item in items if wanted and wanted in item[3].casefold()]
        if len(chosen) != 1:
            if not chosen:
                raise StateError(f"no open item contains {which!r}")
            numbers = [str(items.index(item) + 1) for item in chosen]
            raise StateError(f"{which!r} matches items {', '.join(numbers)}; pass the number")
    title, first, stop, text = chosen[0]
    state.remove_item(first, stop)
    state.touch(today or datetime.now().date().isoformat())
    _write(state.path, state.lines)
    return title, text


def switch_active(project_root, investigation: str) -> bool:
    """Point README's Active investigation line at an investigation, keeping its link form.

    The investigation's state.md must parse. Returns whether the line changed.
    """
    root = Path(project_root).resolve()
    _State(root, investigation)
    readme, index, (current, rewrite) = _readme_pointer(root)
    if current == investigation:
        return False
    line = _bare(readme.lines[index])
    value = line[len("Active investigation:"):]
    spacing = value[:len(value) - len(value.lstrip())] or " "
    readme.lines[index] = f"Active investigation:{spacing}{rewrite(investigation)}" + readme.lines[index][len(line):]
    _write(readme.path, readme.lines)
    return True


_STATE_EXIT = "Exit status: 0 done; 1 a record is missing or malformed, or nothing matched (one line on stderr, " \
              "nothing written); 2 unusable arguments or an unknown investigation."


def cli_state(root: Path, argv: list[str]) -> int:
    """Show or update the active investigation's state.md, history.md, and README pointer."""
    root = Path(root).resolve()
    actions = {
        "finding": "change a finding's status or wording; history.md records the prior ones",
        "issue": "add a bullet to Unresolved issues",
        "next": "add a bullet to Next steps",
        "done": "remove an Unresolved issues or Next steps bullet by number or text",
        "switch": "point README's Active investigation line at another investigation and show it",
    }
    action = argv[0] if argv and argv[0] in actions else None
    parser = argparse.ArgumentParser(
        prog="awb.py state" + (f" {action}" if action else ""),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=actions[action] if action else
        "Show the active investigation (README's Active investigation line): its brief's question, purpose, "
        "and audience, findings rows with counts by status, Unresolved issues and Next steps numbered "
        "together, and Last updated. run.py writes findings rows itself.",
        epilog=("Writes change only the affected lines and set state.md's Last updated to today.\n"
                if action and action != "switch" else "Rewrites only README's Active investigation line, "
                "keeping its link form; the investigation's state.md must parse.\n" if action else "") +
        ("subcommands:\n" + "\n".join(f"  {name:<8} {summary}" for name, summary in actions.items()) +
         "\nRun `awb.py state <subcommand> --help` for its arguments.\n" if not action else "") + _STATE_EXIT)
    if action != "switch":
        parser.add_argument("--investigation", metavar="NAME",
                            help="act on this investigation instead of the active one")
    if action == "finding":
        parser.add_argument("result_id", help="the result ID its Evidence cell links")
        parser.add_argument("--status", choices=_STATUSES, help="new status")
        parser.add_argument("--text", help="new finding wording")
        parser.add_argument("--caveat", help="replace the caveat's notes; the checks' caveat run.py writes stays "
                                             "('' clears the notes)")
        parser.add_argument("--reason", help="why, for the history entry a status or wording change writes")
    elif action in ("issue", "next"):
        parser.add_argument("text", help="the bullet's text")
    elif action == "done":
        parser.add_argument("item", metavar="number-or-text",
                            help="the number `awb.py state` shows, or text only one bullet contains")
    elif action == "switch":
        parser.add_argument("investigation", help="directory name under investigations/")
    try:
        args = parser.parse_args(argv[1:] if action else argv)
    except SystemExit as stop:
        return stop.code
    if action == "finding" and args.status is None and args.text is None and args.caveat is None:
        parser.print_usage(sys.stderr)
        print("awb.py state finding: give --status, --text, or --caveat", file=sys.stderr)
        return 2
    name = args.investigation
    if name is not None and not (_ID.fullmatch(name) and (root / "investigations" / name).is_dir()):
        print(f"awb.py state: no investigation named {name!r} under investigations/", file=sys.stderr)
        return 2
    try:
        name = name or _active(root)
        if action is None:
            print(state_view(root, name))
        elif action == "switch":
            changed = switch_active(root, name)
            print(("Active investigation now " if changed else "Already active: ") + state_view(root, name))
        elif action == "finding":
            result = update_finding(root, name, args.result_id, status=args.status, text=args.text,
                                    caveat=args.caveat, reason=args.reason)
            print(result["row"] if result["changed"] else f"unchanged: {result['row']}")
            if result["history"]:
                print(f"history.md: {result['history']}")
        elif action in ("issue", "next"):
            title = "Unresolved issues" if action == "issue" else "Next steps"
            number = add_item(root, name, title, args.text)
            print(f"added {title} item {number}")
        else:
            title, text = remove_item(root, name, args.item)
            print(f"removed from {title}: {text}")
    except StateError as error:
        print(f"awb.py state: {error}", file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"awb.py state: {error}", file=sys.stderr)
        return 2
    return 0


def _short(detail, limit=3):
    parts = detail.rstrip(".").split("; ")
    more = f"; +{len(parts) - limit} more" if len(parts) > limit else ""
    return "; ".join(parts[:limit]) + more + "."


def cli_stale(root: Path, argv: list[str]) -> int:
    """Print, as compact JSON, each recorded result whose evidence no longer matches the project."""
    parser = argparse.ArgumentParser(
        prog="awb.py stale",
        description="Compare investigations' evidence files with the current code, views, inputs, and "
                    "settings; changes nothing.",
        epilog="Prints one JSON line: checked, stale, skipped (JSON in an evidence directory that is not "
               "evidence), and results, one entry per result with a failing comparison: investigation, "
               "result_id, evidence, failed [{name, detail}], and findings, the exact state.md rows to "
               "flag. A finding whose linked evidence file is missing is listed too. Exit 0 whether or "
               "not anything is stale; 2 for an unknown investigation.")
    parser.add_argument("--investigation", metavar="NAME",
                        help="check only this investigation, by its directory name under investigations/")
    args = parser.parse_args(argv)
    root = Path(root).resolve()
    base = root / "investigations"
    if args.investigation is not None:
        if not _ID.fullmatch(args.investigation) or not (base / args.investigation).is_dir():
            print(f"no investigation named {args.investigation!r} under investigations/", file=sys.stderr)
            return 2
        directories = [base / args.investigation]
    else:
        directories = sorted(p for p in base.iterdir() if p.is_dir()) if base.is_dir() else []
    results, checked, skipped = [], 0, []
    for directory in directories:
        rows = finding_rows(directory / "state.md")
        # Evidence files on disk, plus any a finding links that is missing.
        ids = {p.stem for p in (directory / "evidence").glob("*.json") if _ID.fullmatch(p.stem)}
        for result_id in sorted(ids | set(rows)):
            evidence = f"investigations/{directory.name}/evidence/{result_id}.json"
            try:
                content = json.loads((root / evidence).read_text())
                if not (isinstance(content, dict) and str(content.get("schema", "")).startswith("awb-evidence/")):
                    skipped.append(evidence)  # Another record kept beside the evidence, such as saved export checks.
                    continue
            except (OSError, ValueError):
                pass  # compare_evidence reports missing or unreadable evidence.
            checked += 1
            failed = [{"name": c["name"], "detail": _short(c["detail"])}
                      for c in compare_evidence(root, evidence) if c["outcome"] == "fail"]
            if failed:
                results.append({"investigation": directory.name, "result_id": result_id, "evidence": evidence,
                                "failed": failed, "findings": rows.get(result_id, [])})
    print(json.dumps({"checked": checked, "stale": len(results), "skipped": skipped, "results": results}))
    return 0
