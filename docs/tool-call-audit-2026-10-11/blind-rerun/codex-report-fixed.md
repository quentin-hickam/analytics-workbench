# Workbench exercise report

Completed requests 1–16 in order in `work/returns`. No network, push, sub-agents, or helper-source debugging was used. All requested commits were made locally. Active investigation is now `channel-returns`; its new setup is uncommitted because request 16 did not request a commit.

## 1 — Initialize and commit

Applied awb-init. Inspected the sandbox/target, copied root orientation, instructions and ignore rules, installed helpers/guides/dependencies, and populated region-returns brief, state, history, runner and settings. Created the candidate ERP source register and glossary. Scoped all H1 2026 orders, all channels, order-recorded region; pilot decision, leadership audience and 3-point threshold recorded. Data/cache/delivery directories were deferred. Commit `b97c6c3`.

Failures/recovery: `ls -la work/returns` reported “No such file or directory”; `git status --short` at sandbox root reported “not a git repository”. Created the target and initialized its local repository. The first `install_helpers.py work/returns` returned exit 1 with `"workbench": false`; installing README/AGENTS/.gitignore first satisfied detection and the next installation succeeded. No package/dependency attention items remained.

Choices/lookups: read awb-init assets and installed guides, without opening Python source. Interpreted “the rest” as non-West orders pooled, with individual comparisons as sensitivity; selected Wilson intervals. Assumptions were logged and recorded. No host instruction file existed inside the permitted ancestors. Ancestors outside the sandbox were not inspected, per the brief.

## 2 — Land one acquisition

Read the data guide. Recorded supplied raw retention location, ran retain, and landed both ERP files as `erp/extract-2026-07-01`. Landing reported 2 files, 118915 bytes, copied/matched retention, no discrepancies; the helper added the acquisition and marked the source acquired. Filled “Internal; no customer PII” restrictions. Inspected only landed records, using awb.py profile: 2412 order rows, 2400 distinct order IDs, 400 unique customers.

Failures: none. Lookups: command help for profile/sql/publish; landed profile samples established Y/N returns, region variants and source schema. The extraction identifier dates the source export, while provenance records the actual landing time in October; these are distinct.

## 3 — Publish, expose, catalog and commit

Saved conversion SELECTs and failure-returning checks for both datasets. Committed conversion code first (`7674964`) so publications identify committed conversion code. Published orders (2412 rows) and customers (400 rows), both validated, under publication ID `extract-2026-07-01`. Created Git-managed canonical views and completed the catalog. Commit `9031ec2`.

Failures: none. Lookups: the publish helper’s printed view_sql/catalog_row supplied the view/publication paths. Order labels/dates and Y/N indicators remained raw until cleaning. The initially drafted integer cast for returned was corrected to preserve Y/N before execution, based on the landed profile; no failed publication occurred. No custom convert callable or landing-reference read was needed.

## 4 — Clean and commit

Applied awb-clean to orders, order_id grain, customer reference and H1 date range. Classified all 13 issues: shared rules Q-001–Q-011, real large values accepted as Q-012, and partial-customer orphans open as Q-013. Used supplied answers to drop duplicate copies, null -999 amounts, keep large amounts/orphans and parse slash dates month/day/year. Read correction-views reference, corrected the canonical view, rescanned, ran stale, and recorded quality/catalog in the helper. No findings existed to flag; no analysis rerun. Commit `e6490f5`.

Failures/recovery: attempted `--range returned=Y:N`; scanner returned exit 2, `"ValueError: --range returned=Y:N: bounds are numbers or ISO dates"`. Removed this categorical range. First record_cleaning refused with `"RecordError: foundation/catalog.md: several rows are named orders"`, writing nothing. Renamed publication rows `orders-publication` and `customers-publication`, kept canonical names, and reran recording successfully.

Instruction/tool mismatch: the data guide/publish output gave the publication and canonical view the same catalog name, but record_cleaning requires a unique name. Distinct publication names reconcile them without changing dataset/view identities. Internal-source restrictions were retained; no prohibition on local quality examples or local commits was stated.

Rescan delta lines, verbatim:

- S1 duplicate-rows: 12 -> 0 resolved
- S2 duplicate-key:order_id: 12 -> 0 resolved
- S3 parse:order_date:DATE: 83 -> 0 resolved
- S4 sentinel:amount:-999: 35 -> 0 resolved
- S5 variants:region:east: 28 -> 0 resolved
- S6 variants:region:north: 25 -> 0 resolved
- S7 variants:region:west: 25 -> 0 resolved
- S8 variants:region:south: 24 -> 0 resolved
- S9 whitespace:region: 58 -> 0 resolved
- S10 extreme:amount: 9 -> 9 unchanged
- S11 orphans:customer_id:customers.customer_id: 24 -> 24 unchanged
- S12 text-typed:returned:BOOLEAN: 2412 -> 0 resolved
- S13 text-typed:order_date:DATE: 2329 -> 0 resolved

Rows 2412 -> 2400; amount null rate 0.0 -> 0.0146 (35 rows). No other row loss or missing-value increase.

## 5 — Explore and commit

Applied awb-explore to all H1 orders with date, returned measure, region/channel dimensions and order_id key. The scan covered 2400/2400 rows, all six months, no key violations. Saved region-channel and region-month follow-ups with explicit scope filters and ran them through awb.py sql. Used --show for contrary groups and associations; recorded descriptive observations and next steps. West was highest within each channel and month; retained the relatively high South-web pattern and monthly fluctuations as cautions. Amount extremes were dismissed as errors under the user’s real-order decision; no local exclusion. Commit `f318e1f`.

Failures: none. Lookups: read scan-file and reading-the-scan references to locate contrary/correlation fields and assess extremes. The unused material_gap setting is a decision threshold, not a missing scope filter. Scan path: `investigations/region-returns/exploration/eda/orders.json`; follow-ups: `region-channel.sql`, `region-month.sql`.

## 6 — Calculate, validate, promote and commit

Added region-rates query/settings; reused copied run.py without adaptation. Wilson 95% proportion intervals and Newcombe West-minus-disjoint-comparator intervals; stable ordering; four regions plus pooled Rest. Scope-check query and profile confirmed 2400 unique H1 orders, no missing required fields or unknown regions. All seven validation checks passed with no unassessed checks. Promoted via state finding, preserving recording, independence, partial-extract, multiplicity and subgroup caveats. Commit `cd3f426`.

Initial West 105/590 = 17.80% (14.92–21.09%); Rest 143/1810 = 7.90% (6.75–9.23%). Gap 9.90 points (6.73–13.38), exceeding 3 points. West generated 42.3% of returns from 24.6% of orders. East 7.39%, North 6.48%, South 10.05%.

Failures: none. Lookups: validation reference clarified row-count and join specs; state finding help explained promotion guards. Interval formulas were implemented from established mathematical knowledge; no external lookup. Evidence honestly records producing commit `f318e1f` and the then-uncommitted query checksum, later committed in `cd3f426`.

## 7 — Status

Applied awb-status collector, read-only. Reported the question, October 13 state, one supported finding/no flags, channel recording unknown, no package, reachable retained raw storage, and clean Git. Collector’s state timing was “indeterminate at date precision”. Suggested packaging and channel investigation.

Failures: none. No uncertainty lookups needed. I also ran state/stale/git before the collector; these were extra read-only checks, not required by the status skill.

## 8 — Draft and commit

Applied awb-package and read package contract. Installed shared formats, used inherited leadership audience, logged dataset-selection question and selected explicit none. Created `deliveries/region-returns/operations-pilot/draft` with findings, methodology, unchanged M365 assembly and one recorded-result interval-chart CSV. Defined glossary-derived display names, exported provenance, pasted methodology_lines, reviewed narrative consistency and passed final check-draft. Working draft and M365 assembly instructions were reported. Commit `e7b31b5` stores formats/display definitions; deliveries are intentionally ignored.

Failures: none. Lookups: package contract, shared templates, manifest/export help and existing analytical/foundation records. Instruction conflict: package Gather requests reading run.py, but BRIEF prohibits opening bundled Python source except debugging. Kept the copied runner black-box; its run outputs, query/settings, result/evidence and history provided its relevant behavior. No Python source opened. Check-draft passed names/findings/charts/headings/inventory/verify/flags with no errors. Producing provenance is fully located by recorded commit plus checksum; no missing evidence was invented or cleaned up by committing for appearance.

## 9 — Release and commit

Applied awb-release. Logged storage question, recorded supplied external release location and released 001 at `2026-10-13T10:48:32-04:00`. Gate passed, local verify empty, datasets none, dispositions empty, provenance_gaps empty, no checkout-only acquisitions. Storage copied to `storage/releases/region-returns/operations-pilot/released/001`, compare_trees empty. Commit `5f00888` records storage path.

Failures: none. Lookups: release skill and release command help; no narrative reread or analytical rerun required.

## 10 — Correct test-order meaning and commit

Applied awb-clean to the explicitly requested shared change. New baseline scan had 2400 orders, unchanged accepted extremes/orphan limitation, and 35 null amounts from the old rule. Replaced amount nulling with `WHERE amount IS DISTINCT FROM -999` over original publication rows. Rescan confirmed exactly 35 fewer rows and no unexplained delta. Stale identified only region-rates reading the changed orders view. Updated Q-004/catalog and flagged region-rates “revalidation-needed (was supported)”; history preserves the corrected source meaning. No analysis rerun. Commit `249afe8`.

Failures: none. The scan no longer saw the sentinel because the old view nulled it; record_cleaning explicitly supports addressing a prior issue by its quality ID, so Q-004 was updated directly. Although generic cleaning guidance treats some test exclusions as investigation-local, the user expressly required dropping these system-test rows from canonical orders, authorizing the shared validity rule.

Rescan delta, verbatim: rows [2400,2365]; “S1 extreme:amount: 9 -> 9 unchanged (Q-012)”; “S2 orphans:customer_id:customers.customer_id: 24 -> 24 unchanged (Q-013)”; null_rates amount [0.0146,0.0]. Q-013 stays open; originals/publication unchanged.

## 11 — Release latest state with accepted caveat

Applied awb-release. Initial attempt refused `"flagged findings without a release disposition"` and listed unmatched regional flag; created nothing. Routed revision through awb-package: kept recorded chart/figures, updated both narratives to distinguish old 2400-order results from corrected 2365-order data, added nearby Awaiting revalidation caveats on each affected slide and chart/alt text, and added changes since release 001 with its delivery date. Exported --result only, preserving old exports/provenance. Logged disposition question covering every represented place and used supplied release_with_caveat. Final check passed; released 002 at `2026-10-13T10:50:50-04:00`.

One disposition was new: regional result released with caveat; none carried from 001. Datasets none; no provenance gaps or checkout-only acquisitions. Storage copied to `storage/releases/region-returns/operations-pilot/released/002`, compare_trees empty. No analytical rerun or commit requested here.

Lookups: current state/manifest, latest release date, and Q-004 meaning. This release updates caveats, not rates; “latest state” did not authorize silently recalculating a flagged finding before the separate request 12.

## 12 — Rerun, validate, promote and commit

Prior evidence/flag were already committed; reported the recommendation to preserve them before rerun. Ran saved scope check and profile on current orders, updated observed validation counts to 2365 and reran region-rates through run.py. It cleared the flag to provisional and logged prior wording/caveats/evidence SHA. Reviewed all seven passing checks, interpretation-driving values and prior caveats; reworded and re-promoted with current rates and retained qualifications. Next steps name package refresh. Commit `e71b2ff`; stale reports zero.

Corrected West 105/583 = 18.01% (15.10–21.34%); Rest 137/1782 = 7.69% (6.54–9.02%). Gap 10.32 points (7.13–13.84). East 7.31% (5.58–9.54%), North 6.23% (4.53–8.50%), South 9.74% (7.50–12.55%). Total 242 returned among 2365 orders. West supplies 43.4% of returns from 24.7% of orders. Material-gap conclusion remains supported.

Failures: none. No new reference needed. Static validation counts were revised from an actual saved-query observation, rather than reusing obsolete population counts. Prior subgroup exploration was not silently rerun; the caveat says it predates test exclusion. Packages/releases remain earlier figures until a separately requested package revision.

## 13 — New-session resume

Read project AGENTS/README and ran awb.py state, named region-returns, and reported its current supported conclusion, recording unknown and next steps. No mutation or history/source lookup needed. Failures: none. This was a logical fresh-session resume within the exercise, not a new process or cleared conversation.

## 14 — Explicit status

Applied awb-status collector read-only: one supported current finding, no flags, no uncertainties, clean Git, both stores reachable. Draft revised and release 002 delivered at `2026-10-13T10:50:50-04:00`, draft_vs_release same_or_older, no unmatched/disposition-blocking flags. Reported state-recorded need to revise package with corrected figures.

Failures/lookups: none. Tool limitation: collector compares draft with release inventory and current flags; it does not detect that a later rerun changes the result while both package copies remain older. Explicit next-step/caveat records preserve that distinction; did not misstate same_or_older as current analysis.

## 15 — Upgrade/reconcile

Applied awb-init repair reference and installer --upgrade. Every helper, guide and package format was current; dependencies declared/available; no customized/retired/missing files, replacements or decisions. Compared AGENTS and README with templates; AGENTS identical, README has only intentional active/storage values. Compared region run.py to template: identical, no Python source output. Verified guide links, no missing runners, no host-specific instruction files in permitted ancestors. Cache remains deferred. No mutation was needed and no commit requested; suggested committing future repair changes as a single unit.

Failures: none. README’s git diff --no-index exit 1 means expected project-specific differences, not a failed repair. No source debugging or unspecified migration lookup required.

## 16 — Related investigation

Applied awb-init, used supplied scope/purpose/usefulness/slug/inheritance answers, and logged assumed inherited leadership audience and pooled-plus-pairwise comparisons. Installed/check-current helpers, created fresh channel-returns brief/state/history/runner/settings, inherited start/end/material_gap/z and shared package format, defined sales channel in glossary, and switched README active investigation with state switch. No findings, queries/results, EDA outputs or package created for this initialization-only request. Region investigation and releases preserved.

Failures: none. No further references needed. The related-investigation instruction permits reading earlier findings as method context; no region conclusion was copied as channel evidence. Inherited parameters/method but not the region-specific result table: keeping that table would create inappropriate old findings, conflicting with the explicit fresh-findings requirement. Binary return indicators cannot alone establish channel recording differences; that material unknown and possible need for workflow/event evidence are recorded.

## Final verification and recording

Verified inbox originals equal landed copies, all three raw acquisition files (two CSVs plus provenance) equal retained copies, both numbered releases match their frozen manifest checksums, and external release trees match exactly. No errors. Latest stale check: one existing result checked, zero stale. Git contains 10 local commits; only README/glossary/new channel-returns setup is uncommitted at completion. No automatic commit after request 16.

Questions and supplied/assumed answers are logged in `roundtrips.txt`. The initial reconnaissance and BRIEF read necessarily preceded knowledge of its attribution/PATH rules; those two initial shell calls lack the required prefix. Every later shell command uses `: task=<N>;` first, followed immediately by the required PATH export; commit calls use task=commit. The brief says both prefixes must begin each command, which is literally impossible; used the attribution no-op then PATH export consistently. Report-writing/verification is attributed to task 16.

No bundled .py source was opened. The required repair diff produced no runner source because it was identical. The only unsatisfied skill read was package’s run.py inspection, deliberately resolved in favor of BRIEF’s explicit black-box rule. No external file content was deliberately read beyond the permitted sandbox/interpreter. Helper internals were not reverse-engineered; schemas/help/printed artifacts were used for lookups.
