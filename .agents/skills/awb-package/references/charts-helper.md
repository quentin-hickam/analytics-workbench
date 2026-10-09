# Charts helper interface

Read when a draft's `findings.md` specifies charts. `awb-init`'s `scripts/install_helpers.py` places this helper at `src/packaging/charts.py` and restores it when missing; never copy by hand. Preserve a customized helper and call the project copy; inspect implementation only for incompatible interfaces or diagnosis. `write_charts` needs pandas; `check_charts` needs only the standard library.

`write_charts(charts_dir, charts) -> list[Path]` takes one DataFrame per chart, in the order the **Chart N.** specifications appear in `findings.md`, and writes `charts_dir/chart-1.csv`, `chart-2.csv`, and so on, removing chart files a previous revision left beyond the new count. Each frame holds exactly the plotted values, in display order and at the slide's rounding, with display-name headers carrying units and interval bounds as their own columns. It raises, writing nothing, for an empty list, an empty frame, a blank or repeated header, or a header that looks like an internal name (an underscore or a dot between letters).

`check_charts(findings_path, charts_dir) -> list[dict]` matches the specifications with the files. Rows retain `chart` and `problem`: a specification numbered out of order, a specification without a file, a file without a specification, a file in `charts/` that is not a chart file, or a file without data rows. `[]` means the mechanical match passed; whether each file carries its recorded result's values is settled by the export check in `awb-package`.

Run from the project root, replacing the example paths and frames with the package's charts, each serialized from its recorded result after `draft-provenance --export-checks` passes:

```python
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path("src/packaging").resolve()))
from charts import write_charts

draft = Path("deliveries/order-quality/decision/draft")
paths = write_charts(draft / "charts", [late_by_region, monthly_cases])
print(json.dumps({"charts": [str(p) for p in paths]}))
```

`check-draft` runs `check_charts` on the draft and reports its rows unchanged under `charts`. Repair every returned result during drafting. At release, stop for a package revision when any remain.
