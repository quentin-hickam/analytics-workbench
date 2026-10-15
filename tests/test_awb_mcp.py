# Kept cases:
# test_handshake_ping_and_tool_list: initialize answers 2025-11-25, echoes an earlier legacy version but not 2025-03-26 (which requires batches), and answers 2025-11-25 to an unknown one; initialized gets no reply; ping answers {}; tools/list gives seven tools, readOnlyHint true only on read, openWorldHint true only on read, destructiveHint left to its default (true), no outputSchema; stdout carries only JSON-RPC lines.
# test_unknown_methods_fail_at_once: server/discover and any other unknown request get -32601 at once; a bad line gets -32700, a non-2.0 message, one with an id and neither method nor result, or one whose id is not a string, number, or null -32600, an unknown tool or a non-string tool name -32602; the server keeps serving.
# test_setup_installs_into_a_folder_without_helpers: setup round trip: check writes nothing, then install writes src/awb.py and the receipt; a folder without workbench markers exits 1 with the installer's hint.
# test_read_commands_round_trip_and_write_nothing: every read command without DuckDB (state, questions, stale, review-rules, check-draft, status, help) runs its helper and leaves the project, .git included, unchanged.
# test_records_round_trip: records adds a question, edits next steps, adds a review rule, flags through stdin, and runs clean-record, each writing its record.
# test_question_tree_metadata_round_trip: records sets parent and priority on add and on an answered question's edit; read returns both changes while keeping its answer, and attempts to change answered question content or replace its answer are refused.
# test_concurrent_write_calls_keep_every_update: write calls sent without waiting run one at a time, so every next step each one adds is kept.
# test_data_run_package_release_round_trip: with DuckDB, data writes sql --out and an EDA scan, run writes evidence and a finding, read shows sql, profile, and the scan, package and release reach their helpers, and every read leaves the project unchanged.
# test_read_sql_refuses_writes: read sql and profile refuse COPY, ATTACH, INSTALL, LOAD, EXPORT, SET, CREATE, a SELECT calling enable_profiling with save_location or enable_logging with file storage, and a query() whose SQL differs between the plan check and the run, and write no file; read refuses arguments outside its command and help topics outside the helpers.
# test_read_runs_the_histogram_aggregate_and_refuses_the_histogram_macro: read sql and profile run the histogram() aggregate, directly and from a view file, and refuse FROM histogram(...), the table macro that calls query_table, writing nothing.
# test_read_queries_a_landed_excel_file_through_a_view: with the excel extension installed, read sql and profile query a landed .xlsx through a view and write nothing; skipped where the extension cannot be loaded.
# test_write_tools_refuse_bad_arguments: unknown commands, non-string args, unknown keys, and a run of an absent investigation are error results naming the problem, and nothing runs.
# test_project_root_resolution: the project argument wins over roots; one root is used; several roots without an argument name each; without roots the working directory is used; each candidate needs src/awb.py; a relative project is refused.
# test_no_workbench: a read in a folder without src/awb.py, by argument, root, or working directory, is an error result pointing at awb-init; setup alone accepts it.
# test_long_output_is_cut_with_a_pointer: output over AWB_MCP_MAX_CHARS is cut, keeping its start and end, and names a file holding the full text, in a directory private to the server process.
# test_clip_stays_within_the_limit_and_counts_the_cut: the cut output never exceeds the limit, the note states the number of characters actually cut, and a limit below 1000 is raised to 1000.
# test_read_writes_no_bytecode_and_reads_no_shared_cache: a read subprocess runs with bytecode writes off and no PYTHONPYCACHEPREFIX, even one the server inherits, so it reads no bytecode from a cache directory; a write subprocess keeps Python's cache settings.
# test_root_uris_are_unquoted_once: a root URI's percent escapes are decoded once.

import importlib.util
import json
import os
import queue
import shutil
import subprocess
import sys
import threading
from pathlib import Path

import pytest

if shutil.which("git") is None:
    pytest.skip("git is required", allow_module_level=True)

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / ".agents/skills/awb-init/assets/awb_mcp.py"
TEMPLATES = ROOT / ".agents/skills/awb-init/assets/workbench"
INV = "investigations/churn"
HAS_DUCKDB = all(importlib.util.find_spec(name) for name in ("duckdb", "pandas"))
needs_duckdb = pytest.mark.skipif(not HAS_DUCKDB, reason="needs duckdb and pandas")


class Client:
    """A stdio MCP client: one server process, answering its roots/list requests from `roots`."""

    def __init__(self, cwd, log, roots=None, env=None):
        self.roots = roots
        self.roots_asked = 0
        self.log = open(log, "ab")
        self.process = subprocess.Popen(
            [sys.executable, str(SERVER)], cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=self.log, env={**os.environ, "AWB_PYTHON": sys.executable, **(env or {})})
        self.lines = queue.Queue()
        self.raw = []
        threading.Thread(target=self._read, daemon=True).start()
        self.next_id = 0

    def _read(self):
        for line in self.process.stdout:
            self.raw.append(line)
            self.lines.put(line)

    def send(self, message):
        data = message if isinstance(message, bytes) else (json.dumps(message) + "\n").encode()
        self.process.stdin.write(data)
        self.process.stdin.flush()

    def receive(self, timeout=120):
        while True:
            message = json.loads(self.lines.get(timeout=timeout))
            if message.get("method") == "roots/list":
                self.roots_asked += 1
                roots = [{"uri": Path(path).as_uri(), "name": Path(path).name} for path in self.roots or []]
                self.send({"jsonrpc": "2.0", "id": message["id"], "result": {"roots": roots}})
                continue
            return message

    def request(self, method, params=None, timeout=120):
        self.next_id += 1
        self.send({"jsonrpc": "2.0", "id": self.next_id, "method": method,
                   **({"params": params} if params is not None else {})})
        message = self.receive(timeout)
        assert message["id"] == self.next_id
        return message

    def initialize(self, version="2025-11-25"):
        capabilities = {"roots": {"listChanged": True}} if self.roots is not None else {}
        response = self.request("initialize", {"protocolVersion": version, "capabilities": capabilities,
                                               "clientInfo": {"name": "test", "version": "1"}})
        self.send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        return response

    def call(self, name, **arguments):
        result = self.request("tools/call", {"name": name, "arguments": arguments})["result"]
        assert set(result) == {"content", "isError"}  # plain text only, never structuredContent
        assert [item["type"] for item in result["content"]] == ["text"]
        return result["content"][0]["text"], result["isError"]

    def close(self):
        self.process.stdin.close()
        self.process.wait(timeout=60)
        self.log.close()


@pytest.fixture
def connect(tmp_path):
    clients = []

    def start(cwd=None, roots=None, env=None, initialize=True):
        client = Client(cwd or tmp_path, tmp_path / "server.log", roots, env)
        clients.append(client)
        if initialize:
            client.initialize()
        return client

    yield start
    for client in clients:
        client.close()


def git(root, *args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid",
                           "-c", "commit.gpgsign=false", *args],
                          cwd=root, check=True, capture_output=True, text=True).stdout


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def scaffold(root):
    """Workbench markers, records, and one investigation with a result, before any helper is installed."""
    root.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(TEMPLATES / "AGENTS.md", root / "AGENTS.md")
    shutil.copyfile(TEMPLATES / ".gitignore", root / ".gitignore")
    readme = (TEMPLATES / "README.md").read_text().replace(
        "Active investigation: none", "Active investigation: [churn](investigations/churn/state.md)")
    (root / "README.md").write_text(readme)
    directory = root / INV
    (directory / "queries").mkdir(parents=True)
    for record in ("state.md", "history.md", "brief.md", "run.py"):
        shutil.copyfile(TEMPLATES / "investigation" / record, directory / record)
    state = directory / "state.md"
    state.write_text(state.read_text().replace("<!-- use an ISO date -->", "2026-09-01"))
    (directory / "settings.toml").write_text(
        '[parameters]\n\n[results.by-region]\nquestion = "How many orders does each region take?"\n'
        '[results.by-region.validation]\nrequired_columns = ["region", "orders"]\n')
    (directory / "queries/by-region.sql").write_text(
        "SELECT region, count(*) AS orders FROM orders GROUP BY region ORDER BY region\n")
    (root / "foundation/views").mkdir(parents=True)
    (root / "foundation/views/01_orders.sql").write_text(
        "CREATE VIEW orders AS SELECT * FROM (VALUES (1, 'east'), (2, 'west'), (3, 'west')) t(id, region);\n")
    return root


@pytest.fixture
def workbench(tmp_path, connect):
    root = scaffold(tmp_path / "wb")
    text, error = connect(cwd=root).call("setup")
    assert not error, text
    git(root, "init", "-q")
    git(root, "add", "-A")
    git(root, "commit", "-qm", "workbench")
    return root


def test_handshake_ping_and_tool_list(tmp_path, connect):
    client = connect(initialize=False)
    response = client.initialize()
    assert response["result"]["protocolVersion"] == "2025-11-25"
    assert response["result"]["capabilities"] == {"tools": {"listChanged": False}}
    assert response["result"]["serverInfo"]["name"] == "awb"
    assert client.request("ping") == {"jsonrpc": "2.0", "id": client.next_id, "result": {}}
    tools = client.request("tools/list")["result"]["tools"]
    assert [tool["name"] for tool in tools] == ["read", "records", "data", "run", "package", "release", "setup"]
    assert {tool["name"]: tool["annotations"]["readOnlyHint"] for tool in tools} == {
        "read": True, "records": False, "data": False, "run": False, "package": False, "release": False,
        "setup": False}
    assert all("outputSchema" not in tool and tool["inputSchema"]["type"] == "object" for tool in tools)
    assert all(len(f"mcp_awb_{tool['name']}") <= 64 for tool in tools)
    assert {tool["name"] for tool in tools if tool["annotations"]["openWorldHint"]} == {"read"}
    assert all("destructiveHint" not in tool["annotations"] for tool in tools)
    for version, answered in (("2025-06-18", "2025-06-18"), ("2024-11-05", "2024-11-05"),
                              ("2025-03-26", "2025-11-25"), ("2099-01-01", "2025-11-25")):
        assert connect(initialize=False).initialize(version)["result"]["protocolVersion"] == answered
    client.close()
    assert all(json.loads(line)["jsonrpc"] == "2.0" for line in client.raw)
    assert "awb-mcp:" in (tmp_path / "server.log").read_text()


def test_unknown_methods_fail_at_once(connect):
    client = connect(initialize=False)
    for method in ("server/discover", "resources/list", "prompts/list", "completion/complete"):
        response = client.request(method, {}, timeout=5)
        assert response["error"]["code"] == -32601 and method in response["error"]["message"]
    client.send(b"{not json\n")
    assert client.receive(5) == {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
    client.send({"jsonrpc": "1.0", "id": 99, "method": "ping"})
    assert client.receive(5)["error"]["code"] == -32600
    client.send({"jsonrpc": "2.0", "id": 98})
    assert client.receive(5) == {"jsonrpc": "2.0", "id": 98, "error": {"code": -32600, "message": "Invalid Request"}}
    client.initialize()
    response = client.request("tools/call", {"name": "write_anything", "arguments": {}}, timeout=5)
    assert response["error"]["code"] == -32602
    # An id or tool name of the wrong type is an error, not a crash.
    response = client.request("tools/call", {"name": ["read"], "arguments": {}}, timeout=5)
    assert response["error"]["code"] == -32602
    for message in ({"jsonrpc": "2.0", "id": [7], "result": {}}, {"jsonrpc": "2.0", "id": {"a": 1}, "method": "ping"}):
        client.send(message)
        assert client.receive(5) == {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Invalid Request"}}
    client.send({"jsonrpc": "2.0", "method": "notifications/cancelled", "params": {"requestId": 1}})
    assert client.request("ping", timeout=5)["result"] == {}


def test_setup_installs_into_a_folder_without_helpers(tmp_path, connect):
    root = scaffold(tmp_path / "wb")
    before = snapshot(root)
    client = connect(cwd=root)
    text, error = client.call("setup", check=True)
    assert not error and '"src/awb.py": "missing"' in text and snapshot(root) == before
    text, error = client.call("setup", project=str(root))
    assert not error and '"src/awb.py": "installed"' in text and text.endswith("exit status 0")
    assert (root / "src/awb.py").is_file() and (root / ".awb-receipt.json").is_file()
    bare = tmp_path / "bare"
    bare.mkdir()
    text, error = client.call("setup", project=str(bare))
    assert error and '"workbench": false' in text and "exit status 1" in text
    assert list(bare.iterdir()) == []


def test_read_commands_round_trip_and_write_nothing(workbench, connect):
    client = connect(cwd=workbench)
    before = snapshot(workbench)
    text, error = client.call("read", command="state")
    assert not error and "==> investigations/churn/state.md <==" in text
    assert client.call("read", command="state", investigation="churn")[0] == text
    text, error = client.call("read", command="questions", all=True)
    assert "no questions" in text or "questions.json" in text
    text, error = client.call("read", command="stale")
    assert not error and '"checked": 0' in text
    text, error = client.call("read", command="review-rules", investigation="churn", package="pkg")
    assert '"rules_file"' in text
    text, error = client.call("read", command="check-draft", investigation="churn", package="pkg")
    assert error and '"passed": false' in text
    text, error = client.call("read", command="status")
    assert not error and json.loads(text.split("\n\n")[0])["active"]["name"] == "churn"
    for topic, expected in ((None, "usage: python3 src/awb.py"), ("questions add", "--answerer"),
                            ("state finding", "--claim"), ("eda-scan", "--show"), ("install", "--upgrade")):
        text, error = client.call("read", command="help", **({"topic": topic} if topic else {}))
        assert not error and expected in text, topic
    assert snapshot(workbench) == before


def test_records_round_trip(workbench, connect):
    client = connect(roots=[workbench])
    text, error = client.call("records", command="questions", args=[
        "add", "Which regions churn most?", "--kind", "analytical", "--answerer", "data", "--origin", "scope"])
    assert not error and text.startswith("Q-001 open")
    assert "Q-001" in client.call("read", command="questions")[0]
    text, error = client.call("records", command="state", args=["next", "--add", "Rerun by-region"])
    assert not error and "Rerun by-region" in (workbench / INV / "state.md").read_text()
    text, error = client.call("records", command="review-rules", args=[
        "add", "--area", "periods", "--severity", "error", "--rule", "Name the period.", "--fix", "Add it."])
    assert not error and (workbench / "foundation/review-rules.md").is_file()
    text, error = client.call("records", command="state", args=["flag", "--check"], stdin="[]")
    assert not error and text.startswith("{")
    text, error = client.call("records", command="clean-record", args=["absent", "--dry-run"], stdin="{}")
    assert error and "absent" in text
    assert client.roots_asked == 6


def test_question_tree_metadata_round_trip(workbench, connect):
    client = connect(cwd=workbench)
    for args in (["add", "What should the retention plan decide?", "--kind", "decision",
                  "--answerer", "user", "--origin", "scope"],
                 ["add", "Which regions churn most?", "--kind", "analytical", "--answerer", "data",
                  "--origin", "scope", "--parent", "Q-001", "--priority", "must"],
                 ["add", "Which period should the plan cover?", "--kind", "context", "--answerer", "user",
                  "--origin", "scope"]):
        text, error = client.call("records", command="questions", args=args)
        assert not error, text
    text, error = client.call("read", command="questions", all=True)
    assert not error, text
    assert "  Q-002 open [data, analytical, must; parent: Q-001] Which regions churn most?" in text
    text, error = client.call("records", command="questions", args=[
        "answer", "Q-003", "--text", "The next quarter", "--by", "user"])
    assert not error, text
    text, error = client.call("records", command="questions", args=[
        "edit", "Q-003", "--parent", "Q-001", "--priority", "could",
        "--audience", "Which period matters for the decision?"])
    assert not error, text
    text, error = client.call("read", command="questions", all=True)
    assert not error, text
    assert ("  Q-003 answered [user, context, could; parent: Q-001] "
            "Which period should the plan cover? -> The next quarter (user) "
            "[audience: Which period matters for the decision?]") in text
    for flag, value in (("--text", "A different question?"), ("--kind", "analytical"),
                        ("--answerer", "stakeholder"), ("--unblocks", "Another decision")):
        refusal, error = client.call("records", command="questions", args=[
            "edit", "Q-003", flag, value, "--priority", "must"])
        assert error and "only an open or parked question" in refusal
    refusal, error = client.call("records", command="questions", args=[
        "answer", "Q-003", "--text", "The next year", "--by", "user"])
    assert error and "an answer is never replaced" in refusal
    assert client.call("read", command="questions", all=True) == (text, False)


def test_concurrent_write_calls_keep_every_update(workbench, connect):
    client = connect(cwd=workbench)
    tasks = [f"Task {n}" for n in range(8)]
    for n, task in enumerate(tasks):
        client.send({"jsonrpc": "2.0", "id": 1000 + n, "method": "tools/call", "params": {
            "name": "records", "arguments": {"command": "state", "args": ["next", "--add", task]}}})
    responses = [client.receive() for _ in tasks]
    assert sorted(response["id"] for response in responses) == list(range(1000, 1008))
    assert not any(response["result"]["isError"] for response in responses)
    state = (workbench / INV / "state.md").read_text()
    assert all(f"- {task}\n" in state for task in tasks), state


@needs_duckdb
def test_data_run_package_release_round_trip(workbench, connect):
    client = connect(cwd=workbench)
    text, error = client.call("data", command="sql", args=["SELECT * FROM orders", "--out", "out/orders.csv"])
    assert not error and (workbench / "out/orders.csv").is_file()
    text, error = client.call("data", command="eda-scan", args=["orders", "--no-scope"])
    assert not error and "exploration/eda/orders.json" in text
    text, error = client.call("run", investigation="churn", results=["by-region"])
    assert not error and '"result_id": "by-region"' in text
    assert (workbench / INV / "evidence/by-region.json").is_file()
    text, error = client.call("package", command="check-draft", args=["churn", "pkg"])
    assert error and '"passed": false' in text
    text, error = client.call("release", command="release", args=["churn", "pkg"])
    assert error and "exit status" in text
    git(workbench, "add", "-A")
    git(workbench, "commit", "-qm", "results")
    before = snapshot(workbench)
    text, error = client.call("read", command="sql", query="SELECT region, count(*) AS n FROM orders GROUP BY 1 ORDER BY 1",
                              limit=1)
    assert not error and text.startswith("| region | n |\n|---|---|\n| east | 1 |\n1 of 2 rows shown")
    text, error = client.call("read", command="sql", query=f"{INV}/queries/by-region.sql")
    assert not error and "| west | 2 |" in text
    text, error = client.call("read", command="sql", query="-- leading comment\nSELECT 1 AS one")
    assert not error and "| 1 |" in text
    text, error = client.call("read", command="profile", query="orders", max_rows=10)
    assert not error and text.startswith("rows: 3")
    text, error = client.call("read", command="eda-show", dataset="orders", section="rows")
    assert not error and text.startswith("3"), text
    text, error = client.call("read", command="stale")
    assert not error and '"checked": 1, "stale": 0' in text
    assert "by-region" in client.call("read", command="state")[0]
    assert snapshot(workbench) == before


@needs_duckdb
def test_read_sql_refuses_writes(workbench, connect):
    client = connect(cwd=workbench)
    before = snapshot(workbench)
    for query in (f"COPY (SELECT 1) TO '{workbench / 'x.csv'}'", f"ATTACH '{workbench / 'x.duckdb'}' AS x",
                  "INSTALL httpfs", "LOAD httpfs", f"EXPORT DATABASE '{workbench / 'dump'}'",
                  "SET threads = 1", "CREATE TABLE t AS SELECT 1", "SELECT 1; DROP VIEW orders",
                  # SELECTs whose table functions write files
                  f"FROM enable_profiling(format := 'json', save_location := '{workbench / INV / 'questions.json'}'); "
                  "SELECT region, count(*) AS n FROM orders GROUP BY 1",
                  f"FROM enable_logging(storage := 'file', storage_path := '{workbench / 'logdir'}')",
                  # query() reads range(1) under the plan check and would enable profiling at the run
                  "FROM query(CASE WHEN current_query() LIKE 'EXPLAIN%' THEN 'FROM range(1)' ELSE 'FROM "
                  f"enable_profiling(format := ''json'', save_location := ''{workbench / INV / 'questions.json'}'')' "
                  "END); SELECT region, count(*) AS n FROM orders GROUP BY 1"):
        for command in ("sql", "profile"):
            text, error = client.call("read", command=command, query=query)
            assert error and "read-only: refused" in text, (command, query)
    assert snapshot(workbench) == before


@needs_duckdb
def test_read_runs_the_histogram_aggregate_and_refuses_the_histogram_macro(workbench, connect):
    client = connect(cwd=workbench)
    (workbench / "foundation/views/02_spread.sql").write_text(
        "CREATE VIEW spread AS SELECT histogram(region) AS h FROM orders;\n")
    before = snapshot(workbench)
    text, error = client.call("read", command="sql", query="SELECT histogram(region) AS h FROM orders")
    assert not error and "{'east': 1, 'west': 2}" in text, text
    text, error = client.call("read", command="sql", query="SELECT h FROM spread")
    assert not error and "{'east': 1, 'west': 2}" in text, text
    text, error = client.call("read", command="profile", query="SELECT histogram(id) AS h FROM orders")
    assert not error and text.startswith("rows: 1"), text
    for command in ("sql", "profile"):
        text, error = client.call("read", command=command, query="FROM histogram(orders, region)")
        assert error and "read-only: refused histogram()" in text, (command, text)
    assert snapshot(workbench) == before


def excel_loads():
    """Whether DuckDB's excel extension is installed here, so a session can load it without installing."""
    import duckdb
    try:
        with duckdb.connect(config={"autoinstall_known_extensions": False}) as connection:
            connection.execute("LOAD excel")
        return True
    except duckdb.Error:
        return False


@needs_duckdb
def test_read_queries_a_landed_excel_file_through_a_view(workbench, connect):
    if not excel_loads():
        pytest.skip("needs DuckDB's excel extension installed")
    import duckdb
    book = workbench / "data/raw/books/a1/book.xlsx"
    book.parent.mkdir(parents=True)
    with duckdb.connect() as connection:
        connection.execute("LOAD excel")  # COPY's xlsx format does not load it on its own
        connection.execute(f"COPY (SELECT 'north' AS region, 4 AS n) TO '{book}' (FORMAT xlsx, HEADER true)")
    (workbench / "foundation/views/02_book.sql").write_text(
        "CREATE VIEW book AS FROM read_xlsx('data/raw/books/a1/book.xlsx');\n")
    client = connect(cwd=workbench)
    before = snapshot(workbench)
    text, error = client.call("read", command="sql", query="SELECT region, n FROM book")
    assert not error and "| north | 4" in text, text
    text, error = client.call("read", command="profile", query="book")
    assert not error and text.startswith("rows: 1"), text
    assert snapshot(workbench) == before


def test_read_refuses_what_it_does_not_run(workbench, connect):
    client = connect(cwd=workbench)
    before = snapshot(workbench)
    for arguments, expected in (
            ({"command": "sql", "query": "SELECT 1", "args": ["--out", "x.csv"]}, "unknown arguments: args"),
            ({"command": "state", "query": "x"}, "unknown arguments: query"),
            ({"command": "questions", "status": ["closed"]}, "status items"),
            ({"command": "help", "topic": "state finding r1 --status supported"}, "topic must be"),
            ({"command": "help", "topic": "run"}, "topic must be"),
            ({"command": "review-rules", "investigation": "--all", "package": "p"}, "simple name"),
            ({"command": "sql"}, "query is required"),
            ({"command": "sql", "query": "SELECT 1", "limit": -1}, "limit must be"),
            ({"command": "write"}, "unknown read command")):
        text, error = client.call("read", **arguments)
        assert error and expected in text, arguments
    assert snapshot(workbench) == before


def test_write_tools_refuse_bad_arguments(workbench, connect):
    client = connect(cwd=workbench)
    before = snapshot(workbench)
    for name, arguments, expected in (
            ("records", {"command": "land"}, "records command must be one of"),
            ("data", {"command": "state", "args": []}, "data command must be one of"),
            ("records", {"command": "questions", "args": "list"}, "args must be an array"),
            ("data", {"command": "sql", "stdin": "x"}, "unknown arguments: stdin"),
            ("records", {}, "command is required"),
            ("run", {"investigation": "absent"}, "investigations/absent/run.py does not exist"),
            ("run", {"investigation": "churn", "results": ["--all"]}, "result IDs"),
            ("setup", {"replace": "src/awb.py"}, "replace must be an array")):
        text, error = client.call(name, **arguments)
        assert error and expected in text, (name, arguments)
    assert snapshot(workbench) == before


def test_project_root_resolution(tmp_path, workbench, connect):
    other = scaffold(tmp_path / "other")
    shutil.copytree(workbench / "src", other / "src")
    plain = tmp_path / "plain"
    plain.mkdir()
    state = "==> investigations/churn/state.md <=="
    # The argument wins over roots and the working directory.
    client = connect(cwd=plain, roots=[plain])
    text, error = client.call("read", command="state", project=str(other))
    assert not error and state in text and client.roots_asked == 0
    # One root is used.
    text, error = connect(cwd=plain, roots=[workbench]).call("read", command="state")
    assert not error and state in text
    # Several roots without an argument name each.
    client = connect(cwd=workbench, roots=[workbench, other])
    text, error = client.call("read", command="state")
    assert error and "several folders" in text and str(workbench) in text and str(other) in text
    assert not client.call("read", command="state", project=str(other))[1]
    # No roots capability: the working directory.
    assert not connect(cwd=workbench).call("read", command="state")[1]
    # An empty roots list falls back to the working directory too.
    assert not connect(cwd=workbench, roots=[]).call("read", command="state")[1]
    # Relative and missing paths are refused.
    client = connect(cwd=workbench)
    text, error = client.call("read", command="state", project="wb")
    assert error and "absolute path" in text
    text, error = client.call("read", command="state", project=str(tmp_path / "missing"))
    assert error and "not a directory" in text


def test_no_workbench(tmp_path, connect):
    plain = scaffold(tmp_path / "plain")  # markers, but no helpers
    before = snapshot(plain)
    for client, arguments in ((connect(cwd=tmp_path), {"project": str(plain)}),
                              (connect(cwd=tmp_path, roots=[plain]), {}),
                              (connect(cwd=plain), {})):
        for name, extra in (("read", {"command": "state"}), ("records", {"command": "questions", "args": ["list"]}),
                            ("run", {"investigation": "churn"})):
            text, error = client.call(name, **arguments, **extra)
            assert error and "no src/awb.py" in text and "awb-init" in text, (name, arguments)
            assert str(plain.resolve()) in text
    text, error = connect(cwd=plain).call("setup", check=True)
    assert not error
    assert snapshot(plain) == before


def test_long_output_is_cut_with_a_pointer(workbench, connect):
    client = connect(cwd=workbench, env={"AWB_MCP_MAX_CHARS": "1200"})
    text, error = client.call("read", command="help")
    assert not error and len(text) <= 1200 and text.startswith("usage: python3 src/awb.py")
    assert text.endswith("exit status 0") and "characters cut; the full output is in " in text
    path = Path(text.split("the full output is in ")[1].split(" ...]")[0])
    full = path.read_text()
    assert len(full) > 1200 and full.startswith("usage:") and full.endswith("exit status 0")
    assert not path.resolve().is_relative_to(workbench.resolve())
    assert path.parent.name.startswith("awb-mcp-") and path.parent.stat().st_mode & 0o777 == 0o700


def load_server(monkeypatch, max_chars=None):
    if max_chars is not None:
        monkeypatch.setenv("AWB_MCP_MAX_CHARS", max_chars)
    spec = importlib.util.spec_from_file_location("awb_mcp_under_test", SERVER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_clip_stays_within_the_limit_and_counts_the_cut(monkeypatch):
    server = load_server(monkeypatch, "100")
    assert server.MAX_CHARS == 1000
    for size, limit in ((40000, 1000), (40000, 16000), (1001, 1000)):
        server.MAX_CHARS = limit
        text = "".join(chr(65 + n % 26) for n in range(size))
        clipped = server._clip(text, "probe")
        assert len(clipped) <= limit and clipped.endswith(text[-min(2000, limit // 4):])
        head = clipped.split("\n\n[... ")[0]
        cut = int(clipped.split("\n\n[... ")[1].split(" characters cut")[0])
        assert text.startswith(head) and cut == size - len(head) - min(2000, limit // 4)


def test_read_writes_no_bytecode_and_reads_no_shared_cache(tmp_path, monkeypatch):
    server = load_server(monkeypatch)
    monkeypatch.delenv("PYTHONDONTWRITEBYTECODE", raising=False)
    monkeypatch.setenv("PYTHONPYCACHEPREFIX", str(tmp_path / "cache"))  # inherited by the server
    probe = [sys.executable, "-c", "import os, sys; print(sys.flags.dont_write_bytecode, sys.pycache_prefix)"]
    assert server.execute(probe, tmp_path, read=True)["content"][0]["text"].startswith("1 None")
    assert server.execute(probe, tmp_path, read=False)["content"][0]["text"].startswith(f"0 {tmp_path / 'cache'}")


def test_root_uris_are_unquoted_once(monkeypatch):
    server = load_server(monkeypatch)
    path = Path("/tmp/sales 100%25 done")
    assert server._root_paths([{"uri": path.as_uri()}, {"uri": "https://example.invalid/x"}]) == [path]
