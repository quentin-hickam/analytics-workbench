#!/usr/bin/env python3
"""Relay tool for the UX simulations.

Runs one Codex role (agent or human) per simulation, detached, one turn at a
time, and keeps a shared transcript.

  simctl.py send   <simdir> <role> <message-file>   start a Codex turn (new session or resume by stored id)
  simctl.py wait   <simdir> <role> [--timeout S]    block up to S seconds (default 540); print reply when done
  simctl.py log    <simdir> <role> <message-file>   append an Opus-side message to the transcript
  simctl.py status <simdir>                         show turn counts, session ids, running turns

<role> is "agent" or "human". sim.json in <simdir> says which role Codex plays.
"""
import json
import os
import re
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load(simdir):
    return json.loads((simdir / "sim.json").read_text())


def role_paths(simdir, role):
    cfg = load(simdir)
    if cfg["codex_role"] != role:
        sys.exit(f"Codex does not play the {role} in this simulation (it plays {cfg['codex_role']}).")
    home = simdir / f"{role}-home"
    cwd = simdir / ("project" if role == "agent" else "human")
    state = simdir / "relay"
    state.mkdir(exist_ok=True)
    return cfg, home, cwd, state


def append_transcript(simdir, speaker, text):
    t = simdir / "transcript.md"
    with t.open("a") as f:
        f.write(f"\n\n## [{now()}] {speaker}\n\n{text.strip()}\n")


def next_turn(state, role):
    n = 1
    while (state / f"{role}-{n:03d}.out.md").exists() or (state / f"{role}-{n:03d}.in.md").exists():
        n += 1
    return n


def cmd_send(simdir, role, msgfile):
    cfg, home, cwd, state = role_paths(simdir, role)
    pidf = state / f"{role}.pid"
    if pidf.exists():
        pid = int(pidf.read_text())
        try:
            os.kill(pid, 0)
            sys.exit(f"A {role} turn is still running (pid {pid}); wait for it first.")
        except ProcessLookupError:
            pidf.unlink()
    msg = Path(msgfile).read_text()
    n = next_turn(state, role)
    inp = state / f"{role}-{n:03d}.in.md"
    out = state / f"{role}-{n:03d}.out.md"
    log = state / f"{role}-{n:03d}.log"
    inp.write_text(msg)
    sid_file = state / f"{role}.session"
    env = dict(os.environ, HOME=str(home), CODEX_HOME=str(home / ".codex"))
    base = ["codex", "exec"]
    if sid_file.exists():
        base += ["resume", sid_file.read_text().strip()]
    base += ["--skip-git-repo-check", "-o", str(out), "-"]
    with inp.open() as stdin, log.open("w") as lf:
        p = subprocess.Popen(base, cwd=cwd, env=env, stdin=stdin, stdout=lf, stderr=subprocess.STDOUT,
                             start_new_session=True)
    pidf.write_text(str(p.pid))
    (state / f"{role}.current").write_text(str(n))
    speaker = f"{role.upper()} ← (Codex {role}, turn {n} input)" if role == "agent" else f"HUMAN prompt (Codex human, turn {n} input)"
    if role == "agent":
        append_transcript(simdir, f"HUMAN → agent (turn {n})", msg)
    # capture the session id from the log header
    if not sid_file.exists():
        for _ in range(120):
            time.sleep(1)
            m = re.search(r"session id:\s*([0-9a-f-]{36})", log.read_text(errors="replace"))
            if m:
                sid_file.write_text(m.group(1))
                break
            if p.poll() is not None:
                break
    print(f"started {role} turn {n} (pid {p.pid}); session {sid_file.read_text().strip() if sid_file.exists() else 'UNKNOWN - check log'}")


def cmd_wait(simdir, role, timeout):
    cfg, home, cwd, state = role_paths(simdir, role)
    pidf = state / f"{role}.pid"
    n = int((state / f"{role}.current").read_text())
    out = state / f"{role}-{n:03d}.out.md"
    log = state / f"{role}-{n:03d}.log"
    if not pidf.exists():
        status = "FINISHED"
    else:
        pid = int(pidf.read_text())
        deadline = time.time() + timeout
        status = "RUNNING"
        while time.time() < deadline:
            try:
                r, _ = os.waitpid(pid, os.WNOHANG)
            except ChildProcessError:
                r = None
            try:
                os.kill(pid, 0)
                alive = True
            except ProcessLookupError:
                alive = False
            if not alive:
                status = "FINISHED"
                break
            time.sleep(5)
        if status == "FINISHED":
            pidf.unlink(missing_ok=True)
    if status == "RUNNING":
        size = log.stat().st_size if log.exists() else 0
        print(f"RUNNING: {role} turn {n} still in progress after {timeout}s (log {size} bytes). Call wait again.")
        return
    if out.exists() and out.read_text().strip():
        reply = out.read_text()
        if role == "agent":
            append_transcript(simdir, f"AGENT (Codex) reply (turn {n})", reply)
        else:
            append_transcript(simdir, f"HUMAN (Codex) message (turn {n})", reply)
        print(f"FINISHED: {role} turn {n}\n----- REPLY -----\n{reply}")
    else:
        tail = log.read_text(errors="replace").splitlines()[-25:] if log.exists() else []
        print(f"FAILED: {role} turn {n} produced no reply. Log tail:\n" + "\n".join(tail))
        print(f"\nSession id: {(state / f'{role}.session').read_text().strip() if (state / f'{role}.session').exists() else 'none'}."
              f" To retry, send the same message file again (it resumes this session by id).")


def cmd_log(simdir, role, msgfile):
    cfg = load(simdir)
    msg = Path(msgfile).read_text()
    label = "HUMAN (Opus) message" if role == "human" else "AGENT (Opus) reply"
    append_transcript(simdir, label, msg)
    print("logged")


def cmd_status(simdir):
    cfg = load(simdir)
    state = simdir / "relay"
    print(json.dumps(cfg, indent=2))
    for role in ("agent", "human"):
        sid = state / f"{role}.session"
        if sid.exists():
            print(f"{role} session: {sid.read_text().strip()}")
        pidf = state / f"{role}.pid"
        if pidf.exists():
            print(f"{role} turn running: pid {pidf.read_text().strip()}")
        print(f"{role} turns started: {next_turn(state, role) - 1 if state.exists() else 0}")


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    cmd, simdir = a[0], Path(a[1]).resolve()
    if cmd == "send":
        cmd_send(simdir, a[2], a[3])
    elif cmd == "wait":
        t = 540
        if "--timeout" in a:
            t = int(a[a.index("--timeout") + 1])
        cmd_wait(simdir, a[2], t)
    elif cmd == "log":
        cmd_log(simdir, a[2], a[3])
    elif cmd == "status":
        cmd_status(simdir)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
