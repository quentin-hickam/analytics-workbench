### Added

- `check-draft` reports an informational `note_length` row when `methodology-note.md` runs more than 10% over the length the investigation's brief records on a `Methods note length: about <n> words` line, and when such a line is written in another form or a second length is recorded. The brief template's **Audience** section offers that line and a precision for numbers.
- `review-rules add --package <investigation>/<package>` keeps a rule for one package: it writes a `- Package:` field, and `review-rules check` lists the rule for that package alone. A rule kept for another package is left out of a review's record, so adding or changing it leaves that review current.

### Changed

- `review-rules add` refuses without `--confirmed`, which the agent passes only after the user says yes to keeping a correction as a standing rule. `awb-package` asks first, saying in plain words what later drafts will be checked for. `add` warns, still adding the rule, when the rule or its fix names a number a draft's narratives state.
- The draft review reads the investigation's brief, and the review's record includes it. It checks that every part of the brief's question and of each represented result's question is in a slide's headline, bullets, or chart, not only in its notes, and that a claim about how a source builds a series rests on the source's documentation or a recorded check. A closed readability item reports a glossary term used without its definition, a number more precise than a precision the brief's **Audience** states, and record words, record IDs, or imperative wording in audience text.
- A "checked" sentence in `methodology.md` may cite a result ID, an evidence path, or a foundation quality ID with its scan. A tolerance is stated only where one was set before the data was seen, and only in `methodology.md` and speaker notes; an exact check says "exactly" or "every row". The findings and methodology note templates drop "within 0.5%", and `state finding`'s warning no longer asks for a tolerance.
- When two review rules conflict on a line, the `error` rule wins over a `warning` one, and a conflict between two rules of one severity goes to the user.
