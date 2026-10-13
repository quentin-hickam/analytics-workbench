# Data catalog

Describe shared datasets, canonical views, and deliberate caches. Keep business-term definitions in `glossary.md` and source acquisition details in `sources.md`.

## Published datasets and views

| Name | Kind | Grain | Inputs | Definition or location | Preparation rules | Quality constraints | Availability or refresh notes |
| --- | --- | --- | --- | --- | --- | --- | --- |

For canonical views, identify the Git-managed definition that is loaded into each process-local analytical session. Name the publication that each view reads, for example `data/parquet/<dataset>/<publication-id>/`. The `publication.json` of that publication records its inputs, conversion commit, and file checksums. A change of a view to a newer publication is a deliberate preparation change, recorded here. For published files, give the validated Parquet location. Cleanliness comes from the quality record, not from the conversion.

Record expensive, rebuildable caches as Kind `cache`:

- Put the purpose under Preparation rules.
- Put the inputs and settings under Inputs.
- Put the location under Definition or location.
- Put the rebuild method and the freshness decision under Availability or refresh notes.
