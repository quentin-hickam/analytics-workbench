# Findings helper interface

Read when interpreting the `findings` rows `check-draft` reports or calling the helper directly. If `src/packaging/findings.py` is missing, copy [awb_findings.py](../assets/awb_findings.py) there. Preserve existing helpers and call the project copy; inspect implementation only for incompatible interfaces or diagnosis.

`check(path, *, names=()) -> list[dict]` scans Markdown for code, paths, filenames, identifiers, SHAs, and supplied internal names. Rows retain `line`, `kind`, and `text`, ordered by line and column. It ignores HTML comments and Markdown link targets. `[]` means this mechanical check passed; audience suitability, supported claims, matching headings, and caveats still require the package contract's review. Read errors fail the check.

`check-draft` in `src/awb.py` calls it on the draft's `findings.md` with the complete `names` set, which it derives from the project as the package contract's **Commands** section describes, and reports its rows unchanged. A narrative-only change still checks the whole file with the complete set. When the command reports `names_problems`, the set is incomplete: repair the cause, such as an unparsable settings file, rather than checking by hand.

Repair every returned result during drafting. At release, report results unchanged and stop for a package revision when any remain; the `release` command runs the check fresh even when no disposition changed. The command keeps its complete output in its `record` file.
