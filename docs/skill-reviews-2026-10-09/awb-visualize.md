# Review: awb-visualize

Files read in full: `SKILL.md`, `references/charts.md`, `references/plotting-recipes.md`, `references/figure-delivery.md`, `references/tables.md`, `references/diagrams.md`, `assets/rendering-notes.md`, `assets/awb_style.py`. Sibling material read for R10/R12: `awb-init/assets/workbench/AGENTS.md`, `awb-init/assets/workbench/workbench-guides/analysis.md`, `awb-init/references/provenance.md` and `assets/awb_provenance.py` (figure checksum), `awb-package/SKILL.md`, `awb-package/assets/package-format/findings-template.md` and `m365-assembly.md`, repo `README.md` (install model).

## Summary

The skill is compact (about 190 lines of Markdown) and its routing by output type is sound, but it has two kinds of problems. First, two critical gaps can change what an agent does. The plotting-recipes file, which every matplotlib chart needs, sits behind an optional "consult" pointer. The evidence-figure flow never says when to save the figure relative to `record_evidence`, and the helper records a missing figure as a null checksum without raising. Second, the chart branch is spread across four files that point at each other repeatedly. Several core rules (nothing drawn in the image besides labels, display names only, values match narrative rounding, caption content) are each restated four to six times, often as prohibitions. The helper interface in `plotting-recipes.md` matches `awb_style.py` exactly (all signatures, return values, failure behavior and constants check out), apart from one wrong grid-axis recipe. The fix is mostly consolidation: choose one home for each rule, inline the tables rules that every branch needs, and remove the instructions that would make an agent edit the installed skill.

## Findings

Sorted by severity. Line numbers are 1-based in the named file.

### High

**F1. high, R2/R3: `SKILL.md:15`, `references/charts.md:9`. The plotting recipes every chart needs sit behind an optional pointer.**
Every plotted figure goes through the style helper: `charts.md:9` requires copying and importing it, and `charts.md:29` requires `save_figure`/`check_text`. The usage rules live only in `plotting-recipes.md`, including the critical ordering rule "Call `apply_style()` before `plt.subplots()`" (line 7) and the failure behavior of `save_figure`. Both pointers to that file are conditional and weakly worded, so whether the agent opens it varies from run to run.
Quote: "For library calls or style-helper usage, consult [plotting recipes](references/plotting-recipes.md)."
Fix: Make the read mandatory for the branch. `SKILL.md:15` becomes "**Charts and plotted figures:** read [charts](references/charts.md), then [plotting recipes](references/plotting-recipes.md) before writing figure code." Better still, move `plotting-recipes.md` lines 5–31 (shared style helper, example, helper contract) into `charts.md` under "Analysis and placement". Keep `plotting-recipes.md` for the library-call table and formatters, which are optional.

**F2. high, R6/R4: `references/figure-delivery.md:7,9`; `references/charts.md:7`. The evidence-figure flow has no defined trigger and no ordering against `record_evidence`.**
"Evidence figure" is never defined. The only clue is a folder location (line 7), so the agent cannot tell when the provenance and `figure=` duties apply. Ordering is also unstated. `record_evidence` checksums `figure` at call time, and a missing file is recorded with null size and digest, with no error (`awb_provenance.py`, `file_checksums`). The guide says to call `record_evidence` from the composition entry (`analysis.md:27`, `provenance.md:7`). `charts.md:7`, however, puts figure code in "the investigation's figure script", which suggests a separate run after evidence has already been written. The likely result is evidence files that silently lack the figure's checksum.
Quote: "For an evidence figure, pass its path as `figure=` to `record_evidence`."
Fix: Put the definition and the order together at `figure-delivery.md:7–9`. Suggested text: "An evidence figure supports a finding recorded in `state.md`; all others are exploratory. Render it in the investigation's composition entry, save it with `save_figure`, and pass the returned path as `figure=` to that result's `record_evidence` call. A figure re-saved after recording requires calling `record_evidence` again." Change `charts.md:7` "figure script" to "composition entry (or a figure module it calls)".

### Medium

**F3. medium, R3: `references/tables.md` (whole file); pointers at `SKILL.md:14`, `charts.md:9`, `figure-delivery.md:3`. Material every branch needs is disclosed behind pointers.**
Every branch reaches `tables.md`: standalone tables directly, charts for the companion table, and diagrams for the structure table (`diagrams.md:3`, `figure-delivery.md:3` "read tables for formatting"). The file is 10 lines and costs three pointers plus an extra hop on every run.
Quote: "Use a compact Markdown table for chat, whether standalone or accompanying a chart."
Fix: Move the `tables.md` bullets and the check from line 10 into a `## Tables` section of `SKILL.md`. Delete `tables.md` and the three pointers to it. Drop the line 3 sentence about not needing plotting libraries; once the rules are inline, a standalone table plainly ends with this section.

**F4. medium, R10/R9: `charts.md:19`, `charts.md:29`, `figure-delivery.md:13`, `plotting-recipes.md:9`, `plotting-recipes.md:37`, `figure-delivery.md:8`. The no-caption-in-image rule is stated six times, mostly as a prohibition.**
Each repetition names the forbidden thing ("caption ... in the image"), which keeps the banned behavior in the agent's context. Its prominence is also inflated past its real rank.
Quote (charts.md:19): "Draw no caption, source line, or notes in the image."
Fix: State it once, positively, in the `SKILL.md` shared contract: "Image text is limited to the title, axis labels, ticks, legend entries, facet titles, and direct labels; every explanation goes in the document caption." Keep one checklist item in `charts.md:29` ("image text is limited to labels"). Delete the restatements in `plotting-recipes.md:9` (second sentence), `plotting-recipes.md:37` (second sentence), and `figure-delivery.md:13` (", never draw it inside the image").

**F5. medium, R8/R10: `charts.md:3,18,29`; `plotting-recipes.md:29,35`; `figure-delivery.md:9,13,21`. Several phrasings of the display-name rule, where one leading word would do.**
The same idea appears as "glossary display names and plain business language", "business language", "plain labels", "raw labels", "raw codes", "technical identifiers", "column names", and "single-word names and short codes". The caveat that `check_text` misses short codes appears three times (`charts.md:18`, `charts.md:29`, `plotting-recipes.md:29`).
Quote (charts.md:18): "Every title, tick, legend entry, facet, and annotation must use business language, including short codes that automated checks cannot recognize."
Fix: Use **display names** as the leading word, defined once in the `SKILL.md` shared contract: "All visible text and captions use display names from the glossary; `check_text` catches identifiers and file names but not single-word codes." Then use only "display names" or "raw names" everywhere else. Delete the last sentence of `charts.md:18` and of `plotting-recipes.md:35`. In `plotting-recipes.md:29`, keep only the list of things `check_text` flags.

**F6. medium, R10: `SKILL.md:24`; `charts.md:25,27`; `tables.md:6,10`; `plotting-recipes.md:55`; `figure-delivery.md:21`. The rule that displayed values match the analysis and the narrative's rounding is repeated six times.**
The contrary-results rule is also duplicated (`SKILL.md:24`, `charts.md:27`, and `AGENTS.md:23` "Preserve results that challenge the expected explanation").
Quote (tables.md:6): "Use the same rounding as the narrative and any companion figure."
Fix: `SKILL.md:24` is the authoritative home. Branch checklists cite it in a few words ("values match the shared contract") and do not restate it. Delete `plotting-recipes.md:55` "Match narrative rounding." and the duplicate clause in `tables.md:6`.

**F7. medium, R4/R8: `charts.md:3,19,23,26–28`; `figure-delivery.md:13,21`. Caption content is spread across files, and the term is defined in the middle of a checklist.**
The rules for what goes in the caption are split between `charts.md` (comparison sentence, annotation reasons, baseline/scale, interval identity) and `figure-delivery.md:13`, which lists most of the same items. The definition of "caption" appears at `charts.md:23`, after the term has already been used at lines 3 and 19. `figure-delivery.md:21` adds a third term, "external caption".
Quote (charts.md:23): "Here, “caption” means the caption in the document containing the image."
Fix: Use **document caption** everywhere and delete `charts.md:23`. Make `figure-delivery.md:13` the single caption checklist. `charts.md` checklist items 2–4 then say only what must be visible in the image, and end with "disclosed per the document caption list in figure delivery". Replace "external caption" at `figure-delivery.md:21` with "document caption".

**F8. medium, R10 (cross-skill): `figure-delivery.md:8,17`. This file restates package rules owned by `awb-package`.**
Line 8 says "Package figures follow `awb-package`" and then paraphrases `awb-package/SKILL.md:47` on reuse and re-rendering legacy figures. Line 17 restates the `*Figure N. ...*` form from `findings-template.md:23–31`. Two copies of the rules for legacy figures will drift.
Quote: "Re-render legacy figures with captions in the image or raw labels for presentation from the plotted numbers in their recorded tables"
Fix: Cut line 8 to "Package figures: follow `awb-package`." In line 17, cut the package clause to "a package figure's caption follows `findings-template.md`."

**F9. medium, R10 (cross-skill contradiction): `figure-delivery.md:13` vs `awb-package/assets/package-format/findings-template.md:28`. The two disagree about whether the caption carries the finding sentence.**
`figure-delivery.md:13` and `charts.md:3` require "the full finding/comparison sentence" in the caption. The package caption form lists unit, population, period, n, source, and so on, but no finding sentence, and puts the finding in the alt text instead. An agent writing a package figure gets two specifications.
Quote: "Give the full finding/comparison sentence, unit, population, period, n, source in plain words"
Fix: Decide which is right and align both files. If package captions should omit the finding because the `###` heading carries it, write in `figure-delivery.md:13`: "Give the comparison sentence (omit in a package, where the section heading states the finding), unit, ...". Otherwise, add "<the comparison sentence>" to the start of the caption placeholder in `findings-template.md:28`.

**F10. medium, R12: `SKILL.md:18`, `figure-delivery.md:23`, `rendering-notes.md:3`. The skill tells the agent to edit its own installed files.**
The skill is installed in a user-level skills directory, and upgrades replace those files (README "Install": "replacing any earlier copies"). Notes an agent writes there are lost on upgrade, are not shared with the project, and under Codex's workspace sandbox may not be writable at all. `rendering-notes.md:3` goes further and asks for a revision of the figure-delivery contract, which is a maintainer's job, not a task in a user project. The "User-confirmed" definition and the "Output rationale" section on that page are also maintainer material.
Quote (SKILL.md:18): "update them when observed behavior changes."
Fix: In `SKILL.md:18` and `figure-delivery.md:23`, replace the update instruction with: "Report the host, its version, and what displayed so the user can file it with the skill maintainers." Move the first paragraph of `rendering-notes.md` (lines 3) into a maintainer note in the repository README or `docs/`.

**F11. medium, R12 (correctness): `plotting-recipes.md:55`. The value-axis grid recipe is wrong for vertical charts.**
`axis="x"` is the value axis only for horizontal bars. For time lines and vertical bars it puts the grid on the category axis, which contradicts `charts.md:17` ("light grid on the value axis only").
Quote: "a value-axis grid with `ax.grid(axis="x")` when needed"
Fix: Change the sentence to "a value-axis grid with `ax.grid(axis="x")` for horizontal bars or `ax.grid(axis="y")` for vertical bars and lines".

**F12. medium, R6: `charts.md:29`, `figure-delivery.md:21`. "Inspect the rendered image" does not say what action to take.**
Both checklists rely on visual inspection for what `check_text` cannot catch: single-word codes, clipping, and legibility. Neither says to open the saved file, so an agent can treat a passing `check_text` as the inspection. The two checklists also duplicate each other on clipping, raw labels, and legibility.
Quote (charts.md:29): "Inspect the rendered image for column names or raw codes in all text elements"
Fix: In `charts.md:29`, write "Open the saved PNG with the image viewer or file-read tool and read every text element: each is a display name, legible, and unclipped." In `figure-delivery.md:21`, keep only the checks specific to delivery (width, opacity, and that image, caption, table, alt text, and evidence agree).

**F13. medium, R2/R10: `charts.md:9`, `plotting-recipes.md:7`, `awb_style.py:3`. The copy-the-style-helper instruction appears three times, with a trigger that can overwrite customizations.**
"On the first project figure" depends on remembering history the agent may not have in a new session. It also omits the guard the sibling skills use for their helpers: "only if missing; preserve customized copies" (`analysis.md:17,25`, `provenance.md:3`). `charts.md:9` itself says defaults are changed in the project copy, so overwriting that copy loses them.
Quote: "On the first project figure, copy [awb_style.py](../assets/awb_style.py) to `src/presentation/style.py` and import from the project module."
Fix: Keep a single statement, at whichever location F1 makes the home: "If `src/presentation/style.py` is missing, copy [awb_style.py](../assets/awb_style.py) there; otherwise import the existing, possibly customized, module." Delete the duplicate at `plotting-recipes.md:7`, first sentence.

**F14. medium, R10/R8: `SKILL.md:22`; `charts.md:7`; `plotting-recipes.md:41`. The presentation boundary restates project rules and drifts in terminology.**
"Pass frames in memory ... rather than creating CSV intermediates" duplicates `AGENTS.md:21` ("Intermediate computation belongs in canonical views and in-process results"), which is always loaded in a workbench project. `plotting-recipes.md:41` says it a third time. The location of display-only classifications is given in two different terms: "the investigation's presentation code" (`SKILL.md:22`) and "the investigation's figure script" (`charts.md:7`).
Quote (SKILL.md:22): "Pass frames in memory from canonical DuckDB views or in-process results, rather than creating CSV intermediates."
Fix: Delete that sentence from `SKILL.md:22`; `AGENTS.md:21` owns it. Keep `plotting-recipes.md:41` as the concrete call (`con.sql(query).df()`). Choose one term for where display classifications live and use it in both `SKILL.md:22` and `charts.md:7`. Then delete the restated boundary in `charts.md:7` ("Figure functions take analytical results and draw them.").

**F15. medium, R2/R12: `diagrams.md:3`. The Mermaid branches cannot be told apart.**
"Where the host supports it" and "when rendering is unconfirmed" read as two branches, but both produce the same artifact: a fenced `mermaid` block with a structure table. The real difference (a host render tool such as VS Code's `renderMermaidDiagram` versus Markdown rendering) is left to the rendering notes.
Quote: "Use Mermaid for chat where the host supports it. ... Keep source in a fenced `mermaid` block when rendering is unconfirmed, including github.com chat."
Fix: Replace the paragraph with: "In chat, write the diagram as a fenced `mermaid` block followed by a compact structure table. Where the host offers a Mermaid render tool (VS Code `renderMermaidDiagram`), call it as well. Consult the [rendering notes](../assets/rendering-notes.md) only when a host's support is unknown."

### Low

**F16. low, R1: `SKILL.md:3`. The description's trigger sentence repeats its identity sentence.**
"A visual or a results table" restates "charts, figures, diagrams, and formatted results tables". "Charts" and "figures" name one branch twice. The list of destinations (chat, record, package) covers every case, so it narrows nothing.
Quote: "Use whenever a visual or a results table is produced for chat, an investigation record, or a delivery package."
Fix: "Charts, diagrams, and results tables for analytics workbench results, styled to display in agent chat and paste into documents. Use when producing a chart or plotted figure, a process or lineage diagram, or a results table." Model invocation is correct: `AGENTS.md:15` and the agent must reach this skill unprompted, and `awb-package` links to it.

**F17. low, R3/R10: `charts.md:9,19,30`. Pointers repeat inside `charts.md`.**
`charts.md` points to `figure-delivery.md` three times and to `tables.md` and `plotting-recipes.md` once each, although `SKILL.md:14–17` already routes to all of them.
Quote (charts.md:9): "Read [figure delivery](figure-delivery.md) before delivery and [tables](tables.md) for the companion table."
Fix: Keep one pointer, at checklist item 6 (line 30). Delete the last sentence of line 9 and the last sentence of line 19.

**F18. low, R11/R12: `plotting-recipes.md:17–18,28–31`. The helper contract is cached here; the cache is accurate today, but the example contradicts it.**
The cached contract matches `awb_style.py` exactly. However, `charts.md:9` invites customizing the project copy, so the cache can go stale against it. The example calls `apply_style()` on every draw, while line 28 and the docstring say "once per process". One gotcha is missing: `save_figure` forces the `.png` suffix (`Path(path).with_suffix(".png")`), so a path ending `.svg` silently writes a PNG.
Quote (line 28): "`apply_style()` configures the theme and rcParams once per process."
Fix: Cut lines 28–31 down to the gotchas: call `apply_style()` once before the first `plt.subplots()`; `save_figure` raises before writing and leaves the figure open; on success it closes the figure, forces `.png`, keeps the current size, and returns the PNG path. Move `apply_style()` out of `draw_rates`, or comment that it is idempotent.

**F19. low, R9: `charts.md:16`, `figure-delivery.md:13`, `tables.md:3`. Prohibitions that could be stated positively.**
Quotes: "Color must not be the only cue." / "Name no view, column, setting, or file." / "A standalone table requires no plotting libraries, style setup, image, or image checklist."
Fix: "Pair every color distinction with a second cue (direct label, position, or marker)." Delete "Name no view, column, setting, or file.": the preceding "source in plain words (data owner, extract, period)" already states the positive target. The `tables.md:3` sentence goes away under F3.

**F20. low, R10: `charts.md:3` / `plotting-recipes.md:29,37`; `charts.md:7` / `plotting-recipes.md:53`; `figure-delivery.md:3` / `awb_style.py:22–25`. Small duplicates.**
The 65-character title limit appears three times (it is also enforced by `MAX_TEXT_CHARS`). "Seed bootstraps" appears twice. The 6.5 in / 200 dpi / 1300 px size is restated next to the module that `charts.md:9` calls authoritative. The size line is justified for Mermaid exports, which do not use the module.
Quote (plotting-recipes.md:37): "Keep the title one line, at most 65 characters"
Fix: Keep the title rule at `charts.md:3` and delete it at `plotting-recipes.md:37`. Keep "seed" only at `plotting-recipes.md:53`. At `figure-delivery.md:3`, add "(the style module's `WIDTH_IN`/`DPI`)" so readers know which copy is the source.

**F21. low, R6: `diagrams.md:11`. A check with no remedy.**
Quote: "Check the actual export dimensions; the viewport option alone may not produce the required image width."
Fix: Add the corrective action: "If the PNG is narrower than 1300 px, re-export with a larger `-s` scale factor until it reaches that width."

**F22. low, R13: `SKILL.md:8` (first sentence), `charts.md:3` (first sentence), `diagrams.md:13` ("labels are legible"). Sentences that do not change behavior.**
`SKILL.md:8` repeats the description. "Choose the form from the comparison the reader must make" is already carried out by the form bullets. "Labels are legible" is a weaker copy of the legibility check covered by F12.
Quote: "Present analytical results so they remain legible in chat and documents."
Fix: Delete these sentences or clauses. Keep the path-resolution sentence at `SKILL.md:8`.

**F23. low, R2/R5: `SKILL.md:17`. The pointer lists the target's table of contents.**
Quote: "read [figure delivery](references/figure-delivery.md) for PNG, document caption, and table output, placement, accessibility, and evidence provenance."
Fix: "**Image delivery:** before showing or saving a chart or exported diagram, read [figure delivery](references/figure-delivery.md)."

**F24. low, R12: `tables.md:8`. A package-only fact sits in the general tables reference.**
Quote: "Package tables reach Word through the M365 assembly."
Fix: Delete it; `m365-assembly.md:72` owns table conversion for packages.

## Rubric coverage

- R1 Description: F16
- R2 In-body pointers: F1, F13, F15, F23
- R3 Hierarchy and disclosure: F1, F3, F17
- R4 Co-location: F2, F7
- R5 Sprawl: clean (about 190 Markdown lines; the longest file is 55 lines). Only F23 touches it.
- R6 Completion criteria: F2, F12, F21. `SKILL.md:26` gives a clear overall criterion ("the selected branch's checks pass and any evidence figure is recorded").
- R7 Splitting: clean. Model invocation is warranted, since `AGENTS.md:15`, the agent's own judgment, and `awb-package` must all reach the skill. No sequence split is needed because there is no fuzzy early step for later steps to rush.
- R8 Leading words: F5 (display names), F7 (document caption), F14 (presentation code vs figure script)
- R9 Negation: F4, F19
- R10 Duplication: F4, F5, F6, F8, F9, F13, F14, F17, F20. `AGENTS.md:15` overlaps the description on purpose to sharpen the trigger, which is acceptable.
- R11 Environment cache: F18. The helper interface in `plotting-recipes.md` matches `awb_style.py`: `apply_style`, `check_text` (the flagged classes, empty list means pass), `save_figure` (signature, ValueError before writing, figure left open, mkdir, metadata stringified, optional SVG, figure closed, Path returned), and every named constant exists.
- R12 Relevance and sediment: F10, F11, F15, F18, F24
- R13 No-ops: F22

## Top 3 changes

1. **Make the chart branch one mandatory read path (F1, F3, F17).** Move the style-helper section of `plotting-recipes.md` (lines 5–31) into `charts.md`, or change the pointer to "read ... before writing figure code". Inline `tables.md` into `SKILL.md`, since every branch needs it. Reduce the pointer mesh in `charts.md` to one pointer to figure delivery. This removes the main source of run-to-run variance: whether the agent learns `apply_style()` ordering and how `save_figure` behaves.
2. **Define "evidence figure" and fix its ordering against `record_evidence` (F2).** One paragraph in `figure-delivery.md`: an evidence figure supports a recorded finding; render it in the composition entry; save it before calling `record_evidence` with `figure=`; re-record if the figure is re-saved. This closes a gap where evidence silently records a null figure checksum.
3. **Give each repeated rule one positive home in the `SKILL.md` shared contract (F4, F5, F6, F7).** Write three sentences there: "Image text is limited to labels; every explanation goes in the document caption." "All visible text uses display names." "Displayed values match the analysis and the narrative's rounding." Then remove the four to six restatements of each across the references, use "document caption" and "display names" as the leading words throughout, and drop the "draw no caption" prohibitions.
