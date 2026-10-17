# Source register

Record source provenance, relevance, and fitness here. Add a source when it becomes a real candidate.

## Sources

| Source ID | System or provider | Contents and grain | Owner or contact | Acquisition method | Relevance and fitness | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |

Status is one of:

- `candidate`: identified as possibly relevant; no acquisition has completed.
- `acquired`: at least one acquisition has completed and the source has not been rejected.
- `rejected`: assessed as irrelevant or unfit; give the reason under Relevance and fitness and stop preparing it.

Begin Relevance and fitness with the assessment's basis: `from documentation` when documentation or a schema settled it, otherwise `from landed records`. In Notes, record each reference it relied on as a plain-text clause that opens the cell or follows `;`, beginning `reference:` followed directly by one of three forms:

- A link to the kept copy: `reference: [codebook](references/<source-id>/codebook.pdf)`.
- For material kept out of Git, its retained location in backticks and its SHA-256: ``reference: `/secure/<source-id>/manual.pdf`, sha256 <64-digit checksum>``.
- For documentation read but not kept, an access note giving its URL, the date it was read, and why it was not kept: `reference: read at https://example.org/dictionary.pdf on 2026-10-16, not kept: the server refused downloads (HTTP 403)`. Status reports it as a known limitation.

When a document's revision postdates the data, say so after its reference, such as `; dictionary revised 2024, after the 2019 data`. `awb-status` lists any other spelling as no reference, with the reason, and an entry such as `reference: not yet retained` counts as none; the `awb-init` skill's `references/landing.md` (**Source references**) gives the exact grammar it reads.

Note failed acquisition attempts in the source's Notes. Use stable source IDs in the catalog, quality record, and investigation records.

## Acquisitions

`land` and `retain` write these rows, one per completed acquisition directory under `data/raw/<source>/<acquisition-id>/` unless the project has its own layout. Fill Restrictions yourself, and update Retained copy once a manual copy is verified.

| Acquisition ID | Source ID | Acquired at | Source version, query, or request | Landed directory | Retained copy | Integrity or completeness check | Restrictions | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
