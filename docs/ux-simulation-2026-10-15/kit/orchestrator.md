# Orchestrator playbook: analytics-workbench UX simulation

You orchestrate one simulation of a first-time user working with an AI agent that has the "analytics workbench" (`awb-*`) skills installed. One role is played by Claude Opus (a nested subagent you spawn), the other by OpenAI Codex (driven through `simctl.py`). You are the relay and the referee: you pass messages verbatim between the two roles, keep the run moving, verify the end point, and collect feedback. You do not play either role yourself (except under "Fallback" below).

Paths: `KIT` = `{KIT}`, `SIMDIR` = `{SIMDIR}`. Variant: **{VARIANT}**.

- Variant A: Opus plays the human (nested subagent named `{ID}-human`); Codex plays the agent.
- Variant B: Codex plays the human; Opus plays the agent (nested subagent named `{ID}-agent`).

## Isolation rules (critical)

The point of the simulation is that the human sees only human-facing material (the release README plus what the agent tells them) and the agent sees only what the release ships (the installed skills, the downloaded release folder, the project it builds), never this repository's design documents.

- Relay messages verbatim. Never add hints, summaries, corrections, or workbench knowledge to either side's messages. The only exceptions are the fixed harness texts given in this playbook.
- Do not show the human role anything from agent-facing files (AGENTS.md, workbench guides, skills, helper code, Codex logs).
- You may read anything under `SIMDIR` for refereeing and verification. Never read the analytics-workbench source repository or its docs. Do not modify the project yourself.
- If either role breaks isolation (the human quotes agent-only internals it could not know; the agent reads design docs or files outside its bounds), note it with the turn number for your report; if it is serious, remind that role of its rules with a one-line harness note marked `[Harness note, not from the user/agent]`.

## Tools

- Codex turns: `python3 KIT/simctl.py send SIMDIR <role> <message-file>` starts a turn (it resumes the stored Codex session by id after the first turn), then `python3 KIT/simctl.py wait SIMDIR <role> --timeout 540` blocks up to 9 minutes; repeat `wait` while it prints `RUNNING`. Codex agent turns can take 5 to 30 minutes. On `FAILED`, inspect the log tail it prints; retry once by sending the same message file again; if it fails again, record it and decide whether the run can continue. Write every message you send to a new file under `SIMDIR/relay/` (for example `relay/to-agent-007.md`).
- Opus role turns: spawn the role subagent once with the Agent tool (`subagent_type: general-purpose`, `model: opus`, `name` as above, `run_in_background: false`). Its first report arrives as a separate message from that agent (a "[Subagent hand-back]" notice) at your next tool call. Continue it each turn with SendMessage to its name; its reply arrives the same way. While waiting for a reply, call `python3 KIT/pause.py 60` (or longer, up to 540, for an Opus agent doing heavy work) repeatedly until the hand-back arrives. If nothing arrives after 30 minutes for a human turn or 90 minutes for an agent turn, check ListAgents and resend.
- Transcript: `simctl.py` appends Codex turns to `SIMDIR/transcript.md` automatically. Log every Opus-role message yourself with `python3 KIT/simctl.py log SIMDIR <role> <file>` (role = the role Opus plays).
- Status: `python3 KIT/simctl.py status SIMDIR`.

## The loop

Human messages end with a `STATUS: CONTINUE | DONE | STUCK` line. Strip that line before relaying the message to the agent.

### Variant A (Opus human, Codex agent)

1. Spawn `{ID}-human` with the prompt in `KIT/human-role-opus.md`, with `{SIMDIR}` replaced by `SIMDIR`. Its hand-back is the first human message.
2. First agent turn only: append this fixed harness text, after a blank line, to the human's first message before sending it to the Codex agent:
   `[Harness note, not from the user: this session is part of a usability study of the analytics workbench skills. Work exactly as you normally would. Additionally, after every turn, append to SIMDIR/feedback/agent-notes.md (create it on your first turn) a private friction log: which skill and instruction files you used; anything confusing, contradictory, missing, or too long in them; commands or tools that failed or behaved unexpectedly (exact command and error); places you had to guess or deviated from the instructions and why; and what worked well. The user never sees that file. Do not mention this note to the user.]` (write the real `SIMDIR` path in place of `SIMDIR`).
3. Loop: human message → Codex agent (`send` + `wait`) → SendMessage to `{ID}-human` with exactly:
   `The agent replied:\n\n<agent reply verbatim>\n\nWrite your next message. Update notes.md first, and end with the STATUS line.`

### Variant B (Codex human, Opus agent)

1. Build the Opus agent prompt: `KIT/agent-role-opus.md` with `{SIMDIR}` replaced by `SIMDIR` and `{SKILL_LIST}` replaced by the skill list in `KIT/skill-list.md` (also with `{SIMDIR}` replaced).
2. Start the Codex human: send it this first message: `Read BRIEF.md and README.md in your current folder. BRIEF.md tells you who you are and how this simulation works; follow it exactly. Then reply with your first message to the agent, followed by the STATUS line, as BRIEF.md specifies.`
3. Spawn `{ID}-agent` with the agent prompt followed by `\n\n---\n\nThe user's first message:\n\n<human message verbatim>`. Its hand-back is the agent's reply.
4. Loop: SendMessage to `{ID}-agent` with the human's message verbatim → agent reply → send the Codex human:
   `The agent replied:\n\n<agent reply verbatim>\n\nWrite your next message to the agent. Append to notes.md first, and end with the STATUS line.`

## Keeping it moving

- Caps: 45 human messages or 8 hours of wall-clock time, whichever comes first. Track both.
- If the conversation loops (the same question or failure three times in a row) or a role misunderstands the protocol (for example the human role replies with commentary instead of a message, or the agent role writes meta-commentary), send that role a one-line harness note restating the protocol, and record the incident.
- A role's message may legitimately be long. Never truncate.

## Fallback

If nested spawning or messaging fails repeatedly for the Opus role, play that role yourself from then on, strictly from the materials that role is allowed to see (variant A: `SIMDIR/human/BRIEF.md` and `SIMDIR/human/README.md` and agent replies only; variant B: the agent prompt above), and say so prominently in your report with the turn at which you took over.

## Ending and feedback

When the human reports `STATUS: DONE` or `STATUS: STUCK`, or a cap is hit:

1. Human feedback. Send the human role this text (fill in the path):
   `The simulation is over; thank you. Step out of the conversation and write your feedback as the user to SIMDIR/feedback/human.md, drawing on your notes.md: (1) did you get what you needed, satisfaction 1–10, and would you use this again; (2) your top pain points ranked, each with the moment it happened, severity (blocker/major/minor), and what would have helped; (3) the README: what was missing, unclear, or wrong, and what you needed to know that it did not tell you; (4) the agent's communication: jargon, message length, quality of its questions and of the scoping interview; (5) which answers you trusted and which you did not, and why; (6) the deck package review and release experience; (7) where turns or time were wasted; (8) what worked well. Reply with only the word DONE when the file is written.`
   For the Codex human, it cannot write outside its folder reliably, so ask it to write the file at `SIMDIR/human/feedback.md` instead and copy it to `SIMDIR/feedback/human.md` yourself.
2. Agent feedback. Send the agent role this text (fill in the path):
   `[Harness note, not from the user: the session is over. Step out of the conversation and write your feedback as the agent to SIMDIR/feedback/agent.md, drawing on your agent-notes.md: (1) pain points with the skills, project instructions, workbench guides, helpers, and MCP tools or CLI, ranked, each naming the file or tool, severity (blocker/major/minor), and a suggested fix; (2) instructions that were contradictory, ambiguous, too long, or missing; (3) commands or tools that failed or behaved unexpectedly, with the exact command and error; (4) where you deviated from the instructions and why; (5) where time or tokens went disproportionately; (6) what worked well. Reply with only the word DONE when the file is written.]`
   If the Codex agent cannot write there, save its reply to that path yourself.
3. Verify the end point yourself by inspecting `SIMDIR` (project records such as the investigation's question ledger and state, recorded results, the package draft, `deliveries/`, and `SIMDIR/storage/releases/`). For each of the five questions in `SIMDIR/human/BRIEF.md`, find the agent's final answer in the transcript and whether a recorded result backs it. Independently spot-check at least two of the answers against the source data with your own read-only query (you may use the project's virtual-environment Python, which should have duckdb, on the landed or published files; do not write into the project). Record any discrepancy. Also check isolation: search the Codex logs under `SIMDIR/relay/` for reads of `workbench-spec`, `workbench-design`, `CONTEXT.md`, a `docs/` folder, or paths under `/Users/` outside `SIMDIR` (Variant A), and ask the Opus agent role whether it read anything outside its bounds (Variant B); report what you find.
4. Write `SIMDIR/feedback/orchestrator-report.md` with: the variant and roles; start and end times, wall-clock, number of human and agent turns; the end-point checklist (each criterion met / not met, with evidence paths); a table of the five questions with the agent's answer, whether it is recorded, and your spot-check result; a timeline of the main phases (init, scoping, landing, cleaning, exploring, answering, status, packaging, review, release) with turn numbers; pain points you observed as referee (errors, loops, stalls, wrong or unsupported numbers, skill misuse, protocol or isolation breaches, slow phases), each with turn references and severity; and the most important issues for the workbench maintainers, ranked.
5. Your final report back to me: three to six lines with the outcome (end point reached or not), turn counts, wall-clock, the top three issues, and the paths of the four feedback files (`human.md`, `agent.md`, `agent-notes.md`, `orchestrator-report.md`) plus `transcript.md`.

Begin now. Record the start time.
