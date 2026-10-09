#!/usr/bin/env python3
"""Run script for this investigation: produce, validate, and record each result.

Run from anywhere: `python3 investigations/<name>/run.py [result-id ...]`. With no IDs it
produces every result in settings.toml. For each result it runs the result's saved queries in a
fresh session of canonical views, validates the result, saves the table and its profile under
results/, records evidence under evidence/, and prints one compact JSON line with the paths,
failed and unassessed checks, and the state.md findings row to paste.

Adapt this file rather than rewriting it: a new result is a [results.<id>] table in settings.toml
and its query in queries/<id>.sql. Add a producer below only when a result needs more than its
query, and put reusable operations in src/. Requires duckdb and pandas.
"""

import json
import re
import sys
import traceback
from pathlib import Path

try:
    import tomllib
except ImportError:  # Python 3.10
    import tomli as tomllib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NAME = HERE.name
SETTINGS = f"investigations/{NAME}/settings.toml"
sys.path.insert(0, str(ROOT))

from src.exploration.validate import profile, validate  # noqa: E402
from src.preparation.landing import session  # noqa: E402
from src.provenance import finding_row, record_evidence, views_read  # noqa: E402


def run(connection, sql, parameters):
    """Run SQL text with the settings parameters it names as $name, returning a DataFrame."""
    names = set(re.findall(r"\$(\w+)", sql))
    return connection.execute(sql, {k: v for k, v in parameters.items() if k in names}).df()


def produce(connection, sql, parameters):
    """Default producer: the result is its first query's output, with nothing measured."""
    return run(connection, sql[0], parameters), {}


# Producers for results that need more than one query's output, by result ID. A producer
# receives the session, the texts of the result's queries (settings `queries`, in order), and
# the [parameters] table; it returns (frame, measured), where measured holds validation spec
# entries only known at run time, such as row_counts or joins.left_rows. Read further data
# through saved queries listed in settings so their views are recorded. Example:
#
# def orders_by_month(connection, sql, parameters):
#     before = int(run(connection, sql[1], parameters)["orders"].iloc[0])  # unfiltered count
#     frame = run(connection, sql[0], parameters)
#     return frame, {"row_counts": [{"step": "period filter", "before": before,
#                                    "after": int(frame["orders"].sum()), "min_ratio": 0.01}]}
PRODUCERS = {
    # "orders-by-month": orders_by_month,
}


def _spec(validation, measured):
    # Settings supply the static spec and the three judgments; measured entries extend them.
    spec = dict(validation)
    for key, value in measured.items():
        spec[key] = {**spec.get(key, {}), **value} if isinstance(value, dict) else value
    return spec


def produce_result(connection, result_id, config, parameters):
    queries = config.get("queries", [f"queries/{result_id}.sql"])
    sql = [(HERE / query).read_text() for query in queries]
    frame, measured = PRODUCERS.get(result_id, produce)(connection, sql, parameters)
    checks = validate(frame, _spec(config.get("validation", {}), measured))
    output = HERE / "results"
    output.mkdir(exist_ok=True)
    # The saved table holds the computed values that packaging later serializes for charts.
    table, profile_path = output / f"{result_id}.csv", output / f"{result_id}.profile.json"
    frame.to_csv(table, index=False)
    profile_path.write_text(json.dumps(profile(frame), indent=2) + "\n")
    # Settings `views` overrides detection when a result reads views its queries do not name.
    views = config.get("views") or views_read(ROOT, [HERE / query for query in queries])
    evidence = record_evidence(ROOT, NAME, result_id, views=views, settings_path=SETTINGS, checks=checks)
    return {
        "result_id": result_id, "rows": len(frame),
        "failed_checks": [c["name"] for c in checks if c["outcome"] == "fail"],
        "not_assessed": [c["name"] for c in checks if c["detail"] == "not assessed"],
        "evidence": evidence.relative_to(ROOT).as_posix(),
        "table": table.relative_to(ROOT).as_posix(),
        "profile": profile_path.relative_to(ROOT).as_posix(),
        "state_row": finding_row(ROOT, NAME, result_id, checks),
    }


def main(argv):
    settings = tomllib.loads((ROOT / SETTINGS).read_text())
    results = settings.get("results", {})
    wanted = argv or list(results)
    unknown = [result_id for result_id in wanted if result_id not in results]
    if unknown or not wanted:
        print(f"settings.toml defines no result {', '.join(unknown)}" if unknown else
              "settings.toml defines no [results.<id>] tables", file=sys.stderr)
        return 2
    status = 0
    with session(ROOT) as connection:
        for result_id in wanted:
            try:
                line = produce_result(connection, result_id, results[result_id],
                                      settings.get("parameters", {}))
            except Exception as error:  # Report and continue; the other results still run.
                traceback.print_exc()
                line, status = {"result_id": result_id, "error": f"{type(error).__name__}: {error}"}, 1
            print(json.dumps(line))
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
