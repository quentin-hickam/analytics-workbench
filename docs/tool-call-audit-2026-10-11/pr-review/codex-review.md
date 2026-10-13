Found two **P2** issues:

1. **Malformed flag keys crash after export has changed files.** [awb_draft.py:388](.agents/skills/awb-package/assets/awb_draft.py:388)  
   A manifest entry with `"reason": []` causes `sync_flags` to raise `TypeError`. Full export reaches this after rewriting chart/dataset files, leaving the old manifest alongside changed exports. `check-draft` detects the malformed entry, but subsequently crashes in `unmatched_flags` instead of returning `flag_entries`. Read-only mocked probes confirmed both failures.  
   **Fix:** validate finding/reason types before hashing them, make unmatched comparisons tolerate invalid entries, and compute flag sync before export writes. Add array/object-key regression cases asserting no partial export.

2. **Rerun detection misses results represented only in prose.** [collect_status.py:215](.agents/skills/awb-status/scripts/collect_status.py:215)  
   Create a narrative-only package using `export --result r-001`, then rerun that result after the draft revision. Its manifest has `export_checks: "none"`, so status returns `rerun_since_draft: []` without reading the newer evidence. Mixed chart/prose packages likewise miss prose-only results, contradicting the status skill’s stated coverage and suppressing its revision request.  
   **Fix:** track every represented result’s evidence independently of export checks. Add narrative-only and mixed-package tests.

I inspected `git diff main...HEAD`, the touched helpers and tests, skills, package contract/template, and guides. Normal flag sync preserves exact-match user choices, resets changed reasons, and reports pending fields correctly. The structural release gate includes `flag_entries`; frozen-release behavior remains intact. Template creation, retention matching/conflicts, SQL escaping, quality-ID observation preservation, marker/alias checks, and catalog view preference look sound. I found no actionable contradictions in the historical audit records.

The template-equality test passed, as did read-only flag and TOML probes. **The full suite could not run:** the sandbox has no writable temporary directory, so pytest stopped before collection. No files were modified.