# Agent feedback: CO₂ donor-roundtable workbench

The investigation and release completed successfully. Five business questions were answered and accepted, the donor package was revised after headline review, and release 001 and its external copy verified. No blocker remained. This assessment draws on agent-notes.md; quoted commands and errors below are the strings preserved there, with incomplete historical command arguments identified rather than reconstructed.

## 1. Ranked pain points and suggested fixes

1. **Major — package number checking and presentation-unit conversion.** `awb-package` / `awb.py check-draft` could trace literal quantities but did not infer that a change recorded in million tonnes supports an approximate billion-tonne sentence. The final cosmetic rounding request required a new `territorial-change-tonnes` result, run.py integration, seven validations, evidence, a finding, and additional manifest provenance. Earlier, the same issue caused removal of an optional global-denominator amount expressed in billion tonnes. Suggested fix: give results explicit units and support declared presentation transforms, including scale, rounding and approximate wording, in narrative number checking. Keep transformations auditable without making them new analytical findings.

2. **Major — cumulative instruction and template load.** `awb-init/SKILL.md`, `awb-scope/SKILL.md`, `awb-package/SKILL.md`, package-contract.md, review.md, helpers.md, project AGENTS.md, guides, and installed templates form a long dependency chain. Several combined reads were truncated and required focused rereads. The material is useful, but initialization, headline-only preview, full packaging and a small revision each carry considerable reading overhead. Suggested fix: publish a compact workflow index with task-specific required reads, short command examples and an explicit “already read this session” checklist. Keep reference material separate from mandatory procedure.

3. **Major — deck delivery expectation versus actual package artifact.** `awb-package` produces a slide manuscript, CSV chart sources, methodology and Microsoft 365 PowerPoint-agent assembly instructions, rather than a rendered presentation. This was made explicit and the user accepted START-HERE, so it did not block this task. Nevertheless, “prepare a deck” can reasonably imply an inspectable PPTX/PDF. Suggested fix: state this boundary at the skill's entry, distinguish manuscript completion from presentation assembly, and optionally provide a supported renderer plus visual checks.

4. **Minor — MCP schema and implementation mismatch.** `mcp__awb__read` exposed a shared `settings` field, but `profile` rejected it. The schema documentation was easy to interpret as supporting investigation-aware profiling. Suggested fix: implement settings for profile or make command-specific support explicit in both the field description and tool schema; ideally use separate input variants per command.

5. **Minor — name checker false positive.** `check-draft` treated ordinary donor prose “coal-share” as leakage of the internal result ID `coal-share`. Suggested fix: recognize identifier formatting or context, or allow narrowly recorded lexical exceptions; do not reject an ordinary phrase solely because it matches a result slug.

6. **Minor — scope interview before any investigation records.** `awb-init` → `awb-scope` required the first interview before investigation records, despite an unusually detailed initial brief. The supplied business question and five exact questions had to be held temporarily in README's Scoping handoff. Suggested fix: permit an intake brief and draft ledger before unresolved choices are settled, clearly marking only those choices as pending. Ask only for material missing decisions.

7. **Minor — preflight errors mix expected draft lifecycle with actual defects.** Read-only `check-draft` returned failure for absent inventory/review before the writing check, alongside substantive narrative issues. After edits, stale inventory/review are expected but still create noisy failing reports. Suggested fix: provide a preflight mode that separates expected lifecycle tasks from content defects and prints the exact next command.

8. **Minor — timestamp-based status noise.** The status collector called state out of date because history was one second newer, although all evidence was current. Suggested fix: separate narrative timestamps from evidence freshness and say what semantic change requires action. The targeted stale check was the more useful signal.

9. **Minor — manually completed acquisition metadata.** Landing/retention helpers generated useful register rows, but Restrictions needed manual completion and acquisition prose could remain phrased as planned after acquisition was complete. Suggested fix: accept restrictions explicitly and update lifecycle wording atomically when acquisition/retention succeeds.

10. **Minor — sandbox temporary-file behavior.** Shell heredocs failed because zsh could not create a temporary file; macOS Git/xcrun and pip also attempted unwritable cache locations. This was environmental, not an awb defect. Suggested fix: document a writable task TMPDIR/cache configuration during setup and prefer apply_patch or Python -c examples for small scripts in restricted environments.

## 2. Contradictory, ambiguous, long or missing instructions

- **Concrete inconsistency:** the read tool's shared settings input and profile's rejection, described above.
- **Ambiguous boundary:** whether a simple presentation-unit conversion is an analytical result or export shaping. The numeric checker effectively forced new analysis records for a cosmetic wording change. The skills should define the permitted transformation contract.
- **Ambiguous initial intake:** a business question may already be fully specified, yet the init-to-scope interview sequence assumes there is enough unknown to delay creating records. A satisfied-by-existing-context branch would help.
- **Length:** package instructions plus templates repeat contract details across multiple files. Targeted rereading was necessary after output truncation. A compact authoritative checklist would reduce both omissions and redundant reading.
- **Slide-count pressure:** required title, Answer, five question slides, methods and limitations produced nine content slides against “about eight.” We proposed eight main slides plus a limitations appendix and explicitly disclosed the standard divider, yielding ten assembled slides. The user approved. A documented rule for approximate counts and optional appendix placement would simplify this choice.
- **Missing early expectation:** the package workflow's lack of a rendering step should be explicit before the user expects a finished presentation.
- **Overly fine editorial constraint:** a reviewer rejected a donor-methods statement about consistency within source rounding because tolerance explanations belonged in internal methodology or notes. This was resolved, but that constraint is easy to miss in the lengthy package contract.
- **No unresolved authorization contradiction:** the user declined permanent review rules for one-off edits, so none were created or requested. Release occurred only after explicit delivery authorization. Mandatory fresh reviewer agents were permitted by the package skill despite the general restriction on unsolicited delegation.

## 3. Failed commands and unexpected behavior

The following are recorded failures or unexpected outputs, not all workbench defects:

- `python3 - <<'PY'` during ancestor-instruction inspection failed: `zsh:1: can't create temp file for here document: operation not permitted`. Retried with Python -c successfully.
- `.venv/bin/python - <<'PY'` during the release turn, with a README-update/private-log script, failed before Python ran: `zsh:1: can't create temp file for here document: operation not permitted` (exit 1). Replaced with apply_patch. The release had already succeeded and was unaffected.
- `ls -la; git status --short; git rev-parse --show-toplevel; python3 --version` in the initially empty project produced `error: couldn't create cache file /var/folders/cr/64mtlg6x6j3_sjjtj19wyfzh0000gn/T/xcrun_db-Se87hg2O (errno=Operation not permitted)` and an analogous warning, plus `fatal: not a git repository (or any of the parent directories): .git`.
- `mkdir -p ../agent-home/.cache/tmp && TMPDIR="$PWD/../agent-home/.cache/tmp" git init && python3 -m venv .venv && .venv/bin/python -m pip install duckdb pandas` succeeded, but Git still printed the xcrun cache warning. Pip disabled its default cache because it was not writable. These warnings did not invalidate setup.
- `pwd && rg --files -g AGENTS.md ... .` returned exit 1 in the initially empty project. The ellipsis here reflects the abbreviated command recorded in the notes. It was a normal no-match result.
- `apply_patch` for `queries/historical-shares-audit.sql` used an incorrect bare WHERE context: `apply_patch verification failed: Failed to find expected lines in .../queries/historical-shares-audit.sql: WHERE`. No file changed; read the actual context and corrected the patch.
- `mcp__awb__read` with `command="profile"`, `settings="emissions-and-country-focus"`, `query="country_data"` returned `unknown arguments: settings` (`isError: true`). Retried a foundation-view SELECT with the equivalent explicit eligibility filter.
- `state finding coverage` warned: `2023 is not a value its table, profile, checks, or settings record; check the number or reword`. The 2023 evidence belonged to a separate consumption result. Narrowed the coverage finding to the years its own result recorded. Full original argument text was not retained in the notes.
- Initial read-only `check-draft` preflight reported `manifest: manifest.json records no inventory list; run check-draft without --verify-only`, as expected before finalization. It also flagged “coal-share,” an unrecognized billion-tonne conversion, and the 500-word note target. Fixed the prose/unit issue; recorded the note-length target with the brief as its authority.
- The first `mcp__awb__package` export attempt during precision edits returned `args must be an array of strings`. I had incorrectly treated manifest results as a list of IDs, although it is a list of objects containing result_id. Extracted the IDs and reran successfully. This was an agent input error, not a tool implementation failure; the refused call wrote nothing. Full attempted array was not preserved in the notes.
- Large combined file reads exceeded output budgets multiple times. Focused reads resolved the truncation.

## 4. Deviations and judgment calls

- No shipped helpers or package-format templates were customized. No raw data values or shared canonical observations were corrected merely to simplify the investigation. No accepted analytical results were unnecessarily rerun.
- Preserved the complete source, including aggregates and land-use columns, while applying the user's country and no-land-use scope in investigation views. This follows the shared-foundation boundary rather than interpreting the scope as permission to delete columns.
- Retained the initial brief temporarily in README instead of creating unapproved investigation records before the first scope interview. This was a workaround for sequencing, not a change to the business question.
- Treated “largest” in Q2 as endpoint annual emissions and documented it without interrupting data ingestion for another question. The user later accepted the resulting analysis and chart cohort.
- Did not ask again whether the user wanted a methodology note, no supporting tables, or permanent rounding rules: those preferences were already explicit.
- Excluded special historical Ryukyu series alongside other non-country records and explicitly included Kosovo after checking ISO completeness. Did not assume that no ISO code meant aggregate.
- Proposed eight main slides plus an appendix rather than silently dropping a required element; received approval before full drafting.
- Avoided exempting an analytical number through allowed_numbers. Instead, added a unit-only recorded result for the billion-tonne narrative. That preserved provenance, but at disproportionate cost.
- Used direct apply_patch for documentation after shell temporary-file failures. Frozen release contents were never edited.

## 5. Disproportionate time and token costs

- Repeated instruction/template reads and recovery from truncated output consumed substantial context relative to the small number of substantive statistical questions.
- Cosmetic precision changes required updates to slide prose, alt text, chart export overrides, internal methodology, audience note, brief precision, manifest provenance, a unit-conversion result, fresh review and inventory. Some synchronization is valuable; introducing a new finding for a scale conversion is excessive.
- The first full package needed a full review, a small note wording repair, and a fresh scoped review. This enforced the receipt contract correctly, but the editorial constraint was small relative to the review machinery.
- Packaging also required a separately recorded combined US/EU share for a derived headline. That was defensible, but a reusable derived-expression provenance mechanism could handle sums of accepted results more cheaply.
- Actual computations, data ingestion and release copying were comparatively smooth. There are no reliable timing measurements in the notes, so these are qualitative assessments rather than measured durations.

## 6. What worked well

- Skills kept preparation, local filtering, analysis, packaging and frozen releases distinct. The originals and all source columns were preserved; country eligibility stayed auditable and investigation-specific.
- Landing recorded hashes and upstream validators; retention independently verified originals; publication enforced 16 checks on 50,411 rows and 79 columns. Publication output supplied usable catalog/view text.
- The eligibility audit caught Kosovo and classified all exclusions. The EU-27 reconciliation and historical coverage checks found substantive issues that mattered to the donor explanation.
- Parallel Q2 definitions preserved the accepted 45 while adding the user's meaningful 5% threshold, producing 38 on the same cohort rather than silently replacing the original result.
- Evidence and finding checks prevented cross-result number leakage. Missing early China/India observations were disclosed, not imputed away. Primary OWID documentation resolved international aviation/shipping semantics.
- Preview-and-wait matched the user's requested workflow. The user changed chart design before the full draft, avoiding unnecessary rework.
- Package-local --round overrides supported one-off precision without changing shared defaults. Unchanged Q2/coal chart bytes were verified.
- Fresh read-only reviewers and review receipts gave a clear audit trail. The final check verified twelve inventory rows and a current review; release reused the current receipt rather than ordering redundant review.
- `release` froze a numbered package and independently compared the external storage copy. It returned a full path, complete carried caveat list, and explicit empty provenance-gap/checkout-only-acquisition lists. This made the final report straightforward.
- The project respected Commits: on request and never committed without authorization. Release was not confused with sending messages or publishing to third parties.

## MCP visibility and usage

Visible awb tools were `mcp__awb__read`, `mcp__awb__records`, `mcp__awb__data`, `mcp__awb__run`, `mcp__awb__setup`, `mcp__awb__package`, and `mcp__awb__release`. All seven were used during the session: setup/install checks; state/help/status/questions/SQL/profile/stale/review/check reads; question/finding/next-step records; landing/retention/publication/cleaning data operations; investigation result runs; chart exports/review receipts/final package checks; and release creation with verified external storage. I used absolute project roots and the declared project interpreter for CLI fallbacks. No awb write tool required a CLI fallback because of refusal or unavailability. The profile settings mismatch was handled through a supported read query.
