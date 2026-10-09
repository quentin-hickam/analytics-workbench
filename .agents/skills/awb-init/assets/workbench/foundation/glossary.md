# Shared glossary

Define shared business and analytical terms used across investigations. Test each definition against a concrete example, available source fields, and the logic that uses it.

| Term | Definition | Concrete example or boundary case | Source-data or analytical implications |
| --- | --- | --- | --- |

Display names for exported columns and coded values live in `foundation/display.toml`, under `[columns]`, `[values.<column>]`, and `[round]`, so `export` can apply them; take each name from a term here, with its unit. Evidence does not read that file, so renaming a label never marks a result stale.

Population selections, reporting periods, and similar settings belong in investigation records rather than here. Record a deliberate investigation-specific departure in that investigation's `brief.md` and explain why; do not duplicate the full glossary.
