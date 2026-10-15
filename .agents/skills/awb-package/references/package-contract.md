# Package contract

Repository paths are relative to the project root.

## Layout and formats

All revisions use `deliveries/<investigation>/<package>/draft/`. Numbered `released/001`, `released/002`, … siblings are frozen. Each draft contains:

```text
findings.md                  # audience-facing deck outline; sole slide-content source
methodology.md               # internal reference; kept out of the deck
deck-rules.md                # how any builder builds the deck from findings.md and charts/
assembly/m365.md             # Microsoft 365 Copilot specifics
manifest.json
charts/                      # only when findings.md specifies charts: chart-N.csv per chart
datasets/                    # only when datasets were selected
```

Shared formats live in root `package-format/`: `findings-template.md`, `methodology-template.md`, `deck-rules.md`, `assembly/m365.md`, and `manifest-template.md`. They are shared across investigations; preserve existing files. The project's copies govern: `findings-template.md` holds the translation rule and slide rules, and `manifest-template.md` the manifest fields.

`methodology.md` is the complete authoritative analytical account in internal vocabulary. `findings.md` derives from it for the brief's **Audience**, states nothing it does not support, and is the slide-by-slide outline of the deck and the only source of slide content.

When releases exist, findings adds **What changed since the last version** against the latest release, identifying its delivery date from manifest `released_at`.

The **Answer** slide in `findings.md` is the executive summary; the builder writes none. Any builder builds the deck from `findings.md` and draws each chart from its file under `deck-rules.md`, with its own steps in its file under `assembly/`; datasets travel beside the deck. Microsoft 365 Copilot's PowerPoint agent is the builder the package ships for, under `assembly/m365.md`. The builder consults methodology for reasoning only. Findings, methodology, chart files, and datasets stay authoritative upstream: substantive revisions return through the draft, and layout and polish made in the deck are not carried back to the workbench.

## Ledger storyline

Read the complete question tree: each question has an existing `parent` ID or an empty root parent, and `priority` is `must`, `should`, or `could` (default `should`). Walk roots and children depth-first, sorting siblings by priority in that order, then by question ID. A finding slide's matching methodology section identifies its represented results through result IDs or evidence links; each result's recorded settings `answers` identifies the ledger questions it answers. Select the highest-priority question the slide answers, breaking a tie by its position in that depth-first walk. Order finding slides by that selected question's priority, then its walk position. Slides tied on both retain their order; slides answering no ledger question go last and are named in the report's informational `unlinked_findings` list. `storyline` rows report each finding slide out of place: the slides outside the longest run already in order, so moving one slide reports that slide alone.

**Open questions** follows **Limitations and open caveats**, before **What changed since the last version** when that slide exists. Include it if and only if unanswered `must` questions exist: open or parked questions, plus answered data questions whose answering findings include any flagged (`revalidation-needed`) or superseded finding. The latter display as `answered (awaiting recheck)` while their stored status remains `answered`. Declined or superseded questions are set aside and excluded. Give each required question exactly once as a top-level bullet, using its exact rendered ledger text; inline Markdown accepted by the outline reader is allowed. Keep IDs and owner commentary out of those bullets, and use no nested bullets. The slide is exempt from the five-bullet limit so every required question fits; report the count when it exceeds five. `open_questions` rows report presence, placement, and membership violations. This is exact text comparison, not a paraphrase or audience-language classifier; record audience-ready question text in the ledger before packaging.

Before writing a new draft's full slides, present the title slide and every slide headline in storyline order and wait for the user's approval or reorder. Resolve a reorder through the ledger fields so the resulting slide order passes the same checks. A revision retaining the storyline skips this checkpoint; a changed storyline returns to it.

## Structural consistency

Every rule holds for the complete draft:

- `findings.md` follows the slide rules in `package-format/findings-template.md` (`outline`): a title slide, one headline of at most 15 words, at most five bullets (except **Open questions**), at most one chart, and a closing **Notes:** paragraph per slide, and nothing outside a slide. Its finding order and **Open questions** content follow **Ledger storyline** (`storyline`, `open_questions`).
- `findings.md` stands alone for its audience: context, answer, findings with evidence and contrary results, plain-language method, limitations, and caveats need no earlier release, methodology, or edits in the deck. `findings: []` is the mechanical check only.
- `methodology.md` stands alone as the analytical account: scope, sources, method, settings, validation, findings, evidence, contrary results, limitations, and caveats need no earlier release or investigation records. Include methodological mistakes that changed understanding; execution attempts that changed no understanding stay in code history.
- The narratives agree in claims, numbers, qualifications, and caveats. Every number in either traces to a represented result or is listed in the manifest's `allowed_numbers` with its reason (`numbers`). That check proves each number is recorded somewhere, not that the two narratives agree, so the [draft review](review.md) confirms that every claim in `findings.md`, with its numbers, traces to the matching claim in `methodology.md`. Every `###` finding heading in findings has exactly one methodology section with identical heading text, and no two finding slides share a heading (`headings`); methodology repeats verbatim the question each represented result answers (`questions`). Both files keep to the Markdown subset the checks read as it renders, so no form hides text from them or moves it between slides (`markdown`; the subset is in [helpers](helpers.md)).
- No slide in findings is worded more strongly than its claim strength (`claims`), read from the rendered `state.md` Claim cells of the manifest's `results`. A checked slide is read whole: its heading (a finding slide's headline), bullets, **Caveat:** lines, chart specification, and notes. A `###` finding slide takes the weakest claim among the results its methodology section cites by ID or evidence link outside comments, or among all represented results when it cites none; the title, **Answer**, **Implications**, and any other slide stating conclusions take the strongest. Below `causal`, wording such as drives, causes, because of, due to, leads to, or impact of is refused: reword it, since only a finding recorded `causal` with its design basis supports it. A verb of change with an agent as its subject ("the carrier raised late orders", "discounts cut them") is not on the list, so the [draft review](review.md) catches it. **How we know**, **Limitations and open caveats**, **What changed since the last version**, and **Supporting datasets** are not checked. Each methodology finding section has exactly one `**Claim strength:**` line, opening a top-level paragraph at the start of a line (helpers.md states the reading), naming its slide's claim as a `state.md` Claim cell does; a causal one is the Claim cell, design basis included, that every result the section cites records, so results of different designs need separate findings. The reference therefore states what the record holds.
- Commands write every manifest field except `allowed_numbers` and the `results` entry and producing state of a result without evidence; in `revalidation_flags` you fill `represented_in` and the user's `disposition`. A field recorded by hand follows `package-format/manifest-template.md`.
- The manifest `inventory` matches every draft file's byte size and SHA-256, except its own path-only row (`verify`).
- `charts/` matches the chart specifications in `findings.md` (`charts`): numbered in order, each with its file, a form from `deck-rules.md`, and a **Data:** line naming that form's roles by columns the file holds and naming every column it holds. Each chart file serializes a recorded result, and the manifest's `charts` and the methodology name that result.
- `datasets/` and the manifest match the recorded audience-facing selection, including explicit `none`. Headers use glossary display names; methodology maps each to its source column. Dataset and column caveats go under findings' **Supporting datasets**, leaving values as recorded.

## Revalidation caveats

`check-draft` refuses drift in the rendered table and names `state render`; with no `findings.json` any row is drift; a project helper without `findings_drift` needs `awb-init` repair (`install_helpers.py --upgrade`). Flags still come from the rendered `state.md` rows.

The manifest's `revalidation_flags` is `none` or one entry per finding the investigation's `state.md` currently flags (`unmatched_flags` lists the ones it lacks): `{finding, reason, represented_in, disposition}`. `finding` and `reason` are exactly as that row writes them. `represented_in` lists every place the draft represents an affected conclusion, each a short description such as `findings: <slide headline>`, `methodology: <section>`, `chart 2`, or `dataset late-closures: <column>`; or it is `none` when the draft represents none. `disposition` is one of `none`, `revalidate`, `omit`, or `release_with_caveat`: required when `represented_in` lists places, optional when it is `none`. Each represented flagged finding is listed as unresolved under findings' **Limitations and open caveats**.

Each represented conclusion carries a nearby caveat unless the disposition omits the conclusion: beside claims in both narratives, in a chart specification's **Caveat:** and **Alt text:** lines in findings, or in the dataset or column description under **Supporting datasets**. Findings uses the template's **Awaiting revalidation:** prefix with a plain-language reason, on every slide where the conclusion appears.

A recorded disposition applies while its finding and reason match the current `state.md` row exactly; a new or changed reason reopens it. A draft holds `none` until the user chooses. Release requires `omit` or `release_with_caveat` for every represented flag; `revalidate` pauses the release for separately authorized analytical work.

## Commands

The commands' verdicts settle every mechanical rule; summarize their outcomes in chat. Run each from the project root; `python3 src/awb.py <command> --help` gives its arguments, output keys, and exit status. To diagnose a helper's rows, such as a name `check-draft` reports that is not internal, read [helpers](helpers.md).

- `export <investigation> <package>` writes the chart and dataset files, `charts`, `dataset_selection`, `export_checks`, and the producing and packaging state, creating the manifest when absent; a call with only `--result` refreshes provenance and leaves exported files untouched. It serializes only when every `--chart` and `--dataset` result passes `compare_evidence`, otherwise reporting `exports_blocked`; a `--result` is recorded without that check. It writes nothing when any evidence is missing.
- `review-rules check <investigation> <package>` lists every rule in `foundation/review-rules.md` with the narrative lines its pattern matches, writing nothing; `review-rules add` appends the next numbered rule. [Draft review](review.md) says who runs each.
- `check-draft <investigation> <package> [--verify-only]` checks the whole draft against every internal name the project defines, the slide rules, the ledger-derived finding order and **Open questions** slide, the chart specifications and files, the headings, the Markdown subset, causal wording against claim strength, each manifest `results` question in methodology, every number in both narratives against the represented results, the inventory (rewritten unless `--verify-only`, which writes nothing), and `state.md`'s current flags. `unlinked_findings` is informational; `storyline` and `open_questions` violations fail the check. `names_problems` means that name set is incomplete, and `numbers_problems` the recorded values: repair the cause and rerun.
