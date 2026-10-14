"""Land, publish, retain, and open analytical sessions for a workbench.

Copy this file to src/preparation/landing.py and import the project copy. src/awb.py runs
its cli_* functions as the land, retain, publish, and sql commands.

data/raw/<source>/<acquisition-id>/provenance.json:
    {source, acquisition_id, request, started_at, completed_at, status,
     files: [{path, bytes, sha256, records}], notes}
    status is "complete"; records is an integer or null.
data/parquet/<dataset>/<publication-id>/publication.json:
    {dataset, publication_id,
     inputs: [{source, acquisition_id, files: [{path, sha256}]}],
     conversion_commit, converted_at, files: [{path, bytes, sha256}],
     checks: [{name, outcome, detail}], notes}
    conversion_commit is git HEAD or "uncommitted". checks lists the dataset's declared checks
    from foundation/datasets.toml, then `validate` when a validate callable ran; every outcome
    is "pass", because a failure refuses publication.
Paths are sorted POSIX paths relative to their acquisition or publication.
"""

import argparse
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
from collections.abc import Callable, Sequence
from datetime import date, datetime, timezone
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


# Declared dataset checks: [datasets.<name>.checks] in foundation/datasets.toml, run by publish()
# against every publication of that dataset. The shipped foundation/datasets.toml documents the keys.

DATASETS = "foundation/datasets.toml"
CHECK_KEYS = ("columns", "types", "not_null", "key", "unique", "accepted_values", "range", "row_count")


class ChecksFailed(ValueError):
    """A declared check failed; checks holds every declared check's {name, outcome, detail}."""

    def __init__(self, checks):
        self.checks = checks
        failed = [f"{check['name']} ({check['detail'].rstrip('.')})"
                  for check in checks if check["outcome"] == "fail"]
        super().__init__("Declared checks failed: " + "; ".join(failed))


def _toml():
    try:
        import tomllib
    except ImportError:  # Python 3.10
        import tomli as tomllib
    return tomllib


def _names(value):
    return isinstance(value, list) and all(isinstance(name, str) and name for name in value)


def _number_or_date(bound):
    """A range bound: a number other than NaN, or a TOML date or date-time."""
    if isinstance(bound, float):
        return not math.isnan(bound)
    return isinstance(bound, (int, date)) and not isinstance(bound, bool)


def _in_utc(bound):
    """bound, a local date-time taken as UTC, as the checks' UTC connection compares it."""
    return bound.replace(tzinfo=timezone.utc) if isinstance(bound, datetime) and bound.tzinfo is None else bound


def _bounds(value, accepts):
    """{min, max}, either optional, each accepted, with min no greater than max."""
    if not (isinstance(value, dict) and value and set(value) <= {"min", "max"}
            and all(accepts(bound) for bound in value.values())):
        return False
    try:
        return "min" not in value or "max" not in value or _in_utc(value["min"]) <= _in_utc(value["max"])
    except TypeError:  # bounds of different kinds, such as a number and a date
        return False


def _by_column(value, accepts):
    """{column: entry}, each column named and each entry accepted."""
    return isinstance(value, dict) and all(column and accepts(entry) for column, entry in value.items())


def _duckdb():
    try:
        import duckdb
    except ImportError as error:
        raise ImportError("declared checks need the duckdb package") from error
    return duckdb


def _toml_key(name):
    """name as a TOML key: bare when it can be, else quoted."""
    return name if name and all(c.isascii() and (c.isalnum() or c in "_-") for c in name) else json.dumps(name)


def _nested_checks(value, path=()):
    """The key path to the first checks table nested in value, or None."""
    if not isinstance(value, dict):
        return None
    if "checks" in value:
        return path
    for key, inner in value.items():
        found = _nested_checks(inner, path + (key,))
        if found is not None:
            return found
    return None


SHAPES = {
    "columns": lambda v: _names(v) and v,
    "types": lambda v: _by_column(v, lambda t: isinstance(t, str) and t.strip() and ";" not in t),
    "not_null": _names,
    "key": lambda v: _names(v) and v and len(set(v)) == len(v),
    "unique": lambda v: isinstance(v, list) and all(
        (isinstance(item, str) and item) or (_names(item) and item and len(set(item)) == len(item))
        for item in v),
    "accepted_values": lambda v: _by_column(v, lambda values: isinstance(values, list) and values),
    "range": lambda v: _by_column(v, lambda bounds: _bounds(bounds, _number_or_date)),
    "row_count": lambda v: _bounds(v, lambda bound: type(bound) is int and bound >= 0),
}


def _planned(spec):
    """[(name, kind, arguments)] for each check spec declares, in CHECK_KEYS order."""
    planned = []
    for key in CHECK_KEYS:
        value = spec.get(key)
        if value is None:
            continue
        if key == "columns":
            planned.append(("columns", key, (value,)))
        elif key == "types":
            planned += [(f"types:{column}", key, (column, declared)) for column, declared in value.items()]
        elif key == "not_null":
            planned += [(f"not_null:{column}", key, (column,)) for column in value]
        elif key == "key":
            planned.append((f"key:{','.join(value)}", key, (value,)))
        elif key == "unique":
            for item in value:
                columns = [item] if isinstance(item, str) else item
                planned.append((f"unique:{','.join(columns)}", key, (columns,)))
        elif key == "accepted_values":
            planned += [(f"accepted_values:{column}", key, (column, accepted)) for column, accepted in value.items()]
        elif key == "range":
            planned += [(f"range:{column}", key, (column, bounds)) for column, bounds in value.items()]
        else:
            planned.append(("row_count", key, (value,)))
    return planned


def _validated(name, entry):
    """[datasets.<name>]'s checks table, else ValueError naming the key at fault."""
    where = f"{DATASETS} [datasets.{_toml_key(name)}]"
    if not isinstance(entry, dict) or set(entry) - {"checks"} or not isinstance(entry.get("checks", {}), dict):
        nested = _nested_checks({key: value for key, value in entry.items() if key != "checks"}) \
            if isinstance(entry, dict) else None
        if nested:  # [datasets.orders.v1.checks] nests v1 under orders; it declares nothing for orders.v1
            dotted = ".".join((name,) + nested)
            raise ValueError(f"{where} holds only a checks table; to declare checks for the dataset {dotted}, "
                             f"quote its name: [datasets.{json.dumps(dotted)}.checks]")
        raise ValueError(f"{where} holds only a checks table")
    spec = entry.get("checks", {})
    for key, value in spec.items():
        if key not in SHAPES:
            raise ValueError(f"{where}: unknown check {key}; use {', '.join(CHECK_KEYS)}")
        if not SHAPES[key](value):
            raise ValueError(f"{where}: checks.{key} is malformed; see the comments in the shipped {DATASETS}")
    names = [check for check, _, _ in _planned(spec)]
    repeated = sorted({check for check in names if names.count(check) > 1})
    if repeated:  # such as unique = ["a,b", ["a", "b"]]; a name must identify one check
        raise ValueError(f"{where}: more than one declared check is named {', '.join(repeated)}; "
                         "declare each check once (a check's name joins its columns with commas)")
    column_sets = [frozenset(arguments[0]) for _, kind, arguments in _planned(spec) if kind == "unique"]
    repeated = sorted({",".join(sorted(columns)) for columns in column_sets if column_sets.count(columns) > 1})
    if repeated:  # unique = [["a", "b"], ["b", "a"]] declares one check under two names
        raise ValueError(f"{where}: checks.unique declares the columns {'; '.join(repeated)} more than once, "
                         "in different orders; declare each check once")
    return spec


def declared_checks(project_root: str | Path, dataset: str) -> dict:
    """Return [datasets.<dataset>.checks] from foundation/datasets.toml, {} when none are declared.

    Raises ValueError when any dataset's declaration is malformed, naming the key at fault.
    """
    path = Path(project_root) / DATASETS
    if not path.is_file():
        return {}
    try:
        tomllib = _toml()
    except ImportError as error:
        raise ImportError(f"reading {DATASETS} needs Python 3.11 or the tomli package") from error
    try:
        document = tomllib.loads(path.read_text(encoding="utf-8"))
    except ValueError as error:
        raise ValueError(f"{DATASETS}: {error}") from error
    if set(document) - {"datasets"}:  # such as [dataset.<name>.checks], which would declare nothing
        raise ValueError(f"{DATASETS}: unknown table {', '.join(sorted(set(document) - {'datasets'}))}; "
                         "declare checks under [datasets.<name>.checks]")
    datasets = document.get("datasets", {})
    if not isinstance(datasets, dict):
        raise ValueError(f"{DATASETS}: datasets must be a table of [datasets.<name>] tables")
    # Validate every entry: a mistyped one may be meant for this dataset, such as an unquoted dotted name.
    specs = {name: _validated(name, entry) for name, entry in datasets.items()}
    return specs.get(dataset, {})


def _quote(name):
    return '"' + name.replace('"', '""') + '"'


def _literal(value):
    return "'" + str(value).replace("'", "''") + "'"


def _span(bounds):
    return f"[{bounds.get('min', '-inf')}, {bounds.get('max', 'inf')}]"


def _run_checks(directory, spec):
    """Run spec's checks over the Parquet files under directory; return [{name, outcome, detail}].

    columns and types hold in every Parquet file, since a reader takes the first file's schema.
    Temporal values compare in UTC. When the files cannot be read, every check fails.
    """
    duckdb = _duckdb()
    planned = _planned(spec)

    def unread(detail):
        return [{"name": name, "outcome": "fail", "detail": detail} for name, _, _ in planned]

    paths = [path for path in _files(directory) if path.endswith(".parquet")]
    if not paths:
        return unread("The publication holds no Parquet file.")
    connection = duckdb.connect()
    try:
        # DuckDB takes its zone from the host; a date or date-time compared with the other kind of
        # timestamp casts through it, so pin it for an outcome that is the same on every machine.
        connection.execute("SET TimeZone = 'UTC'")
        schemas = []
        for path in paths:
            try:
                schemas.append(dict(connection.execute(
                    "SELECT column_name, column_type FROM (DESCRIBE SELECT * FROM read_parquet("
                    + _literal(directory / path) + "))").fetchall()))
            except duckdb.Error as error:  # name the file and the error's kind, never DuckDB's message
                return unread(f"{path} could not be read as Parquet ({type(error).__name__}).")
        try:
            connection.execute("CREATE VIEW awb_publication AS SELECT * FROM read_parquet(["
                               + ", ".join(_literal(directory / path) for path in paths) + "])")
            rows = connection.execute("SELECT count(*) FROM awb_publication").fetchone()[0]
        except duckdb.Error as error:
            return unread(f"The Parquet files could not be read together ({type(error).__name__}).")

        def count(condition, parameters=()):
            return connection.execute(f"SELECT count(*) FROM awb_publication WHERE {condition}",
                                      list(parameters)).fetchone()[0]

        def repeats(columns, where="true"):
            listed = ", ".join(map(_quote, columns))
            return connection.execute(f"SELECT coalesce(sum(n - 1), 0) FROM (SELECT count(*) AS n "
                                      f"FROM awb_publication WHERE {where} GROUP BY {listed})").fetchone()[0]

        def columns_present(columns):
            lacking = {column: sum(column not in schema for schema in schemas) for column in columns}
            missing = [column if files == len(schemas) else f"{column} (from {files} of {len(schemas)} Parquet files)"
                       for column, files in lacking.items() if files]
            return f"Missing column{'s' * (len(missing) > 1)}: {', '.join(missing)}." if missing else None

        # Each measure returns (failure or None, pass detail); every detail is counts, never values.
        def measure_columns(columns):
            return columns_present(columns), f"All {len(columns)} declared columns present."

        def measure_type(column, declared):
            missing = columns_present([column])
            if missing:
                return missing, ""
            try:
                expected = connection.execute(f"SELECT typeof(CAST(NULL AS {declared}))").fetchone()[0]
            except duckdb.Error:
                return f"Declared type {declared} is not a DuckDB type.", ""
            wrong = [schema[column] for schema in schemas if schema[column] != expected]
            if not wrong:
                return None, f"{column} is {expected}."
            files = "" if len(wrong) == len(schemas) else f" in {len(wrong)} of {len(schemas)} Parquet files"
            return f"{column} is {' or '.join(sorted(set(wrong)))}{files}, declared {expected}.", ""

        def measure_not_null(column):
            missing = columns_present([column])
            if missing:
                return missing, ""
            nulls = count(f"{_quote(column)} IS NULL")
            return (f"{nulls} of {rows} rows are null." if nulls else None), f"No nulls in {rows} rows."

        def measure_key(columns):
            missing = columns_present(columns)
            if missing:
                return missing, ""
            nulls = count(" OR ".join(f"{_quote(column)} IS NULL" for column in columns))
            repeated = repeats(columns, " AND ".join(f"{_quote(column)} IS NOT NULL" for column in columns))
            failures = ([f"{nulls} of {rows} rows have a null key column"] if nulls else []) + (
                [f"{repeated} of {rows} rows repeat a key"] if repeated else [])
            return ("; ".join(failures) + "." if failures else None), f"{rows} rows, each key complete and unique."

        def measure_unique(columns):
            missing = columns_present(columns)
            if missing:
                return missing, ""
            repeated = repeats(columns, " AND ".join(f"{_quote(column)} IS NOT NULL" for column in columns))
            return (f"{repeated} of {rows} rows repeat a value." if repeated else None), (
                f"No repeated values in {rows} rows; nulls are not compared.")

        def measure_accepted(column, accepted):
            missing = columns_present([column])
            if missing:
                return missing, ""
            outside = count(f"{_quote(column)} IS NOT NULL AND NOT list_contains(?, {_quote(column)})",
                            [accepted])
            return (f"{outside} of {rows} rows hold a value outside the {len(accepted)} accepted."
                    if outside else None), f"Every non-null value is one of the {len(accepted)} accepted."

        def measure_range(column, bounds):
            missing = columns_present([column])
            if missing:
                return missing, ""
            tests = [(f"{_quote(column)} < ?", bounds["min"])] if "min" in bounds else []
            tests += [(f"{_quote(column)} > ?", bounds["max"])] if "max" in bounds else []
            outside = count(" OR ".join(test for test, _ in tests), [bound for _, bound in tests])
            return (f"{outside} of {rows} rows fall outside {_span(bounds)}." if outside else None), (
                f"No value outside {_span(bounds)} in {rows} rows.")

        def measure_rows(bounds):
            bounds = {"min": 0, **bounds}  # a row count's floor is 0
            inside = bounds["min"] <= rows <= bounds.get("max", rows)
            return (None if inside else f"{rows} rows, outside {_span(bounds)}."), f"{rows} rows, within {_span(bounds)}."

        measures = {"columns": measure_columns, "types": measure_type, "not_null": measure_not_null,
                    "key": measure_key, "unique": measure_unique, "accepted_values": measure_accepted,
                    "range": measure_range, "row_count": measure_rows}
        checks = []
        for name, kind, arguments in planned:
            try:
                failure, detail = measures[kind](*arguments)
            except duckdb.Error as error:
                # DuckDB's message can quote a source value; name only the error's kind.
                failure = f"The check could not run ({type(error).__name__})"
                if name.startswith(("accepted_values:", "range:")):  # declared values the column can't compare with
                    failure += "; compare its declared values with the column's type"
                failure += "."
            checks.append({"name": name, "outcome": "fail" if failure else "pass",
                           "detail": failure or detail})
        return checks
    finally:
        connection.close()


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
    """Convert completed acquisitions, check and validate the output, then write publication.json
    and rename it. The dataset's declared checks run first; any failure raises ChecksFailed."""
    _check_name(dataset)
    _check_name(publication_id)
    root = Path(project_root)
    spec = declared_checks(root, dataset)  # a malformed declaration refuses before any output
    if _planned(spec):
        _duckdb()  # and so does a missing duckdb
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
    checks = _run_checks(partial, spec) if _planned(spec) else []
    if any(check["outcome"] == "fail" for check in checks):
        raise ChecksFailed(checks)
    if validate is not None:
        outcome = validate(partial)
        if outcome is False:
            raise ValueError("Publication validation returned False")
        detail = " ".join(outcome.split()) if isinstance(outcome, str) else ""
        checks.append({"name": "validate", "outcome": "pass",
                       "detail": detail or "The validate callable passed."})
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
        "checks": checks,
        "notes": notes,
    })


def retain(project_root: str | Path, acquisition_dir: str | Path,
           location: str | Path) -> dict:
    """Copy an acquisition to the retained location without overwriting, then compare checksums.

    Returns {destination, copied, conflict, matched, discrepancies}: matched when the
    destination holds the same files and checksums, conflict when an existing destination differs.
    """
    root = Path(project_root)
    directory = _under(root, acquisition_dir).resolve()
    raw = (root / "data/raw").resolve()
    if directory.parent.parent != raw:
        raise ValueError(f"Not a <source>/<acquisition-id> directory under {raw}: {directory}")
    _complete_provenance(directory)
    _check_name(directory.parent.name)
    _check_name(directory.name)
    destination = Path(location) / "data/raw" / directory.parent.name / directory.name
    existed = destination.exists() or destination.is_symlink()
    if not existed:
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
    # An existing destination conflicts only when it differs; an identical one matches.
    matched = not discrepancies and destination.is_dir()
    return {"destination": str(destination), "copied": not existed,
            "conflict": existed and not matched, "matched": matched,
            "discrepancies": discrepancies}


# Ledger rows. Helpers write the facts they produce into foundation/sources.md themselves;
# columns that need human judgment (Restrictions, Sources-table descriptions) stay as they are.

_NO_RETAINED_COPY = "this checkout only"

# foundation/sources.md as awb-init installs it; record_acquisition writes it when absent.
SOURCES_TEMPLATE = """\
# Source register

Record source provenance, relevance, and fitness here. Add a source when it becomes a real candidate.

## Sources

| Source ID | System or provider | Contents and grain | Owner or contact | Acquisition method | Relevance and fitness | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |

Status is one of:

- `candidate`: identified as possibly relevant; no acquisition has completed.
- `acquired`: at least one acquisition has completed and the source has not been rejected.
- `rejected`: assessed as irrelevant or unfit; give the reason under Relevance and fitness and stop preparing it.

Note failed acquisition attempts in the source's Notes. Use stable source IDs in the catalog, quality record, and investigation records.

## Acquisitions

`land` and `retain` write these rows, one per completed acquisition directory under `data/raw/<source>/<acquisition-id>/` unless the project has its own layout. Fill Restrictions yourself, and update Retained copy once a manual copy is verified.

| Acquisition ID | Source ID | Acquired at | Source version, query, or request | Landed directory | Retained copy | Integrity or completeness check | Restrictions | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
"""


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
    status `candidate` becomes `acquired`. A missing foundation/sources.md is written from
    SOURCES_TEMPLATE with the row. Returns {"row": "added" | "updated" | "unchanged",
    "source_status": <status> | "missing"}, plus "created": True when the file was written
    from the template; raises LookupError when an existing file has no Acquisitions table.
    """
    root = Path(project_root)
    directory = _under(root, acquisition_dir)
    provenance = _complete_provenance(directory)
    source, acquisition_id = provenance["source"], provenance["acquisition_id"]
    path = root / "foundation/sources.md"
    created = not (path.exists() or path.is_symlink())
    text = SOURCES_TEMPLATE if created else path.read_text(encoding="utf-8")
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
    if created:
        path.parent.mkdir(parents=True, exist_ok=True)
    if created or "\n".join(lines) != text:
        path.write_text("\n".join(lines), encoding="utf-8")
    return {"row": outcome, "source_status": status, **({"created": True} if created else {})}


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
    """land <source> <acquisition-id> <file>... [--request TEXT] [--records NAME=COUNT]... [--notes TEXT]"""
    import argparse
    parser = argparse.ArgumentParser(
        prog="awb.py land",
        description="Copy files byte for byte into data/raw/<source>/<acquisition-id>/, retain "
                    "the acquisition at README's Landed data location, and record its Acquisitions row.",
        epilog="Retention runs when README's `Landed data is kept at` line names a reachable filesystem "
               "path. The Acquisitions row goes in foundation/sources.md, created from the template when "
               "absent, and sets a candidate source to acquired; fill its Restrictions yourself. Prints "
               "one JSON line: landed, files, bytes, retention (the retained copy's destination, copied, "
               "conflict, matched, and discrepancies, or skipped with a warning to act on), and ledger "
               "(row, source_status, and created when sources.md was created; missing means the source "
               "still needs its Sources row). Exit 1 means the files landed but retention or the "
               "row failed; exit 2 means unusable arguments, with nothing landed.")
    parser.add_argument("source", help="source directory name under data/raw/ (one name, not ending "
                                       "in .partial)")
    parser.add_argument("acquisition_id", metavar="acquisition-id",
                        help="new acquisition directory name under data/raw/<source>/")
    parser.add_argument("files", nargs="+", metavar="file",
                        help="file or directory to copy under its own name; relative to the current directory")
    parser.add_argument("--request", help="source version, query, or request (default: the copied paths)")
    parser.add_argument("--records", action="append", default=[], metavar="NAME=COUNT",
                        help="record count of a landed file, by its path inside the acquisition; "
                             "repeat the flag for each file")
    parser.add_argument("--notes", help="note recorded in the Acquisitions row")
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
                    "a retained copy, and write missing Acquisitions rows.",
        epilog="Run it after a library land() and whenever README's `Landed data is kept at` line is "
               "first recorded or changed; without a reachable filesystem location it only writes "
               "missing rows. Copies never overwrite. Prints one JSON line: location (or the skip "
               "reason), acted_on (each acquisition's retention result, with matched when the destination "
               "holds an identical copy, and its ledger row outcome, with created when sources.md was "
               "created), already_retained, and still_this_checkout_only. Report every conflict and "
               "discrepancy. Exit 1 when a retention or row failed.").parse_args(argv)
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
    """publish <dataset> <publication-id> --from <acquisition-dir> [--from ...] --sql <select.sql> [--check <check.sql>]"""
    import argparse
    import re
    parser = argparse.ArgumentParser(
        prog="awb.py publish",
        description="Write a SQL select over landed files as data/parquet/<dataset>/<publication-id>/"
                    "<dataset>.parquet, check it, and publish it with publication.json.",
        epilog="The dataset's checks declared in foundation/datasets.toml run first, then --check; "
               "publication.json records each outcome under checks. Commit the SQL first so "
               "conversion_commit holds it; otherwise the output carries a warning. Prints one JSON line. "
               "On success: published, rows, bytes, inputs, conversion_commit, checks (the number "
               "recorded, all passed), view_sql, a canonical view definition for foundation/views/, and "
               "catalog_row, a foundation/catalog.md row to complete with grain and availability. On "
               "refusal (exit 1): published false, error, failed_checks with each failing declared "
               "check's name and detail, or failing_rows with up to 20 under first, and the partial "
               "directory left behind. A select returning no rows is refused. Needs duckdb.")
    parser.add_argument("dataset", help="dataset directory name under data/parquet/")
    parser.add_argument("publication_id", metavar="publication-id",
                        help="new publication directory name under data/parquet/<dataset>/")
    parser.add_argument("--from", dest="acquisitions", action="append", required=True,
                        metavar="ACQUISITION_DIR",
                        help="completed acquisition directory, project-relative; repeat the flag for each, "
                             "naming exactly the acquisitions the select reads")
    parser.add_argument("--sql", required=True,
                        help="file holding one SELECT that reads landed files by project-relative path, "
                             "such as read_csv('data/raw/<source>/<acquisition-id>/<file>.csv')")
    parser.add_argument("--check", help="file holding a query over the view `publication` (landed files "
                                        "are readable too); any returned row refuses publication")
    parser.add_argument("--notes", help="comment recorded in publication.json")
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
            return f"The select returned {notes['rows']} rows."
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
        return f"The select returned {notes['rows']} rows; {notes['check']} returned none."

    try:
        connection.execute("SET file_search_path = ?", [str(root.resolve())])
        final = publish(root, args.dataset, args.publication_id, convert,
                        acquisitions=args.acquisitions, validate=validate, notes=notes)
    except (duckdb.Error, OSError, ValueError, ImportError) as error:
        if isinstance(error, ChecksFailed):
            failures["failed_checks"] = [{"name": check["name"], "detail": check["detail"]}
                                         for check in error.checks if check["outcome"] == "fail"]
        partial = root / "data/parquet" / args.dataset / f"{args.publication_id}.partial"
        _print({"published": False, "error": f"{type(error).__name__}: {error}", **failures,
                "partial": _relative(root, partial) if partial.is_dir() else None})
        return 1
    finally:
        connection.close()
    publication = json.loads((final / "publication.json").read_text(encoding="utf-8"))
    location = _relative(root, final) + "/"
    view_name = '"' + args.dataset.replace('"', '""') + '"'
    quality = f"`{notes['check']}` returns no rows" if notes["check"] else "nonzero row count"
    declared = len(publication["checks"]) - 1  # the last check is the validate callable's
    if declared:
        verb = "pass" if declared > 1 else "passes"
        quality = f"{declared} declared check{'s' * (declared > 1)} in `{DATASETS}` {verb}; {quality}"
    result = {
        "published": location, "rows": notes["rows"],
        "bytes": sum(file["bytes"] for file in publication["files"]),
        "inputs": sorted(named), "conversion_commit": publication["conversion_commit"],
        "checks": len(publication["checks"]),
        "view_sql": (f"CREATE VIEW {view_name} AS SELECT * FROM "
                     f"read_parquet({literal(location + args.dataset + '.parquet')});"),
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


def _sql_argument(root, argument):
    """Return the text of the query file argument names, else argument itself as SQL text."""
    try:
        path = _under(root, argument)
        is_file = path.is_file()
    except (OSError, ValueError):  # SQL text can be too long, or hold a NUL, for a path
        is_file = False
    return path.read_text(encoding="utf-8") if is_file else argument


def _table_cell(value, width=80):
    text = "NULL" if value is None else str(value)
    text = text.replace("|", "\\|").replace("\r", "\\r").replace("\n", "\\n")
    return text if len(text) <= width else text[:width - 1] + "…"


def _markdown_table(header, rows):
    lines = ["| " + " | ".join(map(_table_cell, header)) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(map(_table_cell, row)) + " |" for row in rows]
    return "\n".join(lines)


def _fail(command, error):
    """Print the error, with its cause, as one line on stderr and return exit status 1."""
    message = f"{error}: {error.__cause__}" if error.__cause__ else str(error)
    print(f"{command}: {' '.join(message.split())}", file=sys.stderr)
    return 1


def cli_sql(root: Path, argv: list[str]) -> int:
    """Run a query file or SQL text in a fresh session with the foundation views loaded; every
    statement runs, and the last one's first rows print as a Markdown table with the row count."""
    parser = argparse.ArgumentParser(prog="awb.py sql", description=" ".join(cli_sql.__doc__.split()),
                                     epilog="Errors print one line on stderr and exit 1.")
    parser.add_argument("query", help="query file (absolute or project-relative) or SQL text")
    parser.add_argument("--limit", type=int, default=20, help="rows to print (default 20)")
    parser.add_argument("--out", help="write the full result to this project-relative .csv or .parquet file")
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
