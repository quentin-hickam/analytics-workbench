#!/usr/bin/env python3
"""reviewloop.py <simdir>... [--json] [--reports]: package review rounds per agent turn, from the relay logs.

Added 2026-10-17 for the perfectionism-loop focus. For each agent turn (one user request):
wall-clock minutes (from <stem>.ts line stamps, else .err start to log mtime), whether it packaged or
released, review-receipt starts (full/scoped), records (the report's last line, passed/refused),
reviewer subagent launches, review-rules and check-draft runs, and minutes from the first review start
to the turn's end ("review tail"). --reports writes each recorded report to <simdir>/review-reports/.
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SUMMARY = re.compile(r"review( \(scoped\))?: (clean|[0-9]+ violations?.*)")
RR = re.compile(r"review-receipt[\"'\],\s]+(start|record|show)")
KIND = re.compile(r"--kind[\"',\s=]+(full|scoped)")


def stamp(errf):
    m = re.match(r"# (\S+)", errf.read_text(errors="replace")) if errf.exists() else None
    return datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp() if m else None


def events(log):
    ts = {}
    tsf = log.with_suffix(".ts")
    if tsf.exists():
        for line in tsf.read_text().splitlines():
            t, i = line.split()
            ts[int(i)] = float(t)
    out = []
    for i, line in enumerate(log.read_text(errors="replace").splitlines()):
        if line.startswith("{"):
            try:
                out.append((ts.get(i), json.loads(line)))
            except ValueError:
                pass
    return out, bool(ts)


def calls(evs):
    """Yield (time, kind, text, result_text, sub) for each tool call; sub=True inside a subagent."""
    results = {}
    for t, e in evs:
        if e.get("type") == "user":
            for c in (e.get("message") or {}).get("content", []) if isinstance((e.get("message") or {}).get("content"), list) else []:
                if c.get("type") == "tool_result":
                    r = c.get("content")
                    results[c.get("tool_use_id")] = json.dumps(r) if not isinstance(r, str) else r
    for t, e in evs:
        if e.get("type") == "assistant":
            sub = bool(e.get("parent_tool_use_id"))
            for c in (e.get("message") or {}).get("content", []):
                if c.get("type") == "tool_use":
                    yield t, c["name"], json.dumps(c.get("input")), results.get(c.get("id"), ""), sub, c.get("input")
        elif e.get("type") == "item.completed":
            it = e.get("item") or {}
            ty = it.get("type")
            if ty == "command_execution":
                yield t, "shell", it.get("command") or "", it.get("aggregated_output") or "", False, it
            elif ty == "mcp_tool_call":
                yield t, f"mcp:{it.get('tool')}", json.dumps(it.get("arguments")), json.dumps(it.get("result")) if it.get("result") else str(it.get("error") or ""), False, it
            elif ty == "collab_tool_call":
                yield t, f"collab:{it.get('tool')}", json.dumps(it.get("prompt") or ""), "", False, it


def report_text(name, text, inp):
    if isinstance(inp, dict):
        if isinstance(inp.get("arguments"), dict) and inp["arguments"].get("stdin"):
            return inp["arguments"]["stdin"]
        if inp.get("stdin"):
            return inp["stdin"]
        cmd = inp.get("command") if isinstance(inp.get("command"), str) else None
        if cmd:
            return cmd
    return text


def analyse(d, write_reports=False):
    rows = []
    rep_dir = d / "review-reports"
    for log in sorted((d / "relay").glob("agent-[0-9][0-9][0-9].jsonl")):
        evs, has_ts = events(log)
        t0 = stamp(log.with_suffix(".err"))
        t_end = max([t for t, _ in evs if t] or [log.stat().st_mtime])
        r = {"turn": log.stem, "minutes": round((t_end - t0) / 60, 1) if t0 else None, "timed": has_ts,
             "package": False, "release": False, "starts": [], "records": [], "reviewers": 0,
             "review_rules": 0, "check_draft": 0, "first_review": None}
        for t, name, text, res, sub, inp in calls(evs):
            blob = text
            a = inp.get("arguments") if isinstance(inp, dict) and isinstance(inp.get("arguments"), dict) else inp
            if isinstance(a, dict) and isinstance(a.get("command"), str) and isinstance(a.get("args"), list):
                blob = f"{a['command']} {' '.join(map(str, a['args']))} || {text}"  # MCP form: command + args
            if name == "Skill" and "awb-package" in blob or "awb-package/SKILL.md" in blob:
                r["package"] = True
            if name == "Skill" and "awb-release" in blob or "awb-release/SKILL.md" in blob:
                r["release"] = True
            if not sub and (name in ("Agent", "Task") or name == "collab:spawn_agent"):
                r["reviewers"] += 1
            if "review-rules" in blob and "check" in blob or (name.endswith("read") and '"review-rules"' in blob and "add" not in blob):
                r["review_rules"] += 1
            if "check-draft" in blob:
                r["check_draft"] += 1
            if sub or '"command": "help"' in text or re.search(r"\bawb(\.py)? help\b", blob):
                continue
            for m in RR.finditer(blob):
                verb = m.group(1)
                k = KIND.search(blob)
                ev = {"t": round((t - t0) / 60, 1) if (t and t0) else None, "kind": k.group(1) if k else "?"}
                if verb == "start":
                    r["starts"].append(ev)
                    if r["first_review"] is None:
                        r["first_review"] = t
                elif verb == "record":
                    rt = report_text(name, text, inp)
                    s = SUMMARY.findall(rt.replace("\\n", "\n"))
                    ev["summary"] = (("review (scoped): " if s[-1][0] else "review: ") + s[-1][1])[:120] if s else "?"
                    ev["accept"] = "--accept" in blob
                    pm = re.search(r'passed\\*"\s*:\s*(true|false)', res)
                    ev["passed"] = (pm.group(1) == "true") if pm else None
                    ev["refused"] = "refused" in res
                    r["records"].append(ev)
                    if write_reports:
                        rep_dir.mkdir(exist_ok=True)
                        (rep_dir / f"{log.stem}-record{len(r['records']):02d}.txt").write_text(rt.replace("\\n", "\n"))
                break_once = True
        r["review_tail_min"] = round((t_end - r["first_review"]) / 60, 1) if r["first_review"] else 0
        r.pop("first_review")
        rows.append(r)
    total = sum(x["minutes"] or 0 for x in rows[:-1] if True) if rows else 0
    return rows


def main():
    a = sys.argv[1:]
    as_json, reps = "--json" in a, "--reports" in a
    dirs = [Path(x) for x in a if not x.startswith("--")]
    allout = {}
    for d in dirs:
        rows = analyse(d, reps)
        allout[d.name] = rows
        if as_json:
            continue
        conv = rows  # feedback turn is included as the last row once the run ends
        tot = sum(r["minutes"] or 0 for r in conv)
        tail = sum(r["review_tail_min"] for r in conv)
        pk = sum(r["minutes"] or 0 for r in conv if r["package"] or r["release"] or r["starts"])
        print(f"== {d.name}: {len(rows)} agent turns, {tot:.0f} min; packaging turns {pk:.0f} min "
              f"({100 * pk / tot if tot else 0:.0f}%); from first review start to turn end {tail:.0f} min "
              f"({100 * tail / tot if tot else 0:.0f}%)")
        for r in rows:
            flag = "  <-- >2 recorded reviews in one request" if len(r["records"]) > 2 else ""
            print(f"   {r['turn']}: {r['minutes']} min{' pkg' if r['package'] else ''}{' rel' if r['release'] else ''}"
                  f" starts={len(r['starts'])} ({','.join(s['kind'] for s in r['starts'])}) records={len(r['records'])}"
                  f" reviewers={r['reviewers']} rules={r['review_rules']} check-draft={r['check_draft']}"
                  f" tail={r['review_tail_min']}{flag}")
            for rec in r["records"]:
                print(f"      @{rec['t']} {rec['summary']} passed={rec['passed']} refused={rec['refused']}"
                      f"{' accept' if rec['accept'] else ''}")
    if as_json:
        print(json.dumps(allout, indent=1))


if __name__ == "__main__":
    main()
