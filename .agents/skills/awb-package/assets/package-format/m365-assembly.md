# M365 assembly instructions

The Markdown narrative and packaged datasets are the authoritative source. Use Microsoft 365 to improve presentation while preserving every substantive claim, value, qualification, and caveat.

## Files in this package

The draft replaces this list with every file it includes, one path per line relative to the package directory. Write **None** under figures or datasets when the package has none.

- `executive-summary.md`
- `journal.md`
- `m365-assembly.md`
- `manifest.<format>`
- Figures: `figures/<figure>.png`
- Datasets: `datasets/<dataset>.<format>`

## Word

- Produce a concise executive-summary document from `executive-summary.md` and a detailed report from `journal.md`, or combine them when the requested deliverable calls for one document.
- Preserve the heading hierarchy and keep caveats beside the claims they qualify.
- Format tables for readability, repeat header rows across pages, and use accessible captions for figures or tables.
- Insert each PNG from `figures/` at 6.5 in width beside the text that cites it, with its caption and alt text. Turn off picture compression for the document, or choose high fidelity, so figures keep their resolution.
- Convert Markdown tables into Word tables rather than pasting their source.
- Apply the organization's approved theme, typography, page furniture, and accessibility conventions when available.

## Excel

- Create workbooks only from the datasets listed in the manifest.
- Preserve source values and column meaning. Add display formatting, filters, frozen headers, tables, and explanatory notes without changing analytical content.
- Carry units, population, reporting period, and material caveats into the workbook where readers will encounter the affected data.
- Do not add derived metrics or hidden transformations unless they are first produced and documented in the workbench package.

## Revision boundary

When a requested change affects the analysis, wording, findings, calculations, scope, or dataset contents, make that revision in the upstream workbench draft. Send the refreshed package forward and assemble the M365 outputs again. M365 edits are not synchronized back into the workbench.
