# AWB exercise report

Completed requests 1–16 in order on 2026-10-13. Project: `work/returns/`. Active investigation: `channel-returns`. Required questions and assumed decisions are in `roundtrips.txt`. No network access or pushes were used.

## 1. Initialize regional investigation; commit

Read `awb-init/SKILL.md`, checked the empty target and instruction-file locations inside the sandbox, initialized a local Git repository, and installed project orientation, rules, guides, helpers, dependency declaration, source register and glossary. Created `investigations/region-returns/{brief,state,history}.md`, `settings.toml`, and `run.py`. Recorded the supplied population, pilot purpose, 3-point threshold, audience, unknown and slug. Assumed West-versus-pooled-others as primary comparison, Wilson rate intervals and a difference interval, recorded in the interview log and brief. Data and delivery directories were deferred.

Failures/recovery: initial discovery `git status --short` reported `fatal: not a git repository (or any of the parent directories): .git`; initialized Git in the target. The first installer call, before README existed, returned `workbench: false` and installed nothing; created the workbench records and reran successfully. All helpers installed and duckdb/pandas passed. No host instruction conflict was found. Commit: `c16979c`.

Recording caveat: the two discovery commands used to find/read BRIEF ran before its task-tag and PATH requirements were known. Subsequent shell calls begin with `: task=...; export PATH=...;`. BRIEF independently says both prefixes must begin every command; I placed the required attribution no-op first and PATH setup immediately after it.

## 2. Land ERP acquisition

Recorded the supplied external raw-retention location in README, ran `retain`, then landed both CSVs together with `land erp extract-2026-07-01 ...`. Acquisition: 2 files, 118,915 bytes, with file SHA-256s and complete provenance. Automatic retention copied to `storage/raw/data/raw/erp/extract-2026-07-01/`; no conflicts or discrepancies. Source became acquired; filled `internal; no customer PII`. No failures or additional assumptions. No commit requested at this step.

## 3. Publish and catalog; commit

Profiled only landed copies: 2,412 order rows/2,400 IDs and 400 customer rows/400 IDs. Saved faithful all-text conversion SQL and publication checks (non-null primary IDs and counts matching landed files), committed before publishing so both publications identify conversion commit `16af603`. Published orders (35,614 bytes) and customers (4,457 bytes), with checks returning no failures. Created canonical views and catalog rows; verified both through profile. Commit: `9d57ca8` after publication/cataloging. No publication refusal.

Usability issue discovered in request 4: the publication's printed `catalog_row` names the dataset, as does its canonical view. The recorder later requires unique catalog names. Recovery is described below.

## 4. Clean orders; commit

Read `awb-clean` and its correction-view reference. Scanned using order_id grain, customer reference and H1 bounds. Used supplied decisions for duplicate landings, -999 missing amounts, real large amounts, partial-customer orphans and month/day/year slash dates. Implemented shared representation rules plus exact duplicate removal in `foundation/views/00_orders.sql`; retained missing-amount and unmatched-customer orders. Recorded Q-001–Q-014: shared corrections Q-001–009 and Q-012–014; Q-011 open partial-extract limitation; Q-010 accepted real large amounts. No investigation exclusion or finding rerun.

Rescan delta lines, verbatim:

```text
S1 duplicate-rows: 12 -> 0 resolved
S2 duplicate-key:order_id: 12 -> 0 resolved
S3 parse:order_date:DATE: 83 -> 0 resolved
S4 sentinel:amount:-999: 35 -> 0 resolved
S5 variants:region:east: 28 -> 0 resolved
S6 variants:region:north: 25 -> 0 resolved
S7 variants:region:west: 25 -> 0 resolved
S8 variants:region:south: 24 -> 0 resolved
S9 whitespace:region: 58 -> 0 resolved
S10 extreme:amount: 9 -> 9 unchanged
S11 orphans:customer_id:customers.customer_id: 24 -> 24 unchanged
S12 text-typed:amount:DOUBLE: 2412 -> 0 resolved
S13 text-typed:returned:BOOLEAN: 2412 -> 0 resolved
S14 text-typed:order_date:DATE: 2329 -> 0 resolved
```

Rows `[2412,2400]`; amount null rates `[0.0,0.0146]`, matching 35 placeholders. `stale`: checked 0, stale 0, no flags.

Failure/recovery: `record_cleaning.py` returned `RecordError: foundation/catalog.md: several rows are named orders`, `written: []`. The following `cat foundation/quality.md` also failed because nothing had been written. Renamed publication entries `orders-publication` and `customers-publication`, kept canonical names, and retried successfully. This uniqueness requirement was absent from the skill instructions. Source restrictions did not prohibit local quality examples; no PII was present. Commit: `fbbe3c5`.

## 5. Explore orders; commit

Read `awb-eda`; framed all H1 orders, returned measure, region/channel dimensions. Scan: 2,400/2,400 rows, unique order_id, six months and 181 dates, no date gaps. Saved scan `exploration/eda/orders.json`, queries `region-channel.sql` and `region-month.sql`, and exploratory observations. West was highest within each channel; channel shares were similar, so mix alone did not explain the crude regional difference. Retained contrary comparisons (North store above North web; South web near West store) and nonmonotonic monthly variation. Disposed the 35 3-IQR amount extremes as real orders under Q-010; the cleaning scan's 5-IQR threshold had found 9. No new shared defect or coverage limitation. Updated issues/next steps, without promoting exploratory output.

Failure/recovery: the month query's window partition repeated `date_trunc(order_date)` while the grouped expression had a DATE cast. DuckDB reported a Binder Error that order_date must appear in GROUP BY. Used the grouped `month` alias, revised the same saved query, and reran successfully. No interpretation changed. Commit: `835c26d`.

## 6. Calculate, validate and promote; commit

Used the analysis guide and validation reference. Implemented saved queries for `region-rates` (Wilson 95%) and `west-gap` (Newcombe differences), H1 parameters and substantive validation specifications. Inspected region, channel and Boolean returned values via profile and checked source/scope/unique counts via SQL. Committed implementation first (`8eda44c`), then ran investigation run.py. Both results had `failed_checks: []` and `not_assessed: []`; promoted using `state finding`, preserving independent-order, customer-dependence, recording-consistency and descriptive-comparison caveats.

Initial supported results: West 105/590 = 17.80% (14.92–21.09%); pooled others 7.90%; gap 9.90 points (6.73–13.38), above 3 points. West generated 42.34% of returns from 24.58% of volume. Other rates: South 10.05%, East 7.39%, North 6.48%. No failed checks or commands. Statistical-method details were analytical choices, recorded as assumptions; no external lookup. Evidence/state commit: `117cb6d`.

## 7. Status

Read `awb-status`; ran its collector read-only. Reported two supported findings, recording unknown and partial customer coverage, clean Git, no package, reachable raw storage, unrecorded release storage. State timing was `indeterminate at date precision`. Suggested drafting a package. No uncertainties, missing-record lookups, failures or writes.

## 8. Draft operations package; commit

Read `awb-package`, package contract, installed shared formats, and gathered the required analytical/foundation records. Named package `region-returns-pilot`; used recorded operations audience and supplied dataset selection `none`. Wrote findings outline, matching methodology and unchanged M365 assembly instructions. Exported chart 1 from region-rates and chart 2 from west-gap; added glossary-derived display headers and pasted exact export mappings into methodology. Manifest records producing commit `8eda44c`, clean producing files and first assembly's uncommitted package templates. No provenance gaps or flags. Confirmed narrative numbers/caveats agree and all claims have methodology support.

Failure/recovery: first `check-draft` flagged ordinary prose `yes/no` as a path at line 73. Replaced with “yes or no” and rechecked: all finding/chart/heading/inventory/flag/error lists empty, `passed: true`. Reported working-copy behavior and PowerPoint-agent assembly instructions. Commit `f438b1a` contains formats, receipt and display vocabulary; drafts are intentionally excluded from Git.

Instruction conflict: packaging expressly requires reading the investigation's run.py, while BRIEF broadly forbids opening bundled .py sources except when stuck/debugging. I read the copied project run.py for the required packaging gather. I did not read any installer, scanner, recorder, collector, CLI, provenance, landing, validation or packaging-helper implementation source.

## 9. Deliver package; commit

Read `awb-release`; release gate passed and froze `released/001` at `2026-10-13T10:47:32-04:00`. Datasets none; dispositions [], provenance gaps [], checkout-only acquisitions [], verify []. Storage initially `unrecorded`; used supplied answer, updated README and ran copy-releases. Storage row: `status: copied`, `compare_trees: []`. Commit `1febc84` records storage; frozen package remains outside Git. No refusal or failure.

## 10. Drop system tests; commit

Used awb-clean again. Canonical scan cannot detect original -999 because the earlier rule already nulled it. Consulted scanner/recorder help, scanned the immutable publication's amount separately (`orders-test-input`), and located 35 -999 orders. Replaced nulling with a shared canonical filter excluding those explicitly identified system tests. Canonical rescan preserved its new 2,400-row baseline and showed rows `[2400,2365]`, amount null rates `[0.0146,0.0]`:

```text
S1 extreme:amount: 9 -> 9 unchanged (Q-010)
S2 orphans:customer_id:customers.customer_id: 24 -> 24 unchanged (Q-011)
```

`stale` identified both findings through changed committed code and view SHA-256. Recorder created Q-015, flagged region-rates and west-gap as `revalidation-needed (was supported)`, and updated the canonical catalog. Superseded Q-004's active treatment while retaining its historical correction row; recorded the changed system-test meaning and analytical impact. Publication-scan duplicate/extreme/text observations restated already settled Q-001/Q-002, Q-010 and Q-012. No analysis was rerun. Commit `50540e6`.

Usability gap: the skill does not explain reopening a hidden sentinel after an earlier correction. The additional publication scan supplied source evidence; the canonical rescan supplied the actual delta. The recorder's publication-based correction has no automatic before/after count, so its rationale explicitly records the canonical delta and unchanged publication.

## 11. Deliver latest state with accepted caveats

Initial release was refused: `flagged findings without a release disposition`, with two unmatched flags. Routed revision through awb-package. Preserved prior chart bytes and results; `export --result region-rates --result west-gap` refreshed recorded provenance without trying to serialize stale results. Updated both narratives, each affected slide, both chart caveats/alt text, changed-version slide and exact manifest flags. Distinguished corrected population 2,365 from displayed prior population 2,400. Both flags represented throughout findings/methodology and their charts.

Used supplied choice `release_with_caveat` for both, recorded questions, checked final draft successfully, and released `002` at `2026-10-13T10:50:56-04:00`. Both dispositions `new: true`; datasets none; provenance gaps [], checkout-only acquisitions [], verify []; storage `copied`, `compare_trees: []`. Release 001 remained frozen. No unauthorized rerun or commit.

## 12. Rerun flagged findings; commit

Reviewed the flagged history/caveats and current interpretation profile. Current counts: 2,365 source/scoped/unique orders, same H1 period and categorical values. Prior evidence was already committed; suggested committing before rerun. Added saved runtime count query and reusable denominator/return-count reconciliation, adapting investigation run.py's producer rather than evidence machinery. Committed implementation `493dce9`, then ran both flagged IDs. Each returned provisional with `state: flag cleared`, `history: true`, no failed or unassessed checks. Reworded and re-promoted with restored caveats after reviewing values and prior history.

Corrected findings: West 105/583 = 18.01% (Wilson 15.10–21.34%); South 9.74%, East 7.31%, North 6.23%; overall 242/2,365 = 10.23%. West versus pooled others 7.69%: gap 10.32 points (Newcombe 7.13–13.84). West generates 43.39% of returns from 24.65% of orders. Individual gaps remain above threshold descriptively. `stale` checked 2, stale 0. Recorded package revision as next work, preserving releases. Commit `4ee782f`. No failures.

The initial validation counts were observed static specifications; this rerun added runtime measurements/reconciliation to avoid manual count maintenance. No earlier interpretation depended on an incorrect count. The project's run scaffold was adapted as its analysis guide prescribes; bundled helper implementations remained unopened.

## 13. Resume in new session

Read project AGENTS and ran `awb.py state`, naming region-returns. Reported two revalidated supported findings and the remaining recording-consistency question. Highlighted that draft/release 002 still contain prior figures with accepted caveats and need an explicitly requested package revision. No analysis, package writes or failures.

## 14. Status

Ran awb-status collector read-only: two supported findings, no flags, no uncertainties, clean Git, state `indeterminate at date precision`; both storage locations reachable, one retained acquisition, zero checkout-only acquisitions. Draft revised `2026-10-13T10:50:37-04:00`; latest release 002 delivered `10:50:56-04:00`; `draft_vs_release: same_or_older`, no release-disposition blockers. Reported the state-recorded package revision next step.

Collector limitation: draft-versus-release compares package artifacts, not whether their numerical contents match newly rerun findings. It did not flag the old figures; the next-step record made that visible. No failures or modifications.

## 15. Bring workbench up to date

Read awb-init repair reference, target orientation/ignores and active records; ran installer `--upgrade`. All 11 helper/guide/package-format files were `current`; requirements declared and interpreter/dependencies passed. Compared AGENTS and README with templates and investigation run.py via prescribed no-index diffs. AGENTS matched; README differences were only project-specific active/storage lines; run.py differed only by its intended runtime producer adaptation. Guide links resolve; no investigation lacks run.py. No customized/retired decisions or repair writes were needed. Existing records, paths and templates were preserved; data/cache remains deferred. No repair commit needed.

The no-index diffs use exit 1 to signal expected content differences, not failures requiring recovery. The repair instructions require comparing the .py scaffold with its asset; this exposed the adaptation diff, an additional required inspection under the same blanket .py restriction noted in request 8. No helper source debugging occurred.

## 16. Initialize related channel investigation

Used awb-init, read active brief/findings as allowed related-method context, and took supplied scoping answers. Created fresh `channel-returns` brief/state/history/settings and current run scaffold. Inherited inclusive H1 dates, every channel, returned/eligible metric, Wilson/Newcombe methods, z, 3-point threshold, shared canonical cleaning and shared package format. Assumed each channel versus pooled others, region-mix assessment and inherited operations audit audience; recorded assumptions. Added shared sales-channel vocabulary. Fresh findings, no result definitions, no analysis, no package. Switched active investigation through `state switch channel-returns` and confirmed installer files/dependencies current.

Recording procedures remain an explicit unknown: export rates alone cannot prove channel recording differences. Region investigation, evidence and releases remain intact. No failures, conflicts or additional lookup. README/glossary/new investigation are uncommitted because this request did not ask for a commit. Suggested continuation: awb-status or awb-eda for orders in channel-returns; commit these new records when requested.

## Final verification

- `stale`: `{"checked": 2, "stale": 0, "skipped": [], "results": []}`.
- Both investigations have complete required records; only region-returns has results defined.
- Both regional evidence records include the new shared validation operation.
- Raw originals match inbox SHA-256s; independently retained acquisition matches every file.
- Frozen releases 001 and 002 match their inventory checksums and every retained-copy file; no discrepancies.
- All explicitly requested commits completed, 12 commits including separate implementation/provenance commits. No pushes.
- Remaining work is intentionally recorded: channel analysis/audit evidence, and revising the regional package to the corrected findings. Neither was authorized as analysis/package work by request 16's initialization.
