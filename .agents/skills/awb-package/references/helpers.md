# Diagnosing a helper's rows

The `scripts/install_helpers.py` script of `awb-init` installs `src/packaging/draft.py`. If this file is missing, the script restores it. Call the project's copy, also if it is customized. Open its source only to adapt or debug it.

- `findings` rows (`check_findings(path, *, names=(), roots=())`): `line`, `kind` (`code`, `path`, `file`, `identifier`, `sha`, or `name`), and `text`. HTML comments and Markdown link targets are skipped.
- The `text` of a `name` row is a name from these sources:
  - The investigation and package names.
  - The view and table names that are created or read in `foundation/views/*.sql` and in the views that the investigation's evidence cites. CTE names and table functions are not included.
  - The settings keys of `settings.toml` and of the settings files and resolved settings that its evidence records. These are the top-level keys and the dotted path of every nested key. The bare name of a nested key is usually a plain word, so it is left out.
  - The result IDs of `investigations/<investigation>/evidence/*.json`, and the evidence links in its brief, state, and history.

  A name of letters only is never in the set, because it collides with ordinary words. Instead, `check-draft` passes those plain-word names as `roots`. A slash token with any recorded name as a segment (for example, `orders/region`) is a `path` row. But a slash between two other plain words (for example, yes/no) is prose.
- `charts` rows (`check_charts(findings_path, charts_dir)`): `chart` and `problem`. There is one row for each of these:
  - A specification numbered out of order.
  - A specification without a file.
  - A file without a specification.
  - A non-chart file in `charts/`.
  - A file without data rows.
- `verify` and `compare_trees` rows: `path`, `kind` (`missing`, `extra`, `size`, `checksum`), `expected`, and `actual`. `compare_trees(local_dir, copy_dir)` compares every file (the manifest also) and uses the local release as the expected value. Invalid inventories, missing or unreadable directories, and symlinks raise errors. The commands report these errors under `errors` or `problem`.
