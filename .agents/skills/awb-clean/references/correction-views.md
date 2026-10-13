# Correction views

Corrections are in the Git-managed canonical view definitions under `foundation/views/`. `session()` loads these definitions in filename order. A definition that reads another view must sort after that view.

## Where the correction goes

Keep one definition for each dataset while the definition stays easy to read. When the corrections become larger, split the definition into a source view and a corrected view under the canonical name. For example, `01_orders_source.sql` reads the publication and `02_orders.sql` applies the rules. Keep the canonical name, because findings and the catalog cite it.

The originals stay readable in the publication and in the landed files. For this reason, add a `_raw` copy of a corrected column only when an investigation needs both. Write fixed date bounds instead of `current_date`, so that a rule gives the same result on any day.

## Patterns

Each pattern is DuckDB SQL in one `CREATE VIEW`. Combine the patterns in a single `SELECT source.* REPLACE (...)`, so that the view keeps the column order of the publication.

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

- **Text placeholders:** `CASE WHEN lower(trim(note)) IN ('', 'n/a', 'unknown') THEN NULL ELSE note END`. Map a placeholder to a value, such as `0`, only when the user said that it means that value.
- **Typing text:** first, map the decided bad values. Then use `CAST`. With a strict `CAST`, a new unparseable value makes the query fail, and this failure is the signal to rescan. `TRY_CAST` changes such a value into null and gives no signal. Use `TRY_CAST` only when the user decided that unparseable values mean missing.
- **Mixed date formats:** `coalesce(TRY_CAST(d AS DATE), CAST(try_strptime(d, '%d/%m/%Y') AS DATE))`. List the formats in the decided order of precedence.
- **Exact duplicate rows:** `SELECT DISTINCT * FROM source` in the source view.
- **Repeated keys:** `QUALIFY row_number() OVER (PARTITION BY order_id ORDER BY updated_at DESC, <tie-breaker>) = 1`. Use the winning-row rule that the user chose, and a deterministic tie-breaker.
- **Out-of-range values:** change the value to null, not the row: `CASE WHEN amount < 0 THEN NULL ELSE amount END`. Use the bound that the user decided.
- **Orphans:** keep the rows. Record the limitation. Each investigation chooses if it excludes these rows.

## When a view cannot express it

A new parse of the landed files (for malformed rows, the wrong delimiter or encoding, or a column that is split differently) is a conversion change. A correction that is too expensive to repeat in every session is also a conversion change.

Publish a corrected dataset from the landed acquisitions with `python3 src/awb.py publish` (its `--help` gives the arguments). Then point the canonical view at the new publication. This switch is a deliberate preparation change, so name it in the report. Keep the earlier publication in place while any reader needs it. The catalog row then names the new publication under `Definition or location` and `Inputs`. Start this catalog row from the `catalog_row` of the command.
