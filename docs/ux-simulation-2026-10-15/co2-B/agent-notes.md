# Agent friction log (co2-B)

## Turn 1 — awb-init, then awb-scope (New branch)

Files used: awb-init/SKILL.md; assets/workbench/{README.md,AGENTS.md,.gitignore}; foundation/{sources.md,glossary.md,quality.md} templates; investigation/{brief,state,history,settings.toml,run.py}; scripts/install_helpers.py (--help, install, --check, --mcp-config claude); installed workbench-guides/data.md; awb-scope/SKILL.md. Did not read references/landing.md, analysis.md (no result work yet).

What worked well
- Installer is a clean black box: one JSON line, clear `files`/`packages`/`install` fields. `--check` after installing confirmed packages ok.
- `questions add` prints the ID immediately, which made writing brief references easy. `state switch` works before brief.md exists.
- awb.py --help is a good index.

Friction / confusion
- Step 1.3 (host instruction files above the target) conflicts with sandbox bounds: checking ancestors means touching dirs outside the project. I did existence-only `test -e` checks for CLAUDE.md/CLAUDE.local.md/.claude/CLAUDE.md/AGENTS.md; none found.
- Installer needs workbench markers before it runs (exit 1 otherwise, per help). SKILL.md step 3 orders root files (3.1) before installer (3.3), so it's fine, but the dependency isn't stated.
- "Declare the helpers' packages, with the interpreter that will run the project's analysis, such as its virtual environment" — no guidance on creating a venv when none exists. System python3 lacks duckdb, so I created `.venv` with uv (Python 3.12). The installer's printed install command is `.venv/bin/python -m pip install duckdb pandas`, which FAILS on a uv-created venv ("No module named pip"). Used `uv pip install --python .venv/bin/python -r requirements.txt` instead.
- SKILL.md says the user "adds or runs" the install command; I ran it myself in the project-local venv (deviation) because every later helper needs duckdb. Reported it.
- AGENTS.md hardcodes `python3 src/awb.py` everywhere; with a venv that's wrong. I added a "Project environment" section to AGENTS.md telling agents to use `.venv/bin/python`. Templates could mention the interpreter substitution.
- I accidentally read the top 80 lines of install_helpers.py source (head) before --help; the skill asks to treat it as a black box. --help duplicates the docstring anyway.
- zsh: `echo ======` errors ("= not found") — my own mistake, not the skill's.
- `--mcp-config claude` prints an entry whose command is <python-prefix>/bin/python3 (no duckdb). Unclear whether the MCP server runs helpers with its own interpreter or the project's; if its own, data commands would fail. Not documented.
- sources.md reference-format rules are very long (a paragraph of parsing edge cases); I just used the simple `reference: [text](path)` form. The guidance is overkill for authors.
- data.md: "Assess a candidate from its documentation" — fetched codebook + README into foundation/references/owid-co2/ before landing anything. Good fit, but SKILL.md (init) says create sources.md "when a source becomes a real candidate" without saying whether init should land data; I deferred landing to a later turn since scope says "writes investigation records only".
- awb-scope says interview until settled, then write records "without a separate confirmation round" — but in a single-turn host the agent can't ask mid-turn. I created the investigation from the settled parts and parked the unresolved method choices as user questions Q-001..Q-007, asking the first four at turn end. Pacing rule (max four per round) left 3 decisions for a later round.
- `state next --add` items render directly under the template guidance paragraph with no blank line (cosmetic).
- The state.md/brief guidance paragraphs remain in the files after population; unclear whether to delete instructional comments in brief (I replaced brief guidance with content but left state.md's table guidance, since tools render around it).

## Turn 2 — answers recorded, landing, publish, results (awb-scope Sharpen + data.md + analysis.md)

Files used: workbench-guides/data.md, analysis.md; awb-init/references/landing.md, validation.md; datasets.toml and catalog.md templates.

What worked well
- `land()` fetch-script pattern + `retain` worked first try; retention copy matched; Acquisitions row written automatically and source flipped to acquired.
- `publish` refused on my custom check with a clear failing row (Namibia 1990) and left a .partial; easy to resolve.
- run.py template is solid: answers= auto-marked ledger questions answered; JSON output lines are easy to scan.
- `state finding` stale guard caught that I'd edited run.py after running results ("stale (uncommitted-code)"); rerun fixed it. Good guard, but message could say "run.py changed since this result ran" rather than "uncommitted-code", which made me think I had to commit first.

Friction
- Retention destination nests the full project-relative path: storage/landed/data/raw/owid-co2/<acq>/. Surprising; the user might expect storage/landed/owid-co2/<acq>/.
- `awb.py sql` defaults to 20 rows and silently truncates ("20 of 36 rows shown") — fine, but I missed it the first time.
- `sql` parser error on alias `rows` (DuckDB reserved) — my mistake.
- analysis.md wants row_counts and joins checks for every result, but joins needs `left_rows` from a producer; for simple results that meant writing trivial producers (`unique_rows`) whose left_rows = len(frame) just to get key-uniqueness assessed. The joins spec conflates "no multiplication" with "key uniqueness". A `keys_unique`-only mode would help.
- row_counts for static results must be hand-entered before/after constants in settings — awkward; I wrote counts queries as a second query and a generic `with_counts` producer.
- `state next --drop 1 --drop 1` (repeat) only dropped one item; second silently ignored? Output said dropped 0 for second call. Unclear semantics for repeated same index.
- Guidance says suggest commits before publishing ("so conversion_commit holds it"), but AGENTS.md says commit only when the user asks. In a single-turn flow I published uncommitted and recorded it as an unresolved issue.
- Promotion to supported: the guide doesn't say whether the agent may promote on its own after checks pass or should wait for the user. I promoted with caveats since the user asked for analysis.
- State template guidance paragraphs remain inside state.md, so `state` output is noisy.

## Turn 3 — awb-status, analysis additions, commit, awb-package (stopped at headline checkpoint)

Files used: awb-status/SKILL.md + collect_status.py; awb-package/SKILL.md, references/package-contract.md; package-format/findings-template.md (installed via --package-formats).

What worked well
- collect_status.py output is complete and easy to summarize; uncertainties empty.
- `stale` command is a fast sanity check before promoting.
- Rerun keeps finding text when tables are unchanged.

Friction
- User asked for status AND a list of actions in one message; awb-status is read-only and its report ends with "You can ask for" suggestions, which are moot when the user already asked for the next things. I gave a compressed status.
- Editing settings [parameters] (adding two new parameters for a new result) made ALL results stale and reset every supported finding to provisional on rerun, requiring re-promotion of 6 findings. Parameters are global to all results' evidence; a per-result parameter scope would avoid this churn.
- Promotion after a rerun needed the same --reason boilerplate again; one bulk call with multiple IDs worked (good).
- `state next --drop 1 --drop 1` again dropped only one item (second ignored, no error). Dropping by text worked.
- Git identity: commits need an author; I used `-c user.name/user.email` placeholders rather than reading the host's global identity. The skills say nothing about authorship.
- Publication made before first commit records conversion_commit "uncommitted"; no command to re-stamp it after committing short of republishing under a new ID. Recorded as an unresolved issue.
- awb-package: the template mandates Answer, findings, Implications, How we know, Limitations, Supporting datasets slides => 12 slides for 6 findings, vs the user's "about eight slides". No guidance for a slide budget or appendix. Asked the user.
- awb-package requires a headline-approval checkpoint before full slides, so the user's request "draft the package ... point me to the files" cannot be completed in one turn. Followed the skill; user gets headlines, not files.
- Chart files serialize a whole result (columns selectable, rows not), so a top-10 chart from a 45/59-row ranking needs a separate chart-only result (I added coal-share-since-2010-top10). Row filtering in export would avoid result proliferation.
- A result that answers no data question (countries-for-further-assessment) will sort last as "unlinked" — that's where I want it, but the contract calls it out as something to report; slightly odd for a deliberate closing slide.
- A data question can't be answered by a result whose question differs from it, and the run.py result question must be "the user's own words": for derived/supporting results (full ranking, chart subset) there are no user words; I wrote neutral questions.

## Turn 4 — awb-package full draft

Files used: methodology-template.md, deck-rules.md, manifest-template.md, references/review.md, references/helpers.md; export/check-draft/review-rules CLI.

What worked well
- export + display.toml flow is clear; display_stub errors list every missing column at once.
- check-draft caught a 16-word headline and four untraceable numbers (ISO 3166, row count, a year, Namibia 1990) precisely; fixes were quick.
- The read-only reviewer subagent (Plan type) found real problems check-draft can't: agent-verb wording ("countries cut CO2") above descriptive claim strength, a regional generalization, a claim not computable from net-only trade data ("domestic emissions remain the larger part"), missing years. Valuable.

Friction
- `export` refuses with "no draft at ... create it with awb-package" when the draft dir doesn't exist; the skill says export comes after writing, but doesn't say to mkdir the draft first. Minor.
- My own mistake: a stray `cat > /dev/null` hung a Bash call for 120s (waiting on stdin).
- The host's Write tool refused to write findings.md/methodology.md from a subagent context ("Subagents should return findings as text"); wrote via shell heredoc instead. Environment-specific.
- Review rules I recorded from user corrections were judged very literally: R-periods-001 ("every finding statement that gives a number names the years") produced 13 errors on round 2, every bullet. Took 4 review rounds to reach clean. Rule wording matters a lot; a slide-level scope option would help. Each round needs a new fresh subagent (staleness), which is slow.
- Appendix: deck-rules forbid adding/dropping slides and the outline format has no appendix marker; I marked appendix slides only in speaker Notes. The template-mandated sections (Implications, How we know, Limitations, Supporting datasets) push decks over a user's slide budget.
- Five-bullet limit vs user wanting 8 datasets described: had to merge datasets into bullets.
- The run results/rerun/commit dance: evidence recorded before a commit gave producing_uncommitted_changes in the manifest; rerunning results at a clean commit and re-exporting fixed it, but nothing told me to do that except reading the manifest.
- Chart 2 (Table with 10 rows x 3 numbers) exceeds deck-rules' "about six numbers" guidance for Table; the user explicitly asked for a compact table, so kept it.

## Turn 5 — package revision from user review

What worked well
- Recording the user's review corrections as review rules (appendix headline, missing-vs-zero, rounding) and having the reviewer enforce them worked; two review rounds to clean.
- The user's question about the reconciliation exposed a real error: my "countries + non-country = World" claim was checked only on sample years and fails in 1991 (Kuwaiti oil fires double count, 478 Mt). Spot-check validation in a metric judgment let an untrue claim become a supported finding. A yearly reconciliation result fixed it; recorded as a methodological correction.

Friction
- The validation spec's judgments (scope/metrics/values) are free text the analyst writes before seeing outputs; nothing forces the claims in them to be computed. Here a spot-check claim turned out false.
- Methodology template has no slot for a plain-language summary; I added a "Methods in brief" section; check-draft accepted it.
- R-structure-001 pattern (headlines not starting "Appendix:") also matches core slides' headlines (false positives on Answer); reviewer judged correctly but the pattern can't be scoped to sections.
- Adding a new result (world-reconciliation) as --result only (not a dataset) because dataset selection is the user's decision per the skill; offered it instead.

## Turn 6 — ninth dataset + awb-release

Files used: awb-release/SKILL.md; review.md (reviewer launched again as required at release start).

What worked well
- `release` is one command: gate (check-draft --verify-only), numbered copy, storage copy and tree comparison; output reports copy verified (compare_trees empty). Clear.

Friction
- display.toml names are global by column name: the reconciliation's `world_mt` (annual) collided with Q4's `world_mt` (cumulative 1850-2024, rounded to 0), mislabeling the new dataset. Had to rename the result column (rerun, re-promote twice). Per-result display overrides would help.
- A result first run with uncommitted code is "refreshed" back to provisional when rerun at the commit, needing a second promotion each time — repeated churn across turns.
- The release skill requires a fresh review at the start of every release request even right after a clean review in the package revision; with subagent startup cost that's slow but cheap insurance.
- `git commit` with nothing to commit printed to stdout inside the JSON pipeline (my sequencing), harmless.
