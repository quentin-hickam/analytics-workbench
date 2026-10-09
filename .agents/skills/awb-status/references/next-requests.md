## You can ask for

End with the handful of requests the current state makes relevant, each phrased as a sentence the user could type, with its handler in parentheses so hosts without a skill menu still route it. Choose from this map and offer nothing else:

| State | Request | Handler | Kind |
| --- | --- | --- | --- |
| No active investigation | "Start an investigation into <question>" | `awb-init` | progress |
| A consequential scope or purpose decision is open in the brief or state | "Resolve the <topic> scope change" | `awb-init` | progress |
| Findings flagged for revalidation | "Rerun the flagged findings" | `python3 investigations/<name>/run.py` under AGENTS.md | risk |
| A dataset the active investigation uses has no row in the quality record, or unresolved issues or next steps name data errors | "Clean the <dataset> data" | `awb-clean` | progress |
| An active investigation with no findings yet, or a next step that calls for exploring a dataset | "Explore <dataset> for this investigation" | `awb-eda` | progress |
| A draft or release represents a finding flagged since the draft was revised | "Revise the <package> draft to carry the new caveats" | `awb-package` | risk |
| Supported findings and no draft | "Prepare a draft package" | `awb-package` | progress |
| Draft ahead of the latest release, or never released | "Mark the <package> package delivered" | `awb-release` | progress |
| A release exists and storage is unrecorded or unreachable | "Record where releases are kept" | `awb-release` | risk |
| An acquisition is recorded and landed data storage is unrecorded, `none chosen`, or unreachable, or an acquisition has no retained copy | "Record where landed data is kept" | AGENTS.md record maintenance | risk |
| Next steps call for preparation beyond the active question | "Prepare <source> more broadly" | analytical work under AGENTS.md | progress |
| Other investigations exist | "Checkpoint this investigation and switch to <name>" | AGENTS.md record maintenance | progress |
| Uncommitted analytical code or records | "Commit the current work" | explicit commit request | progress |
| State is stale | "Update the investigation state" | AGENTS.md record maintenance | risk |
| `state.md` lists next steps and no other progress row applies | "Continue: <first next step, shortened>" | analytical work under AGENTS.md | progress |

Limit the list to at most five applicable requests that matter most, ordered by risk first (revalidation, storage, staleness), then progress.
