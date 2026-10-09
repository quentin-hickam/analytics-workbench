# Package helpers

`awb-init`'s `scripts/install_helpers.py` installs `src/packaging/findings.py`, `charts.py`, and `manifest.py` and restores a missing one. Call the project's copy, customized or not; open its source only to adapt or debug it. Each section below serves one branch.

## Hand export

A project with an established non-CSV export format writes its files by hand under the same rules as `export`: each file holds exactly the plotted or selected values of a saved result, with display-name headers carrying units, interval bounds as their own columns, values at the slide's rounding, and coded values mapped to display names.

- Charts in CSV: `write_charts(charts_dir, charts) -> list[Path]` (needs pandas) takes one DataFrame per chart, in the order the **Chart N.** specifications appear, writes `chart-1.csv`, `chart-2.csv`, …, and removes chart files a previous revision left beyond the new count. It raises, writing nothing, for an empty list, an empty frame, a blank or repeated header, or a header that looks like an internal name (an underscore or a dot between letters).
- Then run `python3 src/awb.py draft-provenance <investigation> <package> <result-id>... --export-checks` naming every exported result: it records `export_checks` only when every comparison passes. Fill `charts` and `dataset_selection` in the manifest yourself.

## Non-JSON manifest

`check-draft` runs the findings and chart checks on any draft but automates the inventory only for JSON. For another format:

- `inventory(package_dir, *, manifest_name) -> list[dict]` returns sorted relative paths with `bytes` and `sha256`, plus a path-only row for the manifest. Serialize the rows in order under `path`, `bytes`, and `sha256` with the project's established serializer, once every other draft file is final.
- `verify(package_dir, inventory, *, manifest_name) -> list[dict]` compares the files with the recorded rows; manifest content is excluded, its presence checked. Empty means the inventory holds.
- Fill the producing and packaging state, `charts`, and `dataset_selection` by hand under `package-format/manifest-template.md`.

## Diagnosing a helper's rows

- `findings` rows (`check(path, *, names=())`): `line`, `kind` (`code`, `path`, `file`, `identifier`, `sha`, or `name`), and `text`. HTML comments and Markdown link targets are skipped.
- The names set `check-draft` passes holds the investigation and package names; the view and table names created or read in `foundation/views/*.sql` and in the views the investigation's evidence cites, without CTE names or table functions; the settings keys of `settings.toml` and of the settings files and resolved settings its evidence records, as top-level keys and the dotted path of every nested key (a nested key's bare name is usually a plain word, so it is left out); and the result IDs of `investigations/<investigation>/evidence/*.json` and the evidence links in its brief, state, and history. The full set is under `names_set` in the `check-draft` record file. A `name` row for an ordinary audience word means a record defines that word as a name: rename it in the record, or rephrase the slide.
- `charts` rows (`check_charts(findings_path, charts_dir)`): `chart` and `problem`, one per specification numbered out of order, specification without a file, file without a specification, non-chart file in `charts/`, or file without data rows.
- `verify` and `compare_trees` rows: `path`, `kind` (`missing`, `extra`, `size`, `checksum`), `expected`, and `actual`. `compare_trees(local_dir, copy_dir)` compares every file, manifest included, with the local release as expected. Invalid inventories, missing or unreadable directories, and symlinks raise errors, which the commands report under `errors` or `problem`.
