# Delivery manifest fields

The manifest is `manifest.json`. Record times in ISO 8601 with a UTC offset, such as `2026-09-30T14:05:00-04:00`.

## Package identity

- `investigation`, `package`, and `status` (`draft` or `release`): written by `export` when it creates the manifest;
- `revised_at`: stamped by `check-draft` when the inventory changes; a release keeps the draft's value;
- `release_number` (such as `002`), `released_at`, and `prior_release` (the latest numbered release before this one, such as `released/001`, or `none`): written by `release` on the release copy;
- `review`: the passed review the release rests on, its `kind` (`full` or `scoped`), `recorded_at`, and `accepted`, each problem the user accepted with their reason, written by `release` on the release copy from the draft's review receipt; and
- `inventory`: every file in the package directory, each with its path relative to the package directory using `/` separators, byte size, and SHA-256; directories are not listed. The manifest lists itself by path only, with no size or checksum, since writing them would change them. `python3 src/awb.py check-draft` writes it.

## Producing state

The analytical results this package represents.

- `producing_commit`: the producing commit SHA, recovered from result evidence in the investigation records or an earlier manifest, never assumed from the packaging checkout; or `uncommitted` with the recorded SHA-256 checksums of the producing files when no commit existed;
- `producing_uncommitted_changes`: `none`, or each affected code, view, and settings path with the checksum recorded for it when the result was produced, since a SHA with uncommitted changes does not fully identify the producing code; paths without recorded checksums are listed as such, and the producing state is then not recoverable;
- `inputs`: the inputs actually used: source and acquisition or publication identifiers with the checksums their provenance or publication files record, and the view definitions read with their checksums; and
- `analytical_settings`: the analytical settings represented by the results.

Each result's runtime is recorded beside it under `results`, in **Packaging state**.

`python3 src/awb.py export` writes these fields from the represented results' evidence files. When every result records the same value, the field holds it; when results differ, it holds each distinct value with the results that recorded it, under `value` and `results`. `inputs` holds `publications`, `acquisitions`, and `views` lists copied from the evidence; list entries name the results that recorded them under `results`. An unknown is `{"unknown": "<reason>"}`. For an `uncommitted` state, `producing_uncommitted_changes` holds the checksum of every producing file.

## Packaging state

The operation that assembled this package, recorded separately from the producing state.

- `packaging_commit`: the packaging checkout commit;
- `packaging_uncommitted_changes`: `none`, or the relevant uncommitted package-source paths;
- `export_checks`: each serialized result's `compare_evidence` output, or `none` without exports; and
- `results`: every represented result, serialized or not, as `result_id`, `evidence` path, `question`, copied verbatim from the evidence, and `runtime`, the Python version, platform, package versions, and `unread_requirements` (requirements lines it could not read, each a provenance gap) its evidence recorded, or `{"unknown": "<reason>"}` when it recorded none.

`export` writes `packaging_commit` and `packaging_uncommitted_changes` (paths under `src/` and `package-format/`), and `export_checks` as one entry per result, each with `result_id`, `evidence`, and the unchanged `comparisons`: a serialized result's entry is replaced, a represented result not serialized keeps its entry, and an entry outside the represented set is dropped.

## Selection

- `dataset_selection`: each dataset's `path`, `result_id`, `columns`, `percent` columns shown 100 times larger, file `scale` divisors, optional `prose_scale` divisors for prose alone, and decimal places (`round`); or explicit `none`. An earlier export may list paths alone; and
- `charts`: each chart file's `path`, `result_id`, `columns`, row `selection` (`all`, `{"first": n}`, or `{"where": {"column", "values"}}`), `headers`, value labels used (`values`), `percent`, `scale`, optional `prose_scale`, and `round`; or `none`. `check-draft` traces narrative numbers to a `scale` or `prose_scale` column's values divided by its divisor, refuses an entry whose headers, value labels, percent columns, or divisors differ from `foundation/display.toml`, reapplies each entry to the saved table, and refuses a differing chart file.

`export` writes both, and each `revalidation_flags` entry's finding and reason, one per flagged finding; you fill `represented_in` and the user's `disposition`, required when `represented_in` lists places. The package contract's **Revalidation caveats** defines the field. `methodology.md` states row selection, file and prose unit scales, percent scaling, and rounding from `charts` and `dataset_selection`, as `export`'s `methodology_lines` give them.

Say the provenance locates the producing state; never call a package reproducible. Record an undeterminable field as `{"unknown": "<reason>"}`; a string such as `"unknown: evidence lost"` is not read as a provenance gap.

## Storyline

- `slide_slugs`: each finding slide in deck order as `slug`, `heading`, and `primary`, the first result its methodology section cites, or `none`. `export` writes it once `findings.md` and `methodology.md` exist, and `check-draft` updates each `heading`; both leave it as it is while `check-draft`'s `headings` lists a row.
  - A slug is taken from the slide's heading the first time it is recorded: its first six words, lowercased ASCII letters and digits joined by hyphens, such as `late-orders-rose-in-the-west`.
  - A slide keeps its slug while its heading stays, or, reworded, while its primary result stays, so a reworded heading keeps its place in `presentation_order`. A slide reworded while citing no result, or both reworded and given another primary result, takes a new slug.
- `presentation_order`: absent or `none`, or the finding slide slugs in the order the user approved, main sequence first and then the appendix, as `slide_slugs` and `check-draft`'s `ledger_order` give them.
  - Record it when the user approves an order of finding slides that differs from the order the ledger gives. Ledger priority, parent, and `show` stay as they are: they decide what the **Open questions** slide lists.
  - While it is a list, `check-draft`'s `storyline` rows hold the finding slides to it, and refuse a list that misses or repeats a slide's slug or names a slug no finding slide has.

You record `presentation_order` and `export` keeps it.

## Numbers

- `allowed_numbers`: `none`, or each narrative number that no represented result records as `{text, reason}`. An absent field is `none`.
  - `text` is the row's `text` exactly as `check-draft` reports it, or a phrase around it, such as `Week 23` or `over 2025`; a space in it matches any whitespace or line wrap the narrative has there. Prefer the phrase: a bare text is accepted wherever it is written in any narrative, a phrase only where that phrase is.
  - `reason` is one of two kinds. For a number the records support from elsewhere, name the record, such as the earlier release it comes from or the `history.md` entry recording the fact the user supplied. For a text that is not a quantity, say what it is: a comparison year, a tool version, a week or section number, or an identifier.
  - Never for a number from a recorded result the draft relies on: pass that result to `export` instead, so `results` and the producing state record it. Never for a number computed from results that none records.

You record it and `export` keeps it.

## The user's acceptances

- `accepted_long_headlines`: absent, or `{headline, reason}` for each headline over 15 words the user chose to keep. `headline` is the `outline` row's `headline` exactly, so a reworded headline needs a new entry; `reason` is the user's reason.
- `helper_drift_confirmed`: absent, or `{file, sha256, reason}` for each `helper_drift` row the user confirmed, `file` and `sha256` copied from the row (`null` for a missing file), so a later change to that file needs a new entry; `reason` is the change and why the user accepts it.

You record each on the user's yes, and `export` keeps them.
