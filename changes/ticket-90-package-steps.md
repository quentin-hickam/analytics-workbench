### Added

- `questions edit Q-NNN --show` puts an unanswered question on the **Open questions** slide whatever its priority, and `--no-show` takes it off. The flag is stored in `questions.json`, shown as `shown` in `questions list` and in a Show column of `questions.md`, and leaves priority to mean what the decision needs.
- `check-draft` prints `ledger_order`, every finding slide in the order the ledger gives, with its slug, heading, primary result, and question, whatever `presentation_order` holds.
- `release`'s `storage` row gives the full destination as `path`, absolute for a path location.

### Changed

- A finding slide ranks by its primary result alone: the first result its methodology section cites. A result it cites later supports the slide without moving it, and a result ID cites only as a whole code span, such as `` `monthly` ``, or in an evidence path, so the plain word "monthly" no longer cites result `monthly`.
- `presentation_order` lists slide slugs instead of headings. `export` records each finding slide's slug in the manifest's `slide_slugs`, taken from its heading the first time, and a slide keeps its slug when its heading is reworded while its primary result stays, so the order needs no hand edit.
- `export` creates the draft folder when it is missing. `check-draft` and `review-receipt record` refuse a missing draft by naming that step, not the skill already running. `awb-package` writes a first pass of the narratives, exports, then fills in display names and pastes `methodology_lines`, in that order.
- Preview-and-wait headlines go in the draft's `.preview/headlines.md`. The inventory, and so `check-draft` and `release`, skip that folder, and `release` never copies it. `awb-status` reports a draft holding only the preview as "headline preview awaiting approval" rather than a missing manifest.
- `START-HERE.md` lists `methodology.md` and `deck-rules.md` once, as files for the builder only, and its part 3 is titled "Internal: keep these; do not send them to the audience".
- `awb-package`'s instructions are shorter: step 4 is numbered sub-steps, the headline checkpoint's modes are stated only in the skill, which the package contract points to, and the procedure for results whose evidence is missing moved to the helpers reference. A test holds the skill to a word budget.
- `awb-package`'s report repeats the package name, `awb-scope`'s names the investigation folder it created, and `awb-release`'s gives the storage copy's full path. The findings template says a finding slide may present several recorded results.
