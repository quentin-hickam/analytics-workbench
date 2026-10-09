# Result evidence helper

If the project lacks `src/provenance.py`, copy [awb_provenance.py](../assets/awb_provenance.py) there. Preserve an existing customized helper and import the project copy. The helper uses Python 3.10+ and the standard library; parsed TOML settings require `tomllib` (Python 3.11+). A non-Python project ports the same interface and `awb-evidence/1` format.

## Record a produced result

`record_evidence(root, investigation, result_id, *, views, publications, acquisitions, settings_path, checks, figure=None, notes=None, code_paths=None) -> Path` writes the full evidence atomically at `investigations/<investigation>/evidence/<result_id>.json`, replacing that result ID's previous record. Call from the investigation's composition entry after producing and validating the result.

Use project-relative paths for views, input directories, settings, figure, and code; paths must remain within the project. `investigation` and `result_id` are simple identifiers starting with an alphanumeric character and continuing with alphanumerics, `.`, `_`, or `-`. Supply every actual input explicitly; view references are inspected, but input lists are not inferred. `checks` is the unchanged validation list of `{name, outcome, detail}` strings. `settings_path=None` records unknown settings, not an empty known configuration. Settings parsing is TOML; projects with another configuration format adapt the project helper to record their resolved settings.

`code_paths` accepts producing files or directories. Its default covers `src` and investigation files while excluding brief/state/history and the evidence, figures, and exploration directories. Supply explicit paths when producing code lies outside that default, including saved exploratory SQL consumed by the composition entry.

```python
from pathlib import Path
import json
from src.provenance import record_evidence

root = Path.cwd()
checks_path = root / 'investigations/order-quality/exploration/orders-checks.json'
checks = json.loads(checks_path.read_text())
evidence_path = record_evidence(
    root, 'order-quality', 'orders-001',
    views=['foundation/views/01_orders.sql'],
    publications=['data/parquet/orders/publication-001'],
    acquisitions=['data/raw/orders/received-001'],
    settings_path='investigations/order-quality/settings.toml',
    checks=checks,
    code_paths=['src', 'investigations/order-quality/run.py',
                'investigations/order-quality/exploration/orders.sql'],
)
print({'result_id': 'orders-001', 'checks': len(checks), 'evidence_path': str(evidence_path)})
```

The file preserves producing commit and uncommitted-file hashes, view definitions, publications, acquisitions, resolved settings, checks, optional figure, and notes. Unknowns are `{"unknown": "reason"}`. Data hashes are copied from acquisition/publication metadata during recording and checked against files during comparison. Before a first commit, evidence records `uncommitted` and producing-file hashes; suggest a commit so later results carry a SHA. Track analytical code in Git.

## Compare before an export

`compare_evidence(root, evidence_path) -> list[dict]` returns five ordered comparisons: `committed-code`, `uncommitted-code`, `views`, `inputs`, `settings`. Each contains `name`, `paths`, `outcome` (`pass` or `fail`), and `detail`. Save the complete list and carry it unchanged into the package manifest's `export_checks`. This is a state comparison, not renewed analytical validation. Failed or missing evidence blocks the export under `awb-package`.

```python
from src.provenance import compare_evidence

comparisons = compare_evidence(root, evidence_path)
comparison_path = evidence_path.with_name('orders-001-export-checks.json')
comparison_path.write_text(json.dumps(comparisons, indent=2) + '\n')
failed = [item['name'] for item in comparisons if item['outcome'] == 'fail']
print({'comparisons': len(comparisons), 'failed_checks': failed,
       'comparison_path': str(comparison_path)})
```

Use the package's existing audit location for comparison output during packaging. Read failure details as needed without dumping complete file inventories into chat. `file_checksums(paths, *, root=None)` supports inventories: it returns `{path, bytes, sha256}` entries in input order, with null size/digest for missing files. Store full inventories on disk and surface counts, discrepancies, and their paths.

For package inventories and draft/release verification, use the [manifest helper interface](../../awb-package/references/manifest-helper.md).
