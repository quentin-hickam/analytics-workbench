---
name: awb-status
description: Report analytics workbench status, revalidation flags, package and storage state, and relevant next requests. Use when the user asks where things stand or what to do next. Read-only.
---

# Report workbench status

Give a read-only snapshot and the requests that fit now. Change no files, run no analysis, refresh no caches, query no sources, and make no commit. Mention fixes as possible next requests.

## Collect

Run the bundled helper, using this skill's actual directory to resolve its path:

```sh
python3 <skill-directory>/scripts/collect_status.py <project-root>
```

Use the user-named project, otherwise the current directory. The helper uses Python's standard library and emits compact JSON; execute it without reading its implementation. It reads standard Markdown records, JSON manifests, local storage availability, and Git with optional locks disabled, including projects inside larger repositories. It reads other investigations only for names and state dates. A non-workbench result means stop and suggest `awb-init`.

Treat `null`, `unknown`, and `uncertainties` as targeted fallback requests, never as empty findings or zero risk. Read only the named record or field needed to resolve each uncertainty. Established custom formats remain valid: inspect their manifests directly when the helper cannot parse them. Missing records are facts to report, not permission to create them. Absent optional storage lines mean unrecorded storage; they matter when acquisitions or releases exist. Unknown directory inventories remain unknown, including `release_inventory_known: false`. For unavailable Git, make a read-only check using the repository's actual root if needed, or report the limitation. Skip history, source data, and other investigations' conclusions.

## Interpret

- Count statuses from the active findings; `revalidation-needed (was supported)` belongs only in needs revalidation. Give every flagged finding its current reason. Read `foundation/quality.md` correction rows only when a reason points to one and needs explanation.
- For each package's `representation_review`, read its `review_methodology` (`methodology.md`, which names finding identifiers) to decide whether it represents each unmatched flagged finding. An unmatched finding represented there was flagged since the draft revision. Count it as lacking a disposition; also count each `confirmed_flags` finding whose `without_disposition` is true. A disposition applies only to the same finding and current reason, and every represented place must have a disposition other than `none`. Helper counts are confirmed subsets until semantic review finishes; customized or malformed flags need manual review.
- Use the helper's commit/change dates and day difference for staleness. Same-day comparisons are indeterminate at date precision; deleted files lack modification dates. With no commits, say “no commits yet; all work uncommitted.” Modification dates use the host timezone; if it differs from the user's reporting timezone and changes the comparison, convert those timestamps before reporting.
- Compare draft `revised_at` with the highest numeric release's `released_at`. File modification time is an estimate only when a field is absent; malformed values remain unknown.
- An open decision must be explicitly recorded in the brief or state. Material unknowns alone do not establish one.
- Landed-data storage is at risk when acquisitions exist and storage is unrecorded, unreachable, or an acquisition has a blank retained copy or `this checkout only`. Release storage is at risk when a release exists and storage is unrecorded or unreachable. Unknown availability needs a read-only check through the established access method or an explicit “not verified.”

## Report

Keep the report to one screen: active question and state date/staleness; findings counts and every flag/reason; unresolved issues and next steps; other investigation names/dates; each package's draft/latest release dates, comparison, findings without dispositions, and findings flagged since draft; relevant storage risks. Preserve the investigation's wording, shortened. Omit empty sections; expose material uncertainties.

Finish with up to five relevant **You can ask for** requests, risk first then progress. Read [next-requests.md](references/next-requests.md) to select requests and their handlers; offer only applicable entries from that map. Reporting never performs those follow-up actions.
