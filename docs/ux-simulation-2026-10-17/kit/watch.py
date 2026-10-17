#!/usr/bin/env python3
"""watch.py <simroot> <run>...: one stdout line per notable event, polling every 90 s; exits when all runs end.

Events: an agent turn finished (minutes, review starts/records), a running turn crossed another
3 review starts or another 20 minutes, a run finished or died. Added 2026-10-17.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

root = Path(sys.argv[1])
quiet = "--quiet-start" in sys.argv
runs = [r for r in sys.argv[2:] if not r.startswith("--")]
seen = {}
sys.path.insert(0, str(root / "kit"))
import reviewloop  # noqa: E402


def alive(st):
    try:
        os.kill(st.get("relay_pid") or 0, 0)
        return bool(st.get("relay_pid"))
    except (ProcessLookupError, PermissionError):
        return False


done = set()
while len(done) < len(runs):
    for run in runs:
        if run in done:
            continue
        d = root / run
        st = json.loads((d / "relay/state.json").read_text()) if (d / "relay/state.json").exists() else {}
        rows = reviewloop.analyse(d)
        key = seen.setdefault(run, {"turns": 0, "starts": 0, "mins": 0})
        finished_turns = rows if not (st.get("running") or "").startswith("agent") else rows[:-1]
        if quiet and key.get("new", True):
            key["turns"], key["new"] = len(finished_turns), False
        key["new"] = False
        for r in finished_turns[key["turns"]:]:
            if not (r["starts"] or r["package"] or r["release"] or (r["minutes"] or 0) >= 15):
                continue
            recs = "; ".join(f"{x['summary']}{' (refused)' if x['refused'] else ''}" for x in r["records"])
            print(f"{run} {r['turn']} done: {r['minutes']} min, review starts {len(r['starts'])}"
                  f"{', records: ' + recs if recs else ''}", flush=True)
        key["turns"] = len(finished_turns)
        if (st.get("running") or "").startswith("agent") and rows:
            cur = rows[-1]
            n = len(cur["records"])
            if n >= max(3, key["starts"] + 2):
                print(f"{run} {cur['turn']} running: {n} recorded reviews so far, {cur['minutes']} min", flush=True)
                key["starts"] = n
            if (cur["minutes"] or 0) >= key["mins"] + 20:
                print(f"{run} {cur['turn']} running: {cur['minutes']} min, {n} review starts", flush=True)
                key["mins"] = cur["minutes"]
        else:
            key["starts"], key["mins"] = 0, 0
        if st.get("phase") in ("finished", "crashed") or (st and not alive(st)):
            print(f"{run} ENDED: phase={st.get('phase')} outcome={st.get('outcome')} user={st.get('human_messages')}"
                  f" agent={st.get('agent_replies')}", flush=True)
            done.add(run)
    time.sleep(90)
print("ALL RUNS ENDED", flush=True)
