#!/usr/bin/env python3
"""Stand-in for a user who clicks Allow: a stdio MCP server whose one tool,
`approve`, is passed to headless Claude Code as --permission-prompt-tool.
Every permission prompt the agent would have shown is allowed and logged, so
the study can count how many prompts a real user would have faced.

  approver_mcp.py <log-file>
"""
import json
import sys
from datetime import datetime, timezone

LOG = sys.argv[1] if len(sys.argv) > 1 else None


def send(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def log(entry):
    if LOG:
        with open(LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")


for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        msg = json.loads(line)
    except ValueError:
        continue
    mid, method = msg.get("id"), msg.get("method")
    if method == "initialize":
        send({"jsonrpc": "2.0", "id": mid, "result": {
            "protocolVersion": msg.get("params", {}).get("protocolVersion", "2025-06-18"),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "simperm", "version": "1"}}})
    elif method == "tools/list":
        send({"jsonrpc": "2.0", "id": mid, "result": {"tools": [{
            "name": "approve",
            "description": "Answers a permission prompt on the user's behalf.",
            "inputSchema": {"type": "object", "properties": {
                "tool_name": {"type": "string"}, "input": {"type": "object"}, "tool_use_id": {"type": "string"}},
                "required": ["tool_name", "input"]}}]}})
    elif method == "tools/call":
        args = msg.get("params", {}).get("arguments", {})
        log({"at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "tool": args.get("tool_name"),
             "input": args.get("input")})
        decision = {"behavior": "allow", "updatedInput": args.get("input", {})}
        send({"jsonrpc": "2.0", "id": mid, "result": {"content": [{"type": "text", "text": json.dumps(decision)}]}})
    elif mid is not None:
        send({"jsonrpc": "2.0", "id": mid, "result": {}})
