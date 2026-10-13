# Shared glossary

Define shared business and analytical terms that are used across investigations. Test each definition against a concrete example, available source fields, and the logic that uses it.

| Term | Definition | Concrete example or boundary case | Source-data or analytical implications |
| --- | --- | --- | --- |

Display names for exported columns and coded values are in `foundation/display.toml`, under `[columns]`, `[values.<column>]`, and `[round]`, so that `export` can apply them. Take each name from a term here, with its unit. Evidence does not read that file. For this reason, a new name for a label never marks a result stale.

Population selections, reporting periods, and similar settings belong in investigation records, not here. Record a deliberate investigation-specific departure in the `brief.md` of that investigation. Record only the departure and the reason for it.
