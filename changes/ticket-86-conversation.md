### Changed

- An answered data question none of whose answering findings is promoted to supported, and none flagged or superseded, displays as `answered (provisional)` in `questions list`, `questions.md`, `state`, and the status collector, which counts it apart from answered and lists it under `questions.provisional`. The stored status stays `answered`; promoting a finding shows it answered. The turn footer counts it as provisional, and in preview-and-wait the headline checkpoint shows the figures behind each headline that chat has not shown.
- The project `AGENTS.md` **Conversation** section holds the rule to offer an untested explanation as a question, moved from **Analytical invariants**, and a new rule to name every share's base and say when it changes. IDs stay in the records: chat no longer sets an ID beside plain text. The headline checkpoint repeats the explanation rule.
- Report rules use plain words: a new review rule is reported as what later drafts will be checked for, a package's charts by what they show, and `awb-clean`'s recorded issues in plain words with their quality IDs kept in the files. `awb-clean` treats `duplicate-rows` as repeats to explain and proposes their treatment without asserting why they repeat.
- A commit is suggested at most once a session in the `awb-status` "Commit the current work" request, the package and release reports, and the `awb-init` repair report, as the guides already did.
- Scoping counts each decision as one choice: unrelated choices are never numbered under one item, and go to a second round.

### Fixed

- A packaging commit recorded as unknown because the repository has no commit yet is no longer a `provenance_gaps` entry, nor is one in a project without Git, so release reports stop naming a missing commit nobody could have made. Any other unknown packaging state is still a gap.
