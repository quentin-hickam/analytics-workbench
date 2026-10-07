"""Result evidence for an analytics workbench (Python 3.10+, standard library).

Copy this file to `src/provenance.py`; do not import it from the skill folder.

Schema awb-evidence/1, in order: schema, investigation, result_id, recorded_at
(local ISO time), producing_commit (SHA/uncommitted/unknown), producing_paths
(sorted), producing_uncommitted_changes (path/status/bytes/sha256), views
(path/bytes/sha256/publications), publications (path/publication_file/inputs/
conversion_commit/files), acquisitions (path/provenance_file/status/files),
settings (path/bytes/sha256/content), checks (name/outcome/detail), figure
(path/bytes/sha256 or null), notes (text or null). Unknowns are {"unknown": reason}.
Paths are project-relative POSIX; listed data paths are metadata-directory-relative.
Data hashes are copied when recording and verified when comparing; TOML date/time
values use ISO strings in JSON, consistently during comparison.
"""

import hashlib
import json
import os
import re
import subprocess
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path


def file_checksums(paths: Iterable[str | os.PathLike], *,
                   root: str | os.PathLike | None = None) -> list[dict]:
    """Hash files in input order; missing files have null size and digest."""
    base = Path(root).resolve() if root is not None else None
    entries = []
    for path in paths:
        file = (base / path).resolve() if base is not None else Path(path)
        path = file.relative_to(base).as_posix() if base is not None else file.as_posix()
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


def _relative(root, path):
    return (root / path).resolve().relative_to(root).as_posix()


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


def _refs(root, path):
    try:
        return sorted({f"data/parquet/{dataset}/{publication}" for dataset, publication in
                       re.findall(r"data/parquet/([^/\s'\"]+)/([^/\s'\"*]+)/", (root / path).read_text())})
    except (OSError, ValueError) as error:
        return {"unknown": f"{path}: {error}"}


def _metadata(root, path, filename, keys):
    path = _relative(root, path)
    entry = file_checksums([f"{path}/{filename}"], root=root)[0]
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
    entry = file_checksums([path], root=root)[0]
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
                    publications: list[str], acquisitions: list[str], settings_path: str | None,
                    checks: list[dict], figure: str | None = None, notes: str | None = None,
                    code_paths: list[str] | None = None) -> Path:
    """Write one result's complete producing state atomically, replacing the same id."""
    root = Path(project_root).resolve()
    if not all(isinstance(v, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", v)
               for v in (investigation, result_id)):
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
                in {"brief.md", "state.md", "history.md", "evidence", "figures", "exploration"})]
    paths = sorted(set(code + [_relative(root, p) for p in views] +
                       ([_relative(root, settings_path)] if settings_path is not None else [])))
    try:
        vcs = _git(root, "rev-parse", "--is-inside-work-tree").strip() == "true"
    except (OSError, subprocess.CalledProcessError, ValueError):
        vcs = False
    try:
        if not vcs:
            raise subprocess.CalledProcessError(128, "git")
        commit = _git(root, "rev-parse", "--verify", "HEAD").strip()
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
                changes.append({"path": path, "status": status.strip(), **file_checksums([path], root=root)[0]})
    except subprocess.CalledProcessError:
        commit = "uncommitted" if vcs else {"unknown": "not a git repository"}
        changes = [{"path": e["path"], "status": "uncommitted" if vcs else "no-vcs", **e}
                   for e in file_checksums(paths, root=root)]
    evidence = {
        "schema": "awb-evidence/1", "investigation": investigation, "result_id": result_id,
        "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "producing_commit": commit, "producing_paths": paths, "producing_uncommitted_changes": changes,
        "views": [{**e, "publications": _refs(root, e["path"])} for e in file_checksums(views, root=root)],
        "publications": [_metadata(root, p, "publication.json", ["inputs", "conversion_commit", "files"])
                         for p in publications],
        "acquisitions": [_metadata(root, p, "provenance.json", ["status", "files"]) for p in acquisitions],
        "settings": _settings(root, settings_path) if settings_path is not None else
                    {"unknown": "no settings file given"},
        "checks": checks, "figure": file_checksums([figure], root=root)[0] if figure else None, "notes": notes,
    }
    path = root / _relative(root, f"investigations/{investigation}/evidence/{result_id}.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        temporary.write_text(json.dumps(evidence, indent=2) + "\n")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
    return path


def _known(value, *, deep=True):
    if isinstance(value, dict):
        if set(value) == {"unknown"}:
            raise ValueError(value["unknown"])
    if deep and isinstance(value, (dict, list)):
        for item in value.values() if isinstance(value, dict) else value:
            _known(item)
    return value


def _file_diff(root, entry, keys=("sha256",), *, absent_ok=False):
    try:
        _known({k: entry[k] for k in ("path", *keys)})
        path = entry["path"]
        current = file_checksums([path], root=root)[0]
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
    evidence_path = _relative(root, evidence_path)
    names = ("committed-code", "uncommitted-code", "views", "inputs", "settings")
    try:
        evidence = json.loads((root / evidence_path).read_text())
        if evidence["schema"] != "awb-evidence/1":
            raise ValueError("wrong schema")
    except (OSError, ValueError, KeyError, TypeError) as error:
        return [{"name": name, "paths": [evidence_path], "outcome": "fail",
                 "detail": f"missing evidence: {evidence_path}: {error}."} for name in names]
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
                    _git(root, "cat-file", "-e", f"{sha}^{{commit}}")
                    changed = _git(root, "diff", "--name-only", "-z", "--relative", sha, "--", *paths)
                    mismatches = [f"{p}: differs from producing commit" for p in changed.split("\0") if p]
            elif name == "uncommitted-code":
                paths = [e["path"] for e in _known(evidence["producing_uncommitted_changes"], deep=False)]
                for entry in evidence["producing_uncommitted_changes"]:
                    mismatches.extend(_file_diff(root, entry, ("bytes", "sha256"), absent_ok=True))
            elif name == "views":
                paths = [e["path"] for e in _known(evidence["views"], deep=False)]
                publications = {_known(e["path"]) for e in _known(evidence["publications"], deep=False)} if paths else set()
                for entry in evidence["views"]:
                    path = entry["path"]
                    mismatches.extend(_file_diff(root, entry))
                    try:
                        references = _refs(root, path)
                        _known(references)
                        _known(entry["publications"])
                    except (OSError, ValueError) as error:
                        mismatches.append(f"missing evidence: {path}: {error}")
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
                if set(old) != {"unknown"} and set(new) != {"unknown"}:
                    keys = sorted(k for k in old.keys() | new.keys() if (k not in old or k not in new or old[k] != new[k]))
                    if keys:
                        mismatches.append(f"{entry['path']}: settings differ for keys {', '.join(keys)}")
                else:
                    if entry["sha256"] is None:
                        raise ValueError(f"{entry['path']}: missing sha256")
                    if entry["sha256"] != current["sha256"]:
                        mismatches.append(f"{entry['path']}: sha256 differs")
        except (OSError, ValueError, KeyError, TypeError, AttributeError, subprocess.CalledProcessError) as error:
            mismatches.append(f"missing evidence: {evidence_path}: {error}")
        if mismatches:
            prefix = "missing evidence: " if any(m.startswith("missing evidence:") for m in mismatches) else ""
            detail = (prefix if not mismatches[0].startswith(prefix) else "") + "; ".join(mismatches) + "."
        elif name == "committed-code" and evidence["producing_commit"] == "uncommitted":
            detail = "no producing commit; producing files compared under uncommitted-code"
        else:
            detail = "current state matches recorded evidence." if paths else "nothing to compare."
        comparisons.append({"name": name, "paths": paths, "outcome": "fail" if mismatches else "pass", "detail": detail})
    return comparisons
