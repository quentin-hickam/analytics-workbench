# Source register

Record source provenance, relevance, and fitness here. Add a source when it becomes a real candidate.

## Sources

| Source ID | System or provider | Contents and grain | Owner or contact | Acquisition method | Relevance and fitness | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |

Status is one of:

- `candidate`: identified as possibly relevant; no acquisition has completed.
- `acquired`: at least one acquisition has completed and the source has not been rejected.
- `rejected`: assessed as irrelevant or unfit; give the reason under Relevance and fitness and stop preparing it.

Note failed acquisition attempts in the source's Notes. Use stable source IDs in the catalog, quality record, and investigation records.

## Acquisitions

`land` and `retain` write these rows, one per completed acquisition directory under `data/raw/<source>/<acquisition-id>/` unless the project has its own layout. Fill Restrictions yourself, and update Retained copy once a manual copy is verified.

| Acquisition ID | Source ID | Acquired at | Source version, query, or request | Landed directory | Retained copy | Integrity or completeness check | Restrictions | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
