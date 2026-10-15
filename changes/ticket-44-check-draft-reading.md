### Changed

- `check-draft`'s `numbers` check skips a `methodology.md` **Claim strength:** line that the `claims` check accepts. That line repeats its results' `state.md` Claim cell, design basis included, so a basis such as `randomized holdout of 2024 Q3, 50/50 split` no longer needs `allowed_numbers` entries. A line the `claims` check refuses keeps its numbers, and so does a line continuing its paragraph.

### Fixed

- `check-draft`'s `questions` check reads `methodology.md` as it renders, as every other draft check but `numbers` does. A question only inside a comment or fenced code no longer passes; a question wrapped across lines, in a code span, or written with emphasis or a link still matches. The manifest's question matches as written or rendered the same way, so a code span showing it exactly counts even when it holds a markup character such as `[` or `~`. It must fall within one paragraph or heading, and the row now says so.
- `check-draft`'s `numbers` rows give the correct line after a comment holding a line break other than a newline (U+2028, a form feed, or NEL); the line used to be one lower than the real one.
- The `check-draft` help text, the comment above the helper's shared Markdown reading, `references/helpers.md`, and the design record now agree that every draft check but `numbers` reads both narratives as they render. `helpers.md` gains a `questions` row.
