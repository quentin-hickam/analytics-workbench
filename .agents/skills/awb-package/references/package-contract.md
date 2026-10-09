# Package contract

Repository paths are relative to the project root.

## Layout and formats

All revisions use `deliveries/<investigation>/<package>/draft/`. Numbered `released/001`, `released/002`, … siblings are frozen. The `audit/` sibling holds the complete records the package commands write, outside every draft and release. Each draft contains:

```text
findings.md                  # audience-facing deck outline; sole slide-content source
methodology.md               # internal reference; kept out of the deck
m365-assembly.md
manifest.<project-format>
charts/                      # only when findings.md specifies charts: chart-N.csv per chart
datasets/                    # only when datasets were selected
```

Shared formats live in root `package-format/`: `findings-template.md`, `methodology-template.md`, `m365-assembly.md`, and `manifest-template.md`. They are shared across investigations; preserve existing files and established manifest schemas. The project's copies govern: `findings-template.md` holds the translation rule and slide rules, and `manifest-template.md` the manifest fields.

`methodology.md` is the complete authoritative analytical account in internal vocabulary. `findings.md` derives from it for the brief's **Audience**, states nothing it does not support, and is the slide-by-slide outline of the deck and the only source of slide content.

When releases exist, both narratives retain their complete account and add a concise changes section against the latest release: findings' **What changed since the last version** identifies its delivery date from manifest `released_at`; methodology's **Changes since previous release** names its release number.

The **Answer** slide in `findings.md` is the executive summary; M365 writes none. In the Microsoft 365 Copilot app, the PowerPoint agent builds the deck from `findings.md` and draws each chart natively from its file under `m365-assembly.md`, which lists the draft's files and carries the brief's **Audience**; datasets travel beside the deck. M365 consults methodology for reasoning only. Findings, methodology, chart files, and datasets stay authoritative upstream: substantive revisions return through the draft, and deck edits stay in the deck.

## Structural consistency

Every rule holds for the complete draft:

- `findings.md` stands alone for its audience: context, answer, findings with evidence and contrary results, plain-language method, limitations, and caveats need no earlier release, methodology, or M365 edits. `findings: []` is the mechanical check only.
- `methodology.md` stands alone as the analytical account: scope, sources, method, settings, validation, findings, evidence, contrary results, limitations, and caveats need no earlier release or investigation records. Include methodological mistakes that changed understanding; execution attempts that changed no understanding stay in code history.
- The narratives agree in claims, numbers, qualifications, and caveats. Every `###` finding heading in findings has a methodology section with identical heading text (`headings`).
- The manifest satisfies `package-format/manifest-template.md`.
- The manifest `inventory` matches every draft file's byte size and SHA-256, except its own path-only row (`verify`).
- `charts/` matches the chart specifications in `findings.md` (`charts`). Each chart file serializes a recorded result, and the manifest's `charts` and the methodology name that result.
- `datasets/` and the manifest match the recorded audience-facing selection, including explicit `none`. Headers use glossary display names; methodology maps each to its source column. Dataset and column caveats go under findings' **Supporting datasets**, leaving values as recorded. Exact-rerun inputs or snapshots are included only when the user selects them.

## Revalidation caveats

The manifest's `revalidation_flags` records every finding the investigation's `state.md` currently flags, with its finding and reason exactly as that row writes them (`unmatched_flags` lists the ones it lacks). `represented_in` lists every place the draft represents an affected conclusion, or is `none` when the draft represents none. Each represented flagged finding is listed as unresolved under findings' **Limitations and open caveats** and methodology's **Revalidation status**.

Each represented conclusion carries a nearby caveat unless a recorded disposition omits it: beside claims in both narratives, in a chart specification's **Caveat:** and **Alt text:** lines in findings, or in the dataset or column description under **Supporting datasets**. Findings uses the template's **Awaiting revalidation:** prefix with a plain-language reason, on every slide where the conclusion appears.

A recorded disposition applies while its finding and reason match the current `state.md` row exactly; a new or changed reason reopens it. A draft holds `none` until the user chooses. Release requires `omit` or `release_with_caveat` for every place; `revalidate` pauses the release for separately authorized analytical work.

## Commands

The commands' verdicts settle every mechanical rule; report their rows verbatim. Run each from the project root; `python3 src/awb.py <command> --help` gives its arguments, output keys, and exit status. For a hand export, a non-JSON manifest, or diagnosing a helper's rows (such as a name `check-draft` reports that is not internal), read [helpers](helpers.md).

- `export <investigation> <package>` writes `charts/chart-N.csv`, `datasets/`, and the manifest's `charts`, `dataset_selection`, and `export_checks` from saved result tables, only when every result passes `compare_evidence`; otherwise it reports `exports_blocked` and writes nothing.
- `draft-provenance <investigation> <package> <result-id>...` writes the producing and packaging state from the results' evidence; it writes nothing when any evidence is missing.
- `check-draft <investigation> <package> [--verify-only]` checks the whole draft against every internal name the project defines, the chart files, the headings, the inventory (rewritten unless `--verify-only`), and `state.md`'s current flags. `names_problems` means that name set is incomplete: repair the cause and rerun.
