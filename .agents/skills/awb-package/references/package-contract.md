# Package contract

Repository paths are relative to the project root.

## Layout and formats

All revisions use `deliveries/<investigation>/<package>/draft/`. The numbered sibling directories `released/001`, `released/002`, … are frozen. Each draft contains:

```text
findings.md                  # audience-facing deck outline; sole slide-content source
methodology.md               # internal reference; kept out of the deck
m365-assembly.md
manifest.json
charts/                      # only when findings.md specifies charts: chart-N.csv per chart
datasets/                    # only when datasets were selected
```

Shared formats are in the root `package-format/` directory: `findings-template.md`, `methodology-template.md`, `m365-assembly.md`, and `manifest-template.md`. All investigations share them. Keep existing files. The project's copies are the copies that apply. `findings-template.md` holds the translation rule and slide rules. `manifest-template.md` holds the manifest fields.

`methodology.md` is the complete, authoritative analytical account, in internal vocabulary. `findings.md` comes from it and is written for the brief's **Audience**. `findings.md` states nothing that `methodology.md` does not support. It is the slide-by-slide outline of the deck and the only source of slide content.

When releases exist, findings adds **What changed since the last version**, compared with the latest release. It identifies the delivery date of that release from the manifest `released_at`.

The **Answer** slide in `findings.md` is the executive summary. M365 does not write an executive summary. In the Microsoft 365 Copilot app, the PowerPoint agent builds the deck from `findings.md`. It draws each chart natively from its file, as `m365-assembly.md` specifies. Datasets travel beside the deck. M365 consults methodology only for reasoning. Findings, methodology, chart files, and datasets stay authoritative upstream: substantive revisions go back through the draft, and deck edits stay in the deck.

## Structural consistency

Every rule applies to the complete draft:

- `findings.md` stands alone for its audience. Its context, answer, findings with evidence and contrary results, plain-language method, limitations, and caveats need no earlier release, no methodology, and no M365 edits. `findings: []` is only the mechanical check.
- `methodology.md` stands alone as the analytical account. Its scope, sources, method, settings, validation, findings, evidence, contrary results, limitations, and caveats need no earlier release and no investigation records. Include the methodological mistakes that changed understanding. Execution attempts that changed no understanding stay in code history.
- The narratives agree in claims, numbers, qualifications, and caveats. Every `###` finding heading in findings has a methodology section with identical heading text (`headings`).
- Commands write every manifest field, except the producing state of a result without evidence. In `revalidation_flags`, you fill `represented_in` and the user's `disposition`. A field that you record by hand follows `package-format/manifest-template.md`.
- The manifest `inventory` matches each draft file in byte size and SHA-256, except the row for the manifest itself, which has only the path (`verify`).
- `charts/` matches the chart specifications in `findings.md` (`charts`). Each chart file serializes a recorded result. The manifest's `charts` and the methodology name that result.
- `datasets/` and the manifest match the recorded audience-facing selection. This includes an explicit `none`. Headers use glossary display names. The methodology maps each header to its source column. Dataset and column caveats go under **Supporting datasets** in findings, and the values stay as recorded.

## Revalidation caveats

`check-draft` refuses drift in the rendered table and names `state render`. If there is no `findings.json`, any row is drift. If a project helper does not have `findings_drift`, it needs `awb-init` repair (`install_helpers.py --upgrade`). Flags still come from the rendered `state.md` rows.

The manifest's `revalidation_flags` is `none`, or one entry for each finding that the investigation's `state.md` currently flags: `{finding, reason, represented_in, disposition}`. `unmatched_flags` lists the flagged findings that `revalidation_flags` does not have. `finding` and `reason` are exactly as that row writes them. `represented_in` lists every place where the draft represents an affected conclusion. Each place is a short description, for example `findings: <slide headline>`, `methodology: <section>`, `chart 2`, or `dataset late-closures: <column>`. If the draft represents no affected conclusion, `represented_in` is `none`. `disposition` is one of `none`, `revalidate`, `omit`, or `release_with_caveat`. If `represented_in` lists places, the entry must have a `disposition`. If `represented_in` is `none`, the `disposition` is optional. Each represented flagged finding is listed as unresolved under **Limitations and open caveats** in findings.

Each represented conclusion carries a nearby caveat, unless the disposition omits it. The caveat is:

- beside claims in both narratives,
- in the **Caveat:** and **Alt text:** lines of a chart specification in findings, or
- in the dataset or column description under **Supporting datasets**.

Findings uses the **Awaiting revalidation:** prefix of the template, with a plain-language reason, on every slide where the conclusion appears.

A recorded disposition applies while its finding and reason match the current `state.md` row exactly. A new or changed reason opens it again. A draft holds `none` until the user chooses. For a release, every represented flag must have `omit` or `release_with_caveat`. `revalidate` pauses the release for analytical work that has a separate authorization.

## Commands

The verdicts of the commands decide every mechanical rule. Report their rows verbatim. Run each command from the project root. `python3 src/awb.py <command> --help` gives its arguments, output keys, and exit status. To diagnose the rows of a helper, read [helpers](helpers.md). An example is a name that `check-draft` reports but that is not internal.

- `export <investigation> <package>` writes the chart and dataset files, `charts`, `dataset_selection`, `export_checks`, and the producing and packaging state. If the manifest is absent, the command creates it. A call with only `--result` refreshes provenance and does not change the exported files. The command serializes only when every `--chart` and `--dataset` result passes `compare_evidence`. If not, it reports `exports_blocked`. It records a `--result` without that check. If any evidence is missing, it writes nothing.
- `check-draft <investigation> <package> [--verify-only]` checks the whole draft against these items:
  - Every internal name that the project defines.
  - The chart files.
  - The headings.
  - The inventory. The command rewrites the inventory, unless you use `--verify-only`, which writes nothing.
  - The current flags of `state.md`.

  `names_problems` means that the name set is incomplete. Repair the cause and run the command again.
