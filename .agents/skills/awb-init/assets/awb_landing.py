"""Land, publish, retain, and open analytical sessions for a workbench.

Copy this file to src/preparation/landing.py and import it from there, never
from the skill folder.

data/raw/<source>/<acquisition-id>/provenance.json:
    {source, acquisition_id, request, started_at, completed_at, status,
     files: [{path, bytes, sha256, records}], notes}
    status is "complete"; records is an integer or null.
data/parquet/<dataset>/<publication-id>/publication.json:
    {dataset, publication_id,
     inputs: [{source, acquisition_id, files: [{path, sha256}]}],
     conversion_commit, converted_at, files: [{path, bytes, sha256}], notes}
    conversion_commit is git HEAD or "uncommitted".
Paths are sorted POSIX paths relative to their acquisition or publication.
"""

import hashlib
import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


def _timestamp():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _files(directory):
    return sorted(path.relative_to(directory).as_posix()
                  for path in directory.rglob("*") if path.is_file())


def _write_json(path, value):
    # Serialize before opening so a serialization error leaves no metadata file.
    text = json.dumps(value, indent=2) + "\n"
    path.write_text(text, encoding="utf-8")


def _refuse_existing(*paths):
    for path in paths:
        if path.exists() or path.is_symlink():
            raise FileExistsError(str(path))


def _identifier(value):
    if (not isinstance(value, str) or not value or value in {".", ".."}
            or "/" in value or "\\" in value or value.endswith(".partial")):
        raise ValueError(f"Invalid directory identifier: {value!r}")


def land(project_root, source, acquisition_id, fetch, *, request, records=None, notes=None) -> Path:
    """Fetch original files into a partial directory, then publish provenance."""
    _identifier(source)
    _identifier(acquisition_id)
    final = Path(project_root) / "data/raw" / source / acquisition_id
    partial = final.with_name(final.name + ".partial")
    _refuse_existing(final, partial)
    partial.mkdir(parents=True)
    started_at = _timestamp()
    fetch(partial)
    paths = _files(partial)
    if not paths:
        raise ValueError("Acquisition contains no files")
    if (partial / "provenance.json").exists():
        raise ValueError("provenance.json is reserved")
    if records is not None:
        if not isinstance(records, dict) or any(type(count) is not int for count in records.values()):
            raise ValueError("records must be a dictionary of integer counts")
        if set(records) - set(paths):
            raise ValueError("Record counts name files that were not landed")
    files = [
        {"path": path, "bytes": (partial / path).stat().st_size,
         "sha256": _sha256(partial / path), "records": (records or {}).get(path)}
        for path in paths
    ]
    provenance = {
        "source": source,
        "acquisition_id": acquisition_id,
        "request": request,
        "started_at": started_at,
        "completed_at": _timestamp(),
        "status": "complete",
        "files": files,
        "notes": notes,
    }
    _refuse_existing(final)
    metadata = partial / "provenance.json"
    try:
        _write_json(metadata, provenance)
        _refuse_existing(final)
        os.rename(partial, final)
    except BaseException:
        metadata.unlink(missing_ok=True)
        raise
    return final


def session(project_root, *, views_dir="foundation/views") -> "duckdb.DuckDBPyConnection":
    """Open a session and load view files in name order.

    A view that reads another view must sort after it; use numeric prefixes,
    for example 01_base.sql and 02_derived.sql.
    """
    try:
        import duckdb
    except ImportError as error:
        raise ImportError("session() needs the duckdb package") from error
    root = Path(project_root)
    directory = Path(views_dir)
    if not directory.is_absolute():
        directory = root / directory
    connection = duckdb.connect()
    connection.execute("SET file_search_path = ?", [str(root.resolve())])
    for path in sorted(directory.glob("*.sql")):
        if not path.is_file():
            continue
        try:
            connection.execute(path.read_text(encoding="utf-8"))
        except Exception as error:
            connection.close()
            raise RuntimeError(f"Failed to load view file: {path}") from error
    return connection


def retain(project_root, acquisition_dir, location) -> dict:
    """Copy an acquisition without overwriting and compare the retained files."""
    root = Path(project_root)
    directory = Path(acquisition_dir)
    if not directory.is_absolute():
        directory = root / directory
    directory = directory.resolve()
    raw = (root / "data/raw").resolve()
    if (not directory.is_dir() or not directory.is_relative_to(raw)
            or directory.name.endswith(".partial")
            or not (directory / "provenance.json").is_file()):
        raise ValueError(f"Not a completed acquisition under {raw}: {directory}")
    provenance = json.loads((directory / "provenance.json").read_text(encoding="utf-8"))
    if not isinstance(provenance, dict) or provenance.get("status") != "complete":
        raise ValueError(f"Not a completed acquisition: {directory}")
    _identifier(directory.parent.name)
    _identifier(directory.name)
    destination = Path(location) / "data/raw" / directory.parent.name / directory.name
    conflict = destination.exists() or destination.is_symlink()
    if not conflict:
        partial = destination.with_name(destination.name + ".partial")
        shutil.copytree(directory, partial)
        _refuse_existing(destination)
        os.rename(partial, destination)
    discrepancies = []
    local_files = set(_files(directory))
    retained_files = set(_files(destination))
    for path in sorted(local_files - retained_files):
        discrepancies.append(f"missing at destination: {path}")
    for path in sorted(retained_files - local_files):
        discrepancies.append(f"extra at destination: {path}")
    for path in sorted(local_files & retained_files):
        if _sha256(directory / path) != _sha256(destination / path):
            discrepancies.append(f"sha256 differs: {path}")
    return {"destination": str(destination), "copied": not conflict,
            "conflict": conflict, "discrepancies": discrepancies}


def publish(project_root, dataset, publication_id, convert, *, acquisitions, validate=None,
            notes=None) -> Path:
    """Convert completed acquisitions and publish their validated output."""
    _identifier(dataset)
    _identifier(publication_id)
    root = Path(project_root)
    if not acquisitions:
        raise ValueError("At least one completed acquisition is required")
    inputs = []
    for acquisition in acquisitions:
        directory = Path(acquisition)
        if not directory.is_absolute():
            directory = root / directory
        if (not directory.is_dir() or directory.name.endswith(".partial")
                or not (directory / "provenance.json").is_file()):
            raise ValueError(f"Not a completed acquisition: {directory}")
        provenance = json.loads((directory / "provenance.json").read_text(encoding="utf-8"))
        if not isinstance(provenance, dict) or provenance.get("status") != "complete":
            raise ValueError(f"Not a completed acquisition: {directory}")
        inputs.append({
            "source": provenance["source"],
            "acquisition_id": provenance["acquisition_id"],
            "files": [{"path": file["path"], "sha256": file["sha256"]}
                      for file in sorted(provenance["files"], key=lambda file: file["path"])],
        })
    final = root / "data/parquet" / dataset / publication_id
    partial = final.with_name(final.name + ".partial")
    _refuse_existing(final, partial)
    partial.mkdir(parents=True)
    convert(partial)
    if validate is not None and validate(partial) is False:
        raise ValueError("Publication validation returned False")
    try:
        result = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                                check=False, capture_output=True, text=True)
        conversion_commit = result.stdout.strip() if result.returncode == 0 else "uncommitted"
    except FileNotFoundError:
        conversion_commit = "uncommitted"
    paths = _files(partial)
    if not paths:
        raise ValueError("Publication contains no files")
    if (partial / "publication.json").exists():
        raise ValueError("publication.json is reserved")
    files = [{"path": path, "bytes": (partial / path).stat().st_size,
              "sha256": _sha256(partial / path)} for path in paths]
    publication = {
        "dataset": dataset,
        "publication_id": publication_id,
        "inputs": inputs,
        "conversion_commit": conversion_commit,
        "converted_at": _timestamp(),
        "files": files,
        "notes": notes,
    }
    _refuse_existing(final)
    metadata = partial / "publication.json"
    try:
        _write_json(metadata, publication)
        _refuse_existing(final)
        os.rename(partial, final)
    except BaseException:
        metadata.unlink(missing_ok=True)
        raise
    return final
