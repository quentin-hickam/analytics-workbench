# Follow-up queries

Read this before writing the first follow-up query of a session. Save each query as `investigations/<name>/exploration/<topic>.sql` and run it from the project root:

```sh
python3 src/awb.py sql investigations/<name>/exploration/<topic>.sql
```

The command opens a fresh session with the canonical views, prints the first rows as a table with the row count, and takes `--limit N` for more rows and `--out <file>.csv|.parquet` for the full result. Keep results small enough to read in chat: aggregate, order, and limit in SQL.

Start each file with a comment naming the question it serves and the scope it applies. Copy the scan's printed filters into the `WHERE` clause so the follow-up explores the same population. Replace the illustrative names below.

## Drill into one group

```sql
-- Why does site South fall while overtime rises overall? Scope: region <> 'EU', 2025.
SELECT date_trunc('month', shift_date) AS month, role,
       count(*) AS shifts, avg(overtime_hours) AS mean_overtime
FROM shifts
WHERE region <> 'EU' AND shift_date BETWEEN DATE '2025-01-01' AND DATE '2025-12-31'
  AND site = 'South'
GROUP BY ALL ORDER BY month, role;
```

## Cross two dimensions

```sql
-- Does the site difference hold within each role?
SELECT site, role, count(*) AS shifts, avg(overtime_hours) AS mean_overtime
FROM shifts
WHERE region <> 'EU'
GROUP BY ALL ORDER BY role, mean_overtime DESC;
```

## Separate mix from within-group change

```sql
-- Group shares and means per quarter; a moving overall mean with stable group means is a mix shift.
WITH groups AS (
    SELECT date_trunc('quarter', shift_date) AS quarter, site,
           count(*) AS shifts, avg(overtime_hours) AS mean_overtime
    FROM shifts
    WHERE region <> 'EU'
    GROUP BY ALL)
SELECT quarter, site, shifts * 1.0 / sum(shifts) OVER (PARTITION BY quarter) AS share, mean_overtime
FROM groups ORDER BY quarter, site;
```

## List duplicates or variants for a shared data problem

```sql
-- Duplicate shift_id values, for the awb-clean handoff.
SELECT shift_id, count(*) AS copies, min(shift_date) AS first_date, max(shift_date) AS last_date
FROM shifts
GROUP BY shift_id HAVING count(*) > 1
ORDER BY copies DESC LIMIT 50;
```

```sql
-- Spellings that collapse under lower(trim()).
SELECT lower(trim(site)) AS normalized, list(DISTINCT site) AS spellings, count(*) AS rows
FROM shifts
GROUP BY 1 HAVING count(DISTINCT site) > 1;
```

## Distribution within groups

```sql
-- Quartiles of the measure by group.
SELECT site, count(*) AS shifts,
       quantile_cont(overtime_hours, [0.25, 0.5, 0.75]) AS quartiles,
       max(overtime_hours) AS max_overtime
FROM shifts
WHERE region <> 'EU'
GROUP BY site ORDER BY site;
```

## Examine a gap or low period

```sql
-- Rows per day around an empty month.
SELECT shift_date, count(*) AS shifts
FROM shifts
WHERE shift_date BETWEEN DATE '2025-05-15' AND DATE '2025-07-15'
GROUP BY 1 ORDER BY 1;
```

A follow-up that excludes rows for a local reason states the reason in a comment. Before the exclusion goes into the composition entry, it belongs in settings, never in a shared view.
