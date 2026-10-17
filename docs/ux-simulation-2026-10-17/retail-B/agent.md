# Agent feedback — retail-B (UCI Online Retail II, leadership marketing deck)

Outcome: workbench initialised, data landed/retained/published/cleaned, 8 run.py results (all supported), deck + one-page methods note + 4 datasets drafted, three review passes, release 001 frozen and copied to storage. Seven user turns.

## awb MCP tools seen and used

Seen: `setup`, `read`, `records`, `data`, `run`, `package`, `release`. Used all of them:
- `setup` (install helpers, then `package_formats`), 
- `read` (`status`, `help`, `stale`, `check-draft` verify-only),
- `records` (`clean-record`; questions/state I mostly ran via CLI in batches),
- `data` (`retain`, `publish`, `clean-scan`, `sql` for `INSTALL excel` via CLI),
- `run`, `package` (`export`, `review-receipt`, `check-draft`), `release` (`release`).
I used the CLI for multi-command batches (questions add ×6, state finding ×7) because a single shell call was cheaper than many tool calls; no MCP tool refused.

## 1. Pain points, ranked

1. **Review "unchanged since prior review → take to user" rule** — `awb-package/references/review.md` (After the review). *Major.* A one-word internal citation error in methodology.md forced a whole extra user round trip at the moment the user asked for "confirm final checks pass". Fix: let the agent repair problems in internal-only files (methodology.md) that change no claim/number, reporting them; reserve the escalation for audience-facing text or rule conflicts. (User then made this a project convention.)
2. **Imperative-sentence readability rule vs. a requested recommendation** — review.md step 3 readability + findings-template Answer slide. *Major.* The user explicitly asked for a recommendation on the Answer slide; the reviewer flagged "Protect key accounts…" as imperative. I had to write awkward gerunds ("Recommendation: protecting key accounts, testing…"). Fix: allow a clearly labelled recommendation bullet/headline on the Answer slide, or exempt sentences starting "Recommendation:".
3. **Floating-point reconciliation vs. "exactly"** — run.py/validate + review.md tolerance rule. *Major.* `identified + no-ID − total` = −4.4e-06 from summing doubles; review correctly rejected "equals the total exactly", but the only way to record a tolerance is in brief or `[parameters]` before the result, which nobody would think of up front. Fix: document a DECIMAL-sum pattern for money in analysis.md, or a first-class `tolerance` key in the validation spec that counts as recorded.
4. **`joins` always "not assessed"** — settings.toml template / validate. *Minor-major (noise).* Every result without a join carries "not assessed: joins" which must be caveated, and awb-status then lists every finding under caveats. Fix: allow `joins = { outcome = "not-applicable", detail = ... }` like scope/metrics/values.
5. **Headline edit needs identical methodology heading; check-draft reports it as four rows** (`headings`, `claims`, `storyline`, `unlinked_findings`). *Minor.* Fix: collapse into one "methodology section missing for heading X" row.
6. **Preview step can't word-count** — awb-package headline checkpoint. *Minor.* A user-approved 16-word headline surfaced only at check-draft, costing another approval. Fix: a `check-draft --preview` or a word-count helper on `.preview/headlines.md`.
7. **`.preview/headlines.md` before the draft folder exists** — awb-package step 3 vs step 4. *Minor.* Preview is written "in the draft folder" which `export` creates later; I mkdir'd it. Fix: say "create the folder" or have export/preview helper create it.
8. **awb-clean issue granularity** — `scan_dataset.py` duplicate-rows S1 mixes cross-sheet copies and within-sheet repeats. *Minor.* One part corrected, other part pending user → unclear status. Fix: split cross-part and within-part duplicates into separate issue keys.
9. **awb-clean self-decide on cross-sheet duplicates** — *Minor (judgment).* The skill let me remove overlapping-period copies myself; the user approved afterwards but said they expect to be asked when meaning is uncertain. Fix: require source documentation explicitly stating overlap, otherwise ask.
10. **review-rules scope** — `review-rules add`. *Minor.* Only "every package" or one package; user asked "this investigation". Fix: `--investigation` scope.
11. **`precision_warnings` false positive** — `export`. *Minor.* 0.1875 (=3/16) flagged as query-rounded on every export; can't be silenced. Fix: allow confirming a column, as `[confirmed]` does for labels.
12. **Commit/rerun/re-export dance** — `producing_uncommitted_changes`. *Minor.* With "commit as I go", results run before their code was committed need commit → rerun → re-export `--result`. Fix: mention the order in analysis.md ("commit, then run") or let export accept matching checksums.
13. **check-draft `passed: true` while review `failed`** — *Minor, misleading.* The JSON flag doesn't fold in review status; release does gate on it. Fix: add `review_ok` or make `passed` include it, or document.

## 2. Instructions contradictory, ambiguous, too long, or missing

- awb-init step 1.3: "any directory above" for CLAUDE.md — unbounded; I checked only within allowed folders. Say "up to the repo root / home".
- awb-scope "look facts up yourself" vs "Scoping writes investigation records only; data work follows on request" — I used prior knowledge of the dataset rather than landing during scoping.
- data.md fetch-script path vs landing.md archive section (CLI `land` with archive + extracted folder): combining "fetched" and "archive" needs inference (extract inside the fetch callable). One sentence would fix it.
- data.md "commit conversion SQL before publish" under default `Commits: on request` → publication permanently records `uncommitted`.
- AGENTS.md end-of-turn ledger line: ambiguous on the init turn before a ledger exists.
- Where user working preferences belong (e.g., "don't ask about citation fixes", wording preferences before a draft exists) — no named home; I used brief Audience and a new AGENTS.md "Project conventions" section.
- "About 8 slides": whether the title counts is not stated in the brief template (contract counts it).
- awb-package step 1 "ask which datasets" vs preview-and-wait — fine, but order of asking datasets/methods note vs headlines could be stated.
- The package contract + findings template + review.md are long; the rules that actually bit (number tracing, check citations, imperative, glossary-term first use) could be a short checklist at the top of findings-template.

## 3. Commands/tools that failed or surprised (exact)

- `Q=".venv/bin/python src/awb.py questions add"; $Q "..."` → `(eval):2: no such file or directory: .venv/bin/python src/awb.py questions add` (zsh, no word splitting; my error).
- `awb.py sql --read-only "... round(sum(quantity*price),2) value FROM ..."` → `Parser Error: syntax error at or near "value"`; same for alias `share`.
- `awb.py sql --read-only "... GROUP BY ALL QUALIFY row_number() ..."` → `Binder Error: Combining QUALIFY with GROUP BY ALL is not supported yet`.
- `ls ../.. | head -0` → `head: illegal line count -- 0` (mine).
- `state next --drop 1 --drop 1` — both drops resolve to the same item before change; second effectively ignored (stderr suppressed in my pipe). Expected behaviour per help, but surprising.
- `export` repeatedly: `precision_warnings` for `largest_line_share_of_cancellations` example 0.1875 (false positive).
- `retain` reported `upstream_check: not possible ... no ETag or Last-Modified` — correct and useful.

## 4. Deviations and why

- Recorded Q-006 (small-base threshold) and Q-007 (within-sheet duplicates) as open user decisions rather than blocking scope, because the user asked to proceed with download and checks.
- Removed the cross-sheet overlap myself (skill permitted); user later approved and asked to be consulted in future — recorded in DQ-001 and AGENTS.md conventions.
- Added `largest_customer_share_of_change` and cohort coverage columns after seeing results (new descriptive measures, not thresholds) — disclosed to the user.
- Promoted `foundation/views/02_online_retail_lines.sql` (line classification) to the foundation directly instead of starting in investigation views, because the glossary defines non-product codes as shared meaning.
- Created `.preview/` folder by hand before export.
- Copied foundation templates (catalog, glossary) by hand; added AGENTS.md "Project conventions" section (not in template) to hold the user's standing preferences.
- Used CLI rather than MCP for batched ledger/state writes.

## 5. Where time/tokens went disproportionately

- awb-package cycle: export output is very large (methodology_lines + questions repeated every call, ~5k tokens each) and I ran export 5 times; check-draft output also repeats ledger_order every call. A `--quiet`/summary mode would help a lot.
- Three review rounds plus receipts (record requires pasting the full report back via stdin).
- Repeated "changed on disk" notifications re-showing whole files (harness, not workbench).
- Reading long contract/template/review docs once was fine; the cost was in iterations driven by rules discovered late (number tracing, exact-match wording, imperative, headline length).

## 6. What worked well

- `setup` with explicit project `.venv` interpreter: first-time success, clear JSON.
- `land()` fetch callable + `retain` copy to storage + provenance; `publish` with declared checks (20 passed) and printed `view_sql`/`catalog_row`.
- landing.md's Excel serial-date guidance was exactly right.
- `clean-scan` / `--rescan` deltas and `clean-record` writing quality.md + catalog in one call.
- run.py/settings/producers/`reconcile()` design: results reproducible, `answers` linking the ledger, evidence with commits.
- `state finding --text` warns on numbers not in any table — caught a derived figure early.
- check-draft's number tracing and allowed_numbers with reasons; the independent read-only reviewer caught genuinely important overstatements (unsupported "exactly", superlatives, claims resting only on exploration).
- `release`: one call froze, verified, copied to storage, and returned open caveats ready to report.
- awb-status gave an accurate, compact picture (including "state out of date").
