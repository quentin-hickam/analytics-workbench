# Source register

Record source provenance, relevance, and fitness here. Add a source when it becomes a real candidate.

## Sources

| Source ID | System or provider | Contents and grain | Owner or contact | Acquisition method | Relevance and fitness | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |

Status is one of:

- `candidate`: identified as possibly relevant; no acquisition has completed.
- `acquired`: at least one acquisition has completed and the source has not been rejected.
- `rejected`: assessed as irrelevant or unfit; give the reason under Relevance and fitness and stop preparing it.

Begin Relevance and fitness with the assessment's basis: `from documentation` when documentation or a schema settled it, otherwise `from landed records`. In Notes, record each reference it relied on as a clause that opens the cell or follows `;`, `,`, `.` or `<br>`, and that begins `reference:` followed directly by one of two forms:

- A complete Markdown link to the copy, such as `reference: [codebook](references/<source-id>/codebook.pdf)`. Put a path that contains spaces in angle brackets: `[codebook](<references/hr/data dictionary.pdf>)`.
- For material kept out of Git, the retained location in backticks, a comma, and `sha256` with the full 64-digit checksum, such as ``reference: `/secure/<source-id>/manual.pdf`, sha256 <checksum>``. `SHA-256` and `sha256:` are also read.

`awb-status` reads these two forms and nothing else, ignoring letter case; any other entry, such as `reference: not yet retained`, counts as no reference.

Note failed acquisition attempts in the source's Notes. Use stable source IDs in the catalog, quality record, and investigation records.

## Acquisitions

`land` and `retain` write these rows, one per completed acquisition directory under `data/raw/<source>/<acquisition-id>/` unless the project has its own layout. Fill Restrictions yourself, and update Retained copy once a manual copy is verified.

| Acquisition ID | Source ID | Acquired at | Source version, query, or request | Landed directory | Retained copy | Integrity or completeness check | Restrictions | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
