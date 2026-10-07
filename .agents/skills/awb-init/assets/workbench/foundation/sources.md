# Source register

Record source provenance, relevance, and fitness here. Add a source when it becomes a real candidate; if it is rejected, record why and stop preparing it.

## Sources

| Source ID | System or provider | Contents and grain | Owner or contact | Acquisition method | Relevance and fitness | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |

Status is one of:

- `candidate`: identified as possibly relevant; no acquisition has completed.
- `acquired`: at least one acquisition has completed and the source has not been rejected.
- `rejected`: assessed as irrelevant or unfit; give the reason under Relevance and fitness and stop preparing it.

Note failed acquisition attempts in the source's Notes. Use stable source IDs in the catalog, quality record, and investigation records.

## Acquisitions

List completed landings only, one row per acquisition directory, `data/raw/<source>/<acquisition-id>/` unless the project has its own layout. A landing is complete only when every acquired artifact and its provenance file are durable and the directory has dropped its `.partial` suffix; a failed or partial attempt gets no row. A file the user hands over is an acquisition too. `data/raw/` is excluded from Git, so record where each acquisition directory is retained outside this checkout, or `this checkout only`.

| Acquisition ID | Source ID | Acquired at | Source version, query, or request | Landed directory | Retained copy | Integrity or completeness check | Restrictions | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
