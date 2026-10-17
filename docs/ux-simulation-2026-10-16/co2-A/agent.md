# Agent feedback — OWID CO2 donor-roundtable workbench

This report draws on feedback/agent-notes.md and the retained project records. The session completed successfully: five original data questions, three follow-ups and two supporting questions answered; 11 supported findings; an approved package with eight main slides, two appendix slides, six chart files and a short methods note; frozen release 001 verified locally and in the user's requested storage. No commits were made, as instructed.

## 1. Ranked pain points and suggested fixes

1. **Major — User wording versus hard-coded format enforcement.** Files: awb-package/SKILL.md, package-format/findings-template.md, src/packaging/draft.py::outline_problems, foundation/review-rules.md. A 15-word headline limit pushed country lists into slashes and encouraged dropping half of the Answer slide's story. The user first corrected the slashes and later explicitly restored the exact two-clause headline. The helper had no authorized-exception mechanism, so following the user would fail the release gate. I added a narrowly matched headline_length_exceptions field (slide, exact visible text, reason linked to the user's instruction), documented it and verified both positive and negative cases. **Fix:** ship an explicit, auditable user-override mechanism for presentation guidelines; make the word limit a warning by default. Never let a style limit erase the executive answer.

2. **Major — Inconsistent Unicode normalization between narratives and exported headers.** File: src/packaging/draft.py; tools: package/export and check-draft. Display names used typographic CO₂; the narrative reader normalized them to CO2 while CSV headers retained CO₂. The checker then reported nonexistent columns despite matching visible labels. This affected all six charts. My new headline exception initially hit the same normalization mismatch. **Fix:** normalize both sides consistently for comparison, preserving original display labels in outputs. Add tests covering CO₂, accented country names, smart punctuation and Unicode mathematical signs.

3. **Major — Repeated full narrative review after small repairs.** Files: awb-package/references/review.md and awb-release/SKILL.md. Independent review was valuable, but the rule that the last review must always be full led to repeated reading of three narratives, rules and evidence after small citation or wording fixes. The full-draft pass required four snapshots/reports; later corrections and release each needed another full review. **Fix:** retain an auditable review artifact keyed to narrative/rule/evidence hashes. Allow a scoped repair review plus an automated unchanged-content check to satisfy completion; reserve a new full review for material changes and release where appropriate. Make the cost and trigger explicit.

4. **Major — Number tracing treats presentation unit conversions as new analytical work.** Files: awb-package/SKILL.md, src/packaging/draft.py number checks, investigation queries/evidence. Recorded Mt results could not directly support the same values displayed in billions of tonnes. I added Gt presentation columns to two saved queries, reran and re-promoted the findings, and re-exported, although no underlying quantities, ranks or conclusions changed. The fixed conversion constant 1000 then itself needed an allowed_numbers explanation. **Fix:** support declared unit transforms and rounding as export metadata, with value-level checks. Distinguish unit constants, axis limits and derived analytical quantities. Keep the prohibition on inventing analytical numbers.

5. **Major — Oversized tool responses and duplicated context.** Files/tools: large packaging helper, serialized manifest, MCP read/state and package provenance output. A manifest read produced 17,385 tokens; one broad rg with context produced 36,108 tokens. Several initial batches were truncated, once hiding an interpreter refusal. **Fix:** provide compact status summaries and field-selectable manifest/evidence reads. Return provenance paths/digests by default, with expanded details on request. Split helpers or document a stable command-to-function/file index so agents need not search a large source file.

6. **Major — Read-only SQL wrapper misclassifies a normal SQL error.** Tool: mcp__awb__read command sql. An ambiguous year column generated a message saying the statement could not be checked and suggesting a retry without --read-only. The actual repair was an explicit join qualifier. **Fix:** distinguish binding/parser errors from unsupported read-only-plan verification. Never suggest more write privilege for an ordinary binder error.

7. **Major environment friction, not a skill defect — Default temporary paths are unwritable.** Tools: exec_command, shell heredocs, macOS Git/xcrun, pip. Shell heredocs failed before Python executed; xcrun tried to create caches outside writable roots even after setting TMPDIR. **Fix:** bootstrap a writable task temp/cache directory and document shell-safe Python -c or script-file patterns. Surface this environment constraint once. A setup preflight should check temp creation, interpreter and Git execution before multi-step installation.

8. **Minor — Generated START-HERE gives apparently contradictory handling instructions.** File: src/packaging/draft.py::start_here. It told the user to attach methodology.md to the builder, then said internal files must not be sent, without naming the audience. The user explicitly asked whether the builder could read it. **Fix:** say “The builder may read methodology.md as an internal reference; the audience receives methodology-note.md instead,” and “do not send to the audience.” I made that generator change so later checks would not overwrite a manual fix.

9. **Minor — Ledger-derived order can conflict with a sensible deck order.** Files: package contract, ledger, manifest storyline check. Consumption and historical slides cited EU reconciliation, whose supporting question was a child of Q1. Their earliest ancestor position put them ahead of GDP, even though the user approved a different order. **Fix:** separate primary answering results from supporting validation results when deriving a storyline; supporting checks should not determine a slide's position. The existing presentation_order override solved this case.

10. **Minor — Bootstrap is more interruptive than necessary for a detailed brief.** Files: awb-init/SKILL.md and awb-scope/SKILL.md. The init handoff requires an initial scope interview before investigation creation. This user already supplied five precise questions, source URLs, retention paths, audience and checkpoint mode. I preserved these in a temporary README handoff and asked only unresolved choices. **Fix:** support a filled-in scope proposal with one concise confirmation/missing-fields step rather than treating every new project as an empty interview.

11. **Minor — Source registration spans helper-written and hand-written records.** Files: foundation/sources.md, catalog.md, quality.md, glossary.md; data guide. Acquisition rows are automated, while assessment status, references, restrictions and interpretation need hand maintenance. **Fix:** offer a structured registration/update helper with validation and a clear ownership table. Keep the explicit distinction between original retention and analytical publication.

12. **Minor — Date-only state freshness is inconclusive during a no-commit session.** Tool: read/status. It correctly reported “indeterminate at date precision” while explicit evidence checks showed all 11 findings current. **Fix:** show evidence freshness beside state-record/Git freshness, and avoid presenting the latter as the principal freshness signal. Preserve the user's no-commit preference without repeated commit prompts.

## 2. Contradictory, ambiguous, overlong or missing instructions

- **User instructions versus the 15-word format rule:** the priority is clear at the top level, but the release helper enforced the subordinate rule without a documented exception. This was the clearest operational conflict.
- **START-HERE's builder/internal distinction:** technically consistent, conversationally ambiguous. “Internal” should mean withheld from donors, not prohibited as a builder input.
- **Headline country groups:** there was no reasoned path for fitting multiple requested claims into the word limit. Slashes were formally convenient but wrong for this audience. The guidance should prioritize coherent sentences over token counts.
- **Mandatory slide structure versus “about eight slides”:** title, answer, six findings, methods and caveats produce ten content slides. The appendix rule resolved this, but a slide-budget example up front would help. The builder also adds an Appendix divider, which should be counted explicitly when discussing the eventual PowerPoint's physical slide count.
- **Skill length and cross-references:** awb-package requires its contract, review procedure, helpers reference, multiple templates and deck/assembly files, on top of project AGENTS and data/analysis guides. Many rules are repeated with slightly different wording. A compact execution checklist plus a reference section would reduce rereading and compaction risk.
- **Review/check sequencing:** reviewer freshness is defined precisely, but small edits force an expensive full pass and the agent must maintain separate snapshots manually. A review artifact helper is missing.
- **“Compute through saved queries” versus packaging transformations:** a percentage-to-display or Mt-to-Gt conversion should be a checked serialization transform, not a new analytical finding cycle.
- **Plain-language methods note:** “short” has no concrete size target. Mine was approximately 831 words, defensible as one to two pages, but a target would improve consistency.
- **Package versus completed PowerPoint:** the skills produce an outline, CSV sources and M365 instructions. This worked because the user ultimately chose to build the deck, but the skill should establish early whether the deliverable is an assembly package or an actual PowerPoint. Do not imply a PPTX has been produced.
- **Missing helper navigation:** the instructions correctly say treat helpers as black boxes, but adaptation requires discovering a large source file's functions. A small architecture index would prevent guessing filenames.
- **Scope distinction was good:** data guides explicitly keep exploratory preparation local and require deliberate promotion, while the ledger separates user roots and analytical children. These were not contradictory; they prevented overreach.

## 3. Failed or unexpected commands/tools

Exact commands/calls and errors retained in the session notes are listed below. Some earlier multiline commands were logged only as fragments; I identify those as fragments rather than inventing an exact full script.

- Command: python3 - <<'PY' followed by a setup-copy script.
  Error: zsh:1: can't create temp file for here document: operation not permitted.
  The same failure occurred later with .venv/bin/python - <<'PY' for a manifest edit, and in one reviewer's read-only heredoc. Recovered with Python -c or apply_patch.
- Call: mcp__awb__setup(project=<project>), immediately after the failed marker-copy script.
  Error, exit 1: No workbench markers here. At the project root, first adapt README.md and AGENTS.md (awb-init SKILL.md, section 3, item 1); otherwise pass the project root.
  This refusal was correct; the prerequisite shell failure was the cause.
- Command: TMPDIR="$PWD/../agent-home/.cache/tmp" git init
  Unexpected stderr still named /var/folders/cr/64mtlg6x6j3_sjjtj19wyfzh0000gn/T/xcrun_db-zDbjPATB and errno=Operation not permitted. Exit was 0 and Git initialized. TMPDIR did not control xcrun's cache.
- Earlier command fragment: git status --short inside an initial shell batch.
  Errors: git: error: couldn't create cache file '/var/folders/cr/64mtlg6x6j3_sjjtj19wyfzh0000gn/T/xcrun_db-R3SK9UWQ' (errno=Operation not permitted); fatal: not a git repository (or any of the parent directories): .git.
  The repository absence was expected; cache permission failure was not.
- Command: python3 -m venv --system-site-packages .venv && .venv/bin/python ../agent-home/.agents/skills/awb-init/scripts/install_helpers.py .
  The venv was created, but installation rejected the README's still-global interpreter.
  Follow-up exact command: .venv/bin/python ../agent-home/.agents/skills/awb-init/scripts/install_helpers.py . --check
  Error: README's Project interpreter is <python-prefix>/bin/python3, not this interpreter (.../project/.venv/bin/python); rerun with it, or edit that line to switch.
  Changed README explicitly and reran successfully.
- Command: .venv/bin/python -m pip install duckdb
  Warning: default pip cache under agent-home/Library/Caches/pip was not writable; cache disabled. Install succeeded.
- Tool: apply_patch, attempted Delete File and Add File for settings.toml in the same patch.
  Error: apply_patch verification failed: invalid patch: multiple operations target .../project/investigations/co2-country-priorities/settings.toml.
  Agent mistake; replaced with a single update.
- Tool: apply_patch, expected a brief sentence as a standalone line.
  Error fragment retained: Failed to find expected lines.
  The sentence was inside a paragraph; removed unrelated hunk and reapplied atomically.
- Tool: records/state finding entity-coverage.
  Warning: entity-coverage: 215 is not a value its table, profile, checks, or settings record; check the number or reword.
  Correct guard: I removed a cross-result scalar from this finding rather than bypassing it.
- Tool: read/sql, query fragment JOIN national n USING(year) following a join that kept g.year and w.year.
  Exact error: sql: read-only: refused a statement whose plan cannot be checked (Binder Error: Ambiguous reference to column name "year" (use: "g.year" or "w.year")); run it without --read-only: Binder Error: Ambiguous reference to column name "year" (use: "g.year" or "w.year").
  Fixed with ON n.year=g.year and kept read-only access.
- Calls: web open https://zenodo.org/records/17417124/files/GCP%20fossilCO2%202025v15.pdf and the same URL with ?download=1.
  Error: (400) Unicode decoding error.
  Recovered using the Zenodo API content URL, urllib download, retained PDF and installed <homebrew>/bin/pdftotext.
- Tool: package/check-draft after Unicode-header exports.
  Exact representative error: chart-1.csv has no column 'Change in annual CO2 (Mt)', which **Data:** names.
  Fixed export display names/Data fields to ASCII while preserving CO₂ in prose.
- Tool: package/check-draft, causal phrase detector.
  Unexpected behavior: flagged the negated phrase containing “attributable to” as causal. Exact complete diagnostic was not retained in notes. Reworded as a statement of timing.
- Command: rg -n '15|headline|read_outline' src/packaging/outline.py
  Error: rg: src/packaging/outline.py: IO error for operation on src/packaging/outline.py: No such file or directory (os error 2).
  Agent guessed the filename; function actually lives in draft.py.
- Regression command: .venv/bin/python -c with temporary copies of findings.md/manifest.json, failing line assert not outline_problems(target), outline_problems(target).
  Error: AssertionError: [{'slide': 'Answer', 'line': 4, 'problem': 'the headline has 21 words; keep it to 15'}].
  The first exception implementation compared original Unicode against normalized text. Applied matching NFKC normalization and reran all cases successfully. This implementation error was mine.
- Tool: functions.exec while appending private notes.
  Error: SyntaxError: Unexpected identifier 'assert'.
  Markdown backticks inside a JavaScript template string terminated it early. Rewrote the string; no shell tool executed in the failed call.
- Reviewer reported a read-only print expression raising NameError for t. Its exact complete command was not provided. It corrected the print; no files changed.
- Broad reads returned 17,385- and 36,108-token outputs with truncation. These were agent query-sizing errors amplified by verbose provenance, not silent data loss.
- No MCP release/write approval rejection occurred. Release completed with released:true, verify:[], storage.status:"copied", compare_trees:[].

## 4. Deviations and judgment calls

- I skipped redundant interview questions already answered by the user, including whether a methods note was wanted, and carried detailed initial facts in a temporary README handoff until scope records could be created.
- I used awb-package for narrative corrections and its explicitly required reviewer agents. I did not proactively delegate the analysis. awb-explore/clean/brainstorm were not necessary merely because the work involved data.
- I customized the project's helper and format documentation for exact authorized headline-length exceptions and unambiguous START-HERE output. This was needed to implement the user's specific wording and prevent regeneration from undoing their correction. I did not weaken number, claim-strength, data, inventory or release-copy checks.
- I used narrow allowed_numbers entries for layout axis bounds and a fixed unit-conversion definition, with history explanations. I did not whitelist computed analytical totals; those went through saved-query result evidence.
- I initially used slash-separated country groups to meet the style constraint and later used only the growth clause in the Answer headline when the user had allowed one idea. Both choices were superseded after the user's feedback. This was poor prioritization of compactness over the donor narrative, not a data disagreement.
- I narrowed the EU per-person reconciliation to the actual latest consumption comparison year after older historical population/rate observations did not align; annual emissions-member checks still span the full historical period. No conclusion rests on the abandoned broad rate check.
- The historical missing-data exercise was explicitly illustrative, not an imputation, estimate, confidence interval or bound. The dataset could not honestly supply a probabilistic error bar. Canonical data stayed unchanged.
- Kosovo was included explicitly despite no ISO; Antarctica and aggregate/historical special series were excluded after checking names. Missing ISO alone was never the filter.
- I used CLI skill installer scripts by path where instructed and MCP for workbench commands; no persistent substitution of CLI for available MCP writes was needed.
- I made no commits, releases before authorization, donor dataset exports, unsolicited messages or upstream refreshes. Release 001 was frozen only after explicit approval and copied to the recorded storage.
- I did not remove the word draft from historical/internal provenance prose. No audience-facing title/subtitle/headline draft markers existed, and verify-only confirmed that. Frozen files were not edited after release.

## 5. Disproportionate time/token use

- Packaging and compliance work consumed more iterations than core numerical analysis: templates, glossary/display mappings, number traces, unit-only result reruns, repeated reviews, manifests, and final reports.
- Repeated full narrative reviews after citation-sized changes were the largest avoidable loop.
- Very large provenance/helper reads caused truncation and rereads. The output budget was spent on repeated metadata rather than decisions.
- The headline word-limit issue generated user corrections plus helper customization and regression checking for a purely editorial request.
- Initial environment/bootstrap consumed extra cycles on temp directories, interpreter mismatch, package cache warnings and markers-before-setup ordering.
- Historical World-accounting research took real time but was justified: it changed an important interpretation and prevented treating World as independent gap filling.
- No elapsed-time or token totals were instrumented, so these are qualitative rankings, not measured percentages.

## 6. What worked well

- Explicit user-facing headline checkpoint and no full draft before approval matched the user's preference. Persistent records made successive corrections coherent.
- Immutable upstream pinning, original-file retention and lossless publication produced a trustworthy foundation. The 50,411-row publication passed 14 checks.
- Saved SQL plus run.py/settings/evidence made findings inspectable and reusable. Source checksums allowed freshness checks despite the no-commit request.
- Country/entity review caught Kosovo and Antarctica correctly. Coverage profiling caught older GDP/consumption endpoints, Libya's missing coal data and early historical gaps before misleading comparisons reached donors.
- The Ukraine follow-up exposed the important distinction between strictly after calendar 2022 and including the large 2022 drop. Separating observation from causal attribution improved the package.
- Retaining primary source documents enabled the World=national sum plus bunkers interpretation and the appropriately qualified sensitivity test.
- Independent review caught a real overstatement about uniqueness checks and missing evidence citations. Its value was genuine even though its repetition was costly.
- Chart export selection and display metadata kept CSV contents aligned with specifications. Release verification checked the actual files against inventory.
- Release was smooth: fresh review passed, verify-only found no draft markers, numbered release and storage copy both verified, and all accepted caveats remained visible.
- The user could make concrete approvals without extra permission loops. Their no-commit and no-audience-dataset preferences persisted.
- awb-status separated completed analysis from PowerPoint assembly and future operational feasibility screening.

## 7. AWB MCP visibility and use

Seven AWB tools were visible through ALL_TOOLS discovery and callable as tools.mcp__awb__* inside functions.exec. I used all seven during the session:

- mcp__awb__setup: workbench helper installation/check workflow; initial prerequisite refusal recovered after markers existed.
- mcp__awb__data: data retention/publication workflow. The saved fetch script itself called land() by path; data acquisition was not misrepresented as an ad hoc download.
- mcp__awb__read: state, questions, help, sql, profile, stale, review-rules, check-draft and status.
- mcp__awb__records: questions, state/finding/issues/next and review-rules maintenance.
- mcp__awb__run: investigation result production, validation and evidence, including the two presentation-unit refreshes.
- mcp__awb__package: export and check-draft.
- mcp__awb__release: release; it automatically copied to recorded storage, so a separate copy-releases call was unnecessary.

The MCP read/write distinction was helpful and generally reliable. All calls supplied the absolute project root. Read-only SQL's misleading retry advice and response verbosity were the main MCP usability defects, not tool availability.
