"""Standard exploration of one canonical view or publication for an investigation.

Run with Python 3.10+ and duckdb: eda_scan.py PROJECT_ROOT DATASET [options]. DATASET is a
canonical view name, loaded through the project's session() helper, or a project-relative
publication directory or Parquet file. Scope, measure, and dimensions come from the
investigation's settings unless options override them. Writes the complete scan to
investigations/<name>/exploration/eda/<dataset>[-<label>].json and prints a compact summary.
Writes nothing else: no findings, state, history, or evidence.
"""

import argparse
from datetime import date, datetime, time, timezone
from decimal import Decimal
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import statistics
import sys

FORMAT = "awb-eda/1"
SETTINGS_KEYS = ("where", "date_column", "period_start", "period_end", "measure", "dimensions",
                 "key", "period")
PERIODS = ("day", "week", "month", "quarter", "year")
PERIOD_DAYS = {"day": 1, "week": 7, "month": 30.4, "quarter": 91.3, "year": 365.25}
MAX_PERIODS = 2000
QUANTILES = (0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99)
NUMERIC = re.compile(r"^(U?(TINYINT|SMALLINT|INTEGER|BIGINT|HUGEINT)|FLOAT|DOUBLE|REAL|DECIMAL.*)$")
TEMPORAL = re.compile(r"^(DATE|TIMESTAMP.*)$")
MAX_PATTERN_COLUMNS = 12
MAX_ASSOCIATION_COLUMNS = 15
TABLE_ROWS = 15


class ScanError(Exception):
    """A usage or data problem the caller fixes; reported without a traceback."""


def q(name):
    return '"' + str(name).replace('"', '""') + '"'


def lit(value):
    return "'" + str(value).replace("'", "''") + "'"


def plain(value):
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        return None if math.isnan(value) else value if math.isfinite(value) else str(value)
    if isinstance(value, Decimal):
        return plain(float(value))
    if isinstance(value, (date, datetime, time)):
        return value.isoformat()
    if isinstance(value, (list, tuple)):
        return [plain(item) for item in value]
    return str(value)


def ratio(part, whole):
    return part / whole if whole else None


# ---------------------------------------------------------------- project context

def active_investigation(root):
    try:
        readme = (root / "README.md").read_text(encoding="utf-8")
    except OSError:
        return None
    match = re.search(r"^Active investigation:[ \t]*(.*)$", readme, re.M)
    value = (match[1].strip().strip("`") if match else "")
    link = re.fullmatch(r"\[[^\]]*\]\(([^)]+)\)", value)
    value = link[1] if link else value
    path = re.fullmatch(r"(?:\./)?investigations/([A-Za-z0-9][A-Za-z0-9_.-]*)(?:/state\.md)?", value)
    value = path[1] if path else value
    return value if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", value or "") and value != "none" else None


def load_settings(path):
    """Return (mapping, note). A missing or unreadable file yields an empty mapping and a note."""
    if not path.is_file():
        return {}, f"no settings file at {path.name}"
    if path.suffix != ".toml":
        return {}, f"settings format {path.suffix or 'unknown'} is not read; pass options"
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            return {}, "TOML settings need Python 3.11+ or tomli; pass options"
    try:
        return tomllib.loads(path.read_text(encoding="utf-8")), None
    except (OSError, ValueError) as error:
        return {}, f"settings unreadable: {error}"


def resolve_settings(data, dataset):
    """Find each scan key in [eda.<dataset>], [eda], [scope], then the top level."""
    eda = data.get("eda") if isinstance(data.get("eda"), dict) else {}
    tables = [(f"eda.{dataset}", eda.get(dataset)), ("eda", eda),
              ("scope", data.get("scope")), ("", data)]
    found, used = {}, set()
    for key in SETTINGS_KEYS:
        for name, table in tables:
            if isinstance(table, dict) and key in table and not isinstance(table[key], dict):
                found[key] = (table[key], f"{name}.{key}" if name else key)
                used.add(found[key][1])
                break
    unused = [key for key in data if key != "eda" and key not in used]
    if isinstance(data.get("scope"), dict):
        unused = [key for key in unused if key != "scope"]
        unused += [f"scope.{key}" for key in data["scope"] if f"scope.{key}" not in used]
    return found, unused


def as_list(value):
    if value is None:
        return []
    return [str(item) for item in value] if isinstance(value, (list, tuple)) else [str(value)]


def open_session(root):
    path = root / "src/preparation/landing.py"
    if not path.is_file():
        raise ScanError("the scan needs src/preparation/landing.py for session(); install the "
                        "workbench helpers with the awb-init skill's scripts/install_helpers.py")
    spec = importlib.util.spec_from_file_location("awb_project_landing", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        return module.session(root)
    except ImportError as error:
        raise ScanError(f"{error}; install duckdb in the interpreter that runs the project") from error


def resolve_source(connection, root, dataset):
    """Return (sql relation, record, output name) for a view or a publication path."""
    exists = connection.execute("SELECT count(*) FROM information_schema.tables WHERE table_name = ?",
                                [dataset]).fetchone()[0]
    if exists:
        definition = None
        pattern = re.compile(rf"CREATE\s+(?:OR\s+REPLACE\s+)?(?:TEMP\w*\s+)?VIEW\s+(?:IF\s+NOT\s+EXISTS\s+)?"
                             rf"\"?{re.escape(dataset)}\"?(?:\s|\()", re.I)
        for path in sorted((root / "foundation/views").glob("*.sql")):
            try:
                if pattern.search(path.read_text(encoding="utf-8")):
                    definition = str(path.relative_to(root))
                    break
            except (OSError, UnicodeError):
                continue
        return q(dataset), {"name": dataset, "kind": "view", "definition": definition}, dataset
    path = (root / dataset).resolve()
    if path.is_dir() or (path.is_file() and path.suffix == ".parquet"):
        if root not in path.parents:
            raise ScanError(f"{dataset} is outside the project")
        pattern = str(path / "**" / "*.parquet") if path.is_dir() else str(path)
        name = "-".join(path.relative_to(root).parts[-2:]) if path.is_dir() else path.stem
        record = {"name": name, "kind": "publication", "path": str(path.relative_to(root))}
        return f"read_parquet({lit(pattern)}, union_by_name = true)", record, name
    raise ScanError(f"{dataset} is neither a view loaded from foundation/views nor a publication "
                    "path under the project")


# ---------------------------------------------------------------- computation

def kind_of(column_type):
    if NUMERIC.match(column_type):
        return "numeric"
    if TEMPORAL.match(column_type):
        return "temporal"
    if column_type == "BOOLEAN":
        return "boolean"
    if column_type == "VARCHAR":
        return "text"
    return "other"


def column_stats(connection, columns, rows):
    exprs, slots = [], []

    def add(name, stat, sql):
        slots.append((name, stat))
        exprs.append(f"{sql} AS s{len(exprs)}")

    for column in columns:
        name, kind, c = column["name"], column["kind"], q(column["name"])
        add(name, "non_null", f"count({c})")
        add(name, "distinct", f"count(DISTINCT {c})" if kind != "other"
            else f"count(DISTINCT CAST({c} AS VARCHAR))")
        if kind == "numeric":
            d = f"CAST({c} AS DOUBLE)"
            add(name, "min", f"min({c})")
            add(name, "max", f"max({c})")
            add(name, "mean", f"avg({d})")
            add(name, "sd", f"stddev_samp({d})")
            add(name, "quantiles", f"quantile_cont({d}, [{', '.join(map(str, QUANTILES))}])")
            add(name, "zeros", f"count(*) FILTER (WHERE {d} = 0)")
            add(name, "negatives", f"count(*) FILTER (WHERE {d} < 0)")
        elif kind == "temporal":
            add(name, "min", f"min({c})")
            add(name, "max", f"max({c})")
        elif kind == "text":
            add(name, "blank", f"count(*) FILTER (WHERE trim({c}) = '')")
            add(name, "distinct_normalized", f"count(DISTINCT lower(trim({c})))")
    values = connection.execute(f"SELECT {', '.join(exprs)} FROM __eda").fetchone()
    stats = {column["name"]: {} for column in columns}
    for (name, stat), value in zip(slots, values):
        stats[name][stat] = value
    for column in columns:
        s = stats[column["name"]]
        column["nulls"] = rows - s["non_null"]
        column["null_rate"] = ratio(column["nulls"], rows)
        column["distinct"] = s["distinct"]
        column["unique"] = rows > 0 and s["non_null"] == rows and s["distinct"] == rows and bool(keyish(column))
        if column["kind"] == "numeric":
            quantiles = s["quantiles"] or [None] * len(QUANTILES)
            column["numeric"] = {
                "min": plain(s["min"]), "max": plain(s["max"]), "mean": plain(s["mean"]),
                "sd": plain(s["sd"]), "zeros": s["zeros"], "negatives": s["negatives"],
                "quantiles": {f"p{round(p * 100)}": plain(v) for p, v in zip(QUANTILES, quantiles)}}
        elif column["kind"] == "temporal":
            column["temporal"] = {"min": s["min"], "max": s["max"]}
        elif column["kind"] == "text":
            column["text"] = {"blank": s["blank"],
                              "case_or_space_variants": s["distinct"] - s["distinct_normalized"]}
    outliers(connection, [c for c in columns if c["kind"] == "numeric"])
    for column in columns:
        if (column.get("text") or {}).get("case_or_space_variants"):
            c = q(column["name"])
            column["text"]["variant_examples"] = [plain(values) for values, in connection.execute(
                f"SELECT list(DISTINCT {c} ORDER BY {c}) FROM __eda WHERE {c} IS NOT NULL "
                f"GROUP BY lower(trim({c})) HAVING count(DISTINCT {c}) > 1 ORDER BY count(*) DESC LIMIT 3").fetchall()]


def outliers(connection, columns):
    """Count values beyond 1.5 and 3 interquartile ranges from the quartiles."""
    exprs, owners = [], []
    for column in columns:
        quantiles = column["numeric"]["quantiles"]
        q1, q3 = quantiles["p25"], quantiles["p75"]
        if q1 is None or q3 is None or q3 == q1:
            column["numeric"]["outliers"] = None
            continue
        d, iqr = f"CAST({q(column['name'])} AS DOUBLE)", q3 - q1
        for factor in (1.5, 3):
            exprs.append(f"count(*) FILTER (WHERE {d} < {q1 - factor * iqr!r} OR {d} > {q3 + factor * iqr!r})")
        owners.append(column)
    if not exprs:
        return
    values = connection.execute(f"SELECT {', '.join(exprs)} FROM __eda").fetchone()
    for index, column in enumerate(owners):
        column["numeric"]["outliers"] = {"beyond_1_5_iqr": values[2 * index],
                                         "beyond_3_iqr": values[2 * index + 1]}


def top_values(connection, columns, rows, top):
    """Most frequent values with their share of non-null rows; skipped for unique columns."""
    for column in columns:
        wanted = column["kind"] in {"text", "boolean"} or (
            column["kind"] == "numeric" and column["distinct"] <= top)
        if not (wanted and column["distinct"] and not column["unique"]):
            continue
        c, non_null = q(column["name"]), rows - column["nulls"]
        found = connection.execute(
            f"SELECT CAST({c} AS VARCHAR) AS value, count(*) AS n FROM __eda WHERE {c} IS NOT NULL "
            f"GROUP BY 1 ORDER BY n DESC, value LIMIT {int(top)}").fetchall()
        column["top"] = [{"value": value, "count": n, "share": ratio(n, non_null)} for value, n in found]
        column["other_share"] = ratio(non_null - sum(n for _, n in found), non_null)


def choose_period(low, high, override):
    span = max((to_date(high) - to_date(low)).days, 0)
    period = override or ("day" if span <= 92 else "month" if span <= 3660 else "year")
    while span / PERIOD_DAYS[period] > MAX_PERIODS and period != "year":
        period = PERIODS[PERIODS.index(period) + 1]
    return period


def to_date(value):
    return value.date() if isinstance(value, datetime) else value


def coverage(connection, column, period):
    """Rows per period across the column's whole range, with empty periods as gaps."""
    c, p = q(column["name"]), period
    series = connection.execute(f"""
        WITH counts AS (
            SELECT CAST(date_trunc('{p}', {c}) AS DATE) AS period, count(*) AS n
            FROM __eda WHERE {c} IS NOT NULL GROUP BY 1),
        periods AS (
            SELECT CAST(unnest(generate_series(lo, hi, INTERVAL 1 {p.upper()})) AS DATE) AS period
            FROM (SELECT CAST(date_trunc('{p}', min({c})) AS TIMESTAMP) AS lo,
                         CAST(max({c}) AS TIMESTAMP) AS hi FROM __eda))
        SELECT periods.period, coalesce(counts.n, 0) FROM periods LEFT JOIN counts USING (period)
        ORDER BY 1""").fetchall()
    gaps, start = [], None
    for index, (when, n) in enumerate(series):
        if n == 0 and start is None:
            start = index
        if start is not None and (n != 0 or index == len(series) - 1):
            end = index if n == 0 else index - 1
            gaps.append({"from": series[start][0].isoformat(), "to": series[end][0].isoformat(),
                         "periods": end - start + 1})
            start = None
    counts = [n for _, n in series if n]
    median = statistics.median(counts) if counts else 0
    low = [{"period": when.isoformat(), "rows": n, "edge": index in (0, len(series) - 1)}
           for index, (when, n) in enumerate(series) if 0 < n < 0.5 * median]
    return {"period": period, "periods": len(series), "median_rows": median, "gaps": gaps,
            "low_periods": low, "series": [{"period": w.isoformat(), "rows": n} for w, n in series]}


def grain(connection, columns, rows, key):
    result = {"rows": rows, "duplicate_rows": rows - connection.execute(
        "SELECT count(*) FROM (SELECT DISTINCT * FROM __eda)").fetchone()[0]}
    result["single_column_keys"] = [c["name"] for c in columns if c["unique"]]
    # A nearly unique column makes any pair containing it unique, so it is reported, not paired.
    near = [c for c in columns if not c["unique"] and rows and c["distinct"] >= 0.95 * rows
            and keyish(c)]
    result["near_unique_columns"] = [{"column": c["name"], "distinct": c["distinct"], "nulls": c["nulls"]}
                                     for c in near]
    result["column_pair_keys"] = []
    if not result["single_column_keys"] and rows:
        ranked = sorted((c for c in columns if c["nulls"] == 0 and c["distinct"] > 1 and keyish(c)
                         and c not in near), key=lambda c: -c["distinct"])[:8]
        pairs = [(a["name"], b["name"]) for i, a in enumerate(ranked) for b in ranked[i + 1:]]
        if pairs:
            exprs = [f"count(DISTINCT ({q(a)}, {q(b)}))" for a, b in pairs]
            values = connection.execute(f"SELECT {', '.join(exprs)} FROM __eda").fetchone()
            result["column_pair_keys"] = [list(pair) for pair, n in zip(pairs, values) if n == rows]
    if key:
        names = {c["name"] for c in columns}
        missing = [k for k in key if k not in names]
        if missing:
            result["declared_key"] = {"columns": key, "missing_columns": missing}
        else:
            keys = ", ".join(q(k) for k in key)
            groups, members = connection.execute(
                f"SELECT count(*), coalesce(sum(n), 0) FROM (SELECT count(*) AS n FROM __eda "
                f"GROUP BY {keys} HAVING count(*) > 1)").fetchone()
            nulls = connection.execute(
                f"SELECT count(*) FROM __eda WHERE {' OR '.join(q(k) + ' IS NULL' for k in key)}").fetchone()[0]
            result["declared_key"] = {"columns": key, "duplicate_keys": groups,
                                      "rows_in_duplicate_keys": members, "rows_with_null_key": nulls}
    return result


def keyish(column):
    """Identifier-like types; measured floats are not key candidates."""
    return column["kind"] in {"text", "temporal", "boolean"} or (
        column["kind"] == "numeric" and re.match(r"^U?(TINYINT|SMALLINT|INTEGER|BIGINT|HUGEINT)$", column["type"]))


def null_patterns(connection, columns, date_column, period):
    nullable = sorted((c for c in columns if c["nulls"]), key=lambda c: -c["nulls"])[:MAX_PATTERN_COLUMNS]
    result = {"columns": [c["name"] for c in nullable], "patterns": [], "by_period": None}
    if not nullable:
        return result
    flags = ", ".join(f"{q(c['name'])} IS NULL AS f{i}" for i, c in enumerate(nullable))
    for row in connection.execute(f"SELECT {flags}, count(*) AS n FROM __eda GROUP BY ALL "
                                  "ORDER BY n DESC LIMIT 10").fetchall():
        result["patterns"].append({"null_columns": [c["name"] for c, flag in zip(nullable, row) if flag],
                                   "rows": row[-1]})
    if date_column:
        d = q(date_column)
        counts = ", ".join(f"count({q(c['name'])})" for c in nullable)
        series = connection.execute(
            f"SELECT CAST(date_trunc('{period}', {d}) AS DATE) AS period, count(*) AS n, {counts} "
            f"FROM __eda WHERE {d} IS NOT NULL GROUP BY 1 ORDER BY 1").fetchall()
        result["by_period"] = {"date_column": date_column, "period": period, "series": [
            {"period": row[0].isoformat(), "rows": row[1],
             "null_rates": {c["name"]: ratio(row[1] - row[2 + i], row[1]) for i, c in enumerate(nullable)}}
            for row in series]}
    return result


def measure_scan(connection, measure, dimensions, date_column, period, min_group, top):
    m = f"CAST(({measure['sql']}) AS DOUBLE)"
    n, mean, sd, total, median, var_pop = connection.execute(
        f"SELECT count({m}), avg({m}), stddev_samp({m}), sum({m}), median({m}), var_pop({m}) "
        "FROM __eda").fetchone()
    result = {"expression": measure["label"], "source": measure["source"],
              "overall": {"n": n, "mean": mean, "sd": sd, "sum": total, "median": median},
              "by_dimension": [], "over_time": None, "contrary": []}
    total_ss = (var_pop or 0) * n
    for dimension in dimensions:
        g = f"CAST(({dimension['sql']}) AS VARCHAR)"
        groups = connection.execute(
            f"SELECT {g} AS grp, count(*) AS rows, count({m}) AS n, avg({m}) AS mean, "
            f"stddev_samp({m}) AS sd, sum({m}) AS total, median({m}) AS median "
            f"FROM __eda GROUP BY 1 ORDER BY rows DESC, grp").fetchall()
        between = sum(gn * (gm - mean) ** 2 for _, _, gn, gm, *_ in groups if gn and gm is not None) \
            if mean is not None else 0
        entry = {"dimension": dimension["label"], "groups": len(groups),
                 "eta_squared": ratio(between, total_ss),
                 "values": [{"group": grp, "rows": rows, "n": gn, "mean": gm, "sd": gsd, "sum": gt,
                             "median": gmed} for grp, rows, gn, gm, gsd, gt, gmed in groups[:max(top, 50)]]}
        sized = [v for v in entry["values"] if v["n"] >= min_group and v["mean"] is not None]
        entry["highest"] = max(sized, key=lambda v: v["mean"], default=None)
        entry["lowest"] = min(sized, key=lambda v: v["mean"], default=None)
        result["by_dimension"].append(entry)
    if date_column and n:
        d = q(date_column)
        series = connection.execute(
            f"SELECT CAST(date_trunc('{period}', {d}) AS DATE) AS period, count(*), count({m}), "
            f"avg({m}), sum({m}) FROM __eda WHERE {d} IS NOT NULL GROUP BY 1 ORDER BY 1").fetchall()
        result["over_time"] = {"date_column": date_column, "period": period, "series": [
            {"period": w.isoformat(), "rows": r, "n": k, "mean": a, "sum": s} for w, r, k, a, s in series]}
        result["contrary"] = contrary(connection, m, dimensions, d, min_group, top, result)
    return result


def contrary(connection, m, dimensions, d, min_group, top, result):
    """Groups whose mean moves against the overall mean between the two halves of the date range."""
    low, high = connection.execute(f"SELECT min({d}), max({d}) FROM __eda").fetchone()
    if low is None or low == high:
        return []
    low_ts = datetime.combine(low, time()) if not isinstance(low, datetime) else low
    high_ts = datetime.combine(high, time()) if not isinstance(high, datetime) else high
    middle = (low_ts + (high_ts - low_ts) / 2).replace(tzinfo=None).isoformat(sep=" ")
    early = f"CAST({d} AS TIMESTAMP) < TIMESTAMP {lit(middle)}"
    before, after = connection.execute(
        f"SELECT avg({m}) FILTER (WHERE {early}), avg({m}) FILTER (WHERE NOT ({early})) "
        f"FROM __eda WHERE {d} IS NOT NULL").fetchone()
    result["halves"] = {"split_at": middle, "before": before, "after": after}
    if before is None or after is None or before == after:
        return []
    found = []
    for dimension in dimensions:
        g = f"CAST(({dimension['sql']}) AS VARCHAR)"
        late = f"NOT ({early})"
        for grp, nb, b, sb, na, a, sa in connection.execute(
                f"SELECT {g}, count({m}) FILTER (WHERE {early}), avg({m}) FILTER (WHERE {early}), "
                f"stddev_samp({m}) FILTER (WHERE {early}), count({m}) FILTER (WHERE {late}), "
                f"avg({m}) FILTER (WHERE {late}), stddev_samp({m}) FILTER (WHERE {late}) "
                f"FROM __eda WHERE {d} IS NOT NULL GROUP BY 1 ORDER BY count(*) DESC, 1 "
                f"LIMIT {int(top)}").fetchall():
            if nb < min_group or na < min_group or None in (b, a, sb, sa):
                continue
            # Opposite direction and a move larger than about two standard errors, so noise is not flagged.
            error = math.sqrt(sb ** 2 / nb + sa ** 2 / na)
            if (a - b) * (after - before) < 0 and abs(a - b) > 2 * error:
                found.append({"dimension": dimension["label"], "group": grp, "before": b, "after": a,
                              "n_before": nb, "n_after": na, "standard_error": error})
    return found


def associations(connection, columns, measure, min_r):
    candidates = [c for c in columns if c["kind"] == "numeric" and not c["unique"] and c["distinct"] > 1]
    candidates = sorted(candidates, key=lambda c: c["nulls"])[:MAX_ASSOCIATION_COLUMNS]
    items = [(c["name"], f"CAST({q(c['name'])} AS DOUBLE)") for c in candidates]
    if measure and measure["label"] not in {name for name, _ in items}:
        items.append((measure["label"], f"CAST(({measure['sql']}) AS DOUBLE)"))
    pairs = [(a, b) for i, a in enumerate(items) for b in items[i + 1:]]
    if not pairs:
        return {"method": "pearson", "columns": [n for n, _ in items], "pairs": [], "min_r": min_r}
    exprs = []
    for (_, a), (_, b) in pairs:
        exprs += [f"corr({a}, {b})", f"count(*) FILTER (WHERE {a} IS NOT NULL AND {b} IS NOT NULL)"]
    values = connection.execute(f"SELECT {', '.join(exprs)} FROM __eda").fetchone()
    found = [{"a": a[0], "b": b[0], "r": plain(values[2 * i]), "n": values[2 * i + 1]}
             for i, (a, b) in enumerate(pairs)]
    found.sort(key=lambda p: -abs(p["r"]) if p["r"] is not None else 0)
    return {"method": "pearson", "columns": [n for n, _ in items], "min_r": min_r, "pairs": found}


# ---------------------------------------------------------------- reading the scan

def anomalies(scan, today):
    """Mechanical flags. Route awb-clean marks a possible shared data problem to confirm first."""
    found = []

    def add(kind, column, detail, route):
        found.append({"kind": kind, "column": column, "detail": detail, "route": route})

    g = scan["grain"]
    if g["duplicate_rows"]:
        add("duplicate-rows", None, f"{g['duplicate_rows']:,} rows repeat another row exactly", "awb-clean")
    declared = g.get("declared_key") or {}
    if declared.get("missing_columns"):
        add("key-missing", ", ".join(declared["columns"]),
            f"declared key columns absent: {', '.join(declared['missing_columns'])}", "investigation")
    elif declared.get("duplicate_keys") or declared.get("rows_with_null_key"):
        add("key-violated", ", ".join(declared["columns"]),
            f"{declared['duplicate_keys']:,} duplicated key values covering {declared['rows_in_duplicate_keys']:,} "
            f"rows; {declared['rows_with_null_key']:,} rows with a null key", "awb-clean")
    for c in scan["columns"]:
        name = c["name"]
        if scan["rows"] and c["nulls"] == scan["rows"]:
            add("all-null", name, "every row is null", "awb-clean")
            continue
        if c["distinct"] == 1 and scan["rows"] > 1:
            add("constant", name, "a single value in scope", "investigation")
        if c["null_rate"] and c["null_rate"] >= 0.2:
            add("high-nulls", name, f"{c['null_rate']:.1%} null", "investigation")
        text = c.get("text") or {}
        if text.get("case_or_space_variants"):
            examples = "; ".join(" / ".join(shown(v) for v in group) for group in text["variant_examples"])
            add("case-or-space-variants", name, f"spellings differing only by case or spaces: {examples}",
                "awb-clean")
        if text.get("blank"):
            add("blank-strings", name, f"{text['blank']:,} blank strings beside nulls", "awb-clean")
        numeric = c.get("numeric") or {}
        non_null = scan["rows"] - c["nulls"]
        if numeric.get("negatives") and ratio(numeric["negatives"], non_null) < 0.01:
            add("rare-negatives", name, f"{numeric['negatives']:,} negative values "
                f"({ratio(numeric['negatives'], non_null):.2%})", "awb-clean")
        extreme = (numeric.get("outliers") or {}).get("beyond_3_iqr")
        if extreme:
            add("extreme-values", name, f"{extreme:,} values beyond 3 IQR "
                f"(range {fmt(numeric['min'])} to {fmt(numeric['max'])})", "investigation")
        temporal = c.get("temporal") or {}
        if temporal.get("max") and to_date(plain_date(temporal["max"])) > today:
            add("future-dates", name, f"latest value {temporal['max']} is after {today}", "awb-clean")
        if temporal.get("min") and to_date(plain_date(temporal["min"])) < date(1901, 1, 1):
            add("sentinel-dates", name, f"earliest value {temporal['min']} looks like a placeholder", "awb-clean")
        cov = temporal.get("coverage") or {}
        if cov.get("gaps"):
            spans = ", ".join(f"{g['from']}..{g['to']}" if g["from"] != g["to"] else g["from"]
                              for g in cov["gaps"][:3])
            add("period-gaps", name, f"empty {cov['period']}s: {sum(g['periods'] for g in cov['gaps'])}, "
                f"{spans}{' …' if len(cov['gaps']) > 3 else ''}", "awb-clean")
        inner = [p for p in cov.get("low_periods", []) if not p["edge"]]
        if inner:
            add("low-periods", name, f"{len(inner)} {cov['period']}s under half the median rows "
                f"({cov['median_rows']:,}), first {inner[0]['period']}", "awb-clean")
    by_period = (scan["null_patterns"] or {}).get("by_period")
    if by_period:
        rows = [p for p in by_period["series"] if p["rows"] >= 10]
        for name in scan["null_patterns"]["columns"]:
            rates = [p["null_rates"][name] for p in rows]
            if len(rates) > 1 and max(rates) - min(rates) >= 0.25:
                add("null-shift", name, f"null rate ranges {min(rates):.0%} to {max(rates):.0%} across "
                    f"{by_period['period']}s of {by_period['date_column']}", "awb-clean")
    for pair in scan["associations"]["pairs"]:
        if pair["r"] is not None and abs(pair["r"]) >= 0.98:
            add("near-duplicate-columns", f"{pair['a']}, {pair['b']}", f"r = {pair['r']:.3f}", "investigation")
    measure = scan.get("measure") or {}
    for item in measure.get("contrary", []):
        halves = measure["halves"]
        add("contrary-trend", item["dimension"], f"{shown(item['group'])}: mean {fmt(item['before'])} → "
            f"{fmt(item['after'])} while overall {fmt(halves['before'])} → {fmt(halves['after'])}", "investigation")
    return found


def shown(value):
    """Quote a value whose spaces would otherwise be invisible."""
    return f'"{value}"' if isinstance(value, str) and (value != value.strip() or not value) else str(value)


def plain_date(value):
    return value if isinstance(value, (date, datetime)) else date.fromisoformat(str(value)[:10])


def suggested_records(scan, path):
    issues, steps = [], []
    for item in scan["anomalies"]:
        where = f"{scan['dataset']['name']}.{item['column']}" if item["column"] else scan["dataset"]["name"]
        if item["route"] == "awb-clean" and len(issues) < 5:
            issues.append(f"- {where}: {item['detail']}. Possible shared data problem; confirm, then hand "
                          f"to awb-clean (EDA scan `{path}`).")
    measure = scan.get("measure") or {}
    for item in measure.get("contrary", [])[:4]:
        halves = measure["halves"]
        steps.append(f"- Check whether {item['dimension']} {shown(item['group'])} moving against the overall "
                     f"{measure['expression']} trend (mean {fmt(item['before'])} → {fmt(item['after'])}; overall "
                     f"{fmt(halves['before'])} → {fmt(halves['after'])}) holds in the composition entry.")
    ranked = sorted((d for d in measure.get("by_dimension", []) if d["eta_squared"] is not None),
                    key=lambda d: -d["eta_squared"])
    if ranked and len(steps) < 5:
        best = ranked[0]
        steps.append(f"- Test {best['dimension']} as an explanation of {measure['expression']} in the composition "
                     f"entry (EDA: {best['eta_squared']:.0%} of its variance across {best['groups']} groups).")
    return {"unresolved_issues": issues, "next_steps": steps}


# ---------------------------------------------------------------- scan and report

def scan_dataset(root, dataset, options):
    root = Path(root).resolve()
    investigation = options.investigation or active_investigation(root)
    if not investigation:
        raise ScanError("no active investigation in README.md; pass --investigation")
    folder = root / "investigations" / investigation
    if not folder.is_dir():
        raise ScanError(f"investigations/{investigation} does not exist")
    settings_path = root / options.settings if options.settings else folder / "settings.toml"
    data, settings_note = load_settings(settings_path)
    connection = open_session(root)
    try:
        source, record, name = resolve_source(connection, root, dataset)
        settings, unused = resolve_settings(data, record["name"])
        chosen = {}
        for key, value in (("where", options.where), ("date_column", options.date_column),
                           ("period_start", options.start), ("period_end", options.end),
                           ("measure", options.measure), ("dimensions", options.dimension),
                           ("key", options.key), ("period", options.period)):
            if value:
                chosen[key] = (value, "option")
            elif key in settings and not (options.no_scope and key in {"where", "period_start", "period_end"}):
                chosen[key] = settings[key]
        period_choice = as_scalar(chosen.get("period"))
        if period_choice and period_choice not in PERIODS:
            raise ScanError(f"period {period_choice} ({chosen['period'][1]}) is not one of {', '.join(PERIODS)}")
        connection.execute(f"CREATE TEMP VIEW __eda_all AS SELECT * FROM {source}")
        names = [row[0] for row in connection.execute("DESCRIBE __eda_all").fetchall()]
        scope = scope_filters(chosen, names)
        condition = " AND ".join(f"({f['sql']})" for f in scope["applied"]) or "TRUE"
        try:
            connection.execute(f"CREATE TEMP VIEW __eda AS SELECT * FROM __eda_all WHERE {condition}")
            rows = connection.execute("SELECT count(*) FROM __eda").fetchone()[0]
        except Exception as error:
            raise ScanError(f"scope filter failed on {record['name']}: {error}; correct the settings "
                            "or pass --where or --no-scope") from error
        scope["rows_before"] = connection.execute("SELECT count(*) FROM __eda_all").fetchone()[0]
        if not rows:
            applied = "; ".join(f"{f['sql']} ({f['source']})" for f in scope["applied"]) or "none"
            raise ScanError(f"scope selects 0 of {scope['rows_before']:,} rows of {record['name']}; "
                            f"filters: {applied}")
        scope["rows"] = rows
        scope["settings_path"] = str(settings_path.relative_to(root)) if root in settings_path.parents else str(settings_path)
        scope["settings_note"] = settings_note
        scope["settings_unused"] = unused
        columns = [{"name": n, "type": t, "kind": kind_of(t)}
                   for n, t, *_ in connection.execute("DESCRIBE __eda").fetchall()]
        column_stats(connection, columns, rows)
        top_values(connection, columns, rows, options.top)
        temporal = [c for c in columns if c["kind"] == "temporal" and c["temporal"]["min"] is not None]
        for c in temporal:
            c["temporal"]["coverage"] = coverage(
                connection, c, choose_period(c["temporal"]["min"], c["temporal"]["max"], period_choice))
            c["temporal"]["min"], c["temporal"]["max"] = plain(c["temporal"]["min"]), plain(c["temporal"]["max"])
        date_column, date_source = pick_date(chosen, temporal)
        period = next((c["temporal"]["coverage"]["period"] for c in temporal if c["name"] == date_column), None)
        if "date_column" in chosen and chosen["date_column"][0] != date_column:
            scope["skipped"].append({"setting": chosen["date_column"][1],
                                     "reason": f"{chosen['date_column'][0]} is not a populated date column here"})

        def usable(item):
            # An option that fails is a usage error; a shared setting may not fit every dataset.
            if not item:
                return None
            try:
                connection.execute(f"SELECT ({item['sql']}) FROM __eda LIMIT 0")
                return item
            except Exception as error:
                if item["source"] == "option":
                    raise ScanError(f"{item['label']} is not a valid expression on {record['name']}: {error}") from error
                scope["skipped"].append({"setting": item["source"], "reason": f"{item['label']} is not valid here"})
                return None

        measure = usable(expression(chosen.get("measure"), names))
        dimensions = [d for d in (usable(expression((value, chosen["dimensions"][1]), names))
                                  for value in as_list(chosen["dimensions"][0])) if d] if "dimensions" in chosen else []
        if measure and not dimensions:
            dimensions = [{"label": c["name"], "sql": q(c["name"]), "source": "auto"} for c in columns
                          if c["kind"] in {"text", "boolean"} and 2 <= c["distinct"] <= 20
                          and (c["null_rate"] or 0) < 0.5][:5]
        key = as_list(chosen["key"][0]) if "key" in chosen else []
        if key and chosen["key"][1] != "option" and any(k not in names for k in key):
            scope["skipped"].append({"setting": chosen["key"][1],
                                     "reason": f"key columns not in this dataset: {', '.join(k for k in key if k not in names)}"})
            key = []
        scan = {
            "format": FORMAT,
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "investigation": investigation, "dataset": record, "scope": scope, "rows": rows,
            "date_column": {"name": date_column, "source": date_source, "period": period},
            "grain": None, "columns": columns, "null_patterns": None, "measure": None,
            "associations": None, "anomalies": [], "suggested_records": None,
        }
        scan["grain"] = grain(connection, columns, rows, key)
        scan["null_patterns"] = null_patterns(connection, columns, date_column, period)
        if measure:
            scan["measure"] = measure_scan(connection, measure, dimensions, date_column, period,
                                           options.min_group, options.top)
            scan["measure"]["dimensions"] = [{"label": d["label"], "source": d["source"]} for d in dimensions]
        scan["associations"] = associations(connection, columns, measure, options.min_r)
    finally:
        connection.close()
    scan = deep_plain(scan)
    label = f"-{options.label}" if options.label else ""
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-.") or "dataset"
    output = folder / "exploration" / "eda" / f"{safe}{label}.json"
    relative = str(output.relative_to(root))
    scan["anomalies"] = anomalies(scan, date.today())
    scan["suggested_records"] = suggested_records(scan, relative)
    output.parent.mkdir(parents=True, exist_ok=True)
    partial = output.with_name(output.name + ".partial")
    partial.write_text(json.dumps(scan, indent=2) + "\n", encoding="utf-8")
    os.replace(partial, output)
    return scan, relative


def deep_plain(value):
    if isinstance(value, dict):
        return {k: deep_plain(v) for k, v in value.items()}
    if isinstance(value, list):
        return [deep_plain(v) for v in value]
    return plain(value)


def as_scalar(entry):
    return str(entry[0]) if entry else None


def scope_filters(chosen, names):
    applied, skipped = [], []
    for sql in as_list(chosen["where"][0]) if "where" in chosen else []:
        applied.append({"sql": sql, "source": chosen["where"][1]})
    column = chosen.get("date_column")
    for key, op in (("period_start", ">="), ("period_end", "<=")):
        if key not in chosen:
            continue
        value, source = chosen[key]
        if not column:
            skipped.append({"setting": source, "reason": "no date_column names the period column"})
        elif column[0] not in names:
            skipped.append({"setting": source, "reason": f"column {column[0]} is not in this dataset"})
        else:
            applied.append({"sql": f"CAST({q(column[0])} AS DATE) {op} CAST({lit(value)} AS DATE)",
                            "source": source})
    return {"applied": applied, "skipped": skipped}


def pick_date(chosen, temporal):
    names = [c["name"] for c in temporal]
    if "date_column" in chosen and chosen["date_column"][0] in names:
        return chosen["date_column"][0], chosen["date_column"][1]
    if not temporal:
        return None, None
    best = max(temporal, key=lambda c: -c["nulls"])
    return best["name"], "auto" if len(temporal) == 1 else f"auto: most populated of {len(temporal)}"


def expression(entry, names):
    if not entry:
        return None
    value, source = str(entry[0]), entry[1]
    return {"label": value, "sql": q(value) if value in names else value, "source": source}


def fmt(value):
    if value is None:
        return "–"
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, float):
        return f"{value:,.0f}" if abs(value) >= 1e5 else f"{value:.4g}"
    return str(value)


def pct(value):
    return "–" if value is None else f"{value:.1%}"


def table(header, rows):
    lines = ["| " + " | ".join(header) + " |", "|" + " --- |" * len(header)]
    lines += ["| " + " | ".join(str(cell).replace("|", "\\|") for cell in row) + " |" for row in rows]
    return lines


def column_summary(c):
    if c.get("unique"):
        return "unique"
    if c.get("numeric"):
        n, qs = c["numeric"], c["numeric"]["quantiles"]
        return (f"p50 {fmt(qs['p50'])} [p5 {fmt(qs['p5'])}, p95 {fmt(qs['p95'])}] "
                f"mean {fmt(n['mean'])} sd {fmt(n['sd'])}")
    if c.get("temporal"):
        if c["temporal"]["min"] is None:
            return "all null"
        t, cov = c["temporal"], c["temporal"].get("coverage") or {}
        return (f"{t['min']} to {t['max']}; {cov.get('periods', 0)} {cov.get('period', '')}s, "
                f"gaps {len(cov.get('gaps', []))}")
    if c.get("top"):
        top = ", ".join(f"{shown(v['value'])} {v['share']:.0%}" for v in c["top"][:3])
        return f"{top}{' …' if c['other_share'] else ''}"
    return ""


def markdown(scan, path):
    s, out = scan["scope"], []
    out.append(f"## EDA scan: {scan['dataset']['name']} ({scan['investigation']})")
    filters = "; ".join(f"`{f['sql']}` ({f['source']})" for f in s["applied"]) or "none"
    out.append(f"- rows: {fmt(scan['rows'])} of {fmt(s['rows_before'])}; scope filters: {filters}")
    for item in s["skipped"]:
        out.append(f"- not applied: {item['setting']}: {item['reason']}")
    if s["settings_note"]:
        out.append(f"- settings: {s['settings_note']}")
    if s["settings_unused"]:
        out.append(f"- settings keys not read by the scan: {', '.join(s['settings_unused'])}")
    g = scan["grain"]
    keys = ", ".join(g["single_column_keys"]) or "; ".join(" + ".join(p) for p in g["column_pair_keys"]) or "none found"
    near = ", ".join(f"{n['column']} ({fmt(n['distinct'])} distinct)" for n in g["near_unique_columns"])
    declared = g.get("declared_key")
    if declared and declared.get("missing_columns"):
        declared = f"; declared key {' + '.join(declared['columns'])}: missing {', '.join(declared['missing_columns'])}"
    elif declared:
        declared = (f"; declared key {' + '.join(declared['columns'])}: {fmt(declared['duplicate_keys'])} duplicated "
                    f"values, {fmt(declared['rows_with_null_key'])} null")
    out.append(f"- grain: candidate keys {keys}{'; nearly unique ' + near if near else ''}{declared or ''}; "
               f"duplicate rows {fmt(g['duplicate_rows'])}")
    if scan["date_column"]["name"]:
        out.append(f"- date column: {scan['date_column']['name']} ({scan['date_column']['source']}), "
                   f"by {scan['date_column']['period']}")
    out.append(f"- full scan: `{path}`")
    out.append("")
    columns = scan["columns"]
    out += table(["column", "type", "null", "distinct", "summary"],
                 [[c["name"], c["type"], pct(c["null_rate"]), fmt(c["distinct"]), column_summary(c)]
                  for c in columns[:TABLE_ROWS]])
    if len(columns) > TABLE_ROWS:
        out.append(f"\n{len(columns) - TABLE_ROWS} more columns in the full scan.")
    measure = scan.get("measure")
    if measure:
        o = measure["overall"]
        out += ["", f"### Measure `{measure['expression']}`: n {fmt(o['n'])}, mean {fmt(o['mean'])}, "
                f"median {fmt(o['median'])}, sum {fmt(o['sum'])}", ""]
        rows = []
        for d in sorted(measure["by_dimension"], key=lambda d: -(d["eta_squared"] or 0))[:TABLE_ROWS]:
            hi, lo = d["highest"], d["lowest"]
            rows.append([d["dimension"], fmt(d["groups"]), pct(d["eta_squared"]),
                         f"{hi['group']} {fmt(hi['mean'])}" if hi else "–",
                         f"{lo['group']} {fmt(lo['mean'])}" if lo else "–"])
        if rows:
            out += table(["dimension", "groups", "variance explained", "highest mean", "lowest mean"], rows)
        series = (measure.get("over_time") or {}).get("series") or []
        if series:
            out.append("")
            if len(series) <= TABLE_ROWS:
                out += table([measure["over_time"]["period"], "rows", "mean", "sum"],
                             [[p["period"], fmt(p["rows"]), fmt(p["mean"]), fmt(p["sum"])] for p in series])
            else:
                means = [p for p in series if p["mean"] is not None]
                first, last = means[0], means[-1]
                low = min(means, key=lambda p: p["mean"])
                high = max(means, key=lambda p: p["mean"])
                out.append(f"Over time by {measure['over_time']['period']} ({len(series)} periods): mean "
                           f"{fmt(first['mean'])} ({first['period']}) → {fmt(last['mean'])} ({last['period']}); "
                           f"low {fmt(low['mean'])} ({low['period']}), high {fmt(high['mean'])} ({high['period']}).")
    strong = [p for p in scan["associations"]["pairs"] if p["r"] is not None and abs(p["r"]) >= scan["associations"]["min_r"]]
    if strong:
        out += ["", f"### Associations (Pearson, |r| ≥ {scan['associations']['min_r']})", ""]
        out += table(["a", "b", "r", "n"], [[p["a"], p["b"], f"{p['r']:.2f}", fmt(p["n"])] for p in strong[:TABLE_ROWS]])
    if scan["anomalies"]:
        out += ["", "### Anomalies", ""]
        out += table(["kind", "column", "detail", "route"],
                     [[a["kind"], a["column"] or "–", a["detail"], a["route"]] for a in scan["anomalies"][:TABLE_ROWS]])
        if len(scan["anomalies"]) > TABLE_ROWS:
            out.append(f"\n{len(scan['anomalies']) - TABLE_ROWS} more anomalies in the full scan.")
    records = scan["suggested_records"]
    if records["unresolved_issues"] or records["next_steps"]:
        out += ["", "### Suggested state.md lines (edit before recording)"]
        if records["unresolved_issues"]:
            out += ["", "Unresolved issues:", *records["unresolved_issues"]]
        if records["next_steps"]:
            out += ["", "Next steps:", *records["next_steps"]]
    return "\n".join(out)


def compact(scan, path):
    measure = scan.get("measure")
    return {
        "dataset": scan["dataset"]["name"], "investigation": scan["investigation"], "path": path,
        "rows": scan["rows"], "rows_before_scope": scan["scope"]["rows_before"],
        "filters": [f["sql"] for f in scan["scope"]["applied"]], "skipped": scan["scope"]["skipped"],
        "settings_unused": scan["scope"]["settings_unused"],
        "keys": scan["grain"]["single_column_keys"] or scan["grain"]["column_pair_keys"],
        "duplicate_rows": scan["grain"]["duplicate_rows"],
        "measure": None if not measure else {
            "expression": measure["expression"], "overall": measure["overall"],
            "dimensions": {d["dimension"]: d["eta_squared"] for d in measure["by_dimension"]},
            "contrary": len(measure["contrary"])},
        "anomalies": scan["anomalies"][:TABLE_ROWS], "suggested_records": scan["suggested_records"],
    }


def parse(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("root", help="project root")
    parser.add_argument("dataset", help="canonical view name, or a project-relative publication path")
    parser.add_argument("--investigation", help="investigation name; default: README's active investigation")
    parser.add_argument("--settings", help="project-relative settings file; default: the investigation's settings.toml")
    parser.add_argument("--where", action="append", help="SQL predicate; repeatable; replaces the settings filter")
    parser.add_argument("--date-column", help="date or timestamp column for scope period and trends")
    parser.add_argument("--start", help="first date in scope, inclusive (needs a date column)")
    parser.add_argument("--end", help="last date in scope, inclusive (needs a date column)")
    parser.add_argument("--no-scope", action="store_true", help="ignore the settings' where and period filters")
    parser.add_argument("--measure", help="numeric column or SQL expression to break down")
    parser.add_argument("--dimension", action="append", help="grouping column or SQL expression; repeatable")
    parser.add_argument("--key", action="append", help="declared grain column; repeatable")
    parser.add_argument("--period", choices=PERIODS, help="period for coverage and trends; default: by span")
    parser.add_argument("--top", type=int, default=10, help="top categories kept per column (default 10)")
    parser.add_argument("--min-group", type=int, default=30, help="minimum rows for group comparisons (default 30)")
    parser.add_argument("--min-r", type=float, default=0.5, help="|r| shown in the summary (default 0.5)")
    parser.add_argument("--label", help="suffix for the scan file, for a second scope of the same dataset")
    parser.add_argument("--json", action="store_true", help="print compact JSON instead of Markdown")
    options = parser.parse_args(argv)
    if options.label and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", options.label):
        parser.error("--label must be a simple name")
    if options.top < 1 or options.min_group < 1:
        parser.error("--top and --min-group must be positive")
    return options


def main(argv=None):
    options = parse(sys.argv[1:] if argv is None else argv)
    try:
        scan, path = scan_dataset(options.root, options.dataset, options)
    except ScanError as error:
        print(f"eda_scan: {error}", file=sys.stderr)
        return 2
    print(json.dumps(compact(scan, path), separators=(",", ":")) if options.json else markdown(scan, path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
