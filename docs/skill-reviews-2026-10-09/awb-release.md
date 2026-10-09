# Review: awb-release

Scope read in full: `.agents/skills/awb-release/SKILL.md`; pointed-at `.agents/skills/awb-package/references/package-contract.md`, `manifest-helper.md`, `findings-helper.md`; `.agents/skills/awb-package/SKILL.md`. For R10/R12 cross-checks: `awb-package/assets/package-format/manifest-template.md`, `awb-init/assets/workbench/AGENTS.md`, `awb-init/assets/workbench/README.md`, `awb-init/assets/workbench/workbench-guides/data.md` (storage lines), `awb-status/SKILL.md`, `awb-status/references/next-requests.md`, `awb-status/scripts/collect_status.py` (storage parsing). Authority: `writing-for-agents` SKILL.md and SKILL-MECHANICS.md.

## Summary

awb-release is a well-ordered step document: every heading is a step, the verify, disposition, re-verify sequence ends on checkable helper results, and the storage branch has an exhaustive bar ("each existing numbered release"). Its two weakest points are run-to-run variance in the critical disposition step and a broken pointer path on the storage-only branch. The test for whether a recorded disposition still applies is the vague "materially the same", stated twice and inconsistently, while awb-package and awb-status use a checkable "same recorded reason" test. The storage-only branch skips **Verify the draft**, so it never reaches `manifest-helper.md`, and that file is the only place the bundled `compare_trees` helper's location is given. The rest is load: the "a release is a frozen copy" meaning is restated as five separate prohibitions, and the rerun/no-hand-check/recorded-inventory rules are repeated across this skill, the contract and both helper references.

## Findings

### High

**F1. R6 / R10. `SKILL.md:32`, `SKILL.md:40`. The disposition applicability test is vague and duplicated inconsistently.**
Whether a recorded disposition still applies decides whether the release stops and asks the user. "Materially the same" is a judgement call, so the outcome will vary from run to run. The skill states the test twice. Line 32 includes "a flag raised or changed since then reopens it". Line 40 drops that clause. The siblings use a checkable test: awb-package:51 resets on a changed reason, and awb-status:26 says "same finding and current reason".
Quote (line 40): "A recorded disposition stays applicable while the finding and its evidence remain materially the same."
Fix: Delete line 40's last sentence. Replace line 32's last two sentences with a checkable criterion that uses the manifest fields: "A recorded disposition applies when its `finding` and `reason` match the finding and reason currently in `state.md`, every place now representing the finding has a disposition other than `none`, and no history entry for that finding postdates its `disposition_recorded_at`. Otherwise it is reopened."

**F2. R2. `SKILL.md:8`, `SKILL.md:52`, `SKILL.md:58`. The storage-only branch never reaches the helper location.**
Line 8 sends a storage-only request "directly" to **Record storage without releasing**. That branch runs **Copy to storage**, which says to copy the helper "as in **Verify the draft**". That step never ran on this branch, and it holds no path anyway. Only `manifest-helper.md` gives the bundled `awb_manifest.py` location and the reporting rules for large discrepancy lists. If the project lacks `src/packaging/manifest.py`, the agent must improvise, which invites a hand comparison or a skipped check.
Quote (line 52): "copying the helper first as in **Verify the draft** if it is missing"
Fix: In **Copy to storage**, replace that clause with a direct pointer: "Read the [manifest helper interface](../awb-package/references/manifest-helper.md), which says where to install the helper when the project lacks it, then run `compare_trees(local_dir=<release>, copy_dir=<copy>)`."

### Medium

**F3. R6. `SKILL.md:48`. Create the release has no completion check on the local copy.**
The step copies the draft and edits the copy's manifest, but nothing checks that `released/<NNN>/` matches. `compare_trees` only runs when external storage is reachable. With `none chosen` or a URL location, the immutable release is never verified. This is the one step without a checkable end.
Quote: "Copy the complete draft, including its exact exported datasets, to `deliveries/<investigation>/<package>/released/<NNN>/`"
Fix: Append "Then run `verify` on `released/<NNN>/` with the copied manifest's `inventory`. It must return no discrepancies. Report any discrepancy and stop."

**F4. R12 / R2. `SKILL.md:8`, `SKILL.md:48`. The pointer misdescribes the contract, and the `prior_release` format is ambiguous.**
Line 8 says the contract "defines ... manifest fields". It does not: the contract defers the field list to the project's `package-format/manifest-template.md`. Release writes four of those fields without ever pointing at them. As a result, `prior_release` is underspecified: the skill says "the previous highest release", and the template says "such as `released/001`". Runs will write either `002` or `released/002`.
Quote (line 48): "`prior_release` to the previous highest release or `none`"
Fix: Line 8: change "which defines layout, shared formats, manifest fields, and all consistency rules" to "which defines layout and every consistency rule; manifest fields are in the project's `package-format/manifest-template.md`". Line 48: change to "`prior_release` to `released/<previous NNN>` or `none`, and `released_at` in the template's ISO 8601 form".

**F5. R2 / R7. `SKILL.md:40`. The disposition revision hands off to awb-package with no return point.**
"Revise the draft through awb-package" does not say how the revision is classed or that control comes back here. awb-package:57 says that when the user has marked the package delivered, it finishes the revision and then *invokes awb-release*. That can restart the release from the top instead of resuming at re-verification. awb-package:31 already names the right path, "Bounded narrative revision, including an omission or accepted caveat", but this skill does not use that name.
Quote: "revise the draft through [awb-package](../awb-package/SKILL.md) so each listed place omits the conclusion or carries the caveat"
Fix: "...revise the draft through awb-package as a bounded narrative revision, then resume here at re-verification." Also add to awb-package:57: "When awb-release requested the revision, return to it instead of invoking it again."

**F6. R12. `SKILL.md:8` vs `SKILL.md:16`. The two lines contradict each other on draft creation.**
Line 8 says to load awb-package "when a draft needs creation or revision", which implies the release may create a missing draft. Line 16 says that when the draft is missing, the agent should stop and direct the user, because "a release never creates a draft". The only revision the release itself triggers is the disposition revision at line 40.
Quote (line 8): "Load [awb-package](../awb-package/SKILL.md) only when a draft needs creation or revision."
Fix: Delete that sentence from line 8. Line 16 already covers a missing draft, and line 40 covers the one in-release revision.

**F7. R8 / R9. `SKILL.md:8, 16, 28, 40, 48`. One meaning is restated as five prohibitions.**
Line 8 already has the leading word, "A release is a frozen copy of the draft". The same meaning is then repeated as negations, which keeps "draft/revise/rerun/regenerate" active in context:
- line 8: "never drafts, revises, or reruns analysis"
- line 16: "a release never creates a draft"
- line 28: "never reconstructed here"
- line 40: "Release is never authority to revalidate or rerun analysis"
- line 48: "never re-export or regenerate results"

Quote (line 40): "Release is never authority to revalidate or rerun analysis."
Fix: Keep "A release is a frozen copy of the draft: it copies files and edits only the copy's manifest release fields." Delete the line 8 clause "it never drafts, revises, or reruns analysis", the line 16 clause after the semicolon, the line 28 clause ", never reconstructed here", the line 40 first sentence, and the line 48 clause "; never re-export or regenerate results for a release". Line 40's second sentence (a revalidation choice pauses the release) already states what to do positively.

**F8. R10. `SKILL.md:26, 42, 52` vs the contract and both helper references. Verification rules are duplicated across four files.**
The skill and its references repeat the same rules: install the helper only if it is missing, run fresh after dispositions, never reuse a result, no hand checks, and use the recorded inventory without regenerating it.
- "Install only if missing" appears at release:26 and :52, manifest-helper:3, findings-helper:3 and awb-package:20.
- "Rerun both even if nothing changed / never reuse" appears at release:42, contract:43, manifest-helper:35 and findings-helper:25.
- "Hand checks never substitute" appears at release:26 and :52, contract:30 and :34, and findings-helper:5.
- "Recorded inventory, no rebuild" appears at release:26, contract:34 and manifest-helper:15 and :35.

Quote (line 26): "Hand checks never substitute. Read and verify the recorded inventory without rebuilding it."
Fix: Make awb-release lines 26 and 42 the single home for the release *procedure* (which pass, when to rerun). Make the helper references the home for *how to call* (install path, no hand check, reporting). In awb-release, delete "install each bundled helper only if its project copy is missing" and "Hand checks never substitute. Read and verify the recorded inventory without rebuilding it." Line 26 already says to verify "with the manifest's recorded `inventory`". In the references, delete contract:43's last sentence ("Release first checks structural rules...") and the release-procedure sentences at manifest-helper:35 and findings-helper:25.

**F9. R1. `SKILL.md:3`. The description restates the storage branch and ends with a negation.**
The description is always loaded. It names the storage branch twice ("record where released packages are kept and copy existing releases there", then "asks to record or change the release storage location"). It ends with a prohibition that awb-package's description already covers from the other side ("Marking a package delivered belongs to awb-release"). "Requests an equivalent delivery milestone" is a vague synonym for the delivered branch. The leading word users actually type, according to next-requests.md:12, is "delivered", and it is not front-loaded.
Quote: "Use only when the user explicitly marks the package delivered, requests an equivalent delivery milestone, or asks to record or change the release storage location; drafting and revision never trigger it."
Fix: "Release a delivered analytics workbench package as a numbered frozen copy of its draft, or record where releases are kept. Use when the user marks a package delivered (final, sent, shipped), or asks to record or change where releases are kept." Model invocation is correct: awb-package:57 invokes this skill, and awb-status routes requests to it.

### Low

**F10. R10. `SKILL.md:22, 54, 69`. The only-copy warning is specified three times.**
Quote (line 54): "With `none chosen`, repeat the warning that this checkout holds the only copy."
Fix: Delete line 22's "repeat the warning at each release". Keep line 54 as the step and line 69 as the report item.

**F11. R12. `SKILL.md:28`, `SKILL.md:32`. A rationale is repeated, and some exposition does not change actions.**
Line 28 already says "a draft can predate a flag". Line 32 repeats this and adds a causal story that the agent does not act on.
Quote (line 32): "a shared-data correction may flag findings in the investigation records after drafting, and record maintenance leaves the draft unchanged."
Fix: Delete line 32's second sentence. Line 28's clause and line 32's "A flag counts whether or not the draft mentions it" carry the operative rule.

**F12. R13. `SKILL.md:22, 46, 48, 52`. Several sentences are no-ops.**
These sentences describe what a capable model already does:
- line 22: "warn plainly" (the adverb)
- line 46: "and existing releases untouched" (immutability is already in the contract and implied by numbering)
- line 48: "The draft stays the working location for later revisions and the next delivery."
- line 52: "creating the intermediate directories as needed"

Quote (line 48): "The draft stays the working location for later revisions and the next delivery."
Fix: Delete the line 48 sentence and the line 52 clause. Change "warn plainly" to "warn". Change "Leave numbering gaps unfilled and existing releases untouched" to "Leave numbering gaps unfilled."

**F13. R6 / R4. `SKILL.md:68`. The report requires legwork that no step assigns.**
The acquisition warning requires reading `foundation/sources.md` retained-copy cells for each acquisition the manifest's `inputs` cite. No step says to do this, so it appears only at report time, where it is easy to skip or to answer from memory.
Quote: "a warning naming each acquisition the manifest cites whose retained copy in `foundation/sources.md` is blank or `this checkout only`"
Fix: Move the read into **Copy to storage**: "Read the `foundation/sources.md` row for each acquisition in the manifest's `inputs`, and note each one whose retained copy is blank or `this checkout only`." Shorten the report bullet to "the acquisitions noted in **Copy to storage** as held only in this checkout."

**F14. R3. `SKILL.md:18–22`. The storage question comes before verification.**
On the release branch, the user is asked for a storage location before verification. A failed structural check or a revalidation pause then stops the release, so the question was wasted, and a release request asks the user two questions at different points.
Quote (line 22): "ask the user where released packages are kept before creating the release."
Fix: Move **Record where releases are kept** to just before **Create the release**, after **Resolve revalidation flags**. Keep its text unchanged. The storage-only branch's "as above" still resolves.

**F15. R5. Whole file. The file is moderately sprawling.**
The file is about 1,150 words. Every line is live, but F7, F8, F10, F11 and F12 together remove about 20–25% without moving anything down the ladder. Nothing needs disclosure: the disposition and storage material is needed on its branches and is short.
Fix: Apply F7, F8 and F10–F12. No new reference file is needed.

## Rubric coverage

- R1 Description: F9
- R2 In-body pointers: F2, F4, F5
- R3 Hierarchy / disclosure: F14 (steps visible; branch material appropriately inline; no over- or under-disclosure)
- R4 Co-location: F13 (otherwise clean; the disposition concept is fragmented only through the F1 duplication)
- R5 Sprawl: F15
- R6 Completion criteria: F1, F3, F13
- R7 Splitting: F5 (hand-off boundary). Sequence and invocation splits are otherwise clean: the disposition step ends on a hard stop, and the storage branch rightly shares this skill.
- R8 Leading words: F7
- R9 Negation: F7. "Never overwrite" (line 52) is a legitimate guardrail paired with its positive target.
- R10 Single source of truth: F1, F8, F10
- R11 Environment as cache: clean. "`deliveries/` is excluded from Git" is a reason, not a lookup. The README line convention and insertion order match `README.md` and `data.md`. Restated helper signatures are covered under F8.
- R12 Relevance / sediment: F4, F6, F11
- R13 No-ops: F12

## Top 3 changes

1. **Replace "materially the same" with a checkable applicability test (F1).** Use matching `finding` and `reason` against `state.md`, every represented place set to a disposition other than `none`, and no later history entry than `disposition_recorded_at`. State it once at line 32 and delete line 40's restatement. This removes the main source of variance in the critical stop-and-ask step and aligns the skill with awb-package and awb-status.
2. **Point Copy to storage directly at `manifest-helper.md` (F2).** This lets the storage-only branch find the helper's install path and reporting rules. Also add a `verify` of the local `released/<NNN>/` copy as Create the release's completion criterion (F3), so every release gets an integrity check whether or not external storage is reachable.
3. **Collapse the "frozen copy" prohibitions and the cross-file verification duplicates (F7, F8).** Keep "A release is a frozen copy of the draft" as the leading word and delete its five negated restatements. Make awb-release the single home for the release verification procedure and the helper references the home for calling conventions. This is the largest token and legibility saving, and it removes the four-file duplication.

Counts: high 2, medium 7, low 6 (15 total).
