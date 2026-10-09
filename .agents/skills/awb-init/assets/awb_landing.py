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


# Ledger rows. Helpers write the facts they produce into foundation/sources.md themselves;
# columns that need human judgment (Restrictions, Sources-table descriptions) stay as they are.

_NO_RETAINED_COPY = "this checkout only"


def _split_row(line):
    import re
    text = line.strip()
    text = text[1:] if text.startswith("|") else text
    text = text[:-1] if text.endswith("|") and not text.endswith("\\|") else text
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", text)]


def _join_row(cells):
    return "| " + " | ".join(cells) + " |"


def _cell(value):
    return " ".join(str(value).split()).replace("|", "\\|")


def _plain(cell):
    return cell.strip().strip("`").strip()


def _unretained(cell):
    return _plain(cell).lower() in {"", _NO_RETAINED_COPY}


def _table(lines, title, key):
    """Locate the table under `## <title>` whose header names `key`: (columns, first row, end)."""
    start = next((index for index, line in enumerate(lines) if line.strip() == f"## {title}"), None)
    if start is None:
        return None
    for index in range(start + 1, len(lines)):
        line = lines[index].strip()
        if line.startswith("#"):
            return None
        if line.startswith("|"):
            columns = _split_row(line)
            if (key not in columns or index + 1 >= len(lines)
                    or not lines[index + 1].strip().startswith("|")):
                return None
            end = index + 2
            while end < len(lines) and lines[end].strip().startswith("|"):
                end += 1
            return columns, index + 2, end
    return None


def _acquisition_rows(project_root):
    """Map (source, acquisition_id) to the Retained copy cell of each Acquisitions row, else None."""
    try:
        text = (Path(project_root) / "foundation/sources.md").read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    lines = text.split("\n")
    table = _table(lines, "Acquisitions", "Acquisition ID")
    if table is None:
        return None
    columns, first, end = table
    rows = {}
    for line in lines[first:end]:
        row = dict(zip(columns, _split_row(line)))
        rows[(_plain(row.get("Source ID", "")), _plain(row["Acquisition ID"]))] = row.get("Retained copy", "")
    return rows


def _mark_source_acquired(lines, source):
    """Set the source's Status from candidate to acquired; return its status or `missing`."""
    table = _table(lines, "Sources", "Source ID")
    if table is None:
        return "missing"
    columns, first, end = table
    for index in range(first, end):
        cells = _split_row(lines[index])
        row = dict(zip(columns, cells))
        if _plain(row["Source ID"]) != source:
            continue
        status = row.get("Status", "")
        if _plain(status) == "candidate":
            cells[columns.index("Status")] = status.replace("candidate", "acquired")
            lines[index] = _join_row(cells)
            return "acquired"
        return _plain(status) or "unrecorded"
    return "missing"


def record_acquisition(project_root: str | Path, acquisition_dir: str | Path,
                       retained_copy: str | Path | None = None) -> dict:
    """Write a completed acquisition's row in foundation/sources.md from its provenance.

    retained_copy is a destination retain() verified with no discrepancies, or None for
    `this checkout only`. An existing row is never rewritten, except that a verified copy
    fills a Retained copy cell that is empty or `this checkout only`. A Sources row with
    status `candidate` becomes `acquired`. Returns {"row": "added" | "updated" |
    "unchanged", "source_status": <status> | "missing"}; raises LookupError when the
    Acquisitions table is missing.
    """
    root = Path(project_root)
    directory = _under(root, acquisition_dir)
    provenance = _complete_provenance(directory)
    source, acquisition_id = provenance["source"], provenance["acquisition_id"]
    path = root / "foundation/sources.md"
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise LookupError(f"Missing {path}") from None
    lines = text.split("\n")
    table = _table(lines, "Acquisitions", "Acquisition ID")
    if table is None:
        raise LookupError(f"No Acquisitions table in {path}")
    columns, first, end = table
    retained = f"`{_cell(retained_copy)}`" if retained_copy else _NO_RETAINED_COPY
    outcome = "added"
    for index in range(first, end):
        cells = _split_row(lines[index])
        row = dict(zip(columns, cells))
        if (_plain(row["Acquisition ID"]) != acquisition_id
                or _plain(row.get("Source ID", source)) != source):
            continue
        outcome = "unchanged"
        if retained_copy and "Retained copy" in columns and _unretained(row.get("Retained copy", "")):
            cells += [""] * (len(columns) - len(cells))
            cells[columns.index("Retained copy")] = retained
            lines[index] = _join_row(cells)
            outcome = "updated"
        break
    else:
        files = provenance["files"]
        check = (f"{len(files)} file{'s' * (len(files) != 1)}, "
                 f"{sum(file['bytes'] for file in files)} bytes; SHA-256 per file in provenance.json")
        counted = [f"{file['path']} {file['records']}" for file in files if file["records"] is not None]
        if counted:
            check += "; records: " + ", ".join(counted)
        request = provenance["request"]
        notes = provenance["notes"]
        values = {
            "Acquisition ID": acquisition_id,
            "Source ID": source,
            "Acquired at": provenance["completed_at"],
            "Source version, query, or request": _cell(
                request if isinstance(request, str) else json.dumps(request, ensure_ascii=False)),
            "Landed directory": f"`{_cell(_relative(root, directory))}/`",
            "Retained copy": retained,
            "Integrity or completeness check": _cell(check),
            "Notes": _cell(notes) if isinstance(notes, str) else "",
        }
        lines.insert(end, _join_row([values.get(column, "") for column in columns]))
    status = _mark_source_acquired(lines, source)
    if "\n".join(lines) != text:
        path.write_text("\n".join(lines), encoding="utf-8")
    return {"row": outcome, "source_status": status}


# Command-line entry points, run as `python3 src/awb.py land|retain|publish ...`. Each prints
# one line of compact JSON and returns 0 when done, 1 when something it attempted failed
# (named in the JSON), or 2 for unusable arguments.

def _print(value):
    print(json.dumps(value, ensure_ascii=False, default=str))


def _relative(root, path):
    try:
        return Path(path).resolve().relative_to(Path(root).resolve()).as_posix()
    except ValueError:
        return str(path)


def _landed_location(project_root):
    """Return (reachable location, None) from README's `Landed data is kept at`, else (None, why)."""
    import re
    root = Path(project_root)
    try:
        readme = (root / "README.md").read_text(encoding="utf-8")
    except FileNotFoundError:
        readme = ""
    values = re.findall(r"^Landed data is kept at:[ \t]*(.*?)[ \t]*$", readme, re.M)
    value = _plain(values[0]) if len(values) == 1 else ""
    if len(values) > 1:
        return None, {"skipped": "unrecorded", "warning": "README repeats the Landed data is kept at line"}
    if value.lower() in {"", "not yet recorded"}:
        return None, {"skipped": "unrecorded",
                      "warning": "ask where landed data is kept, record it on README's Landed data "
                                 "is kept at line, then run python3 src/awb.py retain"}
    if value.lower() in {"none", "none chosen"}:
        return None, {"skipped": "none chosen", "warning": "originals exist only in this checkout"}
    # A URI or prose names storage reached another way; never guess a network call.
    if "://" in value or not value.startswith(("/", "~", "./", "../")):
        return None, {"skipped": "not a filesystem path", "location": value,
                      "warning": "copy the acquisition directory there, then record the "
                                 "verified destination in its Retained copy cell"}
    location = Path(value).expanduser()
    location = location if location.is_absolute() else (root / location).resolve()
    if not location.is_dir():
        return None, {"skipped": "unreachable", "location": str(location)}
    return location, None


def _settle(root, directory, location, skipped):
    """Retain one acquisition when a location is reachable, then write its ledger row."""
    report = {"acquisition": _relative(root, directory) + "/"}
    succeeded = True
    verified = None
    if location is None:
        report["retention"] = skipped
    else:
        try:
            result = retain(root, directory, location)
        except (OSError, ValueError) as error:
            result = {"error": f"{type(error).__name__}: {error}"}
        if result.get("discrepancies") == []:
            verified = result["destination"]
        else:
            succeeded = False
        if len(result.get("discrepancies", [])) > 10:
            result["discrepancies"] = result["discrepancies"][:10] + [
                f"and {len(result['discrepancies']) - 10} more"]
        report["retention"] = result
    try:
        report["ledger"] = record_acquisition(root, directory, verified)
    except (LookupError, ValueError, OSError) as error:
        report["ledger"] = {"row": "not written", "error": str(error)}
        succeeded = False
    return report, succeeded


def cli_land(root: Path, argv: list[str]) -> int:
    """land <source> <acquisition-id> <file>... [--request TEXT] [--records NAME=COUNT ...] [--notes TEXT]"""
    import argparse
    parser = argparse.ArgumentParser(
        prog="awb.py land",
        description="Copy files byte for byte into data/raw/<source>/<acquisition-id>/, retain "
                    "the acquisition at README's Landed data location, and record its Acquisitions row.")
    parser.add_argument("source")
    parser.add_argument("acquisition_id", metavar="acquisition-id")
    parser.add_argument("files", nargs="+", metavar="file",
                        help="file or directory to copy under its own name; relative to the current directory")
    parser.add_argument("--request", help="source version, query, or request (default: the copied paths)")
    parser.add_argument("--records", nargs="+", action="extend", default=[], metavar="NAME=COUNT",
                        help="record count of a landed file, by its path inside the acquisition")
    parser.add_argument("--notes")
    args = parser.parse_args(argv)
    records = {}
    for item in args.records:
        name, _, count = item.rpartition("=")
        if not name or not count.isdigit():
            parser.error(f"--records expects NAME=COUNT, got {item!r}")
        records[name] = int(count)
    inputs = [Path(name).expanduser().resolve() for name in args.files]
    missing = [str(path) for path in inputs if not path.exists()]
    if missing:
        parser.error("no such file: " + ", ".join(missing))
    names = [path.name for path in inputs]
    if len(set(names)) != len(names) or "provenance.json" in names:
        parser.error("inputs need distinct names other than provenance.json")

    def fetch(output):
        for path in inputs:
            if path.is_dir():
                shutil.copytree(path, output / path.name, copy_function=shutil.copyfile)
            else:
                shutil.copyfile(path, output / path.name)

    request = args.request or "copied from " + ", ".join(map(str, inputs))
    try:
        directory = land(root, args.source, args.acquisition_id, fetch, request=request,
                         records=records or None, notes=args.notes)
    except (OSError, ValueError) as error:
        partial = Path(root) / "data/raw" / args.source / f"{args.acquisition_id}.partial"
        _print({"landed": False, "error": f"{type(error).__name__}: {error}",
                "partial": _relative(root, partial) if partial.is_dir() else None})
        return 1
    files = json.loads((directory / "provenance.json").read_text(encoding="utf-8"))["files"]
    report, succeeded = _settle(root, directory, *_landed_location(root))
    _print({"landed": report.pop("acquisition"), "files": len(files),
            "bytes": sum(file["bytes"] for file in files), **report})
    return 0 if succeeded else 1


def cli_retain(root: Path, argv: list[str]) -> int:
    """retain: retain and record every completed acquisition lacking a retained copy or a row."""
    import argparse
    argparse.ArgumentParser(
        prog="awb.py retain",
        description="Retain every completed acquisition under data/raw/ whose Acquisitions row lacks "
                    "a retained copy, and write missing Acquisitions rows.").parse_args(argv)
    location, skipped = _landed_location(root)
    rows = _acquisition_rows(root) or {}
    raw = Path(root) / "data/raw"
    reports, succeeded, retained, unretained = [], True, 0, 0
    for directory in sorted(raw.glob("*/*")) if raw.is_dir() else []:
        try:
            _complete_provenance(directory)
        except (ValueError, OSError):
            continue
        cell = rows.get((directory.parent.name, directory.name))
        if cell is not None and not _unretained(cell):
            retained += 1
            continue
        if cell is not None and location is None:
            unretained += 1
            continue
        report, ok = _settle(root, directory, location, skipped)
        if location is None:
            # The skip reason is reported once, under location.
            del report["retention"]
        reports.append(report)
        succeeded = succeeded and ok
    _print({"location": str(location) if location else skipped, "acted_on": reports,
            "already_retained": retained, "still_this_checkout_only": unretained})
    return 0 if succeeded else 1


def cli_publish(root: Path, argv: list[str]) -> int:
    """publish <dataset> <publication-id> --from <acquisition-dir>... --sql <select.sql> [--check <check.sql>]"""
    import argparse
    import re
    parser = argparse.ArgumentParser(
        prog="awb.py publish",
        description="Write a SQL select over landed files as data/parquet/<dataset>/<publication-id>/"
                    "<dataset>.parquet, check it, and publish it with publication.json.")
    parser.add_argument("dataset")
    parser.add_argument("publication_id", metavar="publication-id")
    parser.add_argument("--from", dest="acquisitions", nargs="+", required=True, metavar="ACQUISITION_DIR",
                        help="completed acquisition directory the select reads, project-relative")
    parser.add_argument("--sql", required=True, help="file holding one SELECT over the landed files")
    parser.add_argument("--check", help="file holding a query over the view `publication`; any row refuses")
    parser.add_argument("--notes")
    args = parser.parse_args(argv)
    root = Path(root)
    queries = {}
    for name in ("sql", "check"):
        if getattr(args, name) is None:
            continue
        path = _under(root, getattr(args, name))
        if not path.is_file():
            parser.error(f"no such SQL file: {path}")
        queries[name] = (path, path.read_text(encoding="utf-8").strip().rstrip(";").strip())
    # publication.json lists --from as the inputs, so it must match what the select reads.
    named = set()
    for acquisition in args.acquisitions:
        try:
            provenance = _complete_provenance(_under(root, acquisition))
        except (ValueError, OSError) as error:
            parser.error(str(error))
        named.add(f"data/raw/{provenance['source']}/{provenance['acquisition_id']}")
    read = set(re.findall(r"data/raw/[^/\s'\"]+/[^/\s'\"]+", queries["sql"][1]))
    if read != named:
        parser.error(f"--from must name exactly the acquisitions the select reads: the select reads "
                     f"{sorted(read)}, --from names {sorted(named)}")
    try:
        import duckdb
    except ImportError:
        parser.exit(2, "publish needs the duckdb package\n")
    if "," in str(root.resolve()):
        # file_search_path is a comma-separated list with no escape for a comma.
        parser.exit(2, f"publish cannot use a project root containing a comma: {root.resolve()}\n")
    notes = {"select": _relative(root, queries["sql"][0]), "select_sha256": _sha256(queries["sql"][0]),
             "check": None, "check_sha256": None, "rows": None, "comment": args.notes}
    if "check" in queries:
        notes.update(check=_relative(root, queries["check"][0]), check_sha256=_sha256(queries["check"][0]))
    failures = {}
    connection = duckdb.connect()

    def literal(path):
        return "'" + str(path).replace("'", "''") + "'"

    def convert(directory):
        target = literal(directory / f"{args.dataset}.parquet")
        connection.execute(f"COPY ({queries['sql'][1]}) TO {target} (FORMAT parquet)")
        # notes is serialized after validation, so publication.json records the count.
        notes["rows"] = connection.execute(f"SELECT count(*) FROM read_parquet({target})").fetchone()[0]

    def validate(directory):
        if not notes["rows"]:
            raise ValueError("The select returned no rows")
        if "check" not in queries:
            return
        connection.execute("CREATE VIEW publication AS SELECT * FROM read_parquet("
                           f"{literal(directory / f'{args.dataset}.parquet')})")
        result = connection.execute(queries["check"][1])
        if result.description is None:
            raise ValueError("The check must be a query returning failing rows")
        columns = [column[0] for column in result.description]
        rows = result.fetchall()
        if rows:
            failures.update(failing_rows=len(rows), first=[dict(zip(columns, row)) for row in rows[:20]])
            raise ValueError(f"The check returned {len(rows)} failing rows")

    try:
        connection.execute("SET file_search_path = ?", [str(root.resolve())])
        final = publish(root, args.dataset, args.publication_id, convert,
                        acquisitions=args.acquisitions, validate=validate, notes=notes)
    except (duckdb.Error, OSError, ValueError) as error:
        partial = root / "data/parquet" / args.dataset / f"{args.publication_id}.partial"
        _print({"published": False, "error": f"{type(error).__name__}: {error}", **failures,
                "partial": _relative(root, partial) if partial.is_dir() else None})
        return 1
    finally:
        connection.close()
    publication = json.loads((final / "publication.json").read_text(encoding="utf-8"))
    location = _relative(root, final) + "/"
    quality = f"`{notes['check']}` returns no rows" if notes["check"] else "nonzero row count"
    result = {
        "published": location, "rows": notes["rows"],
        "bytes": sum(file["bytes"] for file in publication["files"]),
        "inputs": sorted(named), "conversion_commit": publication["conversion_commit"],
        # Grain and availability need judgment; the agent completes and places the row.
        "catalog_row": _join_row([_cell(args.dataset), "Parquet publication", "",
                                  ", ".join(f"`{name}/`" for name in sorted(named)),
                                  f"`{location}`", f"`{notes['select']}`", quality, ""]),
    }
    try:
        status = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--",
                                 *(str(path) for path, _ in queries.values())],
                                check=False, capture_output=True, text=True)
        if status.returncode == 0 and status.stdout.strip():
            result["warning"] = ("conversion SQL is uncommitted; conversion_commit does not hold it, "
                                 "its sha256 is in publication.json notes")
    except FileNotFoundError:
        pass
    _print(result)
    return 0


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
