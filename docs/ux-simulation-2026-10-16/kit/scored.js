export const meta = {
  name: 'ux-sim-scored',
  description: 'Six scored UX simulations (3 datasets x 2 role pairings, both roles as headless CLI sessions), blind recompute of every answer from source, product-vs-harness tagging, cross-run consolidation, skeptic verification, and a report against Oct 15',
  phases: [
    { title: 'Runs', detail: 'one referee per run starts the deterministic relay, waits, verifies the end point' },
    { title: 'Grade', detail: 'two blind recomputes per run plus independent finding tagging' },
    { title: 'Compare', detail: 'agent answers vs recomputes, per question' },
    { title: 'Consolidate', detail: 'merge findings across runs, map to Oct 15' },
    { title: 'Verify', detail: 'two skeptics per product finding' },
    { title: 'Report', detail: 'comparison report and proposed issue list' },
  ],
}

const K = args.kit, OCT = args.oct15, REL = args.release, OUT = args.out

const RUN_RESULT = {
  type: 'object',
  properties: {
    end_point_met: { type: 'boolean' },
    end_point_notes: { type: 'string' },
    human_messages: { type: 'integer' },
    agent_turns: { type: 'integer' },
    wall_clock_minutes: { type: 'number' },
    satisfaction: { type: 'string', description: 'score out of 10 as the human gave it, or "none"' },
    answers: { type: 'array', items: { type: 'object', properties: { q: { type: 'integer' }, answer: { type: 'string' }, recorded: { type: 'string' }, spot_check: { type: 'string' } }, required: ['q', 'answer', 'recorded', 'spot_check'] } },
    top_issues: { type: 'array', items: { type: 'string' } },
    harness_events: { type: 'array', items: { type: 'string' } },
    fallback_used: { type: 'boolean' },
  },
  required: ['end_point_met', 'end_point_notes', 'human_messages', 'agent_turns', 'satisfaction', 'answers', 'top_issues', 'harness_events', 'fallback_used'],
}
const RECOMP = {
  type: 'object',
  properties: {
    source_files: { type: 'array', items: { type: 'string' } },
    answers: { type: 'array', items: { type: 'object', properties: { q: { type: 'integer' }, answer: { type: 'string' }, method: { type: 'string' }, assumptions: { type: 'string' } }, required: ['q', 'answer', 'method', 'assumptions'] } },
  },
  required: ['source_files', 'answers'],
}
const TAGGED = {
  type: 'object',
  properties: {
    findings: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' }, summary: { type: 'string' }, source: { type: 'string' }, evidence: { type: 'string' },
      severity: { type: 'string', enum: ['blocker', 'major', 'minor'] },
      tag: { type: 'string', enum: ['product', 'harness', 'unclear'] }, tag_reason: { type: 'string' },
      orchestrator_tag: { type: 'string' },
    }, required: ['id', 'summary', 'source', 'evidence', 'severity', 'tag', 'tag_reason', 'orchestrator_tag'] } },
  },
  required: ['findings'],
}
const COMPARE = {
  type: 'object',
  properties: {
    per_question: { type: 'array', items: { type: 'object', properties: {
      q: { type: 'integer' }, agent_answer: { type: 'string' }, recompute_sql: { type: 'string' }, recompute_pandas: { type: 'string' },
      verdict: { type: 'string', enum: ['match', 'match_within_rounding', 'differs_by_definition', 'mismatch', 'unanswered'] }, explanation: { type: 'string' },
    }, required: ['q', 'agent_answer', 'verdict', 'explanation'] } },
    summary: { type: 'string' },
  },
  required: ['per_question', 'summary'],
}
const CONSOL = {
  type: 'object',
  properties: {
    findings: { type: 'array', items: { type: 'object', properties: {
      cid: { type: 'string' }, title: { type: 'string' }, description: { type: 'string' },
      runs: { type: 'array', items: { type: 'string' } }, severity: { type: 'string' },
      tag: { type: 'string', enum: ['product', 'harness', 'unclear'] },
      oct15_ref: { type: 'string', description: 'Oct 15 synthesis/fix-plan IDs and GitHub issue numbers it relates to, or "new"' },
      oct15_status: { type: 'string', enum: ['new', 'persists', 'partly_fixed', 'regressed', 'n/a'] },
      evidence: { type: 'string' }, member_ids: { type: 'array', items: { type: 'string' } },
    }, required: ['cid', 'title', 'description', 'runs', 'severity', 'tag', 'oct15_ref', 'oct15_status', 'evidence', 'member_ids'] } },
    fixed_since_oct15: { type: 'array', items: { type: 'object', properties: { oct15_ref: { type: 'string' }, evidence: { type: 'string' } }, required: ['oct15_ref', 'evidence'] } },
  },
  required: ['findings', 'fixed_since_oct15'],
}
const VERDICT = {
  type: 'object',
  properties: {
    verdict: { type: 'string', enum: ['product', 'harness', 'unsupported'] },
    confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
    reasoning: { type: 'string' },
    release_evidence: { type: 'string', description: 'file:line in the release that causes or contradicts it, or "none found"' },
  },
  required: ['verdict', 'confidence', 'reasoning', 'release_evidence'],
}

const orchPrompt = r =>
  `You are the referee for one scored usability-simulation run. Read ${r.simdir}/REFEREE.md and follow it exactly, from start to finish: start the relay (unless it is already running or finished), wait for it with relay.py wait until FINISHED or DEAD, then verify the end point, spot-check at least two answers against the source data, audit isolation, and write orchestrator-report.md and findings.json.\n\n` +
  `Never message either role, never read the analytics-workbench source repository or its docs, and never modify anything under ${K} or inside the project. Return the structured result: end point met or not, counts, wall-clock, the user's satisfaction score, each of the five questions with the agent's final answer, whether a recorded result backs it, and your spot-check, the top issues, and every harness event (fallback_used is always false in this harness).`

const recomputePrompt = (r, how) =>
  `You are an independent grader recomputing the answers of one usability simulation from the source data, blind to what the simulated agent answered.\n\n` +
  `Read the five questions and the persona's definitions (what "countries" means, which years, which variable, and so on) in ${r.simdir}/human/BRIEF.md. Use as source data only the original files the run landed in ${r.simdir}/storage/landed/ (look recursively), or, for taxi, ${r.simdir}/inbox/. If nothing was landed, download the dataset from the URL in BRIEF.md into ${OUT}/grading/${r.id}-${how}/data/ (a new empty folder) and use that.\n\n` +
  `Do NOT read ${r.simdir}/transcript.md, ${r.simdir}/project/, ${r.simdir}/feedback/, ${r.simdir}/relay/, ${r.simdir}/handoff/ or the human's notes: you must not see the agent's answers. Work only in ${OUT}/grading/${r.id}-${how}/ (create it). Run Python with -I and pass file paths as arguments. ` +
  (how === 'sql'
    ? `Compute with DuckDB SQL (\`uv run --with duckdb --with openpyxl python -I script.py\`; uv is <homebrew>/bin/uv).`
    : `Compute with pandas (\`<python-prefix>/bin/python3 -I script.py\`; add openpyxl or pyarrow through \`uv run --with pandas --with pyarrow --with openpyxl python -I script.py\` if needed). Do not use DuckDB.`) +
  ` Where a question is ambiguous, pick the reading the persona's definitions support, and state your assumptions. Save your scripts and outputs in your folder. Return each answer with the numbers in full (ranked lists with values, counts, shares, years used).`

const tagPrompt = r =>
  `You are an independent reviewer of one usability simulation of the "analytics workbench" skills release. Your job is to list every distinct issue the run surfaced and tag each one as a product issue or a harness artifact.\n\n` +
  `Read in ${r.simdir}/feedback/: human.md, agent.md, agent-notes.md, orchestrator-report.md, harness-log.md and findings.json (the referee's own tagging), plus ${r.simdir}/human/notes.md, and consult ${r.simdir}/transcript.md and the role logs in ${r.simdir}/relay/ for evidence (read *.jsonl logs through "python3 ${K}/logview.py <file>", not raw; ${r.simdir}/relay/permission-prompts.jsonl, if present, lists permission prompts a real Claude Code user would have had to approve). You may read the release under test at ${REL} to check what the product actually ships.\n\n` +
  `How the run worked: a simulated user and a simulated agent talked through a relay. Variant ${r.variant}: ${r.variant === 'A' ? 'Claude Opus (headless claude -p) plays the user; Codex (codex exec, non-interactive, workspace-write sandbox, fake HOME) plays the agent, with the awb MCP server registered and its tools auto-approved' : 'Codex (codex exec) plays the user; Claude Opus in headless Claude Code (claude -p) plays the agent, with real skill discovery of the awb skills, the awb MCP server registered and its tools allowed, user settings off, and a short system-prompt note giving the simulated home folder and boundaries'}. A deterministic script relays messages verbatim (no model in between).\n\n` +
  `Tag "harness" anything caused by how the simulation runs rather than by the released skills, README, helpers or MCP server: relay mistakes, Codex sandbox or approval limits, non-interactive CLI sessions (no mid-turn prompts), the simulated home folder, a model role breaking its protocol, personas front-loading answers. Tag "product" only what a real user of the release on a normal host (VS Code Copilot, Claude Code or Codex, interactive) would also hit. Model behavior that the release's instructions caused or failed to prevent counts as product; model behavior the instructions clearly forbid counts as product only if it recurs, else "unclear". Make your own judgment; record the referee's tag in orchestrator_tag. Use ids ${r.id}-NN. Be complete: one entry per distinct issue, including minor ones.`

const comparePrompt = (r, x) =>
  `You grade whether one usability simulation's final answers are correct. Read the agent's final answers to the five questions in ${r.simdir}/transcript.md (the last answer the agent gave for each, plus any corrections; the orchestrator's summary of them is below) and the questions and definitions in ${r.simdir}/human/BRIEF.md.\n\n` +
  `Orchestrator's answers table:\n${JSON.stringify(x.res ? x.res.answers : 'unavailable', null, 1)}\n\n` +
  `Independent recompute with DuckDB (blind to the agent):\n${JSON.stringify(x.a, null, 1)}\n\nIndependent recompute with pandas (blind to the agent):\n${JSON.stringify(x.b, null, 1)}\n\n` +
  `For each question give a verdict. "differs_by_definition" means the difference comes from a defensible definitional choice the user agreed to in the transcript (say which); "mismatch" means a real error by the agent or a recompute. When the two recomputes disagree with each other, work out which is right, if needed by running your own read-only query on the landed files (scripts only in ${OUT}/grading/${r.id}-compare/; Python with -I). Do not modify anything under ${r.simdir}.`

// ---------- per-run pipeline ----------
const perRun = await pipeline(args.runs,
  r => agent(orchPrompt(r), { label: `run:${r.id}`, phase: 'Runs', schema: RUN_RESULT }),
  (res, r) => parallel([
    () => agent(recomputePrompt(r, 'sql'), { label: `recompute-sql:${r.id}`, phase: 'Grade', schema: RECOMP }),
    () => agent(recomputePrompt(r, 'pandas'), { label: `recompute-pandas:${r.id}`, phase: 'Grade', schema: RECOMP }),
    () => agent(tagPrompt(r), { label: `tag:${r.id}`, phase: 'Grade', schema: TAGGED }),
  ]).then(([a, b, t]) => ({ id: r.id, res, a, b, t })),
  (x, r) => agent(comparePrompt(r, x), { label: `compare:${r.id}`, phase: 'Compare', schema: COMPARE }).then(c => ({ ...x, compare: c })),
)
const done = perRun.filter(Boolean)
log(`${done.length}/${args.runs.length} runs graded`)

// ---------- consolidate across runs (needs every run's findings) ----------
phase('Consolidate')
const allFindings = done.map(x => ({ run: x.id, findings: x.t ? x.t.findings : [] }))
const consol = await agent(
  `Consolidate the issues found across ${done.length} usability simulations of the analytics workbench release into one deduplicated list. Input (each run's independently tagged findings):\n${JSON.stringify(allFindings)}\n\n` +
  `Merge findings that describe the same underlying problem; keep the most severe credible severity; list the runs; keep the tag (when members disagree, prefer the better-evidenced tag and say so in the description). Then map each to the Oct 15 study: read ${OCT}/README.md (synthesis) and ${OCT}/fix-plan.md (57 classified findings, phases 1-7 = GitHub issues #61-#67). Set oct15_status: "new", "persists" (the same problem recurs), "partly_fixed", "regressed", or "n/a" for harness items. Also list Oct 15 product findings that did NOT recur and show evidence of being fixed in this run set (fixed_since_oct15), citing run evidence. Use cids C-01, C-02, ... ordered by severity then by number of runs.`,
  { label: 'consolidate', phase: 'Consolidate', schema: CONSOL })

// ---------- skeptic verification of product findings ----------
phase('Verify')
const toVerify = (consol ? consol.findings : []).filter(f => f.tag !== 'harness')
log(`${toVerify.length} product/unclear findings to verify; ${(consol ? consol.findings.length : 0) - toVerify.length} harness findings not verified`)
const lenses = [
  { key: 'harness', text: 'Your lens: is this really a harness artifact? Try hard to show it was caused by how the simulation was run (non-interactive codex exec or claude -p, the Codex sandbox, auto-approved MCP tools, the simulated home folder, relay mistakes, model role behavior, personas front-loading answers) rather than by the release. Default to "harness" if the evidence points that way.' },
  { key: 'release', text: 'Your lens: does the release actually cause this? Open the shipped files under the release path and find the instruction, helper code, template or README text that causes it, or that already prevents it (in which case the finding is "unsupported" unless the agent ignored a clear instruction repeatedly). Check that the cited run evidence really shows the problem.' },
]
const verified = await parallel(toVerify.map(f => () =>
  parallel(lenses.map(l => () => agent(
    `You are a skeptic verifying one finding from usability simulations of the analytics workbench skills release (release under test: ${REL}; run folders: ${args.runs.map(r => r.simdir).join(', ')}).\n\nFinding ${f.cid}: ${f.title}\n${f.description}\nRuns: ${f.runs.join(', ')}. Severity: ${f.severity}. Evidence: ${f.evidence}\n\n${l.text}\n\nRead the evidence yourself (transcripts, feedback files, relay logs, project files in the run folders, and the release). Do not modify anything. Verdict: "product" (a real user on a normal interactive host would hit it, and the release is the cause), "harness", or "unsupported" (the evidence does not show it).`,
    { label: `verify-${l.key}:${f.cid}`, phase: 'Verify', schema: VERDICT })))
    .then(vs => ({ ...f, verdicts: vs.filter(Boolean).map((v, i) => ({ lens: lenses[i].key, ...v })) }))))
const verifiedOk = verified.filter(Boolean).map(f => {
  const p = f.verdicts.filter(v => v.verdict === 'product').length
  return { ...f, final: p === f.verdicts.length && p > 0 ? 'confirmed' : p > 0 ? 'contested' : 'rejected' }
})

// ---------- report ----------
phase('Report')
const data = {
  runs: done.map(x => ({ id: x.id, result: x.res, compare: x.compare })),
  consolidated: verifiedOk,
  harness_findings: (consol ? consol.findings : []).filter(f => f.tag === 'harness'),
  fixed_since_oct15: consol ? consol.fixed_since_oct15 : [],
}
const report = await agent(
  `Write the comparison report for a re-run of the analytics workbench UX simulations, and a proposed issue list. Write two files: ${OUT}/report/README.md and ${OUT}/report/proposed-issues.md (create the folder). Also save the raw data below as ${OUT}/report/data.json.\n\n` +
  `Context: on 2026-10-15 six simulated first-time users took the awb-* skills from an empty folder to a released deck package (synthesis: ${OCT}/README.md; classified findings and the seven phases that became GitHub issues #61-#67: ${OCT}/fix-plan.md). Those issues have since been fixed and merged. This re-run used the release built from current main at ${args.commit}, the same three datasets, persona briefs, end point and role swap (A = Opus user, Codex agent; B = Codex user, Opus agent), with a rebuilt harness: both roles ran as headless CLI sessions (codex exec and claude -p) driven by a deterministic relay script, with no model relaying; the Codex agent had the awb MCP server registered with tools auto-approved, a writable .git, Python 3.13 on PATH and Codex's bundled skills off; the Claude agent ran in real headless Claude Code with real skill discovery and the awb MCP server (on Oct 15 the Opus agent was a subagent imitating a host with no MCP server, so variant B results are not strictly like-for-like). Per-run referees verified end points and audited isolation. New this time: every answer was recomputed blind from the source data twice (DuckDB and pandas) and graded; every finding was tagged product vs harness by the run's referee and again independently; product findings were checked by two skeptics (harness lens, release lens). Only product findings count toward scores and the issue list.\n\n` +
  `Data:\n${JSON.stringify(data)}\n\n` +
  `README.md: follow the shape of ${OCT}/README.md (bottom line, method, results by run table with the same columns plus an answer-accuracy column, findings ranked, what worked, differences between variants, isolation, limits) and add a "Compared with Oct 15" section: per Oct 15 finding area 1-11, fixed / improved / persists / regressed with evidence, and the score and turn/wall-clock deltas. Keep harness findings in their own section, clearly excluded from scoring. Link per-run evidence by relative path SIMS/<run>/... as the Oct 15 study did.\n` +
  `proposed-issues.md: only "confirmed" findings, plus "contested" ones in a separate clearly marked section; group them into PR-sized issues the way the Oct 15 fix plan did, each with a title, the problem, evidence (runs, files), the release file:line that causes it, a suggested fix direction, and severity. Nothing is filed; this is a proposal for the maintainer to review.\n` +
  `Style: plain English, short sentences, no em-dashes. Do not mention any employer, company or work environment. Return a 10-line summary of the bottom line.`,
  { label: 'report', phase: 'Report' })
return { summary: report, runs: data.runs.map(r => ({ id: r.id, end: r.result && r.result.end_point_met, sat: r.result && r.result.satisfaction })), confirmed: verifiedOk.filter(f => f.final === 'confirmed').length, contested: verifiedOk.filter(f => f.final === 'contested').length }
