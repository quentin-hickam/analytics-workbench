#!/usr/bin/env python3
"""Scan one workbench dataset for candidate cleaning issues. Proposes only: data and views stay as they are.

Run with Python 3.10+ and the duckdb package from the project's environment:
    scan_dataset.py PROJECT_ROOT DATASET [--key COLS] [--ref COL=TARGET.COL] [--range COL=MIN:MAX]
                    [--columns COLS] [--name NAME] [--rescan [BASELINE]]
DATASET is a canonical view, a dataset under data/parquet/ (its newest publication), a publication
or acquisition directory, a data file, or a saved .sql query. Views load through the project's
session() in src/preparation/landing.py. Landed CSV is read as text so parse failures stay visible.

The complete scan goes to foundation/scans/<name>.json, beside the quality record that cites it;
a query saved under investigations/ is scanned to <query>.scan.json beside it, so a local
assessment stays local. Stdout is compact JSON: counts, a few examples, and the scan path.

Scan file (schema awb-scan/1):
    {schema, name, target: {kind, label, path}, scanned_at, options, row_count,
     columns: {column: {type, typed_as, non_null, distinct, null_rate}},
     candidate_keys, null_patterns: [{columns, rows}], issues: [issue],
     baseline: null | {scanned_at, row_count, columns, issues}, delta: null | {...}}
    issue: {id, key, check, column, count, of, summary, examples: [{value, count}], detail,
            recorded: null | {id, status, count}}
Issue ids (S1, S2, ...) stay stable from a baseline scan through its rescans; a key names the
check, column, and value, so a rescan matches issues by key and reports before and after counts.
Keys written into foundation/quality.md as `<name>#<key>` mark an issue as recorded; the row's
"(<count> of <of>)" is its recorded count, printed on stdout as recorded_count beside the current count.
Stdout lists at most 25 unrecorded issues; more_issues counts the rest, which are in the scan file.
"""

import argparse
import importlib.util
import json
import math
import os
import re
import sys
from datetime import date, datetime, time
from decimal import Decimal
from pathlib import Path

SCHEMA = "awb-scan/1"
TEXT_SENTINELS = ("", "n/a", "na", "#n/a", "null", "none", "nil", "nan", "-", "--", "?", ".",
                  "unknown", "missing", "tbd", "not available")
NUMERIC_SENTINELS = (-1, -9, -99, -999, -9999, -99999, 99, 999, 9999, 99999, 999999, 9999999)
# Placeholder dates. 1970-01-01 is a real date often enough that it needs concentration to count.
DATE_SENTINELS = ("0001-01-01", "1800-01-01", "1899-12-30", "1899-12-31", "1900-01-01",
                  "1970-01-01", "2099-12-31", "2999-12-31", "9999-12-31")
TYPE_ORDER = ("BIGINT", "DOUBLE", "DATE", "TIMESTAMP", "BOOLEAN")
DATE_FORMATS = ("%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y", "%m-%d-%Y", "%d.%m.%Y",
                "%d %b %Y", "%b %d, %Y")
DATE_LIKE = r"^\d{1,4}[/.\-]\d{1,2}[/.\-]\d{1,4}$|^\d{1,2} [A-Za-z]{3} \d{4}$|^[A-Za-z]{3} \d{1,2}, \d{4}$"
TRIM = r"^[\s\x{00A0}]+|[\s\x{00A0}]+$"
NUMERIC_TYPES = ("TINYINT", "SMALLINT", "INTEGER", "BIGINT", "HUGEINT", "UTINYINT", "USMALLINT",
                 "UINTEGER", "UBIGINT", "UHUGEINT", "FLOAT", "REAL", "DOUBLE", "DECIMAL")
METADATA = ("provenance.json", "publication.json")
KEY_NAME = re.compile(r"(^|_)(id|key|uuid|guid)$|[a-z0-9]Id$", re.I)
CHECK_ORDER = ("duplicate-rows", "duplicate-key", "null-key", "parse", "date-formats", "sentinel",
               "variants", "near-variants", "whitespace", "negative", "range", "future-date",
               "ancient-date", "extreme", "orphans", "all-null", "text-typed")
READERS = {".parquet": "read_parquet({files})",
           ".csv": "read_csv({files}, all_varchar = true, union_by_name = true)",
           ".tsv": "read_csv({files}, all_varchar = true, union_by_name = true, delim = '\t')",
           ".txt": "read_csv({files}, all_varchar = true, union_by_name = true)",
           ".json": "read_json_auto({files}, union_by_name = true)",
           ".jsonl": "read_json_auto({files}, union_by_name = true)",
           ".ndjson": "read_json_auto({files}, union_by_name = true)"}


def q(name):
    return '"' + str(name).replace('"', '""') + '"'


def lit(text):
    return "'" + str(text).replace("'", "''") + "'"


def _cast(t, sql_type):
    """TRY_CAST, except that BIGINT accepts only integer text (DuckDB would round '11.5')."""
    if sql_type == "BIGINT":
        return f"TRY_CAST(CASE WHEN regexp_matches({t}, '^[+-]?[0-9]+$') THEN {t} END AS BIGINT)"
    return f"TRY_CAST({t} AS {sql_type})"


def _kind(sql_type):
    base = sql_type.split("(")[0].strip().upper()
    if base in NUMERIC_TYPES:
        return "number"
    if base == "DATE" or base.startswith("TIMESTAMP"):
        return "time"
    if base == "VARCHAR":
        return "text"
    return "other"


def _plain(value, limit=80):
    """Return a short strict-JSON value: dates as ISO text, long text truncated."""
    if value is None or isinstance(value, (bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else str(value)
    if isinstance(value, Decimal):
        return float(value) if value.is_finite() else str(value)
    if isinstance(value, datetime) and value.time() == time() and value.tzinfo is None:
        return value.date().isoformat()
    if isinstance(value, (date, datetime, time)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): _plain(v, 40) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v, 40) for v in value]
    text = str(value)
    return text if len(text) <= limit else text[:limit] + "..."


def _number_text(value):
    return str(int(value)) if float(value).is_integer() else str(value)


# ----- target resolution -------------------------------------------------------------------------

def _connect(root, need_views):
    try:
        import duckdb
    except ImportError as error:
        raise RuntimeError("the scan needs the duckdb package in the project's Python environment") from error
    helper = root / "src/preparation/landing.py"
    if helper.is_file():
        # Load views exactly as analytical sessions do.
        sys.path.insert(0, str(helper.parent))
        spec = importlib.util.spec_from_file_location("awb_project_landing", helper)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.session(root)
    if need_views and (root / "foundation/views").is_dir():
        raise RuntimeError("views need src/preparation/landing.py; install the workbench helpers with awb-init")
    connection = duckdb.connect()
    connection.execute("SET file_search_path = ?", [str(root)])
    return connection


def _file_relation(path):
    """Return (relation SQL, kind, default name) for a data file or directory."""
    if path.is_file():
        files, directory = [path], path.parent
    else:
        directory = path
        files = sorted(p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in READERS
                       and p.name not in METADATA)
    if not files:
        raise ValueError(f"no data files in {path}")
    suffixes = {READERS.get(p.suffix.lower()) for p in files}
    if None in suffixes or len(suffixes) != 1:
        raise ValueError(f"name one data file; {path} holds mixed or unsupported formats")
    relation = READERS[files[0].suffix.lower()].format(files="[" + ", ".join(lit(p) for p in files) + "]")
    if (directory / "publication.json").is_file():
        return relation, "publication", f"{directory.parent.name}@{directory.name}"
    if (directory / "provenance.json").is_file():
        return relation, "acquisition", f"{directory.parent.name}@{directory.name}"
    return relation, "file", path.stem


def _newest_publication(directory):
    found = []
    for path in directory.iterdir():
        metadata = path / "publication.json"
        if path.is_dir() and not path.name.endswith(".partial") and metadata.is_file():
            try:
                converted = json.loads(metadata.read_text(encoding="utf-8")).get("converted_at") or ""
            except (OSError, ValueError, AttributeError):
                converted = ""
            found.append((converted, path.name, path))
    return max(found)[2] if found else None


def _resolve(root, connection, dataset):
    """Return {relation, kind, label, path, name} for a view, dataset, path, or saved query."""
    path = Path(dataset)
    full = path if path.is_absolute() else root / path
    relative = os.path.relpath(full, root)
    if full.suffix == ".sql" and full.is_file():
        sql = re.sub(r";\s*$", "", full.read_text(encoding="utf-8").strip())
        return {"relation": f"(\n{sql}\n)", "kind": "query", "label": f"query {relative}",
                "path": relative, "name": full.stem}
    if full.exists():
        relation, kind, name = _file_relation(full)
        return {"relation": relation, "kind": kind, "label": f"{kind} {relative}",
                "path": relative, "name": name}
    names = {row[0].lower(): row[0] for row in connection.execute(
        "SELECT view_name FROM duckdb_views() WHERE NOT internal "
        "UNION ALL SELECT table_name FROM duckdb_tables()").fetchall()}
    if dataset.lower() in names:
        view = names[dataset.lower()]
        return {"relation": q(view), "kind": "view", "label": f"view {view}", "path": None, "name": view}
    publications = root / "data/parquet" / dataset
    if publications.is_dir():
        newest = _newest_publication(publications)
        if newest is not None:
            relation, kind, name = _file_relation(newest)
            relative = os.path.relpath(newest, root)
            return {"relation": relation, "kind": kind, "label": f"{kind} {relative}",
                    "path": relative, "name": name}
    raise ValueError(f"no view, dataset, or path named {dataset!r}")


# ----- the scan ----------------------------------------------------------------------------------

class Scan:
    def __init__(self, connection, target, options, today):
        self.db = connection
        self.target = target
        self.options = options
        self.today = today
        self.issues = []

    def one(self, sql):
        return self.db.execute(sql).fetchone()

    def aggregate(self, items, source):
        """Run many named aggregates in one pass and return them as a dict."""
        if not items:
            return {}
        row = self.one("SELECT " + ", ".join(f"{expr} AS {q(alias)}" for alias, expr in items)
                       + f" FROM {source}")
        return dict(zip((alias for alias, _ in items), row))

    def examples(self, expr, where, order="n DESC, v", limit=10):
        rows = self.db.execute(f"SELECT {expr} AS v, count(*) AS n FROM __awb_typed WHERE {where} "
                               f"GROUP BY 1 ORDER BY {order} LIMIT {limit}").fetchall()
        return [{"value": _plain(v), "count": n} for v, n in rows]

    def add(self, check, column, suffix, count, of, summary, examples=(), detail=None):
        key = ":".join(str(part) for part in (check, column, suffix) if part is not None)
        summary = re.sub(r"(?<![\d.])1 (extra row|value|row|date|lone negative value)s\b", r"1 \1", summary)
        self.issues.append({"id": None, "key": key, "check": check, "column": column,
                            "count": int(count), "of": int(of),
                            "summary": summary, "examples": list(examples), "detail": detail,
                            "recorded": None})

    def run(self):
        db = self.db
        db.execute(f"CREATE OR REPLACE TEMP VIEW __awb_scan AS SELECT * FROM {self.target['relation']}")
        described = db.execute("DESCRIBE __awb_scan").fetchall()
        columns = [(row[0], row[1]) for row in described]
        names = [name for name, _ in columns]
        chosen = self.options.get("columns") or names
        unknown = sorted(set(chosen) - set(names))
        if unknown:
            raise ValueError(f"unknown columns: {', '.join(unknown)}")
        index = {name: i for i, name in enumerate(names)}
        kinds = {name: _kind(sql_type) for name, sql_type in columns}
        text = [name for name in chosen if kinds[name] == "text"]
        trimmed = {name: q(f"__t{index[name]}") for name in text}
        tokens = "(" + ", ".join(lit(token) for token in TEXT_SENTINELS) + ")"
        extra = "".join(f", regexp_replace({q(n)}, '{TRIM}', '', 'g') AS {trimmed[n]}" for n in text)
        db.execute(f"CREATE OR REPLACE TEMP VIEW __awb_base AS SELECT *{extra} FROM __awb_scan")

        # Pass 1: counts, distincts, and text-shape measures for every column at once.
        items = [("n", "count(*)")]
        for name in chosen:
            i, c = index[name], q(name)
            items.append((f"nn{i}", f"count({c})"))
            if kinds[name] != "other":
                items.append((f"d{i}", f"count(DISTINCT {c})"))
        for name in text:
            i, c, t = index[name], q(name), trimmed[name]
            real = f"lower({t}) NOT IN {tokens}"
            items += [(f"ws{i}", f"count(*) FILTER (WHERE {c} <> {t})"),
                      (f"sen{i}", f"count(*) FILTER (WHERE lower({t}) IN {tokens})"),
                      (f"cand{i}", f"count({t}) FILTER (WHERE {real})"),
                      (f"lz{i}", f"count(*) FILTER (WHERE regexp_matches({t}, '^[+-]?0[0-9]'))"),
                      (f"dl{i}", f"count(*) FILTER (WHERE regexp_matches({t}, {lit(DATE_LIKE)}))")]
            items += [(f"ty{i}_{T}", f"count({_cast(t, T)}) FILTER (WHERE {real})") for T in TYPE_ORDER]
        a = self.aggregate(items, "__awb_base")
        rows = a["n"]
        # Examples read __awb_typed; it gains the typed columns once they are known.
        db.execute("CREATE OR REPLACE TEMP VIEW __awb_typed AS SELECT * FROM __awb_base")
        threshold = self.options["typed_threshold"]

        info = {}
        for name, sql_type in columns:
            if name not in chosen:
                continue
            i = index[name]
            non_null = a[f"nn{i}"]
            info[name] = {"type": sql_type, "typed_as": None, "non_null": non_null,
                          "distinct": a.get(f"d{i}"),
                          "null_rate": round(1 - non_null / rows, 4) if rows else 0.0}

        # Decide which text columns look typed, and build each column's typed expression.
        typed = {}
        for name in chosen:
            if kinds[name] in ("number", "time"):
                typed[name] = (kinds[name], q(name) if kinds[name] == "number"
                               else f"CAST({q(name)} AS TIMESTAMP)")
        for name in text:
            i, t = index[name], trimmed[name]
            candidates = a[f"cand{i}"]
            if not candidates:
                continue
            found = None
            for T in TYPE_ORDER:
                if T in ("BIGINT", "DOUBLE") and a[f"lz{i}"]:
                    continue  # leading zeros mark a code, not a number
                if a[f"ty{i}_{T}"] / candidates >= threshold:
                    found = (T, a[f"ty{i}_{T}"], None, [])
                    break
            if found is None and a[f"dl{i}"] / candidates >= threshold:
                found = self.date_formats(name, t, tokens, candidates, threshold)
            if found is None:
                continue
            T, parsed, formats, covering = found
            info[name]["typed_as"] = T
            real = f"lower({t}) NOT IN {tokens}"
            if formats:
                # One covering format parses alone; mixed formats parse in turn, ISO first.
                used = covering[:1] or list(formats)
                parse = "coalesce({parts})".format(parts=", ".join(
                    f"TRY_CAST({t} AS TIMESTAMP)" if f == "ISO" else f"try_strptime({t}, {lit(f)})" for f in used))
                parse = parse if len(used) > 1 else parse[len("coalesce("):-1]
            else:
                parse = _cast(t, T)
            if T in ("BIGINT", "DOUBLE"):
                typed[name] = ("number", parse)
            elif T in ("DATE", "TIMESTAMP"):
                typed[name] = ("time", parse if formats else f"TRY_CAST({t} AS TIMESTAMP)")
            failures = candidates - parsed
            if failures:
                self.add("parse", name, T, failures, candidates,
                         f"{failures} of {candidates} values in {name} not parsing as {T}",
                         self.examples(t, f"{real} AND {parse} IS NULL"),
                         {"type": T, "parsed": parsed})
            if formats and len(covering) != 1:
                if covering:
                    count, words = parsed, "every value fits " + " and ".join(covering) + "; day and month order is ambiguous"
                else:
                    count, words = parsed - max(formats.values()), "mixes date formats"
                self.add("date-formats", name, None, count, candidates,
                         f"{name} {words}: " + ", ".join(f"{f} {n}" for f, n in formats.items()),
                         self.examples(t, f"{real} AND TRY_CAST({t} AS TIMESTAMP) IS NULL AND {parse} IS NOT NULL"),
                         {"formats": formats, "note": "format counts overlap where day and month are both 12 or less"})
            if self.target["kind"] != "acquisition":
                self.add("text-typed", name, T, parsed, info[name]["non_null"],
                         f"{name} stored as text, with {parsed} values parsing as {T}"
                         + (f" ({', '.join(covering[:1] or formats)})" if formats else ""),
                         self.examples(t, f"{t} IS NOT NULL", limit=3), {"type": T, "formats": formats})

        typed_columns = ", ".join(f"{expr} AS {q(f'__v{index[n]}')}" for n, (_, expr) in typed.items())
        db.execute("CREATE OR REPLACE TEMP VIEW __awb_typed AS SELECT *"
                   + (", " + typed_columns if typed_columns else "") + " FROM __awb_base")

        for name in text:
            i, c, t = index[name], q(name), trimmed[name]
            if a[f"ws{i}"]:
                self.add("whitespace", name, None, a[f"ws{i}"], info[name]["non_null"],
                         f"{a[f'ws{i}']} values in {name} with leading or trailing whitespace",
                         self.examples(c, f"{c} <> {t}"))
            if a[f"sen{i}"]:
                for example in self.examples(f"lower({t})", f"lower({t}) IN {tokens}", limit=len(TEXT_SENTINELS)):
                    token = example["value"]
                    self.add("sentinel", name, json.dumps(token), example["count"], info[name]["non_null"],
                             f"{example['count']} values in {name} equal to the placeholder {json.dumps(token)}",
                             self.examples(c, f"lower({t}) = {lit(token)}", limit=3))
            distinct = info[name]["distinct"] or 0
            if info[name]["typed_as"] is None and 1 < distinct <= self.options["max_categories"]:
                self.variants(name, t, tokens, distinct, info[name]["non_null"])

        self.ranges(typed, index, info)
        self.duplicates(names, chosen, kinds, info, index, rows)
        self.orphans()
        for name in chosen:
            if rows and info[name]["non_null"] == 0:
                self.add("all-null", name, None, rows, rows, f"{name} null in every row")
        candidate_keys = [n for n in chosen if rows and info[n]["non_null"] == rows and info[n]["distinct"] == rows]
        return rows, info, candidate_keys, self.null_patterns(chosen, info, rows)

    def date_formats(self, name, t, tokens, candidates, threshold):
        """Count each date format; return (type, parsed, {format: count}, formats covering every value)."""
        real = f"lower({t}) NOT IN {tokens}"
        items = [("ISO", f"count(TRY_CAST({t} AS TIMESTAMP)) FILTER (WHERE {real})")]
        items += [(f, f"count(try_strptime({t}, {lit(f)})) FILTER (WHERE {real})") for f in DATE_FORMATS]
        items.append(("any", "count(coalesce(TRY_CAST({t} AS TIMESTAMP), {rest})) FILTER (WHERE {real})".format(
            t=t, real=real, rest=", ".join(f"try_strptime({t}, {lit(f)})" for f in DATE_FORMATS))))
        counts = self.aggregate(items, "__awb_base")
        parsed = counts.pop("any")
        if parsed / candidates < threshold:
            return None
        formats = {f: n for f, n in counts.items() if n}
        if set(formats) <= {"ISO"}:
            return None  # ISO dates already passed or failed the DATE and TIMESTAMP casts
        return "DATE", parsed, formats, [f for f, n in formats.items() if n == parsed]

    def variants(self, name, t, tokens, distinct, non_null):
        normalize = "trim(lower(regexp_replace(value, '[[:punct:][:space:]]+', ' ', 'g')))"
        values = (f"SELECT {t} AS value, count(*) AS n FROM __awb_base WHERE {t} IS NOT NULL "
                  f"AND lower({t}) NOT IN {tokens} GROUP BY 1")
        groups = self.db.execute(
            f"WITH v AS ({values}), g AS (SELECT {normalize} AS norm, value, n FROM v) "
            "SELECT norm, sum(n) AS total, max(n) AS top, "
            "list({'value': value, 'count': n} ORDER BY n DESC, value) AS items "
            "FROM g WHERE norm <> '' GROUP BY norm HAVING count(*) > 1 ORDER BY total DESC").fetchall()
        for norm, total, top, items in groups:
            leading = items[0]["value"]
            self.add("variants", name, norm, total - top, non_null,
                     f"{total - top} values in {name} spelling {json.dumps(leading)} another way",
                     [{"value": _plain(item["value"]), "count": item["count"]} for item in items[:10]])
        if distinct > 200:
            return
        pairs = self.db.execute(
            f"WITH v AS ({values}), g AS (SELECT {normalize} AS norm, sum(n) AS n FROM v GROUP BY 1) "
            "SELECT a.norm, a.n, b.norm, b.n, jaro_winkler_similarity(a.norm, b.norm) AS sim "
            "FROM g a JOIN g b ON a.norm < b.norm "
            "WHERE length(a.norm) >= 4 AND length(b.norm) >= 4 "
            "AND jaro_winkler_similarity(a.norm, b.norm) >= 0.92 "
            "AND regexp_replace(a.norm, '[0-9]', '', 'g') <> regexp_replace(b.norm, '[0-9]', '', 'g') "
            "ORDER BY sim DESC, a.norm LIMIT 20").fetchall()
        for left, left_n, right, right_n, similarity in pairs:
            self.add("near-variants", name, f"{left}|{right}", min(left_n, right_n), non_null,
                     f"{name} has near-identical labels {json.dumps(left)} and {json.dumps(right)}",
                     [{"value": left, "count": left_n}, {"value": right, "count": right_n}],
                     {"similarity": round(similarity, 3)})

    def ranges(self, typed, index, info):
        """Sentinels, lone negatives, extremes, impossible dates, and requested ranges."""
        requested = {}
        for spec in self.options["ranges"]:
            column, low, high = _parse_range(spec)
            if column not in typed:
                raise ValueError(f"--range {spec}: {column} is not a numeric or date column in the scan")
            requested.setdefault(column, []).append((spec, low, high))
        sentinel_numbers = "(" + ", ".join(map(str, NUMERIC_SENTINELS)) + ")"
        sentinel_dates = "(" + ", ".join(f"DATE {lit(d)}" for d in DATE_SENTINELS) + ")"
        items = []
        for name, (kind, _) in typed.items():
            i = index[name]
            v = q(f"__v{i}")
            items += [(f"mn{i}", f"min({v})"), (f"mx{i}", f"max({v})")]
            if kind == "number":
                items += [(f"neg{i}", f"count(*) FILTER (WHERE {v} < 0)"),
                          (f"mxo{i}", f"max({v}) FILTER (WHERE {v} NOT IN {sentinel_numbers})"),
                          (f"mno{i}", f"min({v}) FILTER (WHERE {v} NOT IN {sentinel_numbers})"),
                          (f"q1{i}", f"quantile_cont(CAST({v} AS DOUBLE), 0.25)"),
                          (f"q3{i}", f"quantile_cont(CAST({v} AS DOUBLE), 0.75)")]
                items += [(f"s{i}_{k}", f"count(*) FILTER (WHERE {v} = {s})") for k, s in enumerate(NUMERIC_SENTINELS)]
            else:
                day = f"CAST({v} AS DATE)"
                items += [(f"fut{i}", f"count(*) FILTER (WHERE {day} > DATE {lit(self.today)} "
                                      f"AND {day} NOT IN {sentinel_dates})"),
                          (f"anc{i}", f"count(*) FILTER (WHERE {day} < DATE '1900-01-01' "
                                      f"AND {day} NOT IN {sentinel_dates})")]
                items += [(f"s{i}_{k}", f"count(*) FILTER (WHERE {day} = DATE {lit(d)})") for k, d in enumerate(DATE_SENTINELS)]
            for k, (_, low, high) in enumerate(requested.get(name, [])):
                items.append((f"r{i}_{k}", f"count(*) FILTER (WHERE {_outside(v, kind, low, high)})"))
        a = self.aggregate(items, "__awb_typed")

        fences = {}
        for name, (kind, _) in typed.items():
            i = index[name]
            v = q(f"__v{i}")
            non_null = info[name]["non_null"]
            flagged = []
            if kind == "number":
                for k, s in enumerate(NUMERIC_SENTINELS):
                    count = a[f"s{i}_{k}"]
                    if not count:
                        continue
                    others_max, others_min = a[f"mxo{i}"], a[f"mno{i}"]
                    if (s < 0 and others_min is not None and others_min >= 0) or \
                            (s > 0 and not KEY_NAME.search(name) and others_max is not None
                             and s > 2 * max(others_max, 0)):
                        flagged.append(s)
                        self.add("sentinel", name, _number_text(s), count, non_null,
                                 f"{count} values in {name} equal to {s}, far outside the other values "
                                 f"({_plain(others_min)} to {_plain(others_max)})",
                                 [{"value": s, "count": count}])
                excluded = f" AND {v} NOT IN ({', '.join(map(str, flagged))})" if flagged else ""
                negatives = a[f"neg{i}"] - sum(a[f"s{i}_{NUMERIC_SENTINELS.index(s)}"] for s in flagged if s < 0)
                if negatives and non_null and negatives / non_null <= 0.01:
                    self.add("negative", name, None, negatives, non_null,
                             f"{negatives} lone negative values in {name}",
                             self.examples(v, f"{v} < 0{excluded}", order="v, n DESC"))
                q1, q3 = a[f"q1{i}"], a[f"q3{i}"]
                if q1 is not None and q3 is not None and q3 > q1 and math.isfinite(q3 - q1) \
                        and not KEY_NAME.search(name):
                    spread = q3 - q1
                    fences[name] = (q1 - 5 * spread, q3 + 5 * spread, excluded)
            else:
                distinct = info[name]["distinct"] or 1
                for k, d in enumerate(DATE_SENTINELS):
                    count = a[f"s{i}_{k}"]
                    if count and (d != "1970-01-01" or count > 3 * non_null / distinct):
                        self.add("sentinel", name, d, count, non_null,
                                 f"{count} values in {name} equal to the placeholder date {d}",
                                 [{"value": d, "count": count}])
                day = f"CAST({v} AS DATE)"
                for check, alias, words, where in (
                        ("future-date", f"fut{i}", f"after the scan date {self.today}", f"{day} > DATE {lit(self.today)}"),
                        ("ancient-date", f"anc{i}", "before 1900", f"{day} < DATE '1900-01-01'")):
                    if a[alias]:
                        self.add(check, name, None, a[alias], non_null, f"{a[alias]} dates in {name} {words}",
                                 self.examples(v, f"{where} AND {day} NOT IN {sentinel_dates}", order="v DESC, n"))
            for k, (spec, low, high) in enumerate(requested.get(name, [])):
                count = a[f"r{i}_{k}"]
                if count:
                    self.add("range", name, f"{_plain(low)}:{_plain(high)}", count, non_null,
                             f"{count} values in {name} outside {_plain(low)} to {_plain(high)}",
                             self.examples(v, _outside(v, kind, low, high), order="v, n DESC"),
                             {"requested": spec})

        if fences:
            items = []
            for name, (low, high, excluded) in fences.items():
                v = q(f"__v{index[name]}")
                items.append((f"x{index[name]}", f"count(*) FILTER (WHERE (CAST({v} AS DOUBLE) < {low!r} "
                                                 f"OR CAST({v} AS DOUBLE) > {high!r}){excluded})"))
            a = self.aggregate(items, "__awb_typed")
            for name, (low, high, excluded) in fences.items():
                v = q(f"__v{index[name]}")
                count = a[f"x{index[name]}"]
                if count:
                    where = f"(CAST({v} AS DOUBLE) < {low!r} OR CAST({v} AS DOUBLE) > {high!r}){excluded}"
                    self.add("extreme", name, None, count, info[name]["non_null"],
                             f"{count} values in {name} beyond five interquartile ranges",
                             self.examples(v, where, order="abs(CAST(v AS DOUBLE)) DESC, n DESC"),
                             {"low_fence": round(low, 6), "high_fence": round(high, 6)})

    def duplicates(self, names, chosen, kinds, info, index, rows):
        everything = ", ".join(q(n) for n in names)
        extra, groups = self.one(f"SELECT coalesce(sum(n - 1), 0), count(*) FROM (SELECT count(*) AS n "
                                 f"FROM __awb_scan GROUP BY {everything} HAVING count(*) > 1)")
        if extra:
            sample = self.db.execute(f"SELECT {everything}, count(*) AS __awb_n FROM __awb_scan "
                                     f"GROUP BY {everything} HAVING count(*) > 1 "
                                     f"ORDER BY __awb_n DESC LIMIT 5").fetchall()
            self.add("duplicate-rows", None, None, extra, rows,
                     f"{extra} extra rows repeating another row exactly ({groups} distinct repeated rows)",
                     [{"value": _plain(dict(zip(names, row[:-1]))), "count": row[-1]} for row in sample])
        keys = [[c.strip() for c in spec.split(",") if c.strip()] for spec in self.options["keys"]]
        explicit = bool(keys)
        if not explicit:
            for name in chosen:
                item = info[name]
                distinct, non_null = item["distinct"] or 0, item["non_null"]
                numeric_text = item["typed_as"] in ("DOUBLE", "DATE", "TIMESTAMP")
                sql_type = item["type"].upper()
                integral = kinds[name] == "text" or (kinds[name] == "number" and not sql_type.startswith(
                    ("FLOAT", "REAL", "DOUBLE", "DECIMAL")))
                # A key-like name repeated often is a reference to another table, not this one's key.
                looks_like_key = ((KEY_NAME.search(name) and distinct >= 0.8 * non_null)
                                  or (non_null >= 20 and distinct >= 0.98 * non_null))
                if integral and not numeric_text and looks_like_key and 0 < distinct < non_null:
                    keys.append([name])
        for key in keys:
            missing = [c for c in key if c not in names]
            if missing:
                raise ValueError(f"--key names unknown columns: {', '.join(missing)}")
            columns = ", ".join(q(c) for c in key)
            present = " AND ".join(f"{q(c)} IS NOT NULL" for c in key)
            label = "+".join(key)
            values, extra = self.one(f"SELECT count(*), coalesce(sum(n) - count(*), 0) FROM (SELECT count(*) AS n "
                                     f"FROM __awb_scan WHERE {present} GROUP BY {columns} HAVING count(*) > 1)")
            if extra:
                sample = self.db.execute(f"SELECT {columns}, count(*) AS __awb_n FROM __awb_scan WHERE {present} "
                                         f"GROUP BY {columns} HAVING count(*) > 1 "
                                         f"ORDER BY __awb_n DESC LIMIT 10").fetchall()
                self.add("duplicate-key", label, None, extra, rows,
                         f"{values} values of {label} occurring more than once ({extra} extra rows)",
                         [{"value": _plain(row[0] if len(key) == 1 else dict(zip(key, row[:-1]))), "count": row[-1]}
                          for row in sample], {"explicit": explicit})
            if explicit:
                (absent,) = self.one(f"SELECT count(*) FROM __awb_scan WHERE NOT ({present})")
                if absent:
                    self.add("null-key", label, None, absent, rows, f"{absent} rows without a complete {label}")

    def orphans(self):
        for k, spec in enumerate(self.options["refs"]):
            column, target, target_column = _parse_ref(spec)
            resolved = _resolve(self.options["root"], self.db, target)
            self.db.execute(f"CREATE OR REPLACE TEMP VIEW __awb_ref{k} AS SELECT * FROM {resolved['relation']}")
            c = f"s.{q(column)}"
            join = (f"FROM __awb_scan s ANTI JOIN __awb_ref{k} r "
                    f"ON CAST({c} AS VARCHAR) = CAST(r.{q(target_column)} AS VARCHAR) WHERE {c} IS NOT NULL")
            rows, values = self.one(f"SELECT count(*), count(DISTINCT {c}) {join}")
            if rows:
                (non_null,) = self.one(f"SELECT count({q(column)}) FROM __awb_scan")
                sample = self.db.execute(f"SELECT {c}, count(*) AS n {join} GROUP BY 1 "
                                         "ORDER BY n DESC, 1 LIMIT 10").fetchall()
                self.add("orphans", column, f"{target}.{target_column}", rows, non_null,
                         f"{rows} rows ({values} values) of {column} without a match in {resolved['label']}.{target_column}",
                         [{"value": _plain(v), "count": n} for v, n in sample], {"reference": spec})

    def null_patterns(self, chosen, info, rows):
        partial = sorted((n for n in chosen if 0 < info[n]["non_null"] < rows),
                         key=lambda n: info[n]["non_null"])[:24]
        if not partial:
            return []
        flags = " || ".join(f"CASE WHEN {q(n)} IS NULL THEN '1' ELSE '0' END" for n in partial)
        anywhere = " OR ".join(f"{q(n)} IS NULL" for n in partial)
        patterns = self.db.execute(f"SELECT {flags} AS p, count(*) AS n FROM __awb_scan WHERE {anywhere} "
                                   "GROUP BY 1 ORDER BY n DESC, p LIMIT 5").fetchall()
        return [{"columns": [partial[j] for j, bit in enumerate(p) if bit == "1"], "rows": n} for p, n in patterns]


def _outside(v, kind, low, high):
    if kind == "number":
        bounds = [f"{v} < {low!r}" if low is not None else None, f"{v} > {high!r}" if high is not None else None]
    else:
        bounds = [f"CAST({v} AS DATE) < DATE {lit(low)}" if low is not None else None,
                  f"CAST({v} AS DATE) > DATE {lit(high)}" if high is not None else None]
    return "(" + " OR ".join(b for b in bounds if b) + ")"


def _parse_bound(text):
    if text == "":
        return None
    try:
        return float(text)
    except ValueError:
        return date.fromisoformat(text).isoformat()


def _parse_range(spec):
    column, _, bounds = spec.partition("=")
    parts = bounds.split(":")
    if not column or len(parts) != 2 or parts == ["", ""]:
        raise ValueError(f"--range {spec}: expected COLUMN=MIN:MAX with at least one bound")
    try:
        low, high = (_parse_bound(p.strip()) for p in parts)
    except ValueError as error:
        raise ValueError(f"--range {spec}: bounds are numbers or ISO dates") from error
    if low is not None and high is not None and type(low) is not type(high):
        raise ValueError(f"--range {spec}: both bounds must be numbers or both dates")
    return column, low, high


def _parse_ref(spec):
    column, _, target = spec.partition("=")
    target, _, target_column = target.rpartition(".")
    if not column or not target or not target_column:
        raise ValueError(f"--ref {spec}: expected COLUMN=TARGET.COLUMN")
    return column, target, target_column


# ----- records, baselines, and output ------------------------------------------------------------

def _recorded(root, name):
    """Map `<name>#<key>` markers in the quality record to their row's ID, status, and recorded count."""
    path = root / "foundation/quality.md"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {}
    marker = re.compile(r"`" + re.escape(name) + r"#([^`]+)`")
    found = {}
    for line in lines:
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
        for key in marker.findall(line):
            cell = next((c for c in cells if f"`{name}#{key}`" in c), "")
            count = re.search(r"\((\d+) of \d+\)", cell)
            found[key.replace("\\|", "|")] = {"id": cells[0], "status": cells[-1],
                                              "count": int(count.group(1)) if count else None}
    return found


def _scan_path(root, target, name):
    if target["kind"] == "query" and target["path"].startswith("investigations/"):
        return root / Path(target["path"]).with_suffix(".scan.json")
    return root / "foundation/scans" / f"{name}.json"


def _load_previous(root, rescan, own_path):
    if rescan is True:
        path = own_path
    elif str(rescan).endswith(".json"):
        path = Path(rescan) if Path(rescan).is_absolute() else root / rescan
    else:
        path = root / "foundation/scans" / f"{rescan}.json"
    try:
        previous = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise ValueError(f"--rescan needs an earlier scan at {os.path.relpath(path, root)}") from error
    if previous.get("schema") != SCHEMA:
        raise ValueError(f"{os.path.relpath(path, root)} is not an {SCHEMA} scan")
    return previous


def _delta(baseline, row_count, columns, issues):
    current = {issue["key"]: issue for issue in issues}
    changes = []
    for before in baseline["issues"]:
        after = current.get(before["key"], {}).get("count", 0)
        change = ("resolved" if after == 0 else "unchanged" if after == before["count"]
                  else "reduced" if after < before["count"] else "increased")
        changes.append({"id": before["id"], "key": before["key"], "before": before["count"],
                        "after": after, "change": change})
    known = {issue["key"] for issue in baseline["issues"]}
    changes += [{"id": i["id"], "key": i["key"], "before": 0, "after": i["count"], "change": "new"}
                for i in issues if i["key"] not in known]
    old = baseline["columns"]
    null_rates = {c: [old[c]["null_rate"], columns[c]["null_rate"]] for c in columns
                  if c in old and old[c]["null_rate"] != columns[c]["null_rate"]}
    types = {c: [old.get(c, {}).get("typed_as") or old.get(c, {}).get("type"),
                 columns.get(c, {}).get("typed_as") or columns.get(c, {}).get("type")]
             for c in sorted(set(old) | set(columns))
             if (old.get(c, {}).get("typed_as") or old.get(c, {}).get("type"))
             != (columns.get(c, {}).get("typed_as") or columns.get(c, {}).get("type"))}
    return {"baseline_scanned_at": baseline["scanned_at"], "rows": [baseline["row_count"], row_count],
            "issues": changes, "null_rates": null_rates, "types": types}


def scan(project_root, dataset, *, keys=(), refs=(), ranges=(), columns=None, name=None, rescan=None,
         typed_threshold=0.9, max_categories=500, today=None):
    """Scan DATASET, write the complete scan file, and return (scan record, its path)."""
    root = Path(project_root).resolve()
    connection = _connect(root, need_views=not (root / dataset).exists() and not Path(dataset).is_absolute())
    try:
        target = _resolve(root, connection, dataset)
        name = name or target["name"]
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._@-]*", name):
            raise ValueError(f"scan name {name!r} must be a simple file name; pass --name")
        path = _scan_path(root, target, name)
        previous = _load_previous(root, rescan, path) if rescan else None
        old = previous["options"] if previous else {}
        options = {"keys": list(keys) or old.get("keys", []), "refs": list(refs) or old.get("refs", []),
                   "ranges": list(ranges) or old.get("ranges", []),
                   "columns": list(columns or []) or old.get("columns", []),
                   "typed_threshold": typed_threshold, "max_categories": max_categories}
        today = (today or date.today()).isoformat()
        worker = Scan(connection, target, {**options, "root": root}, today)
        row_count, info, candidate_keys, null_patterns = worker.run()
    finally:
        connection.close()

    issues = sorted(worker.issues, key=lambda i: (CHECK_ORDER.index(i["check"]), -i["count"], i["key"]))
    baseline = None
    if previous:
        baseline = previous.get("baseline") or {k: previous[k] for k in ("scanned_at", "row_count", "columns", "issues")}
        ids = {i["key"]: i["id"] for i in baseline["issues"] + previous["issues"]}
        numbers = [int(v[1:]) for v in ids.values() if re.fullmatch(r"S\d+", v)]
        next_number = max(numbers, default=0) + 1
        for issue in issues:
            if issue["key"] in ids:
                issue["id"] = ids[issue["key"]]
            else:
                issue["id"], next_number = f"S{next_number}", next_number + 1
    else:
        for number, issue in enumerate(issues, 1):
            issue["id"] = f"S{number}"
    recorded = _recorded(root, name)
    for issue in issues:
        issue["recorded"] = recorded.get(issue["key"])
    delta = _delta(baseline, row_count, info, issues) if baseline else None
    for change in (delta or {}).get("issues", []):
        change["quality"] = (recorded.get(change["key"]) or {}).get("id")

    record = {"schema": SCHEMA, "name": name,
              "target": {k: target[k] for k in ("kind", "label", "path")},
              "scanned_at": datetime.now().astimezone().isoformat(timespec="seconds"),
              "options": options, "row_count": row_count, "columns": info,
              "candidate_keys": candidate_keys, "null_patterns": null_patterns, "issues": issues,
              "baseline": baseline,
              "delta": delta}
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".tmp")
    partial.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(partial, path)
    return record, path


def _compact(issue):
    item = {"id": issue["id"], "key": issue["key"], "count": issue["count"], "of": issue["of"],
            "examples": [f"{json.dumps(e['value'], ensure_ascii=False)[:60]} ({e['count']})"
                         for e in issue["examples"][:3]]}
    detail = issue.get("detail") or {}
    for field in ("formats", "note", "low_fence", "high_fence", "similarity"):
        if detail.get(field):
            item[field] = detail[field]
    return item


def summary(record, path, root, limit=25):
    """Return the compact stdout view of a scan record."""
    out = {"scan": os.path.relpath(path, Path(root).resolve()), "target": record["target"]["label"],
           "rows": record["row_count"], "columns": len(record["columns"])}
    open_issues = [i for i in record["issues"] if not i["recorded"]]
    if record["delta"]:
        delta = record["delta"]
        out["delta"] = {"rows": delta["rows"], "issues": [
            f"{d['id']} {d['key']}: {d['before']} -> {d['after']} {d['change']}"
            + (f" ({d['quality']})" if d.get("quality") else "") for d in delta["issues"]]}
        for field in ("null_rates", "types"):
            if delta[field]:
                out["delta"][field] = delta[field]
        new = {d["key"] for d in delta["issues"] if d["change"] == "new"}
        open_issues = [i for i in open_issues if i["key"] in new]
    out["issues"] = [_compact(i) for i in open_issues[:limit]]
    if len(open_issues) > limit:
        out["more_issues"] = len(open_issues) - limit
    recorded = [{"id": i["id"], "quality": i["recorded"]["id"], "status": i["recorded"]["status"], "count": i["count"]}
                | ({"recorded_count": i["recorded"]["count"]} if i["recorded"].get("count") is not None else {})
                for i in record["issues"] if i["recorded"]]
    if recorded:
        out["recorded"] = recorded
    if record["candidate_keys"]:
        out["candidate_keys"] = record["candidate_keys"]
    nulls = sorted(((c, v["null_rate"]) for c, v in record["columns"].items() if v["null_rate"]),
                   key=lambda item: -item[1])
    if nulls:
        out["null_rates"] = dict(nulls[:8])
        if record["null_patterns"]:
            out["null_patterns"] = record["null_patterns"][:3]
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("root", help="workbench root")
    parser.add_argument("dataset", help="view, dataset, publication or acquisition directory, data file, or .sql query")
    parser.add_argument("--key", action="append", default=[], help="candidate key columns, comma-separated; repeatable")
    parser.add_argument("--ref", action="append", default=[], help="COLUMN=TARGET.COLUMN referential check; repeatable")
    parser.add_argument("--range", action="append", default=[], dest="ranges",
                        help="COLUMN=MIN:MAX valid range, numbers or ISO dates, one side may be empty; repeatable")
    parser.add_argument("--columns", help="limit per-column checks to these comma-separated columns")
    parser.add_argument("--name", help="scan name (default: view name, <dataset>@<publication>, or file stem)")
    parser.add_argument("--rescan", nargs="?", const=True,
                        help="compare with the baseline of this scan's earlier file, or of the named scan")
    parser.add_argument("--typed-threshold", type=float, default=0.9,
                        help="share of text values that must parse before a column counts as typed")
    parser.add_argument("--max-categories", type=int, default=500,
                        help="largest distinct count checked for spelling variants")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    try:
        record, path = scan(root, args.dataset, keys=args.key, refs=args.ref, ranges=args.ranges,
                            columns=[c.strip() for c in args.columns.split(",")] if args.columns else None,
                            name=args.name, rescan=args.rescan, typed_threshold=args.typed_threshold,
                            max_categories=args.max_categories)
    except Exception as error:  # report any failure compactly; the scan changes nothing on failure
        print(json.dumps({"error": f"{type(error).__name__}: {error}"}), file=sys.stderr)
        return 2
    print(json.dumps(summary(record, path, root), ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
