# Agent feedback — retail-A analytics workbench

This retrospective draws on feedback/agent-notes.md from setup through delivery of release 001. The requested analysis and release completed successfully. No remaining blocker prevented delivery. Severities below describe friction during this session, not hypothetical defects. Where I caused a problem, I distinguish it from a workbench limitation.

## 1. Ranked pain points and suggested fixes

1. **Major — Packaging/review instruction volume and repeated full review.** Files: awb-package/SKILL.md, references/package-contract.md, references/review.md, awb-release/SKILL.md, installed package-format templates. Preparing eight main slides required navigating a large contract, several templates, exact narrative/manifest relationships, persistent review rules, snapshots, multiple independent full reviews, export, check-draft, and final verification. Review improved the deliverable, but packaging administration consumed much more effort than the core calculations. Even after the corrected candidate had a clean full review and the user merely confirmed it, release required another fresh full review. **Fix:** provide one concise operational checklist with links to detailed rules; generate repetitive manifest/specification fields from structured authoring; retain content-hash-bound review receipts and reuse a clean review when the candidate and rules are unchanged, while always running final integrity checks.

2. **Major — Numeric checks sometimes police text shape rather than evidence.** Tools: records/state finding; package/check-draft. A date year, a bibliographic year, compact count/rate pairs, and source counts already present in validation evidence could fail recognition. I had to rewrite sound prose around the checker. **Fix:** distinguish dates, citations, ratios and analytic quantities; recognize declared check metrics and source metadata; report the exact text location, expected evidence source and permitted tolerance. Keep substantive number checking strict without requiring awkward prose.

3. **Major — SQL read errors conflate missing parameter bindings with read-only safety.** Tool: read/sql. Running the saved parameterized validation query without settings bindings returned a refusal whose advice was to run without read-only. The actual issue was unbound parameters, not an unsafe statement. **Fix:** expose explicit parameter bindings or an investigation/settings option, and diagnose missing bindings before plan safety checks. Never recommend write capability for a binding error.

4. **Major — Mixed-intent status requests have no clear durable steering path.** Files: awb-status/SKILL.md and project AGENTS.md. The user supplied approved slide changes and then requested status. Status explicitly required a read-only turn, so I left the edits in conversation rather than recording them. My opening commentary had already promised to save them. **Fix:** explicitly allow a separate authorized record-maintenance stage alongside read-only status, or provide a durable pending-steering inbox. Status should distinguish “approved changes awaiting application” from the prior recorded next step.

5. **Major — Setup/scope/clean boundaries require interpretation for routine technical decisions.** Files: awb-init/SKILL.md, awb-scope/SKILL.md, awb-clean/SKILL.md. An investigation could not be created before the initial interview, so I stored the user's substantial intake temporarily in README. The clean workflow appeared to require a user choice over repeated rows even after exact cross-sheet overlap was proved. **Fix:** support a provisional intake/brief before unresolved business definitions are settled; distinguish consequential business decisions from technically demonstrated duplicate imports. Offer audited default handling for exact cross-acquisition overlap while retaining originals. The actual four scope questions were useful and answered quickly.

6. **Minor — Slide count rules exceed the nominal request.** File: awb-package/references/package-contract.md and deck rules. Title, answer, five findings, methods and caveats produce nine content slides; an assembly divider can add another physical slide. I explicitly proposed eight main slides plus one appendix, which the user accepted. **Fix:** show main/appendix/divider counts before drafting and allow methods/caveats to be combined or moved to the methodology note where appropriate.

7. **Minor — Initial interpreter/dependency setup needs a safer default.** Files/tools: awb-init/SKILL.md, setup, README Project interpreter. Setup correctly reported missing DuckDB but initially targeted a non-project interpreter. I created a local venv and set the project interpreter manually. **Fix:** offer an explicit project-venv bootstrap option and show the actual executable and installation destination before installing. My subsequent venv-symlink mistake was my own error, detailed below.

8. **Minor — Source-reference syntax documentation is disproportionate.** File: foundation/sources.md template and foundation/references/README.md. The strict link-parsing instructions were unusually long for entering a normal source reference. **Fix:** lead with one supported example; move parser internals to a reference; consider structured reference entries with existence/hash validation rather than requiring agents to reason about Markdown parsing.

9. **Minor — Expected preview incompleteness looks like package uncertainty.** Tool: read/status; package checkpoint model. At the user-requested headline-only checkpoint, the missing full manifest was expected, but status had to explain it manually. **Fix:** record an explicit headline-preview checkpoint so status can say “awaiting headline approval” without presenting ordinary partial-draft files as ambiguous gaps.

10. **Minor — Some helper output is too large or easy to misread.** Tools: package/export, read/status and metadata output. Repeated provenance/narrative details and long absolute paths increase reading cost. A result-only export returned an empty charts list while retaining the existing five chart files, which needs contextual interpretation. **Fix:** default to a compact summary plus receipt path; distinguish added, retained and removed chart counts; make detailed output opt-in.

11. **Minor — Storyline expectations need a preview/explanation.** Tool: package/check-draft. The first full check requested concentration and products at positions different from the user's approved order. The supported presentation_order override solved it. **Fix:** provide a planning command showing proposed order, the question path/priority behind it, and how to record an approved alternative. I did not inspect the helper source, so I cannot establish whether its initial order was erroneous.

12. **Minor — Lifecycle metadata can remain stale after success.** Files: README.md and scaffolded state sections. README still said no release was authorized after authorization and needed manual reconciliation. Some template guidance also survived in state records. **Fix:** distinguish standing authorization policy from current lifecycle status and update lifecycle fields through the helper; remove instructional placeholder text when scaffolding becomes live records.

13. **Minor — General audience checks did not prevent several user-facing corrections.** Files: package templates/review rules. I initially used generic “online retailer” framing, public-source chart labels, technical control-group language and imperative method bullets. The user corrected these, and persistent rules then covered them. This is partly my drafting responsibility. **Fix:** scope the company's own description and intended source label; check declarative methods, plain campaign language and prominent metric definitions before the first full draft.

## 2. Contradictory, ambiguous, long or missing instructions

- **Autonomy versus initial interview:** developer instructions favored continuing authorized work; init/scope required settling material choices before creating an investigation. I resolved this by doing setup independently, asking four bounded questions with recommendations, and keeping intake in README. A provisional intake artifact would remove the awkward choice.
- **Read-only status versus combined user edits:** described above. This was a real same-message workflow tension, not permission uncertainty.
- **Default no delegation versus required independent reviewers:** package/release skills explicitly required fresh review agents, so delegation was authorized by the applicable exception. That hierarchy was workable, but should appear clearly in the review checklist.
- **Read-once guidance versus repeated release gates:** I reread some previously loaded skill/reference files for confidence before release. That was my inefficiency; a short remembered checklist and review receipt would reduce it.
- **Approximately eight slides versus mandatory distinct sections:** resolved transparently as eight main slides plus an appendix rather than silently dropping required content.
- **No audience datasets versus necessary chart inputs:** this distinction was clear enough in the contract and worked well. Five chart CSVs were retained as build inputs; no audience datasets were selected.
- **What “slides” means:** the package skill produced a slide outline, chart inputs, methodology assets and PowerPoint assembly instructions, not a finished PPTX. The handoff made this explicit. A concise deliverable-format statement at intake would prevent surprises in less informed sessions.
- **Reference and review documentation length:** multiple files repeat requirements. Prefer a single source of truth, a short task checklist, and targeted deep references.
- **Missing sandbox guidance:** shell heredocs and macOS temporary cache locations were not usable here. Examples should avoid assuming a writable system temporary directory, or setup should establish a writable TMPDIR.

## 3. Failed or unexpected commands/tools

The project path in examples below is:

SIMS/retail-A/project

Where the notes did not retain a complete command body, I say so instead of inventing it.

### Environment and agent execution

- Initial file search, recorded in abbreviated form as `pwd && rg --files -g AGENTS.md ... .`, exited 1 because the project was empty. This was ordinary no-match behavior, not a workbench failure.
- Exact command: `ls -la && git status --short && git rev-parse --show-toplevel`.
  It returned `fatal: not a git repository (or any of the parent directories): .git` on the empty root, plus:
  `git: error: couldn't create cache file '/var/folders/cr/64mtlg6x6j3_sjjtj19wyfzh0000gn/T/xcrun_db-JT9kP2TH' (errno=Operation not permitted)`.
  Later git init/status had analogous cache warnings but succeeded. No repository damage occurred.
- An ancestor-instruction scan using `python3 - <<'PY'` failed before execution with `zsh:1: can't create temp file for here document: operation not permitted`. The complete scan body was not preserved in agent-notes. A review agent later hit the same heredoc limitation and reported `zsh:1: cannot create temp file for here document: operation not permitted`; its full body was also not supplied. Both were retried with Python -c.
- My pip subprocess selected `str(Path(".venv/bin/python3").resolve().parent/"python3")`, resolving the venv symlink to the base interpreter. Pip printed `Defaulting to user installation because normal site-packages is not writeable` and installed DuckDB in user site. I removed it with `python3 -m pip uninstall -y duckdb`, installed through the non-resolved absolute venv executable, and verified the import path inside .venv. This was my error, not a helper defect.
- A functions.exec script failed before any nested tool ran: `SyntaxError: Unexpected identifier 'state'`. Unescaped backticks inside my JavaScript template string caused it. I corrected quoting and reran. The entire script is not retained in the notes.

### Workbench tools

- Read/sql call:
  `command="sql", query="investigations/marketing-investment/queries/validation.sql"`, with the absolute project supplied.
  Error:
  `sql: read-only: refused a statement whose plan cannot be checked (Invalid Input Error: Values were not provided for the following prepared statement parameters: cohort_end, cohort_start, end, home_country, minimum_product_sales, source_sheet_split, start); run it without --read-only`.
  I generated a saved exploration query with explicit settings-derived literals and retained the parameterized query for the producer. I did not remove read-only protection.
- Records/state finding, nonproducts promotion:
  `warning: nonproducts: "reconciliation" asserts a reconciliation or a completed check that no passing check in its evidence records; state the check, with its tolerance, in the detail of a passing values or metrics judgment in [results.nonproducts.validation] and rerun, or reword`.
  This was a useful guard. I reworded the categorical finding; the actual reconciliation remained with the validated revenue result.
- Records/state finding, seasonality-comparison:
  `warning: seasonality-comparison: 2011 is not a value its table, profile, checks, or settings record; check the number or reword`.
  The number was a date context. I changed summary prose to earlier/later periods and retained actual dates in result tables.
- Initial package/export wrote chart inputs/manifest but exited 1 because each of the five chart files had `no specification in findings`. I had exported before completing chart specifications to obtain exact methodology metadata. That sequencing error was mine. Writing the complete specifications and rerunning succeeded. A metadata-only/dry-run facility would avoid the temptation.
- First full package/check-draft returned storyline errors: concentration at finding position 2 versus expected 3, products at 4 versus expected 5. I used the documented presentation_order field for the user's approved order, leaving question priority/parents unchanged.
- The same check flagged numeric text including `2012`, `1,067,371`, `1,044,848`, and compact pairs such as `368/53.5%`. I allowed only the bibliographic phrase “Chen, D. (2012)”, expanded count/rate prose, and omitted unnecessary raw counts from narrative while preserving evidence. No analytic numbers were exempted.
- Exact reviewer CLI command:
  `.venv/bin/python3 src/awb.py review-rules check marketing-investment leadership-budget --project SIMS/retail-A/project`
  exited 2:
  `awb.py review-rules: error: unrecognized arguments: --project ...`.
  The reviewer retried through read/review-rules with the structured project argument successfully. This was CLI/MCP argument confusion, not a failed review.
- Publish warned that conversion SQL was uncommitted and conversion_commit did not contain it; checksums were retained in publication notes. This was expected under the user's on-request commit policy, not an unresolved execution error.
- One help read accidentally omitted the required project argument and resolved the correct cwd. I supplied absolute project paths thereafter.

No write MCP tool was refused. No approval failure or CLI fallback for an unavailable write tool occurred. Final package checks, release creation, local verification and stored-copy comparison all passed.

## 4. Deviations and judgment calls

- Temporarily preserved rich intake in README before creating the investigation because scope forbade creation before the first interview.
- Did not invoke a global cleaning pass for the proved cross-sheet December 2010 overlap. Canonical raw data retained all 1,067,371 lines. Investigation queries used the first sheet before December 2010 and the second thereafter, documented the exact 22,523 overlapping lines, and preserved within-sheet repeats. This was a deliberate local scope choice, not silent deduplication.
- Used an additive derived cancellation value for a C-marked manual line with positive quantity; source quantities were preserved.
- Recommended inclusive signed export transaction value for revenue with merchandise sensitivity, rather than claiming accounting-certified recognized sales. The user accepted it. Excluded non-product codes from product rankings.
- Exported before full chart specifications once, causing the failure above; then followed normal write/export/check sequencing.
- Kept same-message slide amendments pending during the explicitly read-only status turn rather than pretending they were saved.
- Adjusted narrative formatting for number recognition, with only citation metadata allowed as an exception. Computed quantities were unchanged.
- Corrected my earlier brief wording that implied concentration required a purchase, while the accepted implementation used all identified customers, including cancellation-only IDs. This was documentation repair, not a change to the figures.
- During a full review, added a rounding clarification and explicitly asked the reviewer to reread the changed passages before its final verdict; updated the review snapshot. No edits followed its clean verdict.
- Spawned independent reviewers because the skills explicitly required them. I did not delegate ordinary analysis.
- Did not commit without user authorization, release before the requested changed-slide checkpoint, send external messages, or modify a frozen release.
- The pip interpreter and JavaScript quoting mistakes were avoidable execution errors and were corrected immediately.

## 5. Where time and tokens went disproportionately

I did not collect a reliable token or elapsed-time profile, so this is qualitative.

Packaging dominated: reading overlapping contracts/templates, authoring synchronized narratives and manifest specifications, number-check rewrites, saving review snapshots, multiple fresh full reviews, and repeated final gates. The core five business calculations were comparatively direct once source semantics and overlap were settled.

Verbose helper receipts and long absolute paths added repeated context. Reopening already read instructions also cost unnecessary tokens. A compact checklist, small default receipts, structured narrative/manifest generation, and review reuse for byte-identical candidates would reduce overhead substantially without weakening integrity.

Some additional analytical work was worthwhile rather than overhead: verifying the fully reversed jar order, separating Jan–Nov from December cohort ranges, calculating Australia's largest account contribution to growth, and checking all 90-day observation deadlines. These directly improved leadership decisions.

The initial headline-only preview followed the requested checkpoint, but the user then needed full tables in chat before approving. A short evidence capsule alongside proposed headlines would have reduced that extra round while still honoring preview-and-wait.

## 6. What worked well

- The initial four recommended scope choices settled consequential definitions quickly. Audience, deadline, paths, no-dataset preference and preview/release permissions persisted across turns without repeated questions.
- The workbench distinguished five original questions from child checks instead of inflating progress counts.
- Landing retained the original ZIP and workbook together with provenance and verified hashes. Explicit Excel date conversion preserved times of day, and source checks caught the overlapping sheet period.
- Saved settings, producer queries, validated results and findings were clearly separated. Exploratory output was not silently promoted to a supported conclusion.
- The analysis challenged the retention hypothesis appropriately: repeat purchasing described revenue concentration but could not establish campaign returns without spend/margin/control evidence.
- Sensitivities were concrete: removing both sides of the exceptional jar reversal preserved net revenue; the jar then fell below the £10k sales threshold. Australia’s dependency was checked as both share of revenue and contribution to growth rather than conflated.
- User corrections became reusable review rules. Reviewers caught real weaknesses in completed-check citations and tolerance wording, not just cosmetic preferences.
- Narrative-only corrections reused accepted analytical evidence and did not trigger gratuitous recomputation.
- The short audience methods note, internal methodology, slide outline, chart inputs and START-HERE handoff gave distinct practical entry points.
- Final release gates returned a frozen numbered package, exact external storage path, provenance caveats, and independent local/storage integrity comparisons. Release 001 copied successfully; no discrepancies were reported.
- Remaining caveats were preserved rather than hidden: absent campaign cost/margin evidence, first-observed rather than lifetime acquisition, unidentified revenue, two seasonal cycles, small cohorts/account concentration, exceptional cancellations, inclusive transaction-value accounting, and no packaging commit.

## 7. awb MCP visibility and use

All seven workbench MCP tools were visible and used:

- **mcp__awb__setup:** install/check helpers and package formats.
- **mcp__awb__read:** state, questions, help, SQL/profile, stale/status, draft verification; review agents also used review-rules.
- **mcp__awb__records:** question answers/children, state findings/issues/next steps and persistent review rules.
- **mcp__awb__data:** extension/SQL setup, publication and durable retention. The acquisition itself used a saved fetch callable through the landing machinery.
- **mcp__awb__run:** investigation producers and validated results.
- **mcp__awb__package:** chart/manifest export and package checks, including result-only refreshes retaining chart inputs.
- **mcp__awb__release:** release 001 freeze and verified copy to configured release storage.

The CLI was not needed as a fallback for unavailable or refused MCP writes. One reviewer used an incorrect CLI --project flag, then returned to the functioning structured MCP read tool. Overall the MCP interface worked reliably and made project targeting, writes and release verification reviewable.
