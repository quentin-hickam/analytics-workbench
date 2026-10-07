# Data catalog

Describe shared datasets, canonical views, and deliberate caches. Keep business-term definitions in `glossary.md` and source acquisition details in `sources.md`.

## Published datasets and views

| Name | Kind | Grain | Inputs | Definition or location | Preparation rules | Quality constraints | Availability or refresh notes |
| --- | --- | --- | --- | --- | --- | --- | --- |

For canonical views, identify the Git-managed definition loaded into each process-local analytical session. Name the publication each view reads, such as `data/parquet/<dataset>/<publication-id>/`, whose `publication.json` records its inputs, conversion commit, and file checksums; switching a view to a newer publication is a deliberate preparation change recorded here. For published files, identify the validated Parquet location without treating conversion alone as proof of cleanliness.

## Deliberate caches

| Name | Purpose | Inputs and settings | Location | Rebuild method | Freshness decision | Notes |
| --- | --- | --- | --- | --- | --- | --- |

Add a cache only when recomputation is expensive. Choose cache identity and refresh behavior from the concrete project need rather than assuming a universal strategy.
