# Review: awb-package

Scope read in full: `SKILL.md`, `references/package-contract.md`, `references/findings-helper.md`, `references/manifest-helper.md`, `assets/package-format/{findings-template,methodology-template,manifest-template,m365-assembly}.md`, and the docstrings/interfaces of `assets/awb_findings.py` and `assets/awb_manifest.py`. Siblings were read for R10/R12 only: `awb-release/SKILL.md`, `awb-init/references/provenance.md`, `awb-init/assets/workbench/AGENTS.md`, `awb-init/assets/workbench/investigation/{brief,state}.md`, `awb-visualize/SKILL.md`, `awb-visualize/references/figure-delivery.md`, and `awb-status/SKILL.md` plus `awb-status/scripts/collect_status.py` (to check manifest parsing).

## Summary

The skill is substantively sound. Its steps are ordered, the Verify step ends on a strong, checkable criterion ("until all structural and caveat rules pass and both helpers return no results"), and the package contract is correctly disclosed as shared reference with awb-release. Three defects can make runs go wrong or differ from each other:
- The figure-reuse criterion asks for a helper check that cannot run on a saved PNG.
- The manifest format is left open, but awb-status only parses JSON manifests.
- "Keep audit records on disk" never says where, so output can land inside `draft/` and ship.

The main load problem is duplication. `SKILL.md` (1,745 words in 61 lines) restates most of the contract's rules, and the same five or six guardrails appear three to five times across the skill. Examples are "no rerun", "never reproducible", "hand checks never substitute", the helper-install rule and "keep output on disk". Each guardrail should have one home and be cut everywhere else. Cutting them would reduce `SKILL.md` by roughly a third without losing any rule.

## Findings

### High

**H1. R12/R10 — `assets/package-format/manifest-template.md:3`**
The template lets the agent pick a manifest format. But `awb-status/scripts/collect_status.py:183` only reads one `manifest*.json` and marks anything else as uncertain. `references/manifest-helper.md:15` also assumes JSON. Different runs can therefore choose YAML or TOML, which silently breaks status reporting.
Quote: "when none exists, choose a simple readable format consistent with the repository and keep it for every later manifest"
Fix: replace it with "Serialize them as JSON in `manifest.json` unless the project already has an established manifest format; awb-status reads JSON manifests only." Make the same edit to `package-contract.md:13` (`manifest.<project-format>` → `manifest.json`, or the established format).

**H2. R6/R12 — `SKILL.md:47`**
The reuse criterion can't be checked. `check_text(fig)` takes a live matplotlib figure, not a PNG, and the next clause admits that a saved PNG "cannot be rechecked by the helper". So it's unclear what makes a figure eligible for reuse, and runs will differ: some will reuse, some will re-render, and some will try to load the PNG into the check.
Quote: "reuse the investigation's evidence figure when it passes `check_text` … a PNG saved earlier cannot be rechecked by the helper"
Fix: replace the first four sentences of the paragraph with: "Reuse an evidence figure unchanged when inspecting the PNG shows plain-language labels and no caption drawn in the image. Otherwise re-render it for presentation from its recorded companion table, without running analytical code, using `save_figure` with `Comment: presentation re-render of <evidence path>`. When no table is recorded, leave the figure out, state its finding in text, and report the gap."

**H3. R6 — `SKILL.md:45` (also `SKILL.md:53`, `references/findings-helper.md:25`, `references/manifest-helper.md:37`, `awb-init/references/provenance.md:51`)**
Every file says to keep audit output "on disk", but none says where. provenance.md points to "the package's existing audit location", which no file defines. If the agent writes `compare_evidence` output into `draft/`, `inventory` will list it and the file ships to M365. Only manifest-helper.md:37 says "outside the package", and only for large discrepancy lists.
Quote: "Keep full audit records on disk and return only counts, failures, and paths to the conversation."
Fix: add one line under the contract's **Layout and formats** (`package-contract.md:7`): "Audit output (export checks, large helper results) goes in `deliveries/<investigation>/<package>/audit/`, beside `draft/` and never inside it; report counts, failures, and that path." Replace each of the five on-disk sentences with a pointer to that line, and change provenance.md:51 from "existing audit location" to the contract path.

### Medium

**M1. R1/R9/R10 — `SKILL.md:3` and `SKILL.md:8`**
In the description, the key term "delivery package" comes after the verb. The description also spends words listing non-triggers ("routine analysis, record maintenance, and revalidation flags"), which names the unwanted behaviours instead of the wanted one. Line 8 then repeats the description almost word for word, and `AGENTS.md:35` says the same thing a third time. Model invocation itself is justified: awb-init and awb-release both reach this skill.
Quote: "Use only when the user explicitly requests package work; routine analysis, record maintenance, and revalidation flags never trigger it."
Fix: change the description to "Delivery package drafting for an analytics workbench: create or revise a package's working draft (findings, methodology, manifest, figures, datasets) for M365 assembly. Use only on an explicit user request for a package or package revision; awb-release preserves delivered releases." Delete line 8.

**M2. R10/R4 — `SKILL.md:35–53` against `references/package-contract.md:20–43`**
The "Assemble the draft" section of `SKILL.md` restates most of the contract's rules. This doubles their weight and splits each rule across two or three files. Instances:
- **Translation rule** in three places: SKILL:35, contract:20, findings-template:5 (the authoritative one).
- **Reproducibility guardrail** in three places: SKILL:37, contract:33, manifest-template:42.
- **Caption/caveat-outside-PNG** in five places: SKILL:47, contract:41, findings-template:31, m365-assembly:65, figure-delivery.md:17.
- **Dataset caveat placement** in three places: SKILL:43, contract:35, findings-template:51.
- **Revalidation listing and disposition persistence** in four places: SKILL:51, contract:39–43, manifest-template:39, awb-release:32/40.
- **Audience resolution** in five places: SKILL:24, contract:20, brief.md:17, AGENTS.md:33, awb-init:35.

Quote (SKILL:37): "A package built from a dirty or uncommitted producing state is never described as reproducible."
Fix: make the contract the single home for rules, with the templates as the home for field and section meaning. In `SKILL.md`, keep only the actions and point to the contract, for example "Apply the contract's provenance, dataset, figure, and revalidation rules." Delete the restated rule sentences listed above from SKILL:35, 37, 43, 47 and 51, and the Audience restatement from contract:20 (SKILL:24 owns the step).

**M3. R10/R8 — `SKILL.md:30, 45, 47, 49, 51`**
The same boundary appears five times in different words:
- "Changed results require separately authorized analytical work"
- "changed results need separate analytical work"
- "Unless separate analytical work changed the result"
- "Run analytical code only when the user separately requests changed results"
- "Packaging never reruns analysis on its own"

Quote (51): "Packaging never reruns analysis on its own; an export under the check above is not a rerun."
Fix: state it once near the top, under the H1, using *serialize* as the key term: "Packaging serializes recorded results; producing or changing a result is separate analytical work the user requests." Delete the other four restatements and use *serialize* wherever an export is meant.

**M4. R8 — `SKILL.md:31, 49`; `references/findings-helper.md:7`; `references/package-contract.md:30`**
One branch has four names: "Bounded narrative revision", "narrative-only revision", "narrative-only change", "bounded revision" (plus "bounded reads"). Nothing confirms they are the same thing, so an agent may treat them as different branches.
Quote (SKILL:31): "**Bounded narrative revision, including an omission or accepted caveat:**"
Fix: use *narrative revision* everywhere and drop "bounded" and "narrative-only".

**M5. R2/R10 — `SKILL.md:47` and `awb-visualize/references/figure-delivery.md:8`**
The two files point at each other. awb-package says figures "follow awb-visualize", and awb-visualize says "Package figures follow `awb-package`" and then restates the reuse rule. Neither pointer says what to read or when. Once H2 is fixed, the restated rule will also be out of date.
Quote: "Copy each figure `findings.md` cites into `figures/`; figures follow [awb-visualize](../awb-visualize/SKILL.md)."
Fix: in SKILL:47, write "Invoke awb-visualize to render or re-render a figure; the reuse decision below is this skill's." In figure-delivery.md:8, replace the restated rule with "Package figure reuse and re-rendering: see awb-package."

**M6. R4/R6 — `assets/package-format/methodology-template.md` (no section); required by `SKILL.md:43` and `package-contract.md:35`**
Both files require methodology.md to map each dataset display header to its source column, but the template has no section for it. Runs will put the mapping in different places, or leave it out.
Quote (SKILL:43): "Record each display header with the source column it came from in `methodology.md`."
Fix: add a section after **Findings**: "## Supporting datasets — For each exported dataset, its path, the recorded result it serializes, and a table mapping each display header to its source column. Otherwise state **None**." Then point SKILL:43 to that section.

**M7. R6/R10 — `assets/package-format/manifest-template.md:39` and `methodology-template.md:43`**
`collect_status.py` matches `revalidation_flags[].finding` and `.reason` exactly against the state.md `Finding` and `Revalidation reason or caveat` cells. The template only says the reason is "as currently recorded" and says nothing about how to write `finding`, so paraphrased text drops out of the automatic match. awb-status:25 also expects methodology.md to "name finding identifiers", which the template never asks for.
Quote: "with `finding`, `reason` as currently recorded in `state.md`"
Fix: change it to "`finding`: the state.md **Finding** cell, verbatim; `reason`: its **Revalidation reason or caveat** cell, verbatim". In methodology-template:43, add "naming each finding exactly as in `state.md`".

**M8. R12/R6 — `references/findings-helper.md:18–20` with `SKILL.md:16`**
The example names the package `decision` and puts it in `names`. `check` would then flag every ordinary "decision" in findings.md, which the template and the Audience section use throughout ("the decision they own"). An agent following "repair until `[]`" would have to reword correct prose.
Quote: `names = ["order-quality", "decision", "orders_view", ...`
Fix: change the example package to `staffing-decision`, with the path `deliveries/order-quality/staffing-decision/draft/`. In SKILL:16, add "a hyphenated slug, so the names check does not match plain words".

**M9. R5/R3 — `SKILL.md` overall (1,745 words; lines 37, 43–47 are each 130–230 words)**
The file is too long even though every line is live. Two branch-specific blocks sit inline although only some runs reach them:
- dataset export and `compare_evidence` (lines 43–45), only when datasets other than **none** are selected;
- legacy figure re-rendering (part of 47), only for evidence figures made under earlier rules.

About 35–40% of the file could go through M2/M3 deduplication plus disclosing these blocks.
Quote (43): "These are audience-facing outputs, not intermediate handoffs; convenience extracts, temporary query dumps, and full database snapshots are out of scope."
Fix: after deduplication, move the export procedure (43–45) into `references/exports.md`, with this pointer: "When the selection is not **none**, read [exports](references/exports.md) before exporting." If the figure paragraph is still over about 80 words after H2, apply the same move to it.

**M10. R11/R10 — `SKILL.md:45` and `assets/package-format/manifest-template.md:33`**
Both lines restate the five comparisons that `compare_evidence` already returns by name, and that provenance.md:38 already lists. The manifest-template parenthetical alone runs about 70 words.
Quote (SKILL:45): "It must compare the complete producing code, views, input publications/acquisitions, and resolved settings."
Fix: delete that sentence from SKILL:45. In manifest-template:33, replace the parenthetical with "the complete, unchanged list `compare_evidence` in `src/provenance.py` returns, run before that export".

**M11. R6 — `SKILL.md:37`**
"Say" has no target. The agent can't tell whether the statement goes in the manifest, in methodology.md, or in the final report, so placement will vary.
Quote: "say that its SHA does not fully identify the producing code and record the changed paths"
Fix: "state in methodology.md's **Sources and data quality** and in the report that its SHA does not fully identify the producing code", and the same for the `uncommitted` sentence.

**M12. R10/R3 — `references/manifest-helper.md:35–37`, `references/findings-helper.md:25`, `references/package-contract.md:43`**
These lines describe awb-release's procedure: the second verification pass, rerunning after dispositions, and `compare_trees` after the copy. awb-release:26, 42 and 52 already state all of it, so it is duplicated, and every drafting run loads it for nothing.
Quote (contract:43): "Release first checks structural rules, settles dispositions, then checks every rule here and reruns both `check` and `verify` even if nothing changed."
Fix: delete contract:43's last sentence and findings-helper:25's second and third sentences. Reduce manifest-helper:35–37 to the call fact only: "Release verification calls `verify` on the recorded rows without regenerating; `compare_trees` compares a copied release." awb-release owns the sequence.

### Low

**L1. R9 — `SKILL.md:43`**
The positive target, "Export exactly the user-selected datasets", is already stated. The list of what to leave out after it only names the unwanted behaviour.
Quote: "convenience extracts, temporary query dumps, and full database snapshots are out of scope"
Fix: delete that clause.

**L2. R4 — `SKILL.md:47` (last sentence)**
A dataset-selection rule sits at the end of the figures paragraph. It also seems to contradict line 43, which puts "full database snapshots" out of scope.
Quote: "Exact-rerun inputs or database snapshots are included only when the user explicitly chooses them."
Fix: move it to the dataset question at line 22: "…explicitly offer **none**; exact-rerun inputs or snapshots are a separate opt-in."

**L3. R13/R12 — `SKILL.md:10`**
The portability sentence contradicts the Python-specific helper steps later in the file, and it changes nothing about what the agent does.
Quote: "Keep the workflow portable: use repository conventions and available tools rather than assuming a language, backend, or global skill installation."
Fix: delete the sentence. If non-Python support matters, write "A non-Python project ports each helper's interface" in the two helper references, as provenance.md:3 already does.

**L4. R4 — `SKILL.md:18`**
The rule about how many packages an investigation gets sits under the contract pointer instead of with package naming.
Quote: "Use one stable package per investigation unless another has an independent scope or delivery schedule."
Fix: move it to line 16.

**L5. R12 — `references/manifest-helper.md:11`**
This is an implementation detail the agent never acts on.
Quote: "Files are hashed in bounded chunks."
Fix: delete it.

**L6. R10 — `SKILL.md:41`**
This repeats the field semantics in manifest-template:11–12.
Quote: "Set `created_at` once, `revised_at` on every revision, and `status` to `draft`."
Fix: shorten it to "Fill the manifest per `manifest-template.md`."

**L7. R9 — `SKILL.md:37`, `SKILL.md:57`, `manifest-template.md:42`**
These are guardrails phrased only as prohibitions.
Quotes: "Commit nothing on the user's behalf to make provenance look clean." / "this skill never creates a `released/` directory" / "do not describe such a package as exactly reproducible"
Fix: rewrite them as positive targets: "Record provenance as it stands; commits are the user's decision." / "Release creation belongs to awb-release." For the third, keep the single positive statement in the contract (see M2).

**L8. R8 — `SKILL.md:41`**
"Lazily" has an ambiguous sense here.
Quote: "Create the draft lazily at the paths in the package contract"
Fix: "Create missing draft files at the contract paths; revise existing ones in place."

**L9. R10 — `SKILL.md:14`**
This duplicates AGENTS.md:7, which is always loaded in the project, and awb-release:14.
Quote: "If the request could refer to multiple investigations, ask which one before changing package files."
Fix: delete it.

**L10. R13 — `references/findings-helper.md:9`**
A capable model already replaces placeholder values in an example.
Quote: "replacing the example path and names with the actual package and complete set"
Fix: shorten it to "Run from the project root:".

**L11. R3 — `SKILL.md:20`**
The helper-interface pointers sit in "Establish the package", but the helpers are first used at Verify (line 53). The install rule repeats findings-helper:3, manifest-helper:3 and awb-release:26.
Quote: "Before checking audience-facing prose, read the [findings helper interface]…"
Fix: move both pointers to the start of the Verify paragraph at line 53, and delete the install sentence, since each reference states it.

**L12. R6 — `SKILL.md:43`**
The line says what to use "where available" but not what to do when no export code exists.
Quote: "through existing code in `src/packaging/` or the analytical modules where available"
Fix: add "; otherwise add a serializer in `src/packaging/` that reads the recorded result and renames headers only."

**L13. R9 — `assets/package-format/m365-assembly.md:80`**
Line 78 already states the positive target ("without changing analytical content").
Quote: "Do not add derived metrics or hidden transformations unless they are first produced and documented in the workbench package."
Fix: delete it, or merge it into 78 as "…; derived metrics come only from the workbench package."

## Rubric coverage

- R1 Description: M1
- R2 In-body pointers: M5 (the contract, helper, provenance and awb-release pointers are otherwise well conditioned)
- R3 Hierarchy and disclosure: M9, M12, L11. Disclosing the contract is justified, since it is shared with awb-release.
- R4 Co-location: M2, M6, L2, L4
- R5 Sprawl: M9
- R6 Completion criteria: H2, H3, M6, M7, M8, M11, L12. Verify (SKILL:53) and the M365 "Ask before drafting" step (m365-assembly:39) are strong.
- R7 Splitting: clean. The sequence ends on a checkable Verify gate. Model invocation is justified because awb-init and awb-release reach the skill.
- R8 Leading words: M3, M4, L8
- R9 Negation: M1, L1, L7, L13. The findings-template:5 prohibition list and the helper docstrings' "do not import it from the skill folder" are hard guardrails paired with positive targets: clean.
- R10 Duplication: H3, M1, M2, M3, M5, M7, M10, M12, L6, L9, L11
- R11 Environment as cache: M10. The helper references otherwise record error semantics and gotchas that the docstrings do not.
- R12 Relevance and sediment: H1, H2, M8, L3, L5
- R13 No-ops: L3, L10

## Top 3 changes

1. **Rewrite the figure-reuse rule (H2, M5).** Replace the impossible "passes `check_text`" criterion in SKILL:47 with inspection of the PNG for plain labels and no drawn caption, followed by a re-render from the recorded table or a reported gap. Then make awb-visualize point to awb-package for reuse instead of restating it.
2. **Make the manifest machine-matchable for awb-status (H1, M7).** Default the manifest to JSON (`manifest.json`) in manifest-template:3 and contract:13, and require `revalidation_flags[].finding` and `.reason` to copy the state.md cells verbatim. awb-status's collector relies on both.
3. **Make package-contract.md the single home for rules (H3, M2, M3).** Add one audit-location line outside `draft/`. In SKILL.md, state the serialize-not-produce boundary once, and cut its restatements of the provenance, caption, dataset-caveat, revalidation, names-set, hand-check and on-disk rules, replacing them with pointers to the contract. This cuts about a third of SKILL.md and closes the gap where audit files could ship to M365.

Counts: 3 high, 12 medium, 13 low (28 findings).
