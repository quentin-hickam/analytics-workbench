# AWB exercise report

I completed requests 1–16 in order on 2026-10-13. Project: `work/returns/`. Active investigation: `channel-returns`. The necessary questions and the assumed decisions are in `roundtrips.txt`. I used no network access and did no pushes.

## 1. Initialize regional investigation; commit

I read `awb-init/SKILL.md`. I examined the empty target and the instruction-file locations in the sandbox. I initialized a local Git repository. I installed project orientation, rules, guides, helpers, dependency declaration, source register and glossary. I created `investigations/region-returns/{brief,state,history}.md`, `settings.toml`, and `run.py`. I recorded the supplied population, pilot purpose, 3-point threshold, audience, unknown and slug. I assumed West-versus-pooled-others as the primary comparison, Wilson rate intervals and a difference interval. I recorded these assumptions in the interview log and the brief. The data and delivery directories were deferred.

Failures/recovery: in the initial discovery, `git status --short` reported `fatal: not a git repository (or any of the parent directories): .git`. I initialized Git in the target. The first installer call occurred before README existed. It returned `workbench: false` and installed nothing. I created the workbench records and ran the installer again successfully. All helpers installed, and duckdb/pandas passed. I found no host instruction conflict. Commit: `c16979c`.

Recording caveat: I used two discovery commands to find and read BRIEF. These commands ran before I knew the task-tag and PATH rules of BRIEF. The later shell calls start with `: task=...; export PATH=...;`. BRIEF says separately for each of the two prefixes that it must begin every command. I put the necessary attribution no-op first, and the PATH setup immediately after it.

## 2. Land ERP acquisition

I recorded the supplied external raw-retention location in README, and I ran `retain`. Then I landed both CSVs together with `land erp extract-2026-07-01 ...`. Acquisition: 2 files, 118,915 bytes, with file SHA-256s and complete provenance. Automatic retention copied the files to `storage/raw/data/raw/erp/extract-2026-07-01/`. There were no conflicts or discrepancies. The source became acquired. I filled in `internal; no customer PII`. There were no failures and no more assumptions. The user did not request a commit at this step.

## 3. Publish and catalog; commit

I profiled only the landed copies: 2,412 order rows/2,400 IDs and 400 customer rows/400 IDs. I saved faithful all-text conversion SQL and publication checks (non-null primary IDs, and counts that match the landed files). I committed them before I published, so that both publications identify conversion commit `16af603`. I published orders (35,614 bytes) and customers (4,457 bytes). The checks returned no failures. I created canonical views and catalog rows. I verified both with profile. Commit: `9d57ca8`, after publication/cataloging. There was no publication refusal.

Usability issue that I found in request 4: the printed `catalog_row` of the publication names the dataset. Its canonical view also names the dataset. Later, the recorder needs unique catalog names. The recovery is described below.

## 4. Clean orders; commit

I read `awb-clean` and its correction-view reference. I scanned with the order_id grain, the customer reference and the H1 bounds. I used the supplied decisions for duplicate landings, -999 missing amounts, real large amounts, partial-customer orphans and month/day/year slash dates. In `foundation/views/00_orders.sql`, I implemented shared representation rules and exact duplicate removal. I kept the missing-amount orders and the unmatched-customer orders. I recorded Q-001–Q-014. Q-001–009 and Q-012–014 are shared corrections. Q-011 is an open partial-extract limitation. Q-010 accepted real large amounts. There was no investigation exclusion and no finding rerun.

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

Rows: `[2412,2400]`. Amount null rates: `[0.0,0.0146]`, which agrees with the 35 placeholders. `stale`: checked 0, stale 0, no flags.

Failure/recovery: `record_cleaning.py` returned `RecordError: foundation/catalog.md: several rows are named orders`, `written: []`. The next command, `cat foundation/quality.md`, also failed, because nothing was written. I renamed the publication entries to `orders-publication` and `customers-publication`. I kept the canonical names. The next attempt was successful. The skill instructions did not include this rule for unique names. The source restrictions did not prohibit local quality examples. No PII was present. Commit: `fbbe3c5`.

## 5. Explore orders; commit

I read `awb-eda`. I framed all H1 orders, the returned measure and the region/channel dimensions. Scan: 2,400/2,400 rows, unique order_id, six months and 181 dates, no date gaps. I saved the scan `exploration/eda/orders.json`, the queries `region-channel.sql` and `region-month.sql`, and the exploratory observations. West was highest in each channel. Channel shares were similar. As a result, mix alone did not explain the crude regional difference. I kept the contrary comparisons (North store above North web, and South web near West store) and the nonmonotonic monthly variation. I disposed the 35 3-IQR amount extremes as real orders under Q-010. The 5-IQR threshold of the cleaning scan had found 9. I found no new shared defect or coverage limitation. I updated issues/next steps. I did not promote exploratory output.

Failure/recovery: the window partition of the month query repeated `date_trunc(order_date)`, but the grouped expression had a DATE cast. DuckDB reported a Binder Error that said that order_date must appear in GROUP BY. I used the grouped `month` alias and revised the same saved query. Then I ran it again successfully. No interpretation changed. Commit: `835c26d`.

## 6. Calculate, validate and promote; commit

I used the analysis guide and the validation reference. I implemented saved queries for `region-rates` (Wilson 95%) and `west-gap` (Newcombe differences). I also implemented H1 parameters and substantive validation specifications. I examined the region, channel and Boolean returned values with profile. I checked the source/scope/unique counts with SQL. I committed the implementation first (`8eda44c`). Then I ran the investigation run.py. Both results had `failed_checks: []` and `not_assessed: []`. I promoted them with `state finding`. I kept the independent-order, customer-dependence, recording-consistency and descriptive-comparison caveats.

Initial supported results: West was 105/590 = 17.80% (14.92–21.09%). Pooled others were 7.90%. The gap was 9.90 points (6.73–13.38), which is above 3 points. West generated 42.34% of returns from 24.58% of volume. Other rates: South 10.05%, East 7.39%, North 6.48%. No checks or commands failed. The statistical-method details were analytical choices, and I recorded them as assumptions. I did no external lookup. Evidence/state commit: `117cb6d`.

## 7. Status

I read `awb-status`. I ran its collector read-only. I reported two supported findings, the recording unknown, partial customer coverage, clean Git, no package, reachable raw storage and unrecorded release storage. State timing was `indeterminate at date precision`. I suggested the next step: draft a package. There were no uncertainties, missing-record lookups, failures or writes.

## 8. Draft operations package; commit

I read `awb-package` and the package contract. I installed the shared formats. I gathered the necessary analytical/foundation records. I named the package `region-returns-pilot`. I used the recorded operations audience and the supplied dataset selection `none`. I wrote the findings outline, a matching methodology and unchanged M365 assembly instructions. I exported chart 1 from region-rates and chart 2 from west-gap. I added glossary-derived display headers. I pasted the exact export mappings into the methodology. The manifest records producing commit `8eda44c`, clean producing files, and the uncommitted package templates of the first assembly. There were no provenance gaps or flags. I confirmed that the narrative numbers/caveats agree, and that all claims have methodology support.

Failure/recovery: the first `check-draft` flagged the ordinary prose `yes/no` at line 73 as a path. I replaced it with “yes or no” and did the check again. All finding/chart/heading/inventory/flag/error lists were empty, and the result was `passed: true`. I reported the working-copy behavior and the PowerPoint-agent assembly instructions. Commit `f438b1a` contains formats, receipt and display vocabulary. The drafts are intentionally not in Git.

Instruction conflict: packaging explicitly says that you must read the run.py of the investigation. But BRIEF broadly forbids you to open bundled .py sources, except when you are stuck/debugging. I read the copied project run.py for the necessary packaging gather. I did not read the implementation source of any installer, scanner, recorder, collector, CLI, provenance, landing, validation or packaging helper.

## 9. Deliver package; commit

I read `awb-release`. The release gate passed, and `released/001` was frozen at `2026-10-13T10:47:32-04:00`. Datasets: none. Dispositions [], provenance gaps [], checkout-only acquisitions [], verify []. Storage was `unrecorded` at first. I used the supplied answer, updated README and ran copy-releases. Storage row: `status: copied`, `compare_trees: []`. Commit `1febc84` records the storage. The frozen package stays outside Git. There was no refusal or failure.

## 10. Drop system tests; commit

I used awb-clean again. The canonical scan cannot detect the original -999 because the earlier rule already nulled it. I read the scanner/recorder help. I scanned the amount of the immutable publication separately (`orders-test-input`), and I found 35 -999 orders. I replaced the nulling with a shared canonical filter that excludes those explicitly identified system tests. The canonical rescan kept its new 2,400-row baseline. It showed rows `[2400,2365]` and amount null rates `[0.0146,0.0]`:

```text
S1 extreme:amount: 9 -> 9 unchanged (Q-010)
S2 orphans:customer_id:customers.customer_id: 24 -> 24 unchanged (Q-011)
```

`stale` identified both findings through the changed committed code and the view SHA-256. The recorder created Q-015, flagged region-rates and west-gap as `revalidation-needed (was supported)`, and updated the canonical catalog. I superseded the active treatment of Q-004 and kept its historical correction row. I recorded the changed system-test meaning and the analytical impact. The duplicate/extreme/text observations of the publication scan restated the already settled Q-001/Q-002, Q-010 and Q-012. No analysis was rerun. Commit `50540e6`.

Usability gap: the skill does not explain how to reopen a hidden sentinel after an earlier correction. The extra publication scan supplied source evidence. The canonical rescan supplied the actual delta. The publication-based correction of the recorder has no automatic before/after count. For this reason, its rationale explicitly records the canonical delta and the unchanged publication.

## 11. Deliver latest state with accepted caveats

The initial release was refused: `flagged findings without a release disposition`, with two unmatched flags. I routed the revision through awb-package. I kept the prior chart bytes and results. `export --result region-rates --result west-gap` refreshed the recorded provenance, and it did not try to serialize stale results. I updated both narratives, each affected slide, the caveats/alt text of both charts, the changed-version slide and the exact manifest flags. I made clear the difference between the corrected population 2,365 and the displayed prior population 2,400. Both flags were represented throughout the findings/methodology and their charts.

I used the supplied choice `release_with_caveat` for both, and I recorded the questions. The check of the final draft was successful. I released `002` at `2026-10-13T10:50:56-04:00`. Both dispositions: `new: true`. Datasets: none. Provenance gaps [], checkout-only acquisitions [], verify []. Storage: `copied`, `compare_trees: []`. Release 001 stayed frozen. There was no unauthorized rerun or commit.

## 12. Rerun flagged findings; commit

I reviewed the flagged history/caveats and the current interpretation profile. Current counts: 2,365 source/scoped/unique orders, with the same H1 period and categorical values. The prior evidence was already committed. I suggested a commit before the rerun. I added a saved runtime count query and a reusable denominator/return-count reconciliation. For this, I adapted the producer in the investigation run.py, not the evidence machinery. I committed the implementation `493dce9`. Then I ran both flagged IDs. Each returned provisional with `state: flag cleared`, `history: true`, and no failed or unassessed checks. I reviewed the values and the prior history. Then I reworded and re-promoted the findings with the restored caveats.

Corrected findings: West 105/583 = 18.01% (Wilson 15.10–21.34%). South 9.74%, East 7.31%, North 6.23%. Overall 242/2,365 = 10.23%. West versus pooled others 7.69%: gap 10.32 points (Newcombe 7.13–13.84). West generates 43.39% of returns from 24.65% of orders. Descriptively, the individual gaps stay above the threshold. `stale` checked 2, stale 0. I recorded the package revision as the next work, and I kept the releases. Commit `4ee782f`. No failures.

The initial validation counts were observed static specifications. This rerun added runtime measurements/reconciliation, so that manual count maintenance is not necessary. No earlier interpretation depended on an incorrect count. The run scaffold of the project was adapted as its analysis guide prescribes. The bundled helper implementations stayed unopened.

## 13. Resume in new session

I read the project AGENTS and ran `awb.py state`, and I named region-returns. I reported two revalidated supported findings and the remaining recording-consistency question. I highlighted that draft/release 002 still contain prior figures with accepted caveats, and that they need an explicitly requested package revision. There was no analysis, no package writes and no failures.

## 14. Status

I ran the awb-status collector read-only. Result: two supported findings, no flags, no uncertainties, clean Git and state `indeterminate at date precision`. Both storage locations were reachable. There was one retained acquisition and there were zero checkout-only acquisitions. The draft was revised at `2026-10-13T10:50:37-04:00`. The latest release 002 was delivered at `10:50:56-04:00`. `draft_vs_release: same_or_older`, and there were no release-disposition blockers. I reported the next step that state recorded: the package revision.

Collector limitation: draft-versus-release compares package artifacts. It does not examine if their numerical contents agree with the newly rerun findings. It did not flag the old figures. The next-step record made that visible. There were no failures or modifications.

## 15. Bring workbench up to date

I read the awb-init repair reference, the target orientation/ignores and the active records. I ran the installer with `--upgrade`. All 11 helper/guide/package-format files were `current`. The requirements were declared, and the interpreter/dependencies passed. I compared AGENTS and README with the templates, and the investigation run.py too, through the prescribed no-index diffs. AGENTS matched. The README differences were only project-specific active/storage lines. run.py was different only by its intended runtime producer adaptation. The guide links resolve. No investigation is without run.py. No customized/retired decisions or repair writes were necessary. The existing records, paths and templates were kept. Data/cache stays deferred. A repair commit was not necessary.

The no-index diffs use exit 1 to show expected content differences. This exit code does not show failures that need recovery. The repair instructions say that you must compare the .py scaffold with its asset. This showed the adaptation diff. This diff was one more necessary inspection under the same blanket .py restriction that I noted in request 8. There was no debugging of helper source.

## 16. Initialize related channel investigation

I used awb-init. I read the active brief/findings as allowed related-method context. I used the supplied scoping answers. I created a fresh `channel-returns` brief/state/history/settings and the current run scaffold. I inherited these items: inclusive H1 dates, every channel, the returned/eligible metric, the Wilson/Newcombe methods, z, the 3-point threshold, shared canonical cleaning and the shared package format. I assumed each channel versus pooled others, a region-mix assessment and the inherited operations audit audience. I recorded these assumptions. I added shared sales-channel vocabulary. The findings are fresh. There are no result definitions, no analysis and no package. I switched the active investigation with `state switch channel-returns`. I confirmed that the installer files/dependencies are current.

Recording procedures stay an explicit unknown: export rates alone cannot prove channel recording differences. The region investigation, evidence and releases stay intact. There were no failures, no conflicts and no other lookup. README/glossary/new investigation are not committed, because this request did not ask for a commit. Suggested continuation: awb-status or awb-eda for orders in channel-returns, and a commit of these new records when the user requests it.

## Final verification

- `stale`: `{"checked": 2, "stale": 0, "skipped": [], "results": []}`.
- Both investigations have complete necessary records. Only region-returns has defined results.
- Both regional evidence records include the new shared validation operation.
- The raw originals match the inbox SHA-256s. The independently retained acquisition matches every file.
- Frozen releases 001 and 002 match their inventory checksums and every retained-copy file. There are no discrepancies.
- All explicitly requested commits are complete. There are 12 commits, which include separate implementation/provenance commits. No pushes.
- The remaining work is intentionally recorded: channel analysis/audit evidence, and a revision of the regional package to the corrected findings. The initialization of request 16 did not authorize either of them as analysis/package work.
