# M365 assembly instructions

`findings.md` is the authoritative source of every word, number, and figure in the delivered documents. It is already written for the audience below, in their terms. Use Microsoft 365 to distill an executive summary from it, assemble the detailed report, and improve presentation, while preserving every substantive claim, value, qualification, and caveat.

## Audience

The draft replaces this section with the investigation brief's **Audience** section:

- **Readers:** who will read the delivered documents.
- **What they already know:**
- **Decision they own:**
- **Terms they use:**

## Files in this package

The draft replaces this list with every file it includes, one path per line relative to the package directory. Write **None** under figures or datasets when the package has none.

- `findings.md`: the source of all document content.
- `methodology.md`: internal reference for the reasoning behind decisions; never rendered.
- `m365-assembly.md`: these instructions; never rendered.
- `manifest.<format>`: provenance record; never rendered.
- Figures: `figures/<figure>.png`, each embedded in `findings.md` with its alt text and caption.
- Datasets: `datasets/<dataset>.<format>`, each described in the **Supporting datasets** section of `findings.md`.

## Using methodology.md

Consult `methodology.md` to understand why a decision was made, or to answer the requester's question about one in plain language. Its sections for each finding use the same headings as `findings.md`. Never quote it, and never copy its identifiers, file names, settings, or code terms into a document. If a document needs a method point that only `methodology.md` has, do not add it: raise it with the requester as a gap to fix upstream in the workbench.

## Ask before drafting

Before drafting any document, check for the conditions below. When one holds, ask the requester before drafting. Put every question in one message, keep each to a sentence or two, and propose a default the requester can accept with a yes.

- **Audience or decision missing or unclear.** The **Audience** section above is blank, or the requester names readers or a decision that differ from it. Example: "The package is written for regional operations managers deciding on staffing. Is this summary for them, or for the finance committee? Default: regional operations managers."
- **Length or format unstated, and `findings.md` runs past a page** (about 500 words of body text). Example: "Do you want a one-page executive summary, a full report, or both in one document? Default: a one-page summary followed by the full report."
- **No clear answer, or findings conflict.** The **Answer** section is missing, hedged without a stated lean, or two findings point different ways without saying how they reconcile. Example: "Findings 2 and 3 point in opposite directions and the package does not say which governs the decision. Should the summary present both without a lead answer? Default: yes, both, with neither as the headline."
- **A caveat's effect on a headline claim is ambiguous.** It is unclear whether a caveat narrows, weakens, or leaves intact a claim the summary would lead with. Example: "The late-closure rate carries a caveat about missing March records. Should the summary lead with it, given the caveat? Default: lead with it and state the caveat in the same sentence."
- **A finding needs method context that only `methodology.md` has.** A reader could not trust or interpret the finding from `findings.md` alone. Example: "The second finding depends on how repeat cases are counted, which the package explains only in its internal notes. Should I flag this for the analyst to add to the findings? Default: yes, and draft now from what the findings say, with the gap noted to you."

When none holds, draft without asking.

## Executive summary

No executive summary is supplied; write it from `findings.md`, following these guidelines.

- **Length:** one page at most.
- **Answer first:** open with the answer in one or two sentences addressed to the decision in the **Audience** section.
- **Key findings:** three to five, one sentence each with its number, ordered by relevance to the decision. Use the finding headings in `findings.md` as the starting point.
- **Contrary evidence:** keep any contrary result that limits or qualifies the answer; never smooth it away to make the summary cleaner.
- **Implications and next steps:** only as `findings.md` supports them in its **Implications** section.
- **Caveats:** include the caveats relevant to the decision, and every caveat marked **Awaiting revalidation:** on any claim the summary includes, beside that claim.
- **Method:** only as much of **How we know** as the reader needs to trust the answer, usually one or two sentences.
- **Numbers:** keep numbers, rounding, units, and qualifiers exactly as `findings.md` gives them; never re-round, recompute, or combine them.
- **Nothing new:** add no claim, metric, comparison, or recommendation that `findings.md` does not make.
- **No internal names:** no file names, paths, or internal names of any kind.

A figure included in the summary keeps its full caption and alt text.

## Detailed report

Build the detailed report from `findings.md`, preserving every claim, number, qualification, and caveat. You may reorganize for readability, for example by merging short sections, turning a list of comparable values into a table, or moving **How we know** to an appendix, but every caveat stays beside the claim it qualifies. When the requested deliverable is one document, place the executive summary first and the detailed report after it.

## Figures

- Insert each PNG from `figures/` at 6.5 in width beside the text that cites it.
- The italic `*Figure N. ...*` paragraph immediately after each image in `findings.md` is that figure's caption. Make it a Word caption below the figure with Word's caption feature, so numbering stays correct when figures move. Keep the caption text, including every caveat, and never place it inside the image.
- Set each figure's alt text from its Markdown alt text.
- Turn off picture compression for the document, or choose high fidelity, so figures keep their resolution.

## Word

- Preserve the heading hierarchy of `findings.md` unless the requested deliverable reorganizes it under **Detailed report**.
- Convert Markdown tables into Word tables rather than pasting their source. Format them for readability, repeat header rows across pages, and give each an accessible caption.
- Apply the organization's approved theme, typography, page furniture, and accessibility conventions when available.

## Excel

- Create workbooks only from the datasets listed in the manifest.
- Preserve source values, column headers, and column meaning. Headers arrive as display names in the audience's terms; keep them as supplied. Add display formatting, filters, frozen headers, tables, and explanatory notes without changing analytical content.
- Carry units, population, reporting period, and material caveats from the dataset's description in `findings.md` into the workbook where readers will encounter the affected data.
- Do not add derived metrics or hidden transformations unless they are first produced and documented in the workbench package.

## Revision boundary

When a requested change affects the analysis, wording, findings, calculations, scope, or dataset contents, make that revision in the upstream workbench draft. Send the refreshed package forward and assemble the M365 outputs again. M365 edits are not synchronized back into the workbench.

The executive summary is written here, so a change to which findings it selects or how it phrases them within the guidelines above is made here. A change that needs a claim, number, qualification, or caveat `findings.md` does not give goes upstream.
