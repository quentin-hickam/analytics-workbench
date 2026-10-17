#!/usr/bin/env python3
"""Deterministic relay for the UX simulations (2026-10-16 harness).

Both roles are headless CLI sessions: Codex through `codex exec --json`
(resumed by the thread id it reports), Claude through `claude -p` with
stream-json output (resumed by a session id fixed up front). The relay passes
messages verbatim, including the agent's interim messages within a turn,
strips the user's STATUS line, enforces the caps after each agent reply, asks
both roles for feedback at the end, and keeps a transcript and a harness log.
No model sits between the roles.

  relay.py start  <simdir> [--force]        detach and run the whole conversation
  relay.py wait   <simdir> [--timeout S]    block until finished or S seconds (default 540)
  relay.py status <simdir>                  print the state
  relay.py stop   <simdir>                  stop the relay and any running turn

sim.json in <simdir> says which CLI plays which role.
"""
import json
import os
import re
import signal
import subprocess
import threading
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

KIT = Path(__file__).resolve().parent
REAL_HOME = Path.home()
BASE_PATH = f"<python-prefix>/bin:<homebrew>/bin:{REAL_HOME}/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
STATUS_RE = re.compile(r"^\s*[`*_]*STATUS:\s*(CONTINUE|DONE|STUCK)[`*_.]*\s*$", re.M)
TURN_TIMEOUT = 3 * 3600  # a single turn longer than this is treated as hung
CLAUDE_MODEL = "claude-opus-5-5"
CLAUDE_AGENT_BLOCKED = ["ListAgents", "SendMessage", "Workflow", "CronCreate", "CronDelete", "CronList", "RemoteTrigger",
                        "PushNotification", "ScheduleWakeup", "Monitor", "EnterWorktree", "ExitWorktree", "DesignSync",
                        "TaskStop", "AskUserQuestion", "mcp__simperm__approve"]
USER_TOOLS = "Read,Write,Edit,Glob,Grep"


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Sim:
    def __init__(self, simdir):
        self.d = Path(simdir).resolve()
        self.cfg = json.loads((self.d / "sim.json").read_text())
        self.relay = self.d / "relay"
        self.relay.mkdir(exist_ok=True)
        self.state_file = self.relay / "state.json"

    # ---------- state and logging ----------
    def state(self):
        return json.loads(self.state_file.read_text()) if self.state_file.exists() else {}

    def save(self, **kw):
        s = self.state()
        s.update(kw, updated=now())
        tmp = self.state_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(s, indent=2))
        tmp.replace(self.state_file)

    def bump(self, key):
        self.save(**{key: self.state().get(key, 0) + 1})
        return self.state()[key]

    def harness(self, text):
        with (self.d / "feedback" / "harness-log.md").open("a") as f:
            f.write(f"- [{now()}] {text}\n")

    def transcript(self, speaker, text):
        with (self.d / "transcript.md").open("a") as f:
            f.write(f"\n\n## [{now()}] {speaker}\n\n{text.strip()}\n")

    def cli(self, role):
        return "codex" if self.cfg["codex_role"] == role else "claude"

    # ---------- one turn ----------
    def turn(self, role, message, label):
        """Run one turn of `role`; return the reply text (all of the role's messages in the turn) or None."""
        n = self.bump(f"{role}_turns")
        self.save(running=f"{role} turn {n} ({label})", turn_started=now())
        stem = self.relay / f"{role}-{n:03d}"
        Path(f"{stem}.in.md").write_text(message)
        reply = self._run(role, message, stem)
        if not (reply and reply.strip()):
            sid = (self.relay / f"{role}.session")
            note = ("[Harness note, not from the other participant: your previous turn ended without a reply. Finish "
                    "what you were doing and give your reply to the last message you received.]")
            retry_msg = note if sid.exists() else message
            self.harness(f"{role} turn {n} ({label}) produced no reply; retrying with "
                         f"{'a resume note' if sid.exists() else 'the same message'}")
            Path(f"{stem}.retry.in.md").write_text(retry_msg)
            reply = self._run(role, retry_msg, Path(f"{stem}.retry"))
            if not (reply and reply.strip()):
                self.harness(f"{role} turn {n} ({label}) failed twice")
                reply = None
        if reply:
            Path(f"{stem}.out.md").write_text(reply)
        self.save(running=None)
        return reply

    SIM_GIT = {"GIT_AUTHOR_NAME": "Sim Analyst", "GIT_AUTHOR_EMAIL": "analyst@example.com",
               "GIT_COMMITTER_NAME": "Sim Analyst", "GIT_COMMITTER_EMAIL": "analyst@example.com"}

    def _env(self, role):
        env = self._env_base(role)
        if role == "agent":  # 2026-10-17: these override even `git -c user.name=...`, which a Claude agent took from the account
            env.update(self.SIM_GIT)
        return env

    def _env_base(self, role):
        if self.cli(role) == "codex":
            home = self.d / ("agent-home" if role == "agent" else "human-home")
            tmp = home / ".cache" / "tmp"
            tmp.mkdir(parents=True, exist_ok=True)
            return {"HOME": str(home), "CODEX_HOME": str(home / ".codex"), "PATH": BASE_PATH, "TMPDIR": str(tmp),
                    "USER": os.environ.get("USER", ""), "LOGNAME": os.environ.get("LOGNAME", ""),
                    "LANG": "en_US.UTF-8", "TERM": "dumb"}
        env = {"HOME": str(REAL_HOME), "PATH": BASE_PATH, "USER": os.environ.get("USER", ""),
               "LOGNAME": os.environ.get("LOGNAME", ""), "TERM": "dumb", "LANG": "en_US.UTF-8",
               "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"}
        if role == "agent":
            ah = self.d / "agent-home"
            env.update(GIT_CONFIG_GLOBAL=str(ah / ".gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                       UV_CACHE_DIR=str(ah / ".cache" / "uv"), XDG_CACHE_HOME=str(ah / ".cache"),
                       PIP_CACHE_DIR=str(ah / ".cache" / "pip"))
        return env

    def _run(self, role, message, stem):
        cli = self.cli(role)
        sid_file = self.relay / f"{role}.session"
        cwd = self.d / ("project" if role == "agent" else "human")
        log = Path(f"{stem}.jsonl")
        err = Path(f"{stem}.err")
        new_sid = None
        if cli == "codex":
            cmd = ["codex", "exec"]
            if sid_file.exists():
                cmd += ["resume", sid_file.read_text().strip()]
            cmd += ["--json", "--skip-git-repo-check", "-o", f"{stem}.last.md", "-"]
        else:
            settings = {"autoMemoryEnabled": False}
            cmd = ["claude", "-p", "--model", CLAUDE_MODEL, "--output-format", "stream-json", "--verbose",
                   "--setting-sources", "project,local", "--strict-mcp-config"]
            if sid_file.exists():
                cmd += ["--resume", sid_file.read_text().strip()]
            else:
                new_sid = str(uuid.uuid4())
                cmd += ["--session-id", new_sid]
            if role == "agent":
                ah = self.d / "agent-home"
                cmd += ["--mcp-config", str(ah / "claude-mcp.json"),
                        "--permission-prompt-tool", "mcp__simperm__approve",
                        "--add-dir", str(ah), "--add-dir", str(self.d / "storage"), "--add-dir", str(self.d / "inbox"),
                        "--add-dir", str(self.d / "feedback"),
                        "--allowedTools", "Bash,Read,Write,Edit,Glob,Grep,NotebookEdit,WebFetch,WebSearch,Agent,Skill,ToolSearch,TodoWrite,mcp__awb",
                        "--disallowedTools", ",".join(CLAUDE_AGENT_BLOCKED),
                        "--append-system-prompt-file", str(self.d / "prompts" / "claude-agent-system.md")]
            else:
                d = str(self.d)
                settings["permissions"] = {"deny": [f"Read(/{d}/agent-home/**)", f"Read(/{d}/relay/**)",
                                                    f"Read(/{d}/prompts/**)", f"Read(/{d}/transcript.md)",
                                                    f"Read(/{d}/project/AGENTS.md)", f"Read(/{d}/project/src/**)",
                                                    f"Read(/{d}/project/workbench-guides/**)", f"Read(/{d}/feedback/**)"]}
                cmd += ["--mcp-config", str(KIT / "empty-mcp.json"), "--tools", USER_TOOLS, "--allowedTools", USER_TOOLS,
                        "--add-dir", str(self.d / "project"), "--add-dir", str(self.d / "storage"),
                        "--add-dir", str(self.d / "inbox")]
            cmd += ["--settings", json.dumps(settings)]
        t0 = time.time()
        with log.open("w") as lf, err.open("w") as ef:
            ef.write(f"# {now()} {' '.join(cmd)}\n")
            ef.flush()
            p = subprocess.Popen(cmd, cwd=cwd, env=self._env(role), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=ef, start_new_session=True, text=True)
            self.save(pid=p.pid)
            p.stdin.write(message)
            p.stdin.close()
            # 2026-10-17: stamp each output line (epoch seconds, line number) in <stem>.ts, so review
            # rounds can be timed; neither CLI's JSON events carry wall-clock times.
            def pump():
                with Path(f"{stem}.ts").open("w") as tf:
                    for i, line in enumerate(p.stdout):
                        lf.write(line)
                        lf.flush()
                        tf.write(f"{time.time():.1f} {i}\n")
                        tf.flush()
            th = threading.Thread(target=pump, daemon=True)
            th.start()
            try:
                p.wait(timeout=TURN_TIMEOUT)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid, signal.SIGTERM)
                self.harness(f"{role} turn killed after {TURN_TIMEOUT}s; log {log.name}")
            th.join(timeout=60)
        self.save(pid=None)
        secs = time.time() - t0
        events = []
        for line in log.read_text(errors="replace").splitlines():
            if line.startswith("{"):
                try:
                    events.append(json.loads(line))
                except ValueError:
                    pass
        return (self._codex_reply if cli == "codex" else self._claude_reply)(role, events, log, secs, sid_file, new_sid,
                                                                            stem)

    def _codex_reply(self, role, events, log, secs, sid_file, new_sid, stem):
        texts, cmds_failed, mcp, mcp_failed = [], 0, 0, []
        for e in events:
            if e.get("type") == "thread.started" and not sid_file.exists() and e.get("thread_id"):
                sid_file.write_text(e["thread_id"])
            it = e.get("item") or {}
            if e.get("type") == "item.completed":
                if it.get("type") == "agent_message" and it.get("text", "").strip():
                    texts.append(it["text"].strip())
                elif it.get("type") == "command_execution" and it.get("exit_code") not in (0, None):
                    cmds_failed += 1
                elif it.get("type") == "mcp_tool_call":
                    mcp += 1
                    if it.get("status") != "completed" or it.get("error"):
                        mcp_failed.append(f"{it.get('server')}/{it.get('tool')}: {str(it.get('error'))[:200]}")
        errs = [e.get("message") or e.get("error") for e in events if e.get("type") in ("error", "turn.failed")]
        self.harness(f"{role} (codex) {log.name}: {secs / 60:.1f} min, {len(texts)} messages, {mcp} MCP calls "
                     f"({len(mcp_failed)} failed), {cmds_failed} commands exited non-zero"
                     + (f"; MCP failures: {mcp_failed}" if mcp_failed else "") + (f"; errors: {errs}" if errs else ""))
        if not texts:
            last = Path(f"{stem}.last.md")
            if last.exists() and last.read_text().strip():
                texts = [last.read_text().strip()]
        return "\n\n".join(texts) if texts else None

    def _claude_reply(self, role, events, log, secs, sid_file, new_sid, stem):
        texts, result, init = [], None, False
        for e in events:
            if e.get("type") == "system" and e.get("subtype") == "init":
                init = True
            if e.get("type") == "assistant" and not e.get("parent_tool_use_id"):
                for c in e.get("message", {}).get("content", []):
                    if c.get("type") == "text" and c.get("text", "").strip():
                        texts.append(c["text"].strip())
            if e.get("type") == "result":
                result = e
        if new_sid and init:
            sid_file.write_text(new_sid)
        cost_prev = self.state().get(f"{role}_cost_usd", 0.0)
        info = f"{role} (claude) {log.name}: {secs / 60:.1f} min"
        if result:
            cost = result.get("total_cost_usd") or 0.0
            self.save(**{f"{role}_cost_usd": cost})
            info += f", {result.get('num_turns')} model turns, ${max(cost - cost_prev, 0):.2f}"
            den = result.get("permission_denials") or []
            if den:
                info += f"; {len(den)} permission denials: " + "; ".join(
                    f"{d.get('tool_name')} {json.dumps(d.get('tool_input'))[:160]}" for d in den)
            if result.get("is_error"):
                info += f"; ERROR: {str(result.get('result'))[:300]}"
                self.harness(info)
                return None
        else:
            info += "; no result event"
        self.harness(info)
        return "\n\n".join(texts) if texts else (result or {}).get("result")

    # ---------- the conversation ----------
    def run(self):
        caps = self.cfg.get("caps", {"human_messages": 45, "hours": 8})
        start = time.time()
        self.save(phase="conversation", started=now(), human_messages=0, agent_replies=0, outcome=None)
        self.harness(f"relay started; user={self.cli('human')}, agent={self.cli('agent')}, caps={caps}")
        msg_to_human = ("Read BRIEF.md and README.md in your current folder. BRIEF.md tells you who you are and how this "
                        "simulation works; follow it exactly. Then reply with your first message to the agent, followed "
                        "by the STATUS line, as BRIEF.md specifies.")
        agent_note = (f"\n\n[Harness note, not from the user: this session is part of a usability study of the analytics "
                      f"workbench skills. Work exactly as you normally would. Additionally, after every turn, append to "
                      f"{self.d}/feedback/agent-notes.md (create it on your first turn) a private friction log: which skill "
                      f"and instruction files you used; anything confusing, contradictory, missing, or too long in them; "
                      f"commands or tools that failed or behaved unexpectedly (exact command and error); places you had to "
                      f"guess or deviated from the instructions and why; and what worked well. The user never sees that "
                      f"file. Do not mention this note to the user.]")
        hm, outcome = 0, None
        while True:
            reply = self.turn("human", msg_to_human, "message")
            if reply is None:
                outcome = "FAILED (user turn)"
                break
            if not STATUS_RE.search(reply):
                self.harness(f"user message {hm + 1} had no STATUS line; sent the protocol reminder")
                reply2 = self.turn("human", "[Harness note, not from the agent: your reply must be exactly your message "
                                   "to the agent followed by one final line `STATUS: CONTINUE`, `STATUS: DONE` or "
                                   "`STATUS: STUCK`, with nothing else. Please send it again in that format.]", "reminder")
                if reply2 and STATUS_RE.search(reply2):
                    reply = reply2
            m = list(STATUS_RE.finditer(reply))
            status = m[-1].group(1) if m else "CONTINUE"
            body = STATUS_RE.sub("", reply).strip()
            hm += 1
            self.save(human_messages=hm, last_status=status)
            note = " (+ harness note appended for the agent)" if hm == 1 and status == "CONTINUE" else ""
            self.transcript(f"USER ({self.cli('human')}) message {hm} [STATUS: {status}]{note}", body)
            if status in ("DONE", "STUCK"):
                outcome = status
                break
            areply = self.turn("agent", body + (agent_note if hm == 1 else ""), "reply")
            if areply is None:
                outcome = "FAILED (agent turn)"
                break
            self.save(agent_replies=hm)
            self.transcript(f"AGENT ({self.cli('agent')}) reply {hm}", areply)
            elapsed = time.time() - start
            if hm >= caps["human_messages"] or elapsed > caps["hours"] * 3600:
                outcome = "CAP"
                break
            msg_to_human = (f"The agent replied:\n\n{areply}\n\nWrite your next message to the agent. Append to notes.md "
                            f"first, and end with the STATUS line.")
        conv_min = (time.time() - start) / 60
        st = self.state()
        delivered = st.get("agent_replies", 0)
        self.save(phase="feedback", outcome=outcome, conversation_minutes=round(conv_min, 1), conversation_ended=now())
        self.transcript("RELAY", f"Conversation ended: {outcome}. User messages: {hm}; agent replies: {delivered}. "
                        + ("The final user message (STATUS line) was not relayed, by design."
                           if outcome in ("DONE", "STUCK") else ""))
        self.harness(f"conversation ended: {outcome} after {hm} user messages and {delivered} agent replies, "
                     f"{conv_min:.0f} min")
        self.feedback(outcome, hm, delivered, caps)
        self.save(phase="finished", finished=now(), total_minutes=round((time.time() - start) / 60, 1))
        self.harness("relay finished")

    def feedback(self, outcome, hm, delivered, caps):
        if outcome == "CAP":
            why = (f"The conversation was stopped by the study's own limit ({caps['human_messages']} user messages or "
                   f"{caps['hours']} hours), not by the product. Every user message was delivered and answered. Judge "
                   f"only what happened; do not count the stop itself as a pain point or in any score.")
        elif outcome and outcome.startswith("FAILED"):
            why = (f"The conversation was stopped by a failure of the study's own tooling ({outcome}), not by the "
                   f"product. Judge only what happened up to then; do not count the stop itself.")
        else:
            why = f"The user ended the conversation ({outcome})."
        # agent first, so it cannot see the user's verdict
        afb = self.d / "feedback" / "agent.md"
        r = self.turn("agent", (
            f"[Harness note, not from the user: the session is over. {why} Step out of the conversation and write your "
            f"feedback as the agent to {afb}, drawing on your agent-notes.md: (1) pain points with the skills, project "
            f"instructions, workbench guides, helpers, and MCP tools or CLI, ranked, each naming the file or tool, "
            f"severity (blocker/major/minor), and a suggested fix; (2) instructions that were contradictory, ambiguous, "
            f"too long, or missing; (3) commands or tools that failed or behaved unexpectedly, with the exact command and "
            f"error; (4) where you deviated from the instructions and why; (5) where time or tokens went "
            f"disproportionately; (6) what worked well. Also say which awb MCP tools you could see and used, if any. "
            f"Reply with only the word DONE when the file is written.]"), "feedback")
        if not afb.exists() and r:
            afb.write_text(r)
            self.harness("agent did not write its feedback file; saved its reply instead")
        hfb = self.d / "human" / "feedback.md"
        self.turn("human", (
            f"The simulation is over; thank you. {why} Step out of the conversation and write your feedback as the user "
            f"to {hfb}, drawing on your notes.md: (1) did you get what you needed, satisfaction 1-10, and would you use "
            f"this again; (2) your top pain points ranked, each with the moment it happened, severity "
            f"(blocker/major/minor), and what would have helped; (3) the README: what was missing, unclear, or wrong, and "
            f"what you needed to know that it did not tell you; (4) the agent's communication: jargon, message length, "
            f"quality of its questions and of the scoping interview; (5) which answers you trusted and which you did "
            f"not, and why; (6) the deck package review and release experience, if you got that far; (7) where turns or "
            f"time were wasted; (8) what worked well. Reply with only the word DONE when the file is written."),
            "feedback")
        if hfb.exists():
            (self.d / "feedback" / "human.md").write_text(hfb.read_text())
        else:
            self.harness("user feedback file was not written")


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        sys.exit(__doc__)
    cmd, sim = a[0], Sim(a[1])
    if cmd == "run":
        try:
            sim.run()
        except Exception as e:  # keep a record; the referee reads it
            sim.harness(f"relay crashed: {type(e).__name__}: {e}")
            sim.save(phase="crashed", error=f"{type(e).__name__}: {e}")
            raise
    elif cmd == "start":
        st = sim.state()
        if st and "--force" not in a:
            sys.exit(f"refusing: {sim.state_file} exists (phase {st.get('phase')}); use wait/status, or --force on a fresh sandbox")
        with (sim.relay / "relay.log").open("a") as lf:
            p = subprocess.Popen([sys.executable, __file__, "run", str(sim.d)], stdin=subprocess.DEVNULL, stdout=lf,
                                 stderr=subprocess.STDOUT, start_new_session=True)
        sim.save(relay_pid=p.pid, phase="starting")
        print(f"relay started (pid {p.pid}) for {sim.d}")
    elif cmd in ("wait", "status"):
        t = int(a[a.index("--timeout") + 1]) if "--timeout" in a else 540
        deadline = time.time() + (t if cmd == "wait" else 0)
        while True:
            st = sim.state()
            alive = False
            if st.get("relay_pid"):
                try:
                    os.kill(st["relay_pid"], 0)
                    alive = True
                except ProcessLookupError:
                    pass
            if st.get("phase") in ("finished", "crashed") or not alive or time.time() >= deadline:
                break
            time.sleep(10)
        st = sim.state()
        word = "FINISHED" if st.get("phase") == "finished" else ("RUNNING" if alive else "DEAD")
        print(word)
        print(json.dumps({k: v for k, v in st.items() if k not in ("pid",)}, indent=2))
    elif cmd == "stop":
        st = sim.state()
        for k in ("pid", "relay_pid"):
            if st.get(k):
                try:
                    os.killpg(st[k], signal.SIGTERM)
                except (ProcessLookupError, PermissionError):
                    pass
        print("stopped")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
