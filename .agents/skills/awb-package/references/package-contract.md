# Package contract

Read for every draft creation, revision, or release verification. Repository paths are relative to the project root. This contract governs structure and consistency; [awb-package](../SKILL.md) governs drafting and [awb-release](../../awb-release/SKILL.md) governs delivery.

## Layout and formats

All revisions use `deliveries/<investigation>/<package>/draft/`. Numbered `released/001`, `released/002`, … siblings are immutable. Each draft contains:

```text
findings.md                  # audience-facing deck outline; sole slide-content source
methodology.md               # internal reference; never shown in the deck
m365-assembly.md
manifest.<project-format>
charts/                      # only when findings.md specifies charts: chart-N.csv per chart
datasets/                    # only when datasets were selected
```

Shared formats live in root `package-format/`: `findings-template.md`, `methodology-template.md`, `m365-assembly.md`, and `manifest-template.md`. Preserve existing shared files and established manifest schemas; templates are shared across investigations. Read the project's findings translation rule and manifest field list when drafting or validating; their initial templates are [findings-template.md](../assets/package-format/findings-template.md) and [manifest-template.md](../assets/package-format/manifest-template.md).

`methodology.md` is the complete authoritative analytical account in internal vocabulary. `findings.md` derives from it for the brief's **Audience**, states nothing it does not support, and is the slide-by-slide outline of the deck and the only source of slide content, following the slide rules in the findings template. Use glossary business terms in findings, describe sources by owner/content/period and analytical choices by their effect. The brief records readers, prior knowledge, owned decision, and terms they use. A missing or blank **Audience** must be resolved with the user and recorded in the brief before drafting.

When releases exist, both narratives retain their complete account and add a concise changes section against the latest release: findings' **What changed since the last version** identifies its delivery date from manifest `released_at`; methodology's **Changes since previous release** names its release number. Assembly instructions list the files and carry the brief's **Audience**.

The **Answer** slide in `findings.md` is the executive summary; M365 writes none. In the Microsoft 365 Copilot app, the PowerPoint agent builds the deck from `findings.md` and draws each chart as a native chart from its file under the chart rules in `m365-assembly.md`; datasets are delivered beside the deck. M365 can consult methodology for reasoning only, never as slide content. Findings, methodology, chart files, and datasets stay authoritative upstream. Substantive revisions return through the draft; deck edits are never reconciled back into the workbench.

## Structural consistency

Verify all of these for the complete draft:

- `findings.md` stands alone for its audience: context, answer, findings with evidence and contrary results, plain-language method, limitations, and caveats require no earlier release, methodology, or M365 edits. Run the [findings helper](findings-helper.md) `check` on it with `names` containing the investigation/package names, every view/table name the investigation reads, every settings key, and every result ID cited in its records. Recover that complete set even for a bounded revision. Repair until it returns `[]`; a hand check never substitutes.
- `methodology.md` stands alone as the analytical account: scope, sources, method, settings, validation, findings, evidence, contrary results, limitations, and caveats require no earlier release or investigation records. Include methodological mistakes that changed understanding; execution attempts that changed no understanding stay in code history.
- The narratives agree in claims, numbers, qualifications, and caveats. Every `###` finding heading in findings has a methodology section with identical heading text.
- The manifest uses shared fields and records unknowns with their reasons. A producing commit describes result code; packaging `HEAD` never substitutes. Dirty, `uncommitted`, or unknown producing state is never called reproducible. Without user-selected exact-rerun inputs, provenance locates the producing state but does not guarantee an exact rerun.
- The manifest `inventory` exactly matches every draft file's byte size and SHA-256, except its own path-only row. Run [the manifest helper](manifest-helper.md) `verify`; it must return no discrepancies. Hand comparisons never substitute. Verification reads recorded rows without regenerating them to hide differences.
- `charts/` matches the chart specifications in `findings.md`: run the [charts helper](charts-helper.md) `check_charts`; it must return `[]`. Each chart file serializes a recorded result under the export check, and the manifest's `charts` and the methodology name that result.
- `datasets/` and the manifest match the recorded audience-facing selection, including explicit `none`. Headers use glossary display names; methodology maps each to its source column. Header renaming preserves values. Dataset/column caveats belong under findings' **Supporting datasets**, never in values. Exact-rerun inputs or snapshots require explicit user selection.

## Revalidation caveats

Check current investigation flags, not only flags copied into the draft. For every represented finding awaiting revalidation, the manifest records its current reason and every affected narrative passage, chart, dataset, or column. List the finding as unresolved under findings' **Limitations and open caveats** and methodology's **Revalidation status**.

Each represented conclusion carries a nearby caveat unless a recorded disposition omits it: beside claims in both narratives, in a chart specification's **Caveat:** and **Alt text:** lines in findings, or in the dataset/column description under **Supporting datasets**. Findings uses the template's **Awaiting revalidation:** prefix with a plain-language reason, on every slide where the conclusion appears.

A disposition remains applicable only while the finding, evidence, and flag reason remain materially the same; new or changed flags reopen the choice. Drafting permits `none` pending the user's choice. Release requires an applicable disposition for every affected place; revalidation pauses release for separate analytical work. Release first checks structural rules, settles dispositions, then checks every rule here and reruns `check`, `check_charts`, and `verify` even if nothing changed.
