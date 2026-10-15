#!/usr/bin/env python3
"""Run script for this investigation: produce, validate, and record each result.

Run from anywhere: `python3 investigations/<name>/run.py [result-id ...]`. With no IDs it
produces every result in settings.toml. It refuses to run, exiting 2, while a wanted result's ID
cannot name its files, or its table lacks its question, lists code that is not files in the project
or parameters that are not names, or declares answers the question ledger does not hold as data
questions, and exits 1 when the ledger cannot be read. For each result it runs the result's saved
queries in a fresh session of canonical views, validates the result, saves the table and its profile
under results/, records evidence under evidence/, writes its state.md findings row, and prints one
compact JSON line with the paths, failed and unassessed checks, and what it did to the row, with
the row's status and claim strength.

Adapt this file rather than rewriting it: a new result is a [results.<id>] table in settings.toml,
with the question it answers, and its query in queries/<id>.sql. A result whose table declares
answers = ["Q-NNN"] marks those question ledger rows answered, and its output line lists them.
A result that needs more than its query gets a producer module, producers/<id>.py, described below,
so adding a result never edits this file; put reusable operations in src/. Requires duckdb and pandas.
"""

import importlib.util
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
from src.provenance import (  # noqa: E402
    ledger_answerers, prior_result, producer_path, record_evidence, record_finding, result_parameters,
    result_problems, views_read)


def run(connection, sql, parameters):
    """Run SQL text with the settings parameters it names as $name, returning a DataFrame."""
    names = set(re.findall(r"\$(\w+)", sql))
    return connection.execute(sql, {k: v for k, v in parameters.items() if k in names}).df()


def produce(connection, sql, parameters):
    """Default producer: the result is its first query's output, with nothing measured."""
    return run(connection, sql[0], parameters), {}


# A result that needs more than its first query's output has a producer module,
# producers/<result-id>.py, named by the result ID exactly. It defines
# produce(connection, sql, parameters), which receives the session, the texts of the result's
# queries (settings `queries`, in order), and only the [parameters] entries the result reads: those
# its queries name as $name and those its table lists in parameters = [...]. Reading any other
# raises KeyError; a listed name [parameters] does not set raises it with [], and get() gives the
# default. It returns (frame, measured), where measured holds validation spec entries only
# known at run time, such as row_counts or joins.left_rows. run.py gives the module run() above
# before loading it. Read further data through saved queries listed in settings so their views are
# recorded, and list any other file it imports or reads in its table's code = [...], since evidence
# records only declared files as the result's code. Example, producers/orders-by-month.py:
#
# def produce(connection, sql, parameters):
#     before = int(run(connection, sql[1], parameters)["orders"].iloc[0])  # unfiltered count
#     frame = run(connection, sql[0], parameters)
#     return frame, {"row_counts": [{"step": "period filter", "before": before,
#                                    "after": int(frame["orders"].sum()), "min_ratio": 0.01}]}
def producer(result_id):
    """The result's produce() from its producer module, or the default producer when it has none."""
    path = HERE / producer_path(result_id)
    if not path.is_file():
        return produce
    # Each character other than a letter or digit becomes _ and its hex code, so no two IDs share a name.
    name = "producer_" + "".join(c if c.isalnum() else f"_{ord(c):02x}" for c in result_id)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    module.run = run
    # Registered as an import is, so dataclasses and pickle can look the module up by name.
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(spec.name, None)
        raise
    if not callable(getattr(module, "produce", None)):
        raise ValueError(f"{path.relative_to(ROOT).as_posix()} defines no produce(connection, sql, parameters)")
    return module.produce


def _spec(validation, measured):
    # Settings supply the static spec and the three judgments; measured entries extend them.
    spec = dict(validation)
    for key, value in measured.items():
        spec[key] = {**spec.get(key, {}), **value} if isinstance(value, dict) else value
    return spec


def produce_result(connection, result_id, config, parameters):
    queries = config.get("queries", [f"queries/{result_id}.sql"])
    sql = [(HERE / query).read_text() for query in queries]
    # The producer gets only the parameters the result reads, and evidence records those.
    scoped = result_parameters(sql, config, parameters)
    frame, measured = producer(result_id)(connection, sql, scoped)
    checks = validate(frame, _spec(config.get("validation", {}), measured))
    # What the rerun replaces: the evidence citation, and the table, checks and settings it compares.
    prior = prior_result(ROOT, NAME, result_id)
    # Evidence describes the saved table, so drop it before the table changes; a failed run leaves none.
    (HERE / "evidence" / f"{result_id}.json").unlink(missing_ok=True)
    output = HERE / "results"
    output.mkdir(exist_ok=True)
    # The saved table holds the computed values that packaging later serializes for charts.
    table, profile_path = output / f"{result_id}.csv", output / f"{result_id}.profile.json"
    frame.to_csv(table, index=False)
    profile_path.write_text(json.dumps(profile(frame), indent=2) + "\n")
    # Settings `views` overrides detection when a result reads views its queries do not name.
    views = config.get("views") or views_read(ROOT, [HERE / query for query in queries])
    evidence = record_evidence(ROOT, NAME, result_id, views=views, settings_path=SETTINGS, checks=checks,
                               parameters=scoped)
    # Writes findings and renders the row; failure before findings are saved removes this evidence.
    state = record_finding(ROOT, NAME, result_id, checks, prior=prior)
    return {
        "result_id": result_id, "rows": len(frame),
        "failed_checks": [c["name"] for c in checks if c["outcome"] == "fail"],
        "not_assessed": [c["name"] for c in checks if c["detail"] == "not assessed"],
        "evidence": evidence.relative_to(ROOT).as_posix(),
        "table": table.relative_to(ROOT).as_posix(),
        "profile": profile_path.relative_to(ROOT).as_posix(),
        "state": state["action"], "status": state["status"], "claim": state["claim"], "history": state["history"],
        **({"questions": state["questions"]} if "questions" in state else {}),
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
    # Check answers against the ledger, and code against the files, now: a rerun replaces the prior
    # evidence before recording.
    declares = any(isinstance(results[result_id], dict) and results[result_id].get("answers") for result_id in wanted)
    try:
        questions = ledger_answerers(ROOT, NAME) if declares else None
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1
    problems = [problem for result_id in wanted
                for problem in result_problems(result_id, results[result_id], questions, folder=HERE)]
    if problems:
        print("\n".join(f"settings.toml: {problem}" for problem in problems), file=sys.stderr)
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
