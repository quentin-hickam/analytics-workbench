### Added

- Parent and priority fields for ledger questions through the CLI and MCP tools, with missing-parent and cycle checks and priority-ordered tree rendering.
- Ledger-derived finding slide order, informational reporting of unlinked findings, and draft checks for slide order and the conditional Open questions slide.
- A headline approval checkpoint before full slides for new drafts or changed storylines.

### Changed

- Answered data questions derive an `answered (awaiting recheck)` display status whenever any answering finding is flagged or superseded; stored status remains unchanged. Status collection reports `awaiting_recheck` in place of `answered_by_unsettled`.
- The findings template includes every unanswered must question after Limitations and open caveats. Open questions is exempt from the five-bullet limit to preserve complete coverage.
