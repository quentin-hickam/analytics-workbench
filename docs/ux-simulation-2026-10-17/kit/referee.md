# Referee playbook: analytics-workbench UX simulation (2026-10-16 harness)

You referee one simulation of a first-time user working with an AI agent that has the "analytics workbench" (`awb-*`) skills installed. Paths: `KIT` = `{KIT}`, `SIMDIR` = `{SIMDIR}`. Run `{ID}`, variant **{VARIANT}**.

- Variant A: Claude (Opus, headless `claude -p`) plays the user; Codex (`codex exec`) plays the agent.
- Variant B: Codex plays the user; Claude (Opus, headless `claude -p`, real Claude Code skill discovery) plays the agent.

Both roles are CLI sessions driven by `KIT/relay.py`, a deterministic relay: it passes messages verbatim, strips the user's STATUS line, enforces the caps ({CAPS}), and asks both roles for feedback at the end. You do not relay anything and never message either role. You start the relay, wait for it, then verify and report.

## Hosts under test

- Codex agent (A): fake HOME holding only the release; the awb MCP server registered with the release's own `codex mcp add` command and its tools auto-approved (standing in for a user who clicks Allow, which non-interactive exec cannot ask); Python 3.13 first on PATH; the project's `.git` writable; Codex's bundled skills off; workspace-write sandbox with network.
- Claude agent (B): headless Claude Code with user settings, user CLAUDE.md and auto memory turned off; the awb skills linked into a simulated `~/.claude/skills` and discovered through `--add-dir`; the awb MCP server registered for the session (a stand-in for the README's user-level registration) with its tools allowed; common tools allowed without prompts, and every remaining permission prompt answered Allow by a harness tool that logs it to `SIMDIR/relay/permission-prompts.jsonl` (each line is a prompt a real Claude Code user would have had to approve: count them, they are product evidence); session-messaging and scheduling tools removed; git, uv and pip pointed at the simulated home; a short system-prompt note giving the simulated home folder and the boundaries.
- Both agents got the same first-turn harness note asking for a private friction log in `SIMDIR/feedback/agent-notes.md`.
- The Claude user (A) can use only Read, Write, Edit, Glob and Grep, with reads of agent-only paths denied.
- The relay passes all of the agent's messages within a turn (interim ones too, as an interactive user would see them), checks the caps only after an agent reply so every user message is answered, and collects the agent's feedback before the user's.

## Rules

- Never read the analytics-workbench source repository or its docs, and never modify anything under `KIT` or inside the project. You may read anything under `SIMDIR`. Do not run git in the project except read-only commands prefixed with `GIT_OPTIONAL_LOCKS=0`.
- Role logs are JSON lines: `SIMDIR/relay/<role>-NNN.jsonl` (Claude stream-json or Codex `--json`), with the command line in `<role>-NNN.err`. Read them through `python3 KIT/logview.py <file>...` (add `--full` for uncut tool inputs), not raw. Per-turn timings, MCP failures and permission denials are summarized in `SIMDIR/feedback/harness-log.md`.
- Do not use `sleep` (it is blocked). `relay.py wait` is your wait.

## 1. Run the relay

1. `python3 KIT/relay.py status SIMDIR`. If the phase is empty, `python3 KIT/relay.py start SIMDIR`. If it is already running or finished (a resumed referee), do not start it again.
2. Loop `python3 KIT/relay.py wait SIMDIR --timeout 540` (give the Bash call a 600000 ms timeout, or it is cut off at two minutes) until it prints `FINISHED` or `DEAD`. A run takes one to three hours, so expect many waits. Between waits you may skim `SIMDIR/transcript.md` and `SIMDIR/feedback/harness-log.md` to note events for your report; keep your reads short.
3. If it prints `DEAD`, read `SIMDIR/relay/relay.log` and the harness log, record what happened, and continue with what you can verify. Do not restart the conversation.

## 2. Verify and report

1. Read `SIMDIR/transcript.md` in full (count user messages and agent replies from it: a user request counts as delivered only when an agent reply follows it; the final DONE message is never relayed), `SIMDIR/feedback/human.md`, `agent.md`, `agent-notes.md`, `harness-log.md`, and `SIMDIR/human/notes.md`.
2. End point: for each criterion in `SIMDIR/human/BRIEF.md` ("The path to the end point"), met or not, with evidence paths: the five answers accepted, `awb-status` (or an equivalent "where are we") asked at least once, a package draft reviewed by the user, released as 001 and copied to `SIMDIR/storage/releases/`. Inspect the project records (question ledger, state, recorded results, the package draft, `deliveries/`) and `SIMDIR/storage/releases/`.
3. Answers: for each of the five questions, the agent's final answer, whether a recorded result backs it, and an independent spot-check of at least two answers against the source data with your own read-only query (the project's own Python environment or `uv run --with duckdb python -I`, on the landed files under `SIMDIR/storage/landed/` or `SIMDIR/inbox/`; write scripts only under `SIMDIR/referee/`).
4. Isolation audit:
   - Agent logs (`SIMDIR/relay/agent-*.jsonl`, through `logview.py --full`): search for reads, including awb MCP `read`/`data` SQL that reads files, of `workbench-spec`, `workbench-design`, `CONTEXT.md`, a `docs/` folder, `analytics-workbench` repository paths, `SIMDIR/human`, `SIMDIR/relay`, `transcript.md`, and, for the Claude agent, any path under the real home directory (`/Users/`) outside `SIMDIR`. The Claude logs are stream-json: tool inputs are in `tool_use` entries.
   - User logs (`SIMDIR/relay/human-*.jsonl`): reads of `AGENTS.md`, `SKILL.md`, `src/`, `.py` files, `workbench-guides/`, agent homes.
   Report each hit with the turn and whether it mattered.
5. Write `SIMDIR/feedback/orchestrator-report.md`: run and variant; start and end times, wall-clock, number of user messages and agent turns (from `SIMDIR/relay/state.json` and the transcript); the end-point checklist; a table of the five questions (answer, recorded or not, spot-check); a timeline of the main phases (init, scoping, landing, cleaning, exploring, answering, status, packaging, review, release) with message numbers; pain points you observed as referee (errors, loops, stalls, wrong or unsupported numbers, skill misuse, protocol or isolation breaches, slow phases) with message references and severity; the user's satisfaction score; and the most important issues for the workbench maintainers, ranked.
6. Write `SIMDIR/feedback/findings.json`: a JSON list with one object per distinct issue reported by the user (feedback and notes), the agent (feedback and notes) or you, with keys `id` (`{ID}-NN`), `source` (list of user/agent/referee), `summary` (one sentence), `evidence` (message numbers and file paths), `severity` (blocker/major/minor), `tag` (`product`, `harness` or `unclear`), and `tag_reason` (one sentence). Tag `harness` anything caused by how the simulation runs rather than by the released skills, README, helpers or MCP server: relay mistakes, Codex sandbox or approval limits, non-interactive CLI sessions, the simulated home, a role breaking its protocol, personas front-loading answers (the persona briefs list facts to give "if it asks", and both models tend to volunteer them; that thins the scoping interview and is a known study limit, kept for comparability with Oct 15). Tag `product` only what a real user of the release on a normal interactive host would also hit. When unsure, `unclear`, with the reason.
