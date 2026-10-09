"""Land, publish, retain, and open analytical sessions for a workbench.

Copy this file to src/preparation/landing.py and import it from there, never
from the skill folder. src/awb.py runs cli_sql() as `python3 src/awb.py sql`.

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

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from collections.abc import Callable, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any


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


def _file_entries(directory, paths):
    return [{"path": path, "bytes": (directory / path).stat().st_size,
             "sha256": _sha256(directory / path)} for path in paths]


def _under(root, path):
    path = Path(path)
    return path if path.is_absolute() else root / path


def _refuse_existing(*paths):
    for path in paths:
        if path.exists() or path.is_symlink():
            raise FileExistsError(str(path))


def _check_name(value):
    if (not isinstance(value, str) or not value or value in {".", ".."}
            or "/" in value or "\\" in value or value.endswith(".partial")):
        raise ValueError(f"Invalid directory name: {value!r}")


def _complete_provenance(directory):
    """Return the provenance of a completed acquisition directory, else raise ValueError."""
    metadata = directory / "provenance.json"
    if not directory.is_dir() or directory.name.endswith(".partial") or not metadata.is_file():
        raise ValueError(f"Not a completed acquisition: {directory}")
    provenance = json.loads(metadata.read_text(encoding="utf-8"))
    if not isinstance(provenance, dict) or provenance.get("status") != "complete":
        raise ValueError(f"Not a completed acquisition: {directory}")
    return provenance


def _finish(partial, final, name, value):
    """Write the metadata file, then rename partial to final; on failure leave no metadata."""
    # Serialize before opening so a serialization error leaves no metadata file.
    text = json.dumps(value, indent=2) + "\n"
    metadata = partial / name
    try:
        metadata.write_text(text, encoding="utf-8")
        # os.rename replaces an empty directory on POSIX; refuse one created meanwhile.
        _refuse_existing(final)
        os.rename(partial, final)
    except BaseException:
        metadata.unlink(missing_ok=True)
        raise
    return final


def land(project_root: str | Path, source: str, acquisition_id: str,
         fetch: Callable[[Path], object], *, request: Any,
         records: dict[str, int] | None = None, notes: Any = None) -> Path:
    """Fetch original files into a partial directory, then write provenance and rename it."""
    _check_name(source)
    _check_name(acquisition_id)
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
    files = [{**entry, "records": (records or {}).get(entry["path"])}
             for entry in _file_entries(partial, paths)]
    return _finish(partial, final, "provenance.json", {
        "source": source,
        "acquisition_id": acquisition_id,
        "request": request,
        "started_at": started_at,
        "completed_at": _timestamp(),
        "status": "complete",
        "files": files,
        "notes": notes,
    })


def publish(project_root: str | Path, dataset: str, publication_id: str,
            convert: Callable[[Path], object], *, acquisitions: Sequence[str | Path],
            validate: Callable[[Path], object] | None = None, notes: Any = None) -> Path:
    """Convert completed acquisitions, validate the output, then write publication.json and rename it."""
    _check_name(dataset)
    _check_name(publication_id)
    root = Path(project_root)
    if not acquisitions:
        raise ValueError("At least one completed acquisition is required")
    inputs = []
    for acquisition in acquisitions:
        provenance = _complete_provenance(_under(root, acquisition))
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
    return _finish(partial, final, "publication.json", {
        "dataset": dataset,
        "publication_id": publication_id,
        "inputs": inputs,
        "conversion_commit": conversion_commit,
        "converted_at": _timestamp(),
        "files": _file_entries(partial, paths),
        "notes": notes,
    })


def retain(project_root: str | Path, acquisition_dir: str | Path,
           location: str | Path) -> dict:
    """Copy an acquisition to the retained location without overwriting, then compare checksums."""
    root = Path(project_root)
    directory = _under(root, acquisition_dir).resolve()
    raw = (root / "data/raw").resolve()
    if directory.parent.parent != raw:
        raise ValueError(f"Not a <source>/<acquisition-id> directory under {raw}: {directory}")
    _complete_provenance(directory)
    _check_name(directory.parent.name)
    _check_name(directory.name)
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


def session(project_root: str | Path, *,
            views_dir: str | Path = "foundation/views") -> "duckdb.DuckDBPyConnection":
    """Open an in-memory DuckDB session and load view files in name order.

    Project-relative paths in views, such as data/parquet/..., resolve against
    the project root from any working directory. A view that reads another view
    must sort after it; use numeric prefixes, for example 01_base.sql and
    02_derived.sql.
    """
    try:
        import duckdb
    except ImportError as error:
        raise ImportError("session() needs the duckdb package") from error
    root = Path(project_root).resolve()
    if "," in str(root):
        # file_search_path is a comma-separated list with no escape for a comma.
        raise ValueError(f"session() cannot use a project root containing a comma: {root}")
    directory = _under(root, views_dir)
    connection = duckdb.connect()
    try:
        connection.execute("SET file_search_path = ?", [str(root)])
        for path in sorted(directory.glob("*.sql")):
            if not path.is_file():
                continue
            try:
                connection.execute(path.read_text(encoding="utf-8"))
            except Exception as error:
                raise RuntimeError(f"Failed to load view file: {path}") from error
    except BaseException:
        connection.close()
        raise
    return connection


def _sql_argument(root, argument):
    """Return the text of the query file argument names, else argument itself as SQL text."""
    try:
        path = _under(root, argument)
        is_file = path.is_file()
    except (OSError, ValueError):  # SQL text can be too long, or hold a NUL, for a path
        is_file = False
    return path.read_text(encoding="utf-8") if is_file else argument


def _cell(value, width=80):
    text = "NULL" if value is None else str(value)
    text = text.replace("|", "\\|").replace("\r", "\\r").replace("\n", "\\n")
    return text if len(text) <= width else text[:width - 1] + "…"


def _markdown_table(header, rows):
    lines = ["| " + " | ".join(map(_cell, header)) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(map(_cell, row)) + " |" for row in rows]
    return "\n".join(lines)


def _fail(command, error):
    """Print the error, with its cause, as one line on stderr and return exit status 1."""
    message = f"{error}: {error.__cause__}" if error.__cause__ else str(error)
    print(f"{command}: {' '.join(message.split())}", file=sys.stderr)
    return 1


def cli_sql(root: Path, argv: list[str]) -> int:
    """Run a query file or SQL text in a fresh session; print the first rows and the row count."""
    parser = argparse.ArgumentParser(prog="awb.py sql", description=cli_sql.__doc__)
    parser.add_argument("query", help="query file (absolute or project-relative) or SQL text")
    parser.add_argument("--limit", type=int, default=20, help="rows to print (default 20)")
    parser.add_argument("--out", help="write the full result to this .csv or .parquet file")
    args = parser.parse_args(argv)
    if args.limit < 0:
        parser.error("--limit must be 0 or more")
    out = _under(root, args.out) if args.out else None
    if out is not None and out.suffix.lower() not in {".csv", ".parquet"}:
        parser.error("--out must end in .csv or .parquet")
    try:
        with session(root) as connection:
            # sql() runs every statement and returns the last one's result, or None.
            relation = connection.sql(_sql_argument(root, args.query))
            if relation is None:
                raise ValueError("the SQL returns no rows; end it with a query")
            if out is not None:
                # DuckDB writes both formats itself; neither needs pandas or pyarrow.
                out.parent.mkdir(parents=True, exist_ok=True)
                if out.suffix.lower() == ".csv":
                    relation.write_csv(str(out), header=True)
                else:
                    relation.write_parquet(str(out))
            header, rows = relation.columns, relation.limit(args.limit).fetchall()
            total = relation.aggregate("count(*)").fetchone()[0]
    except Exception as error:
        return _fail("sql", error)
    print(_markdown_table(header, rows))
    print(f"{len(rows)} of {total} rows shown" + (f"; full result in {args.out}" if out else ""))
    return 0
