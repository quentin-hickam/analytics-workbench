# Review: awb-package

Scope read in full: `SKILL.md`, `references/package-contract.md`, `references/findings-helper.md`, `references/manifest-helper.md`, `assets/package-format/{findings-template,methodology-template,manifest-template,m365-assembly}.md`, and the docstrings/interfaces of `assets/awb_findings.py` and `assets/awb_manifest.py`. The siblings that follow were read only for R10/R12: `awb-release/SKILL.md`, `awb-init/references/provenance.md`, `awb-init/assets/workbench/AGENTS.md`, `awb-init/assets/workbench/investigation/{brief,state}.md`, `awb-visualize/SKILL.md`, `awb-visualize/references/figure-delivery.md`, and `awb-status/SKILL.md` plus `awb-status/scripts/collect_status.py` (to check how it parses manifests).

## Summary

In its substance, the skill is good. Its steps are in order. The Verify step ends on a strong criterion that the agent can check ("until all structural and caveat rules pass and both helpers return no results"). The package contract is correctly disclosed as a reference that the skill shares with awb-release. Three defects can make runs go wrong or make runs different from each other:
- The criterion for figure reuse asks for a helper check that cannot run on a saved PNG.
- The skill lets the agent choose the manifest format, but awb-status parses only JSON manifests.
- "Keep audit records on disk" never says where. As a result, output can go inside `draft/` and then ship.

Duplication is the main load problem. `SKILL.md` (1,745 words in 61 lines) restates most of the rules of the contract. Also, the same five or six guardrails occur three to five times across the skill. Examples are "no rerun", "never reproducible", "hand checks never substitute", the helper-install rule and "keep output on disk". It is better to give each guardrail one home and to cut it from all other places. If you cut them, `SKILL.md` becomes about one third shorter and loses no rule.

## Findings

### High

**H1. R12/R10: `assets/package-format/manifest-template.md:3`**
The template lets the agent choose a manifest format. But `awb-status/scripts/collect_status.py:183` reads only one `manifest*.json` and marks anything else as uncertain. `references/manifest-helper.md:15` also assumes JSON. As a result, different runs can choose YAML or TOML. This breaks status reporting, and nothing gives a warning.
Quote: "when none exists, choose a simple readable format consistent with the repository and keep it for every later manifest"
Fix: Replace it with "Serialize them as JSON in `manifest.json` unless the project already has an established manifest format; awb-status reads JSON manifests only." Make the same change in `package-contract.md:13` (`manifest.<project-format>` → `manifest.json`, or the established format).

**H2. R6/R12: `SKILL.md:47`**
It is not possible to check the reuse criterion. `check_text(fig)` takes a live matplotlib figure, not a PNG. The next clause itself says that a saved PNG "cannot be rechecked by the helper". For this reason, it is not clear what makes a figure eligible for reuse. As a result, runs will be different:
- Some runs will reuse the figure.
- Some runs will re-render the figure.
- Some runs will try to load the PNG into the check.

Quote: "reuse the investigation's evidence figure when it passes `check_text` … a PNG saved earlier cannot be rechecked by the helper"
Fix: Replace the first four sentences of the paragraph with: "Reuse an evidence figure unchanged when inspecting the PNG shows plain-language labels and no caption drawn in the image. Otherwise re-render it for presentation from its recorded companion table, without running analytical code, using `save_figure` with `Comment: presentation re-render of <evidence path>`. When no table is recorded, leave the figure out, state its finding in text, and report the gap."

**H3. R6: `SKILL.md:45` (also `SKILL.md:53`, `references/findings-helper.md:25`, `references/manifest-helper.md:37`, `awb-init/references/provenance.md:51`)**
Every file says to keep audit output "on disk". But no file says where. provenance.md points to "the package's existing audit location", but no file defines this location. If the agent writes `compare_evidence` output into `draft/`, `inventory` will list it. Then the file ships to M365. Only manifest-helper.md:37 says "outside the package", and it says this only for large lists of discrepancies.
Quote: "Keep full audit records on disk and return only counts, failures, and paths to the conversation."
Fix: Add one line under **Layout and formats** in the contract (`package-contract.md:7`): "Audit output (export checks, large helper results) goes in `deliveries/<investigation>/<package>/audit/`, beside `draft/` and never inside it; report counts, failures, and that path." Replace each of the five "on disk" sentences with a pointer to that line. Change provenance.md:51 from "existing audit location" to the contract path.

### Medium

**M1. R1/R9/R10: `SKILL.md:3` and `SKILL.md:8`**
In the description, the key term "delivery package" comes after the verb. The description also uses words to list non-triggers ("routine analysis, record maintenance, and revalidation flags"). This names the unwanted behaviours instead of the wanted behaviour. Then line 8 repeats the description almost word for word. `AGENTS.md:35` says the same thing a third time. There is a good reason for model invocation itself: awb-init and awb-release both reach this skill.
Quote: "Use only when the user explicitly requests package work; routine analysis, record maintenance, and revalidation flags never trigger it."
Fix: Change the description to "Delivery package drafting for an analytics workbench: create or revise a package's working draft (findings, methodology, manifest, figures, datasets) for M365 assembly. Use only on an explicit user request for a package or package revision; awb-release preserves delivered releases." Delete line 8.

**M2. R10/R4: `SKILL.md:35–53` against `references/package-contract.md:20–43`**
The "Assemble the draft" section of `SKILL.md` restates most of the rules of the contract. This doubles their weight. It also splits each rule across two or three files. Instances:
- **Translation rule** in three places: SKILL:35, contract:20, findings-template:5 (this is the authoritative one).
- **Reproducibility guardrail** in three places: SKILL:37, contract:33, manifest-template:42.
- **Caption/caveat-outside-PNG** in five places: SKILL:47, contract:41, findings-template:31, m365-assembly:65, figure-delivery.md:17.
- **Dataset caveat placement** in three places: SKILL:43, contract:35, findings-template:51.
- **Revalidation listing and disposition persistence** in four places: SKILL:51, contract:39–43, manifest-template:39, awb-release:32/40.
- **Audience resolution** in five places: SKILL:24, contract:20, brief.md:17, AGENTS.md:33, awb-init:35.

Quote (SKILL:37): "A package built from a dirty or uncommitted producing state is never described as reproducible."
Fix: Make the contract the single home for rules. Make the templates the home for the meaning of fields and sections. In `SKILL.md`, keep only the actions and point to the contract. For example: "Apply the contract's provenance, dataset, figure, and revalidation rules." Delete the restated rule sentences in the list above from SKILL:35, 37, 43, 47 and 51. Also delete the Audience restatement from contract:20 (SKILL:24 owns the step).

**M3. R10/R8: `SKILL.md:30, 45, 47, 49, 51`**
The same boundary occurs five times in different words:
- "Changed results require separately authorized analytical work"
- "changed results need separate analytical work"
- "Unless separate analytical work changed the result"
- "Run analytical code only when the user separately requests changed results"
- "Packaging never reruns analysis on its own"

Quote (51): "Packaging never reruns analysis on its own; an export under the check above is not a rerun."
Fix: State it one time near the top, under the H1. Use *serialize* as the key term: "Packaging serializes recorded results; producing or changing a result is separate analytical work the user requests." Delete the other four restatements. Use *serialize* in all places where the text means an export.

**M4. R8: `SKILL.md:31, 49`, `references/findings-helper.md:7`, `references/package-contract.md:30`**
One branch has four names: "Bounded narrative revision", "narrative-only revision", "narrative-only change", "bounded revision" (plus "bounded reads"). No text confirms that they are the same thing. For this reason, an agent can possibly treat them as different branches.
Quote (SKILL:31): "**Bounded narrative revision, including an omission or accepted caveat:**"
Fix: Use *narrative revision* in all places. Remove "bounded" and "narrative-only".

**M5. R2/R10: `SKILL.md:47` and `awb-visualize/references/figure-delivery.md:8`**
The two files point to each other. awb-package says that figures "follow awb-visualize". awb-visualize says "Package figures follow `awb-package`" and then restates the reuse rule. Neither pointer says what to read or when to read it. After you fix H2, the restated rule will also be out of date.
Quote: "Copy each figure `findings.md` cites into `figures/`; figures follow [awb-visualize](../awb-visualize/SKILL.md)."
Fix: In SKILL:47, write "Invoke awb-visualize to render or re-render a figure; the reuse decision below is this skill's." In figure-delivery.md:8, replace the restated rule with "Package figure reuse and re-rendering: see awb-package."

**M6. R4/R6: `assets/package-format/methodology-template.md` (it has no section for a mapping that `SKILL.md:43` and `package-contract.md:35` make necessary)**
Both files say that methodology.md must map each dataset display header to its source column. But the template has no section for this mapping. Runs will put the mapping in different places, or leave it out.
Quote (SKILL:43): "Record each display header with the source column it came from in `methodology.md`."
Fix: Add a section after **Findings**: "## Supporting datasets — For each exported dataset, its path, the recorded result it serializes, and a table mapping each display header to its source column. Otherwise state **None**." Then point SKILL:43 to that section.

**M7. R6/R10: `assets/package-format/manifest-template.md:39` and `methodology-template.md:43`**
`collect_status.py` matches `revalidation_flags[].finding` and `.reason` exactly against the state.md `Finding` and `Revalidation reason or caveat` cells. About the reason, the template says only that it is "as currently recorded". It says nothing about how to write `finding`. As a result, paraphrased text drops out of the automatic match. awb-status:25 also expects methodology.md to "name finding identifiers". The template never asks for this.
Quote: "with `finding`, `reason` as currently recorded in `state.md`"
Fix: Change it to "`finding`: the state.md **Finding** cell, verbatim; `reason`: its **Revalidation reason or caveat** cell, verbatim". In methodology-template:43, add "naming each finding exactly as in `state.md`".

**M8. R12/R6: `references/findings-helper.md:18–20` with `SKILL.md:16`**
The example names the package `decision` and puts it in `names`. If an agent follows the example, `check` flags every ordinary "decision" in findings.md. The template and the Audience section use this word throughout ("the decision they own"). An agent that follows "repair until `[]`" will then have to reword correct prose.
Quote: `names = ["order-quality", "decision", "orders_view", ...`
Fix: Change the example package to `staffing-decision`, with the path `deliveries/order-quality/staffing-decision/draft/`. In SKILL:16, add "a hyphenated slug, so the names check does not match plain words".

**M9. R5/R3: `SKILL.md` overall (1,745 words, and lines 37, 43–47 are each 130–230 words)**
The file is too long, although every line is live. Two blocks for specific branches are inline, but only some runs reach them:
- Dataset export and `compare_evidence` (lines 43–45). Runs reach this block only when datasets other than **none** are selected.
- The re-render of legacy figures (part of 47). Runs reach this block only for evidence figures that were made under earlier rules.

About 35–40% of the file can go if you do the M2/M3 deduplication and disclose these blocks.
Quote (43): "These are audience-facing outputs, not intermediate handoffs; convenience extracts, temporary query dumps, and full database snapshots are out of scope."
Fix: After deduplication, move the export procedure (43–45) into `references/exports.md`. Use this pointer: "When the selection is not **none**, read [exports](references/exports.md) before exporting." If the figure paragraph still has more than about 80 words after the H2 fix, move it in the same way.

**M10. R11/R10: `SKILL.md:45` and `assets/package-format/manifest-template.md:33`**
Both lines restate the five comparisons that `compare_evidence` already returns by name. provenance.md:38 also already lists them. The parenthetical in manifest-template alone has about 70 words.
Quote (SKILL:45): "It must compare the complete producing code, views, input publications/acquisitions, and resolved settings."
Fix: Delete that sentence from SKILL:45. In manifest-template:33, replace the parenthetical with "the complete, unchanged list `compare_evidence` in `src/provenance.py` returns, run before that export".

**M11. R6: `SKILL.md:37`**
"Say" has no target. The agent cannot know if the statement goes in the manifest, in methodology.md, or in the final report. As a result, the location will change from run to run.
Quote: "say that its SHA does not fully identify the producing code and record the changed paths"
Fix: "state in methodology.md's **Sources and data quality** and in the report that its SHA does not fully identify the producing code". Make the same change for the `uncommitted` sentence.

**M12. R10/R3: `references/manifest-helper.md:35–37`, `references/findings-helper.md:25`, `references/package-contract.md:43`**
These lines describe the procedure of awb-release:
- the second verification pass
- the rerun after dispositions
- `compare_trees` after the copy.

awb-release:26, 42 and 52 already state all of it. As a result, it is duplicated, and each drafting run loads it with no benefit.
Quote (contract:43): "Release first checks structural rules, settles dispositions, then checks every rule here and reruns both `check` and `verify` even if nothing changed."
Fix: Delete the last sentence of contract:43 and the second and third sentences of findings-helper:25. Reduce manifest-helper:35–37 to only the call fact: "Release verification calls `verify` on the recorded rows without regenerating; `compare_trees` compares a copied release." awb-release owns the sequence.

### Low

**L1. R9: `SKILL.md:43`**
The text already states the positive target, "Export exactly the user-selected datasets". After it, the list of items to leave out names only the unwanted behaviour.
Quote: "convenience extracts, temporary query dumps, and full database snapshots are out of scope"
Fix: Delete that clause.

**L2. R4: `SKILL.md:47` (last sentence)**
A rule for dataset selection is at the end of the figures paragraph. It also seems to contradict line 43, which puts "full database snapshots" out of scope.
Quote: "Exact-rerun inputs or database snapshots are included only when the user explicitly chooses them."
Fix: Move it to the dataset question at line 22: "…explicitly offer **none**; exact-rerun inputs or snapshots are a separate opt-in."

**L3. R13/R12: `SKILL.md:10`**
The portability sentence contradicts the Python-specific helper steps later in the file. Also, it does not change what the agent does.
Quote: "Keep the workflow portable: use repository conventions and available tools rather than assuming a language, backend, or global skill installation."
Fix: Delete the sentence. If support for languages other than Python is important, write "A non-Python project ports each helper's interface" in the two helper references. provenance.md:3 already does this.

**L4. R4: `SKILL.md:18`**
The rule about how many packages an investigation gets is under the contract pointer, not with the package names.
Quote: "Use one stable package per investigation unless another has an independent scope or delivery schedule."
Fix: Move it to line 16.

**L5. R12: `references/manifest-helper.md:11`**
This is an implementation detail. The agent never acts on it.
Quote: "Files are hashed in bounded chunks."
Fix: Delete it.

**L6. R10: `SKILL.md:41`**
This repeats the meaning of the fields in manifest-template:11–12.
Quote: "Set `created_at` once, `revised_at` on every revision, and `status` to `draft`."
Fix: Make it shorter: "Fill the manifest per `manifest-template.md`."

**L7. R9: `SKILL.md:37`, `SKILL.md:57`, `manifest-template.md:42`**
These guardrails are written only as prohibitions.
Quotes: "Commit nothing on the user's behalf to make provenance look clean." / "this skill never creates a `released/` directory" / "do not describe such a package as exactly reproducible"
Fix: Write them again as positive targets: "Record provenance as it stands; commits are the user's decision." / "Release creation belongs to awb-release." For the third, keep the single positive statement in the contract (see M2).

**L8. R8: `SKILL.md:41`**
Here, "Lazily" has more than one possible meaning.
Quote: "Create the draft lazily at the paths in the package contract"
Fix: "Create missing draft files at the contract paths; revise existing ones in place."

**L9. R10: `SKILL.md:14`**
This duplicates two places: AGENTS.md:7, which is always loaded in the project, and awb-release:14.
Quote: "If the request could refer to multiple investigations, ask which one before changing package files."
Fix: Delete it.

**L10. R13: `references/findings-helper.md:9`**
A capable model already replaces placeholder values in an example.
Quote: "replacing the example path and names with the actual package and complete set"
Fix: Make it shorter: "Run from the project root:".

**L11. R3: `SKILL.md:20`**
The pointers to the helper interfaces are in "Establish the package". But the agent first uses the helpers at Verify (line 53). The install rule repeats findings-helper:3, manifest-helper:3 and awb-release:26.
Quote: "Before checking audience-facing prose, read the [findings helper interface]…"
Fix: Move both pointers to the start of the Verify paragraph at line 53, and delete the install sentence, because each reference states it.

**L12. R6: `SKILL.md:43`**
The line says what to use "where available". But it does not say what to do when no export code exists.
Quote: "through existing code in `src/packaging/` or the analytical modules where available"
Fix: Add "; otherwise add a serializer in `src/packaging/` that reads the recorded result and renames headers only."

**L13. R9: `assets/package-format/m365-assembly.md:80`**
Line 78 already states the positive target ("without changing analytical content").
Quote: "Do not add derived metrics or hidden transformations unless they are first produced and documented in the workbench package."
Fix: Delete it, or merge it into 78 as "…; derived metrics come only from the workbench package."

## Rubric coverage

- R1 Description: M1
- R2 In-body pointers: M5 (apart from this, the contract, helper, provenance and awb-release pointers have clear conditions)
- R3 Hierarchy and disclosure: M9, M12, L11. There is a good reason to disclose the contract, because the skill shares it with awb-release.
- R4 Co-location: M2, M6, L2, L4
- R5 Sprawl: M9
- R6 Completion criteria: H2, H3, M6, M7, M8, M11, L12. Verify (SKILL:53) and the M365 "Ask before drafting" step (m365-assembly:39) are strong.
- R7 Splitting: clean. The sequence ends on a Verify gate that the agent can check. There is a good reason for model invocation, because awb-init and awb-release reach the skill.
- R8 Leading words: M3, M4, L8
- R9 Negation: M1, L1, L7, L13. The findings-template:5 prohibition list is a hard guardrail with positive targets. The text "do not import it from the skill folder" in the helper docstrings is also a hard guardrail with a positive target. These are clean.
- R10 Duplication: H3, M1, M2, M3, M5, M7, M10, M12, L6, L9, L11
- R11 Environment as cache: M10. Apart from this, the helper references record error semantics and gotchas that the docstrings do not record.
- R12 Relevance and sediment: H1, H2, M8, L3, L5
- R13 No-ops: L3, L10

## Top 3 changes

1. **Rewrite the figure-reuse rule (H2, M5).** In SKILL:47, replace the impossible "passes `check_text`" criterion with an inspection of the PNG for plain labels and no drawn caption. After the inspection, the rule continues with a re-render from the recorded table or a reported gap. Then make awb-visualize point to awb-package for reuse, and remove its restatement of the rule.
2. **Make the manifest machine-matchable for awb-status (H1, M7).** In manifest-template:3 and contract:13, make JSON (`manifest.json`) the default manifest format. Also state that `revalidation_flags[].finding` and `.reason` must copy the state.md cells verbatim. The awb-status collector relies on both.
3. **Make package-contract.md the single home for rules (H3, M2, M3).** Add one line that puts the audit location outside `draft/`. In SKILL.md, state the serialize-not-produce boundary one time. Cut its restatements of the provenance, caption, dataset-caveat, revalidation, names-set, hand-check and on-disk rules. Replace them with pointers to the contract. This cuts about a third of SKILL.md. It also closes the gap that lets audit files ship to M365.

Counts: 3 high, 12 medium, 13 low (28 findings).
