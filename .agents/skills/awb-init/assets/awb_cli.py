#!/usr/bin/env python3
"""Run workbench helpers from the command line, one call per operation.

Copy this file to `src/awb.py`; run it from anywhere as `python3 src/awb.py <command> [args]`.
`python3 src/awb.py --help` lists the commands and how to get each one's arguments. Each command lives in the project helper named
in COMMANDS as a function `cli_<name>(root: Path, argv: list[str]) -> int`, where `root` is the
project root (the parent of `src/`) and the return value is the exit status. Commands print
compact output for the conversation and keep complete records in files.
"""

import importlib.util
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
    "stale": ("provenance.py", "cli_stale",
              "list findings whose evidence no longer matches the current code, views, inputs, or settings"),
    "draft-provenance": ("packaging/draft.py", "cli_draft_provenance",
                         "fill the draft manifest's producing and packaging state from the results' evidence"),
    "export": ("packaging/draft.py", "cli_export",
               "write the draft's chart and dataset files from saved result tables after the export checks"),
    "check-draft": ("packaging/draft.py", "cli_check_draft",
                    "run every mechanical draft check, including state.md's current flags, and rewrite the "
                    "manifest inventory; --verify-only checks a release candidate"),
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


if __name__ == "__main__":
    sys.exit(main())
