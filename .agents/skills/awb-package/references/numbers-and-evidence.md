# Numbers and missing evidence

## Numbers

- `numbers` rows (`check_numbers(path, values, *, allowed=(), claim_lines=())`; `check-draft` passes
  the line numbers of the **Claim strength:** lines the `claims` check accepts as `claim_lines`):
  `file`, `line`, `text`, and `problem`, which names the rule that left the number untraced (no
  recorded value at its written precision, joined digits, a recorded value on its rounding's edge,
  or a year-like number read as a count) and points to `allowed_numbers`;
- `text` is the number as written with its unit or the letters written against it, such as `21.3%`,
  `4.2M`, `1.5e6`, or `5GB`;
- a currency sign is left out, and so is a USD, EUR, GBP, JPY, CHF, CAD, AUD, CNY, or INR code
  written against the number, as in `USD4.2M`.
- The values are each represented result's `results/<id>.csv` cells, the numbers in its
  `results/<id>.profile.json`, and its evidence's check details and settings, as magnitudes, so a
  sign carried by words such as "fell" still traces.
- JSON numbers are read exactly as written, never through a binary float.
- A cell that is a number whole is that number; any other cell, check detail, or settings text is
  read the way a narrative line is, adding each number it states and, with a scale, the scaled value
  too, so `$4.2M` records 4,200,000 and an ID such as `ORD-123` records nothing.
- A column a manifest `charts` or `dataset_selection` entry records with a `scale` or `prose_scale` divisor also
  records each of its number cells divided by it.

### Tracing

- A number written to d decimal places traces to a value that rounds half up to it, as `export`
  rounds: from half a unit below its last place, that edge included, to strictly below half a unit
  above (`1.5e6` to 1,450,000 up to but not including 1,550,000), compared exactly at every written
  digit as magnitudes, so 0.5245 traces for `52.5%` and 0.5255 does not, giving the edge problem;
- a share a query rounded onto the lower edge is left to `export`'s `precision_warnings`;
- a percent or percentage points also to a fraction 100 times smaller (`21%` to 0.214);
- a scale such as `k`, `M`, `bn`, or `million` also to the scaled value;
- and the lower bound of a range such as `10-15%` or `10 to 15%` takes the upper bound's unit.
- `%` and the word units (`percent`, `per cent`, `percentage points`, `pp`, `thousand`, `million`,
  `billion`, `trillion`, `mn`, `bn`, `tn`) belong to their number across any whitespace, a line wrap
  included;
- a letter scale (`k`, `M`, `b`) or `x` only when written against it, so `5 m` is 5.
- Scientific notation is read with any mantissa, such as `1e-5`, `12.5e3`, `.5e-3`, or `5.e-3`; an
  exponent too large to hold never traces.
- Digits joined by dots, commas, slashes, or colons, or three-digit groups joined by spaces, are one
  number: thousands grouping such as `1,240` and a single decimal point trace;
- a version or address, three or more dotted parts not all three-digit groups such as `3.12.1` or
  `10.0.0.1`, is skipped;
- two numbers joined by one slash, such as `54.8/57.6`, `264/265`, or `368/53.5%`, are two numbers,
  each traced alone, a unit after the second belonging to it alone, so a fraction such as `3/4` is
  checked as 3 and 4, never as 75%;
- and any other join, such as `1,2,3`, the decimal comma `21,3%`, `1/2/3`, `9:30`, `1.234.567`, or
  `1 000 000`, is reported and never traces, so write it as `1, 2, 3`, `21.3%`, `1,234,567`, or a
  share as a percent.

### Reading fails safe

- A number is skipped only in one of the contexts below, each of which marks it as no quantity or,
  on a **Claim strength:** line, as copied from the record.
- Every other number is read, including one whose context leaves it in doubt, and is reported unless
  it traces or is allowed; clear such a row by rewording, such as ending a date or year with a
  comma, or with an `allowed_numbers` entry and its reason.
- A line that wraps a paragraph, in a quote too, is read with the lines around it, so a context or a
  unit split from its number by the wrap is still seen.
- Where a context below says the period ends, it ends at punctuation, at a dash before a space, or
  at the end of its paragraph: a word after it could make its last number a count, as in `in 2000
  orders`.

### Skipped

- Code, HTML comments, and link targets. A comment is what the [helper reading](helpers.md) drops,
  so a `<!--` in a code span, fenced code, or a link's target, or escaped, hides no number. A code
  span is read with escapes first, so text between escaped backticks, as in ``fell \` 37% \` in``,
  is read. A code span is paired across its whole paragraph, so one wrapped over lines hides only
  its own text, never a number after it.
- Paths whole: a slash token, starting with a letter, `_`, `~`, `./`, or `../`, that starts with
  `./`, `../`, or `~`, has two or more slashes, starts with a project folder (`data`, `foundation`,
  `investigations`, `deliveries`, `src`, `views`, `queries`, `results`, `evidence`, `exploration`,
  `scans`), or ends in a file name with a known extension, such as `results/r-001-77.csv`.
- A DOI: `10.`, a registrant code of four to nine digits with any dot-separated parts, a slash, and
  its suffix up to the next whitespace or a `,` or `;` before a digit, such as `10.24432/C5CG6D`,
  after `doi:` or `DOI`, or bare when its suffix holds both a letter and a digit; a bare
  `10.2500/litre` or `10.2500/1000` is a quantity and is read, and so is `478` in
  `10.24432/C5CG6D,478`.
- A file name with a known extension (`.md`, `.py`, `.csv`, `.tsv`, `.parquet`, `.json`, `.jsonl`,
  `.sql`, `.png`, `.svg`, `.jpg`, `.jpeg`, `.pdf`, `.htm`, `.html`, `.duckdb`, `.db`, `.xls`,
  `.xlsx`, `.docx`, `.pptx`, `.yaml`, `.yml`, `.toml`, `.txt`, `.log`, `.ipynb`).
- A hyphenated identifier whose first part is one letter, holds a digit or `_`, or has a capital
  after its first letter, such as `ORD-123-45`, `COVID-19`, `Q-3`, or `r-001`, and the chart file
  stem `chart-1`.
- A number glued to a letter before it or to a name's `_` (`Q2`, `FY2026`, `H1`, `late_77`), or to
  letters and digits after it (a hash such as `3f9a2c1`); a version or address, as above; a
  zero-padded code such as release `002`.
- Numeric dates (`2026-06-30`, with or without a time, and `6/30/2026`), times with am, pm, UTC, or
  GMT or with seconds (`9:30am`, `14:05:30`), and 24-hour times, two-digit hours from 00 to 23 and
  minutes from 00 to 59 (`18:00`, `23:59`), so a ratio such as `12:20` is skipped too; write a ratio
  as `1:20` or in words.
- A day from 1 to 31 before or after a month name, with or without a year, where the date ends or
  runs to another date (`June 5, 2026,`, `5 June.`, `June 1, 2026 to June 30, 2026`).
- A year from 1900 to 2099 directly after an English month name, written in full or in three letters
  with or without a period, whatever follows it (`December 2011 is`, `Dec. 2011`; `Sept 2011` is
  read), or alone in parentheses (`(2025)`; `(Smith, 2025)` is read). A year from 1900 to 2099 after
  in, from, since, during, until, till, through, before, after, between, year, FY, CY, fiscal,
  calendar, early, mid, late, a month name, or a quarter or half such as Q3 or H1, where the period
  ends (`in 2025.`, `mid-2025.`, `Q3 2025,`).
- Years listed after such a year as a range (`2023-2024`, `2023 to 2025`, `2023 vs 2024`) or a list
  that and or or closes (`2019, 2020, and 2021`), where the list ends.
- The one number after Chart or Charts, and the rest of a Charts list listed the same way where the
  list ends (`Charts 1 and 4.`).
- A list marker where a list starts, a heading's leading section number (`## 2. Sources`), and
  footnote marks.
- In `methodology.md`, a **Claim strength:** line the `claims` check accepts, which repeats its
  results' `state.md` Claim cell, design basis included, so its numbers trace to the record (`causal
  (experiment: randomized holdout of 2024 Q3, 50/50 split)`); only that source line, so a number on
  a line continuing its paragraph is read, and a line the `claims` check refuses keeps its numbers.
- Repair that line's `claims` row first: once the line matches `state.md`, its `numbers` rows clear
  with no `allowed_numbers` entry.

### Read

- So reported unless they trace or are allowed: `In June 77 orders`, `June 5 we met`, both numbers
  of `on June 5 77 orders`, `On June 5, 2026 we met` (2026), `in 2000 orders`, `Q3 2025 revenue`
  (2025), `(2025 orders)`, `between 1950 and 2000 stores`, `Charts 1 and 4 show it` (4), `1950
  orders`, `over 2025`, `2026 H1`, `Python 3.12`, `Week 23`, `top-10`, `Total,77`, `West/21.3%`,
  `100ms`, an ordinal such as `95th` (its number traces), and a number other than 1 that starts a
  line continuing a paragraph (`rose to` then `77. Orders`), which Markdown does not make a list;
  inside a list item or a quote too, unless the line is indented exactly as a list item on the line
  above (`- rose to` then `  77. Orders` reads 77; `1. a` then `2. b` is a list).
- An unindented number after a list item or an indented line starts a list.

### Allowed

- An `allowed` text covers a number wherever that text is written around it, matched on the text the
  number is read from: a space in it matches any whitespace or a line wrap, quote markers included,
  so a row's `text` copied exactly always covers its number.
- A bare `23` covers every 23 in every narrative, and the phrase `Week 23` only that one.

### Limit

- The check proves a number is among the recorded values, not that it is its claim's value or that
  the narratives give a claim the same number: with a large represented table most small numbers
  trace, and the two halves of a slash pair trace apart.
- A count right after a month name or alone in parentheses is skipped as a year (`June 2026 orders`,
  `(2025)`); write it with a separator (`2,026`).
- Numbers written as words, such as three, or as a single symbol, such as ½, are not read, so write
  a claim's numbers in digits.
- Two skips can take a count: `chart` as a verb (`We chart 12 months`), and two counts from 1900 to
  2099 written as a year range that ends a sentence (`rose from 1950 to 2040.`); write such counts
  with a separator (`1,950`) or reword.
- Recorded text is read line by line, so a scale on the line after its number (`$4.2` then
  `million`) records only 4.2, and the full written value is reported.
- The contract's [Writing rules](package-contract.md#writing-rules) govern claim agreement.

## Missing evidence

- When `export` reports missing evidence it writes nothing, so the draft and its manifest stay as
  they were.
- Stop and report it as for `exports_blocked` when a result without evidence is serialized by a
  `--chart` or `--dataset`, or has an entry in the manifest's `export_checks` (`export` records one
  for every result a chart or dataset file serializes and keeps it while the result is represented),
  or when no `--result` in a `--result`-only run has evidence: only separately authorized analytical
  work restores the evidence, and dropping a chart, a dataset, or a recorded export check is the
  user's decision.
- Otherwise rerun it without those results.
- For each, the rerun drops only its `results` entry and its share of the producing state (the
  fields under **Producing state** in `package-format/manifest-template.md`);
- add both back by hand: the `results` entry with the `evidence` path `export` named, the `question`
  from the result's settings table, and its `runtime` copied from an earlier manifest's `results`
  entry, or `{"unknown": "evidence missing"}` when none records it, never read from the current
  interpreter;
- and the producing state from investigation records or an earlier manifest, never from the current
  checkout.
- While their evidence is missing, every later `export` run drops them again, so restore them after
  each.
