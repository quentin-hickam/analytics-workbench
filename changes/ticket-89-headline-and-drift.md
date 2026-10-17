### Added

- `check-draft` reports `helper_drift`: each helper under `src/` and each package-format file whose SHA-256 differs from what `.awb-receipt.json` records, as changed, missing, or unreadable, with an unreadable receipt as a row of its own. The rows do not fail `check-draft`, but `release` refuses, creating nothing, until the manifest's `helper_drift_confirmed` lists each file at its current SHA-256 with the user's reason, so a later edit needs a new confirmation. `awb-release` shows the rows in plain words and records the user's confirmation. `helpers.md` says a helper or package format changes only after the user says yes.

### Changed

- A headline over 15 words is now a `warning` outline row carrying the headline's text, and every other outline row an `error`, each row naming its `severity`. The user can keep a longer headline: the manifest's `accepted_long_headlines` lists its exact text with their reason, and `check-draft` and `release` then pass it, while a reworded headline needs a new entry. The headline checkpoint states the 15-word limit and asks before trimming a headline the user wrote or approved.
