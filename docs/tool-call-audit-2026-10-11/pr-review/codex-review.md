The review found two **P2** issues:

1. **Malformed flag keys cause a crash after export changes files.** [awb_draft.py:388](.agents/skills/awb-package/assets/awb_draft.py:388)  
   A manifest entry with `"reason": []` causes `sync_flags` to raise `TypeError`. Full export gets to this point after it rewrites chart/dataset files. As a result, the old manifest stays next to the changed exports. `check-draft` detects the malformed entry. But after that, it crashes in `unmatched_flags` and does not return `flag_entries`. Read-only mocked probes confirmed both failures.  
   **Fix:** validate finding/reason types before you hash them. Make unmatched comparisons tolerate invalid entries. Compute flag sync before export writes. Add array/object-key regression cases that assert no partial export.

2. **Rerun detection misses results that are represented only in prose.** [collect_status.py:215](.agents/skills/awb-status/scripts/collect_status.py:215)  
   Create a narrative-only package with `export --result r-001`. Then rerun that result after the draft revision. Its manifest has `export_checks: "none"`. As a result, status returns `rerun_since_draft: []` and does not read the newer evidence. Mixed chart/prose packages also miss prose-only results. This contradicts the status skill’s stated coverage and suppresses its revision request.  
   **Fix:** track every represented result’s evidence independently of export checks. Add narrative-only and mixed-package tests.

I inspected `git diff main...HEAD`, the touched helpers and tests, skills, package contract/template, and guides. Normal flag sync preserves exact-match user choices, resets changed reasons, and reports pending fields correctly. The structural release gate includes `flag_entries`. Frozen-release behavior remains intact. These areas look sound: template creation, retention matching/conflicts, SQL escaping, quality-ID observation preservation, marker/alias checks, and catalog view preference. I found no actionable contradictions in the historical audit records.

The template-equality test passed. The read-only flag and TOML probes also passed. **The full suite could not run:** the sandbox has no writable temporary directory. As a result, pytest stopped before collection. No files were modified.