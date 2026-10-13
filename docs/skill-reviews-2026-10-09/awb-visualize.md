# Review: awb-visualize

Files that the review read in full: `SKILL.md`, `references/charts.md`, `references/plotting-recipes.md`, `references/figure-delivery.md`, `references/tables.md`, `references/diagrams.md`, `assets/rendering-notes.md`, `assets/awb_style.py`. Sibling material that the review read for R10/R12: `awb-init/assets/workbench/AGENTS.md`, `awb-init/assets/workbench/workbench-guides/analysis.md`, `awb-init/references/provenance.md` and `assets/awb_provenance.py` (figure checksum), `awb-package/SKILL.md`, `awb-package/assets/package-format/findings-template.md` and `m365-assembly.md`, repo `README.md` (install model).

## Summary

The skill is compact (about 190 lines of Markdown), and its routing by output type is sound. But it has two kinds of problems.

First, two critical gaps can change what an agent does:

- Every matplotlib chart needs the plotting-recipes file, but the pointer to this file is an optional "consult" pointer.
- The evidence-figure flow never says when to save the figure relative to `record_evidence`. Also, the helper records a missing figure as a null checksum and does not raise an error.

Second, the chart branch is spread across four files, and these files point at each other many times. Each of several core rules appears four to six times, often as a prohibition (nothing drawn in the image besides labels, display names only, values match narrative rounding, caption content).

The helper interface in `plotting-recipes.md` matches `awb_style.py` exactly (all signatures, return values, failure behavior and constants are correct). The only exception is one wrong grid-axis recipe.

Most of the fix is consolidation:

- Choose one home for each rule.
- Put the tables rules that every branch needs inline.
- Remove the instructions that tell an agent to edit the installed skill.

## Findings

The findings are in order of severity. Line numbers start at 1 in the named file.

### High

**F1. high, R2/R3: `SKILL.md:15`, `references/charts.md:9`. The plotting recipes that every chart needs are behind an optional pointer.**
Every plotted figure goes through the style helper. `charts.md:9` says that the agent must copy and import it, and `charts.md:29` says that the agent must use `save_figure`/`check_text`. The usage rules are only in `plotting-recipes.md`. These rules include the critical ordering rule "Call `apply_style()` before `plt.subplots()`" (line 7) and the failure behavior of `save_figure`. Both pointers to that file are conditional and have weak wording. As a result, the agent opens the file in some runs and does not open it in other runs.
Quote: "For library calls or style-helper usage, consult [plotting recipes](references/plotting-recipes.md)."
Fix: Make the read mandatory for the branch. Change `SKILL.md:15` to "**Charts and plotted figures:** read [charts](references/charts.md), then [plotting recipes](references/plotting-recipes.md) before writing figure code." A better fix is to move `plotting-recipes.md` lines 5–31 (shared style helper, example, helper contract) into `charts.md` under "Analysis and placement". Keep `plotting-recipes.md` for the library-call table and formatters, which are optional.

**F2. high, R6/R4: `references/figure-delivery.md:7,9`; `references/charts.md:7`. The evidence-figure flow has no defined trigger and no order relative to `record_evidence`.**
"Evidence figure" is never defined. The only clue is a folder location (line 7). As a result, the agent cannot tell when the provenance and `figure=` duties apply. The skill also does not state the order. `record_evidence` calculates the checksum of `figure` at call time. It records a missing file with a null size and digest, and it does not give an error (`awb_provenance.py`, `file_checksums`). The guide says to call `record_evidence` from the composition entry (`analysis.md:27`, `provenance.md:7`). But `charts.md:7` puts figure code in "the investigation's figure script". This suggests a separate run after the evidence is already written. The probable result is evidence files that do not have the figure's checksum, with no warning.
Quote: "For an evidence figure, pass its path as `figure=` to `record_evidence`."
Fix: Put the definition and the order together at `figure-delivery.md:7–9`. Suggested text: "An evidence figure supports a finding recorded in `state.md`; all others are exploratory. Render it in the investigation's composition entry, save it with `save_figure`, and pass the returned path as `figure=` to that result's `record_evidence` call. A figure re-saved after recording requires calling `record_evidence` again." Change `charts.md:7` "figure script" to "composition entry (or a figure module it calls)".

### Medium

**F3. medium, R3: `references/tables.md` (whole file); pointers at `SKILL.md:14`, `charts.md:9`, `figure-delivery.md:3`. Material that every branch needs is disclosed behind pointers.**
Every branch gets to `tables.md`:

- Standalone tables go to it directly.
- Charts go to it for the companion table.
- Diagrams go to it for the structure table (`diagrams.md:3`, `figure-delivery.md:3` "read tables for formatting").

The file has 10 lines, but it costs three pointers and one more hop on every run.
Quote: "Use a compact Markdown table for chat, whether standalone or accompanying a chart."
Fix: Move the `tables.md` bullets and the check from line 10 into a `## Tables` section of `SKILL.md`. Delete `tables.md` and the three pointers to it. Delete the line 3 sentence which says that plotting libraries are not necessary. When the rules are inline, it is clear that a standalone table ends with this section.

**F4. medium, R10/R9: `charts.md:19`, `charts.md:29`, `figure-delivery.md:13`, `plotting-recipes.md:9`, `plotting-recipes.md:37`, `figure-delivery.md:8`. The no-caption-in-image rule is stated six times, mostly as a prohibition.**
Each repetition names the forbidden thing ("caption ... in the image"). This keeps the banned behavior in the agent's context. Also, the rule is more prominent than its real rank.
Quote (charts.md:19): "Draw no caption, source line, or notes in the image."
Fix: State it once, positively, in the `SKILL.md` shared contract: "Image text is limited to the title, axis labels, ticks, legend entries, facet titles, and direct labels; every explanation goes in the document caption." Keep one checklist item in `charts.md:29` ("image text is limited to labels"). Delete the repeated statements in `plotting-recipes.md:9` (second sentence), `plotting-recipes.md:37` (second sentence), and `figure-delivery.md:13` (", never draw it inside the image").

**F5. medium, R8/R10: `charts.md:3,18,29`; `plotting-recipes.md:29,35`; `figure-delivery.md:9,13,21`. The display-name rule has several phrasings, but one leading word is enough.**
The same idea appears as "glossary display names and plain business language", "business language", "plain labels", "raw labels", "raw codes", "technical identifiers", "column names", and "single-word names and short codes". The caveat that `check_text` misses short codes appears three times (`charts.md:18`, `charts.md:29`, `plotting-recipes.md:29`).
Quote (charts.md:18): "Every title, tick, legend entry, facet, and annotation must use business language, including short codes that automated checks cannot recognize."
Fix: Use **display names** as the leading word. Define it once in the `SKILL.md` shared contract: "All visible text and captions use display names from the glossary; `check_text` catches identifiers and file names but not single-word codes." Then use only "display names" or "raw names" everywhere else. Delete the last sentence of `charts.md:18` and of `plotting-recipes.md:35`. In `plotting-recipes.md:29`, keep only the list of things that `check_text` flags.

**F6. medium, R10: `SKILL.md:24`; `charts.md:25,27`; `tables.md:6,10`; `plotting-recipes.md:55`; `figure-delivery.md:21`. The rule that displayed values match the analysis and the narrative's rounding is repeated six times.**
The contrary-results rule is also duplicated (`SKILL.md:24`, `charts.md:27`, and `AGENTS.md:23` "Preserve results that challenge the expected explanation").
Quote (tables.md:6): "Use the same rounding as the narrative and any companion figure."
Fix: `SKILL.md:24` is the authoritative home. Branch checklists cite it in a few words ("values match the shared contract") and do not state it again. Delete `plotting-recipes.md:55` "Match narrative rounding." and the duplicate clause in `tables.md:6`.

**F7. medium, R4/R8: `charts.md:3,19,23,26–28`; `figure-delivery.md:13,21`. Caption content is spread across files, and the definition of the term is in the middle of a checklist.**
The rules for what goes in the caption are split between `charts.md` (comparison sentence, annotation reasons, baseline/scale, interval identity) and `figure-delivery.md:13`. `figure-delivery.md:13` lists most of the same items. The definition of "caption" appears at `charts.md:23`, after lines 3 and 19 already use the term. `figure-delivery.md:21` adds a third term, "external caption".
Quote (charts.md:23): "Here, “caption” means the caption in the document containing the image."
Fix: Use **document caption** everywhere. Delete `charts.md:23`. Make `figure-delivery.md:13` the single caption checklist. Then `charts.md` checklist items 2–4 say only what must be visible in the image. They end with "disclosed per the document caption list in figure delivery". Replace "external caption" at `figure-delivery.md:21` with "document caption".

**F8. medium, R10 (cross-skill): `figure-delivery.md:8,17`. This file states again package rules that `awb-package` owns.**
Line 8 says "Package figures follow `awb-package`". Then it paraphrases `awb-package/SKILL.md:47` about how to reuse and re-render legacy figures. Line 17 states again the `*Figure N. ...*` form from `findings-template.md:23–31`. Two copies of the rules for legacy figures will drift.
Quote: "Re-render legacy figures with captions in the image or raw labels for presentation from the plotted numbers in their recorded tables"
Fix: Cut line 8 to "Package figures: follow `awb-package`." In line 17, cut the package clause to "a package figure's caption follows `findings-template.md`."

**F9. medium, R10 (cross-skill contradiction): `figure-delivery.md:13` vs `awb-package/assets/package-format/findings-template.md:28`. The two files disagree about if the caption carries the finding sentence.**
`figure-delivery.md:13` and `charts.md:3` say that the caption must have "the full finding/comparison sentence". The package caption form lists unit, population, period, n, source, and other items, but it has no finding sentence. It puts the finding in the alt text. An agent that writes a package figure gets two specifications.
Quote: "Give the full finding/comparison sentence, unit, population, period, n, source in plain words"
Fix: Decide which file is correct and make both files agree. If the correct rule is that package captions omit the finding because the `###` heading carries it, write in `figure-delivery.md:13`: "Give the comparison sentence (omit in a package, where the section heading states the finding), unit, ...". Otherwise, add "<the comparison sentence>" to the start of the caption placeholder in `findings-template.md:28`.

**F10. medium, R12: `SKILL.md:18`, `figure-delivery.md:23`, `rendering-notes.md:3`. The skill tells the agent to edit its own installed files.**
The skill is installed in a user-level skills directory, and upgrades replace those files (README "Install": "replacing any earlier copies"). Notes that an agent writes there are lost on upgrade, and they are not shared with the project. Under Codex's workspace sandbox, it is possible that the agent cannot write these notes at all. `rendering-notes.md:3` goes further: it asks for a revision of the figure-delivery contract. This is a maintainer's job, not a task in a user project. The "User-confirmed" definition and the "Output rationale" section on that page are also maintainer material.
Quote (SKILL.md:18): "update them when observed behavior changes."
Fix: In `SKILL.md:18` and `figure-delivery.md:23`, replace the update instruction with: "Report the host, its version, and what displayed so the user can file it with the skill maintainers." Move the first paragraph of `rendering-notes.md` (lines 3) into a maintainer note in the repository README or `docs/`.

**F11. medium, R12 (correctness): `plotting-recipes.md:55`. The value-axis grid recipe is wrong for vertical charts.**
`axis="x"` is the value axis only for horizontal bars. For time lines and vertical bars, it puts the grid on the category axis. This contradicts `charts.md:17` ("light grid on the value axis only").
Quote: "a value-axis grid with `ax.grid(axis="x")` when needed"
Fix: Change the sentence to "a value-axis grid with `ax.grid(axis="x")` for horizontal bars or `ax.grid(axis="y")` for vertical bars and lines".

**F12. medium, R6: `charts.md:29`, `figure-delivery.md:21`. "Inspect the rendered image" does not say what action to take.**
Both checklists rely on visual inspection for what `check_text` cannot catch: single-word codes, clipping, and legibility. Neither checklist says to open the saved file. As a result, an agent can treat a `check_text` pass as the inspection. The two checklists also duplicate each other on clipping, raw labels, and legibility.
Quote (charts.md:29): "Inspect the rendered image for column names or raw codes in all text elements"
Fix: In `charts.md:29`, write "Open the saved PNG with the image viewer or file-read tool and read every text element: each is a display name, legible, and unclipped." In `figure-delivery.md:21`, keep only the checks that are specific to delivery (width, opacity, and that image, caption, table, alt text, and evidence agree).

**F13. medium, R2/R10: `charts.md:9`, `plotting-recipes.md:7`, `awb_style.py:3`. The copy-the-style-helper instruction appears three times, with a trigger that can overwrite customizations.**
"On the first project figure" needs the agent to remember history. In a new session, the agent possibly does not have that history. The trigger also does not include the guard that the sibling skills use for their helpers: "only if missing; preserve customized copies" (`analysis.md:17,25`, `provenance.md:3`). `charts.md:9` itself says that defaults are changed in the project copy. If that copy is overwritten, these changes are lost.
Quote: "On the first project figure, copy [awb_style.py](../assets/awb_style.py) to `src/presentation/style.py` and import from the project module."
Fix: Keep a single statement at the location that F1 makes the home (for either of the F1 options): "If `src/presentation/style.py` is missing, copy [awb_style.py](../assets/awb_style.py) there; otherwise import the existing, possibly customized, module." Delete the duplicate at `plotting-recipes.md:7`, first sentence.

**F14. medium, R10/R8: `SKILL.md:22`; `charts.md:7`; `plotting-recipes.md:41`. The presentation boundary states project rules again, and its terminology drifts.**
"Pass frames in memory ... rather than creating CSV intermediates" duplicates `AGENTS.md:21` ("Intermediate computation belongs in canonical views and in-process results"). That file is always loaded in a workbench project. `plotting-recipes.md:41` says it a third time. The location of display-only classifications has two different terms: "the investigation's presentation code" (`SKILL.md:22`) and "the investigation's figure script" (`charts.md:7`).
Quote (SKILL.md:22): "Pass frames in memory from canonical DuckDB views or in-process results, rather than creating CSV intermediates."
Fix: Delete that sentence from `SKILL.md:22`, because `AGENTS.md:21` owns it. Keep `plotting-recipes.md:41` as the concrete call (`con.sql(query).df()`). Choose one term for the location of display classifications. Use this term in both `SKILL.md:22` and `charts.md:7`. Then delete the repeated boundary statement in `charts.md:7` ("Figure functions take analytical results and draw them.").

**F15. medium, R2/R12: `diagrams.md:3`. The Mermaid branches cannot be told apart.**
"Where the host supports it" and "when rendering is unconfirmed" read as two branches. But both produce the same artifact: a fenced `mermaid` block with a structure table. The skill leaves the real difference (a host render tool such as VS Code's `renderMermaidDiagram` versus Markdown rendering) to the rendering notes.
Quote: "Use Mermaid for chat where the host supports it. ... Keep source in a fenced `mermaid` block when rendering is unconfirmed, including github.com chat."
Fix: Replace the paragraph with: "In chat, write the diagram as a fenced `mermaid` block followed by a compact structure table. Where the host offers a Mermaid render tool (VS Code `renderMermaidDiagram`), call it as well. Consult the [rendering notes](../assets/rendering-notes.md) only when a host's support is unknown."

### Low

**F16. low, R1: `SKILL.md:3`. The description's trigger sentence repeats its identity sentence.**
"A visual or a results table" repeats "charts, figures, diagrams, and formatted results tables". "Charts" and "figures" name one branch twice. The list of destinations (chat, record, package) covers every case. As a result, it does not make the trigger narrower.
Quote: "Use whenever a visual or a results table is produced for chat, an investigation record, or a delivery package."
Fix: "Charts, diagrams, and results tables for analytics workbench results, styled to display in agent chat and paste into documents. Use when producing a chart or plotted figure, a process or lineage diagram, or a results table." Model invocation is correct. `AGENTS.md:15` and the agent must get to this skill without a prompt, and `awb-package` links to it.

**F17. low, R3/R10: `charts.md:9,19,30`. Pointers repeat inside `charts.md`.**
`charts.md` points to `figure-delivery.md` three times, and to `tables.md` and `plotting-recipes.md` once each. But `SKILL.md:14–17` already routes to all of them.
Quote (charts.md:9): "Read [figure delivery](figure-delivery.md) before delivery and [tables](tables.md) for the companion table."
Fix: Keep one pointer, at checklist item 6 (line 30). Delete the last sentence of line 9 and the last sentence of line 19.

**F18. low, R11/R12: `plotting-recipes.md:17–18,28–31`. The helper contract is cached here. The cache is accurate today, but the example contradicts it.**
The cached contract matches `awb_style.py` exactly. But `charts.md:9` invites customization of the project copy, so the cache can become stale relative to that copy. The example calls `apply_style()` on every draw, but line 28 and the docstring say "once per process". One gotcha is missing: `save_figure` forces the `.png` suffix (`Path(path).with_suffix(".png")`). As a result, a path that ends in `.svg` writes a PNG, with no warning.
Quote (line 28): "`apply_style()` configures the theme and rcParams once per process."
Fix: Reduce lines 28–31 to the gotchas:

- Call `apply_style()` once before the first `plt.subplots()`.
- `save_figure` raises before it writes and leaves the figure open.
- On success, `save_figure` closes the figure, forces `.png`, keeps the current size, and returns the PNG path.

Move `apply_style()` out of `draw_rates`, or add a comment that says it is idempotent.

**F19. low, R9: `charts.md:16`, `figure-delivery.md:13`, `tables.md:3`. These prohibitions can be stated positively.**
Quotes: "Color must not be the only cue." / "Name no view, column, setting, or file." / "A standalone table requires no plotting libraries, style setup, image, or image checklist."
Fix: "Pair every color distinction with a second cue (direct label, position, or marker)." Delete "Name no view, column, setting, or file." The preceding "source in plain words (data owner, extract, period)" already states the positive target. The fix for F3 removes the `tables.md:3` sentence.

**F20. low, R10: `charts.md:3` / `plotting-recipes.md:29,37`; `charts.md:7` / `plotting-recipes.md:53`; `figure-delivery.md:3` / `awb_style.py:22–25`. Small duplicates.**
The 65-character title limit appears three times (`MAX_TEXT_CHARS` also enforces it). "Seed bootstraps" appears twice. The 6.5 in / 200 dpi / 1300 px size is stated again next to the module that `charts.md:9` calls authoritative. Mermaid exports do not use the module, so the size line is justified for them.
Quote (plotting-recipes.md:37): "Keep the title one line, at most 65 characters"
Fix: Keep the title rule at `charts.md:3` and delete it at `plotting-recipes.md:37`. Keep "seed" only at `plotting-recipes.md:53`. At `figure-delivery.md:3`, add "(the style module's `WIDTH_IN`/`DPI`)" so readers know which copy is the source.

**F21. low, R6: `diagrams.md:11`. A check has no remedy.**
Quote: "Check the actual export dimensions; the viewport option alone may not produce the required image width."
Fix: Add the corrective action: "If the PNG is narrower than 1300 px, re-export with a larger `-s` scale factor until it reaches that width."

**F22. low, R13: `SKILL.md:8` (first sentence), `charts.md:3` (first sentence), `diagrams.md:13` ("labels are legible"). These sentences do not change behavior.**
`SKILL.md:8` repeats the description. The form bullets already carry out "Choose the form from the comparison the reader must make". "Labels are legible" is a weaker copy of the legibility check that F12 covers.
Quote: "Present analytical results so they remain legible in chat and documents."
Fix: Delete these sentences or clauses. Keep the path-resolution sentence at `SKILL.md:8`.

**F23. low, R2/R5: `SKILL.md:17`. The pointer lists the target's table of contents.**
Quote: "read [figure delivery](references/figure-delivery.md) for PNG, document caption, and table output, placement, accessibility, and evidence provenance."
Fix: "**Image delivery:** before showing or saving a chart or exported diagram, read [figure delivery](references/figure-delivery.md)."

**F24. low, R12: `tables.md:8`. A package-only fact is in the general tables reference.**
Quote: "Package tables reach Word through the M365 assembly."
Fix: Delete it. `m365-assembly.md:72` owns table conversion for packages.

## Rubric coverage

- R1 Description: F16
- R2 In-body pointers: F1, F13, F15, F23
- R3 Hierarchy and disclosure: F1, F3, F17
- R4 Co-location: F2, F7
- R5 Sprawl: clean (about 190 Markdown lines, and the longest file has 55 lines). Only F23 touches it.
- R6 Completion criteria: F2, F12, F21. `SKILL.md:26` gives a clear overall criterion ("the selected branch's checks pass and any evidence figure is recorded").
- R7 Splitting: clean. Model invocation is justified, because `AGENTS.md:15`, the agent's own judgment, and `awb-package` must all reach the skill. A sequence split is not necessary, because there is no fuzzy early step that later steps can rush.
- R8 Leading words: F5 (display names), F7 (document caption), F14 (presentation code vs figure script)
- R9 Negation: F4, F19
- R10 Duplication: F4, F5, F6, F8, F9, F13, F14, F17, F20. `AGENTS.md:15` overlaps the description on purpose to make the trigger sharper. This is acceptable.
- R11 Environment cache: F18. The helper interface in `plotting-recipes.md` matches `awb_style.py`: `apply_style`, `check_text` (the flagged classes, empty list means pass), `save_figure` (signature, ValueError before it writes, figure left open, mkdir, metadata stringified, optional SVG, figure closed, Path returned), and every named constant exists.
- R12 Relevance and sediment: F10, F11, F15, F18, F24
- R13 No-ops: F22

## Top 3 changes

1. **Make the chart branch one mandatory read path (F1, F3, F17).** Move the style-helper section of `plotting-recipes.md` (lines 5–31) into `charts.md`, or change the pointer to "read ... before writing figure code". Put `tables.md` inline in `SKILL.md`, because every branch needs it. Reduce the pointer mesh in `charts.md` to one pointer to figure delivery. This removes the main source of run-to-run variance, which is if the agent learns the `apply_style()` order and the behavior of `save_figure`.
2. **Define "evidence figure" and fix its order relative to `record_evidence` (F2).** Write one paragraph in `figure-delivery.md` that says:
   - An evidence figure supports a recorded finding.
   - Render it in the composition entry.
   - Save it before you call `record_evidence` with `figure=`.
   - If the figure is saved again, record it again.

   This closes a gap in which evidence records a null figure checksum with no warning.
3. **Give each repeated rule one positive home in the `SKILL.md` shared contract (F4, F5, F6, F7).** Write three sentences there: "Image text is limited to labels; every explanation goes in the document caption." "All visible text uses display names." "Displayed values match the analysis and the narrative's rounding." Then do these steps:
   - Remove the four to six repeated statements of each rule across the references.
   - Use "document caption" and "display names" as the leading words in all files.
   - Remove the "draw no caption" prohibitions.
