### Added

- `foundation/display.toml` takes a `[scale]` table, such as `change_mt = { divide = 1000 }`, that divides a column's values for display. `export` writes the divided values and records each divisor as `scale` in the manifest's `charts` and `dataset_selection` entries, and `check-draft`'s `numbers` check traces a narrative number to that column's recorded values divided by it, so a figure written in another unit no longer needs a new saved column and a rerun.
- `foundation/display.toml` takes a `[confirmed]` list, `columns = [...]`, of shared column names whose `label_warnings` row then stops repeating on every export.
- `export` reports `value_warnings`, each `[values]` code that no cell of the saved tables it labels holds, such as `true` where pandas saved `True`, and `precision_warnings`, each percent column shown to fewer than two places whose fractions were saved at exactly four, a sign the query rounded them and the display rounds them again.

### Changed

- `check-draft`'s `numbers` rows carry a `problem` naming the rule that left the number untraced and pointing to `allowed_numbers`.
- The `numbers` check reads two numbers joined by one slash, such as `54.8/57.6`, as two numbers, each traced; skips 24-hour times such as `18:00`, a year directly after an English month name, full or in three letters (`December 2011 is`), and a year alone in parentheses (`(2025)`); and no longer traces a number to a recorded value lying exactly on the edge of its rounding, as 0.5245 does for `52.5%`.
- The `claims` check skips a causal phrase in a negated clause, under a closed grammar the helpers reference states, so "does not test what caused them" passes, and no longer reads the methodology note's `## Limitations` section, as it already skipped the deck's Limitations slide.
- The findings template says a chart's fields take no blank line between them and one after the last, and the `outline` check gives a row naming the chart for each bullet that opens with a chart field name other than **Caveat:** after that chart's fields ended, and its bullet-count row names the chart too.
- `awb-package` never tells the user a rewritten sentence is in their wording unless it is word for word theirs.

### Fixed

- The `charts` check compares a chart file's headers NFKC-normalized, as it reads the **Data:** line, so a `CO₂` header matches a `CO₂` role, and `deck-rules.md` tells builders to find each column the same way.
