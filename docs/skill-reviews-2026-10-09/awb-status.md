# Review: awb-status

Scope read in full: `.agents/skills/awb-status/SKILL.md` (35 lines), `.agents/skills/awb-status/references/next-requests.md` (21 lines), and the agent-facing surface of `scripts/collect_status.py` (docstring, `--help`, every JSON field that it emits, traced through the implementation). For R10/R12 cross-checks I also read: `awb-init/assets/workbench/AGENTS.md`, the sibling descriptions, `awb-release/SKILL.md:20-68`, `awb-package/references/package-contract.md:39-43`, `awb-package/assets/package-format/manifest-template.md:39`, `awb-init/assets/workbench/README.md`, `foundation/sources.md`, `investigation/state.md`, and `workbench-guides/data.md`.

## Summary

The skill is short, and its shape is good. It has a read-only status report, a helper that does the parse work, interpretation rules, then a report and a next-request map.

The main weakness is the boundary between SKILL.md and the helper. In prose, SKILL.md re-derives most of what the helper already calculates (counts, staleness, draft-vs-release, retained copies). But it never names the fields that carry those verdicts (`git.staleness`, `draft_vs_release`, `comparison_is_estimate`, `confirmed_without_disposition`, `flags_since_draft`, `acquisitions.without_retained_copy`, `workbench`). It also gives an incorrect meaning for some fields.

There are also these problems:
- The blanket `null` rule treats valid absences as unknowns, for example "no active investigation" or "never released".
- Root selection can send an agent to `awb-init` on an existing workbench.
- The disposition rule contradicts the "materially the same" rule in awb-package and awb-release.
- Lines 20 and 25 are dense paragraphs that mix steps and reference.
- The next-request map is behind a pointer that every run follows anyway.

A fix to the field mapping and to the three high findings will remove most run-to-run variance.

## Findings

### High

**F1. High · R12 (mismatch with helper behaviour) · SKILL.md:18**
By default, root selection uses the current directory. The helper detects a workbench only at the exact root that it gets. Consider an agent that starts in a subdirectory, or at the root of a larger repository that contains the workbench (line 18 itself names this case). This agent gets `"workbench": false`. Then the skill tells it to "stop and suggest `awb-init`" on a project that already has a workbench. That is the wrong action.
> "Use the user-named project, otherwise the current directory. … A non-workbench result means stop and suggest `awb-init`."

Fix: Replace both sentences with: "Use the user-named project; otherwise the nearest directory at or above the current one whose `README.md` has an `Active investigation:` line, else the current directory. If the helper returns `\"workbench\": false`, look one level for such a README below the current directory before suggesting `awb-init`."

**F2. High · R11/R12 (field semantics) · SKILL.md:20**
The blanket rule turns every `null` into an uncertainty. But many nulls that the helper emits mean a real absence, and no uncertainty is recorded for them:
- `active: null` is README `Active investigation: none` (next-requests row 7).
- `latest_release: null` is never released (row 12).
- `revised_at: null` is no draft.
- `draft_vs_release: null` is "nothing to compare".

With this rule, the agent can possibly do reads for facts that it already has. It can also possibly suppress the "Start an investigation" and "Mark delivered" requests. When a null comes from a parse or read failure, the helper always adds an `uncertainties` entry. For this reason, that pairing is the correct test.
> "Treat `null`, `unknown`, and `uncertainties` as targeted fallback requests, never as empty findings or zero risk."

Fix: "A `null` is unknown when an `uncertainties` entry names its record: resolve it with one targeted read or report it unknown, never as zero. Other nulls are absences: `active: null` means no active investigation, `latest_release: null` means never released, `revised_at: null` means no draft. `unknown` availability or staleness stays unknown until checked."

**F3. High · R10 (contradiction across skills) · SKILL.md:25**
One bullet has two problems:
1. "A disposition applies only to the same finding and current reason" is stricter than the authoritative rule. `awb-package/references/package-contract.md:43` keeps a disposition while the finding, evidence, and reason stay "materially the same". `awb-release/SKILL.md:32` says the same. As a result, in status a reworded reason counts as one with no disposition, but in release it does not.
2. "An unmatched finding represented there was flagged since the draft revision" is a wrong inference every time that the mismatch has a different cause. The other causes are:
   - a reworded reason
   - a malformed `revalidation_flags` (the helper then routes every flagged finding to `representation_review`)
   - a flag that the draft failed to record.

   Then the report states a false history, and row 10 of next-requests repeats it.
> "An unmatched finding represented there was flagged since the draft revision. … A disposition applies only to the same finding and current reason"

Fix: Rewrite the bullet as: "For each `representation_review` entry, read `review_methodology` and decide whether the package represents that finding. If it does, report it as lacking a current manifest disposition, replacing the `flags_since_draft` placeholder with those findings. Add `confirmed_without_disposition`. Whether an older disposition still covers a reworded reason is decided at release (package-contract.md); report such cases as needing review." Delete the sentence about the same finding and current reason. Its single source of truth is `package-contract.md:43`. In next-requests.md:10, change "flagged since the draft was revised" to "lacking a current disposition".

### Medium

**F4. Medium · R11 (cache of helper logic, unnamed fields) · SKILL.md:24, 26, 27, 29 and next-requests.md:14, 18**
SKILL.md re-derives calculations that the helper already did and emits as named fields. But SKILL.md does not name those fields. The agent can possibly calculate the result again and get a different result. Or it can report a raw placeholder verbatim, for example `flags_since_draft: "unknown until representation review"`. The table gives each restatement and the field that already carries it:

| Restatement | Field that already carries it |
| --- | --- |
| "Count statuses… `revalidation-needed (was supported)` belongs only in needs revalidation" (24) | `active.counts` (it already folds the prefix) |
| "Use the helper's commit/change dates and day difference for staleness. Same-day comparisons are indeterminate" (26) | `git.staleness`, `git.days_after_state` |
| "With no commits, say 'no commits yet; all work uncommitted.'" (26) | `git.commit_comparison` (the same string) |
| "Compare draft `revised_at` with the highest numeric release's `released_at`. File modification time is an estimate…" (27) | `draft_vs_release`, `comparison_is_estimate` |
| "an acquisition has a blank retained copy or `this checkout only`" (29), and "`none chosen`" (next-requests 14) | `acquisitions.without_retained_copy`. The helper already maps `none chosen` to `availability: "unrecorded"`. |
| "A non-workbench result" (18) | `workbench: false` |

Fix: Replace these sentences with a compact field map under Interpret:
- `workbench` false → see F1
- `active.counts` → status counts
- `git.staleness` (with `days_after_state`) and `git.commit_comparison` → report as emitted
- `packages[].draft_vs_release` → report as emitted, and say "estimated" when `comparison_is_estimate` is true
- `confirmed_without_disposition` plus the review result → findings without dispositions
- `acquisitions.without_retained_copy` and `*_storage.availability` → storage risk

In next-requests.md, change row 14 to "landed-data storage at risk (see Interpret)" and row 18 to "`git.staleness` is `stale`".

**F5. Medium · R6 (unexecutable instruction) · SKILL.md:26**
The agent cannot do the timezone instruction. No workbench record holds a "reporting timezone". The helper emits mtimes only as dates. For this reason, a conversion will need the agent to re-stat files, and line 18 discourages this. Git dates use the timezone of the committer. Different agents will either skip the instruction or improvise.
> "if it differs from the user's reporting timezone and changes the comparison, convert those timestamps before reporting."

Fix: Replace the sentence with: "When `days_after_state` is within one day, say the staleness verdict is approximate (`mtime_date_basis`)."

**F6. Medium · R6 (conflicting bound, no exhaustive bar) · SKILL.md:33**
The text "Keep the report to one screen" competes with "every flag/reason". It also competes with the dates, comparison, and disposition counts for each package. When there are many flags, agents will resolve the conflict in different ways. The skill also has no done-criterion for the uncertainty work. As a result, "expose material uncertainties" leaves "material" to judgement.
> "Keep the report to one screen: … findings counts and every flag/reason; …"

Fix: "Aim for one screen; when flags overflow it, group findings that share a reason. Completeness of flags, risks, and uncertainties wins over length." End Interpret with: "Done when every `uncertainties` and `representation_review` entry is resolved or reported as unknown."

**F7. Medium · R3 (over-disclosure) · SKILL.md:35 → references/next-requests.md**
Every run that gets to Report must read next-requests.md. For this reason, the pointer adds a hop and does not save context. Also, if the agent skips the read, it can improvise requests that the map forbids. Only the `workbench: false` branch skips it, and this branch already stops early. A move of the file also exposes duplication (see F12).
> "Read [next-requests.md](references/next-requests.md) to select requests and their handlers; offer only applicable entries from that map."

Fix: Inline the table as a `### You can ask for` subsection under Report. Keep the phrasing rule of next-requests.md:3 ("a sentence the user could type, handler in parentheses"). Delete next-requests.md:21 and the reference file.

**F8. Medium · R4/R3 (fragmented meanings, reference under a step) · SKILL.md:20, 25, 27, 28, 29, 33 and next-requests.md:8, 13–14**
- Line 20 is under **Collect**, but it is interpretation reference. It has nine separate rules about nulls, custom formats, missing records, storage lines, inventories, Git, and what to skip. It buries the one-command step above it.
- The storage meaning is split three ways: absent line means unrecorded (20), the risk rule (29), and restated state conditions (next-requests 13–14).
- The uncertainty rules are split across 20, 25 ("malformed flags need manual review"), 27 ("malformed values remain unknown"), and 33 ("expose material uncertainties").
- The open-decision rule (28) is in a different place from the row that it gates (next-requests 8).
> "Absent optional storage lines mean unrecorded storage; they matter when acquisitions or releases exist."

Fix: Reduce Collect to the command, the root choice (F1), and "run without reading the implementation". Move line 20 into Interpret as an **Uncertainties** bullet. This bullet holds the F2 rule, plus custom formats, Git fallback, and `release_inventory_known`. Merge the storage sentence into the **Storage** bullet at 29. Then next-requests rows 13–14 refer to that bullet. Put the test from line 28 into the State cell of row 8: "a scope or purpose decision explicitly recorded as open (material unknowns alone do not count)".

**F9. Medium · R8 (term collision) · SKILL.md:20**
The text "Targeted fallback requests" uses *requests* again. In this skill, *requests* is the word for the next requests that the user sees ("You can ask for"). An agent can possibly list unresolved nulls among the requests that it offers.
> "as targeted fallback requests"

Fix: "as prompts for one targeted read" (the F2 rewrite already uses this).

### Low

**F10. Low · R1 · SKILL.md:3**
The description lists contents that the body carries ("revalidation flags, package and storage state"). The cost of that list is paid on every turn. The trigger branches ("where things stand", "what to do next") are distinct and good. Model invocation is correct, because AGENTS.md:9, awb-init:72, and README:41 send agents here.
> "Report analytics workbench status, revalidation flags, package and storage state, and relevant next requests."

Fix: "Report analytics workbench status and the requests that fit next. Use when the user asks where things stand or what to do next. Read-only."

**F11. Low · R9 · SKILL.md:8 (also 18, 20, 35 and next-requests.md:3)**
A stack of five prohibitions names exactly the actions that it bans (analysis, cache refresh, source queries, commits). The positive target occurs only in the last clause.
> "Change no files, run no analysis, refresh no caches, query no sources, and make no commit."

Fix: "The only actions are running the helper and reading the records it names; offer every fix as a next request." Keep "without reading its implementation" (18) as a paired guardrail.

**F12. Low · R10/R13 · SKILL.md:20, 35 and next-requests.md:3, 21**
The skill restates the read-only rule twice after line 8. Because of line 8, both restatements are no-ops. The "up to five, risk first then progress, only from the map" rule occurs three times.
> "Missing records are facts to report, not permission to create them." / "Reporting never performs those follow-up actions."

Fix: Delete both sentences. Keep the order and limit rule one time, in the header of the inlined table (F7). Delete "risk first then progress" from SKILL.md:35 and delete next-requests.md:21.

**F13. Low · R12 (exposition) · SKILL.md:18, 26**
These are implementation notes. The agent never acts on them, and `--help` and the output already show them.
> "It reads standard Markdown records, JSON manifests, local storage availability, and Git with optional locks disabled, including projects inside larger repositories."

Fix: Delete that sentence and "It reads other investigations only for names and state dates." In 26, delete "deleted files lack modification dates", because the helper emits `undated_changes` together with an uncertainty.

**F14. Low · R8 (synonyms and coined terms) · SKILL.md:24, 25**
"semantic review" (25) and the field name "representation review" (`representation_review`, `flags_since_draft`) name the same act. "needs revalidation" (24) and the status token `revalidation-needed` name the same status. "unmatched" and "confirmed subsets" are coined terms.
> "Helper counts are confirmed subsets until semantic review finishes"

Fix: Use "representation review" and `revalidation-needed` in all places. Replace the sentence with "Helper counts are lower bounds until representation review finishes."

**F15. Low · R6/R12 · next-requests.md:21, 17**
The risk order "(revalidation, storage, staleness)" omits the package-caveat risk row (10). As a result, the position of this row in the order is random. Row 17's handler "explicit commit request" routes nowhere. This defeats the purpose of the handler column.
> "ordered by risk first (revalidation, storage, staleness), then progress."

Fix: "risk rows in table order, then progress rows in table order". Set the handler of row 17 to "commit under AGENTS.md".

**F16. Low · R2 · SKILL.md:24**
The pointer condition "needs explanation" is a judgement call. The agent cannot know if it is on that branch.
> "only when a reason points to one and needs explanation"

Fix: "only when a flag reason cites a `quality.md` ID without saying what changed."

**F17. Low · R5 · SKILL.md:20, 25**
The file is short. But lines 20 and 25 are single paragraphs of about 110 and 120 words. When you apply F4, F8, and F12, they cut about 30% and change both paragraphs into bullets.

**F18. Low · R12 (internal tension) · SKILL.md:8 vs 29**
The text "query no sources" is in the same skill as "a read-only check through the established access method". This check is for storage that can be remote, for example SharePoint. The helper comment excludes speculative network calls. Some agents will probe and others will not.
> "Unknown availability needs a read-only check through the established access method or an explicit 'not verified.'"

Fix: "Unknown availability: check only through an already-configured local path or connector; otherwise report 'not verified'."

## Rubric coverage

- R1: F10
- R2: F16
- R3: F7, F8
- R4: F8
- R5: F17
- R6: F5, F6, F15
- R7: clean (no fuzzy step tempts the agent to rush, model invocation fits, and we recommend that no part splits off)
- R8: F9, F14
- R9: F11
- R10: F3, F12
- R11: F2, F4
- R12: F1, F13, F18
- R13: F12

## Top 3 changes

1. **Map SKILL.md onto the emitted fields (F4 + F2 + F3).** Remove the prose that re-derives counts, staleness, draft-vs-release, and retained copies. Put a short field map in its place:
   - `active.counts`
   - `git.staleness`/`commit_comparison`
   - `draft_vs_release`/`comparison_is_estimate`
   - `confirmed_without_disposition`
   - `flags_since_draft`
   - `acquisitions.without_retained_copy`
   - `*_storage.availability`

   Write the null rule again as "null is unknown only when `uncertainties` names its record". Remove the stricter disposition rule, and use package-contract.md:43 in its place.
2. **Fix root selection (F1).** Before you treat `workbench: false` as "suggest `awb-init`", search for the README `Active investigation:` line. Search at or above the current directory, plus one level below a repository root.
3. **Restructure for co-location (F8 + F7 + F6).** Make Collect only the command. Move line 20 into Interpret as **Uncertainties** and **Storage** bullets. Inline the next-requests table under Report. Resolve the conflict between one screen and every flag. Add the done-criterion "every `uncertainties` and `representation_review` entry resolved or reported unknown".
