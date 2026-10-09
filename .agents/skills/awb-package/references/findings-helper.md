# Findings helper interface

Read when checking a draft's audience-facing prose, including both release verification passes. If `src/packaging/findings.py` is missing, copy [awb_findings.py](../assets/awb_findings.py) there. Preserve existing helpers and call the project copy; inspect implementation only for incompatible interfaces or diagnosis.

`check(path, *, names=()) -> list[dict]` scans Markdown for code, paths, filenames, identifiers, SHAs, and supplied internal names. Rows retain `line`, `kind`, and `text`, ordered by line and column. It ignores HTML comments and Markdown link targets. `[]` means this mechanical check passed; audience suitability, supported claims, matching headings, and caveats still require the package contract's review. Read errors fail the check.

Always supply the complete `names` set: investigation name, package name, view/table names the investigation reads, settings keys, and result IDs its records cite. Recover these from the composition/input records, settings, and investigation records as needed; the helper does not discover them. A narrative-only change still checks the whole file with the complete set.

Run from the project root, replacing the example path and names with the actual package and complete set:

```python
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path("src/packaging").resolve()))
from findings import check

path = Path("deliveries/order-quality/decision/draft/findings.md")
names = ["order-quality", "decision", "orders_view", "orders_table",
         "minimum_count", "orders-001"]
results = check(path, names=names)
print(json.dumps({"findings": str(path), "results": results}))
```

Repair every returned result during drafting. At release, report results unchanged and stop for a package revision when any remain. Run fresh after dispositions even when none changed. Keep complete output on disk if large, report its count and path, and make all unchanged rows available without truncation.
