# Landing helper

If the project lacks `src/preparation/landing.py`, copy [awb_landing.py](../assets/awb_landing.py) there. Preserve an existing customized helper and import the project copy. Run examples from the project root with its `src` importable. Replace illustrative paths and identifiers with the actual source and acquisition. Follow the project's acquisition, retention, and publication rules before calling these interfaces.

## Acquire and publish

`land(root, source, acquisition_id, fetch, *, request, records=None, notes=None) -> Path` calls `fetch(partial_directory)`. The callback writes every original file and raises on incomplete acquisition; its return value is ignored. `request` and `notes` must be JSON serializable. `records` maps relative filenames to integer counts; omitted counts become null. `provenance.json` is reserved. Completed files are hashed, provenance is written, and the directory is renamed from `.partial` only on success.

`publish(root, dataset, publication_id, convert, *, acquisitions, validate=None, notes=None) -> Path` calls `convert(partial_directory)`, then `validate(partial_directory)`. Supply validation for publication: raise on failure or return the Python boolean `False`; every other return value permits publication. `acquisitions` lists completed acquisition directories, absolute or project-relative. Conversion reads them without modification. `publication.json` is reserved; the helper records inputs, hashes, and Git HEAD (or `uncommitted`), then renames the output directory.

Example: land a user-supplied CSV, preserving its bytes, and publish a checked Parquet file. Adapt schema and checks to the source.

```python
from pathlib import Path
import shutil
import pandas as pd
from src.preparation.landing import land, publish

root = Path.cwd()
received = Path('/path/to/received/orders.csv')
acquisition = land(
    root, 'orders', 'received-001',
    lambda output: shutil.copyfile(received, output / 'orders.csv'),
    request={'kind': 'user-supplied-file', 'path': str(received)},
)

def convert(output):
    frame = pd.read_csv(acquisition / 'orders.csv')
    frame.to_parquet(output / 'orders.parquet', index=False)

def check_publication(output):
    frame = pd.read_parquet(output / 'orders.parquet')
    if 'order_id' not in frame or frame['order_id'].isna().any():
        raise ValueError('order_id is required and must be populated')

publication = publish(
    root, 'orders', 'publication-001', convert,
    acquisitions=[acquisition], validate=check_publication,
)
print({'acquisition': str(acquisition), 'publication': str(publication)})
```

Both helpers refuse existing final or partial destinations. Failures leave an unpublished partial directory; resolve it deliberately before retrying. Source, dataset, and run identifiers are single directory names, excluding `.`, `..`, and names ending in `.partial`.

## Retain and query

`retain(root, acquisition_dir, location) -> dict` copies to `<location>/data/raw/<source>/<acquisition-id>/` without overwriting. Its result has `destination`, `copied`, `conflict`, and `discrepancies`. Use the recorded retained location, preserve the full result in the acquisition record or supporting JSON, and report conflicts. A verified copy has no discrepancies; an existing destination can match while still reporting a conflict.

`session(root, *, views_dir='foundation/views')` returns a new in-memory DuckDB connection (requires `duckdb`). It loads `*.sql` in filename order; dependent views sort after their inputs. Project-relative data paths resolve against `root`. Run saved queries by path and close the connection:

```python
from src.preparation.landing import session

with session(root) as connection:
    query = root / 'investigations/order-quality/exploration/missing-ids.sql'
    result = connection.execute(query.read_text()).df()
```
