#!/usr/bin/env python3
"""Run workbench helpers from the command line, one call per operation.

Copy this file to `src/awb.py`; run it from anywhere as `python3 src/awb.py <command> [args]`.
`python3 src/awb.py --help` lists the commands and how to get each one's arguments. Each command lives in the project helper named
in COMMANDS as a function `cli_<name>(root: Path, argv: list[str]) -> int`, where `root` is the
project root (the parent of `src/`) and the return value is the exit status. Commands print
compact output for the conversation and keep complete records in files.

Run as a script, it first reruns itself under the project's interpreter when another one started it:
$AWB_PYTHON, else README's `Project interpreter` line, else the project's .venv or venv interpreter,
the order the awb MCP server follows. A rerun is noted on stderr and happens at most once.
"""

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent
ROOT = SRC.parent

# command: (helper path under src/, function, one-line summary), in workflow order
COMMANDS = {
    "land": ("preparation/landing.py", "cli_land",
             "copy supplied or downloaded files into data/raw/ as an acquisition, retain it, and record "
             "its Acquisitions row"),
    "retain": ("preparation/landing.py", "cli_retain",
               "retain and record acquisitions lacking a retained copy or row; run after a library land() "
               "or a new retention location"),
    "publish": ("preparation/landing.py", "cli_publish",
                "convert acquisitions to validated Parquet with a saved SELECT and an optional check query"),
    "sql": ("preparation/landing.py", "cli_sql",
            "run a query file or SQL text against the foundation views; print the first rows and the row count"),
    "profile": ("exploration/validate.py", "cli_profile",
                "print each column's type, null rate, and distinct count for a view, query file, or SQL text"),
    "state": ("provenance.py", "cli_state",
              "print the active investigation's brief and state to resume; promote, reword, or set the claim "
              "strength of findings with their history, edit issues and next steps, or switch investigations"),
    "questions": ("provenance.py", "cli_questions",
                  "list, add, answer, park, decline, supersede, or reword the investigation's ledger questions"),
    "stale": ("provenance.py", "cli_stale",
              "list findings whose evidence no longer matches the current code, views, inputs, or settings, "
              "and warn on runtime differences"),
    "export": ("packaging/draft.py", "cli_export",
               "write the draft's chart and dataset files and the manifest's producing and packaging state; "
               "--result alone refreshes provenance"),
    "review-rules": ("packaging/draft.py", "cli_review_rules",
                     "check: list each review rule with the draft lines its pattern matches, writing nothing; "
                     "add: append the next numbered rule from a user's correction"),
    "check-draft": ("packaging/draft.py", "cli_check_draft",
                    "run every mechanical draft check, including narrative numbers against recorded results "
                    "and state.md's current flags, and rewrite the manifest inventory; --verify-only checks a "
                    "release candidate"),
    "release": ("packaging/draft.py", "cli_release",
                "copy the verified draft to the next numbered release and to release storage"),
    "copy-releases": ("packaging/draft.py", "cli_copy_releases",
                      "copy existing releases to newly recorded release storage and compare each copy"),
}


def _usage():
    width = max(map(len, COMMANDS))
    lines = ["usage: python3 src/awb.py <command> [args]", "", "commands:"]
    lines += [f"  {name:<{width}}  {summary}" for name, (_, _, summary) in COMMANDS.items()]
    lines += ["", "Run `python3 src/awb.py <command> --help` for a command's arguments, output, and exit status.",
              "Paths are project-relative unless that help says otherwise.",
              "Started by another interpreter, it reruns itself under the project's: $AWB_PYTHON, else",
              "README's Project interpreter line, else the project's .venv or venv, noting it on stderr.",
              "Exit status: 0 done; 1 something attempted failed, named in the output or on stderr;",
              "2 unusable arguments, nothing changed."]
    return "\n".join(lines)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] in {"-h", "--help"}:
        print(_usage())
        return 0
    name, rest = argv[0], argv[1:]
    if name not in COMMANDS:
        print(f"unknown command: {name}\n\n{_usage()}", file=sys.stderr)
        return 2
    relative, function, _ = COMMANDS[name]
    path = SRC / relative
    if not path.is_file():
        print(f"{name} needs src/{relative}, which this project lacks; install the workbench helpers "
              "with the awb-init skill's scripts/install_helpers.py", file=sys.stderr)
        return 2
    if name == "review-rules":
        # The read-only review's `review-rules check` must leave the project untouched, so loading its
        # helper writes no __pycache__. The flag is process-wide, so other commands keep Python's cache
        # (git ignores __pycache__/): turned off for them, every call would recompile pandas and duckdb
        # wherever they were installed without bytecode.
        sys.dont_write_bytecode = True
    # Helpers import their siblings by bare name, as the skill references show.
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(f"awb_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    command = getattr(module, function, None)
    if command is None:
        print(f"src/{relative} predates the {name} command; upgrade it with the awb-init skill's repair "
              "(scripts/install_helpers.py --upgrade)", file=sys.stderr)
        return 2
    return command(ROOT, rest)


INTERPRETER_LINE = "Project interpreter:"
# Set on the rerun only, so a rerun never reruns again; the rerun clears it for its own subprocesses.
REEXECUTED = "AWB_REEXECUTED"


def read_interpreter(root):
    """README's `Project interpreter` line as (status, value, detail).

    Accepted input: README.md at the project root, holding at most one line that starts at column 0
    with `Project interpreter:`. Its value is the rest of that line without surrounding spaces and
    one pair of surrounding backticks: `not yet recorded` in any case, or the path of an existing
    file, absolute or relative to the project root. Returns ("none", None, None) without README.md
    or the line, ("unrecorded", value, None) for `not yet recorded`, and ("recorded", value, path)
    for a file. Refused, as ("refused", value, why): a repeated line, an empty value, and a path
    naming no file. Known limits: `~` and environment variables are not expanded, and the file is
    not checked to be an interpreter.
    """
    try:
        text = (Path(root) / "README.md").read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return "none", None, None
    lines = [line for line in text.splitlines() if line.startswith(INTERPRETER_LINE)]
    if not lines:
        return "none", None, None
    if len(lines) > 1:
        return "refused", None, "README.md repeats the Project interpreter line"
    value = lines[0][len(INTERPRETER_LINE):].strip()
    if len(value) >= 2 and value[0] == value[-1] == "`":
        value = value[1:-1].strip()
    if not value:
        return "refused", value, "README's Project interpreter line is empty"
    if value.lower() == "not yet recorded":
        return "unrecorded", value, None
    path = Path(value)
    path = path if path.is_absolute() else Path(root) / path
    if not path.is_file():
        return "refused", value, f"README's Project interpreter {value} names no file"
    return "recorded", value, path


def project_python(root):
    """(interpreter, source, note) for the project: $AWB_PYTHON, else README's recorded interpreter,
    else .venv's or venv's, else (None, None, note). The note names a refused README line."""
    configured = os.environ.get("AWB_PYTHON")
    if configured:
        return configured, "AWB_PYTHON", None
    status, _, detail = read_interpreter(root)
    if status == "recorded":
        return str(detail), "README's Project interpreter", None
    for folder in (".venv", "venv"):
        for candidate in (Path(root) / folder / "bin" / "python", Path(root) / folder / "Scripts" / "python.exe"):
            if candidate.is_file():
                return str(candidate), f"the project's {folder}", detail if status == "refused" else None
    return None, None, detail if status == "refused" else None


def same_interpreter(path):
    """Whether this process runs `path`: the same file once its directories are resolved, or the same
    virtual environment. The file itself is never resolved: a venv's python links to a base interpreter
    whose packages it does not see."""
    def place(name):
        name = Path(os.path.abspath(name))
        return os.path.normcase(os.path.join(os.path.realpath(name.parent), name.name))
    if place(sys.executable) == place(path):
        return True
    environment = Path(os.path.abspath(path)).parent.parent
    return ((environment / "pyvenv.cfg").is_file()
            and os.path.normcase(os.path.realpath(environment)) == os.path.normcase(os.path.realpath(sys.prefix)))


def _rerun_under_project_python(argv):
    """Rerun this script under the project's interpreter when another one runs it; return otherwise."""
    if os.environ.pop(REEXECUTED, None) or not sys.executable:
        return
    target, source, note = project_python(ROOT)
    if note:
        print(f"awb.py: {note}; it is skipped", file=sys.stderr)
    if target is None:
        return
    # AWB_PYTHON may name a command on PATH rather than a path.
    found = (target if os.path.isfile(target) else None) if os.path.dirname(target) else shutil.which(target)
    if not found:
        print(f"awb.py: {source} names no interpreter: {target}", file=sys.stderr)
        return
    if same_interpreter(found):
        return
    print(f"awb.py: running under {found} ({source}) instead of {sys.executable}", file=sys.stderr, flush=True)
    command = [found, str(Path(__file__).resolve()), *argv]
    environment = {**os.environ, REEXECUTED: "1"}
    if os.name == "nt":  # Windows has no exec that keeps the process; wait for the rerun instead.
        sys.exit(subprocess.call(command, env=environment))
    sys.stdout.flush()
    os.execve(found, command, environment)


if __name__ == "__main__":
    _rerun_under_project_python(sys.argv[1:])
    sys.exit(main())
