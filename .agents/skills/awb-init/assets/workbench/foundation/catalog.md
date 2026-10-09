# Data catalog

Describe shared datasets, canonical views, and deliberate caches. Keep business-term definitions in `glossary.md` and source acquisition details in `sources.md`.

## Published datasets and views

| Name | Kind | Grain | Inputs | Definition or location | Preparation rules | Quality constraints | Availability or refresh notes |
| --- | --- | --- | --- | --- | --- | --- | --- |

For canonical views, identify the Git-managed definition loaded into each process-local analytical session. Name the publication each view reads, such as `data/parquet/<dataset>/<publication-id>/`, whose `publication.json` records its inputs, conversion commit, and file checksums; switching a view to a newer publication is a deliberate preparation change recorded here. For published files, give the validated Parquet location; cleanliness comes from the quality record, not conversion.

Record expensive, rebuildable caches as Kind `cache`: purpose under Preparation rules, inputs and settings under Inputs, location under Definition or location, and rebuild method and freshness decision under Availability or refresh notes.
