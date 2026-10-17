### Added

- `awb-clean`'s scan takes `--lineage COLS`, columns such as `sheet` and `sheet_row` that a conversion adds to say where each row came from, and leaves them out of the `duplicate-rows` match, so a copy of the same rows in two sheets or files is counted; each example lists its lineage columns' values first. The default is every lineage column `foundation/datasets.toml` declares under `[datasets.<name>]` as `lineage = [...]`, which no check reads, and a rescan keeps the baseline's.
- `record_cleaning.py` takes `"amend": {"observation", "reason"}` on a recorded row's decision, keyed by its quality ID or its scan issue: the observation becomes the new text with the date and reason, and the replaced text, scan marker included, stays after `was:`. The same amendment again changes nothing.
- A third source reference form, an access note for documentation read but not kept: `reference: read at <URL> on <YYYY-MM-DD>, not kept: <reason>`. `awb-status` lists such a source under `sources.documentation_access_notes`, a known limitation, not under `documentation_without_reference`.
- `awb-status` names under `upstream.not_checkable`, once each and without probing, the sources whose latest landed files record an HTTP URL without an ETag or Last-Modified, and `retain` prints `upstream_check` once, with the acquisition's new row, for such files.

### Changed

- `awb-clean` settles who removes repeated rows: rows shared by sheets, files, or extracts that the user or the source's documentation says are re-extracts of the same rows are a representation fix the agent removes and records; rows shared by other parts, whose name can be data such as one sheet per store, are the user's decision, asked in plain words. Rows repeated within one part (sheet, file, or partition) are the agent's to remove only under a recorded grain none of whose columns the scan left out as lineage, so the repeated rows share one grain key; a grain such as `sheet,sheet_row` no longer qualifies, and any other repeat within one part is the user's decision. A new step counts each pair of parts' shared rows on the non-lineage columns, and the landing reference adds the same check, and the lineage declaration, for multi-sheet workbooks and multi-file extracts.
- `eda_scan.py` accepts an integer year column as `--date-column`: `--start` and `--end` compare as integers, and coverage, null shifts, the measure's trend, and contrary groups run by year. A date bound for such a column, or integers outside 1 to 9999, exits 2 naming the fix; such a setting prints as not applied.
- The source register template states the three reference forms with one example each and allows a note that a document's revision postdates the data; the grammar `awb-status` reads moved to `awb-init`'s `references/landing.md` (**Source references**). Each `documentation_without_reference` entry is now `{source, reason}`, saying why no reference was read.
- `awb-clean`'s record step asks for a `findings` string only when the pass changed a view or publication.
- `land` and `retain` report `source_status_changed` when they set a Sources row's Status from `candidate` to `acquired`.
- The `datasets.toml` template shows the `[datasets.<name>.checks.types]` subtable form for a long table and says an inline table stays on one line.

### Fixed

- A line break or comment inside an inline table in `foundation/datasets.toml` is refused with the subtable to write instead, such as `[datasets.trips.checks.types]`, ahead of the parser's own message.
- A refused `publish` prints `next_step`, saying to remove the partial folder it names before publishing again, and a retry while that folder exists is refused saying the same; the data guide's publish section repeats it.
