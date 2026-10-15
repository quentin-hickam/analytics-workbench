#!/usr/bin/env python3
"""Serve the workbench helpers as MCP tools over stdio. Standard library only; Python 3.10+.

Run from the installed skills, never from a project copy:
    python3 <awb-init skill directory>/assets/awb_mcp.py

Every tool runs an existing command as a subprocess, the same command line the skills give:
`src/awb.py <command>` in the project, or a sibling skill's script, found relative to this file.
The CLI therefore stays the one code path, and nothing here reimplements a helper.

Tools:
  read     read-only (readOnlyHint): state, questions, sql, profile, stale, review-rules check,
           check-draft --verify-only, status, eda-show, and help; built from fixed arguments
  records  investigation and foundation records: state, questions, review-rules, clean-record
  data     land, retain, publish, sql, profile, eda-scan, clean-scan
  run      an investigation's run.py
  package  export, check-draft
  release  release, copy-releases; these also write to release storage outside the project
  setup    install_helpers.py; the only tool that accepts a folder without src/awb.py

Project root, per call: the tool's `project` argument (an absolute path), else the single MCP root
when the client advertises roots (requested with roots/list), else the working directory. A candidate
must hold src/awb.py, except for setup. Several roots and no argument is an error naming them.

Subprocesses run with cwd at the project root and stdin closed unless a tool passes text to it. The
interpreter is $AWB_PYTHON, else README's Project interpreter line, else the project's .venv or venv
interpreter, else this one: the order src/awb.py follows, read with its asset beside this file. Read calls
write no bytecode and take none of Git's optional locks, and stop after $AWB_MCP_READ_TIMEOUT seconds
(default 300); write calls run one at a time, so concurrent updates to one record never overwrite each
other. Results are plain text: stdout, then stderr, then the exit status, cut to $AWB_MCP_MAX_CHARS
characters (default 16000, at least 1000) with the full text saved to a file the result names, in a
directory private to this server process.

Protocol: the legacy handshake era through 2025-11-25 (initialize, notifications/initialized, ping,
tools/list, tools/call), newline-delimited JSON-RPC on stdin and stdout. Every other request,
server/discover included, gets an immediate -32601 error, so dual-era clients fall back to
initialize. Logs go to stderr.
"""

import contextlib
import functools
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

VERSION = "0.1.0"
PROTOCOL = "2025-11-25"
# Earlier legacy revisions share every method this server uses; a client asking for one gets it back.
# 2025-03-26 is left out: it alone requires receiving JSON-RPC batches, which this server refuses.
LEGACY = ("2024-11-05", "2025-06-18", PROTOCOL)
SKILLS = Path(__file__).resolve().parents[2]
SCRIPTS = {
    "status": "awb-status/scripts/collect_status.py",
    "eda-scan": "awb-explore/scripts/eda_scan.py",
    "eda-show": "awb-explore/scripts/eda_scan.py",
    "clean-scan": "awb-clean/scripts/scan_dataset.py",
    "clean-record": "awb-clean/scripts/record_cleaning.py",
    "install": "awb-init/scripts/install_helpers.py",
}
MAX_CHARS = max(1000, int(os.environ.get("AWB_MCP_MAX_CHARS") or 16000))
READ_TIMEOUT = float(os.environ.get("AWB_MCP_READ_TIMEOUT") or 300)
ROOTS_TIMEOUT = 10
WRITE_LOCK = threading.Lock()
NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
QUESTION_STATUSES = ("open", "answered", "parked", "declined", "superseded")
# help topics: awb.py commands, with their subcommands, and the skill scripts.
AWB_COMMANDS = {"land": (), "retain": (), "publish": (), "sql": (), "profile": (),
                "state": ("finding", "render", "flag", "issues", "next", "switch"),
                "questions": ("list", "add", "answer", "status", "edit", "render"),
                "stale": (), "export": (), "review-rules": ("check", "add"), "check-draft": (),
                "release": (), "copy-releases": ()}
HELP_SCRIPTS = ("status", "eda-scan", "clean-scan", "clean-record", "install")


class ToolError(Exception):
    """A refusal reported to the model as a tool result with isError, not as a protocol error."""


def log(message):
    print(f"awb-mcp: {message}", file=sys.stderr, flush=True)


# ---------------------------------------------------------------- tool definitions

PROJECT = {"type": "string",
           "description": "Absolute path of the workbench root (the folder holding src/awb.py). "
                          "Pass it on every call."}
ARGS = {"type": "array", "items": {"type": "string"},
        "description": "The command's arguments, one array item per argument, exactly as on its command line "
                       "and without the project root; `read` with command `help` and this command as topic "
                       "lists them."}


def _write_tool(name, title, description, commands, *, stdin=False):
    properties = {"project": PROJECT,
                  "command": {"type": "string", "enum": list(commands)},
                  "args": ARGS}
    if stdin:
        properties["stdin"] = {"type": "string", "description": "Text passed to the command's standard input, "
                                                                "such as the JSON a command reads there."}
    return {"name": name, "title": title, "description": description,
            "inputSchema": {"type": "object", "properties": properties, "required": ["command"],
                            "additionalProperties": False},
            "annotations": {"title": title, "readOnlyHint": False, "idempotentHint": False,
                            "openWorldHint": False}}


TOOLS = [
    {"name": "read", "title": "Read workbench",
     "description": (
         "Read the workbench without changing any file. command: state (resume view of an investigation), "
         "questions (ledger questions; open unless all or status), sql (run SELECT statements, given as a "
         "query file or SQL text in query, against the foundation views), profile (per-column summary of a "
         "view, query file, or SELECT in query), stale (findings whose evidence no longer matches), "
         "review-rules (check a draft against the review rules), check-draft (verify a release candidate, "
         "writing nothing), status (project status facts), eda-show (one section of a saved EDA scan of "
         "dataset), help (a command's arguments; topic names it, such as `questions add` or `eda-scan`)."),
     "inputSchema": {"type": "object", "additionalProperties": False, "required": ["command"], "properties": {
         "project": PROJECT,
         "command": {"type": "string", "enum": ["state", "questions", "sql", "profile", "stale", "review-rules",
                                                "check-draft", "status", "eda-show", "help"]},
         "investigation": {"type": "string", "description": "Investigation name under investigations/; "
                           "default README's active one. Required for review-rules and check-draft."},
         "package": {"type": "string", "description": "Package name, for review-rules and check-draft."},
         "query": {"type": "string", "description": "sql and profile: a query file path (project-relative or "
                   "absolute) or SQL text; profile also takes a view name."},
         "limit": {"type": "integer", "minimum": 0, "description": "sql: rows to print (default 20)."},
         "max_rows": {"type": "integer", "minimum": 1, "description": "profile: sample above this many rows."},
         "all": {"type": "boolean", "description": "questions: list every question."},
         "status": {"type": "array", "items": {"type": "string", "enum": list(QUESTION_STATUSES)},
                    "description": "questions: the statuses to list."},
         "probe_upstream": {"type": "boolean", "description": "status: send HEAD requests to recorded "
                            "upstream URLs and report each changed, unchanged, or unknown."},
         "dataset": {"type": "string", "description": "eda-show: the scanned view or publication path."},
         "section": {"type": "string", "description": "eda-show: dot-separated keys of the section, such "
                     "as columns or measure.over_time.series."},
         "label": {"type": "string", "description": "eda-show: the scan's --label."},
         "topic": {"type": "string", "description": "help: an awb.py command with an optional subcommand, "
                   "or a script: status, eda-scan, clean-scan, clean-record, install. Omitted, it lists "
                   "the awb.py commands."}}},
     # Open world: status can probe upstream URLs, and a SELECT can read a URL.
     "annotations": {"title": "Read workbench", "readOnlyHint": True, "openWorldHint": True}},
    _write_tool(
        "records", "Update workbench records",
        "Write investigation and foundation records through their helpers. command state: change findings, "
        "issues, next steps, or the active investigation (`state flag` reads JSON from stdin); questions: "
        "add, answer, status, edit, render; review-rules: add a rule; clean-record: record a cleaning pass "
        "for a scan name, decisions JSON on stdin, with scan issues under `issues` and issues the scan did "
        "not report under `new`. Read records with the read tool.",
        ("state", "questions", "review-rules", "clean-record"), stdin=True),
    _write_tool(
        "data", "Prepare workbench data",
        "Land, retain, and publish data, run SQL or profiles that write files (--out) or need what the read "
        "tool refuses (non-SELECT statements, table functions other than file and catalog readers), and "
        "write EDA and cleaning scans. command: land, retain, publish, sql, profile, eda-scan (args: dataset "
        "and options), clean-scan (args: dataset and options).",
        ("land", "retain", "publish", "sql", "profile", "eda-scan", "clean-scan")),
    {"name": "run", "title": "Run investigation",
     "description": "Run an investigation's run.py: produce, validate, and record its results, writing "
                    "results, evidence, and findings rows. Without results it runs every result.",
     "inputSchema": {"type": "object", "additionalProperties": False, "required": ["investigation"],
                     "properties": {
                         "project": PROJECT,
                         "investigation": {"type": "string", "description": "Investigation name."},
                         "results": {"type": "array", "items": {"type": "string"},
                                     "description": "Result IDs to run; default every result."}}},
     "annotations": {"title": "Run investigation", "readOnlyHint": False, "idempotentHint": False,
                     "openWorldHint": False}},
    _write_tool(
        "package", "Build package draft",
        "Write a package draft's exports and manifest. command export: chart and dataset files and "
        "producing state; check-draft: run every draft check and rewrite the manifest inventory (the read "
        "tool's check-draft verifies without writing).",
        ("export", "check-draft")),
    _write_tool(
        "release", "Release package",
        "Freeze a verified draft as the next numbered release, or copy existing releases to recorded "
        "release storage. Both write to release storage, which may be outside the project.",
        ("release", "copy-releases")),
    {"name": "setup", "title": "Install workbench helpers",
     "description": "Install or upgrade the workbench helpers, guides, and package formats in a project "
                    "with workbench markers (AGENTS.md, foundation/, or investigations/), and record the "
                    "interpreter that runs them on README's Project interpreter line unless AWB_PYTHON "
                    "overrides it, through awb-init's "
                    "install_helpers.py. check reports without writing.",
     "inputSchema": {"type": "object", "additionalProperties": False, "properties": {
         "project": PROJECT,
         "check": {"type": "boolean", "description": "Report without writing."},
         "upgrade": {"type": "boolean", "description": "Also replace unmodified earlier copies."},
         "package_formats": {"type": "boolean", "description": "Also install missing package formats."},
         "replace": {"type": "array", "items": {"type": "string"},
                     "description": "With upgrade: customized project paths to replace."},
         "remove_retired": {"type": "boolean", "description": "With upgrade: delete unmodified retired files."}}},
     "annotations": {"title": "Install workbench helpers", "readOnlyHint": False, "idempotentHint": True,
                     "openWorldHint": False}},
]
TOOL_NAMES = {tool["name"] for tool in TOOLS}
# Write tools whose command is an awb.py command; the rest map to scripts.
WRITE_COMMANDS = {tool["name"]: tool["inputSchema"]["properties"]["command"]["enum"]
                  for tool in TOOLS if tool["name"] in ("records", "data", "package", "release")}


# ---------------------------------------------------------------- arguments

def _string(arguments, key, *, required=False, name=False):
    value = arguments.get(key)
    if value is None:
        if required:
            raise ToolError(f"{key} is required")
        return None
    if not isinstance(value, str) or not value:
        raise ToolError(f"{key} must be a non-empty string")
    if name and not NAME.fullmatch(value):
        raise ToolError(f"{key} must be a simple name (letters, digits, '.', '_', '-'): {value!r}")
    return value


def _flag(arguments, key):
    value = arguments.get(key, False)
    if not isinstance(value, bool):
        raise ToolError(f"{key} must be true or false")
    return value


def _strings(arguments, key):
    value = arguments.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ToolError(f"{key} must be an array of strings")
    return value


def _integer(arguments, key, minimum):
    value = arguments.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ToolError(f"{key} must be an integer of at least {minimum}")
    return value


def _check_keys(arguments, allowed):
    unknown = sorted(set(arguments) - set(allowed) - {"project"})
    if unknown:
        raise ToolError(f"unknown arguments: {', '.join(unknown)}")


# ---------------------------------------------------------------- project root

def _is_workbench(path):
    return (path / "src" / "awb.py").is_file()


def _root_paths(roots):
    paths = []
    for root in roots:
        uri = root.get("uri", "") if isinstance(root, dict) else ""
        parsed = urllib.parse.urlparse(uri)
        if parsed.scheme != "file":
            continue
        paths.append(Path(urllib.request.url2pathname(parsed.path)))  # url2pathname unquotes
    return paths


def resolve_project(arguments, client, *, setup=False):
    """The project root for a call: the project argument, else the single MCP root, else the working
    directory, accepted only when it holds src/awb.py (any existing directory for setup)."""
    def accept(path, origin):
        path = path.resolve()
        if not path.is_dir():
            raise ToolError(f"{origin} {path} is not a directory")
        if not setup and not _is_workbench(path):
            raise ToolError(f"{origin} {path} is not a workbench: it has no src/awb.py. Pass project as the "
                            "absolute path of the workbench root, or set one up with the awb-init skill.")
        log(f"project {path}, from {origin}")
        return path

    given = arguments.get("project")
    if given is not None:
        if not isinstance(given, str) or not given.strip():
            raise ToolError("project must be a non-empty string")
        path = Path(given).expanduser()
        if not path.is_absolute():
            raise ToolError(f"project must be an absolute path: {given!r}")
        return accept(path, "project")
    roots = client.roots()
    if roots is not None:
        paths = _root_paths(roots)
        if len(paths) > 1:
            raise ToolError("the workspace has several folders; pass project as one of: "
                            + ", ".join(str(path) for path in paths))
        if len(paths) == 1:
            return accept(paths[0], "the workspace folder")
    return accept(Path.cwd(), "the server's working directory")


# ---------------------------------------------------------------- commands

@functools.cache
def _cli():
    """The awb.py asset beside this file: its project_python() is the rule src/awb.py reruns itself by."""
    spec = importlib.util.spec_from_file_location("awb_mcp_cli", Path(__file__).resolve().parent / "awb_cli.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _python(root):
    return _cli().project_python(root)[0] or sys.executable


def _script(key):
    path = SKILLS / SCRIPTS[key]
    if not path.is_file():
        raise ToolError(f"the skills directory {SKILLS} lacks {SCRIPTS[key]}; install every awb-* skill folder")
    return str(path)


def read_command(arguments, root):
    """argv for a read call, built from fixed arguments so no read can reach a writing subcommand."""
    command = _string(arguments, "command", required=True)
    investigation = _string(arguments, "investigation", name=True)
    inv = [f"--investigation={investigation}"] if investigation else []
    awb = [_python(root), str(root / "src" / "awb.py")]
    if command == "state":
        _check_keys(arguments, ("command", "investigation"))
        return awb + ["state"] + inv
    if command == "questions":
        _check_keys(arguments, ("command", "investigation", "all", "status"))
        statuses = _strings(arguments, "status")
        if any(status not in QUESTION_STATUSES for status in statuses):
            raise ToolError(f"status items must be among {', '.join(QUESTION_STATUSES)}")
        return awb + ["questions", "list"] + inv + ["--all"] * _flag(arguments, "all") \
            + [f"--status={status}" for status in statuses]
    if command in ("sql", "profile"):
        _check_keys(arguments, ("command", "query", "limit" if command == "sql" else "max_rows"))
        query = _string(arguments, "query", required=True)
        option = "limit" if command == "sql" else "max_rows"
        value = _integer(arguments, option, 0 if command == "sql" else 1)
        extra = [] if value is None else [f"--{option.replace('_', '-')}={value}"]
        return awb + [command, "--read-only"] + extra + ["--", query]
    if command == "stale":
        _check_keys(arguments, ("command", "investigation"))
        return awb + ["stale"] + inv
    if command in ("review-rules", "check-draft"):
        _check_keys(arguments, ("command", "investigation", "package"))
        investigation = _string(arguments, "investigation", required=True, name=True)
        package = _string(arguments, "package", required=True, name=True)
        fixed = ["review-rules", "check"] if command == "review-rules" else ["check-draft", "--verify-only"]
        return awb + fixed + [investigation, package]
    if command == "status":
        _check_keys(arguments, ("command", "probe_upstream"))
        return [_python(root), _script("status")] + ["--probe-upstream"] * _flag(arguments, "probe_upstream") \
            + ["--", str(root)]
    if command == "eda-show":
        _check_keys(arguments, ("command", "investigation", "dataset", "section", "label"))
        dataset = _string(arguments, "dataset", required=True)
        section = _string(arguments, "section", required=True)
        label = _string(arguments, "label", name=True)
        return [_python(root), _script("eda-show"), f"--show={section}"] + inv \
            + ([f"--label={label}"] if label else []) + ["--", str(root), dataset]
    if command == "help":
        _check_keys(arguments, ("command", "topic"))
        topic = (_string(arguments, "topic") or "").split()
        if not topic:
            return awb + ["--help"]
        if len(topic) == 1 and topic[0] in HELP_SCRIPTS:
            return [_python(root), _script(topic[0]), "--help"]
        if topic[0] in AWB_COMMANDS and len(topic) <= 2 and (len(topic) == 1 or topic[1] in AWB_COMMANDS[topic[0]]):
            return awb + topic + ["--help"]
        raise ToolError("topic must be an awb.py command (" + ", ".join(AWB_COMMANDS) + ") with an optional "
                        "subcommand, or one of: " + ", ".join(HELP_SCRIPTS))
    raise ToolError(f"unknown read command: {command}")


def write_command(tool, arguments, root):
    """(argv, stdin text) for a write call: the chosen command with the caller's arguments after it."""
    if tool == "run":
        _check_keys(arguments, ("investigation", "results"))
        investigation = _string(arguments, "investigation", required=True, name=True)
        results = _strings(arguments, "results")
        bad = [result for result in results if not NAME.fullmatch(result)]
        if bad:
            raise ToolError(f"results must be result IDs: {', '.join(map(repr, bad))}")
        script = root / "investigations" / investigation / "run.py"
        if not script.is_file():
            raise ToolError(f"investigations/{investigation}/run.py does not exist")
        return [_python(root), str(script)] + results, None
    if tool == "setup":
        _check_keys(arguments, ("check", "upgrade", "package_formats", "replace", "remove_retired"))
        replace = _strings(arguments, "replace")
        argv = [_python(root), _script("install")]
        argv += ["--check"] * _flag(arguments, "check") + ["--upgrade"] * _flag(arguments, "upgrade")
        argv += ["--package-formats"] * _flag(arguments, "package_formats")
        argv += [f"--replace={path}" for path in replace] + ["--remove-retired"] * _flag(arguments, "remove_retired")
        return argv + ["--", str(root)], None
    _check_keys(arguments, ("command", "args", "stdin") if tool == "records" else ("command", "args"))
    command = _string(arguments, "command", required=True)
    if command not in WRITE_COMMANDS[tool]:
        raise ToolError(f"{tool} command must be one of: {', '.join(WRITE_COMMANDS[tool])}")
    args = _strings(arguments, "args")
    stdin = arguments.get("stdin")
    if stdin is not None and not isinstance(stdin, str):
        raise ToolError("stdin must be a string")
    if command in SCRIPTS:
        # Each script takes the project root as its first positional argument.
        return [_python(root), _script(command), str(root)] + args, stdin
    return [_python(root), str(root / "src" / "awb.py"), command] + args, stdin


@functools.cache
def _private_dir():
    """This process's own temporary directory, mode 0700. A fixed name under the shared temp directory
    would let another local user read the files or plant them first."""
    return Path(tempfile.mkdtemp(prefix="awb-mcp-"))


def _clip(text, label):
    if len(text) <= MAX_CHARS:
        return text
    path = _private_dir() / f"{time.strftime('%Y%m%d-%H%M%S')}-{label}-{uuid.uuid4().hex[:8]}.txt"
    path.write_text(text, encoding="utf-8")
    tail = min(2000, MAX_CHARS // 4)
    note = "\n\n[... {} characters cut; the full output is in " + str(path) + " ...]\n\n"
    head = max(0, MAX_CHARS - tail - len(note) - len(str(len(text))))
    return text[:head] + note.format(len(text) - head - tail) + text[-tail:]


def execute(argv, root, *, read, stdin=None, label="tool"):
    """Run argv in the project and return the tool result: bounded text, isError on a nonzero exit."""
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    timeout = None
    if read:
        # Keep a read from writing bytecode caches or refreshing Git's index in the project, and from
        # reading bytecode from a cache directory outside the install.
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env.pop("PYTHONPYCACHEPREFIX", None)
        env["GIT_OPTIONAL_LOCKS"] = "0"
        timeout = READ_TIMEOUT
    log(f"{label}: {' '.join(argv[1:])}")
    try:
        # Helpers read, change, and replace records unlocked, so write calls run one at a time.
        with contextlib.nullcontext() if read else WRITE_LOCK:
            process = subprocess.run(argv, cwd=root, env=env, timeout=timeout, capture_output=True,
                                     input=(stdin or "").encode("utf-8") if stdin is not None else None,
                                     stdin=subprocess.DEVNULL if stdin is None else None)
    except subprocess.TimeoutExpired:
        return _text(f"stopped after {timeout:g} seconds; narrow the query or raise AWB_MCP_READ_TIMEOUT", True)
    except OSError as error:
        return _text(f"could not start {argv[0]}: {error}", True)
    out = process.stdout.decode("utf-8", "replace").rstrip()
    err = process.stderr.decode("utf-8", "replace").rstrip()
    parts = [part for part in (out, f"stderr:\n{err}" if err else "") if part]
    parts.append(f"exit status {process.returncode}")
    return _text(_clip("\n\n".join(parts), re.sub(r"[^A-Za-z0-9_-]", "", label)), process.returncode != 0)


def _text(text, error=False):
    return {"content": [{"type": "text", "text": text}], "isError": error}


def call_tool(name, arguments, client):
    """Run one tools/call; refusals come back as error results the model can act on."""
    try:
        if not isinstance(arguments, dict):
            raise ToolError("arguments must be an object")
        root = resolve_project(arguments, client, setup=name == "setup")
        if name == "read":
            argv, stdin = read_command(arguments, root), None
        else:
            argv, stdin = write_command(name, arguments, root)
        command = arguments.get("command") if isinstance(arguments.get("command"), str) else ""
        return execute(argv, root, read=name == "read", stdin=stdin, label=f"{name}-{command}".rstrip("-"))
    except ToolError as error:
        return _text(str(error), True)


# ---------------------------------------------------------------- JSON-RPC over stdio

class Server:
    def __init__(self, reader=None, writer=None):
        self.reader = reader or sys.stdin.buffer
        self.writer = writer or sys.stdout.buffer
        self.lock = threading.Lock()
        self.pending = {}  # our request id -> [Event, response]
        self.client_roots = False

    def send(self, message):
        data = (json.dumps(message, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
        with self.lock:
            try:
                self.writer.write(data)
                self.writer.flush()
            except (BrokenPipeError, ValueError, OSError):
                log("the client closed the connection")

    def reply(self, request_id, result):
        self.send({"jsonrpc": "2.0", "id": request_id, "result": result})

    def error(self, request_id, code, message):
        self.send({"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}})

    def roots(self):
        """The client's roots, or None when it advertises none or does not answer roots/list."""
        if not self.client_roots:
            return None
        request_id = f"awb-roots-{uuid.uuid4().hex}"
        slot = [threading.Event(), None]
        self.pending[request_id] = slot
        self.send({"jsonrpc": "2.0", "id": request_id, "method": "roots/list"})
        answered = slot[0].wait(ROOTS_TIMEOUT)
        self.pending.pop(request_id, None)
        response = slot[1] if answered else None
        if not isinstance(response, dict) or not isinstance(response.get("result"), dict):
            log("roots/list failed or timed out; using the working directory")
            return None
        roots = response["result"].get("roots")
        return roots if isinstance(roots, list) else None

    def handle(self, message):
        if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
            self.error(None, -32600, "Invalid Request")
            return
        method = message.get("method")
        request_id = message.get("id")
        if not isinstance(request_id, (str, int, float, type(None))):
            self.error(None, -32600, "Invalid Request")
            return
        if method is None:
            # A response to one of our requests.
            slot = self.pending.get(request_id)
            if slot is not None:
                slot[1] = message
                slot[0].set()
            elif "result" not in message and "error" not in message:
                self.error(request_id, -32600, "Invalid Request")
            return
        if not isinstance(method, str):
            self.error(request_id, -32600, "Invalid Request")
            return
        if "id" not in message:
            return  # Notifications, notifications/initialized included, need no answer.
        params = message.get("params") or {}
        if method == "initialize":
            requested = params.get("protocolVersion") if isinstance(params, dict) else None
            capabilities = params.get("capabilities") if isinstance(params, dict) else None
            self.client_roots = isinstance(capabilities, dict) and "roots" in capabilities
            self.reply(request_id, {
                "protocolVersion": requested if requested in LEGACY else PROTOCOL,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "awb", "title": "Analytics workbench", "version": VERSION},
                "instructions": "Workbench helpers. The read tool changes nothing; every other tool writes. "
                                "Pass project when the workspace holds several folders."})
        elif method == "ping":
            self.reply(request_id, {})
        elif method == "tools/list":
            self.reply(request_id, {"tools": TOOLS})
        elif method == "tools/call":
            name = params.get("name") if isinstance(params, dict) else None
            if not isinstance(name, str) or name not in TOOL_NAMES:
                self.error(request_id, -32602, f"Unknown tool: {name}")
                return
            # A worker thread, so the reader keeps answering pings and receives the roots/list answer.
            threading.Thread(target=self._call, args=(request_id, name, params.get("arguments") or {}),
                             name=f"call-{request_id}").start()
        else:
            self.error(request_id, -32601, f"Method not found: {method}")

    def _call(self, request_id, name, arguments):
        try:
            result = call_tool(name, arguments, self)
        except Exception as error:  # Report, never kill the server.
            log(f"{name} failed: {error!r}")
            result = _text(f"the server failed: {error}", True)
        self.reply(request_id, result)

    def serve(self):
        log(f"serving the workbench tools from {SKILLS}")
        for line in iter(self.reader.readline, b""):
            if not line.strip():
                continue
            try:
                message = json.loads(line)
            except ValueError:
                self.error(None, -32700, "Parse error")
                continue
            self.handle(message)
        log("stdin closed; finishing running calls")


def main():
    Server().serve()


if __name__ == "__main__":
    main()
