#!/usr/bin/env python3
"""Run workbench helpers from the command line, one call per operation.

Copy this file to `src/awb.py`; run it from anywhere as `python3 src/awb.py <command> [args]`.
`python3 src/awb.py --help` lists the commands. Each command lives in the project helper named
in COMMANDS as a function `cli_<name>(root: Path, argv: list[str]) -> int`, where `root` is the
project root (the parent of `src/`) and the return value is the exit status. Commands print
compact output for the conversation and keep complete records in files.
"""

import importlib.util
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent
ROOT = SRC.parent

# command: (helper path under src/, function, one-line summary)
COMMANDS = {
    "sql": ("preparation/landing.py", "cli_sql",
            "run a saved query file or SQL text in a fresh session and print the result as a table"),
    "profile": ("exploration/validate.py", "cli_profile",
                "profile a view, query file, or SQL text and save the full profile"),
    "land": ("preparation/landing.py", "cli_land",
             "land files as an acquisition, retain the copy, and record the Acquisitions row"),
    "retain": ("preparation/landing.py", "cli_retain",
               "retain and record every acquisition missing a retained copy or an Acquisitions row"),
    "publish": ("preparation/landing.py", "cli_publish",
                "convert acquisitions to validated Parquet with a SQL select"),
    "stale": ("provenance.py", "cli_stale",
              "compare every finding's evidence with the current state and list the findings that changed"),
    "check-draft": ("packaging/draft.py", "cli_check_draft",
                    "run every mechanical draft check and rewrite the manifest inventory"),
    "draft-provenance": ("packaging/draft.py", "cli_draft_provenance",
                         "fill the manifest's producing state from the represented results' evidence"),
    "export": ("packaging/draft.py", "cli_export",
               "write the draft's chart and dataset files from saved result tables after the export checks"),
    "release": ("packaging/draft.py", "cli_release",
                "copy the verified draft to the next numbered release and to release storage"),
}


def _usage():
    width = max(map(len, COMMANDS))
    lines = ["usage: python3 src/awb.py <command> [args]", "", "commands:"]
    lines += [f"  {name:<{width}}  {summary}" for name, (_, _, summary) in COMMANDS.items()]
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
        print(f"src/{relative} predates the {name} command; update it with the awb-update skill",
              file=sys.stderr)
        return 2
    return command(ROOT, rest)


if __name__ == "__main__":
    sys.exit(main())
