### Changed

- `check-draft`'s `numbers` check skips a `methodology.md` **Claim strength:** line that the `claims` check accepts. That line repeats its results' `state.md` Claim cell, design basis included, so a basis such as `randomized holdout of 2024 Q3, 50/50 split` no longer needs `allowed_numbers` entries. A line the `claims` check refuses keeps its numbers, and so does a line continuing its paragraph.

### Fixed

- `check-draft`'s `questions` check reads `methodology.md` as it renders, as every other draft check but `numbers` does. A question only inside a comment or fenced code no longer passes; a question wrapped across lines, in a code span, or written with emphasis or a link still matches, and the manifest's question is rendered the same way. It must fall within one paragraph or heading.
- The `check-draft` help text, the comment above the helper's shared Markdown reading, `references/helpers.md`, and the design record now agree that every draft check but `numbers` reads both narratives as they render. `helpers.md` gains a `questions` row.
