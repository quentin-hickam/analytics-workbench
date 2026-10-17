#!/usr/bin/env python3
"""measure.py <simdir>...: per-run wait times and package review loops, from the relay logs.

For each agent turn: wall-clock minutes (from the .err start stamp to the log's
mtime), tool calls, whether it touched awb-package, and reviewer runs. A reviewer
run is a subagent call (Claude Agent tool) or a `review-rules check` /
`check-draft` invocation (either host).
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def stamp(errf):
    m = re.match(r"# (\S+)", errf.read_text(errors="replace"))
    return datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp() if m else None


def turn_stats(log):
    tools = pkg = reviewers = checks = 0
    for line in log.read_text(errors="replace").splitlines():
        if not line.startswith("{"):
            continue
        try:
            e = json.loads(line)
        except ValueError:
            continue
        blob = ""
        if e.get("type") == "assistant" and not e.get("parent_tool_use_id"):
            for c in e.get("message", {}).get("content", []):
                if c.get("type") == "tool_use":
                    tools += 1
                    inp = json.dumps(c.get("input"))
                    blob += inp
                    if c["name"] in ("Agent", "Task"):
                        reviewers += 1
                    if c["name"] == "Skill" and "awb-package" in inp:
                        pkg = 1
        elif e.get("type") == "item.completed":
            it = e.get("item", {})
            if it.get("type") in ("command_execution", "mcp_tool_call", "file_change", "web_search"):
                tools += 1
                blob += json.dumps(it.get("command") or it.get("arguments") or "")
            if it.get("type") in ("collab_tool_call",):
                reviewers += 1
        if "awb-package/SKILL.md" in blob:
            pkg = 1
        checks += len(re.findall(r"review-rules[\"', ]+check|check-draft", blob))
    return tools, int(bool(pkg or reviewers or checks)), reviewers, checks


for d in map(Path, sys.argv[1:]):
    rows = []
    for log in sorted((d / "relay").glob("agent-[0-9][0-9][0-9].jsonl")):
        err = log.with_suffix(".err")
        t0 = stamp(err) if err.exists() else None
        mins = (log.stat().st_mtime - t0) / 60 if t0 else 0
        rows.append((log.stem, mins, *turn_stats(log)))
    conv = [r for r in rows]  # includes the feedback turn if present
    pk = [r for r in rows if r[3]]
    print(f"== {d.name}: {len(rows)} agent turns, total {sum(r[1] for r in rows):.0f} min, longest {max((r[1] for r in rows), default=0):.0f} min")
    print(f"   package turns: {len(pk)}, {sum(r[1] for r in pk):.0f} min, reviewer subagent runs {sum(r[4] for r in pk)}, check-draft/review-rules runs {sum(r[5] for r in pk)}")
    for r in rows:
        print(f"   {r[0]}: {r[1]:5.1f} min, {r[2]:3} tool calls{', package' if r[3] else ''}{f', {r[4]} subagent' if r[4] else ''}{f', {r[5]} checks' if r[5] else ''}")
