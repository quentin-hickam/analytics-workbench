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
carries "result", content holds only [parameters] and that table, and the settings file is left
out of producing_paths, so other results' tables and other top-level tables never make this
result stale. Producing paths are the investigation's code (run.py and other files outside its
records, queries/ and settings), the result's own queries, and src/ except the helpers that only
dispatch, record, or package (awb.py, provenance.py, packaging/), so a repair replacing those
stales nothing. compare_evidence reads only awb-evidence/3 files whose settings name their result;
any other file fails every comparison, so its result must be rerun.
Paths are project-relative POSIX, except that a files[].path copied from publication.json or
provenance.json is relative to the directory holding that file, and a publication's
inputs[].files[].path to its acquisition directory.
Data hashes are copied when recording and verified when comparing; TOML date/time
values use ISO strings in JSON, consistently during comparison.

record_evidence derives omitted publications from the views' data/parquet references and
omitted acquisitions from those publications' publication.json inputs. cli_stale backs
`python3 src/awb.py stale`, which compares every recorded result with the current state.

prior_result and record_finding write a recorded result's state.md findings row for run.py, and
cli_state backs `python3 src/awb.py state`, which shows and updates investigation state.
findings.json (awb-findings/1) owns the Current findings table, which every findings write
re-renders whole; hand edits to it are refused as drift. Other lines keep their bytes, and the
writers add the history.md entries for reruns and status changes that matter.
"""

import argparse
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import threading
from collections.abc import Iterable
from contextlib import contextmanager
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


_SCHEMA = "awb-evidence/3"
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
    """The part of parsed settings one result reads: [parameters] and its own [results.<id>]."""
    results = content.get("results")
    table = results.get(result_id) if isinstance(results, dict) else None
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
_NOT_CODE = {"brief.md", "state.md", "findings.json", "history.md", "evidence", "exploration", "results", "queries"}
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
        "schema": _SCHEMA, "investigation": investigation, "result_id": result_id,
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
        current = evidence["schema"] == _SCHEMA and evidence["settings"].get("result")
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        return [{"name": name, "paths": [evidence_path], "outcome": "fail",
                 "detail": f"missing evidence: {evidence_path}: {str(error).rstrip('.')}."} for name in names]
    if not current:
        return [{"name": name, "paths": [evidence_path], "outcome": "fail",
                 "detail": f"unusable evidence: {evidence_path}: not {_SCHEMA} with result-scoped settings; "
                           "rerun the result."} for name in names]
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
                scope = entry["result"]
                current = _settings(root, entry["path"])
                old, new = entry["content"], current["content"]
                if not _is_unknown(old) and not _is_unknown(new):
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


# Investigation state: findings.json, state.md, history.md, and README's Active investigation line.
# A writer validates the findings table and any list section it edits, rewrites only the lines it
# changes, and writes nothing when a record is missing or malformed.

class StateError(ValueError):
    """A record is malformed, a guard refused, or a write failed with recovery details."""


_COLUMNS = ["Finding", "Evidence", "Status", "Revalidation reason or caveat"]
_STATUSES = ("provisional", "supported", "superseded")
_FLAGGED = "revalidation-needed"
_ITEM = re.compile(r"([-*+]|(\d+)([.)]))[ \t]+(.*)")
_LISTS = {"issues": "Unresolved issues", "next": "Next steps"}


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


def _bare(line):
    return line.rstrip("\r\n")


def _cells(line):
    cells = re.split(r"(?<!\\)\|", _bare(line).strip())
    if cells and cells[0] == "":
        cells = cells[1:]
    if cells and cells[-1] == "":
        cells = cells[:-1]
    return [cell.strip() for cell in cells]


def _row(cells):
    return "|" + "|".join(f" {cell} " if cell else " " for cell in cells) + "|"


def _segments(caveat):
    """Split a caveat cell into its reserved check segments and the notes an agent wrote."""
    parts = [part for part in caveat.split("; ") if part]
    return [p for p in parts if p.startswith(_CHECK_LABELS)], [p for p in parts if not p.startswith(_CHECK_LABELS)]


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


class _State(_Record):
    """state.md with one Last updated line and a valid findings table, each result on one row.

    `strict=False` only locates the table, for `state render` to replace whatever rows it holds.
    """

    def __init__(self, root, investigation, *, strict=True):
        super().__init__(root / "investigations" / investigation / "state.md",
                         f"investigations/{investigation}/state.md")
        updated = [i for i, line in enumerate(self.lines) if line.startswith("Last updated:")]
        if len(updated) != 1:
            raise StateError(f"{self.label}: {'no' if not updated else 'repeated'} 'Last updated:' line")
        self.updated = updated[0]
        self.locate(strict)

    def locate(self, strict=True):
        """Find the findings table: its contiguous rows, and stray rows below a break that link evidence."""
        start, end = self.section("Current findings")
        header = next((i for i in range(start + 1, end) if self.lines[i].lstrip().startswith("|")), None)
        if header is None or header + 1 >= end or _cells(self.lines[header]) != _COLUMNS \
                or len(_cells(self.lines[header + 1])) != len(_COLUMNS) \
                or not all(re.fullmatch(r":?-+:?", c) for c in _cells(self.lines[header + 1])):
            raise StateError(f"{self.label}: Current findings needs a table with columns {' | '.join(_COLUMNS)}")
        self.rows_start = self.rows_end = header + 2
        linked = {}
        while self.rows_end < end and self.lines[self.rows_end].lstrip().startswith("|"):
            cells = _cells(self.lines[self.rows_end])
            if not strict:
                self.rows_end += 1
                continue
            if len(cells) != len(_COLUMNS):
                raise StateError(f"{self.label}: findings row {self.rows_end + 1} does not have four cells")
            for result_id in set(_EVIDENCE_LINK.findall(cells[1])):
                if result_id in linked:
                    raise StateError(f"{self.label}: rows {linked[result_id] + 1} and {self.rows_end + 1} "
                                     f"both link {result_id}; keep one row per result")
                linked[result_id] = self.rows_end
            self.rows_end += 1
        self.linked = linked
        self.strays = [i for i in range(self.rows_end, end)
                       if self.lines[i].lstrip().startswith("|") and _EVIDENCE_LINK.search(self.lines[i])]

    def row_for(self, result_id):
        """(line index, cells) of the row linking this result's evidence, or None."""
        index = self.linked.get(result_id)
        return None if index is None else (index, _cells(self.lines[index]))

    def touch(self, today):
        line = self.lines[self.updated]
        self.lines[self.updated] = f"Last updated: {today}" + line[len(_bare(line)):]

    def items(self, title):
        """A list section's items as (first line, end line, text), continuation lines included."""
        start, end = self.section(title)
        items, i = [], start + 1
        while i < end:
            match = _ITEM.fullmatch(_bare(self.lines[i]))
            if not match:
                i += 1
                continue
            j, parts = i + 1, [match[4].strip()]
            while j < end and self.lines[j].strip() and self.lines[j][0] in " \t":
                parts.append(self.lines[j].strip())
                j += 1
            items.append((i, j, " ".join(parts)))
            i = j
        return items


def _today():
    return datetime.now().date().isoformat()


@contextmanager
def _signals_deferred():
    """Hold SIGINT and SIGTERM until the block ends, then restore the handlers and replay them."""
    if threading.current_thread() is not threading.main_thread():
        yield
        return
    pending, previous = [], {}

    def hold(signum, frame):
        pending.append(signum)

    for number in (signal.SIGINT, signal.SIGTERM):
        try:
            previous[number] = signal.signal(number, hold)
        except (OSError, ValueError):
            pass
    try:
        yield
    finally:
        for number, handler in previous.items():
            signal.signal(number, signal.SIG_DFL if handler is None else handler)
        for number in dict.fromkeys(pending):
            signal.raise_signal(number)


def _commit(records, *, replaced=None, prior_rows=()):
    """Prepare all temporary files, then replace records in order with signals deferred."""
    replaced = [] if replaced is None else replaced
    temporaries, current = [], records[0]
    try:
        for record in records:
            current = record
            temporary = record.path.with_name(f".{record.path.name}.{os.getpid()}.tmp")
            temporaries.append(temporary)
            with open(temporary, "w", encoding="utf-8", newline="") as stream:
                stream.write("".join(record.lines))
        with _signals_deferred():
            for record, temporary in zip(records, temporaries):
                current = record
                os.replace(temporary, record.path)
                replaced.append(record.path)
    except OSError as error:
        if not replaced:
            message = f"{current.label} not written: {error}; nothing was replaced"
        else:
            missing = next(r for r in records if r.path not in replaced)
            if missing.path.name == "state.md" and records[0].path.name == "findings.json":
                investigation = missing.path.parent.name
                message = (f"{missing.label} not written ({error}); the table is behind findings.json; "
                           f"restore it with python3 src/awb.py state render --investigation {investigation}")
            else:
                message = f"{missing.label} not written ({error}); the prior rows it lacks: " + " ".join(prior_rows)
        failure = StateError(message)
        failure.replaced = list(replaced)
        raise failure from error
    finally:
        for temporary in temporaries:
            temporary.unlink(missing_ok=True)


def _finding_cells(entry):
    status = entry["status"]
    if status == _FLAGGED and entry["prior_status"] is not None:
        status += f" (was {entry['prior_status']})"
    caveat = "; ".join(p for p in [entry["checks_caveat"], *entry["notes"], entry["flag_reason"]] if p)
    return [_cell(entry["text"]), f"[{entry['result']}](evidence/{entry['result']}.json)",
            _cell(status), _cell(caveat)]


# notes_checks is the checks caveat the notes were written against (null: none); a promotion counts
# the notes as explaining failed or not-assessed checks only while it equals the current one.
_ENTRY_KEYS = {"result", "text", "status", "prior_status", "flag_reason", "notes", "checks_caveat", "notes_checks"}


class _Findings:
    def __init__(self, root, investigation, *, render=False):
        self.state = _State(root, investigation, strict=not render)
        self.path = self.state.path.with_name("findings.json")
        self.label = f"investigations/{investigation}/findings.json"
        self.history, self.prior_rows, self.changed = None, [], False
        if not self.path.exists():  # no finding recorded yet: the table renders empty
            self.entries = []
            return
        try:
            content = json.loads(self.path.read_text(encoding="utf-8"))
            if content["schema"] != "awb-findings/1" or not isinstance(content["findings"], list):
                raise ValueError("expected awb-findings/1 findings list")
            self.entries = content["findings"]
            seen = set()
            for entry in self.entries:
                if (not isinstance(entry, dict) or set(entry) != _ENTRY_KEYS
                        or entry["notes_checks"] is not None and not isinstance(entry["notes_checks"], str)
                        or not all(isinstance(entry[k], str) for k in
                                   ("result", "text", "status", "flag_reason", "checks_caveat"))
                        or not _ID.fullmatch(entry["result"]) or entry["result"] in seen
                        or entry["status"] not in (*_STATUSES, _FLAGGED)
                        or entry["prior_status"] is not None and
                           (entry["status"] != _FLAGGED or not isinstance(entry["prior_status"], str))
                        or not isinstance(entry["notes"], list)
                        or not all(isinstance(n, str) for n in entry["notes"])):
                    raise ValueError(f"invalid finding: {entry}")
                seen.add(entry["result"])
        except (OSError, ValueError, KeyError, TypeError) as error:
            raise StateError(f"{self.label}: {error}") from error

    def drift(self):
        disk = self.state.lines[self.state.rows_start:self.state.rows_end]
        rendered = [_row(_finding_cells(e)) for e in self.entries]
        differences = []
        for i in range(max(len(disk), len(rendered))):
            old = _bare(disk[i]) if i < len(disk) else None
            new = rendered[i] if i < len(rendered) else None
            if old is not None and new is not None and _cells(old) == _cells(new):
                continue
            links = _EVIDENCE_LINK.findall(old or new or "")
            differences.append({"result": links[0] if len(links) == 1 else None, "disk": old, "rendered": new})
        for i in self.state.strays:  # a row cut off from the table by a blank or other line
            links = _EVIDENCE_LINK.findall(self.state.lines[i])
            differences.append({"result": links[0] if len(links) == 1 else None,
                                "disk": _bare(self.state.lines[i]), "rendered": None})
        return differences

    def refuse_drift(self, investigation):
        differences = self.drift()
        if not differences:
            return
        details = []
        by_id = {e["result"]: e for e in self.entries}
        for row in differences:
            details.append(f"disk: {row['disk']}; rendered: {row['rendered']}")
            cells = _cells(row["disk"]) if row["disk"] else []
            entry = by_id.get(row["result"])
            if len(cells) == 4 and cells[2].startswith(_FLAGGED) and entry and entry["status"] != _FLAGGED:
                parts = _segments(cells[3].replace(r"\|", "|"))[1]
                notes = entry["notes"]
                if parts[:len(notes)] == notes:
                    parts = parts[len(notes):]
                reason = "; ".join(parts)
                flags = json.dumps([{"result": row["result"], "reason": reason}])
                details.append(f"if this flag was added by hand, re-apply it after rendering with python3 "
                               f"src/awb.py state flag --investigation {investigation}, stdin: {flags}; if a write "
                               "failed after findings.json was saved, rendering alone restores the table")
        raise StateError("findings drift: " + " | ".join(details) +
                         f"; python3 src/awb.py state render --investigation {investigation} discards the hand edit; "
                         "then re-apply the intended change with state finding")


def findings_drift(project_root, investigation) -> list[dict]:
    """Compare the table with its render from findings.json (empty when absent), writing nothing."""
    return _Findings(Path(project_root).resolve(), investigation).drift()


def _write_findings(root, investigation, mutate, *, check=False, render=False, replaced=None):
    findings = _Findings(root, investigation, render=render)
    if not render:
        findings.refuse_drift(investigation)
    result = mutate(findings)
    if check or not findings.changed:
        return result
    state = findings.state
    state.locate(strict=False)  # a mutation may have moved lines above the table
    for i in reversed(state.strays):
        del state.lines[i]
    state.lines[state.rows_start:state.rows_end] = [
        _row(_finding_cells(e)) + state.newline for e in findings.entries]
    findings.lines = [json.dumps({"schema": "awb-findings/1", "findings": findings.entries}, indent=2, ensure_ascii=False) + "\n"]
    _commit([findings, state] + ([findings.history] if findings.history else []),
            replaced=replaced, prior_rows=findings.prior_rows)
    return result


def render_findings(project_root, investigation) -> dict:
    """Restore the table from JSON, returning every differing disk row discarded."""
    def mutate(findings):
        discarded = [r["disk"] for r in findings.drift() if r["disk"] is not None]
        findings.changed = True
        return {"discarded": discarded}
    return _write_findings(Path(project_root).resolve(), investigation, mutate, render=True)


def _has_reason(flag_reason, reason):
    """Whether `reason` is already a whole run of "; "-separated parts of `flag_reason`."""
    return f"; {reason}; " in f"; {flag_reason}; "


def flag_findings(project_root, investigation, flags, *, check=False, today=None) -> dict:
    """Validate a whole batch, then flag findings without a history entry."""
    if not isinstance(flags, list) or any(not isinstance(f, dict) or set(f) != {"result", "reason"}
            or not all(isinstance(f[k], str) and f[k].strip() for k in f) for f in flags):
        raise ValueError("flags must be a JSON list of result and nonempty reason strings")

    def mutate(findings):
        by_id = {e["result"]: e for e in findings.entries}
        for flag in flags:
            if flag["result"] not in by_id:
                raise StateError(f"{findings.state.label}: no findings row links {flag['result']}")
        changed, unchanged, rows = [], [], []
        for flag in flags:
            entry = by_id[flag["result"]]
            reason = flag["reason"]
            if entry["status"] == _FLAGGED and _has_reason(entry["flag_reason"], reason):
                unchanged.append(entry["result"])
                continue
            if entry["status"] != _FLAGGED:
                entry["prior_status"], entry["status"] = entry["status"], _FLAGGED
            if not _has_reason(entry["flag_reason"], reason):
                entry["flag_reason"] = "; ".join(p for p in (entry["flag_reason"], reason) if p)
            changed.append({"result": entry["result"], "status": _finding_cells(entry)[2]})
            rows.append(_row(_finding_cells(entry)))
        if changed:
            findings.changed = True
            findings.state.touch(today or _today())
        return {"flags": changed, "unchanged": unchanged, "rows": rows}
    return _write_findings(Path(project_root).resolve(), investigation, mutate, check=check)


def _history(root, investigation, entry):
    history = _Record(root / "investigations" / investigation / "history.md",
                      f"investigations/{investigation}/history.md")
    history.insert(len(history.lines), entry)
    return history


def evidence_commit(project_root, investigation: str, result_id: str) -> str:
    """Cite a result's current evidence file: HEAD's full SHA when it is committed and unchanged.

    Otherwise `uncommitted; last committed at <sha>` when Git holds an earlier version, which may
    predate uncommitted evidence, else `uncommitted`.
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
        last = _git(root, "log", "-1", "--diff-filter=AMR", "--format=%H", "--", path).strip()
        if last:
            _git(root, "cat-file", "-e", f"{last}:./{path}")
            return f"uncommitted; last committed at {last}"
    except (OSError, subprocess.CalledProcessError):
        pass
    return "uncommitted"


def _cite(citation):
    return citation if citation.startswith(("uncommitted", "not captured")) else f"at commit {citation}"


def _baseline(table, checks, settings):
    """What an exact-match rerun compares: the table's sha256, the full checks list, scoped settings."""
    return {"table": table, "checks": json.loads(json.dumps(checks)), "settings": settings}


def prior_result(project_root, investigation: str, result_id: str) -> dict:
    """Capture what a rerun replaces; run.py calls this before it unlinks the evidence file.

    Returns {citation, baseline}: the evidence_commit citation, and the saved table's sha256 with
    the evidence's checks and scoped settings, or None when the evidence is unreadable, predates
    scoped settings, or the table is missing.
    """
    root = Path(project_root).resolve()
    base = root / "investigations" / investigation
    # Check drift before run.py removes evidence; a missing state.md refuses here.
    _Findings(root, investigation).refuse_drift(investigation)
    baseline = None
    try:
        evidence = json.loads((base / "evidence" / f"{result_id}.json").read_text())
        table = _checksum(root, f"investigations/{investigation}/results/{result_id}.csv")["sha256"]
        if evidence["settings"].get("result") == result_id and table and isinstance(evidence["checks"], list):
            baseline = _baseline(table, evidence["checks"], evidence["settings"]["content"])
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        pass
    return {"citation": evidence_commit(root, investigation, result_id), "baseline": baseline}


def _rerun_entry(today, result_id, old, cells, exact, flag_reason, citation):
    resulting = cells[2]
    impact = "superseded; no promotion required" if resulting == "superseded" else \
        f"{resulting}; re-promote with `awb.py state finding`"
    return ["", f"### {today} — {result_id} rerun: {old[2]} → {resulting}", "",
            f"- **Change or finding:** prior row `{_row(old)}`; now {resulting}, caveat "
            f"{cells[3] or 'none'}" + ("; table, checks and settings unchanged." if exact else "."),
            f"- **Evidence:** [{result_id}](evidence/{result_id}.json); prior evidence {_cite(citation)}.",
            "- **Reasoning or decision:** rerun" + (f"; flag reason: {flag_reason}" if flag_reason else ""),
            f"- **Impact and caveats:** {impact}.",
            "- **Supersedes or revalidation link:**"]


def record_finding(project_root, investigation: str, result_id: str, checks: list[dict], *,
                   prior: dict | None = None, today: str | None = None) -> dict:
    """Write a just-recorded result's state.md row; run.py calls this after record_evidence.

    `prior` is prior_result(), taken before the rerun. A new result gets a provisional placeholder
    row. An unflagged row whose table, checks, and scoped settings all equal the prior baseline is
    kept untouched; otherwise its reserved caveat segments are replaced, its status becomes
    provisional unless superseded, and history.md records a rerun of a supported row. A flagged row
    returns to superseded if it was superseded, else provisional, with its notes kept, its flag reason
    dropped, and a history entry naming that reason. When findings.json is not replaced, the evidence just recorded is removed before raising.
    Returns {action: added|kept|refreshed|flag cleared, status, history (bool)}.
    """
    root = Path(project_root).resolve()
    today = today or _today()
    prior = prior or {"citation": "not captured", "baseline": None}
    base = root / "investigations" / investigation
    evidence_path = base / "evidence" / f"{result_id}.json"
    replaced = []

    def mutate(findings):
        entry = next((e for e in findings.entries if e["result"] == result_id), None)
        history = None
        old = _finding_cells(entry) if entry else None
        if entry is None:
            entry = {"result": result_id, "text": f"<state the finding from {result_id}>",
                     "status": "provisional", "prior_status": None, "flag_reason": "", "notes": [],
                     "checks_caveat": _check_caveat(checks), "notes_checks": _check_caveat(checks)}
            findings.entries.append(entry)
            action = "added"
        else:
            evidence = json.loads(evidence_path.read_text())
            table = _checksum(root, f"investigations/{investigation}/results/{result_id}.csv")["sha256"]
            exact = prior["baseline"] is not None and \
                prior["baseline"] == _baseline(table, checks, evidence["settings"].get("content"))
            flagged = entry["status"] == _FLAGGED
            if not flagged and exact:
                return {"action": "kept", "status": entry["status"], "history": False}
            flag_reason = entry["flag_reason"] if flagged else ""
            entry["status"] = "superseded" if (entry["prior_status"] if flagged else entry["status"]) == \
                "superseded" else "provisional"
            entry["checks_caveat"] = _check_caveat(checks)
            if flagged:
                entry.update(prior_status=None, flag_reason="")  # notes, such as a known limitation, stay
            action = "flag cleared" if flagged else "refreshed"
            if flagged or old[2] == "supported":
                history = _history(root, investigation, _rerun_entry(
                    today, result_id, old, _finding_cells(entry), exact, flag_reason, prior["citation"]))
        findings.history, findings.changed = history, True
        findings.prior_rows = [_row(old)] if old else []
        findings.state.touch(today)
        return {"action": action, "status": entry["status"], "history": history is not None}

    try:
        return _write_findings(root, investigation, mutate, replaced=replaced)
    except BaseException:
        if base / "findings.json" not in replaced:
            evidence_path.unlink(missing_ok=True)
        raise


def update_findings(project_root, investigation: str, result_ids: list[str], *, status: str | None = None,
                    text: str | None = None, caveat: str | None = None, reason: str | None = None,
                    today: str | None = None) -> dict:
    """Change findings rows' status, or one row's wording or caveat notes, checking every row first.

    ValueError for unusable arguments, including a missing reason when history needs one;
    StateError when a guard refuses. Returns {rows (the changed rows), unchanged, warnings,
    history (the entry's heading, or None)}.
    """
    root = Path(project_root).resolve()
    today = today or _today()
    if not result_ids or status is None and text is None and caveat is None:
        raise ValueError("give --status, --text, or --caveat")
    if status is not None and status not in _STATUSES:
        raise ValueError(f"status must be one of {', '.join(_STATUSES)}")
    if len(result_ids) > 1 and (status is None or text is not None or caveat is not None):
        raise ValueError("several result IDs take --status only, with --reason")
    if text is not None and not text.strip():
        raise ValueError("the finding text is empty")
    notes = [_cell(part) for part in (caveat or "").split(";") if part.strip()]
    if any(note.startswith(_CHECK_LABELS) for note in notes):
        raise ValueError("--caveat cannot use the reserved prefixes 'failed checks:' or 'not assessed:'")

    def mutate(findings):
        state = findings.state
        changes, unchanged, warnings = [], [], []
        for result_id in dict.fromkeys(result_ids):
            found = state.row_for(result_id)
            evidence_path = root / "investigations" / investigation / "evidence" / f"{result_id}.json"
            if found is None:
                raise StateError(f"{state.label}: no findings row links {result_id}; run run.py for it first")
            if not evidence_path.is_file():
                raise StateError(f"{result_id}: evidence/{result_id}.json does not exist; rerun it with run.py")
            index, old = found
            entry = next(e for e in findings.entries if e["result"] == result_id)
            cells = list(old)
            if text is not None:
                cells[0] = _cell(text)
            if status is not None:
                cells[2] = status
            if caveat is not None:
                cells[3] = "; ".join(p for p in [_cell(entry["checks_caveat"]), *notes] if p)
            if cells == old:
                unchanged.append(result_id)
                continue
            flagged = old[2].startswith(_FLAGGED)
            if flagged and (status in ("provisional", "supported") or caveat is not None):
                raise StateError(f"{result_id} is flagged ({old[2]}); only a rerun clears the flag, so it can be "
                                 "superseded or reworded but not promoted or given a caveat")
            if flagged and cells[0] != old[0]:
                warnings.append(f"warning: {result_id} is flagged; package dispositions recorded against its old "
                                "text reopen")
            if cells[2] == "supported":
                failed = [c["name"] for c in compare_evidence(root, evidence_path) if c["outcome"] == "fail"]
                if failed:
                    raise StateError(f"{result_id} is stale ({', '.join(failed)}); rerun it before promoting it")
                gaps = _check_caveat(json.loads(evidence_path.read_text()).get("checks") or [])
                # Kept notes explain the checks only while those checks are the ones they were written for.
                current = entry["notes"] and entry["notes_checks"] == gaps
                if gaps and not (notes if caveat is not None else current):
                    detail = (f"; its notes were written for {entry['notes_checks'] or 'no checks'}, so restate "
                              "those that still hold" if entry["notes"] and caveat is None else "")
                    raise StateError(f"{result_id} has failed or not-assessed checks ({gaps}); "
                                     f"explain them with --caveat before promoting it{detail}")
            logged = (old[2] == "supported" or flagged) or cells[2] in ("supported", "superseded")
            changes.append((result_id, index, old, cells, logged))
        if not changes:
            return {"rows": [], "unchanged": unchanged, "warnings": warnings, "history": None}
        history = heading = None
        if any(logged for *_, logged in changes):
            if not (reason or "").strip():
                raise ValueError("--reason is required: this change is recorded in history.md")
            words = []
            for _, _, old, cells, _ in changes:
                words += (["reworded"] if cells[0] != old[0] else []) + (["caveat revised"] if cells[3] != old[3] else [])
                if cells[2] != old[2]:
                    words.append("promoted to supported" if cells[2] == "supported" else f"set to {cells[2]}")
            heading = f"### {today} — {', '.join(c[0] for c in changes)} {' and '.join(dict.fromkeys(words))}"
            entry = ["", heading, "",
                     "- **Change or finding:** " + " ".join(
                         f"{rid} was `{_row(old)}`; now \"{cells[0]}\" ({cells[2]})." for rid, _, old, cells, _ in changes),
                     "- **Evidence:** " + "; ".join(
                         f"[{rid}](evidence/{rid}.json) {_cite(evidence_commit(root, investigation, rid))}"
                         for rid, *_ in changes) + ".",
                     f"- **Reasoning or decision:** {' '.join(reason.split())}",
                     "- **Impact and caveats:** " + "; ".join(f"{rid}: {cells[3] or 'none'}"
                                                             for rid, _, _, cells, _ in changes) + ".",
                     "- **Supersedes or revalidation link:**"]
            history = _history(root, investigation, entry)
        for rid, _, old, cells, _ in changes:
            entry = next(e for e in findings.entries if e["result"] == rid)
            if text is not None:
                entry["text"] = text
            if status is not None:
                if entry["status"] == _FLAGGED and entry["flag_reason"]:
                    entry["notes"].append(entry["flag_reason"])  # a flag reason explains no check
                    entry["flag_reason"], entry["notes_checks"] = "", None
                entry["status"], entry["prior_status"] = status, None
            if caveat is not None:
                entry["notes"] = [part.replace(r"\|", "|") for part in notes]
                entry["notes_checks"] = entry["checks_caveat"]
        state.touch(today)
        findings.history, findings.changed = history, True
        findings.prior_rows = [_row(old) for _, _, old, _, _ in changes]
        return {"rows": [_row(cells) for *_, cells, _ in changes], "unchanged": unchanged, "warnings": warnings,
                "history": heading}
    return _write_findings(root, investigation, mutate)


def edit_list(project_root, investigation: str, which: str, *, add: list[str] = (), drop: list[str] = (),
              today: str | None = None) -> dict:
    """Add and drop Unresolved issues (`issues`) or Next steps (`next`) items in one write.

    A drop is the item's number in the list or a case-sensitive substring of exactly one item,
    resolved against the list before anything changes; ValueError names the candidates otherwise.
    Only list-item lines change. Returns {added, dropped}.
    """
    root = Path(project_root).resolve()
    title = _LISTS[which]
    added = [" ".join(text.split()) for text in add]
    if not added and not drop or not all(added):
        raise ValueError("give --add or --drop with nonempty text")

    state = _State(root, investigation)
    start, end = state.section(title)
    items = state.items(title)
    chosen = []
    for target in drop:
        if target.strip().isdigit() and 1 <= int(target) <= len(items):
            matches = [items[int(target) - 1]]
        else:
            matches = [item for item in items if target and target in item[2]]
        if len(matches) != 1:
            listing = "; ".join(f"{items.index(m) + 1}. {m[2]}" for m in matches or items) or "the list is empty"
            raise ValueError(f"--drop {target!r} matches {len(matches)} {title} items: {listing}")
        if matches[0] not in chosen:
            chosen.append(matches[0])
    # Plan on the original line numbers, then apply from the bottom up, deletions before an
    # insertion at the same line.
    operations = [(first, 1, stop) for first, stop, _ in chosen]
    if added:
        remaining = [item for item in items if item not in chosen]
        if remaining:
            match = _ITEM.fullmatch(_bare(state.lines[remaining[-1][0]]))
            number = int(match[2]) + 1 if match[2] else None
            position = remaining[-1][1]
            lines = [f"{number + n}{match[3]} {t}" if number else f"{match[1]} {t}" for n, t in enumerate(added)]
        else:
            dropped = {i for first, stop, _ in chosen for i in range(first, stop)}
            body = [i for i in range(start + 1, end) if state.lines[i].strip() and i not in dropped]
            position, lines = (body[-1] if body else start) + 1, [f"- {t}" for t in added]
        operations.append((position, 0, lines))
    for position, kind, value in sorted(operations, key=lambda op: (op[0], op[1]), reverse=True):
        if kind:
            del state.lines[position:value]
        else:
            state.insert(position, value)
    state.touch(today or _today())
    _commit([state])
    return {"added": added, "dropped": [item[2] for item in chosen]}


def _pointer(value):
    """Parse an Active investigation value: (slug or 'none', rewrite function), or None if customized."""
    value = value.strip()
    match = re.fullmatch(r"\[[^\]]*\]\((\./)?investigations/([A-Za-z0-9][A-Za-z0-9_-]*)/state\.md\)", value)
    if match:
        return match[2], lambda new: f"[{new}]({match[1] or ''}investigations/{new}/state.md)"
    match = re.fullmatch(r"(`?)(\./)?investigations/([A-Za-z0-9][A-Za-z0-9_-]*)/state\.md\1", value)
    if match:
        return match[3], lambda new: f"{match[1]}{match[2] or ''}investigations/{new}/state.md{match[1]}"
    if value == "none":
        return value, lambda new: f"[{new}](investigations/{new}/state.md)"
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", value):
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


def state_view(project_root, investigation: str) -> str:
    """The resume view: brief.md and state.md verbatim, then a warning per row with missing evidence."""
    root = Path(project_root).resolve()
    base = root / "investigations" / investigation
    out = []
    for name in ("brief.md", "state.md"):
        label = f"investigations/{investigation}/{name}"
        try:
            text = (base / name).read_text(encoding="utf-8")
        except FileNotFoundError:
            if name == "state.md":
                raise StateError(f"{label} does not exist") from None
            text = "(missing)\n"
        except (OSError, UnicodeError) as error:
            raise StateError(f"{label} is unreadable: {error}") from None
        out.append(f"==> {label} <==\n{text.rstrip()}\n")
    out += [f"warning: {result_id} links evidence/{result_id}.json, which does not exist"
            for result_id in finding_rows(base / "state.md") if not (base / "evidence" / f"{result_id}.json").is_file()]
    return "\n".join(out)


def switch_active(project_root, investigation: str) -> bool:
    """Point README's Active investigation line at an investigation with a state.md, keeping its form."""
    root = Path(project_root).resolve()
    if not (root / "investigations" / investigation / "state.md").is_file():
        raise StateError(f"investigations/{investigation}/state.md does not exist")
    readme, index, (current, rewrite) = _readme_pointer(root)
    if current == investigation:
        return False
    line = _bare(readme.lines[index])
    value = line[len("Active investigation:"):]
    spacing = value[:len(value) - len(value.lstrip())] or " "
    readme.lines[index] = f"Active investigation:{spacing}{rewrite(investigation)}" + readme.lines[index][len(line):]
    _commit([readme])
    return True


_STATE_EXIT = ("Exit status: 0 done; 1 a record is missing or malformed, a guard refused, or a write failed "
               "(stderr names recovery after a partial write); 2 unusable arguments, an unknown investigation, a missing --reason, or a "
               "--drop matching zero or several items.")


def cli_state(root: Path, argv: list[str]) -> int:
    """Show or update an investigation's state.md and history.md, or README's Active investigation line."""
    root = Path(root).resolve()
    actions = {
        "finding": "promote, supersede, or reword findings; history.md records supported, superseded, and "
                   "flagged changes",
        "render": "restore the Current findings table from findings.json",
        "flag": "flag findings from a JSON list of result and reason on stdin",
        "issues": "add or drop Unresolved issues items",
        "next": "add or drop Next steps items",
        "switch": "point README's Active investigation line at another investigation and show it",
    }
    action = argv[0] if argv and argv[0] in actions else None
    epilog = {
        None: "subcommands:\n" + "\n".join(f"  {name:<8} {summary}" for name, summary in actions.items())
              + "\nRun `awb.py state <subcommand> --help` for its arguments.\n",
        "finding": "Refused: an ID without a row or evidence file; any change leaving a finding supported "
                   "when its evidence is stale, or when its failed or not-assessed checks have no caveat note "
                   "(kept notes count only for the checks they were written against); promoting a flagged "
                   "finding or changing its caveat (only a run.py rerun clears a flag). --reason is required "
                   "when the prior status is supported or flagged, or the new one supported or superseded; "
                   "that change appends one history.md entry. Sets Last updated.\n",
        "render": "Prints discarded disk rows; without findings.json the table renders empty.\n",
        "flag": "Validates every flag before writing. --check writes nothing. Only a rerun clears a flag.\n",
        "issues": "--drop takes the item's number in the list or text only one item contains (case-sensitive), "
                  "resolved before any change. Only list-item lines change. Sets Last updated.\n",
        "switch": "Rewrites only README's Active investigation line, keeping its link form.\n",
    }
    epilog["next"] = epilog["issues"]
    for name in ("finding", "flag", "issues", "next"):
        epilog[name] += "Hand edits to the findings table are refused as drift; state render restores JSON rows.\n"
    parser = argparse.ArgumentParser(
        prog="awb.py state" + (f" {action}" if action else ""),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=actions[action] if action else
        "Show an investigation for resuming: brief.md and state.md verbatim, and a warning for each finding "
        "whose evidence file is missing. Changes nothing. Uses README's Active investigation line unless "
        "--investigation is given; with no active investigation it lists the investigations.",
        epilog=epilog[action] + _STATE_EXIT)
    if action != "switch":
        parser.add_argument("--investigation", metavar="NAME", help="use this investigation, not README's active one")
    if action == "finding":
        parser.add_argument("result_ids", nargs="+", metavar="result-id", help="result IDs the Evidence cells link")
        parser.add_argument("--status", choices=_STATUSES, help="new status")
        parser.add_argument("--text", help="new finding wording (one ID)")
        parser.add_argument("--caveat", help="replace the caveat's notes, keeping the checks segments run.py "
                                             "writes; '' clears them (one ID)")
        parser.add_argument("--reason", help="why, for the history.md entry")
    elif action == "flag":
        parser.add_argument("--check", action="store_true", help="validate without writing")
    elif action in _LISTS:
        parser.add_argument("--add", action="append", default=[], metavar="TEXT", help="item to add (repeatable)")
        parser.add_argument("--drop", action="append", default=[], metavar="NUMBER-OR-TEXT",
                            help="item to drop (repeatable)")
    elif action == "switch":
        parser.add_argument("investigation", help="directory name under investigations/")
    try:
        args = parser.parse_args(argv[1:] if action else argv)
    except SystemExit as stop:
        return stop.code
    name = args.investigation
    if name is not None and not (re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", name)
                                 and (root / "investigations" / name).is_dir()):
        print(f"awb.py state: no investigation named {name!r} under investigations/", file=sys.stderr)
        return 2
    try:
        if name is None:
            _, _, (name, _) = _readme_pointer(root)
            if name == "none" and action is not None:
                raise StateError("README.md names no active investigation; pass --investigation or run "
                                 "`awb.py state switch <name>`")
            if name == "none":
                base = root / "investigations"
                names = sorted(p.name for p in base.iterdir() if p.is_dir()) if base.is_dir() else []
                print("No active investigation. Investigations: " + (", ".join(names) or "none")
                      + ". Run `awb.py state switch <name>` or pass --investigation.")
                return 0
        if action is None:
            print(state_view(root, name))
        elif action == "switch":
            changed = switch_active(root, name)
            print(("Active investigation: " if changed else "Already active: ") + name + "\n"
                  + state_view(root, name))
        elif action == "render":
            result = render_findings(root, name)
            print("\n".join(f"discarded: {row}" for row in result["discarded"]))
        elif action == "flag":
            result = flag_findings(root, name, json.load(sys.stdin), check=args.check)
            print(json.dumps(result))
        elif action == "finding":
            result = update_findings(root, name, args.result_ids, status=args.status, text=args.text,
                                     caveat=args.caveat, reason=args.reason)
            print("\n".join(result["warnings"] + result["rows"]
                            + [f"unchanged: {', '.join(result['unchanged'])}"] * bool(result["unchanged"])
                            + [f"history.md: {result['history']}"] * bool(result["history"])))
        else:
            result = edit_list(root, name, action, add=args.add, drop=args.drop)
            print(f"{_LISTS[action]}: added {len(result['added'])}, dropped {len(result['dropped'])}"
                  + "".join(f"\n  - {text}" for text in result["dropped"]))
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
