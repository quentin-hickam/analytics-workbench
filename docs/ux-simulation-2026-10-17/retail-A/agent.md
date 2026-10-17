# Agent feedback: retail-A workbench usability session

The task completed: all five original questions were answered, the requested Q4 comparison was produced, leadership approved the eight-slide narrative and methodology note, two global review rules were saved, and release 001 was frozen and copied to the configured releases folder with verification. No experienced issue permanently blocked completion. This report draws on agent-notes.md; it distinguishes tool failures, expected validation refusals, and my own mistakes.

## 1. Ranked pain points

| Rank | File/tool | Severity | Observed friction | Suggested fix |
| --- | --- | --- | --- | --- |
| 1 | awb-status/SKILL.md; awb read status; state finding model | major | Status exposed seven supported and seven provisional findings for five business questions. The user explicitly asked what the fourteen were. Alternative rankings, summaries, intake checks and sensitivity checks were counted alongside business conclusions. “Provisional” also mixed user acceptance with analytical uncertainty. | Lead status with root business questions. Group supporting calculations/checks beneath each. Distinguish evidence validation, analyst confidence and user acceptance; do not make a sound intake check appear unresolved merely because a slide headline has not been approved. |
| 2 | awb-package/SKILL.md, references/package-contract.md, references/review.md, package-format/* | major | A small deck required a large amount of format reading, thirteen represented-result citations, export metadata, review launch/record ordering, checks and inventory handling. Some work improved accuracy; some enforced syntax/style rather than the decision. | Provide a short executable checklist for preview-only, full draft, bounded text edit and release. Offer a single preparation/check operation that performs ordered mechanical steps and returns only actionable gaps. Keep detailed reference material behind targeted error links. |
| 3 | Package source/translation workflow; findings-template.md; methodology-note-template.md | major | I initially exposed the download distributor and research attribution in audience sources. The user needed their own order-system description and corrected it late. “Signed quantity,” “grouping keys” and “permitted repeated line occurrences” also survived the initial audience review despite the translation rule. | Store original business source identity separately from acquisition/distribution provenance at intake. Generate audience source lines from that business identity. Add an early audience-language pass that checks technical terms in methods, notes and chart footers, not just record IDs. This was partly an execution failure on my part, not absence of a translation instruction. |
| 4 | awb read state/status; tool text envelopes; large manifest | major | Important output was truncated or cached. Cached status text included a JSON object followed by an exit-status trailer, so ordinary json.loads failed. Batched long reads repeatedly exceeded output budgets. The manifest became about 20,000 tokens. | Return structuredContent for facts, expose compact/focused state/status modes and machine-readable cached JSON without trailers. Add manifest summary/projection reads. I also should have used targeted reads earlier. |
| 5 | package-format/findings-template.md; awb-package headline checkpoint | minor | Title + Answer + five findings + required method and limitations slides naturally makes nine slides, before appendices. To meet about eight, I combined Q2/Q3. A useful user-written headline had sixteen words and needed an acceptance field. | Make methods/limitations slide count flexible when a separate methodology note exists. Treat the headline length as a readability warning, and recognize explicit user-supplied wording as an acceptance without another question. Preserve the existing exception mechanism. |
| 6 | Brief Methods note length parser; check-draft numbers | minor | “Methods note length: about 500 words. The user requested …” was rejected although its meaning was unambiguous. An acquisition date embedded in an ID also needed an allowed_numbers entry. | Use structured metadata for length and non-metric identifiers; otherwise tolerate punctuation and trailing explanatory prose, and recognize registered acquisition identifiers automatically. |
| 7 | awb-package/references/review.md | minor | The fresh reviewer caught useful citation problems, but also objected to “keep the saved ranking” inside a chart-axis instruction as an imperative outside Implications. Review lifecycle bookkeeping and another review after adding approved rules were substantial relative to the edits. | Exempt builder specifications from audience prose style rules. Keep evidence and causal-claim review strict, but distinguish editorial warnings from release blockers. Automate scoped-review lifecycle and bind reports to snapshots directly. |
| 8 | awb-package/SKILL.md, review.md: future-rule question | minor | The skill requires asking about reusable checks before repairing a repeatable correction. The user had already authorized the repair and dislikes interruptions. I asked asynchronously and completed the edits without waiting; the user approved global rules next turn. | Make this explicitly optional and nonblocking: apply the authorized correction, ask once whether to retain a rule, and save only on yes. Do not require a separate approval round before an ordinary repair. |
| 9 | awb-release/SKILL.md report requirements | minor | The user asked where the delivered copy ended up, but the skill requires reporting every open caveat, including the limitations headline and all bullets already approved. This lengthened a simple completion response. | Report the release number, verified path and genuinely outstanding action in chat; put the full frozen caveat list in the release record and link it. |
| 10 | Sandbox shell environment, project interpreter/cache setup | minor | zsh heredocs could not create temporary files. Git/xcrun and pip tried unwritable default cache locations. These were environment issues, not AWB failures. | Supply writable TMPDIR/TMPPREFIX/cache defaults in the environment and a documented safe Python -c pattern. Helpers should use configured local cache paths. |

## 2. Contradictory, ambiguous, overlong or missing instructions

- **Status order:** awb-status says other requested work follows its report, while the user explicitly said to do the Q4 comparison and then status. I followed the user's order so the report reflected the new work. The skill should explicitly defer to such ordering.
- **Supported versus provisional:** instructions tie promotion to user approval of finding/headline wording. That is not the same as validity or evidence strength. Supporting policy checks remained provisional even though checks passed and the policy was approved; this confused the user. A three-axis model would be clearer.
- **Rule retention timing:** “ask before repairing” in review.md conflicts operationally with completing an already authorized, reversible correction without unnecessary permission gates. The optional asynchronous question resolved it, but the skill does not clearly describe that path.
- **Repeated questions despite explicit answers:** awb-package says to ask whether the audience needs a methodology note and which datasets to include. The user had already requested the note and later explicitly said no tables. I treated those as answers rather than re-asking. Add “unless already explicitly answered.”
- **Original source versus distributor:** the acquisition instructions were strong on URLs, documentation and attribution, but business source identity was not a separately operationalized field for package generation. Keeping UCI download provenance internally and the company's source identity in leadership material solved the actual need.
- **Counts and display rounding:** exact full-precision evidence and human-readable approximations need a clearer interface. The user suggested “about 22,500”; I used exact 22,523 in plain English, avoiding a new rounding allowance while preserving the intended simplification.
- **Preview-only path is buried:** the package skill starts with full-draft steps, although the required next action was only headline approval. A short preview-only read/write contract would avoid loading manifest, chart, review and release details too early.
- **Review style rules versus specification instructions:** imperative language is sensible in a chart-building field. The blanket outside-Implications rule does not distinguish the audience claim from builder instructions.
- **Strict Markdown-as-configuration:** note length, Claim strength lines, exact question repetition, chart Data roles and ledger question wording are distributed across several references. Errors often require understanding another document's parser, rather than a small typed metadata schema.
- **Helper black-box rule versus required run.py reading:** the general project rule discourages opening shipped helpers except to adapt/debug, while package gathering explicitly asks for run.py/producers. I read the investigation runner because the skill explicitly required it, without altering it.
- **Review cap:** review.md says to stop after a second review still reports problems, even when they might be minor and fully repairable. That could conflict with persistent completion under existing authorization. It did not block this task: the second review was clean.
- **Release authorization was clear:** the user approved the changed lines and explicitly marked delivered. No additional confirmation of the same draft was warranted. The release skill supported that path.
- No missing skill, unavailable AWB command, or irreconcilable instruction conflict prevented completion.

## 3. Failures and unexpected behavior

Commands below are exact where preserved in the running log. Early multiline script bodies were not retained in agent-notes.md; I identify their exact recorded invocation/error rather than inventing the omitted body.

### Environment and shell

1. Invocation `python3 - <<'PY'` (ancestry-check script, closed by `PY`) failed before Python ran:
   `zsh:1: can't create temp file for here document: operation not permitted`.
   The same failure later occurred with `.venv/bin/python - <<'PY'` while inspecting the preview and appending notes. Properly single-quoted `python -c` worked. The full bodies are not preserved in the notes.
2. `ls -la && git rev-parse --show-toplevel` returned 128:
   `could not create cache file /var/folders/cr/64mtlg6x6j3_sjjtj19wyfzh0000gn/T/xcrun_db-clqU3U26 (errno=Operation not permitted)`
   and `fatal: not a git repository (or any of the parent directories): .git`.
   The latter was expected in an empty project.
3. `TMPDIR="$PWD/.workbench-tmp" git init` still produced an xcrun system-temp warning but successfully initialized Git (exit 0).
4. `.venv/bin/python -m pip install duckdb pandas` succeeded, but pip disabled its unwritable default cache under agent-home/Library/Caches/pip. Matplotlib installation had the same cache limitation; plotting worked with MPLCONFIGDIR in ignored project-local storage.

### Expected absent paths and timing

5. `rg --files deliveries package-format investigations/marketing-budget foundation workbench-guides` returned 2:
   `rg: deliveries: No such file or directory (os error 2)`
   and `rg: package-format: No such file or directory (os error 2)`.
   These were expected before the first package; setup installed the missing formats.
6. `cat foundation/review-rules.md` returned 1:
   `cat: foundation/review-rules.md: No such file or directory`.
   No rules had yet been recorded; the reviewer correctly treated this as “none recorded,” not a command problem.
7. `ls -lh data/raw/online-retail-ii/uci-20261017.partial` returned “No such file or directory” because acquisition had already atomically renamed the completed directory. No download recovery was necessary.
8. `rg -n 'Active investigation|Project interpreter' README.md && ls -ld data/raw deliveries investigations/marketing-budget` returned 1 because data/raw and deliveries intentionally did not yet exist. The active investigation pointer itself was correct.
9. Initial `pwd && rg --files -g AGENTS.md -g !node_modules -g !vendor -g !\.git -g *` returned 1 in an empty project. The actual tool call shell-quoted the glob arguments; those exact quoting characters are not retained in the log.

### Parsing, validation and my own mistakes

10. Parsing cached awb read status text with json.loads raised:
    `json.decoder.JSONDecodeError: Extra data: line 3 column 1 (char 16410)`.
    The cached file appended `exit status 0` after JSON. JSONDecoder.raw_decode(...)[0] recovered the object without rerunning status.
11. A verification assertion incorrectly expected plain text:
    `assert "Active investigation: marketing-budget" in (r/"README.md").read_text()`
    raised `AssertionError`. The helper correctly wrote a Markdown link. I corrected my assertion, not the helper output.
12. AWB state finding for sensitivity-summary warned:
    `118465.589 is not a value its table, profile, checks, or settings record; check the number or reword`.
    That value was in the detailed sensitivity result, not its summary. I removed it from that finding text and retained its properly traced presentation elsewhere. This was a useful guard.
13. `mcp__awb__read(command="check-draft", investigation="marketing-budget", package="leadership-budget", project=<project root>)` returned exit 1 before the first final inventory/review:
    - `manifest: manifest.json records no inventory list; run check-draft without --verify-only`;
    - `the methods note length is not written as Methods note length: about <n> words`;
    - `20261017` was reported as an unrecorded number.
    The missing inventory/review were expected intermediate state. The note line required removing trailing prose; the acquisition ID received a non-quantity allowance.
14. The same read-only check after a bounded wording edit reported changed sizes/checksums and stale review. This was expected until review and final inventory refresh, not a data failure.
15. State/status and several batched reads were truncated. Examples: combined outputs of 19,979 and 10,479 tokens; `cat deliveries/marketing-budget/leadership-budget/draft/manifest.json` was 20,088 original tokens with a 1,400-token output budget. The broad manifest read was my poor choice; targeted field extraction is better.
16. The final search `rg -n 'UCI|Daqing|signed|grouping keys|permitted repeated' deliveries/marketing-budget/leadership-budget/draft/findings.md deliveries/marketing-budget/leadership-budget/draft/methodology-note.md` matched “assigned” as a substring of “signed.” That was not residual technical language; use word boundaries.
17. review-rules add for the source rule warned that 2009/2011 also occurred in the draft. Here those are fixed source-coverage metadata explicitly requested by the user, not a draft metric. The conditional rule was appropriate.
18. No MCP write was refused, and no AWB CLI fallback was needed. All final checks and release verification passed.

## 4. Deviations, assumptions and course corrections

- I did not repeat an interview after the user accepted four recommended definitions. Routine implementation choices were disclosed in settings and records.
- I did not ask again for note or dataset approval after the user expressly requested the note and no accompanying tables.
- I followed the requested Q4-then-status order over the skill's default sequence.
- I used an optional asynchronous future-rule question, then completed authorized edits without waiting. No rule was saved until the user expressly approved all-package checks on the following turn.
- I kept the user's sixteen-word headline verbatim and recorded its explicit acceptance, instead of asking another length question or silently trimming it.
- I treated “Something like” as permission to adapt “France shows the broadest growth” to a qualified acquisition-test recommendation. Germany had more identified customers, and the analysis did not decompose customer-level growth breadth. I explained the change.
- I distinguished the user's identification of their own export from the actual acquisition route, retaining technical provenance internally. I attributed their explanation of genuine repeat order items rather than presenting it as independently verified.
- I interpreted a one-page note as about 500 words. Final note: 488 words.
- I combined Q2/Q3 to meet eight main slides while preserving the required title, Answer, methods and limitations. The user approved that layout.
- Chart category display mappings included recorded cancellation invoice/customer counts and country starting values/growth rates. This was a workaround for showing necessary context within the fixed chart role schema, not new analysis or hand-editing chart CSVs. Richer annotation roles would be cleaner.
- The initial non-product audit accidentally omitted POST. I caught it before presenting the table, added it, regenerated all 27 audited codes and checked completeness. This was my error.
- A TOML patch briefly landed before the prior validation line and would have duplicated a key. It was corrected and parsed before any affected run. No bad result was recorded.
- I repeated one review start after refreshing export, before launching the reviewer, to restore the required launch order.
- I created no package files until packaging was actually requested, did not rerun accepted analytical results for mere wording edits, and never changed a frozen release.

## 5. Disproportionate time/token use

- Package mechanics and reviews were the largest avoidable overhead relative to the business output. Across drafting, wording correction and final rule addition, multiple fresh reviewers and receipt/check cycles were required even when values were unchanged. The first review caught three real problems; subsequent scoped passes were clean.
- Reading overlapping skills, contracts, templates and command help consumed substantial context. Compaction summaries and targeted reads helped; broad rereads and batching long documents were still inefficient on my part.
- Fourteen result/evidence objects and their repeated questions/check citations were more machinery than five commercial questions suggest. Some decomposition was analytically useful, but status and package citations exposed too much of it.
- An approximately 20,000-token manifest and verbose read state/status output were expensive to inspect. Structured result summaries would save both tool calls and reasoning context.
- Repeated small records calls were reliable but verbose: adding/answering context questions, changing statuses, recording issues/next steps and promoting supporting checks. A batched atomic record update could preserve safeguards with fewer round trips.
- The one-minute workbook download and initial plotting font-cache build were ordinary runtime costs, not major usability failures.
- The private per-turn log also grew long. Some of its detail was required by the study; the final report separates genuine product friction from my own command/read choices.
- I do not have a reliable end-to-end wall-clock or token accounting total, so I am not inventing one.

## 6. What worked well

- MCP discovery exposed all necessary AWB capabilities. No unavailable tool or blocked mutation interrupted the workflow.
- Immutable ZIP/workbook retention, SHA-256 provenance, workbook publication and canonical views provided a strong foundation. The overlap discovery materially prevented overcounting without destroying source data.
- Reading XLSX with explicit serial timestamp conversion and checking morning/afternoon values avoided a plausible spreadsheet-import error.
- Clean scan/rescan and clean-record made user-approved corrections reviewable, while keeping plausible wholesale repeats and large transactions.
- The parented question ledger preserved five original business questions despite many diagnostics and decisions. The root-count principle was right; the status presentation needs to foreground it.
- User choices were honored: missing-ID revenue remained real revenue; no artificial customer identities; manual/bank uncertainty did not become a meeting blocker; sensitivity showed real monthly/rank effects.
- Reproducible run.py results, measured filter counts, required columns, unique keys, null checks and complete follow-up made the core answers inspectable. Final stale scans had no stale results or runtime mismatches.
- The Q4 refinement was particularly useful: the three-customer screen retained the ceramic jar, demonstrating that customer breadth does not eliminate a one-invoice value problem. The workflow preserved that contrary result instead of forcing the expected story.
- Keeping acquisition tests as recommendations, rather than claiming an optimal budget split or causal ROI, fit the available evidence.
- Headline preview-and-wait matched the user's desired review point and prevented premature full drafting.
- Export serialized existing saved results, selected rows and display precision without changing analysis. User-facing datasets stayed explicitly none.
- Fresh review caught unsupported verification wording, incomplete evidence citation and a specification wording issue; receipts and final checks made the delivered state explicit.
- Global rule recording happened only after yes. Adding rules correctly invalidated the prior review and triggered a focused review of the new rules.
- Release was excellent operationally: one command reran gates, froze 001, copied to external storage and returned both local/storage verification and the exact destination. No manual copying, extra permission or new analysis was needed.

## AWB MCP visibility and actual use

I could see these seven tools through ALL_TOOLS, and used all seven during the session:

- **mcp__awb__setup** — interpreter/helper installation and missing package formats.
- **mcp__awb__read** — state, complete questions, SQL/profile, stale, status, command help, review rules/receipts and read-only draft checks.
- **mcp__awb__records** — questions, answers, state findings/issues/next steps, cleaning records and confirmed review rules.
- **mcp__awb__data** — acquisition/publication/retention and cleaning/SQL operations as supported by the helper interface.
- **mcp__awb__run** — recorded analytical results and targeted Q4 reruns.
- **mcp__awb__package** — chart exports, provenance, review receipt start/record and final draft checking.
- **mcp__awb__release** — freeze and verified storage copy.

No AWB MCP tool was refused; there was no fallback to direct awb.py CLI commands. Shell/Python were used for project files, dependency installation, declared preparation and presentation code, and targeted file inspection. Helpers were treated as black boxes and shipped helpers/templates were not customized.

## Outcome

Release 001 is frozen locally and verified at:

`SIMS/retail-A/storage/releases/marketing-budget/leadership-budget/001/`

The main improvements I would prioritize are business-question-first status, audience source identity separate from download provenance, compact structured outputs, and a substantially shorter path through packaging and bounded editorial revisions.

