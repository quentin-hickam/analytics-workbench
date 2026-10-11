# Correction views

Corrections live in the Git-managed canonical view definitions under `foundation/views/`, loaded by `session()` in filename order. A definition that reads another view must sort after it.

## Where the correction goes

Keep one definition per dataset while it stays readable. When corrections grow, split it into a source view and a corrected view under the canonical name, for example `01_orders_source.sql` reading the publication and `02_orders.sql` applying the rules. Keep the canonical name; findings and the catalog cite it.

The originals stay readable in the publication and the landed files, so add a `_raw` copy of a corrected column only when an investigation needs both. Write fixed date bounds rather than `current_date`, so a rule gives the same result on any day.

## Patterns

Each pattern is DuckDB SQL inside one `CREATE VIEW`. Combine them in a single `SELECT source.* REPLACE (...)` so the view keeps the publication's column order.

```sql
CREATE VIEW orders AS
WITH source AS (
    SELECT * FROM read_parquet('data/parquet/orders/publication-001/*.parquet')
),
labels(variant, canonical) AS (            -- decided spellings, keyed by lower(trim(label))
    VALUES ('sales', 'Sales'), ('markting', 'Marketing')
)
SELECT source.* REPLACE (
    coalesce(labels.canonical, trim(source.dept)) AS dept,                    -- whitespace and variants
    CASE WHEN source.age IN (-1, 9999) THEN NULL ELSE source.age END AS age,  -- placeholders meaning missing
    CAST(strptime(source.order_day, '%d/%m/%Y') AS DATE) AS order_day         -- one decided format
)
FROM source
LEFT JOIN labels ON lower(trim(source.dept)) = labels.variant;
```

- **Text placeholders:** `CASE WHEN lower(trim(note)) IN ('', 'n/a', 'unknown') THEN NULL ELSE note END`. Map a placeholder to a value, such as `0`, only when the user said it means that value.
- **Typing text:** map the decided bad values first, then `CAST`. A strict `CAST` makes a new unparseable value fail the query, which is the signal to rescan; `TRY_CAST` would turn it silently into null. Use `TRY_CAST` only when the user decided that unparseable values mean missing.
- **Mixed date formats:** `coalesce(TRY_CAST(d AS DATE), CAST(try_strptime(d, '%d/%m/%Y') AS DATE))`, listing formats in the decided order of precedence.
- **Exact duplicate rows:** `SELECT DISTINCT * FROM source` in the source view.
- **Repeated keys:** `QUALIFY row_number() OVER (PARTITION BY order_id ORDER BY updated_at DESC, <tie-breaker>) = 1`, with the winning-row rule the user chose and a deterministic tie-breaker.
- **Out-of-range values:** null the value, not the row: `CASE WHEN amount < 0 THEN NULL ELSE amount END`, with the bound the user decided.
- **Orphans:** keep the rows. Record the limitation; whether to exclude them is each investigation's choice.

## When a view cannot express it

Reparsing landed files is a conversion change: malformed rows, the wrong delimiter or encoding, or a column split differently. So is a correction too expensive to repeat in every session. Publish a corrected dataset from the landed acquisitions with `python3 src/awb.py publish` (its `--help` gives the arguments), then point the canonical view at the new publication; that switch is a deliberate preparation change, so name it in the report. Leave the earlier publication in place while any reader needs it. The catalog row then names the new publication under `Definition or location` and `Inputs`, starting from the command's `catalog_row`.
