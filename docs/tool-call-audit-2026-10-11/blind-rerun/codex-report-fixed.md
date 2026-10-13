# Workbench exercise report

I completed requests 1–16 in order in `work/returns`. I used no network, push, sub-agents or helper-source debugging. I made all requested commits locally. Active investigation is now `channel-returns`. Its new setup is not committed, because request 16 did not request a commit.

## 1 — Initialize and commit

I applied awb-init. I examined the sandbox/target. I copied the root orientation, instructions and ignore rules. I installed the helpers/guides/dependencies. I populated the region-returns brief, state, history, runner and settings. I created the candidate ERP source register and glossary. I scoped all H1 2026 orders, all channels and the order-recorded region. I recorded the pilot decision, the leadership audience and the 3-point threshold. The data/cache/delivery directories were deferred. Commit `b97c6c3`.

Failures/recovery: `ls -la work/returns` reported “No such file or directory”. `git status --short` at the sandbox root reported “not a git repository”. I created the target and initialized its local repository. The first `install_helpers.py work/returns` returned exit 1 with `"workbench": false`. I installed README/AGENTS/.gitignore first. This satisfied the detection, and the next installation was successful. No package/dependency attention items remained.

Choices/lookups: I read the awb-init assets and the installed guides. I did not open Python source. I interpreted “the rest” as the pooled non-West orders, with individual comparisons as sensitivity. I selected Wilson intervals. The assumptions were logged and recorded. No host instruction file existed in the permitted ancestors. As the brief says, I did not examine ancestors outside the sandbox.

## 2 — Land one acquisition

I read the data guide. I recorded the supplied raw retention location, and I ran retain. Then I landed both ERP files as `erp/extract-2026-07-01`. Landing reported 2 files, 118915 bytes, copied/matched retention and no discrepancies. The helper added the acquisition and marked the source acquired. I filled in the restrictions: “Internal; no customer PII”. I examined only landed records, with awb.py profile: 2412 order rows, 2400 distinct order IDs, 400 unique customers.

Failures: none. Lookups: command help for profile/sql/publish. Landed profile samples established the Y/N returns, the region variants and the source schema. The extraction identifier gives the date of the source export. But provenance records the actual landing time in October. These two are different.

## 3 — Publish, expose, catalog and commit

I saved conversion SELECTs and failure-returning checks for both datasets. I committed the conversion code first (`7674964`), so that the publications identify committed conversion code. I published orders (2412 rows) and customers (400 rows) under publication ID `extract-2026-07-01`. Both were validated. I created Git-managed canonical views and completed the catalog. Commit `9031ec2`.

Failures: none. Lookups: the publish helper’s printed view_sql/catalog_row supplied the view/publication paths. Order labels/dates and Y/N indicators stayed raw until cleaning. I first drafted an integer cast for returned. Based on the landed profile, I corrected it before execution to keep Y/N. No publication failed. A custom convert callable and a read of the landing reference were not necessary.

## 4 — Clean and commit

I applied awb-clean to orders, with the order_id grain, the customer reference and the H1 date range. I classified all 13 issues: shared rules Q-001–Q-011, real large values accepted as Q-012, and partial-customer orphans open as Q-013. I used the supplied answers to drop duplicate copies, null -999 amounts, keep large amounts/orphans and parse slash dates as month/day/year. I read the correction-views reference and corrected the canonical view. Then I rescanned, ran stale, and recorded quality/catalog through the helper. No findings existed to flag. There was no analysis rerun. Commit `e6490f5`.

Failures/recovery: I tried `--range returned=Y:N`. The scanner returned exit 2, `"ValueError: --range returned=Y:N: bounds are numbers or ISO dates"`. I removed this categorical range. The first record_cleaning refused with `"RecordError: foundation/catalog.md: several rows are named orders"`, and wrote nothing. I renamed the publication rows to `orders-publication` and `customers-publication`. I kept the canonical names. Then I did the recording again, and it was successful.

Instruction/tool mismatch: the data guide/publish output gave the publication and the canonical view the same catalog name. But record_cleaning needs a unique name. Different publication names solve this conflict without a change to the dataset/view identities. I kept the internal-source restrictions. No statement prohibited local quality examples or local commits.

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

Rows 2412 -> 2400. Amount null rate 0.0 -> 0.0146 (35 rows). There was no other row loss or missing-value increase.

## 5 — Explore and commit

I applied awb-eda to all H1 orders with date, returned measure, region/channel dimensions and order_id key. The scan covered 2400/2400 rows and all six months. It found no key violations. I saved region-channel and region-month follow-ups with explicit scope filters. I ran them through awb.py sql. I used --show for contrary groups and associations. I recorded descriptive observations and next steps. West was highest in each channel and month. I kept the relatively high South-web pattern and the monthly fluctuations as cautions. Under the real-order decision of the user, the amount extremes were dismissed as errors. There was no local exclusion. Commit `f318e1f`.

Failures: none. Lookups: I read the scan-file and reading-the-scan references to find contrary/correlation fields and to assess extremes. The unused material_gap setting is a decision threshold, not a missing scope filter. Scan path: `investigations/region-returns/exploration/eda/orders.json`. Follow-ups: `region-channel.sql`, `region-month.sql`.

## 6 — Calculate, validate, promote and commit

I added the region-rates query/settings. I used the copied run.py again without adaptation. Methods: Wilson 95% proportion intervals and Newcombe West-minus-disjoint-comparator intervals. Stable order. Four regions plus pooled Rest. The scope-check query and profile confirmed 2400 unique H1 orders. They also confirmed that there were no missing necessary fields and no unknown regions. All seven validation checks passed with no unassessed checks. I promoted with state finding. I kept the recording, independence, partial-extract, multiplicity and subgroup caveats. Commit `cd3f426`.

Initial: West 105/590 = 17.80% (14.92–21.09%). Rest 143/1810 = 7.90% (6.75–9.23%). Gap 9.90 points (6.73–13.38), which is more than 3 points. West generated 42.3% of returns from 24.6% of orders. East 7.39%, North 6.48%, South 10.05%.

Failures: none. Lookups: the validation reference clarified row-count and join specs. The state finding help explained promotion guards. I implemented the interval formulas from established mathematical knowledge. I did no external lookup. The evidence honestly records producing commit `f318e1f` and the query checksum, which was not committed at that time. It was committed later in `cd3f426`.

## 7 — Status

I applied the awb-status collector, read-only. I reported the question, the October 13 state, one supported finding/no flags, the channel recording unknown, no package, reachable retained raw storage and clean Git. The collector’s state timing was “indeterminate at date precision”. I suggested packaging and a channel investigation.

Failures: none. No uncertainty lookups were necessary. I also ran state/stale/git before the collector. These were extra read-only checks. The status skill did not make them necessary.

## 8 — Draft and commit

I applied awb-package and read the package contract. I installed shared formats and used the inherited leadership audience. I logged the dataset-selection question and selected explicit none. I created `deliveries/region-returns/operations-pilot/draft` with findings, methodology, unchanged M365 assembly and one recorded-result interval-chart CSV. I defined glossary-derived display names and exported provenance. I pasted methodology_lines and reviewed narrative consistency. The final check-draft passed. The Working draft and the M365 assembly instructions were reported. Commit `e7b31b5` stores formats/display definitions. Deliveries are intentionally ignored.

Failures: none. Lookups: package contract, shared templates, manifest/export help and existing analytical/foundation records. Instruction conflict: package Gather asks you to read run.py. But BRIEF prohibits you to open bundled Python source, except for debugging. I kept the copied runner as a black box. Its run outputs, query/settings, result/evidence and history supplied its relevant behavior. I opened no Python source.

Check-draft passed names/findings/charts/headings/inventory/verify/flags with no errors. The recorded commit plus checksum fully locate the producing provenance. I did not invent missing evidence. I did not make a commit for appearance to clean up missing evidence.

## 9 — Release and commit

I applied awb-release. I logged the storage question and recorded the supplied external release location. Then I released 001 at `2026-10-13T10:48:32-04:00`. The gate passed. Local verify was empty, datasets none, dispositions empty and provenance_gaps empty. There were no checkout-only acquisitions. Storage: copied to `storage/releases/region-returns/operations-pilot/released/001`, compare_trees empty. Commit `5f00888` records the storage path.

Failures: none. Lookups: release skill and release command help. No narrative reread or analytical rerun was necessary.

## 10 — Correct test-order meaning and commit

I applied awb-clean to the explicitly requested shared change. The new baseline scan had 2400 orders, the unchanged accepted extremes/orphan limitation, and 35 null amounts from the old rule. I replaced amount nulling with `WHERE amount IS DISTINCT FROM -999` over the original publication rows. The rescan confirmed exactly 35 fewer rows and no unexplained delta. Stale identified only region-rates as a reader of the changed orders view. I updated Q-004/catalog and flagged region-rates “revalidation-needed (was supported)”. History keeps the corrected source meaning. There was no analysis rerun. Commit `249afe8`.

Failures: none. The scan did not see the sentinel any more, because the old view nulled it. record_cleaning explicitly supports addressing a prior issue by its quality ID, so Q-004 was updated directly. Generic cleaning guidance treats some test exclusions as investigation-local. But the user expressly told me to drop these system-test rows from canonical orders. This authorized the shared validity rule.

Rescan delta, verbatim: rows [2400,2365], “S1 extreme:amount: 9 -> 9 unchanged (Q-012)”, “S2 orphans:customer_id:customers.customer_id: 24 -> 24 unchanged (Q-013)”, null_rates amount [0.0146,0.0]. Q-013 stays open. The originals/publication are unchanged.

## 11 — Release latest state with accepted caveat

I applied awb-release. The initial attempt refused with `"flagged findings without a release disposition"` and listed the unmatched regional flag. It created nothing. I routed the revision through awb-package. I kept the recorded chart/figures. I updated both narratives to make clear the difference between old 2400-order results and corrected 2365-order data. I added nearby Awaiting revalidation caveats on each affected slide and on chart/alt text. I added the changes since release 001 with its delivery date. I exported with --result only, and this kept the old exports/provenance. I logged a disposition question that covered every represented place, and I used the supplied release_with_caveat. The final check passed. I released 002 at `2026-10-13T10:50:50-04:00`.

One disposition was new: the regional result was released with caveat. No disposition carried over from 001. Datasets: none. There were no provenance gaps and no checkout-only acquisitions. Storage: copied to `storage/releases/region-returns/operations-pilot/released/002`, compare_trees empty. No analytical rerun or commit was requested here.

Lookups: current state/manifest, latest release date, and Q-004 meaning. This release updates caveats, not rates. “latest state” did not authorize a silent recalculation of a flagged finding before the separate request 12.

## 12 — Rerun, validate, promote and commit

The prior evidence/flag were already committed. I reported the recommendation to keep them before a rerun. I ran the saved scope check and profile on current orders. I updated the observed validation counts to 2365. Then I reran region-rates through run.py. It cleared the flag to provisional, and it logged the prior wording/caveats/evidence SHA. I reviewed all seven passed checks, the interpretation-driving values and the prior caveats. I reworded and re-promoted with the current rates and the retained qualifications. Next steps name a package refresh. Commit `e71b2ff`. Stale reports zero.

Corrected: West 105/583 = 18.01% (15.10–21.34%). Rest 137/1782 = 7.69% (6.54–9.02%). Gap 10.32 points (7.13–13.84). East 7.31% (5.58–9.54%), North 6.23% (4.53–8.50%), South 9.74% (7.50–12.55%). Total 242 returned among 2365 orders. West supplies 43.4% of returns from 24.7% of orders. The material-gap conclusion remains supported.

Failures: none. No new reference was necessary. I revised the static validation counts from an actual saved-query observation. I did not use the obsolete population counts again. The prior subgroup exploration was not silently rerun. The caveat says that it is older than the test exclusion. Packages/releases stay at the earlier figures until a separately requested package revision.

## 13 — New-session resume

I read the project AGENTS/README and ran awb.py state. I named region-returns, and I reported its current supported conclusion, recording unknown and next steps. No mutation or history/source lookup was necessary. Failures: none. This was a logical fresh-session resume in the exercise. It was not a new process or a cleared conversation.

## 14 — Explicit status

I applied the awb-status collector read-only. Result: one supported current finding, no flags, no uncertainties, clean Git, both stores reachable. The draft was revised and release 002 was delivered at `2026-10-13T10:50:50-04:00`. draft_vs_release was same_or_older. There were no unmatched/disposition-blocking flags. I reported the need, recorded in state, to revise the package with the corrected figures.

Failures/lookups: none. Tool limitation: the collector compares the draft with the release inventory and current flags. It does not detect that a later rerun changes the result while both package copies stay older. Explicit next-step/caveat records keep that distinction. I did not misstate same_or_older as current analysis.

## 15 — Upgrade/reconcile

I applied the awb-init repair reference and installer --upgrade. Every helper, guide and package format was current. Dependencies were declared/available. There were no customized/retired/missing files, replacements or decisions. I compared AGENTS and README with the templates. AGENTS was identical. README has only intentional active/storage values. I compared region run.py to the template: identical, with no Python source output. I verified the guide links. I also verified that there were no missing runners and no host-specific instruction files in permitted ancestors. Cache remains deferred. No mutation was necessary, and no commit was requested. I suggested to commit future repair changes as a single unit.

Failures: none. The git diff --no-index exit 1 for README means expected project-specific differences, not a failed repair. No source debugging or unspecified migration lookup was necessary.

## 16 — Related investigation

I applied awb-init and used the supplied scope/purpose/usefulness/slug/inheritance answers. I logged the assumed inherited leadership audience and pooled-plus-pairwise comparisons. I installed the helpers or checked that they were current. I created a fresh channel-returns brief/state/history/runner/settings. I inherited start/end/material_gap/z and the shared package format. I defined sales channel in the glossary. I switched the README active investigation with state switch. For this initialization-only request, I created no findings, queries/results, EDA outputs or package. The region investigation and releases were kept.

Failures: none. No more references were necessary. The related-investigation instruction lets you read earlier findings as method context. I copied no region conclusion as channel evidence. I inherited parameters/method, but not the region-specific result table. If I keep that table, it creates old findings that are not applicable. That conflicts with the explicit rule for fresh findings. Binary return indicators alone cannot establish channel recording differences. That material unknown and the possible need for workflow/event evidence are recorded.

## Final verification and recording

I verified that the inbox originals are equal to the landed copies. I also verified that all three raw acquisition files (two CSVs plus provenance) are equal to the retained copies. I verified that both numbered releases match their frozen manifest checksums, and that the external release trees match exactly. There were no errors. Latest stale check: one existing result checked, zero stale. Git contains 10 local commits. At completion, only README/glossary/new channel-returns setup is not committed. There was no automatic commit after request 16.

The questions and supplied/assumed answers are logged in `roundtrips.txt`. The initial reconnaissance and the BRIEF read necessarily occurred before I knew its attribution/PATH rules. Those two initial shell calls do not have the necessary prefix. Every later shell command uses `: task=<N>;` first, and the necessary PATH export immediately after it. Commit calls use task=commit.

The brief says that both prefixes must begin each command, and this is literally impossible. I used the attribution no-op and then the PATH export consistently. Report-writing/verification is attributed to task 16.

No bundled .py source was opened. The necessary repair diff produced no runner source because it was identical. The only skill read that I did not do was the run.py inspection of package. I deliberately decided this in favor of the explicit black-box rule of BRIEF. I did not deliberately read external file content beyond the permitted sandbox/interpreter. I did not reverse-engineer helper internals. I used schemas/help/printed artifacts for lookups.
