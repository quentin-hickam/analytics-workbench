### Added

- `awb.py review-receipt record` keeps a draft review's report, the problems the user accepted with their reasons, and a copy of what the review read (the narratives, `foundation/review-rules.md`, and the `revalidation_flags` fields that make a review stale) in the package's `review/` folder, beside `draft/`. `review-receipt show` writes nothing and reports that record as `none`, `current`, `stale`, or `failed`, with the inputs that changed and a diff from the reviewed copy. Over MCP, `show` goes through `read` and `record` through `package`, which now takes `stdin`.

### Changed

- The package review converges. The first review of a draft is full and every later one is scoped against the receipt, and a scoped review that passes completes a request or a release. The user may accept a narrative problem with a reason, as they could a warning. A problem raised on a line unchanged since the prior review is marked and goes to the user, and after a second review in one request that still reports problems the agent stops and asks instead of reviewing again. In Claude Code the reviewer uses the awb MCP `read` tool when the session has it.
- `release` refuses, creating nothing, unless the review receipt is `current`, and records the review's kind, time, and accepted problems under `review` in the released manifest. `awb-release` reviews only when the receipt is not current, scoped against it, and shows the user the changed slides of any repair before releasing. `check-draft` reports the receipt's status in an informational `review` row.
