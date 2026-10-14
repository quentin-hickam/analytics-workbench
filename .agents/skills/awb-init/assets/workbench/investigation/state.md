# Current investigation state

Last updated: <!-- use an ISO date -->

## Current findings

| Finding | Evidence | Status | Claim | Revalidation reason or caveat |
| --- | --- | --- | --- | --- |

Status is provisional, supported, superseded, or, for a flagged finding, `revalidation-needed` with its prior status visible, as in `revalidation-needed (was supported)`.

Claim is the strongest wording the finding supports: `descriptive` (what the data shows), `association` (measures move together), or `causal` with its design basis, an experiment or an identified natural experiment, as in `causal (experiment: randomized price test, March 2026)`.

The table is rendered from `findings.json`; change it only through `run.py` and `python3 src/awb.py state` commands. `run.py` writes one row per result, whose Evidence cell links its evidence file, such as `[r-003](evidence/r-003.json)`; `python3 src/awb.py state finding` changes its wording, status, claim, or caveat. Commits and checksums live in the evidence file.

## Unresolved issues

List open analytical questions, relevant data limitations, and decisions still needed. Keep this a short list.

## Next steps

List the smallest concrete steps that would advance the investigation. Keep this a short list.
