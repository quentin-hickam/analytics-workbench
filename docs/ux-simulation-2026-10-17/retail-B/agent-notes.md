# Agent friction log — retail-B

## Turn 1 — awb-init + awb-scope first interview round

Files used: awb-init/SKILL.md; awb-init assets (README.md, AGENTS.md, .gitignore templates); awb-scope/SKILL.md. MCP: awb setup.

What worked well
- `mcp__awb__setup` with explicit `interpreter` = project .venv worked first time; clear JSON (files installed, interpreter written as relative `.venv/bin/python`, requirements.txt written, packages ok).
- Step 3.3 instruction to create `.venv` and install duckdb+pandas first was unambiguous.
- Rule "when the hand-off shares a turn with setup, run awb-scope's first interview round before it creates the investigation" is clear: no investigation folder this turn.

Confusing / guesses
- README storage lines: template allows absolute, `~`, or `./`/`../` paths. I first wrote `../storage/...` relative, then switched to absolute because the user gave absolute paths. No guidance on which to prefer; absolute is less portable but unambiguous.
- awb-init step 1.3 asks to check "any directory above" the target for CLAUDE.md. The sim boundary forbids reading outside the sim folder, so I only checked the project and its sim parent. Instruction could say "up to the repository root / home".
- The user's message opened with a stray line ("I'll read BRIEF.md and README.md, then follow the simulation's response format.") that looks like leaked harness text; ignored it.
- AGENTS.md's "turn that changed workbench records ends with one plain line" about questions/ledger roots — unclear whether it applies when init wrote files but the ledger does not exist yet. I added a line anyway saying questions are not yet recorded.
- awb-scope "Pace by dependency": at most four decisions per round. With five user questions each needing a definition, four was tight; deferred top-10% period basis, country-growth measure, and slide/approval workflow to round 2.
- awb-init asks for the business question "in one line" — user gave it richly; fine.
- Scope skill says "look facts up yourself" but also "Scoping writes investigation records only; data work follows on request" — so I relied on prior knowledge of the UCI dataset structure (C-prefixed invoices, non-product stock codes, Dec 2010 overlap between the two sheets) rather than downloading. Slight tension.

Commands
- `ls ../.. | head -0` → "head: illegal line count -- 0" (my mistake, harmless).

## Turn 2 — awb-scope records, data landing (data.md, landing.md), awb-clean

Files used: awb-scope/SKILL.md (again, already loaded), awb-init investigation templates, workbench-guides/data.md, awb-init/references/landing.md, awb-clean/SKILL.md, awb-clean/references/correction-views.md; foundation templates (sources, catalog, quality, glossary, datasets.toml).

What worked well
- `land()` with a fetch callable that downloads the zip and extracts the xlsx into `extracted/` worked first time; `retain` copied to the storage folder and wrote the Acquisitions row; it told me upstream checking is impossible (no ETag).
- `publish` with declared checks: 20 checks passed first try; view_sql and catalog_row printed are handy.
- landing.md's Excel serial date guidance (to_milliseconds/round) was exactly right; spot-check matched 2009-12-01 07:45.
- clean-scan + --rescan delta output was clear (34,335 -> 11,812 duplicate rows; whitespace resolved; rows 1,067,371 -> 1,044,848 = exactly the 22,523 overlap).
- clean-record via MCP filled DQ IDs, quality.md, catalog cells in one call.

Friction / confusing
- zsh: `Q=".venv/bin/python src/awb.py questions add"; $Q ...` fails (no word splitting) -> "(eval):2: no such file or directory". My error, but the CLI fallback lines in skills assume bash-like use; used a shell function.
- `awb.py sql` read-only: alias `val`/`value` — `value` as column alias gave "Parser Error: syntax error at or near "value"". DuckDB keyword; my mistake.
- data.md says fetched sources use a fetch script + land(), but landing.md's archive section shows the `land` CLI with archive + extracted folder. Combining "fetched" + "archive" required inferring that the fetch callable should do the extraction itself. Worked, but not spelled out.
- data.md: "commit conversion SQL first so conversion_commit holds it" vs Commits: on request — publish then warned "conversion SQL is uncommitted". Fine but the publication is permanently "uncommitted" unless re-published. Slight tension in the default mode.
- awb-clean: the scan's duplicate-rows count mixes cross-sheet and within-sheet repeats in one issue (S1). I had to record S1 as `open` while also recording the cross-sheet correction in the same issue; unclear whether status should be `corrected` (partially) or `open`. Chose open with correction/change fields filled. A way to split an issue would help.
- Sentinel descriptions ("?", "missing") left unrecorded as out of scope (labels only) — skill allows this but they now stay as unrecorded issues in the scan file; awb-status may nag later.
- sources.md/catalog/quality/glossary: had to copy templates myself; awb-init said "create as conditions fire" but no helper creates sources.md (retain created it? It reported "created": true for the ledger — yes, retain created sources.md, good). catalog.md and glossary.md I copied by hand.
- awb-scope says ask all user decisions before writing records; user asked to proceed, so I recorded Q-006 (small-base threshold) as open user decision rather than block.
- Deviation: I ran a quick exploratory query (overseas Year 1 sizes) to make the Q-006 recommendation concrete; not via run.py, so exploration only.

## Turn 3 — analysis (analysis.md), run.py results, awb-package headline preview

Files used: workbench-guides/analysis.md, awb-package/SKILL.md, references/package-contract.md, package-format/findings-template.md.

What worked well
- run.py + settings tables + producers with reconcile(): seven results ran first time, all checks passing; `answers` auto-marked Q-001..Q-005 answered (provisional).
- `state finding --text` number warning caught "-£64k" (a derived sum not in any table) — useful; fixed by adding a total row to the result.
- `questions answer Q-001 --result <id>` linked an extra result without staling.

Friction / confusing
- settings comment says joins needs keys AND left_rows; for a result with no join, `joins` is always "not assessed" and has to be caveated on every finding. Noisy: a "not-applicable" outcome for joins would help.
- DuckDB: `QUALIFY` with `GROUP BY ALL` unsupported (binder error); `share` and `value` are reserved-ish aliases (parser errors). My mistakes but common traps.
- awb-package step 1 says ask which datasets to include for a new package; step 3 preview-and-wait writes `.preview/headlines.md` "in the draft folder", but the draft folder is created by `export` (step 4). I created it by hand (deliveries/<inv>/<pkg>/draft/.preview/). Ordering ambiguity.
- Deck length "about 8 slides": unclear whether title counts. Contract says report main slides "title included". My plan has 9 main incl. title; proposed How we know to appendix.
- User's instruction "I'd expect to be asked before removing transaction rows where meaning is uncertain" — the awb-clean rule let me remove cross-sheet overlaps myself when periods overlap. The user was fine but signalled preference; recorded it in DQ-001 treatment. Possibly the skill's self-decide rule for cross-sheet duplicates is too permissive when documentation doesn't explicitly say so.
- Deviation: added a column to overseas-growth after seeing the result (largest customer share) — a new metric, not a threshold, so no user decision needed per analysis.md, but I disclose it in the reply.

## Turn 4 — awb-status, user's verification requests, headline revisions

Files used: awb-status/SKILL.md; MCP read status.

What worked well
- status collector clear; correctly said "headline preview written, not yet exported" and state "out of date" (my next steps were stale — I had not updated state.md after running results; the rule to keep state current is easy to forget mid-turn).
- Adding coverage columns into the run.py result (rather than chat-only exploration) let the December check become recorded evidence.

Friction / confusing
- `state next --drop 1 --drop 1` — second drop "matching zero or several" refused silently in my pipe (I redirected stderr); dropping by number is resolved before changes, so two `--drop 1` refer to the same item. Needed separate call. Minor.
- awb-status says report is read-only and "carry out other requests through their own skills after" — but the user's checks are analysis (no skill) plus awb-package wording; I did analysis under AGENTS.md and revised the preview file by hand (awb-package checkpoint). No skill covers "revise preview headlines" explicitly; worked.
- Where to record user's audience wording preferences ("first observed" not "new", etc.) — brief Audience section seemed right; review-rules might be better for repeatable checks but awb-package says offer review rules only when correcting a *draft*. Preview isn't a draft yet. Ambiguous; I put them in the brief and will offer review rules at drafting.
- Status prompt: "Treat each finding's not-assessed joins caveat" — all caveats listed in status are noise from joins not-assessed; the report would be cleaner if not-applicable joins could be declared.

## Turn 5 — awb-package full draft, export, review, check-draft

Files used: awb-package SKILL.md, package-contract.md, review.md, helpers.md (skimmed), package-format templates (findings, methodology, methodology-note, manifest, deck-rules).

What worked well
- export's methodology_lines and display_stub flow were smooth once display.toml was written up front; [values.<column>] relabelled "Bad-debt adjustments".
- check-draft numbers check caught three quality-record counts; allowed_numbers with reasons resolved them.
- The read-only reviewer (Plan subagent) caught real problems: an "exactly" claim contradicted by a -4.4e-06 floating-point gap, unsupported "most informative", a speculative notes sentence, imperative Answer headline, and a claim resting only on an exploration query. Scoped re-review was quick and clean.

Friction / confusing
- "Imperative sentence outside Implications" rule collided with the user's explicit request for a recommendation on the Answer slide; I rewrote as gerunds ("Recommendation: protecting key accounts, testing...") which is awkward English. The template's Answer slide could allow a recommendation bullet explicitly.
- Floating-point reconciliation_gap: summing doubles gives -4.4e-06, so a natural "identified + unidentified = total exactly" claim fails review. A DECIMAL cast or a documented tolerance path in settings (not judgment detail) would help; review.md says tolerance must be recorded "before the result" in brief or [parameters] — not obvious up front.
- precision_warnings false positive: 0.1875 (=3/16) is genuinely four decimals; the warning cannot be silenced.
- A result run before its code is committed shows producing_uncommitted_changes; with "commit as I go" I had to commit then rerun then re-export (--result only). Workable but a dance.
- The 16-word headline was user-approved at preview; check-draft only warns but `passed` stays false until accepted or shortened, so I must ask the user again. Preview step could run the word count to catch this earlier (I miscounted).
- deliveries/ is gitignored so package edits never show in git status; fine, but easy to forget they're outside history.

## Turn 6 — corrections, review rules, reconciliation table

What worked well
- review-rules add --confirmed was straightforward; rules immediately judged in the scoped review.
- Reshaping revenue-reconciliation to a wide table and re-exporting was quick; run.py "kept" the supported status after the commit-rerun.

Friction / confusing
- review-rules have no "this investigation" scope — only every package or one package. User asked "future packages in this investigation"; I used every package (only one investigation exists) and will say so.
- Changing a slide headline requires the identical heading in methodology.md; I forgot and check-draft reported headings + claims + storyline + unlinked_findings — four rows for one cause. A single "methodology heading missing" row would be clearer.
- The scoped-review rule "take a problem marked (unchanged since the prior review) to the user rather than repairing it" forced me to stop on a trivial internal citation error (methodology cites the wrong result for monthly movements) and ask the user, leaving the draft not passed at the end of a turn where the user asked to confirm checks pass. Rule is defensible but heavy for internal-reference typos.
- Two reviews per request limit plus the unchanged-problem rule means user must reply again just to approve a one-word citation fix.
- check-draft "passed": true while review is "failed" in the earlier JSON — wait, now passed reflects review? Verified: check-draft passed flag below.

## Turn 7 — citation fix, final review, awb-release

What worked well
- release ran the verify-only gate, froze released/001, and copied to storage with tree comparison, one call. Clear JSON with open_caveats ready for the report.
- Scoped final review was clean first time.

Friction / confusing
- User's preference ("routine citation corrections don't need a decision") conflicts with review.md's "take unchanged-since-prior problems to the user". AGENTS.md says project conventions win, so I recorded it under a new "Project conventions" section in AGENTS.md. No skill names where such working preferences belong; brief Audience is about readers, glossary is terms.
- Earlier observation: check-draft returned "passed": true while review status was "failed" (turn 6). The contract says done requires review current; the passed flag doesn't fold in the review, which is misleading if read alone. release does gate on it.
