"""Land, publish, retain, and open analytical sessions for a workbench.

Copy this file to src/preparation/landing.py and import the project copy. src/awb.py runs
its cli_* functions as the land, retain, publish, and sql commands.

data/raw/<source>/<acquisition-id>/provenance.json:
    {source, acquisition_id, request, started_at, completed_at, status,
     files: [{path, bytes, sha256, records, upstream}], notes}
    status is "complete"; records is an integer or null; upstream is null or
    {url, etag, last_modified, version_id}, each a string or null, as the fetch received them;
    url carries no credentials, and an http(s) url has a host, a valid port, and no space or control character.
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
import atexit
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
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


UPSTREAM_FIELDS = ("url", "etag", "last_modified", "version_id")
# Matched against a query, fragment, or path parameter name, lowercased with non-alphanumerics removed:
# api_key, access_token, client_secret, X-Amz-Signature, X-Amz-Credential, sig (Azure SAS), api_sig, jsessionid, pass, ...
CREDENTIAL_PARAMETER = re.compile(r"(key|token|secret|sig|signature|password|passwd|credentials?|session|sessionid|sessid)$"
                                  r"|^(pass|pwd|auth|authorization|sid|jwt)$")


def _check_url(path, url):
    """Refuse a URL carrying credentials, since provenance files are copied into committed evidence,
    and an http(s) URL a request cannot be sent to as recorded."""
    try:
        parts = urllib.parse.urlsplit(url)
    except ValueError:
        raise ValueError(f"upstream url of {path} is not a valid URL") from None
    # Without "//" (user:pw@host/x), urlsplit leaves the user name and password in the path.
    if "@" in (parts.netloc or parts.path.split("/", 1)[0]):
        raise ValueError(f"upstream url of {path} carries a user name or password; "
                         "record it without credentials")
    # Query and fragment parameters, and the path parameters after the first ; in a segment,
    # are each split on & or ;. Only a name=value piece is a parameter, so a #section anchor is not.
    pieces = [piece for part in (parts.query, parts.fragment) for piece in re.split(r"[&;]", part)]
    pieces += [piece for segment in parts.path.split("/") if ";" in segment
               for piece in re.split(r"[&;]", segment.split(";", 1)[1])]
    names = sorted({name for name in (urllib.parse.unquote_plus(piece.split("=", 1)[0])
                                      for piece in pieces if "=" in piece)
                    if CREDENTIAL_PARAMETER.search(re.sub(r"[^a-z0-9]", "", name.lower()))})
    if names:
        raise ValueError(f"upstream url of {path} carries credential parameters ({', '.join(names)}); "
                         "record it without credentials")
    try:
        parts.port  # raises ValueError for a port that is not a number from 0 to 65535
    except ValueError:
        raise ValueError(f"upstream url of {path} is not a valid URL: "
                         "its port is not a number from 0 to 65535") from None
    if parts.scheme in {"http", "https"} and (not parts.hostname or re.search(r"[\x00-\x20\x7f]", url)):
        raise ValueError(f"upstream url of {path} is not a valid URL: an http(s) URL needs a host "
                         "and no space or control character")


def _upstream(upstream, paths):
    """Return {path: {url, etag, last_modified, version_id}} from land()'s upstream, else raise ValueError."""
    if upstream is None:
        return {}
    if not isinstance(upstream, dict):
        raise ValueError("upstream must be a dictionary of per-file dictionaries")
    if set(upstream) - set(paths):
        raise ValueError("Upstream fields name files that were not landed")
    entries = {}
    for path, fields in upstream.items():
        if not isinstance(fields, dict) or set(fields) - set(UPSTREAM_FIELDS):
            raise ValueError(f"upstream fields of {path} must be a dictionary of {', '.join(UPSTREAM_FIELDS)}")
        if any(value is not None and (not isinstance(value, str) or not value.strip())
               for value in fields.values()):
            raise ValueError(f"upstream fields of {path} must be nonblank strings or None")
        if fields.get("url") is not None:
            _check_url(path, fields["url"])
        if any(value is not None for value in fields.values()):
            entries[path] = {name: fields.get(name) for name in UPSTREAM_FIELDS}
    return entries


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

    columns and types hold in every Parquet file, since a reader takes the first file's schema; a hive
    partition column, which no file stores, holds in the files read together (foundation/datasets.toml).
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
                # The file's stored columns: read alone, a partition column would take its type from one path.
                schemas.append(dict(connection.execute(
                    "SELECT column_name, column_type FROM (DESCRIBE SELECT * FROM read_parquet("
                    + _literal(directory / path) + ", hive_partitioning = false))").fetchall()))
            except duckdb.Error as error:  # name the file and the error's kind, never DuckDB's message
                return unread(f"{path} could not be read as Parquet ({type(error).__name__}).")
        try:
            connection.execute("CREATE VIEW awb_publication AS SELECT * FROM read_parquet(["
                               + ", ".join(_literal(directory / path) for path in paths) + "])")
            rows = connection.execute("SELECT count(*) FROM awb_publication").fetchone()[0]
            combined = connection.execute("SELECT column_name, column_type FROM (DESCRIBE awb_publication)").fetchall()
        except duckdb.Error as error:
            return unread(f"The Parquet files could not be read together ({type(error).__name__}).")
        # A hive partition column lives in the paths, so its type is the one inferred from all of them.
        partitions = {column: kind for column, kind in combined if not any(column in schema for schema in schemas)}

        def count(condition, parameters=()):
            return connection.execute(f"SELECT count(*) FROM awb_publication WHERE {condition}",
                                      list(parameters)).fetchone()[0]

        def repeats(columns, where="true"):
            listed = ", ".join(map(_quote, columns))
            return connection.execute(f"SELECT coalesce(sum(n - 1), 0) FROM (SELECT count(*) AS n "
                                      f"FROM awb_publication WHERE {where} GROUP BY {listed})").fetchone()[0]

        def columns_present(columns):
            lacking = {column: 0 if column in partitions else sum(column not in schema for schema in schemas)
                       for column in columns}
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
            held = [partitions] if column in partitions else schemas
            wrong = [schema[column] for schema in held if schema[column] != expected]
            if not wrong:
                return None, f"{column} is {expected}."
            files = "" if len(wrong) == len(held) else f" in {len(wrong)} of {len(held)} Parquet files"
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
         records: dict[str, int] | None = None,
         upstream: dict[str, dict[str, str | None]] | None = None, notes: Any = None) -> Path:
    """Fetch original files into a partial directory, then write provenance and rename it.

    records and upstream are read after fetch returns, so fetch may fill them as it writes files.
    """
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
    validators = _upstream(upstream, paths)
    files = [{**entry, "records": (records or {}).get(entry["path"]),
              "upstream": validators.get(entry["path"])}
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

Begin Relevance and fitness with the assessment's basis: `from documentation` when documentation or a schema settled it, otherwise `from landed records`. In Notes, record each reference it relied on as a clause in plain text, not inside code, HTML, emphasis, strikethrough, a link or brackets, that opens the cell or follows `;`, `,`, `.` or `<br>`, and that begins `reference:` followed directly by one of two forms:

- A link to the copy, `[text](destination)`, such as `reference: [codebook](references/<source-id>/codebook.pdf)`. The text is not empty and has no `[`, `]`, `\\`, `<` or backtick. The destination is either in angle brackets with no `<`, `>` or `\\` inside, which allows spaces, such as `[codebook](<references/hr/data dictionary.pdf>)`, or bare, with no spaces, `<` or `\\`, and with its parentheses balanced.
- For material kept out of Git, the retained location in single backticks, a comma, and `sha256` with the full 64-digit checksum and no letter, digit, `_`, `\\` or `&` directly after it, such as ``reference: `/secure/<source-id>/manual.pdf`, sha256 <checksum>``. `SHA-256` and `sha256:` are also read.

`awb-status` reads exactly these two forms, ignoring letter case, and lists every other spelling as no reference, including Markdown that renders as a link, such as a link with a title or with brackets in its text. It also stops reading a cell at a link with a title or with a destination neither form allows, at any raw HTML other than `<br>`, at an autolink containing a backtick, bracket or `<`, and at a `*`, `_` or `~` that opens emphasis or strikethrough when a backtick, bracket, `<` or an opening `*`, `_` or `~` of another kind comes before the cell's last `*`, `_` or `~` of that kind that could close it, so put reference clauses before them. To fix a listed entry, rewrite it in one of the forms: drop brackets and backslashes from the link text, write paths with `/`, and put a path with spaces or unbalanced parentheses in angle brackets. An entry such as `reference: not yet retained` counts as no reference.

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
    parser.add_argument("--request", help="source version, query, or request (default: the copied paths); "
                                          "name a credential's variable, never its value")
    parser.add_argument("--records", action="append", default=[], metavar="NAME=COUNT",
                        help="record count of a landed file, by its path inside the acquisition; "
                             "repeat the flag for each file")
    parser.add_argument("--notes", help="note recorded in the Acquisitions row; never a secret")
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
            views_dir: str | Path = "foundation/views",
            read_only: bool = False) -> "duckdb.DuckDBPyConnection":
    """Open an in-memory DuckDB session and load view files in name order.

    Project-relative paths in views, such as data/parquet/..., resolve against
    the project root from any working directory. A view that reads another view
    must sort after it; use numeric prefixes, for example 01_base.sql and
    02_derived.sql.

    read_only=True opens a session that writes nothing: no extension installs (one already
    installed loads when a statement needs it), no persistent secrets, spill files in a
    private temporary directory removed at exit, and configuration locked once the views
    load. View files may then hold only CREATE and SELECT statements, checked in every file
    before any runs, so a view file's ATTACH, COPY, or other statement is refused rather
    than run; each statement's calls and plan are then checked as read_only_sql() checks
    one, just before it runs, and a macro it creates is refused if its body in the catalog
    calls dynamic SQL. Run queries in the session through read_only_sql().
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
    views = []
    for path in sorted(directory.glob("*.sql")):
        if path.is_file():
            try:
                text = path.read_text(encoding="utf-8")
                views.append((path, text, duckdb.extract_statements(text) if read_only else None))
                if read_only:  # every file is checked before any statement runs
                    _refuse_statements(views[-1][2], ("CREATE", "SELECT"), "in a read-only session, which "
                                       "loads only CREATE and SELECT statements from view files")
            except Exception as error:
                raise RuntimeError(f"Failed to load view file: {path}") from error
    if read_only:
        # An in-memory database spills to .tmp/ under the working directory by default; a fixed
        # name under the shared temp directory could belong to another user.
        spill = tempfile.mkdtemp(prefix="awb-duckdb-")
        atexit.register(shutil.rmtree, spill, True)
    connection = duckdb.connect(config={
        "autoinstall_known_extensions": False, "allow_persistent_secrets": False,
        "temp_directory": str(Path(spill) / "spill")}) if read_only else duckdb.connect()
    try:
        connection.execute("SET file_search_path = ?", [str(root)])
        for path, text, statements in views:
            try:
                if read_only:  # what runs is the parsed statement whose kind, calls and plan were checked
                    for statement in statements:
                        _refuse_writing_plan(connection, statement)
                        before = _dynamic_names(connection)
                        connection.execute(statement.query)
                        _refuse_new_dynamic_macros(connection, before)
                else:
                    connection.execute(text)
            except Exception as error:
                raise RuntimeError(f"Failed to load view file: {path}") from error
        if read_only:
            connection.execute("SET lock_configuration = true")
    except BaseException:
        connection.close()
        raise
    return connection


# Table functions a read-only session runs. DuckDB records no side effects for table functions, and
# some write files from a SELECT (enable_profiling's save_location, enable_logging's file storage), so
# any table function not listed here is refused, as is a statement whose plan EXPLAIN cannot show.
# Limits: scalar functions are not checked (none of DuckDB's writes a file while logging is off and the
# configuration locked), and EXPLAIN binds a statement before it is checked, which DuckDB's own table
# functions do without writing; an extension's table function not listed is refused, but only once bound.
# read_xlsx, from DuckDB's excel extension, is listed so that a read-only query can read a landed Excel
# file: its arguments name a file, a sheet, a range and how to read cells, never an output, and an xlsx
# file is written only by COPY, which is refused. The session installs no extension but loads one already
# installed when a statement needs it; without the excel extension, read_xlsx or FROM 'book.xlsx' is
# refused with a hint to install it once without --read-only.
# The plan checked must be the plan that runs, so a read-only session also refuses, by name and before
# EXPLAIN, every function that turns a runtime string into SQL or a table reference: its text is bound
# anew at each bind, and current_query(), random() or now() can pick another table function at the run
# than at the check. Macros calling one, DuckDB's histogram_values and histogram table macros included,
# are refused with it. These are table functions, so a table macro calling one is refused only where it
# is called as a table function, and DuckDB's histogram() aggregate, which shares a table macro's name,
# still runs; a scalar macro calling one is refused wherever it is called. A CREATE statement's body is
# read the same way when it parses alone (_create_body); one that does not is checked by token, so there
# the histogram() aggregate is refused too. Once a view file's CREATE runs, a macro it made is checked
# again from DuckDB's own parse of its body in the catalog (_refuse_new_dynamic_macros), so a misread
# split of the CREATE's text cannot leave the session holding one. Without these dynamic functions,
# every table function a statement binds is named in its text or in a view or macro body fixed before
# the check; what still varies between check and run is values, such as which files a glob reads.
DYNAMIC_SQL_FUNCTIONS = frozenset({"query", "query_table", "json_execute_serialized_sql"})
READ_TABLE_FUNCTIONS = frozenset("""
    seq_scan range generate_series unnest repeat repeat_row glob summary sniff_csv read_text read_blob
    read_csv read_csv_auto read_parquet parquet_scan parquet_metadata parquet_schema parquet_file_metadata
    parquet_kv_metadata read_json read_json_auto read_json_objects read_json_objects_auto read_ndjson
    read_ndjson_auto read_ndjson_objects json_each json_tree read_xlsx duckdb_columns duckdb_constraints
    duckdb_databases duckdb_dependencies duckdb_extensions duckdb_functions duckdb_indexes duckdb_keywords
    duckdb_schemas duckdb_sequences duckdb_settings duckdb_tables duckdb_types duckdb_views
    pragma_table_info pragma_show pragma_version pragma_database_size pragma_storage_info
    pragma_platform pragma_collations pg_timezone_names icu_calendar_names""".split())
# The read list's table functions that come from an extension rather than DuckDB itself, and the extension.
EXTENSION_READ_FUNCTIONS = {"read_xlsx": "excel"}


def read_only_sql(connection, text, parameters=None):
    """Run SQL text in a read-only session(): only SELECT statements, refusing COPY, ATTACH, INSTALL,
    LOAD, EXPORT, SET, a PRAGMA that sets, CALL, CREATE, and every other kind, and a SELECT whose plan
    calls a table function outside READ_TABLE_FUNCTIONS or that calls dynamic SQL (_refuse_dynamic_sql),
    before any statement runs. Each statement is checked and run with the `parameters` it names as $name
    (_bound). Returns the last statement's relation, as connection.sql() does."""
    import duckdb
    statements = duckdb.extract_statements(text)  # parsed once, so what runs is what was checked
    _refuse_statements(statements, ("SELECT",), "(only SELECT runs here, and a PIVOT is one only with an IN "
                       "(...) list of its values)")
    for statement in statements:
        _refuse_writing_plan(connection, statement, parameters)
    for statement in statements[:-1]:
        connection.execute(statement.query, _bound(statement.query, parameters))
    return connection.sql(statements[-1].query, params=_bound(statements[-1].query, parameters)) \
        if statements else None


def _bound(sql, parameters):
    """The entries of parameters that sql names as $name, as run.py binds a result's query; None for none."""
    names = set(re.findall(r"\$(\w+)", sql))
    return {name: value for name, value in (parameters or {}).items() if name in names} or None


# DuckDB's errors for a $name left unbound: EXPLAIN's or a prepared statement's, and sql()'s.
UNBOUND_PARAMETERS = ("prepared statement parameters", "Unexpected prepared parameter")


def _sql_fix(message):
    """The likely fix for a DuckDB error a statement raises: bind its parameters, qualify its column, or
    else fix the statement; a PIVOT, whose expansion a read-only session can plan only with its values
    listed, is named, since its text after DuckDB's expansion no longer says PIVOT."""
    if any(text in message for text in UNBOUND_PARAMETERS):
        return ("bind each $name with --param name=value, or --settings <investigation> for that "
                "investigation's settings [parameters] (over MCP, the read tool's params or settings)")
    if "Ambiguous reference to column" in message:
        return "qualify the column with its table's name or alias"
    return "fix the statement, or for a PIVOT list its values with IN (...)"


def _refuse_writing_plan(connection, statement, parameters=None):
    """Raise unless one parsed statement calls no dynamic SQL (_refuse_dynamic_sql) and the plan DuckDB
    would run for it, bound with the parameters it names, calls only READ_TABLE_FUNCTIONS. EXPLAIN binds the
    statement, expanding views and macros, without running it; the name check runs again after it, since
    binding can load an extension's macros. A statement EXPLAIN cannot bind is refused with DuckDB's error
    and its likely fix (_sql_fix), never with advice to drop read-only, which binds it no better."""
    _refuse_dynamic_sql(connection, statement)
    text = statement.query
    try:
        plan = json.loads(connection.execute("EXPLAIN (FORMAT json) " + text,
                                             _bound(text, parameters)).fetchall()[0][1])
    except Exception as error:  # a PIVOT without IN, SQL that does not bind, or an extension not installed
        called, message = _called_names(text), str(error)
        for name, extension in sorted(EXTENSION_READ_FUNCTIONS.items()):
            # called by name, or a file such as 'book.xlsx' whose replacement scan loads the extension
            needed = name in called or f'extension "{extension}"' in message \
                or f"extension '{extension}'" in message
            if needed and connection.execute("SELECT installed FROM duckdb_extensions() WHERE extension_name = ?",
                                             [extension]).fetchall() != [(True,)]:
                raise ValueError(
                    f"read-only: {name} needs DuckDB's {extension} extension, which is not installed, and a "
                    f"read-only session installs none; install it once without --read-only, "
                    f'python3 src/awb.py sql "INSTALL {extension}; SELECT 1" (over MCP, the data tool\'s sql), '
                    "then run this again") from error
        # from None: the message carries DuckDB's error, which _fail would otherwise print twice
        raise ValueError(f"read-only: refused a statement DuckDB cannot plan ({error}); {_sql_fix(str(error))}") \
            from None
    table_functions = {name for (name,) in connection.execute(
        "SELECT upper(function_name) FROM duckdb_functions() WHERE function_type = 'table'").fetchall()}
    nodes = list(plan)
    while nodes:
        node = nodes.pop()
        info = node.get("extra_info") if isinstance(node.get("extra_info"), dict) else {}
        for name in ({node.get("name")} & table_functions) | {info.get("Function")} - {None}:
            if str(name).lower() not in READ_TABLE_FUNCTIONS:
                raise ValueError(f"read-only: refused table function {str(name).lower()}, which a read-only "
                                 "session does not run; run it without --read-only")
        nodes.extend(node.get("children") or [])
    _refuse_dynamic_sql(connection, statement)


def _refuse_dynamic_sql(connection, statement):
    """Raise when one parsed statement calls dynamic SQL: a function of DYNAMIC_SQL_FUNCTIONS, or a table
    macro calling one, called as a table function, or a scalar macro calling one, called anywhere. Calls
    are read from the statement's parse tree (json_serialize_sql); for a CREATE, which the serializer does
    not take, from the tree of its body and the tokens before it (_create_body), or from all its tokens,
    matching any position, when its body does not parse alone. A statement none of these can read is
    refused."""
    try:
        tables, scalars = _dynamic_names(connection)
        tree = json.loads(connection.execute("SELECT json_serialize_sql(?)", [statement.query]).fetchone()[0])
        by_token = False
        if not tree.get("error"):
            table_calls, calls = _calls(tree)
        elif getattr(statement.type, "name", "") == "CREATE":
            table_calls, calls, by_token = _create_calls(connection, statement.query, tables | scalars)
        else:
            raise ValueError(tree.get("error_message"))
        found = table_calls & (tables | scalars) | calls & scalars
    except Exception as error:
        raise ValueError(f"read-only: refused a statement whose calls cannot be read ({error}); "
                         "run it without --read-only") from error
    if found := sorted(found):
        # a name refused here only because by-token reading counts a table macro's call in any position
        where = (" (this CREATE's calls were checked by token, in any position, which also refuses the "
                 "histogram() aggregate)") if by_token and set(found) <= tables - scalars - DYNAMIC_SQL_FUNCTIONS \
            else ""
        raise ValueError(f"read-only: refused {found[0]}(){where}, which builds SQL from a string each time it "
                         "is bound, so the plan checked need not be the plan that runs; run it without --read-only")


def _refuse_new_dynamic_macros(connection, before):
    """Raise when the catalog now has a macro calling dynamic SQL that was not in before, the result of
    _dynamic_names() just before a statement ran: a check of DuckDB's own parse of a created macro's body,
    behind the split of the CREATE statement's text (_create_body) that _refuse_dynamic_sql reads."""
    after = _dynamic_names(connection)
    if new := sorted((after[0] - before[0]) | (after[1] - before[1])):
        raise ValueError(f"read-only: refused {new[0]}(), a macro just created that calls dynamic SQL, which "
                         "builds SQL from a string each time it is bound, so the plan checked need not be the "
                         "plan that runs; run it without --read-only")


def _dynamic_names(connection):
    """Return the names that call dynamic SQL as table functions (DYNAMIC_SQL_FUNCTIONS and the table
    macros calling one) and as scalar functions (the scalar macros calling one), directly or through
    other macros. A macro body that does not parse alone counts every name its tokens call."""
    tables, scalars = set(DYNAMIC_SQL_FUNCTIONS), set()
    macros = []
    for name, table, body, tree in connection.execute(
            "SELECT DISTINCT lower(function_name), function_type = 'table_macro', macro_definition, "
            "json_serialize_sql(CASE WHEN function_type = 'table_macro' THEN macro_definition "
            "ELSE 'SELECT ' || macro_definition END) FROM duckdb_functions() "
            "WHERE macro_definition IS NOT NULL").fetchall():
        tree = json.loads(tree)
        table_calls, calls = (_called_names(body),) * 2 if tree.get("error") else _calls(tree)
        macros.append((name, table, table_calls, calls))
    while more := [(name, table) for name, table, table_calls, calls in macros
                   if name not in (tables if table else scalars)
                   and (table_calls & (tables | scalars) or calls & scalars)]:
        for name, table in more:
            (tables if table else scalars).add(name)
    return tables, scalars


def _parse_tree(connection, text):
    """Return the parse tree json_serialize_sql gives SQL text, or None when it takes no such text."""
    tree = json.loads(connection.execute("SELECT json_serialize_sql(?)", [text]).fetchone()[0])
    return None if tree.get("error") else tree


def _calls(tree):
    """Return the lowercased names a parse tree calls as table functions, and those it calls anywhere."""
    tables, calls, nodes = set(), set(), [tree]
    while nodes:
        node = nodes.pop()
        if isinstance(node, dict):
            if isinstance(node.get("function_name"), str):
                calls.add(node["function_name"].lower())
            if node.get("type") == "TABLE_FUNCTION":
                function = node.get("function")
                if not (isinstance(function, dict) and isinstance(function.get("function_name"), str)):
                    raise ValueError("a table function reference without a function name")
                tables.add(function["function_name"].lower())
            nodes.extend(node.values())
        elif isinstance(node, list):
            nodes.extend(node)
    return tables, calls


def _create_calls(connection, text, dynamic):
    """Return the names a CREATE statement calls as table functions, those it calls anywhere, and whether
    they were read by token: from its body's parse tree, with every name called before the body counted as
    a table function, when _create_body finds a body whose tree holds each name of dynamic that its tokens
    call; else every name its tokens call, counted as both."""
    split = _create_body(text)
    if split is not None:
        prefix, body, kind = split
        tree = _parse_tree(connection, body if kind == "select" else "SELECT " + body)
        if tree is not None:
            table_calls, calls = _calls(tree)
            if _called_names(body) & dynamic <= calls:
                return _called_names(prefix) | table_calls, calls, False
    names = _called_names(text)
    return names, names, True


def _create_body(text):
    """Split a CREATE statement into the text before its body, the body, and how the body parses alone.

    Closed grammar, on DuckDB's tokens, each read as the word at its start, so a comment glued to a
    token, as in AS/**/ or (/*)*/, is not part of it: CREATE, then tokens up to the first AS keyword
    outside parentheses, then the body. Before that AS, the first of the keywords VIEW, TABLE, MACRO, and FUNCTION
    names the kind. The body of a VIEW or TABLE is a query ("select"); a MACRO's or FUNCTION's is TABLE
    and a query ("select"), or an expression ("expression"), parsed as SELECT <body>. Anything else, such
    as CREATE TYPE or a CREATE TABLE without AS, returns None."""
    import duckdb
    data = text.encode("utf-8")  # token positions are byte offsets
    tokens = duckdb.tokenize(text)
    # a token's word is matched at its start, as _called_names reads it: DuckDB emits no comment tokens, so
    # a comment glued to a token, as in AS/**/ or (/*)*/, is part of its span but not of its word
    spans = [(_token_word(data[start:end].decode("utf-8")), kind.name, start)
             for (start, kind), end in zip(tokens, [after for after, _ in tokens[1:]] + [len(data)])]
    if not spans or spans[0][0].upper() != "CREATE":
        return None
    depth, object_kind = 0, None
    for index, (word, kind, start) in enumerate(spans):
        if kind == "operator":
            depth += (word == "(") - (word == ")")
        elif kind == "keyword" and depth == 0:
            if object_kind is None and word.upper() in ("VIEW", "TABLE", "MACRO", "FUNCTION"):
                object_kind = word.upper()
            elif word.upper() == "AS":
                rest = spans[index + 1:]
                if object_kind is None:
                    return None
                if object_kind in ("VIEW", "TABLE"):
                    body_kind = "select"
                elif rest and rest[0][1] == "keyword" and rest[0][0].upper() == "TABLE":
                    body_kind, rest = "select", rest[1:]
                else:
                    body_kind = "expression"
                if not rest:
                    return None
                return data[:start].decode("utf-8"), data[rest[0][2]:].decode("utf-8"), body_kind
    return None


def _token_word(span):
    """Return the word at the start of a token's span (a quoted name, a name, or one character), or ""."""
    word = re.match(r'"(?:[^"]|"")*"|[\w$]+|\S', span)
    return word.group() if word else ""


def _called_names(text):
    """Return the lowercased names DuckDB's lexer finds just before "(" in SQL text."""
    import duckdb
    data = text.encode("utf-8")  # token positions are byte offsets
    tokens = duckdb.tokenize(text)
    names = set()
    for (start, kind), (after, _) in zip(tokens, tokens[1:]):
        word = re.match(r'"(?:[^"]|"")*"|[\w$]+', data[start:after].decode("utf-8"))  # ':' is a keyword
        if word and data[after:after + 1] == b"(" and kind.name in ("identifier", "keyword"):
            word = word.group()
            names.add(word[1:-1].replace('""', '"').lower() if word.startswith('"') else word.lower())
    return names


def _refuse_statements(statements, allowed, where):
    """Raise unless every statement from duckdb.extract_statements() is of an allowed kind."""
    for statement in statements:
        kind = getattr(statement.type, "name", "") or "unknown"
        if kind not in allowed:
            raise ValueError(f"read-only: refused statement kind {kind} {where}; run it without --read-only")


def _sql_argument(root, argument):
    """Return the text of the query file argument names, else argument itself as SQL text. One line
    ending in .sql, in any case, names a file: when none exists there, this raises rather than run it."""
    try:
        path = _under(root, argument)
        is_file = path.is_file()
    except (OSError, ValueError):  # SQL text can be too long, or hold a NUL, for a path
        is_file = False
    if not is_file and "\n" not in argument and argument.strip().lower().endswith(".sql"):
        raise ValueError(f"no query file {argument.strip()}; a relative path is read from the project root")
    return path.read_text(encoding="utf-8") if is_file else argument


def _parameter(text):
    """(name, value) from --param's name=value. The name is letters, digits, and _, as a query names it
    with $name. The value is read as a one-line TOML value, as settings [parameters] are, so 2026-01-01 is
    a date, 5 an integer, true a boolean, and "5" a string; text that is no TOML value is a string as given."""
    name, separator, value = text.partition("=")
    if not separator or not re.fullmatch(r"\w+", name):
        raise argparse.ArgumentTypeError(f"expected name=value, the name in letters, digits, and _: {text!r}")
    if "\n" in value or "\r" in value:
        return name, value
    try:
        return name, _toml().loads(f"value = {value}")["value"]
    except ValueError:  # TOMLDecodeError
        return name, value


def _settings_parameters(root, investigation):
    """The [parameters] table of investigations/<investigation>/settings.toml."""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", investigation):
        raise ValueError(f"--settings needs an investigation name: {investigation!r}")
    path = Path(root) / "investigations" / investigation / "settings.toml"
    if not path.is_file():
        raise ValueError(f"investigations/{investigation}/settings.toml does not exist")
    try:
        parameters = _toml().loads(path.read_text(encoding="utf-8")).get("parameters", {})
    except ValueError as error:
        raise ValueError(f"investigations/{investigation}/settings.toml: {error}") from error
    if not isinstance(parameters, dict):
        raise ValueError(f"investigations/{investigation}/settings.toml: parameters is not a table")
    return parameters


def _table_cell(value, width=80):
    text = "NULL" if value is None else str(value)
    text = text.replace("|", "\\|").replace("\r", "\\r").replace("\n", "\\n")
    return text if len(text) <= width else text[:width - 1] + "…"


def _markdown_table(header, rows):
    lines = ["| " + " | ".join(map(_table_cell, header)) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(map(_table_cell, row)) + " |" for row in rows]
    return "\n".join(lines)


def _bound_sql(connection, text, parameters):
    """connection.sql(text), each statement bound with the parameters it names as $name (_bound)."""
    import duckdb
    statements = duckdb.extract_statements(text)
    for statement in statements[:-1]:
        connection.execute(statement.query, _bound(statement.query, parameters))
    return connection.sql(statements[-1].query, params=_bound(statements[-1].query, parameters)) \
        if statements else None


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
    parser.add_argument("--param", action="append", default=[], type=_parameter, metavar="NAME=VALUE",
                        help="bind $NAME to VALUE, read as a TOML value as settings are (2026-01-01 is a date, "
                             "5 an integer, other text a string); repeat for each; wins over --settings")
    parser.add_argument("--settings", metavar="INVESTIGATION",
                        help="bind the [parameters] of investigations/INVESTIGATION/settings.toml")
    parser.add_argument("--read-only", action="store_true",
                        help="write nothing: run only SELECT statements whose table functions read files or the "
                             "catalog and build no SQL from a string (query, query_table, the histogram table "
                             "macro; the histogram() aggregate runs), in a session that installs no extension "
                             "and spills outside the project; read_xlsx needs DuckDB's excel extension installed "
                             "once without --read-only; a view file's CREATE whose body does not parse alone is "
                             "checked by token, refusing histogram() there too; refuses --out")
    args = parser.parse_args(argv)
    if args.limit < 0:
        parser.error("--limit must be 0 or more")
    if args.read_only and args.out:
        parser.error("--read-only refuses --out")
    out = _under(root, args.out) if args.out else None
    if out is not None and out.suffix.lower() not in {".csv", ".parquet"}:
        parser.error("--out must end in .csv or .parquet")
    try:
        parameters = {**(_settings_parameters(root, args.settings) if args.settings else {}), **dict(args.param)}
        with session(root, read_only=args.read_only) as connection:
            # sql() runs every statement and returns the last one's result, or None.
            text = _sql_argument(root, args.query)
            if args.read_only:
                relation = read_only_sql(connection, text, parameters)
            elif parameters:
                relation = _bound_sql(connection, text, parameters)
            else:
                relation = connection.sql(text)
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
        if not args.read_only and any(text in str(error) for text in UNBOUND_PARAMETERS):
            error = ValueError(f"{error}; {_sql_fix(str(error))}")
        return _fail("sql", error)
    print(_markdown_table(header, rows))
    print(f"{len(rows)} of {total} rows shown" + (f"; full result in {args.out}" if out else ""))
    return 0
