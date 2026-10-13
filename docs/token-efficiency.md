# Efficiency validation

Measure the instruction load and the whole-run token use separately. A split of files saves context only when the task follows the narrower read path. If every branch reads a reference, that reference is still part of the cost of that branch.

## Static comparison

From the repository root, run this command:

```sh
python3 scripts/measure-instruction-load.py
```

The baseline is `40a0e9330607686e1326f699c684da04c55c13a3`. This is the PR #6 merge on main with audience-facing findings, internal methodology and caption-free figures. To use a different baseline, use `--baseline <revision>`. The script counts the words and characters for the declared instruction paths. If a path is not in the baseline or in the working tree, it counts as zero words and is listed under that side's `missing`, so the script runs across layout changes.

An unchanged release reads only its own skill, because `check-draft --verify-only` is its structural gate. A release with a flagged finding adds the package contract for the disposition. A narrative revision also adds the package contract. The package helper reference is read only on rare branches, and it is excluded.

The analysis path loads the data procedures and the analysis procedures. The cleaning path and the exploration path add their skills. The exploration path also adds the follow-up query reference, which is read before the first query. For these paths, the baseline is only the root instructions, which at that time held every procedure. These full branches can become larger even when the entry points become smaller.

The script does not estimate model tokens, cache savings, reasoning, tool output, project records or artifact generation. When the status fallback references are necessary, they add cost. It is possible that existing sessions already have instructions loaded. These counts describe fresh loads. The script is repository tooling, and it is not shipped in the skills archive.

## Agent-run comparison

Compare the baseline skills and the revised skills. For each comparison, use these conditions:

- fresh chats
- the same model/settings
- identical isolated fixture projects
- the same user prompts.

Repeat each scenario, to tell the difference between variance and improvements. Use these four requests:

1. “Where do things stand?” Include a case with no commit and a case with dirty work. Also include a finding that was flagged after the draft was made and is not in the draft, and a customized record format. The run must show accurate uncertainty. It must not write, and it must not read the conclusions of other investigations.
2. “Calculate the regional rate comparison and record the finding.” Supply canonical inputs and settings. The `run.py` of the investigation must produce the result. All seven validation categories must be assessed. The run must also give full evidence and accurate state/history updates.
3. “Revise the draft to explain this recorded limitation.” Include unrelated older history and existing exports. The run must give a complete and consistent narrative, current caveats, and byte-identical reused results and exports. It must also do a final verification of the findings and the manifest.
4. “Mark this package delivered.” Test an unchanged draft and also a newly flagged finding. A new run of `check-draft --verify-only` must pass. A valid disposition must exist before release. The run must also keep prior releases frozen, copy exactly, and verify the storage or give an explicit copy instruction.

Record these measurements:

- input/output tokens and cached input, separately, where the host shows them
- reasoning tokens, when they are available
- tool-output size
- tool calls
- retries
- correctness outcomes.

If a measurement is not available, record it as unavailable. Compare equivalent completed outcomes. A run that skips necessary work does not show better efficiency. To benchmark instructions, do not run live acquisitions, do not publish artifacts, and do not overwrite project data.

## Acceptance

The existing helper tests and the regression tests of the status collector must pass. Check the links in the source tree and also in a built distribution. After you copy the project guides, check the links in the generated `AGENTS.md`. The build uses tracked files. For this reason, validate newly added files in an isolated Git staging fixture before they are committed here. In behavioral checks, keep the explicit dataset selection, material-unknown handling, validation evidence, release dispositions and frozen releases.

Static reductions and unit tests do not prove end-to-end token savings. Report them separately from any recorded agent-run measurements.

## Validation after rebasing onto PR #6

The earlier measurements against `edcaeff` were made before PR #6 and are superseded. The baseline is now `40a0e9330607686e1326f699c684da04c55c13a3`. The full helper suite passed with 123 tests. Four tests that depend on DuckDB were skipped, because DuckDB was not available. All five skill validators passed. An isolated distribution build included every new asset, and its relative links resolved. The copied project-guide links also resolved.

The status regressions reproduce these conditions:

- Markdown-formatted storage values
- optional storage lines that are absent
- a workbench nested in a larger repository
- unreadable directories
- methodology-based representation review.

Before the fixes, these regressions were run, and they failed. The plotting regression runs the documented recipe against a copy of the current style helper. It checks for a successful PNG output, and it checks dimensions, opacity and provenance. If a helper import is removed, the plotting regression will fail. The manifest and findings interface examples were also run against copies of the project helpers.

An independent synthetic release exercise rejected an internal-name leak. Then, in each of the two release passes, it ran the findings checks and the inventory checks again. It kept the draft and the prior release byte for byte. It advanced the release numbering and did not fill gaps. It verified the retained copy with `compare_trees`. It used only the current findings/methodology layout.

These are the measured instruction words for the declared reading paths:

- Root instructions: 2,010 → 614 (69.5% fewer).
- Root plus both project guides: 2,010 → 1,695 (15.7% fewer).
- Status, with its request map: 3,307 → 1,611 (51.3% fewer).
- Table presentation: 4,490 → 1,635 (63.6% fewer).
- Release without revision: 5,574 → 3,292 (40.9% fewer).
- Narrative revision: 4,292 → 3,789 (11.7% fewer).

The table presentation path was retired when `awb-visualize` was removed. Its measurement above is kept as it was recorded. These figures are from before later layout changes:

- The status request map is now in the status skill.
- The package helper references are one file, which is read only on rare branches.
- `awb-update` was merged into `awb-init`.
- Release uses `check-draft --verify-only` and does not read the package contract again.

For the current paths, run the script again.

These are file-size measurements. They are not whole-run token savings. The release/revision paths include the necessary findings and manifest interfaces. They do not include project records, helper implementation reads or conditional figure work. No matched baseline/revised run with token telemetry was done. The agent-run procedure above is still the method to measure actual token savings.
