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
                    publications: list[str], acquisitions: list[str], settings_path: str | None,
                    checks: list[dict], notes: str | None = None,
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
                # figures/ is excluded for investigations laid out before awb-evidence/2.
                in {"brief.md", "state.md", "history.md", "evidence", "figures", "exploration"})]
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
        "views": [{**e, "publications": _view_publications(root, e["path"])}
                  for e in file_checksums(views, root=root)],
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
