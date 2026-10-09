# Efficiency validation

Measure instruction load separately from whole-run token use. Splitting files only saves context when the task follows the narrower read path. A reference that every branch reads is still part of that branch's cost.

## Static comparison

From the repository root run:

```sh
python3 scripts/measure-instruction-load.py
```

The baseline is `40a0e9330607686e1326f699c684da04c55c13a3`, the PR #6 merge on main with audience-facing findings, internal methodology, and caption-free figures; override it with `--baseline <revision>` only when that revision has the original paths. The script counts words and characters for declared instruction paths, including the shared contract, manifest interface, and findings-check interface needed for release and revisions. The table path includes the analytical procedure guide required before presenting results; the analysis path loads both data and analysis procedures. These full branches can grow even as entry points shrink. It does not estimate model tokens, cache savings, reasoning, tool output, project records, or artifact generation. Status fallback references add cost when needed. Existing sessions may already have instructions loaded; these counts describe fresh loads. The script is repository tooling and is not shipped in the skills archive.

## Agent-run comparison

Compare the baseline and revised skills using fresh chats, the same model/settings, identical isolated fixture projects, and the same user prompts. Repeat each scenario to distinguish variance from improvements. Use these four requests:

1. “Where do things stand?” Include no-commit and dirty-work cases, a current revalidation flag absent from the draft, and a customized record format. Require accurate uncertainty, no writes, and no reading of other investigations' conclusions.
2. “Calculate the regional rate comparison and record the finding.” Supply canonical inputs and settings. Require the composition entry to produce the result, all seven validation categories to be assessed, full evidence, and accurate state/history updates.
3. “Revise the draft to explain this recorded limitation.” Include unrelated older history and existing exports. Require a complete consistent narrative, current caveats, byte-identical reused results and exports, and final findings and manifest verification.
4. “Mark this package delivered.” Test both an unchanged draft and a newly flagged finding. Require both findings-check and manifest-verification passes, a valid disposition before release, immutable prior releases, exact copying, and verified storage or an explicit copy instruction.

Record input/output tokens and cached input separately where the host exposes them, reasoning tokens when available, tool-output size, tool calls, retries, and correctness outcomes. Record unavailable measurements as unavailable. Compare equivalent completed outcomes; a run that skips required work is not an efficiency win. Do not run live acquisitions, publish artifacts, or overwrite project data to benchmark instructions.

## Acceptance

Existing helper tests and the status collector's regression tests must pass. Check links both in the source tree and in a built distribution, and check generated `AGENTS.md` links after copying the project guides. The build uses tracked files: validate newly added files in an isolated Git staging fixture before they are committed here. Preserve the explicit dataset selection, material-unknown handling, validation evidence, release dispositions, and immutable release boundaries in behavioral checks.

Static reductions and unit tests do not establish end-to-end token savings. Report those separately from any recorded agent-run measurements.

## Validation after rebasing onto PR #6

The earlier measurements against `edcaeff` predated PR #6 and are superseded. The baseline is now `40a0e9330607686e1326f699c684da04c55c13a3`. The full helper suite passed with 123 tests; four DuckDB-dependent tests were skipped because DuckDB was unavailable. All five skill validators passed. An isolated distribution build included every new asset and its relative links resolved, as did the copied project-guide links.

Status regressions reproduce Markdown-formatted storage values, absent optional storage lines, a workbench nested in a larger repository, unreadable directories, and methodology-based representation review. They were run failing before the fixes. The plotting regression executes the documented recipe against a copied current style helper, checks successful PNG output, dimensions, opacity, and provenance, and would fail on a removed helper import. Manifest and findings interface examples were also executed against copied project helpers.

An independent synthetic release exercise rejected an internal-name leak, then ran both findings and inventory checks afresh in each of the two release passes. It preserved the draft and prior release byte for byte, advanced release numbering without filling gaps, and verified the retained copy with `compare_trees`. It used only the current findings/methodology layout.

Measured instruction words for the declared reading paths:

- Root instructions: 2,010 → 614 (69.5% fewer).
- Root plus both project guides: 2,010 → 1,695 (15.7% fewer).
- Status, including its request map: 3,307 → 1,611 (51.3% fewer).
- Table presentation: 4,490 → 1,635 (63.6% fewer).
- Release without revision: 5,574 → 3,292 (40.9% fewer).
- Narrative revision: 4,292 → 3,789 (11.7% fewer).

The table presentation path was retired when `awb-visualize` was removed; its measurement above is kept as recorded.

These are file-size measurements, not whole-run token savings. Required findings and manifest interfaces are included in the release/revision paths; project records, helper implementation reads, and conditional figure work are not. A matched baseline/revised run with token telemetry has not been performed. The agent-run procedure above remains the method for measuring actual token savings.
