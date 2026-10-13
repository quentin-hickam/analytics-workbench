# Review: awb-release

Scope read in full: `.agents/skills/awb-release/SKILL.md`, the files that it points to (`.agents/skills/awb-package/references/package-contract.md`, `manifest-helper.md`, `findings-helper.md`), and `.agents/skills/awb-package/SKILL.md`. Files read for R10/R12 cross-checks: `awb-package/assets/package-format/manifest-template.md`, `awb-init/assets/workbench/AGENTS.md`, `awb-init/assets/workbench/README.md`, `awb-init/assets/workbench/workbench-guides/data.md` (storage lines), `awb-status/SKILL.md`, `awb-status/references/next-requests.md`, `awb-status/scripts/collect_status.py` (how it parses storage). Authority: `writing-for-agents` SKILL.md and SKILL-MECHANICS.md.

## Summary

awb-release is a step document in a good order:
- Every heading is a step.
- The sequence of verify, disposition and re-verify ends on helper results that the agent can check.
- The storage branch has an exhaustive bar ("each existing numbered release").

Its two weakest points are run-to-run variance in the critical disposition step and a broken pointer path on the storage-only branch. The test that decides if a recorded disposition still applies is the vague "materially the same". The skill states this test twice, and the two statements are not consistent. But awb-package and awb-status use a "same recorded reason" test, which the agent can check. The storage-only branch skips **Verify the draft**. As a result, it never reaches `manifest-helper.md`. That file is the only place that gives the location of the bundled `compare_trees` helper.

The other problems are load:
- The skill restates the "a release is a frozen copy" meaning as five separate prohibitions.
- The rerun/no-hand-check/recorded-inventory rules are repeated across this skill, the contract and both helper references.

## Findings

### High

**F1. R6 / R10. `SKILL.md:32`, `SKILL.md:40`. The test for disposition applicability is vague. It is duplicated, and the two copies are not consistent.**
The release uses this test to decide if it stops and asks the user. "Materially the same" is a judgement call. As a result, the outcome will be different from run to run. The skill states the test twice. Line 32 includes "a flag raised or changed since then reopens it". Line 40 does not have that clause. The siblings use a test that the agent can check. awb-package:51 resets on a changed reason. awb-status:26 says "same finding and current reason".
Quote (line 40): "A recorded disposition stays applicable while the finding and its evidence remain materially the same."
Fix: Delete the last sentence of line 40. Replace the last two sentences of line 32 with a criterion that the agent can check and that uses the manifest fields: "A recorded disposition applies when its `finding` and `reason` match the finding and reason currently in `state.md`, every place now representing the finding has a disposition other than `none`, and no history entry for that finding postdates its `disposition_recorded_at`. Otherwise it is reopened."

**F2. R2. `SKILL.md:8`, `SKILL.md:52`, `SKILL.md:58`. The storage-only branch never reaches the helper location.**
Line 8 sends a storage-only request "directly" to **Record storage without releasing**. That branch runs **Copy to storage**. This step says to copy the helper "as in **Verify the draft**". But that step never runs on this branch. Also, that step gives no path. Only `manifest-helper.md` gives the location of the bundled `awb_manifest.py` and the reporting rules for large lists of discrepancies. If the project does not have `src/packaging/manifest.py`, the agent must improvise. This makes a hand comparison or a skipped check more likely.
Quote (line 52): "copying the helper first as in **Verify the draft** if it is missing"
Fix: In **Copy to storage**, replace that clause with a direct pointer: "Read the [manifest helper interface](../awb-package/references/manifest-helper.md), which says where to install the helper when the project lacks it, then run `compare_trees(local_dir=<release>, copy_dir=<copy>)`."

### Medium

**F3. R6. `SKILL.md:48`. Create the release has no completion check on the local copy.**
The step copies the draft and edits the manifest of the copy. But nothing checks that `released/<NNN>/` matches. `compare_trees` runs only when external storage is reachable. With `none chosen` or a URL location, the immutable release is never verified. This is the only step with no end that the agent can check.
Quote: "Copy the complete draft, including its exact exported datasets, to `deliveries/<investigation>/<package>/released/<NNN>/`"
Fix: Append "Then run `verify` on `released/<NNN>/` with the copied manifest's `inventory`. It must return no discrepancies. Report any discrepancy and stop."

**F4. R12 / R2. `SKILL.md:8`, `SKILL.md:48`. The pointer gives an incorrect description of the contract. Also, the `prior_release` format is ambiguous.**
Line 8 says the contract "defines ... manifest fields". This is not true. The contract leaves the field list to the project's `package-format/manifest-template.md`. Release writes four of those fields, but it never points to them. As a result, the specification of `prior_release` is not complete. The skill says "the previous highest release". The template says "such as `released/001`". Runs will write either `002` or `released/002`.
Quote (line 48): "`prior_release` to the previous highest release or `none`"
Fix: Line 8: change "which defines layout, shared formats, manifest fields, and all consistency rules" to "which defines layout and every consistency rule; manifest fields are in the project's `package-format/manifest-template.md`". Line 48: change to "`prior_release` to `released/<previous NNN>` or `none`, and `released_at` in the template's ISO 8601 form".

**F5. R2 / R7. `SKILL.md:40`. The disposition revision hands off to awb-package with no return point.**
The text "Revise the draft through awb-package" does not say how to class the revision. It also does not say that control comes back here. awb-package:57 says this: when the user marked the package delivered, awb-package finishes the revision and then *invokes awb-release*. This can start the release again from the top, and not continue at re-verification. awb-package:31 already names the correct path: "Bounded narrative revision, including an omission or accepted caveat". But this skill does not use that name.
Quote: "revise the draft through [awb-package](../awb-package/SKILL.md) so each listed place omits the conclusion or carries the caveat"
Fix: "...revise the draft through awb-package as a bounded narrative revision, then resume here at re-verification." Also add to awb-package:57: "When awb-release requested the revision, return to it instead of invoking it again."

**F6. R12. `SKILL.md:8` vs `SKILL.md:16`. The two lines contradict each other about draft creation.**
Line 8 says to load awb-package "when a draft needs creation or revision". This implies that the release can create a missing draft. Line 16 tells the agent to stop and direct the user when the draft is missing, because "a release never creates a draft". The release itself starts only one revision: the disposition revision at line 40.
Quote (line 8): "Load [awb-package](../awb-package/SKILL.md) only when a draft needs creation or revision."
Fix: Delete that sentence from line 8. Line 16 already covers a missing draft. Line 40 covers the one revision inside the release.

**F7. R8 / R9. `SKILL.md:8, 16, 28, 40, 48`. One meaning is restated as five prohibitions.**
Line 8 already has the leading word, "A release is a frozen copy of the draft". Then the skill repeats the same meaning as negations. These negations keep "draft/revise/rerun/regenerate" active in context:
- line 8: "never drafts, revises, or reruns analysis"
- line 16: "a release never creates a draft"
- line 28: "never reconstructed here"
- line 40: "Release is never authority to revalidate or rerun analysis"
- line 48: "never re-export or regenerate results"

Quote (line 40): "Release is never authority to revalidate or rerun analysis."
Fix: Keep "A release is a frozen copy of the draft: it copies files and edits only the copy's manifest release fields." Delete these parts:
- the line 8 clause "it never drafts, revises, or reruns analysis"
- the line 16 clause after the semicolon
- the line 28 clause ", never reconstructed here"
- the first sentence of line 40
- the line 48 clause "; never re-export or regenerate results for a release".

The second sentence of line 40 (a revalidation choice pauses the release) already states in a positive form what to do.

**F8. R10. `SKILL.md:26, 42, 52` vs the contract and both helper references. Verification rules are duplicated across four files.**
The skill and its references repeat the same rules:
- Install the helper only if it is missing.
- Run fresh after dispositions.
- Never reuse a result.
- Do no hand checks.
- Use the recorded inventory, and do not regenerate it.

The locations are:
- "Install only if missing" appears at release:26 and :52, manifest-helper:3, findings-helper:3 and awb-package:20.
- "Rerun both even if nothing changed / never reuse" appears at release:42, contract:43, manifest-helper:35 and findings-helper:25.
- "Hand checks never substitute" appears at release:26 and :52, contract:30 and :34, and findings-helper:5.
- "Recorded inventory, no rebuild" appears at release:26, contract:34 and manifest-helper:15 and :35.

Quote (line 26): "Hand checks never substitute. Read and verify the recorded inventory without rebuilding it."
Fix: Make awb-release lines 26 and 42 the single home for the release *procedure* (which pass, when to rerun). Make the helper references the home for *how to call* (install path, no hand check, reporting). In awb-release, delete "install each bundled helper only if its project copy is missing" and "Hand checks never substitute. Read and verify the recorded inventory without rebuilding it." Line 26 already says to verify "with the manifest's recorded `inventory`". In the references, delete the last sentence of contract:43 ("Release first checks structural rules...") and the release-procedure sentences at manifest-helper:35 and findings-helper:25.

**F9. R1. `SKILL.md:3`. The description restates the storage branch and ends with a negation.**
The description is always loaded. It names the storage branch twice ("record where released packages are kept and copy existing releases there", then "asks to record or change the release storage location"). It ends with a prohibition. The description of awb-package already covers this prohibition from the other side ("Marking a package delivered belongs to awb-release"). "Requests an equivalent delivery milestone" is a vague synonym for the delivered branch. According to next-requests.md:12, the leading word that users actually type is "delivered". The description does not front-load this word.
Quote: "Use only when the user explicitly marks the package delivered, requests an equivalent delivery milestone, or asks to record or change the release storage location; drafting and revision never trigger it."
Fix: "Release a delivered analytics workbench package as a numbered frozen copy of its draft, or record where releases are kept. Use when the user marks a package delivered (final, sent, shipped), or asks to record or change where releases are kept." Model invocation is correct, because awb-package:57 invokes this skill and awb-status routes requests to it.

### Low

**F10. R10. `SKILL.md:22, 54, 69`. The skill specifies the only-copy warning three times.**
Quote (line 54): "With `none chosen`, repeat the warning that this checkout holds the only copy."
Fix: Delete "repeat the warning at each release" from line 22. Keep line 54 as the step and line 69 as the report item.

**F11. R12. `SKILL.md:28`, `SKILL.md:32`. The skill repeats a rationale. Also, some exposition does not change actions.**
Line 28 already says "a draft can predate a flag". Line 32 repeats this and adds a story about the cause. The agent does not act on this story.
Quote (line 32): "a shared-data correction may flag findings in the investigation records after drafting, and record maintenance leaves the draft unchanged."
Fix: Delete the second sentence of line 32. The operative rule is in the clause in line 28 and in the text "A flag counts whether or not the draft mentions it" in line 32.

**F12. R13. `SKILL.md:22, 46, 48, 52`. Several sentences are no-ops.**
These sentences describe what a capable model already does:
- line 22: "warn plainly" (the adverb)
- line 46: "and existing releases untouched" (immutability is already in the contract, and the numbering implies it)
- line 48: "The draft stays the working location for later revisions and the next delivery."
- line 52: "creating the intermediate directories as needed"

Quote (line 48): "The draft stays the working location for later revisions and the next delivery."
Fix: Delete the line 48 sentence and the line 52 clause. Change "warn plainly" to "warn". Change "Leave numbering gaps unfilled and existing releases untouched" to "Leave numbering gaps unfilled."

**F13. R6 / R4. `SKILL.md:68`. The report needs legwork that no step assigns.**
For the acquisition warning, the agent must read the retained-copy cells in `foundation/sources.md` for each acquisition that the `inputs` of the manifest cite. No step says to do this. As a result, this read occurs only at report time. At that time, it is easy to skip the read or to answer from memory.
Quote: "a warning naming each acquisition the manifest cites whose retained copy in `foundation/sources.md` is blank or `this checkout only`"
Fix: Move the read into **Copy to storage**: "Read the `foundation/sources.md` row for each acquisition in the manifest's `inputs`, and note each one whose retained copy is blank or `this checkout only`." Make the report bullet shorter: "the acquisitions noted in **Copy to storage** as held only in this checkout."

**F14. R3. `SKILL.md:18–22`. The storage question comes before verification.**
On the release branch, the agent asks the user for a storage location before verification. If a structural check then fails, or a revalidation pause occurs, the release stops. In that case, the question was wasted. Also, a release request asks the user two questions at different points.
Quote (line 22): "ask the user where released packages are kept before creating the release."
Fix: Move **Record where releases are kept** to the position immediately before **Create the release**, after **Resolve revalidation flags**. Do not change its text. The "as above" in the storage-only branch still resolves.

**F15. R5. Whole file. The file has moderate sprawl.**
The file has about 1,150 words. Every line is live. But together, F7, F8, F10, F11 and F12 remove about 20–25%, and they do not move anything down the ladder. No part needs disclosure. The disposition and storage material is necessary on its branches, and it is short.
Fix: Apply F7, F8 and F10–F12. A new reference file is not necessary.

## Rubric coverage

- R1 Description: F9
- R2 In-body pointers: F2, F4, F5
- R3 Hierarchy / disclosure: F14 (the steps are visible, the branch material is correctly inline, and there is no over- or under-disclosure)
- R4 Co-location: F13 (clean apart from this, and the only fragmentation of the disposition concept comes from the F1 duplication)
- R5 Sprawl: F15
- R6 Completion criteria: F1, F3, F13
- R7 Splitting: F5 (hand-off boundary). Apart from this, the sequence and invocation splits are clean. The disposition step ends on a hard stop, and it is correct that the storage branch shares this skill.
- R8 Leading words: F7
- R9 Negation: F7. "Never overwrite" (line 52) is a valid guardrail, and its positive target is with it.
- R10 Single source of truth: F1, F8, F10
- R11 Environment as cache: clean. "`deliveries/` is excluded from Git" is a reason, not a lookup. The README line convention and insertion order match `README.md` and `data.md`. F8 covers the restated helper signatures.
- R12 Relevance / sediment: F4, F6, F11
- R13 No-ops: F12

## Top 3 changes

1. **Replace "materially the same" with a checkable applicability test (F1).** Use these conditions:
   - `finding` and `reason` match `state.md`.
   - Every represented place has a disposition other than `none`.
   - No history entry is later than `disposition_recorded_at`.

   State the test one time at line 32 and delete the restatement in line 40. This removes the main source of variance in the critical stop-and-ask step. It also makes the skill agree with awb-package and awb-status.
2. **Point Copy to storage directly at `manifest-helper.md` (F2).** This lets the storage-only branch find the install path and the reporting rules of the helper. Also, add a `verify` of the local `released/<NNN>/` copy as the completion criterion of Create the release (F3). Then every release gets an integrity check, if external storage is reachable or not.
3. **Collapse the "frozen copy" prohibitions and the cross-file verification duplicates (F7, F8).** Keep "A release is a frozen copy of the draft" as the leading word, and delete its five negated restatements. Make awb-release the single home for the release verification procedure. Make the helper references the home for the conventions to call the helpers. This gives the largest saving in tokens and legibility. It also removes the duplication across four files.

Counts: high 2, medium 7, low 6 (15 total).
