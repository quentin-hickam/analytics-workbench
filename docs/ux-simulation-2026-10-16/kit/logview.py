#!/usr/bin/env python3
"""logview.py <role-NNN.jsonl>...: print a readable list of a turn's tool calls and messages.

Handles Claude stream-json and Codex --json logs. Long inputs and outputs are cut.
  --full    do not cut tool inputs
"""
import json
import sys

full = "--full" in sys.argv
cut = (lambda s, n: s) if full else (lambda s, n: s if len(s) <= n else s[:n] + " ...")
for path in [a for a in sys.argv[1:] if not a.startswith("--")]:
    print(f"===== {path}")
    for line in open(path, errors="replace"):
        if not line.startswith("{"):
            continue
        try:
            e = json.loads(line)
        except ValueError:
            continue
        t = e.get("type")
        if t == "assistant":  # claude
            sub = " (subagent)" if e.get("parent_tool_use_id") else ""
            for c in e.get("message", {}).get("content", []):
                if c.get("type") == "text" and c["text"].strip():
                    print(f"MSG{sub}: {cut(c['text'].strip(), 400)}")
                elif c.get("type") == "tool_use":
                    print(f"TOOL{sub} {c['name']}: {cut(json.dumps(c.get('input')), 300)}")
        elif t == "user":
            for c in (e.get("message", {}).get("content") or []):
                if isinstance(c, dict) and c.get("type") == "tool_result" and c.get("is_error"):
                    print(f"  ERROR: {cut(str(c.get('content')), 300)}")
        elif t == "result":
            print(f"RESULT: turns={e.get('num_turns')} error={e.get('is_error')} denials={len(e.get('permission_denials') or [])}")
        elif t == "item.completed":  # codex
            it = e.get("item", {})
            k = it.get("type")
            if k == "agent_message":
                print(f"MSG: {cut(it.get('text', '').strip(), 400)}")
            elif k == "command_execution":
                print(f"CMD [{it.get('exit_code')}]: {cut(it.get('command', ''), 300)}")
                if it.get("exit_code") not in (0, None):
                    print(f"  OUT: {cut(str(it.get('aggregated_output', '')), 300)}")
            elif k == "mcp_tool_call":
                print(f"MCP {it.get('server')}/{it.get('tool')} [{it.get('status')}]: {cut(json.dumps(it.get('arguments')), 300)}")
                if it.get("error"):
                    print(f"  ERROR: {cut(str(it.get('error')), 300)}")
            elif k == "file_change":
                print(f"FILES: {cut(json.dumps([c.get('path') for c in it.get('changes', [])]), 300)}")
            elif k == "web_search":
                print(f"WEB: {it.get('query')}")
            elif k not in ("reasoning",):
                print(f"{k}: {cut(json.dumps(it), 200)}")
        elif t in ("error", "turn.failed"):
            print(f"ERROR EVENT: {cut(json.dumps(e), 300)}")
