"""Result evidence for an analytics workbench (Python 3.10+, standard library).

Copy this file to `src/provenance.py`; do not import it from the skill folder.

Schema awb-evidence/2, in order: schema, investigation, result_id, recorded_at
(local ISO time), producing_commit (SHA/uncommitted/unknown), producing_paths
(sorted), producing_uncommitted_changes (path/status/bytes/sha256), views
(path/bytes/sha256/publications), publications (path/publication_file/inputs/
conversion_commit/files), acquisitions (path/provenance_file/status/files),
settings (path/bytes/sha256/content), checks (name/outcome/detail), notes (text or null).
Unknowns are {"unknown": reason}. awb-evidence/1 files also carry a figure entry, which
compare_evidence ignores; it compares both versions.
Paths are project-relative POSIX, except that a files[].path copied from publication.json or
provenance.json is relative to the directory holding that file, and a publication's
inputs[].files[].path to its acquisition directory.
Data hashes are copied when recording and verified when comparing; TOML date/time
values use ISO strings in JSON, consistently during comparison.

record_evidence derives omitted publications from the views' data/parquet references and
omitted acquisitions from those publications' publication.json inputs. cli_stale backs
`python3 src/awb.py stale`, which compares every recorded result with the current state.
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


def _settings(root, path):
    entry = _checksum(root, path)
    try:
        import tomllib
    except ImportError:
        entry["content"] = {"unknown": "tomllib unavailable"}
    else:
        try:
            content = tomllib.loads((root / entry["path"]).read_text())
            entry["content"] = json.loads(json.dumps(content, default=lambda value: value.isoformat()))
        except (OSError, ValueError) as error:
            entry["content"] = {"unknown": str(error)}
    return entry


def record_evidence(project_root, investigation: str, result_id: str, *, views: list[str],
                    publications: list[str] | None = None, acquisitions: list[str] | None = None,
                    settings_path: str | None, checks: list[dict], notes: str | None = None,
                    code_paths: list[str] | None = None) -> Path:
    """Write one result's complete producing state atomically, replacing the same id.

    Omitted publications are those the views read; omitted acquisitions are the inputs
    recorded in those publications' publication.json.
    """
    root = Path(project_root).resolve()
    if not all(isinstance(v, str) and _ID.fullmatch(v) for v in (investigation, result_id)):
        raise ValueError("investigation and result_id must be simple identifiers")
    for check in checks:
        if (not isinstance(check, dict) or set(check) != {"name", "outcome", "detail"}
                or not all(isinstance(check[k], str) for k in check)
                or check["outcome"] not in {"pass", "fail", "not-applicable"}):
            raise ValueError("checks require name, outcome (pass/fail/not-applicable), and detail strings")
    code = _expand(root, code_paths if code_paths is not None else
                   [p for p in ("src", f"investigations/{investigation}") if (root / p).is_dir()])
    if code_paths is None:
        prefix = f"investigations/{investigation}/"
        code = [p for p in code if not (p.startswith(prefix) and p[len(prefix):].split("/")[0]
                # figures/ is excluded for investigations laid out before awb-evidence/2.
                in {"brief.md", "state.md", "history.md", "evidence", "figures", "exploration", "results"})]
    view_entries = [{**e, "publications": _view_publications(root, e["path"])}
                    for e in file_checksums(views, root=root)]
    if publications is None:
        publications = sorted({p for e in view_entries if not _is_unknown(e["publications"])
                               for p in e["publications"]})
    if acquisitions is None:
        acquisitions = _publication_acquisitions(root, publications)
    paths = sorted(set(code + [_relative(root, p) for p in views] +
                       ([_relative(root, settings_path)] if settings_path is not None else [])))
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
        "schema": "awb-evidence/2", "investigation": investigation, "result_id": result_id,
        "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "producing_commit": commit, "producing_paths": paths, "producing_uncommitted_changes": changes,
        "views": view_entries,
        "publications": [_input_record(root, p, "publication.json", ["inputs", "conversion_commit", "files"])
                         for p in publications],
        "acquisitions": [_input_record(root, p, "provenance.json", ["status", "files"]) for p in acquisitions],
        "settings": _settings(root, settings_path) if settings_path is not None else
                    {"unknown": "no settings file given"},
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
        if evidence["schema"] not in ("awb-evidence/1", "awb-evidence/2"):
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
                current = _settings(root, entry["path"])
                old, new = entry["content"], current["content"]
                if not _is_unknown(old) and not _is_unknown(new):
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


def finding_row(project_root, investigation: str, result_id: str, checks: list[dict], *,
                finding: str | None = None, status: str = "provisional") -> str:
    """Return the state.md Current findings row for a recorded result, ready to paste.

    The Finding cell keeps the text of a row already linking this result's evidence, else uses
    `finding`, else a placeholder to replace. The caveat names failed and not-assessed checks.
    """
    existing = finding_rows(Path(project_root) / "investigations" / investigation / "state.md")
    if result_id in existing:
        # Split on unescaped pipes; the first cell is the finding text, already escaped.
        text = re.split(r"(?<!\\)\|", existing[result_id][0])[1].strip()
    else:
        text = _cell(finding or f"<state the finding from {result_id}>")
    failed = [c["name"] for c in checks if c["outcome"] == "fail"]
    unassessed = [c["name"] for c in checks if c["outcome"] == "not-applicable" and c["detail"] == "not assessed"]
    caveat = "; ".join(f"{label}: {', '.join(names)}" for label, names in
                       (("failed checks", failed), ("not assessed", unassessed)) if names)
    return f"| {text} | [{result_id}](evidence/{result_id}.json) | {_cell(status)} | {_cell(caveat)} |"


def _short(detail, limit=3):
    parts = detail.rstrip(".").split("; ")
    more = f"; +{len(parts) - limit} more" if len(parts) > limit else ""
    return "; ".join(parts[:limit]) + more + "."


def cli_stale(root: Path, argv: list[str]) -> int:
    """Print, as compact JSON, each recorded result whose evidence no longer matches the project."""
    parser = argparse.ArgumentParser(
        prog="awb.py stale",
        description="Compare investigations' evidence files with the current state; changes nothing.")
    parser.add_argument("--investigation", metavar="NAME", help="check one investigation only")
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
