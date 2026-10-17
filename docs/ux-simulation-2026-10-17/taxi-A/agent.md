# Agent feedback — taxi-A analytics workbench usability session

This report draws on agent-notes.md and the completed investigation. The user supplied two TLC trip files and a zone lookup, requested five comparisons and a board package, reviewed the analysis and headlines, corrected the draft, and approved release 001. All five root questions ended answered with supported primary results. The release and its external storage copy verified. No unresolved operational blocker remained. The most consequential friction was in package construction and editorial review, rather than data execution.

Skill paths below are relative to agent-home/.agents/skills; project paths are relative to project/. I used awb-init, awb-scope, awb-clean, awb-package, awb-status and awb-release. I did not invoke awb-explore or awb-brainstorm. Some later descriptions of failures in the turn log are abbreviated; I identify that instead of inventing an exact missing command body.

## 1. Ranked pain points and suggested fixes

1. **Major — awb-package/references/review.md, step 3, and package-contract.md: every represented question becomes required audience content.** The first reviewer correctly applied the written contract and required an independent no-mix-up verification on the tipping slide because its question appeared among represented results. That verification compared standard-rate overall medians with Manhattan all-card medians. The board was never shown the latter statistic. Adding the bullet satisfied the review but introduced exactly the noise the user subsequently asked to remove. I then had to document an explicit user override in the brief and methodology so a later reviewer would allow notes-only treatment. **Fix:** distinguish audience questions from internal verification questions. Require visible answers for the former, while permitting the latter in notes/internal methodology without an exception ceremony. Evidence representation should not imply presentation priority.

2. **Major — mcp__awb__package export and awb-package/SKILL.md step 4: selection replacement is easy to trigger accidentally.** I attempted a provenance refresh with only --result arguments plus --no-datasets. The helper removed all five existing chart exports and then reported missing chart files. This was my misuse: the skill's specific refresh instruction says to omit --chart, --dataset AND --no-datasets. Nevertheless, --no-datasets looks like an independent audience-dataset choice, not an instruction to replace charts with an empty chart selection. **Fix:** reject a no-chart export that would delete existing charts unless explicitly requested, add an unambiguous refresh-provenance operation, or separate chart selection replacement from dataset selection replacement. Include a dry-run/removal summary. This was reversible and no analytical result was lost, but it consumed a repair cycle.

3. **Major — state/question model in src/awb.py helpers and AGENTS.md record maintenance: no reference-only role.** Superseding a valid unrestricted ranking or an all-card reference finding made a question appear awaiting recheck even when its new primary result was supported and current. I restored the old results to provisional reference status, leaving the project with two provisional findings that are neither unfinished analysis nor board-primary evidence. **Fix:** model presentation role separately from validity/status: primary, reference, internal verification, retired. Permit a valid reference result without treating it as an outstanding provisional answer. Do not let presentation replacement automatically imply analytical invalidation.

4. **Major — package serialization boundary, one-condition chart selection grammar, and run.py result requirements.** Export supports one @where column or @first selector. Showing both months' primary supported top tens needed scenario='all' AND supported_rank<=10; the existing result also contained sensitivity and unqualified rows. I created a separately validated board-rankings projection by recomputing the accepted queries. A second projection recorded the airport median-fare ratio and chart-ready disjoint groups. These were legitimate, traceable results, but package assembly gained more settings, producers, evidence and finding rows. **Fix:** support a safe explicit conjunction of row predicates and a structured chart projection specification. Distinguish selecting/formatting an existing result from conducting new analysis. A newly interpreted ratio still deserves a recorded analytical derivation; filtering a previously validated table should not need another full finding.

5. **Major — awb-package/SKILL.md, package-contract.md, helpers.md, review.md, and package-format templates: packaging instructions are too large and distributed.** The agent must coordinate exact headings, claim strength, chart roles, labels, rounding, questions copied verbatim, inferred primaries, manifests, flags, review snapshots, inventory and release gates. Broad reads repeatedly truncated, producing additional targeted reads. **Fix:** provide a short executable happy path, a concise generated checklist for the specific draft, and link diagnostics only when triggered. Generate boilerplate methodology mappings and represented-question text directly into a maintained section instead of making the agent paste them. Keep policy in one place and avoid repeating it across skill, contract, helper reference and templates.

6. **Minor — package numbers checks in src/packaging/draft.py: formatting repairs displaced analytical work.** Slash-joined times, paired percentages with the percent sign applying only to the second value, and years in some prose contexts produced number errors. Some were genuinely ambiguous formatting; others were familiar compact notation in internal methodology. I rewrote them, lowered unnecessary precision and used explicit percent signs rather than bypassing the checks with allowed_numbers. **Fix:** recognize standard paired values and time lists, provide exact suggested rewrites, and separate stylistic ambiguity from an unsupported quantitative claim. Retain the numerical-traceability check: it was useful.

7. **Minor — package claim and primary-result inference in package-contract.md and check-draft.** A descriptive verification result made the mixed tipping slide's required claim strength descriptive even though its substantive result was an association. Adding an explanatory paragraph before the main methodology paragraph also changed the inferred primary result, because first citation controls primacy/order. I restored the intended first citation before final review. **Fix:** declare primary/supporting/verification roles explicitly in metadata. Determine claim limits from the claims each result actually supports, not the weakest status of any citation in the whole section.

8. **Minor — check-draft reporting and mcp__awb__read state/status output.** check-draft could return passed:true while review was none or stale. The skill explains the extra review-current condition, but a caller reading passed alone could mistake this for release readiness. State/status emitted substantial explanatory/template text and many repeated caveats. **Fix:** expose separate mechanical_passed and release_ready booleans, with a compact blockers list. Offer summary/detail or field-selection modes for state/status. Keep full machine-readable facts available without forcing every resume to print whole documents.

9. **Minor — awb-clean/SKILL.md decision rules and workbench-guides/analysis.md threshold policy: user delegation is underemphasized.** The user explicitly required invalid-record signoff, which was appropriate to honor. Later the user asked me to recommend a few-hundred-trip floor AND rerun. I initially said I would wait again, then recognized that the current request delegated the choice and proceeded. **Fix:** explicitly distinguish unapproved meaning changes from choices the current user request delegates. State that prior authorization persists and that proposing a threshold before inspecting leaders does not always require another turn of approval.

10. **Minor — awb-scope setup and investigation templates.** Even a detailed intake needed multiple template copies and hand-authored records before the investigation existed. The first handoff had no durable intake object, so I temporarily preserved the user's question, delivery preference and method proposals in README. State templates retained long instructional placeholder prose after real entries were added. **Fix:** provide an investigation-create helper with optional populated brief/settings/ledger input and an intake area for work not yet scoped. Remove instructional placeholders from instantiated records, retaining documentation elsewhere.

11. **Minor — awb-package/SKILL.md correction-rule and headline approval instructions.** Asking before every potentially reusable correction could interrupt ordinary edits. In this session I treated specific wording changes as edits, applied the user's explicit twelve-hour standing rule without asking again, and shortened the headline only after the user explicitly authorized shortening. **Fix:** clearly allow direct application of supplied preferences and delegated shortening. Offer persistent rules after ordinary fixes unless the user explicitly requests one; do not infer another permission gate merely because an edit might recur.

12. **Minor — sandbox shell environment and setup examples.** Here-documents failed because the shell could not create a temporary file; Apple's git/xcrun also tried an unwritable system temp location. Python -c and project-local temporary scripts worked. **Fix:** set a writable task-local temporary directory in the execution environment and provide examples that do not depend on heredocs. This was an environment constraint, not a defect in analytical helpers.

13. **Minor — board deliverable is a builder kit, not a rendered deck or paginated note.** awb-package produced Markdown slide content, chart CSVs, builder rules and Microsoft 365 assembly instructions. The user read START-HERE and accepted this. Still, a request for slides plus a one-page note can sound like it will result in PowerPoint and a print-ready page; a 521-word Markdown note has a length check but no page-layout check. **Fix:** state the artifact format early and offer an optional rendering/build stage and one-page PDF/doc output. Do not describe the builder kit as an already built PowerPoint deck.

## 2. Contradictory, ambiguous, long or missing instructions

- **User instruction versus visible-coverage policy:** the user explicitly wanted the no-mix-up verification only in notes; the generic review policy required visible content for every represented question. User instructions took precedence. A presentation-role field would remove the conflict rather than requiring prose exceptions in multiple files.
- **Approved choices versus repeated interviews:** awb-init/scope handoffs, awb-clean meaning-change gates and analysis threshold instructions can imply another question even when the user already supplied the answer or delegated the decision. This session needed two useful initial business-context answers and the user's explicit invalid-cutoff approval. It did not need another dataset-selection question after the user said none, another methods-note question after the user requested it, or another approval for the delegated ranking floor.
- **Cleaning versus first publication:** awb-clean says a cleaning pass need not read the workbench guides, while project AGENTS.md requires data.md before publication. The request included both ingestion and cleaning; I applied data.md to first publication and clean instructions to the scan/treatment. This is resolvable by task boundaries, but a combined-ingest-and-clean example would help.
- **Packaging serialization versus minimal derivations:** the prohibition on new findings from exploratory output was valuable, but the documentation leaves little ergonomic middle ground for a chart projection or an explanatory ratio of accepted statistics. I kept these as new recorded results; this expanded the result/finding surface substantially.
- **Provisional/support semantics versus reference evidence:** all-card and unrestricted rankings remained valid references after the primary presentation changed. The available statuses did not express that well. Superseded means unsettled for every linked question; provisional sounds unfinished. This should be documented or modeled explicitly.
- **Reviewer maximum rounds:** review.md says stop after problems remain on the second review in a request. It protects against endless repairs but could leave a simple reversible issue unfinished, contrary to the host's persistence instruction. We did not hit this limit: the first full review had three problems, the second scoped pass succeeded; later user corrections had one clean scoped review. Prefer escalating only unresolved decisions or repeatedly failing checks, not an absolute repair-round cap.
- **Permission to update shipped helpers/formats:** instructions require asking before modifying them. I respected this and changed none. Good guard for provenance, but it means a minor helper/interface problem can require a separate approval flow. A supported compatibility/repair command is useful; setup already helped here.
- **Question linkage and scopes:** initially created analytical children remained open even after existing result caveats substantively answered them. I later linked those results and retained the limits as caveats rather than artificial unanswered questions. Examples should show that an answer can be 'not observable from these records' and need not become new data work.
- **Output verbosity requirements:** awb-status asks for one screen while listing findings/caveats/roots/subquestions/packages/storage/source limits; awb-release requires every open caveat even when the user asks only for the release path. I repeated the release caveats in the final response because the skill required it. Consider a concise completion mode with a link to retained caveats, especially after the user has reviewed them.
- **Missing crisp distinction between loaded and cleaned:** the system ultimately supports it well, but the user had to ask whether files were fully in. A standard stage indicator such as landed, published/queryable, screened, analyzed, packaged, released would make this visible earlier.

## 3. Failures and unexpected behavior, with commands/errors

### A. External/environment failures

1. Shell here-document invocation recorded in notes as `python3 - <<'PY' ... PY` failed with:
   `zsh:1: can't create temp file for here document: operation not permitted`.
   The body was abbreviated in the turn log, so this is the exact recorded invocation shape, not a reconstructed full command. Workaround: Python -c or a script created with apply_patch.

2. `git status --short` before initialization returned:
   `git: error: couldn't create cache file '/var/folders/cr/64mtlg6x6j3_sjjtj19wyfzh0000gn/T/xcrun_db-G48gXb8v' (errno=Operation not permitted)`
   and `fatal: not a git repository (or any of the parent directories): .git`.
   `TMPDIR="$PWD/.workbench-tmp" git init` still warned about an xcrun temp cache path but successfully initialized the repository. No commit was made. Pip also disabled its unwritable default cache, but installation succeeded.

3. Exact download commands:
   `curl -fL https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf -o foundation/references/tlc-yellow/data_dictionary_trip_records_yellow.pdf`
   and
   `curl -fL https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page -o foundation/references/tlc-yellow/trip-record-data.html`
   both returned `curl: (22) The requested URL returned error: 403`.
   The web reader could access the content. I recorded access notes, including the dictionary revision postdating the extracts, rather than claiming a retained file. The separate NYC311 HTML retention succeeded.

### B. Helper/interface mistakes and diagnostics

4. `mcp__awb__records` with command `clean-record`, scan `yellow-trips`, and a new issue's evidence string
   `src/preparation/yellow_trips-check.sql; both publication.json files; investigations/trip-pattern-comparison/exploration/intake-integrity.sql`
   returned exit 2 and:
   `RecordError: N1 evidence names no saved query: ...; evidence ending in .sql must be a saved query's path alone, relative to the project root and naming a file in it; otherwise give a reference in words that does not end in .sql`.
   This was my payload error; help documents the grammar. It made no partial changes. Retrying with the single saved-query path succeeded. A list-of-evidence schema would be more ergonomic than overloading a string's suffix.

5. Exact MCP export call, shortened only by expressing its JSON as the equivalent argument list:
   `mcp__awb__package(command="export", args=["trip-pattern-comparison","board-brief","--result","q1-volume","--result","board-airports","--result","q3-standard","--result","board-rankings","--result","q4-quality","--result","q1-thursday","--result","q2-airports","--result","q3-verification","--result","q5-supported","--no-datasets"])`, with the absolute project root.
   It removed existing charts, wrote `charts: []`, and returned exit 1 with five `check_charts` entries: `no chart file for this specification`.
   `ls deliveries/trip-pattern-comparison/board-brief/draft/charts` then returned `No such file or directory`, exit 1.
   Full explicit re-export restored all five chart files. The skill actually instructs omission of --no-datasets for provenance-only refresh; my mistake exposed the selection-replacement footgun described above.

6. A premature `mcp__awb__read(command="review-rules", investigation="trip-pattern-comparison", package="board-brief")` before narratives existed reported missing findings.md/methodology.md. That was an ordering error, not an unavailable tool. Creating the narratives resolved it.

7. Mechanical preflight diagnostics included `no represented result records this number at its written precision`, `digits joined by dots, commas, slashes, or colons read as one number with no single value`, and the year-context count diagnostic. A mixed Q3 section also reported `methodology.md states association on its **Claim strength:** line; its results support descriptive`. All were repaired in prose/metadata before narrative review. No unsupported-number allowlist bypass was used.

### C. Agent-authored execution mistakes, not workbench bugs

8. An orchestration loop used `text` as a loop variable and shadowed functions.exec's output helper, producing `TypeError: text is not a function at exec_main.mjs:9:38` after the first state mutation had succeeded. The complete original JS is not retained in agent-notes.md. I renamed the variable, inspected the already-completed first mutation and retried; the first reported unchanged. No analytical calculation was affected.

9. Exact failed diagnostic:
   `.venv/bin/python -c 'import pandas as pd; p="investigations/trip-pattern-comparison/results/"; print(pd.read_csv(p+"q3-standard.csv").query("grain == chr(98)+chr(111)+chr(114)+chr(111)+chr(117)+chr(103)+chr(104)")[["source_month","label","trips","median_tip_pct","all_card_trips","code99_card_share"]].to_string(index=False))'`
   failed with pandas `UndefinedVariableError: name 'chr' is not defined` and `ValueError: "chr" is not a supported function`.
   This unnecessary expression-parser construction was my mistake. Ordinary `.loc[f.grain.eq("borough")]` worked.

10. Exact failed metadata command:
    `.venv/bin/python -c 'from pathlib import Path; import json,shutil; d=Path("deliveries/trip-pattern-comparison/board-brief/draft"); m=json.loads((d/"manifest.json").read_text()); f=d/"methodology.md"; s=f.read_text(); q="\n".join("- "+r["result_id"]+": "+r["question"] for r in m["results"]); s=s.replace("Exact questions follow with chart mappings below.","\n"+q); lines=[]; labels={};\n'`
    failed with `SyntaxError: unexpected character after line continuation character`.
    I wrote a temporary Python script using apply_patch instead of embedding multiline logic in -c.

11. `tools.apply_patch` on methodology.md failed atomically with `apply_patch verification failed: Failed to find expected lines` when I supplied a long paragraph prefix rather than its entire source line. The missing match began `Primary `q5-supported`, evidence/q5-supported.json; supporting `board-rankings`...`. I used short heading context for the replacement instead. No partial patch was applied.

12. A manifest inspection looked for a nonexistent top-level `rows` key and printed None. The publication's actual check outcomes and row counts were available elsewhere and had passed; I did not treat None as failed ingestion. A compact documented publication-summary schema would prevent this guess.

## 4. Adaptations and deviations

- I temporarily used README as durable intake storage before the scope interview created an investigation; there was no dedicated intake record. I subsequently moved the context into brief/settings/history.
- I did not mechanically re-ask for supplied audience, eight-slide target, methods note, no-datasets choice, standing time rule or delegated headline shortening. Existing user instructions supplied those decisions.
- I initially proposed waiting for approval of the ranking support floor, then corrected that interpretation. The user had delegated recommending and rerunning; the earlier invalid-record gate did not cover this later presentation-support request. I stated 300 before inspecting qualified leaders and proceeded.
- I used local screening views rather than editing canonical values. The rules defined eligibility for this investigation, not universally correct source values. Raw records, both repeated July rows and unknown/outside categories remained intact. This was the intended foundation/analysis separation, not silent dropping.
- One early ad hoc diagnostic read a saved five-row CSV. I replaced the durable logic with a saved SQL wrapper over the original canonical query and reran it. No final result consumes intermediate result CSVs.
- I restored still-valid superseded references to provisional because the model otherwise marked fresh primary answers awaiting recheck. The resulting provisional references are a workaround for a missing role/status, not unfinished primary analysis.
- I created chart-ready recorded projections rather than editing chart CSVs by hand or feeding saved CSVs to analysis. This followed provenance requirements but expanded code/evidence during packaging.
- I deliberately obeyed the later user request to remove visible verification noise, overriding the generic review coverage rule for that ancillary question. The exception is recorded; source results and speaker-note verification were not deleted.
- I treated the user's request to see changed slides before release as an actual review gate. The package/release instructions explicitly require their yes after revisions. I completed all revisions, exports, independent review and checks before asking, then released immediately after approval without another confirmation.
- No shipped helper/template was modified, no unrequested Git commit was made, no source file was changed, no data refreshed upstream, and no outside message was sent. Fresh subagents were used only for the skill-required independent package reviews, with read-only instructions; they did not write or repair files.

## 5. Disproportionate time and token costs

- **Highest:** packaging/review scaffolding relative to an eight-slide narrative. Much work went into exact question repetition, chart mappings, first-citation primacy, weakest-result claim labels, manifest lifecycle and receipts. The editorial false positive about internal verification caused an extra board-facing bullet, later removed at the user's request with another scoped review.
- **High:** repeated long reads and large MCP state/status/help outputs, sometimes truncated. Context recovery duplicated some already-read instructions. I could have used more focused reads earlier; tools could expose compact summaries and actionable diffs.
- **High:** maintaining the same intent across README, brief, settings, history, state, ledger, quality records, report files and package methodology. The helpers protected structured records, but prose orientation sentences needed manual synchronization.
- **Moderate:** new validated projections to select already computed chart rows and record a simple fare ratio, plus full export reruns after display changes. Data scans themselves were fast; evidence and record overhead dominated.
- **Moderate and avoidable:** shell quoting/parser errors, the accidental export reset, overlong patch context and numeric-notation repairs. These were recoverable, but consumed attention without improving the analysis.
- **Appropriate cost:** the independent tipping verification. The exact equal medians were a real user concern. Reapplying screens directly from the full publication and checking population counts, median rank counts and tied hourly extrema was worthwhile and did not merely mirror the same saved output.

## 6. What worked well

- Landing preserved supplied bytes and automatically copied originals to the requested retention location. Publication was a distinct step with typed complete analytical inputs, lineage and per-file row reconciliation. This let me answer plainly when files were only landed versus fully queryable.
- Structural ingestion checks passed for 265 zones and 6,041,527 trip records. The scan surfaced duplicate-looking rows, unknown categories and outliers without requiring them to be declared errors. Inspection supported review flags rather than arbitrary high-value exclusions.
- The source register supported honest access notes when TLC downloads were blocked. Official dictionary and NYC311 checks materially improved interpretation: unknown rate 99, absent cash tips, and questionable Newark pickup coding. Historical/current distinctions stayed visible.
- User approval of concrete screening rules worked well. Counts were reported before application, all raw records remained auditable, distinct exclusions and overlapping reasons were separated, and every monthly/vendor denominator reconciled.
- The result runner and evidence system worked reliably without helper edits. Dynamic audits checked join preservation, lookup uniqueness, dates, populations, support thresholds and sensitivity scenarios. Final stale checks showed eleven current results with no runtime mismatches.
- Analytical results challenged the initial framing: sparse unrestricted leaders, unknown-rate zero tips, and the July 4 Thursday comparison. The workflow preserved those results and supported explicit refinements rather than silently smoothing them away.
- records tools safely maintained questions/findings and readable Markdown views. Parented questions preserved the five original user roots. Clean-record kept quality records/catalog coherent. Most calls were fast, predictable and independently inspectable.
- Display mappings converted all hour labels to a.m./p.m. without recalculating results or changing chronological order. The confirmed standing rule passed subsequent independent review.
- A fresh reviewer caught real omissions: airport fare distribution summaries and ranking exposure fields. Receipts made the reviewed snapshot explicit. Reusing a current approved receipt at final release avoided redundant review.
- START-HERE clearly separated audience material, internal methodology and deck-builder inputs. The user reviewed it and understood the package. The release helper froze 001, verified the local copy, copied it to the configured storage path and verified equality, all in one successful call.

## 7. awb MCP tools visible and used

All seven awb MCP tools were discoverable through ALL_TOOLS and used during the session. I preferred them for workbench commands, using shell/Python for authoring code, reading files and environment work rather than replacing functioning MCP tools.

| Tool | Used operations |
| --- | --- |
| mcp__awb__setup | Helper/package-format installation, environment/dependency setup and checks |
| mcp__awb__read | state, questions, sql, profile, stale, help, status, review-rules, review-receipt, read-only check-draft |
| mcp__awb__data | land/retain/publish and data preparation, saved diagnostic SQL/profile output, clean-scan |
| mcp__awb__records | state switch/findings/issues/next, questions, clean-record, confirmed review-rules add |
| mcp__awb__run | Initial result production and later authorized refinement/verification/projection results |
| mcp__awb__package | export, review-receipt start/record, final inventory-writing check-draft |
| mcp__awb__release | release; it also copied and verified external storage automatically |

No separate copy-releases call was needed. I did not use eda-scan/eda-show in this investigation. No awb tool was missing or inaccessible, and no automatic approval rejection blocked work. Functions orchestration, filesystem execution, apply_patch, official web reading and the skill-required fresh reviewer agents supplemented the MCP tools.
