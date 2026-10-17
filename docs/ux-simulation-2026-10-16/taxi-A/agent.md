# Agent feedback — taxi-A analytics workbench usability session

Written after the conversation ended. This report draws on agent-notes.md, the tool outputs still in context, and feedback/harness-log.md. It separates helper defects, environment restrictions, and my own implementation mistakes. No unresolved operational blocker remained at the end: release 001 was frozen and its external copy verified. Two substantive TLC questions remain intentionally open.

## 1. Ranked pain points and proposed fixes

| Rank | File or tool | Severity | Pain point | Suggested fix |
| --- | --- | --- | --- | --- |
| 1 | awb-package/SKILL.md; references/package-contract.md; project package-format/*; references/review.md | major | Packaging required several long, overlapping instruction layers before a modest headline preview and again for bounded edits. The notes estimate roughly 4,000 tokens for the skill and 4,500 for the contract before templates. Large parallel reads were truncated. Repeated rules about storyline, numerical provenance, review and final checks were hard to keep distinct. | Provide a short task router for preview, full draft, wording-only revision, chart revision and release. Put invariant rules in one canonical file and link specific sections. Supply a compact command/checklist reference and a structured package context read. |
| 2 | awb/read check-draft; number matching; manifest allowed_numbers | major | Valid paired quantities such as 54.8/57.6 were interpreted as unsupported compound numbers. Dates, identifier codes, clock times and exact assertion tolerances also needed formatting changes or allowances. This created several failed preflights and a substantial methodology rewrite without changing any analysis. | Tokenize slash-separated numeric pairs and time expressions correctly; distinguish identifiers, dates, validation tolerances and measured quantities. Return the matching source/precision when possible. Offer a dedicated diagnostic explaining how a token was classified rather than making the writer infer the parser. |
| 3 | awb/setup; awb-init installer; README Project interpreter | major | Initial setup selected <python-prefix>/bin/python3, which lacked DuckDB, although the project needed an isolated environment. The setup tool offered no interpreter argument, so a CLI installer invocation was necessary to select the new .venv. | Accept an explicit interpreter or create/select a project-local environment before installing. Report the selected interpreter and missing requirements before recording it. Later setup correctly reused .venv. |
| 4 | settings.toml views; awb/run and awb/read stale | major | views accepted logical view names instead of definition paths. Results could run and pass runtime checks, yet stale later reported missing evidence and attempted a nonexistent project/yellow_trips path. | Validate views entries as files at settings load/run time, or expose separate typed fields for view names and definition paths. Include a complete working example. Fail before computation if provenance cannot be recorded. |
| 5 | package-format/findings-template.md; awb-package review; my slide drafting | major | The draft passed formal checks and an independent review while Q3's hour/borough answer remained only in speaker notes. The user also caught awkward grammar, unexplained occupied hours, excessive currency precision and an unreadable arrow-heavy exclusions headline. These were my presentation misses; mechanical completeness did not establish board usefulness. | Add a semantic checklist mapping each required question's dimensions to visible slide content. Review audience vocabulary and numerical precision explicitly. Use pickup borough rather than implying rider residence, and distinguish readability review from provenance review. |
| 6 | awb-package/references/review.md; awb-release/SKILL.md | minor | Every packaging repair required another fresh full review to finish; release required another full review even immediately after an unchanged approved draft. Parent-managed snapshots and inherited unrestricted tool access added coordination work. The review did catch two real missing citations, so it had value. | Have the helper retain review inputs, hashes and reports automatically. Consider accepting a current full review when all narratives, rules, flags and claim records match a recorded fingerprint, with a new release-time rule/staleness check. Provide a read-only reviewer capability where supported. |
| 7 | awb-init and awb-scope workflow; pending intake records | minor | Init requires the initial scope interview before an investigation exists, even with a rich initial user prompt. There was no standard durable pending-interview location; I improvised an intake section in README. | Support an intake/pending-scope record or provisional investigation status. Separate decisions truly needed from definitions the analyst can propose with concrete defaults. |
| 8 | awb-clean scan/clean-record; foundation/quality.md | minor | Raw and canonical manifestations of the same issue generated many separate quality rows, making the quality ledger large relative to the work. | Allow one issue to reference several scan observations/views and distinguish a recurring issue from a new manifestation. Keep detailed scan facts accessible without duplicating the decision narrative. |
| 9 | awb-package preview; awb/status; manifest lifecycle | minor | A correct preview-and-wait artifact is intentionally incomplete and cannot pass final checks. There was no formal preview state/artifact, and preview-plan.md had to be moved outside the finished draft. | Add a defined preview artifact and status, with lightweight checks for titles, order, required questions and slide count. Show awaiting-headline-approval explicitly in status without implying a broken package. |
| 10 | awb/package export and awb/read check-draft | minor | The first export wrote files and then returned exit 1 for missing chart specifications. Read-only checks after edits also returned errors solely because the previous inventory was stale. Both are understandable but look like failed operations to tooling telemetry. | Document write-on-validation-failure clearly, or preflight specifications before mutation. Separate content validation from inventory verification in output and distinguish expected “needs final inventory refresh” from a substantive error. |
| 11 | workbench-guides/data.md; retained source references; TLC PDF retrieval | major | The official dictionary PDF download was blocked with HTTP 403. The later web-readable dictionary was not contemporaneous with 2024, so retaining a literal PDF and confirming historical Vendor 6 identity were impossible from the available primary material. | Explicitly support a retained access/assessment note with URL, revision, access date, quoted/paraphrased fields and unresolved historical applicability when the original cannot be retained. Do not equate a current vendor mapping with a historical one. |
| 12 | restricted shell environment; setup/git/pip behavior | minor | zsh heredocs could not create temporary files; Apple git emitted xcrun cache-path permission warnings even after TMPDIR was changed; pip disabled caching outside writable roots. These were host/environment problems rather than workbench logic. | Provision a writable shell/tool cache location or document the restriction upfront. Prefer patch tools or properly escaped python -c for file edits in this environment. |
| 13 | foundation/sources.md Notes syntax; awb/status source-reference parsing | minor | A Markdown note field carried relatively strict machine-readable reference syntax, and status semantics around “state_status” were ambiguous at date precision. | Give reference fields a structured representation or validate them when written. Use timestamps/commit or checksum relationships rather than same-date ambiguity when reporting whether state is committed. |
| 14 | workbench-guides/analysis.md; investigation-local shared producers | minor | The guide explained producer modules but not the shared import pattern. I had to choose importlib loading and explicitly enumerate imported files in settings.code. Parallel aggregate reductions also changed floating-point tails across runs. | Ship a small shared-producer example and document code dependency declaration. Document deterministic aggregation options or compare floating results with a declared tolerance rather than implying every tail difference changes the conclusion. |

Severity reflects the cost during this session, not a claim that every user would be blocked. Several items were recovered before the next user response.

## 2. Contradictory, ambiguous, lengthy or missing instructions

- **Read-only status versus a mixed user request:** awb-status says to stay read-only and suggest fixes, while the user also explicitly requested a holiday caveat edit. I honored the authorized narrow edit through records, then ran read-only status. Add an explicit mixed-request example so the skill does not encourage an unnecessary permission loop.
- **MCP preference versus interpreter selection:** AGENTS.md prefers awb MCP for setup, but setup lacked an interpreter selector. CLI fallback was necessary despite the MCP tool itself being available.
- **Runner examples:** analysis.md shows direct investigation run.py invocations, whereas AGENTS.md routes those through awb/run. Project precedence resolved this, but examples should use the same entry point or say they describe the underlying command.
- **Preview mode precedence:** a supplied storyline/full-draft request can select draft-then-review, while the brief records preview-and-wait. The user's explicit preview request won initially; after approval and an explicit full-draft instruction, no second preview pause was needed. This was workable but spread across multiple paragraphs.
- **Ledger order versus decision-first storytelling:** the default order is question-led, but the board wanted airport/tipping decisions first. I proposed the difference and recorded the approved presentation_order. The approved-order escape hatch is essential; give it a concise example.
- **Question priority versus decision gating:** making Vendor 6 a must-priority question made it required on the Open questions slide. It did not mean airport funding must wait for that answer. I recorded this distinction. The skill should state that presentation requirement and decision gate are different concepts.
- **Roots/count footer:** the user started with five study questions, but the later Vendor 6 question became a sixth root. Generic counts could falsely imply an original study answer was missing. Status should distinguish original study questions from newly added stakeholder/context roots.
- **Strict completed-check citations:** review.md requires every completed-check assertion to cite evidence, including source duplicate scans and an OPM date verification. The first reviewer caught missing citations. Clarify explicitly how foundation scans and external source-verification notes satisfy this rule; not every check is an analytical run.py result.
- **“With tolerance” versus board language:** the reviewer instructions ask audience verification claims to include tolerance. The user understandably rejected “with zero-record tolerance.” “Exactly” preserves the accounting meaning in plain language. Add this as an approved example.
- **Package versus assembled deck:** the skill produces a Markdown outline, chart inputs and Copilot assembly instructions, not a PPTX. START-HERE was clear and the user read it, but capability/deliverable names should stay explicit. Likewise a roughly 400-word Markdown note is one-page text, not a verified paginated PDF.
- **Review rules versus one-off edits:** deciding which corrections generalize requires judgment. I saved stable tip framing, definitions, visible dimension coverage and zone display as rules; local grammar/headline wording stayed local. Provide examples to discourage turning every edit into a permanent rule.
- **Reporting burden:** awb-package's report requirements ask for every chart's source, rule IDs, slide counts, datasets, caveats and provenance details even on small revisions. awb-release asks to repeat every limitations/open-question entry. This lengthened the final chat beyond the user's simple request for a location. Prefer a compact receipt plus a linked complete report, while surfacing material unresolved decisions directly.
- **No invented approval gates:** existing authorization was sufficient for retaining supplied files, cleaning under approved rules, committing as I went and final release. I did not request approval again simply because a skill mentioned confirmations generically.

## 3. Failures and unexpected outputs

Exact invocations below are reproduced where preserved in the private log/current context. For older long multiline calls whose full argument text was not preserved in agent-notes.md, I identify the exact tool/command fragment and error rather than invent the missing body. The notes point to the original tool transcript for those full calls.

### Environment and shell

1. Command: `ls -la && git status --short && git rev-parse --show-toplevel`
   Error/exit: 128, `fatal: not a git repository (or any of the parent directories): .git`.
   Git also printed `couldn’t create cache file /var/folders/cr/64mtlg6x6j3_sjjtj19wyfzh0000gn/T/xcrun_db-6sR9v82e (errno=Operation not permitted)`.
   Resolution: initialized the repository when authorized workflow required it. The absent repository was expected initial state, not data loss.

2. Command: `TMPDIR="$PWD/.tmp" git init`
   Outcome: succeeded, but still printed the Apple xcrun cache permission warning. TMPDIR did not redirect that cache.

3. Command: `git status --short && git log -1 --oneline`
   Error/exit: 128, `fatal: your current branch main does not have any commits yet` (the notes omit the original quoting of main).
   Resolution: created the initial preservation commit; Git itself worked.

4. Commands began `python3 - <<'PY'` for an ancestor-instruction scan and later a multiline methodology/manifest repair.
   Exact error: `zsh:1: can't create temp file for here document: operation not permitted`.
   Resolution: correctly shell-escaped python3 -c. The long original Python bodies are not reconstructed here.

5. Command: `.venv/bin/python -m pip install duckdb`.
   Outcome: succeeded; pip warned that agent-home/Library/Caches/pip was not writable and disabled caching. No global package installation.

6. Request performed with Python urllib.request.urlopen, timeout=30:
   `https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf`
   Error: `urllib.error.HTTPError: HTTP Error 403: Forbidden`.
   Resolution: official PDF text was readable through web tools; retained a labeled assessment, not a fabricated PDF download. Historical documentation applicability remains a caveat.

### Analytical setup and guards

7. Tool: `mcp__awb__run`, first cleaning/sensitivity production.
   Error: `median_tip_pct null rate 0.143 exceeds 0.000 (+1 more)`.
   Cause: Vendor 6 has no eligible card trips, so its tip metric is undefined.
   Resolution: conditional null assertion tied to a zero valid-tip denominator; no zero imputation.

8. Tool: `mcp__awb__read(command="stale")`.
   Diagnostics: `missing evidence: yellow_trips: missing sha256` and ENOENT for `<project>/yellow_trips`.
   Cause: settings.views contained names rather than definition paths.
   Resolution: use foundation/views/01_taxi_zones.sql and foundation/views/02_yellow_trips.sql; rerun/revalidate; stale count zero.

9. Tool: apply_patch, a scope/documentation multi-file edit.
   Error fragment: `apply_patch verification failed: Failed to find expected lines ... Historical vendor names have not been verified.`
   Cause: I matched a whole line that was actually inside a paragraph.
   Resolution: confirmed atomic refusal and used precise replacements. A following rg command returned 1 for no matches, so its chained cat did not run.

10. Tool: functions.exec, a loop promoting findings.
    Error: `TypeError: text is not a function`.
    Cause: I shadowed the global text() helper with a destructured variable named text. The first awaited records mutation had already succeeded.
    Resolution: renamed the variable to wording and safely retried; helper reported unchanged for the already-completed mutation.

11. Tools: awb/records question answers linking Q-008 and Q-006 to zone-ranking.
    Refusal excerpt: `[results.zone-ranking] does not declare answers = ["Q-008"] ... add it there first`, with the analogous Q-006 refusal.
    Resolution: declared the answer relationships, then linked the existing recorded result without unnecessary computation. This was a useful guard, not a defective tool.

12. Repeated DuckDB analyses produced tiny floating-tail changes in sums/means despite identical definitions.
    Resolution: investigation-local threads=1, reran affected requested analyses and verified repeat results were kept. No analytical scope change.

### Packaging and checking

13. Tool: apply_patch, one patch deleting and adding findings.md at the same target.
    Error fragment: `invalid patch: multiple operations target ...findings.md`.
    Resolution: separate operations; no partial change.

14. Tool: awb/package export, first full-draft export.
    Outcome: wrote chart files/manifest and returned exit 1 for six missing chart specifications.
    Resolution: completed specifications and re-exported. All six export provenance checks subsequently passed.

15. Exact later read-only preflight:
    `mcp__awb__read({"project":"<absolute project root>","command":"check-draft","investigation":"taxi-trip-patterns","package":"board-decisions"})`.
    Initial number diagnostics included `264/265`, `54.8/57.6`, `18:00`, `0.00000001 percentage points`, and nonrepresented source-profile counts.
    Resolution: separated numeric pairs, used recognized time wording, removed unnecessary unrepresented quantities and supplied narrowly justified identifier/tolerance allowances.

16. Same preflight after bounded revision:
    exit 1 solely for old recorded inventory sizes/checksums of charts/chart-1.csv, charts/chart-4.csv and the three edited narratives.
    There were no number, chart, claim, heading, storyline or question problems.
    Resolution: final writing awb/package check-draft refreshed inventory and passed true. These were expected intermediate verification failures, not transport/permission failures.

17. awb/package export repeatedly emitted a label_warnings entry because source_month used the shared display name Month across airport-comparison, tipping-patterns, trip-volume, zone-ranking and quality-counts.
    Resolution: confirmed the shared source-file-month meaning in methodology. This is a useful prompt, but repeated “confirm” warnings have no recorded resolved state.

18. Reportlab availability probe was false. This was not a failed dependency install; I did not install it. Audience note remained Markdown under the package contract.

### Telemetry interpretation

harness-log.md reports two failed records calls during analysis, five failed MCP calls during the first full package turn, and one failed read call during the revision turn. Those align with deliberate guard refusals and preflight exit statuses above; they should not be read as six/several MCP transport outages. The final release had zero failed MCP calls. A distinct result category for validation failure would improve usability metrics.

## 4. Deviations and judgment calls

- Used the installer CLI once despite an available setup MCP tool, to bind the workbench to a project-local interpreter. Subsequent usable MCP tools remained in use.
- Used a retained documentation assessment instead of a retained literal PDF because retrieval was blocked. Recorded the revision/access gap and did not map a later vendor identity to 2024 as a confirmed fact.
- Stored pending scope intake in README because there was no provisional investigation record template.
- Landed only explicitly supplied originals during initial setup, interpreting the user-provided preservation instruction as authorization despite the general init-to-preparation boundary.
- Performed the separately requested holiday caveat edit alongside a read-only status request. User authorization took precedence; no trip analysis or holiday-effect estimate was added.
- Did not run an EDA scan merely because awb-explore existed. The user authorized computation of defined questions, so saved queries/run.py and validation were the appropriate workflow.
- Added labeled code-99 diagnostics when primary borough patterns were surprising. These were within the tipping question; they did not silently change primary eligibility or establish missingness/passenger intent.
- Used 1,000 trips per zone/month and per sensitivity scenario exactly as approved; the old unrestricted ranking finding was superseded, not erased.
- Used pickup borough and slightly more precise rounded ranges (Manhattan 26–27%, early evening 27–28%) instead of literal suggested rider wording. Explained this, preserving the actual monthly estimates.
- Changed audience comparator label to Other trips but retained confirmed-non-airport membership and unknown-location caveats.
- Used fresh read-only subagents only when package/release review explicitly required them. Codex tool access cannot be technically narrowed here; reviewer briefs prohibited writes. Parent created required snapshots outside the Git-ignored draft.
- Did not force-add delivery artifacts to Git, regenerate analytical provenance to make it look committed, assemble a nonexistent PPTX, contact TLC, or release before the explicit delivery instruction.
- Some instruction/guide reads were repeated unnecessarily, and I initially formatted too many methodology pairs with slashes. Those were my efficiency mistakes rather than required deviations.

## 5. Disproportionate time and token use

The relay log reports 59 minutes across nine user messages and eight agent replies. Approximate agent-turn wall times were 3.2 minutes for initialization, 9.6 for scope/cleaning, 14.4 for analysis, 1.7 for status/caveat, 5.7 for preview, 16.6 for full packaging, 3.7 for final wording changes and 2.1 for release. These are elapsed times from harness events, not measured attribution of every second to a skill.

- Full packaging was the longest turn, exceeding primary analysis. Long instructions, detailed authoritative methodology, six export specifications, number-token repairs, strict completed-check citations, snapshot management and a second full review dominated that stage.
- The 5.7-minute headline preview was expensive for a small visible artifact. A lightweight preview path would have saved reads and scaffolding.
- Cleaning used 48 MCP calls, analysis 30, and full packaging 17 in the relay log. Many were useful declarative checks, but help/schema reads, state/ledger mutations and quality issue maintenance added substantial orchestration.
- Repeated long file reads in parallel caused output truncation and follow-up reads. Smaller structured context outputs would be better than simply raising token limits.
- Mandatory final reports repeated caveats and metadata the user had already accepted. The last user mainly wanted an exact storage path, yet skill reporting rules required a much longer reply.
- Investigation-local shared producer plumbing, deterministic floating aggregation and source-reference/provenance repairs were necessary infrastructure costs before substantive conclusions.
- No repeated full raw-data scans or analysis reruns were done merely for packaging. No new analysis was run for the holiday caveat. Those boundaries saved work.

## 6. What worked well

- The workbench separated preserved originals, canonical source-record views, investigation eligibility, recorded results, audience packaging and frozen releases. This prevented silent deletion or recoding.
- Exact record identity and overlapping reason accounting made exclusions auditable by month and provider. Conditional null validation handled the small provider without inventing tip zeros.
- The user supplied strong decision context and answered method questions together. Persistent authorization avoided repeated confirmations.
- Reproducible saved queries/producers, per-result evidence, settings and stale checks gave concrete provenance. Guards prevented linking undeclared answers and serializing stale chart evidence.
- The code-99 concentration was discovered, retained and explained as an association. The board learned why borough tipping patterns could not safely support a fairness/behavior inference.
- Three-state airport classification prevented unknown geography from being silently treated as non-airport. The monthly 1,000-trip floor made zone rankings board-appropriate.
- The first independent package reviewer found missing duplicate-scan and holiday-verification citations that mechanical checks could not. Later fresh reviews passed all active rules.
- Export regenerates chart files from saved results with explicit labels, filtering and rounding. Changing whole-dollar display did not change analytical ranks or eligibility.
- Preview-and-wait respected the user's requested checkpoint. After approval, routine corrections proceeded without reopening settled scope or asking again about datasets/methods-note needs.
- Durable review rules captured repeated presentation errors. The user corrected readability rather than needing to reopen the analysis.
- START-HERE clearly separated audience deliverables, builder inputs and internal material. The final frozen package contains the approved outline, chart inputs and note; it does not falsely claim an assembled deck.
- Release numbering, local verification, external storage copying and compare_trees all worked in one helper call. Release 001 reached storage/releases/taxi-trip-patterns/board-decisions/001 with no differences, provenance gaps or checkout-only acquisitions.
- As-I-go commits preserved analytical and record changes. Frozen release files were not edited afterward.

## 7. awb MCP visibility and actual use

All seven tools were visible through ALL_TOOLS and callable as tools.mcp__awb__* inside functions.exec:

| Tool | Used? | Session use |
| --- | --- | --- |
| mcp__awb__setup | Yes | Install/check workbench helpers and later package formats; initial interpreter selection required one CLI fallback. |
| mcp__awb__read | Yes | state, questions, help, sql/profile during analysis, stale, status, review-rules in reviewer agents, and read-only check-draft. |
| mcp__awb__data | Yes | land, retain, publish, source/canonical cleaning scans and data preparation operations. |
| mcp__awb__records | Yes | Question creation/answers/editing, findings/caveats/next steps, cleaning decisions and review-rule creation. |
| mcp__awb__run | Yes | Run the investigation's result producers and record validation/evidence. |
| mcp__awb__package | Yes | Export charts/provenance and perform final writing check-draft. |
| mcp__awb__release | Yes | release taxi-trip-patterns board-decisions; the helper copied to the already-recorded storage root. A separate copy-releases call was unnecessary. |

The MCP server did not need registration or user action. No write tool was unavailable or auto-review rejected. Validation refusals were resolved through the supported workflow. CLI/shell use was for interpreter repair, ordinary file editing/reading, dependency setup and Git, not a general bypass of working awb tools.
