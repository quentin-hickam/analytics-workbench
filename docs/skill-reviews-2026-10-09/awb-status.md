# Review: awb-status

Scope read in full: `.agents/skills/awb-status/SKILL.md` (35 lines), `.agents/skills/awb-status/references/next-requests.md` (21 lines), and the agent-facing surface of `scripts/collect_status.py` (docstring, `--help`, every emitted JSON field, traced through the implementation). For R10/R12 cross-checks I also read: `awb-init/assets/workbench/AGENTS.md`, the sibling descriptions, `awb-release/SKILL.md:20-68`, `awb-package/references/package-contract.md:39-43`, `awb-package/assets/package-format/manifest-template.md:39`, `awb-init/assets/workbench/README.md`, `foundation/sources.md`, `investigation/state.md`, and `workbench-guides/data.md`.

## Summary

The skill is short and its shape is sound: a read-only status report, a helper that does the parsing, interpretation rules, then a report and next-request map. The main weakness is the boundary between SKILL.md and the helper. SKILL.md re-derives in prose most of what the helper already computes (counts, staleness, draft-vs-release, retained copies), but it never names the fields that carry those verdicts (`git.staleness`, `draft_vs_release`, `comparison_is_estimate`, `confirmed_without_disposition`, `flags_since_draft`, `acquisitions.without_retained_copy`, `workbench`). It also misstates some field semantics. The blanket `null` rule treats legitimate absences such as "no active investigation" or "never released" as unknowns. Root selection can send an agent to `awb-init` on an existing workbench. The disposition rule contradicts the "materially the same" rule in awb-package and awb-release. Lines 20 and 25 are dense paragraphs that mix steps and reference, and the next-request map is behind a pointer that every run follows anyway. Fixing the field mapping and the three high findings would remove most run-to-run variance.

## Findings

### High

**F1. High · R12 (mismatch with helper behaviour) · SKILL.md:18**
Root selection defaults to the current directory. The helper only detects a workbench at the exact root it is given. An agent started in a subdirectory, or at the root of a larger repository that contains the workbench (a case line 18 itself names), gets `"workbench": false` and is told to "stop and suggest `awb-init`" on a project that already has one. That is the wrong action.
> "Use the user-named project, otherwise the current directory. … A non-workbench result means stop and suggest `awb-init`."

Fix: replace both sentences with: "Use the user-named project; otherwise the nearest directory at or above the current one whose `README.md` has an `Active investigation:` line, else the current directory. If the helper returns `\"workbench\": false`, look one level for such a README below the current directory before suggesting `awb-init`."

**F2. High · R11/R12 (field semantics) · SKILL.md:20**
The blanket rule turns every `null` into an uncertainty. But many emitted nulls mean a real absence with no uncertainty recorded: `active: null` is README `Active investigation: none` (next-requests row 7), `latest_release: null` is never released (row 12), `revised_at: null` is no draft, and `draft_vs_release: null` is "nothing to compare". Under this rule the agent may chase reads for facts it already has, or suppress "Start an investigation" and "Mark delivered" requests. The helper always adds an `uncertainties` entry when a null comes from a parse or read failure, so that pairing is the correct test.
> "Treat `null`, `unknown`, and `uncertainties` as targeted fallback requests, never as empty findings or zero risk."

Fix: "A `null` is unknown when an `uncertainties` entry names its record: resolve it with one targeted read or report it unknown, never as zero. Other nulls are absences: `active: null` means no active investigation, `latest_release: null` means never released, `revised_at: null` means no draft. `unknown` availability or staleness stays unknown until checked."

**F3. High · R10 (contradiction across skills) · SKILL.md:25**
Two problems in one bullet:
1. "A disposition applies only to the same finding and current reason" is stricter than the authoritative rule. `awb-package/references/package-contract.md:43` keeps a disposition while the finding, evidence, and reason stay "materially the same", and `awb-release/SKILL.md:32` says the same. So a reworded reason counts as lacking a disposition in status but not in release.
2. "An unmatched finding represented there was flagged since the draft revision" is a wrong inference whenever the mismatch has another cause: a reworded reason, a malformed `revalidation_flags` (the helper then routes every flagged finding to `representation_review`), or a flag the draft simply failed to record. The report then states a false history, and row 10 of next-requests repeats it.
> "An unmatched finding represented there was flagged since the draft revision. … A disposition applies only to the same finding and current reason"

Fix: rewrite the bullet as: "For each `representation_review` entry, read `review_methodology` and decide whether the package represents that finding. If it does, report it as lacking a current manifest disposition, replacing the `flags_since_draft` placeholder with those findings. Add `confirmed_without_disposition`. Whether an older disposition still covers a reworded reason is decided at release (package-contract.md); report such cases as needing review." Delete the sentence about the same finding and current reason. Its single source of truth is `package-contract.md:43`. In next-requests.md:10, change "flagged since the draft was revised" to "lacking a current disposition".

### Medium

**F4. Medium · R11 (cache of helper logic; unnamed fields) · SKILL.md:24, 26, 27, 29; next-requests.md:14, 18**
SKILL.md re-derives computations the helper has already done and emits as named fields, without naming those fields. The agent may recompute the result and diverge, or report a raw placeholder such as `flags_since_draft: "unknown until representation review"` verbatim. Each restatement and the field that already carries it:

| Restatement | Field that already carries it |
| --- | --- |
| "Count statuses… `revalidation-needed (was supported)` belongs only in needs revalidation" (24) | `active.counts` (already folds the prefix) |
| "Use the helper's commit/change dates and day difference for staleness. Same-day comparisons are indeterminate" (26) | `git.staleness`, `git.days_after_state` |
| "With no commits, say 'no commits yet; all work uncommitted.'" (26) | `git.commit_comparison` (identical string) |
| "Compare draft `revised_at` with the highest numeric release's `released_at`. File modification time is an estimate…" (27) | `draft_vs_release`, `comparison_is_estimate` |
| "an acquisition has a blank retained copy or `this checkout only`" (29); "`none chosen`" (next-requests 14) | `acquisitions.without_retained_copy`; `none chosen` is already mapped to `availability: "unrecorded"` |
| "A non-workbench result" (18) | `workbench: false` |

Fix: replace these sentences with a compact field map under Interpret:
- `workbench` false → see F1
- `active.counts` → status counts
- `git.staleness` (with `days_after_state`) and `git.commit_comparison` → report as emitted
- `packages[].draft_vs_release` → report as emitted; say "estimated" when `comparison_is_estimate` is true
- `confirmed_without_disposition` plus the review result → findings without dispositions
- `acquisitions.without_retained_copy` and `*_storage.availability` → storage risk

In next-requests.md, row 14 becomes "landed-data storage at risk (see Interpret)" and row 18 becomes "`git.staleness` is `stale`".

**F5. Medium · R6 (unexecutable instruction) · SKILL.md:26**
The timezone instruction cannot be carried out. No workbench record holds a "reporting timezone". The helper emits mtimes only as dates, so converting would mean re-statting files, which line 18 discourages. Git dates use the committer's timezone. Different agents will either skip the instruction or improvise.
> "if it differs from the user's reporting timezone and changes the comparison, convert those timestamps before reporting."

Fix: replace the sentence with: "When `days_after_state` is within one day, say the staleness verdict is approximate (`mtime_date_basis`)."

**F6. Medium · R6 (conflicting bound; no exhaustive bar) · SKILL.md:33**
"Keep the report to one screen" competes with "every flag/reason" and per-package dates, comparison, and disposition counts. With many flags, agents will resolve the conflict differently. The skill also lacks a done-criterion for the uncertainty work, so "expose material uncertainties" leaves "material" to judgement.
> "Keep the report to one screen: … findings counts and every flag/reason; …"

Fix: "Aim for one screen; when flags overflow it, group findings that share a reason. Completeness of flags, risks, and uncertainties wins over length." End Interpret with: "Done when every `uncertainties` and `representation_review` entry is resolved or reported as unknown."

**F7. Medium · R3 (over-disclosure) · SKILL.md:35 → references/next-requests.md**
Every run that reaches Report must read next-requests.md, so the pointer adds a hop without saving context, and a skipped read lets the agent improvise requests the map forbids. The only branch that skips it is `workbench: false`, which already stops early. Moving the file also exposes duplication (see F12).
> "Read [next-requests.md](references/next-requests.md) to select requests and their handlers; offer only applicable entries from that map."

Fix: inline the table as a `### You can ask for` subsection under Report, keeping next-requests.md:3's phrasing rule ("a sentence the user could type, handler in parentheses"). Delete next-requests.md:21 and the reference file.

**F8. Medium · R4/R3 (fragmented meanings; reference under a step) · SKILL.md:20, 25, 27, 28, 29, 33; next-requests.md:8, 13–14**
- Line 20 sits under **Collect** but is interpretation reference: nine separate rules about nulls, custom formats, missing records, storage lines, inventories, Git, and what to skip. It buries the one-command step above it.
- Storage meaning is split three ways: absent line means unrecorded (20), the risk rule (29), and restated state conditions (next-requests 13–14).
- Uncertainty handling is split across 20, 25 ("malformed flags need manual review"), 27 ("malformed values remain unknown"), and 33 ("expose material uncertainties").
- The open-decision rule (28) lives apart from the row it gates (next-requests 8).
> "Absent optional storage lines mean unrecorded storage; they matter when acquisitions or releases exist."

Fix: cut Collect down to the command, root choice (F1), and "run without reading the implementation". Move line 20 into Interpret as an **Uncertainties** bullet (holding F2's rule plus custom formats, Git fallback, and `release_inventory_known`) and fold the storage sentence into the **Storage** bullet at 29. Next-requests rows 13–14 then refer to that bullet. Put line 28's test into row 8's State cell: "a scope or purpose decision explicitly recorded as open (material unknowns alone do not count)".

**F9. Medium · R8 (term collision) · SKILL.md:20**
"Targeted fallback requests" reuses *requests*, the skill's word for user-facing next requests ("You can ask for"). An agent could list unresolved nulls among the offered requests.
> "as targeted fallback requests"

Fix: "as prompts for one targeted read" (F2's rewrite already uses this).

### Low

**F10. Low · R1 · SKILL.md:3**
The description lists contents the body carries ("revalidation flags, package and storage state"), and that list is paid on every turn. The trigger branches ("where things stand", "what to do next") are distinct and fine. Model invocation is appropriate: AGENTS.md:9, awb-init:72, and README:41 send agents here.
> "Report analytics workbench status, revalidation flags, package and storage state, and relevant next requests."

Fix: "Report analytics workbench status and the requests that fit next. Use when the user asks where things stand or what to do next. Read-only."

**F11. Low · R9 · SKILL.md:8 (also 18, 20, 35; next-requests.md:3)**
A stack of five prohibitions names the very actions it bans (analysis, cache refresh, source queries, commits). The positive target appears only in the last clause.
> "Change no files, run no analysis, refresh no caches, query no sources, and make no commit."

Fix: "The only actions are running the helper and reading the records it names; offer every fix as a next request." Keep "without reading its implementation" (18) as a paired guardrail.

**F12. Low · R10/R13 · SKILL.md:20, 35; next-requests.md:3, 21**
The read-only rule is restated twice after line 8, and both restatements are no-ops given line 8. The "up to five, risk first then progress, only from the map" rule appears three times.
> "Missing records are facts to report, not permission to create them." / "Reporting never performs those follow-up actions."

Fix: delete both sentences. Keep the ordering and limit rule once, in the inlined table header (F7). Delete SKILL.md:35's "risk first then progress" and next-requests.md:21.

**F13. Low · R12 (exposition) · SKILL.md:18, 26**
Implementation notes the agent never acts on, and which `--help` and the output already show.
> "It reads standard Markdown records, JSON manifests, local storage availability, and Git with optional locks disabled, including projects inside larger repositories."

Fix: delete that sentence and "It reads other investigations only for names and state dates." In 26, delete "deleted files lack modification dates": the helper emits `undated_changes` together with an uncertainty.

**F14. Low · R8 (synonyms and coined terms) · SKILL.md:24, 25**
"semantic review" (25) and the field name "representation review" (`representation_review`, `flags_since_draft`) name the same act. "needs revalidation" (24) and the status token `revalidation-needed` name the same status. "unmatched" and "confirmed subsets" are coined terms.
> "Helper counts are confirmed subsets until semantic review finishes"

Fix: use "representation review" and `revalidation-needed` throughout. Replace the sentence with "Helper counts are lower bounds until representation review finishes."

**F15. Low · R6/R12 · next-requests.md:21, 17**
The risk order "(revalidation, storage, staleness)" leaves out the package-caveat risk row (10), so where it falls in the order is a coin-flip. Row 17's handler "explicit commit request" routes nowhere, which defeats the point of the handler column.
> "ordered by risk first (revalidation, storage, staleness), then progress."

Fix: "risk rows in table order, then progress rows in table order". Set row 17's handler to "commit under AGENTS.md".

**F16. Low · R2 · SKILL.md:24**
The pointer condition "needs explanation" is a judgement call. The agent cannot tell whether it is on that branch.
> "only when a reason points to one and needs explanation"

Fix: "only when a flag reason cites a `quality.md` ID without saying what changed."

**F17. Low · R5 · SKILL.md:20, 25**
The file is short, but lines 20 and 25 are roughly 110- and 120-word single paragraphs. Applying F4, F8, and F12 cuts about 30% and turns both into bullets.

**F18. Low · R12 (internal tension) · SKILL.md:8 vs 29**
"query no sources" sits beside "a read-only check through the established access method" for storage that may be remote, such as SharePoint. The helper comment rules out speculative network calls. Agents will split on whether to probe.
> "Unknown availability needs a read-only check through the established access method or an explicit 'not verified.'"

Fix: "Unknown availability: check only through an already-configured local path or connector; otherwise report 'not verified'."

## Rubric coverage

- R1: F10
- R2: F16
- R3: F7, F8
- R4: F8
- R5: F17
- R6: F5, F6, F15
- R7: clean (no fuzzy step tempts rushing; model invocation fits, and nothing should split off)
- R8: F9, F14
- R9: F11
- R10: F3, F12
- R11: F2, F4
- R12: F1, F13, F18
- R13: F12

## Top 3 changes

1. **Map SKILL.md onto the emitted fields (F4 + F2 + F3).** Replace the prose that re-derives counts, staleness, draft-vs-release, and retained copies with a short field map: `active.counts`, `git.staleness`/`commit_comparison`, `draft_vs_release`/`comparison_is_estimate`, `confirmed_without_disposition`, `flags_since_draft`, `acquisitions.without_retained_copy`, `*_storage.availability`. Restate the null rule as "null is unknown only when `uncertainties` names its record". Drop the stricter disposition rule in favour of package-contract.md:43.
2. **Fix root selection (F1).** Search for the README `Active investigation:` line at or above the current directory, plus one level below a repository root, before treating `workbench: false` as "suggest `awb-init`".
3. **Restructure for co-location (F8 + F7 + F6).** Leave Collect as just the command. Move line 20 into Interpret as **Uncertainties** and **Storage** bullets. Inline the next-requests table under Report. Settle the one-screen versus every-flag conflict, and add the done-criterion "every `uncertainties` and `representation_review` entry resolved or reported unknown".
