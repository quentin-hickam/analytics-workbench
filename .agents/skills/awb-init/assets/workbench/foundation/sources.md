# Source register

Record source provenance, relevance, and fitness here. Add a source when it becomes a real candidate.

## Sources

| Source ID | System or provider | Contents and grain | Owner or contact | Acquisition method | Relevance and fitness | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |

Status is one of:

- `candidate`: identified as possibly relevant; no acquisition has completed.
- `acquired`: at least one acquisition has completed and the source has not been rejected.
- `rejected`: assessed as irrelevant or unfit; give the reason under Relevance and fitness and stop preparing it.

Begin Relevance and fitness with the assessment's basis: `from documentation` when documentation or a schema settled it, otherwise `from landed records`. In Notes, record each reference it relied on as a clause in plain text, not inside code, HTML, emphasis, strikethrough, a link or brackets, that opens the cell or follows `;`, `,`, `.` or `<br>`, and that begins `reference:` followed directly by one of two forms:

- A link to the copy, `[text](destination)`, such as `reference: [codebook](references/<source-id>/codebook.pdf)`. The text is not empty and has no `[`, `]`, `\`, `<` or backtick. The destination is either in angle brackets with no `<`, `>` or `\` inside, which allows spaces, such as `[codebook](<references/hr/data dictionary.pdf>)`, or bare, with no spaces, `<` or `\`, and with its parentheses balanced.
- For material kept out of Git, the retained location in single backticks, a comma, and `sha256` with the full 64-digit checksum and no letter, digit, `_`, `\` or `&` directly after it, such as ``reference: `/secure/<source-id>/manual.pdf`, sha256 <checksum>``. `SHA-256` and `sha256:` are also read.

`awb-status` reads exactly these two forms, ignoring letter case, and lists every other spelling as no reference, including Markdown that renders as a link, such as a link with a title or with brackets in its text. It also stops reading a cell at a link with a title or with a destination neither form allows, at any raw HTML other than `<br>`, at an autolink containing a backtick, bracket or `<`, and at a `*`, `_` or `~` that opens emphasis or strikethrough when a backtick, bracket or `<` comes before the cell's last `*`, `_` or `~` of that kind that could close it, so put reference clauses before them. To fix a listed entry, rewrite it in one of the forms: drop brackets and backslashes from the link text, write paths with `/`, and put a path with spaces or unbalanced parentheses in angle brackets. An entry such as `reference: not yet retained` counts as no reference.

Note failed acquisition attempts in the source's Notes. Use stable source IDs in the catalog, quality record, and investigation records.

## Acquisitions

`land` and `retain` write these rows, one per completed acquisition directory under `data/raw/<source>/<acquisition-id>/` unless the project has its own layout. Fill Restrictions yourself, and update Retained copy once a manual copy is verified.

| Acquisition ID | Source ID | Acquired at | Source version, query, or request | Landed directory | Retained copy | Integrity or completeness check | Restrictions | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
