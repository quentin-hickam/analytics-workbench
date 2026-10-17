# Agent feedback — taxi-B simulation (awb-init → scope → analysis → package → release)

Outcome: workbench set up, two TLC monthly files + zone lookup landed and published, 11 results run and promoted, an 8-slide + 3-appendix package with a one-page methods note drafted, reviewed (4 review passes total), and released as 001 to the recorded storage folder. Seven user turns.

## awb MCP tools seen and used

Seen: `mcp__awb__setup`, `read`, `records`, `data`, `run`, `package`, `release` (all deferred; loaded via ToolSearch).
Used: all seven. `setup` (install), `data` (land, publish), `read` (sql, help, status, check-draft verify, review-receipt), `records` (questions add/answer, state switch/finding/issues/next, review-rules add), `run` (run.py), `package` (export, check-draft, review-receipt start/record), `release` (release). CLI fallback used a few times (see deviations).

## 1. Pain points, ranked

1. **Review strictness vs. available evidence forms** — `awb-package/references/review.md` step 3 + no `awb-clean` scans. *Major.* Any sentence saying "every", "exactly", "identical", or describing how a source builds a field needs a result ID, evidence path, publication check, or `foundation/scans/` path. Facts established by exploration queries or DQ rows citing exploration (not scans) are rejected. This produced 21 narrative problems on the first review, knock-on problems on the second, and a third cycle where I had to rerun a result just to record a flat-fare observation as a `metrics` judgment. Fix: let `methodology.md` cite a saved exploration query (with checksum) as supporting evidence for context claims, or provide a lightweight `awb.py note-check` that records a one-off query + output as a citable check without a full result.
2. **Status output truncated by the MCP tool** — `mcp__awb__read command=status`. *Major.* Response cut "[... 5233 characters cut; full output in /tmp/awb-mcp-…txt]"; the overflow file was outside my allowed paths, so I lost the questions/roots section and had to reconstruct it from `questions list --all`. Fix: a `--summary` mode or paginate sections (`section=questions`), and keep findings text out of the default payload (it duplicates state.md).
3. **Rerun demotes supported finding when only a validation `detail` string changes** — `run.py`/`provenance.record_finding`. *Minor–major.* Editing a metrics judgment's text (no table change) turned a user-approved supported finding back to provisional, requiring re-promotion and a new history entry. Fix: treat judgment-detail-only changes as "kept" or prompt-free refresh when the table is identical.
4. **`joins` check unusable for aggregate results** — `src/exploration/validate.py` / settings comments. *Minor.* Every one of 11 results showed "not assessed: joins" and needed the same caveat note; the joins spec compares result length to left rows, meaningless for GROUP BY outputs. Fix: accept `joins = { outcome = "not-applicable", detail = "..." }` as a judgment, documented in settings.toml comments.
5. **No scaffold helper for a new investigation** — `awb-scope` step 3 "New". *Minor.* Manual `cp` of templates + hand-edit of brief/state. Fix: `awb.py investigation new <slug>` that copies templates, sets dates, and switches.
6. **One question per `questions add` call** — `records questions add`. *Minor.* 11 sequential MCP calls during scoping. Fix: accept a JSON list on stdin.
7. **`@where` takes a single column** — `export --chart`. *Minor.* Couldn't select month='both months' AND vendor∈{…}; and a result with a NULL "all hours" row needed a label column + rerun to be chartable. Fix: allow multiple `@where` clauses joined by `&`, and an `@where-not`.
8. **review-rules add warning about numbers is noisy** — `records review-rules add`. *Minor.* Rule text "payment code 0" triggered "the rule names 0, which findings.md:43 also states", implying the rule encodes a draft figure. Fix: ignore numbers inside quoted identifiers / code labels, or only warn on numbers with units/percent.
9. **Release `open_caveats` duplicates the slide headline as a caveat line** — `release` output. *Minor/cosmetic.*

## 2. Contradictory, ambiguous, too long, or missing instructions

- **Pre-landing inspection**: `awb-scope` says "look facts up yourself… in source systems", while `workbench-guides/data.md` says "inspect records only from landed copies". In turn 1 I peeked at inbox Parquet before landing to ground the interview. Clarify whether a read-only peek at user-supplied files before landing is allowed.
- **Answerer for documentation lookups**: `questions add --answerer {user,stakeholder,data}` has no fit for "agent reads the vendor's data dictionary". I used `stakeholder`. Suggest `--answerer reference` or `documentation`.
- **`question` must be in the user's words** (analysis.md): for sub-questions the user never phrased (sensitivity checks, payment-code check) I used a fragment of their sentence or the ledger text. Guidance on what to do when no user wording exists would help.
- **Preview-and-wait before export**: the contract puts `.preview/headlines.md` inside the draft folder that `export` creates; preview-and-wait wants headlines before the draft. I mkdir'd the path by hand. State explicitly that the preview may be written before the first export.
- **Second-review stop rule** (`review.md` After the review): stopping after a second failing review in one request and taking trivial wording issues to the user felt heavy; it's correct but cost a user round-trip for a two-word fix. Consider allowing the agent to fix narrative problems that only narrow a claim (remove an unsupported word) without escalation.
- **Asking about review rules**: awb-package says ask when a *draft* correction could repeat; the user's correction ("never call code 0 Flex Fare") came before the draft existed. Unclear whether to ask then. I asked after drafting.
- **Length**: package-contract.md (~2,900 words) and helpers.md (~7,000 words) are long; I grep'd helpers.md instead of reading it. A one-screen "cheat sheet" of export/check-draft/review commands would cut tokens.
- **awb-status ordering**: it's "read-only", but I updated state (dropped stale next steps) before running it so it reported accurately. A note that records should be brought current first would help.

## 3. Commands/tools that failed or behaved unexpectedly

- `cat a; echo =====; cat b` (zsh) → `(eval):1: ==== not found` — zsh `=word` expansion; my error, but common in the host shell.
- `Q="python3 src/awb.py questions add"; $Q "..."` (zsh) → `(eval):2: no such file or directory: python3 src/awb.py questions add` — zsh doesn't word-split.
- `mcp__awb__read command=sql` with alias `rows` → `Parser Error: syntax error at or near "rows"` (DuckDB reserved word; mine).
- `mcp__awb__read command=status` → output truncated, overflow file at `/tmp/awb-mcp-9t4d6u08/…txt` not readable within sim bounds.
- `mcp__awb__package export` first call → exit 1 with 34 errors for missing display names/rounding (expected behaviour; the stubs were helpful).
- `mcp__awb__read check-draft` before first write → `errors: ["manifest: manifest.json records no inventory list; run check-draft without --verify-only"]` (expected, but the read-tool path can't succeed until the write path runs once).
- My own Python `str.replace` on `foundation/sources.md` silently no-op'd because `land` had already flipped Status `candidate`→`acquired`; the source kept "reference: not yet retained" until the reviewer caught it two turns later. `awb-status` didn't flag it because the row's basis said "from landed records". Suggest status flag any source whose Notes say `reference: not yet retained` once a file exists under `foundation/references/<source-id>/`.

## 4. Deviations from instructions and why

- Peeked at inbox files before landing (turn 1) to give grounded recommendations in the first interview round.
- Used CLI instead of MCP for: `install_helpers.py --package-formats` (didn't notice `setup.package_formats` until after), `questions answer Q-003 --result …`, `questions list --all`. Same effect.
- Ran awb-status after updating state records rather than strictly read-only first.
- Created `.preview/headlines.md` directory before `export` existed.
- Didn't run `awb-clean` (user never asked); this is why DQ rows had no scans, which fed the review friction above.
- First result runs happened before committing the code (Commits was "on request" then); after switching to "as I go" I committed and reran everything so evidence names a commit.

## 5. Where time/tokens went disproportionately

- Draft review cycles (3 reviewer subagents + repairs): roughly a third of turn 5–6 effort, mostly on evidence-citation wording, not on substantive errors (the one real error caught was July's 6 pm vs 7 pm tip-peak tie — valuable).
- Writing settings.toml validation tables for 11 results (repetitive scope/metrics/values judgments, identical joins caveat ×11).
- Reading long reference docs (package-contract, findings/methodology templates, deck-rules, manifest template) in turn 5.
- Status payload size.

## 6. What worked well

- `setup` tool: one call, clear JSON, interpreter recorded correctly.
- `land` + retention: copy, checksums, Acquisitions row and storage copy in one step; `publish` with declared checks in `datasets.toml` was smooth and the multi-part guidance (lineage, overlap check) was spot on.
- `run.py` + producer/`reconcile()` pattern and `answers = [...]` auto-marking the ledger.
- `state finding` warnings on numbers not in the result table caught derived numbers I'd invented.
- `export` stubs (`display_stub`, `round_stub`, `methodology_lines`) made chart serialization quick; `check-draft` numbers/claims checks were precise (caught a causal "effect of").
- The read-only reviewer caught a genuine factual slip (July peak hour tie) and an unsupported "flat fare" claim.
- Review rules: user's "never call code 0 Flex Fare" became an enforceable project rule in one call and immediately caught a stray line.
- `release`: gate, freeze, storage copy and verification in one call; caveats summarized for the report.
