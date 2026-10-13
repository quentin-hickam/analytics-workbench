# Refined fix plan

This plan was refined on 2026-10-11 against gpt-6.1-sol (6 rounds). The exchange record is kept outside the repository. The sections below are the agreed contract that the workers implement.

F1+F5 helper (W1, awb_draft.py). On every successful export write, set manifest `revalidation_flags` from state_flags():

- If state.md flags nothing, set it to "none".
- If not, write one entry for each flag, in state.md row order:
  - If an existing entry has an identical finding and reason, keep that entry unchanged.
  - If not, write {"finding": verbatim, "reason": verbatim, "represented_in": [], "disposition": "none"}.
- Drop the entries that match no current flag.

If state.md is unreadable, do not change the field, and report `flags_error`. In that case, export still writes. Report `flags_pending`: [{finding, needs: "represented_in"|"disposition"}]. export's epilog names `flags_pending` and `flags_error`.

check-draft gets `flag_entries` (named in its epilog) ([{finding, problem}]) for these problems:

- The field is missing ("revalidation_flags is missing; rerun export").
- The field is not "none" or a list.
- An entry is not a dict, or it does not have a string finding/reason.
- represented_in is neither "none" nor a non-empty list of non-blank strings.
- A represented entry has a disposition that is not none/revalidate/omit/release_with_caveat.

`flag_entries == []` becomes part of `_structure_passed`, so that check-draft and release agree. disposition_problems does not change.

Tests for F1+F5: creation tests start from an absent manifest, because the fixture at tests/test_awb_draft.py:116 pre-seeds `revalidation_flags: "none"`. Preservation, changed-reason, cleared-flag, and unreadable-state tests seed the prior entries that they exercise. The tests are:

- none
- prefilled verbatim entry
- preserved exact-match choice
- changed reason -> fresh entry
- cleared flag dropped
- unreadable state -> flags_error + written
- flags_pending lists [] places and survivors at none
- check-draft and release refuse [] and missing field
- a flag raised after "none" still fails through unmatched_flags
- existing malformed-entry tests updated

F2 helper (W1). When there are display-name gaps, export adds `display_stub`. It has one line for each missing column in the form `"<column>" = ""` (TOML-quoted key), with duplicates removed, to go under [columns]. A blank or whitespace display name counts as missing. Tests: chart and dataset paths, and a dotted column.

F2 text (W2). In awb-package step 3, add a new first bullet: "Before writing, give each column a chart or dataset will export a display name from the glossary in `foundation/display.toml`, e.g. `[columns]` then `return_rate = "Return rate"`; **Data:** lines and dataset headers use these names." Gaps sentence for step 4: "When it lists display-name gaps, fill its `display_stub` under `[columns]` and rerun."

F3 (W2). Text for step 4: "For a revision that only adds caveats and keeps the exported files, pass every represented result with `--result` only; omit `--chart`, `--dataset`, and `--no-datasets`. When `export` reports `exports_blocked`, stop and report it." This text takes the place of the mid-paragraph clause, and includes its content.

F4 (W2). Add to awb-release step 1: "When README's `Released packages are kept at` line is missing, blank, or `not yet recorded`, ask where releases are kept and record it as in step 4 before releasing, so `release` copies it." The unrecorded branch of step 4 stays as a fallback.

F5 text (W2). Last paragraph of step 4: "`export` records each flag's finding and reason and lists `flags_pending`. Review every flag's `represented_in` against the revised draft and fill pending places per the contract; then for any represented flag whose disposition is still `none`, ask the user to revalidate, omit, or release with the caveat, and record the answer; without one it stays `none`." In the contract, change "Commands write every manifest field except revalidation_flags" to "Commands write every manifest field; in `revalidation_flags` you fill `represented_in` and the user's `disposition`." Change package-format/manifest-template.md line 38 to match.

F6 (W3, awb_landing.py). When foundation/sources.md is absent, record_acquisition builds an embedded SOURCES_TEMPLATE and the row in memory, and writes once. SOURCES_TEMPLATE is byte-equal to assets/workbench/foundation/sources.md, and a test checks this. The ledger reports `"created": true`. An existing file without an Acquisitions table still fails.

retain reports copied, conflict, matched, discrepancies:

- matched = the destination exists after the call with no discrepancies.
- conflict = an existing destination differs.

retain never overwrites. Drop the epilog's "can match and still report a conflict". The land/retain epilogs name `matched` and ledger `created`. Tests:

- land without sources.md exits 0 with the row and source_status missing
- template equality
- new, identical-existing, and differing-existing retain cases (update test_awb_landing.py:218)

F7 (W4, record_cleaning.py). If an `issues` key is not a scan id but equals exactly one Active-table ID, the key revises that row:

- The given judgment cells are set. The observation does not change.
- correction+change append a Correction row without a rescan suffix.
- A row whose marker names a different scan is rejected.
- Unmarked rows are accepted.
- Two decisions that resolve to one row (S1 and Q-004) are rejected.

Other keys fail with "issues not in the scan or the quality record". `{Q-004}` placeholders resolve. Dry-run does not change. Add to awb-clean step 6: "A decision on a recorded issue the scan no longer lists uses its quality ID, such as `"Q-004"`, as the key." Tests include: DQ- prefix, alias collision, foreign marker, dry-run.

F8 (lead). Append to awb-eda step 5: "with `python3 src/awb.py state issues --add "<text>"` and `state next --add "<text>" --drop <number>` in one call." There is no provenance change.

F9a (W3). publish prints `view_sql`: `CREATE VIEW "<dataset>" AS SELECT * FROM read_parquet('<published>/<dataset>.parquet');`, with identifier and literal escaping. Text for data.md line 33: "starting from the printed `view_sql` and `catalog_row`". Test through session(), including `order-items` and an apostrophe.

F9b is dropped (shared). F9c (lead). Text for analysis.md: "`--text --status --reason --caveat` in one call".

Partition:

- W1: awb_draft.py + tests/test_awb_draft.py
- W2: awb-package SKILL.md, references/package-contract.md, assets/package-format/manifest-template.md, awb-release SKILL.md (no tests)
- W3: awb_landing.py, workbench-guides/data.md, tests/test_awb_landing.py
- W4: record_cleaning.py, awb-clean SKILL.md, tests/test_awb_clean.py
- lead: awb-eda SKILL.md, analysis.md, CHANGELOG.md

All start at the same time from this contract. Each runs the full suite. The lead does these steps, in this order:

- Merge W1, W2, W3, W4 in this order.
- Run the suite again.
- Measure instruction growth with scripts/measure-instruction-load.py's measure(). Use identical reading-path file sets (each touched SKILL.md, package-contract.md, data.md, analysis.md) at the pinned base SHA and at the merged result.
- Report the words added for each scenario.

Fixed interface:

- export: the revalidation_flags sync rule, `flags_pending`, `flags_error`, `display_stub`
- check-draft: `flag_entries` inside `_structure_passed`

Escalated: F3 mixed omission (omit one stale chart, keep another stale chart with an accepted caveat) is a workflow that existed before and is not supported. A full export blocks. A provenance-only export keeps the omitted chart. This case needs explicit handling, with one of these options:

- Manual removal of the specification, file, and manifest `charts` entry before a provenance refresh.
- Helper support.

In this case, the plan's text stops and reports, as today.


## Escalated, not implemented

- F3 mixed omission (omit one stale chart, keep another stale chart with an accepted caveat) is an existing workflow that the helpers do not support. The stale chart that is kept blocks a full export. A provenance-only export keeps the omitted chart, and its guard needs the result of every recorded chart. This case needs explicit handling, with one of these options:
  - Remove the specification, chart file, and manifest `charts` entry by hand before a provenance refresh.
  - Add helper support (a feature, outside this scope).

  The plan's text stops and reports in this case, as today. The audit did not exercise this case (task 11 had one chart). User decision: accept as documented, or schedule a follow-up.

