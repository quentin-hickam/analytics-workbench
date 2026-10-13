# Source register

Record the provenance, relevance, and fitness of each source here. Add a source when it becomes a real candidate.

## Sources

| Source ID | System or provider | Contents and grain | Owner or contact | Acquisition method | Relevance and fitness | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |

Status is one of:

- `candidate`: The source was identified as possibly relevant. No acquisition of it is complete.
- `acquired`: At least one acquisition of the source is complete, and the source is not rejected.
- `rejected`: The source was assessed as irrelevant or unfit. Give the reason under Relevance and fitness. Also stop the preparation of the source.

Record each failed acquisition attempt in the Notes of the source. Use stable source IDs in the catalog, the quality record, and the investigation records.

## Acquisitions

`land` and `retain` write these rows. They write one row for each completed acquisition directory. The directory is under `data/raw/<source>/<acquisition-id>/`, unless the project has its own layout. Fill in Restrictions yourself. When a manual copy is verified, update Retained copy.

| Acquisition ID | Source ID | Acquired at | Source version, query, or request | Landed directory | Retained copy | Integrity or completeness check | Restrictions | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
