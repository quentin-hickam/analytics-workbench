# Writing review: `awb-init`

Scope read in full: `SKILL.md`; `references/{landing,provenance,validation}.md`; `assets/workbench/{AGENTS.md,README.md,.gitignore}`; `assets/workbench/foundation/{sources,catalog,quality,glossary}.md`; `assets/workbench/investigation/{brief,state,history}.md`; `assets/workbench/workbench-guides/{data,analysis}.md`; module docstrings and public signatures of `assets/awb_{landing,provenance,validate}.py`. Siblings were read only for duplication and contradiction: `awb-status/SKILL.md`, `awb-status/references/next-requests.md`, `awb-status/scripts/collect_status.py` (README parsing only), `awb-package/SKILL.md`, `awb-package/references/{manifest-helper,package-contract}.md`, `awb-release/SKILL.md`, and the awb-package templates, via grep. Paths below are relative to `.agents/skills/awb-init/` unless they name a sibling.

## Summary

The skill is in good shape on the hardest levers. Pointers to templates carry explicit firing conditions (`SKILL.md:45` is a model of this). The scoping interview has an exhaustive finish line. The helper references match the code they describe; every signature, return shape and count I checked against the `.py` files is accurate. The main weaknesses are elsewhere. The first is a must-have pointer that an agent cannot resolve: the project guides send the agent to "the installed `awb-init` skill's `references/...`" with no location, and that location differs between Claude Code and Codex. The second is duplication: the scope-expansion, vocabulary, audience, evidence-contents and shared-correction rules each appear in two to five places. In the always-loaded `AGENTS.md` this costs context on every turn, and it lets the agent settle a scope change inline instead of invoking `awb-init`. The third is the lack of a branch map in `SKILL.md`, together with vague completion criteria for the repair branch. With those fixed, plus a pruning pass that collapses the repeated "preserve, merge, surface conflicts" boilerplate into one word, the skill would be tighter and more predictable. Verdict: sound structure; needs a targeted deduplication pass and one pointer fix before release.

## Findings

### High

**H1. R2: the pointer from the project guides to the helper references cannot be resolved.**
`assets/workbench/workbench-guides/data.md:3`, `data.md:25`, `analysis.md:11`, `analysis.md:17`, `analysis.md:25`.
The guides are project files. The agent needs these references for every acquisition, validation and evidence step: helper installation, interfaces and examples. The guides name "the installed `awb-init` skill" but give no path. The repo README puts that skill under `~/.claude/skills/` for Claude Code and `~/.agents/skills/` for Codex. Claude Code does not show a skill's path until the skill is invoked, and invoking `awb-init` here would load the initialization procedure. The likely failure is that the agent guesses, searches at length, or writes a helper from scratch. The result varies from run to run.
Quote (`data.md:3`): "For helper setup, signatures, and examples, read the installed `awb-init` skill's `references/landing.md`."
Fix: put the location in one place, `AGENTS.md` under "Load the relevant procedures", and have the guides refer to it.
- Add to `AGENTS.md`: "Workbench helper references and helper sources live in the installed `awb-init` skill folder: `~/.claude/skills/awb-init/` (Claude Code) or `~/.agents/skills/awb-init/` (Codex)."
- In each guide, change the wording to "read `references/landing.md` in the `awb-init` skill folder named in `AGENTS.md`".
- Optionally, have `SKILL.md` "Create the project foundation" record the resolved absolute path of its own folder on that line during initialization.

**H2. R10/R3: the always-loaded `AGENTS.md` contains the scope-change rule that `awb-init` owns, so the agent can skip the interview.**
`assets/workbench/AGENTS.md:9` duplicates `SKILL.md:26`. It is restated again in `AGENTS.md:23` and `investigation/brief.md:29`.
`AGENTS.md:9` sends the agent to `awb-init` for scope changes, then gives the full resolution rules: expand or split, what to inherit, what to start fresh. With those rules already in context, the agent can resolve a scope change inline and skip the one-question-at-a-time interview with recommended answers. This is a variance lever, and the meaning now has two homes that must stay in sync.
Quote: "The same ask about a broader population containing the current population expands the existing investigation and reopens only affected decisions."
Fix: replace the last four sentences of `AGENTS.md:9` with the trigger only:
"Use `awb-init` to establish or repair structure, start an investigation, or resolve a consequential scope change, including deciding whether a new ask extends the active investigation or starts another. Use `awb-status` for status and possible next requests."
Keep the rule in `SKILL.md:26` only. In `AGENTS.md:23`, cut "Apart from related findings used to select methods," because `SKILL.md:26` and `brief.md:29` already state it.

### Medium

**M1. R3/R10/R12: data-path rules that never apply during initialization are inlined in `SKILL.md`.**
`SKILL.md:50-58`.
Initialization lands no data. Yet lines 50-58, about 190 words, restate the batch storage path, the landing rules, the CSV rule and the backend rule. `AGENTS.md:21`, `README.md:28-30` and `workbench-guides/data.md` (the authoritative home) already state them. The only part initialization uses is "defer these directories".
Quote: "Land every acquired API response, SQL extract, or other source before canonical ingestion."
Fix: replace lines 48-58 with: "Defer `src/`, configuration, `foundation/views/`, and `data/{raw,parquet,cache}/`; the project's `workbench-guides/data.md` creates each on first use. A speculative framework is out of scope." Move anything in 50-58 that `data.md` lacks into `data.md`; the "default backend / alternate backend" sentence is already at `data.md:31`.

**M2. R3: `SKILL.md` has no branch map, so the agent must infer which sections apply on each branch.**
`SKILL.md:6-74`.
The skill handles four branches: new project, repair, new investigation in an existing workbench, and scope change. Each needs a different subset of sections. Nothing says, for example, whether a scope change reruns the `.gitignore` merge, `git init` or the host-file check, or whether repair runs the interview. The sequence of steps is visible, but which steps are on the path differs from run to run.
Quote (`SKILL.md:8`): "Build a project around one shared data foundation and zero or more investigations."
Fix: after line 8, add a four-line map. "New project: every section. Repair: Resolve, Create (root files and guides), Complete. New investigation: Resolve, Decide, Interview, investigation records, Complete. Scope change: Resolve (steps 1-3), Decide, Interview, investigation records, Complete."

**M3. R6: the completion criteria for initialization and repair are vague.**
`SKILL.md:64` and `SKILL.md:74`.
"Clear responsibility" and "project conventions are usable" give the agent no way to tell done from not done. Repair has no exhaustive check at all.
Quote (`:74`): "Initialization is complete when the project conventions are usable, foundation records exist for the knowledge already established"
Fix: merge both into one checkable list in "Complete initialization":
- "`AGENTS.md`, `README.md` (with `Active investigation` line), `.gitignore`, and both `workbench-guides/` files exist at the root";
- "every link in created or merged files is relative and resolves";
- "every foundation record created has its condition from 'Create the project foundation' satisfied";
- "the active investigation, if any, has brief/state/history populated with settled facts only";
- "no package, `deliveries/`, or unrequested analysis exists".

**M4. R6: the step order lets `git init` run before the business question is asked.**
`SKILL.md:20` comes before `SKILL.md:24`.
"Resolve the target" initializes Git. Only the next section says to ask for the business question "before creating any project file". An agent running the steps in order creates `.git/` first.
Quote (`:24`): "ask for the business question before creating any project file."
Fix: move the Git paragraph (`:20`) into "Create the project foundation" as its first bullet, or begin `:20` with "Once the target and question are settled,".

**M5. R10: the vocabulary-recording rule appears in two places and its pieces in four more.**
`SKILL.md:38` and `AGENTS.md:29`. Fragments are in `foundation/glossary.md:3,8`, `foundation/catalog.md:3` and `investigation/brief.md:33`.
Both main files list the same destinations (glossary, brief, catalog, history or settings) and both say these replace context maps and ADRs.
Quote (`AGENTS.md:29`): "Record shared meanings in `foundation/glossary.md`, local departures in the brief, population and period choices in settings"
Fix: make `AGENTS.md:29` the single home, since it is always loaded in the project. Reduce `SKILL.md:38` to: "Apply the vocabulary discipline from the template `AGENTS.md` ('Maintain records') while interviewing; resolve each term with a concrete example and record it immediately." Leave the template headers as they are; each header describes only its own file.

**M6. R10/R9: the audience rule appears in five places across two skills, and one copy is phrased as a prohibition.**
`SKILL.md:35`, `AGENTS.md:33`, `investigation/brief.md:17`, `awb-package/SKILL.md:24`, `awb-package/references/package-contract.md:20`.
Quote (`SKILL.md:35`): "Do not ask for the audience as a scoping decision; `awb-package` asks when a package needs it"
Fix: the authoritative homes are `brief.md:17` (the section itself) and `awb-package/SKILL.md:24` (when to ask). Keep `AGENTS.md:33`, because the audience can come up at any time. Rewrite `SKILL.md:35` in positive form: "Record a volunteered audience in the brief's Audience section; leave it blank otherwise, for `awb-package` to collect." Delete the restatement in `package-contract.md:20`'s last sentence, which is in the sibling skill.

**M7. R10/R11: the contents of the evidence file are listed three times, and one list sits in a copied project template.**
`workbench-guides/analysis.md:27`, `investigation/state.md:16`, `references/provenance.md:34`, plus the `awb_provenance.py` docstring.
`state.md` is copied into every project. If the `awb-evidence` schema changes, those copies go stale without anyone noticing.
Quote (`state.md:16`): "That file holds the producing commit or `uncommitted`, uncommitted producing changes, input publications and acquisitions, view definitions"
Fix: in `state.md:16`, keep only the link format and "Keep commits and checksums out of this file." In `analysis.md:27`, keep "Call `record_evidence()` for each result; name unknown provenance with its reason; before a first commit, suggest one." `provenance.md:34` and the docstring stay as the schema's home.

**M8. R10: the shared-correction and validation rules are duplicated between `AGENTS.md` and the guides and templates.**
- The shared-correction rule appears at `AGENTS.md:31`, `foundation/quality.md:15` and `analysis.md:29`.
- The retain-checks-unchanged rule appears at `AGENTS.md:25`, `analysis.md:21`, `references/validation.md:7` and `:49`, and the `awb_validate.py` docstring.
`AGENTS.md:14` already routes "correcting shared data and revalidating findings" to `analysis.md`, so the always-loaded copy is redundant.
Quote (`AGENTS.md:31`): "Accepted shared corrections flag every potentially affected finding with a reason while preserving its prior status"
Fix: move the full correction sentence to `analysis.md:29` and delete it from `AGENTS.md:31`. In `AGENTS.md:25`, keep the invariant ("Validate every result before presentation or recording; only the composition entry run with its settings produces a finding") and drop "retain the complete checks with its evidence, and understand and record failures before promoting a finding", which `analysis.md:21` and `validation.md:49` own.

**M9. R8: the "preserve existing, add missing, surface conflicts" idea is spelled out at more than 12 sites; two pretrained words would replace it.**
Sites: `SKILL.md:16,18,44` (twice), `:45,46`, `AGENTS.md:17`, `data.md:3`, `analysis.md:17,25`, `landing.md:3`, `validation.md:3`, `provenance.md:3`, and the helper docstrings.
Quote (`SKILL.md:44`): "Preserve existing guide content and conventions, add clearly compatible missing sections only when useful, and surface conflicts."
Fix: use two leading words, each defined once.
- **reconcile**, already used at `SKILL.md:18`. Define it once at `SKILL.md:16`: "Reconcile: existing files and conventions win; add what is missing and compatible; surface conflicts for a decision." Then write "reconcile" at every other site.
- **vendor**, for the helpers. Define it in `AGENTS.md`: "Vendor each helper: copy it into `src/` if missing, keep customized copies, import the project copy." Then write "vendor `awb_landing.py` as `src/preparation/landing.py`" in each reference's opening line, and drop the Python-port sentence or keep it once.

**M10. R5: `AGENTS.md` is long for an always-loaded file, and `SKILL.md` is padded with material that belongs elsewhere.**
`assets/workbench/AGENTS.md` (614 words, about 800 tokens every turn) and `SKILL.md` (about 1,650 words).
Every line in them is live, but much of it belongs one rung lower on the ladder.
Quote (`AGENTS.md:21`): "Keep preparation reusable and exploratory transformations local until deliberately promoted."
Fix: H2, M5, M8 and M9 together cut roughly 200 words (about a third) from `AGENTS.md`. Also cut from `AGENTS.md:21` the clauses that restate `data.md`: landing and publication mechanics, and caches. Keep the one-line invariants. In `SKILL.md`, M1, M5, M9 and L8 remove roughly 300-350 words (about 20%).

### Low

**L1. R1: the description repeats the product name and omits the words a user would actually say.**
`SKILL.md:3`.
"analytics workbench" appears twice. "Through the scoping interview" is identity the body already carries. No branch names "a business question" or "data analysis project", which are what a user with no workbench yet would say.
Quote: "start a new investigation in an existing analytics workbench, or resolve a consequential scope change through the scoping interview."
Fix: "Initialize or repair an analytics workbench (a data-analysis project), start an investigation of a new business question, or resolve a consequential scope change."
Model invocation is appropriate here, because `AGENTS.md` and `awb-status` both route to this skill.

**L2. R9: three prohibitions are phrased without, or before, their positive target.**
- `SKILL.md:34`: "rather than asking the user to retrieve them or dispatching a sub-agent". Fix: "Look facts up yourself in the repository, source systems, and available tools."
- `SKILL.md:44`: "create no project-specific skill copies or vendor-specific instruction files". Step 4 already states this guardrail. Fix: "The project's agent instructions are `AGENTS.md` and the two guides; the user-level skills serve every project."
- `awb_provenance.py`/`awb_validate.py` docstrings: "never from the skill folder". The positive "import it from there" is already present, so delete the clause.

**L3. R13: several sentences state what the model already does by default.**
- `AGENTS.md:17`: "Once loaded, reuse their context until a relevant change requires rereading."
- `foundation/catalog.md:17`: "Choose cache identity and refresh behavior from the concrete project need rather than assuming a universal strategy."
- `analysis.md:9`: "Reuse existing operations first."
- `investigation/history.md:15`: "Add entries when the investigation's understanding changes." This restates line 3.
- `SKILL.md:74`: "Create a Git commit only when the user explicitly requests one." This duplicates `:20`'s "without creating a commit".
Fix: delete each sentence.

**L4. R12: `references/provenance.md` steers agents to `file_checksums` for inventories, but packaging uses a different helper.**
`references/provenance.md:51`.
Package inventories use `awb-package`'s `inventory()` (`manifest-helper.md`). No skill calls `file_checksums` except `awb_provenance.py` internally.
Quote: "`file_checksums(paths, *, root=None)` supports inventories"
Fix: delete the sentence, or replace it with "Package inventories use the manifest helper below."

**L5. R6: the format of the `Active investigation` line and the slug character set are not specified, although `awb-status` parses them.**
`SKILL.md:46` and `AGENTS.md:7`.
`awb-status/scripts/collect_status.py:108-111` accepts `[..](investigations/<slug>/state.md)` and slugs matching `[A-Za-z0-9][A-Za-z0-9_-]*`. `record_evidence` also allows `.` in the investigation identifier, so a dotted slug passes evidence recording but reads as "customized" in status.
Quote (`SKILL.md:46`): "point the `Active investigation` line in the project README at its state file"
Fix: give the literal form `Active investigation: [<slug>](investigations/<slug>/state.md)` and the slug rule "lowercase letters, digits, hyphens".

**L6. R8: "checkpoint" in `AGENTS.md` is undefined.**
`AGENTS.md:31`.
Quote: "Write a checkpoint before switching investigations when requested."
Fix: "When the user asks for a checkpoint before switching, update the current `state.md` (date, findings, next steps)."

**L7. R10: the project README restates rules owned by `AGENTS.md` and the guides.**
`README.md:21` repeats the retention ask from `data.md:13`. `README.md:34` repeats the finding rule from `AGENTS.md:25`. `analysis.md:7` repeats the `src/` layout from `README.md:17-20`.
The README is mostly for humans, so these copies cost little, but each is one more copy to keep in sync.
Quote (`README.md:21`): "The agent asks for that location before the first landing and records it"
Fix: drop that sentence from `README.md:21`. Have `analysis.md:7` say "Use the `src/` layout in `README.md`; keep presentation logic out of neutral operations."

**L8. R4/R3: the host-instruction-file concept is split between two places, and its branch-only detail sits inline.**
`SKILL.md:15` and `SKILL.md:69`.
The detection rule is at step 4, and the Claude Code import-path detail is at the report step, as a long parenthetical. The import detail fires only when such a file exists.
Quote (`:69`): "for Claude Code, an import line in the found file giving the path from that file to the project's `AGENTS.md`"
Fix: put the import guidance in step 4, after "report it at completion". Reduce `:69` to "any host-specific instruction file found, with the import line from step 4."

**L9. R12: `SKILL.md` names external skills in an opaque way.**
`SKILL.md:38`.
"`grill-with-docs`" and "the unmodified `domain-modeling` skill" assume the reader knows another plugin set; "unmodified" is unexplained.
Quote: "These records replace `CONTEXT.md`, `CONTEXT-MAP.md`, ADRs, `grill-with-docs`, and the unmodified `domain-modeling` skill."
Fix: "Use these records instead of `CONTEXT.md` files, context maps, or ADRs, including when another installed skill would create them."

**L10. R10 (cross-skill): `awb-status` names `AGENTS.md` as the handler for the retention location, but the procedure lives in the data guide.**
`awb-status/references/next-requests.md:14` names "AGENTS.md record maintenance" as the handler for recording the landed-data location. The procedure is in `workbench-guides/data.md:13`, which `AGENTS.md` mentions only as a routing trigger.
Fix (in awb-status): set the handler to "`workbench-guides/data.md` (Retain originals)".

**L11. R4: the rule for what to read on a new question or scope decision is split across two sections.**
`SKILL.md:14` and `SKILL.md:26`.
Step 3 gives a partial rule and defers with "as described below", and line 26 gives the rest.
Quote (`:14`): "read state only for resumed work, repair, or related method context as described below."
Fix: in `:14`, keep "Inspect the target before changing it: repository instructions, orientation, ignore rules" and move every brief/state/findings read rule into `:26`.

## Rubric coverage

- R1 Description: L1
- R2 In-body pointers: H1. Template pointers in `SKILL.md:44-46,60` and `AGENTS.md:13-15` are clean.
- R3 Hierarchy and disclosure: H2, M1, M2, L8
- R4 Co-location: L8, L11; M6 is also partly a co-location issue
- R5 Sprawl: M10
- R6 Completion criteria: M3, M4, L5. The scoping-interview finish (`SKILL.md:36`) and the four mechanical checks (`analysis.md:19`) are clean.
- R7 Splitting: clean. The scope-change branch carries the initialization sections. A separate model-invoked scoping skill would add a permanent description for little gain, and M2's branch map addresses the cost. No sequence split is needed, because the interview has a sharp finish criterion.
- R8 Leading words: M9, L6
- R9 Negation: M6, L2. `SKILL.md:15` "Never create, edit, or bridge" is a valid hard guardrail paired with "report it".
- R10 Single source of truth: H2, M1, M5, M6, M7, M8, L7, L10
- R11 Environment as cache: M7. The helper interfaces in `references/*.md` are a justified cache: they let the agent skip reading 160-326 line helpers it is told not to inspect, and they match the code.
- R12 Relevance and sediment: M1, L4, L9. No stale signatures were found; `land`, `publish`, `retain`, `session`, `record_evidence`, `compare_evidence`, `profile` and `validate` all match their docs.
- R13 No-ops: L3

Severity counts: high 2, medium 10, low 11 (23 findings).

## Top 3 changes

1. **Make the helper-reference pointer resolvable (H1).** Add one line to the template `AGENTS.md` naming the `awb-init` skill folder for each host: `~/.claude/skills/awb-init/` for Claude Code, `~/.agents/skills/awb-init/` for Codex. Point all five "installed `awb-init` skill" mentions in `data.md` and `analysis.md` at that line. Every acquisition, validation and evidence step depends on reaching these references.
2. **Run one deduplication pass to give each rule a single home (H2, M1, M5, M7, M8).**
   - Scope-change rules stay only in `SKILL.md:26`; `AGENTS.md:9` keeps just the trigger.
   - Data-path rules stay only in `data.md`; `SKILL.md:50-58` becomes one "defer these directories" sentence.
   - The vocabulary destinations stay only in `AGENTS.md:29`.
   - The evidence-contents list stays only in `provenance.md`.
   - The correction rule stays only in `analysis.md`.
   This cuts about a third of the always-loaded `AGENTS.md` and removes the inline path that lets an agent bypass the scoping interview.
3. **Add a branch map and a checkable completion list to `SKILL.md` (M2, M3, M4).** Map which sections each of the four branches runs. Replace "conventions are usable" and "clear responsibility" with the explicit file and link checklist. Move `git init` after the business question is settled.
