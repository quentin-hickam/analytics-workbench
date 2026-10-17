# Kept cases:
# test_check_draft_checks_findings_drift: synchronized JSON passes, drift fails with state render in both modes, an old helper gets an upgrade hint, and rows with no findings.json are drift.
# test_names_cover_project_records: names hold created views, sources without CTEs or table functions, settings dotted paths (not bare nested keys), and result IDs from evidence and state links; plain words, including plain investigation and package names, are left out.
# test_toml_keys_fall_back_to_tomli_then_key_lines: without tomllib, settings keys parse with tomli (no bare nested keys); without either, table headers and key lines; display.toml then names the missing package.
# test_check_draft_rewrites_inventory_and_passes: a clean draft passes; START-HERE.md is written and the inventory, rewritten, lists it; revised_at is stamped only when the inventory changes, other manifest fields kept; nothing is written outside the draft.
# test_evidence_older_than_scoped_3_is_reported_for_rerun: check-draft and export --result refuse awb-evidence/1 and unscoped /3 with a rerun instruction.
# test_check_draft_reports_each_helper_problem: an internal name, a path under the plain investigation name, a chart without a file, a finding heading methodology lacks, and a missing settings file each fail with the helper's rows unchanged.
# test_check_draft_reports_outline_and_chart_spec_rows: a headline over 15 words, a chart form outside the seven, a Data column the chart file lacks, and a file column no Data role names fail check-draft with outline and charts rows in both modes, and release refuses on them.
# test_check_draft_requires_each_question_in_methodology: export's questions pass once methodology repeats them; a question methodology lacks or rewords, a results entry without a question, and a manifest without results fail check-draft's questions, and release refuses on the check.
# test_questions_check_reads_methodology_as_it_renders: a question wrapped, emphasized, linked, escaped, in a code span, heading, or list item, or after a comment block on its line matches; one only in a comment, inline or a block, in fenced code, split over two paragraphs, or reworded does not.
# test_questions_check_matches_a_code_span_as_written: a question holding brackets, a tilde, an edge underscore, an asterisk, a character reference, or a backslash matches when a code span shows it exactly as written.
# test_questions_check_refuses_a_commented_question: the issue's probe, a question only inside an HTML comment, fails check-draft's questions; a manifest question with inline markup matches as it renders.
# test_questions_check_leaves_out_image_text: a question only in an image's text, a linked image's included, or split by an image, with text or without, does not match, nor does one in an image's text that holds an autolink (an email's too), a link whose target or title has a bracket, or, after an escaped backslash or backtick, a code span with a bracket, or in an image after an escaped backslash, or whose target nests or escapes parentheses or escapes a quote in its title; one in a link's text, in prose beside an image or after its text, in a code span showing an image's syntax, after an escaped backslash or backtick too, after an escaped !, beside an unclosed ![ whose brackets a link takes, or in a reference image, which never resolves, matches.
# test_other_checks_still_read_image_text: the names scan and the shared reading keep an image's text, so a name in it is a findings row.
# test_check_draft_help_and_references_agree_on_the_rendered_reading: the check-draft help text, helpers.md, and the comment above _view name numbers as the only check that does not read the rendered view, and state that it skips only the comments that view drops; the help and helpers.md state how questions are read, image text left out.
# test_check_draft_reports_unmatched_flags: in both modes, a finding state.md flags fails until the manifest records its exact finding and reason; a changed reason reopens it; no findings table is an error.
# test_export_replaces_malformed_flag_entries_before_writing: an entry whose reason is not text matches no flag and is replaced by a fresh entry; the export writes files and manifest together.
# test_check_draft_and_release_refuse_malformed_flag_entries: a missing revalidation_flags, a non-list value, an entry without text finding and reason, and [] or blank places fail check-draft's flag_entries, and release refuses on the check.
# test_check_draft_traces_narrative_numbers: numbers in both narratives trace to a represented result's table cells within rounding, check details, settings, and profile rates as percents; an untraced number fails with its file, line, and text in both modes and refuses release; allowed_numbers accepts it and export keeps that field; dropping a result from the represented set untraces its numbers.
# test_check_draft_reports_number_problems: a malformed allowed_numbers value or entry, a malformed results value or result_id, a missing result table, and an unreadable profile are numbers_problems that fail the check.
# test_check_numbers_reads_formats: thousands separators, percents of fractions, scales, multipliers, scientific notation, ranges, and rounding trace; dates, years where their period ends, times with am or pm or seconds, codes, glued names, chart number lists, list markers, footnotes, code, comments, and link targets are skipped; a count beside a month name, a bare or parenthesized year-like count, a fraction, a time without am or pm, and a hash in scientific form are read; allowed texts pass.
# test_check_numbers_reviewed_probes: every narrative probed in review rounds 1 to 4 is reported or skipped as intended, reading fail-safe: a context skips a number only where it marks no quantity, so a count after a punctuation mark, a chart reference, a date, or a year, or a year a word follows, is read; paths and identifiers are skipped whole; joined digits that are not thousands grouping or one decimal are read and never trace; a unit or context split by whitespace or a line wrap still counts; a number wrapping a list item's text is read, and a row's text allowed exactly covers it across a wrap; a leading- or trailing-point scientific mantissa is one number; and non-quantities such as a comparison year or a week number are reported.
# test_recorded_text_reviewed_probes: every recorded text probed in review records the magnitudes intended, and an extreme or non-finite cell records nothing or itself without crashing.
# test_check_numbers_skips_a_doi: a DOI, 10. with a four- to nine-digit registrant code, a slash, and a suffix, is skipped whole after doi: or DOI, in a doi.org link, or bare when its suffix holds a letter and a digit, ending at whitespace or a , or ; before a digit; a shorter registrant code, no slash, a bare suffix without a letter or a digit, as in 10.2500/litre, 10.2500/1000, or 10.12345/67.8, and a number glued after a DOI by , or ; are read.
# test_provenance_gaps_are_unknown_objects_and_unread_requirements: an {"unknown": reason} object and an unread requirements line are gaps; a settings value or column name such as unknown_pickup, or a string starting with unknown, is not.
# test_check_numbers_reads_ordinary_notation: the issue's probes: 54.8/57.6 traces when both values are recorded, each half traced alone; 18:00 and December 2011 is give no row; an untraced figure still does.
# test_numbers_rows_name_the_rule_that_applied: each numbers row's problem names why its number did not trace (no recorded value, joined digits, a recorded value on its rounding edge, or a year-like count) and points to allowed_numbers.
# test_check_numbers_allowed_phrases_and_precision: an allowed phrase covers only the number it is written around, a bare allowed text every occurrence; a row's text copied exactly covers its number after a line wrap or extra spaces; a number traces at every written digit beyond 28 significant digits and not one unit of a further place outside its rounding.
# test_recorded_values_reads_whole_cells_and_quantities: a table cell is a number whole (an exponent too large to round does not crash) or read as narrative text, so an ID's or a path's digits add nothing; evidence text and parsed settings content add scaled and scientific values a narrative can write in full, without dates, booleans, or the settings file's size.
# test_recorded_values_keep_every_json_digit: profile and evidence fractions keep every written digit, so the exact narrative value traces and a value one digit off does not.
# test_verify_only_never_writes: a changed file is reported against the recorded inventory; the manifest stays byte-identical.
# test_missing_manifest_runs_other_checks: without manifest.json the findings and chart checks still run; verify is not run and the check fails.
# test_export_results_records_provenance_only: --result alone writes shared commit, inputs, settings, and packaging state, creates the manifest with its identity fields, leaves chart files untouched, and is not gated by a changed setting.
# test_export_creates_revalidation_flags_from_state: from an absent manifest, export records none when state.md flags nothing, else each flag verbatim with represented_in [] and disposition none, listed in flags_pending.
# test_export_syncs_revalidation_flags_with_state: entries follow state.md row order; exact matches are kept whole; a changed reason starts a fresh entry; a cleared flag drops; flags_pending lists [] places and kept entries at none; no flags left records none.
# test_export_keeps_flags_when_state_is_unreadable: export still writes, reports flags_error, and leaves revalidation_flags as it was.
# test_flag_raised_after_none_fails_until_export_records_it: a flag raised after none fails check-draft and release through unmatched_flags; the next export records it as pending.
# test_export_keeps_differences_and_unknowns: differing commits are listed per result and an unknown keeps its reason.
# test_export_refuses_missing_evidence_or_unnamed_chart_result: a missing evidence file, or a --result call that leaves out a charted result, writes nothing.
# test_export_writes_charts_datasets_and_manifest: display names, mapped codes, and rounding shape a saved result into a chart and a dataset; the manifest records each chart's and dataset's shaping, passing export checks for serialized results only, and producing state for every represented result.
# test_export_gives_an_unrounded_float_column_a_round_gap_and_stub: a column showing more than four decimal places without [round] is an error row per file with round_stub lines to paste under [round], and nothing is written; only the cells a file holds count; a blank pasted stub is its own error; [round] or --round covers the column, and the manifest records the places.
# test_unrounded_cells_follow_the_stated_threshold: accepted and refused rows for the stated rule: a finite number cell is unrounded when its saved text, trailing zeros aside, any exponent applied, and a percent column's 100-fold scaling applied, has more than four decimal places, digits beyond a float's precision included; text, NaN, infinity, an overflowing exponent, separators, underscores, and spaces never are.
# test_export_percent_scales_fractions_and_records_them: [percent] columns are scaled by 100 exactly from the saved text before rounding, in charts and datasets, and recorded in the manifest's charts and dataset_selection entries; a top-level list, a non-list, or another key under [percent] is refused.
# test_per_result_display_names_override_the_global_ones: [results."<id>".columns] and .values name one result's columns and values over the global names, a per-result value table replacing the global one whole; another key under a result, or a percent table of another shape, is refused.
# test_a_per_result_percent_list_replaces_the_global_one: [results."<id>".percent] lists one result's percent columns in place of [percent], so a column already holding percents in one result is not scaled again; the manifest records each file's list and check-draft reapplies it.
# test_export_scale_needs_places_when_its_quotient_is_unrounded: a divisor whose quotient shows more than four places needs [round] places, listed with round_stub, and the methodology line states the division before the rounding.
# test_export_scale_divides_records_and_traces: a [scale] divisor divides a column's number cells before percent scaling and rounding, in charts and datasets, is recorded in their manifest entries and methodology lines, is refused when not { divide = <a positive number> }, and makes a narrative number written in the scaled unit trace; check-draft refuses an entry whose divisor differs from display.toml.
# test_export_warns_on_a_fraction_rounded_in_its_query: a [percent] column shown to fewer than two places whose saved fractions have exactly four places is a precision_warnings row, the files still written; full precision, or two places shown, gives none.
# test_export_warns_on_a_value_code_no_cell_holds: a [values] code no exported saved table holds, such as true where pandas saved True, is a value_warnings row naming the table, with the near cell when only case differs; codes the tables hold give none.
# test_confirmed_columns_silence_their_label_warning: a column under [confirmed] columns gives no label_warnings row, other columns still do, and a malformed [confirmed] is refused.
# test_export_warns_when_one_name_labels_results_with_different_questions: a global [columns] name labeling files from results with different questions is a label_warnings row, the files still written; the same question or a per-result name gives none.
# test_chart_selection_grammar_accepts / test_chart_selection_grammar_refuses: accepted and refused rows for --chart RESULT[:COLUMNS][@first=<n>|@where=<column>=<value>[,<value>]], each refusal naming the part that does not fit.
# test_export_selects_chart_rows_and_records_the_selection: @first=10 writes the first 10 rows and @where the matching rows in table order, the manifest recording each selection; an unknown column, a value no row holds, or too many rows is an error, malformed syntax and a dataset selection exit 2, and nothing is written.
# test_check_draft_refuses_a_chart_file_that_differs_from_its_selection: a hand-edited value, an extra row, a renamed header, or a changed saved table fails check-draft in both modes and refuses release; a chart file with no charts entry, an entry from an earlier export, which a --result-only export keeps, so its row names the export with every --chart, an entry whose file is missing, and a malformed charts field each give a row.
# test_check_draft_writes_start_here_before_the_inventory: check-draft writes START-HERE.md's three parts, listing the methodology note and datasets when present, before the inventory lists it; --verify-only writes none and reports an edited one; the prompt is assembly/m365.md's.
# test_check_draft_reports_draft_markers_as_information: draft, working copy, or not a numbered release in the title, subtitle, a heading or headline, or title notes is an informational draft_markers row in both modes; drafted, redraft, working copies, other notes, and bullets are not read as markers.
# test_export_checks_follow_the_represented_set: a represented result not serialized keeps its entry; a result outside the represented set drops; an export without --chart removes the chart files and records charts none.
# test_export_names_every_gap_and_blocks_stale_results: every missing display name is listed at once; a changed setting blocks a serializing export with a stop message and writes nothing; --no-datasets records none; --chart without a dataset choice is refused.
# test_export_display_stub_names_each_gap_once: missing display names on chart and dataset paths give one quoted [columns] line each, deduplicated, a dotted column kept as one key; a blank name gets its own error and no stub line, so the stub pastes as valid TOML.
# test_release_refuses_failed_check_or_pending_disposition: a failing verify, an unmatched flag, or a none/revalidate disposition creates no release; a missing or unknown disposition or malformed places fail the check's flag_entries; represented_in none needs no disposition.
# test_release_reports_fields_for_the_report: datasets, dispositions marked new against the prior release's manifest (unknown when it is unreadable), open caveats (the Limitations and open caveats slide's headline and bullets, then flags released with their caveat, new or carried forward), provenance gaps, checkout-only acquisitions, and a clean local verify.
# test_open_caveats_read_the_deck_wherever_its_caveat_slides_stand: the Open questions slide's headline and bullets and a Limitations and open caveats slide moved under ## Appendix are read in deck order, each headline before its bullets, nested items kept with their bullet; a Limitations slide holding only its headline gives that headline's row; finding slides, omitted flags, and unrepresented flags give no row.
# test_release_manifest_lists_runtime_per_result: export copies each represented result's runtime block into its results entry, unknown when the evidence has none or a null one, as stale reads it, and the release manifest keeps them; each unread requirements line is a provenance gap.
# test_release_numbers_stamps_and_copies_to_storage: the next number after a gap, stamped copy, untouched draft, storage copy at <location>/<investigation>/<package>/<n>/ compared, with no released/ folder there.
# test_release_storage_conflict_and_instructions: an existing destination is never overwritten; none chosen, unrecorded, and URL locations report what to do, naming <location>/<investigation>/<package>/<n>/.
# test_check_draft_refuses_causal_wording_above_claim_strength: causal wording on an association finding's slide fails with a row naming the phrase, line, and claim; a causal finding's slide and the Answer slide under a causal represented finding pass; method and caveat slides, code, comments, and hyphenated words are not read; release refuses on the row.
# test_review_probes_read_markdown_as_it_renders: every reviewer probe of the claim check from rounds 1 to 3, one row each with its claims, headings, and markdown rows: headlines, caveat bullets, fences, comments open, closed, or in a list, declarations hidden, ambiguous, in a code span, in a list or quote, or naming another design, emphasis, links, hard breaks, and other inline markup, commented-out, duplicated, and indented headings, headings continuing a list item, and every form outside the Markdown subset.
# test_unsupported_markdown_fails_check_draft: a heading continuing a list item fails check-draft and release with its markdown row, and the wording below it is read on the finding slide.
# test_names_and_charts_read_the_same_rendered_text: the names scan and the chart check skip comments as CommonMark scopes them, and read escaped, character-reference, zero-width, and emphasized names and chart numbers as they render.
# test_claim_check_reads_headlines_and_cited_designs: a causal ### headline fails check-draft with a row to reword both files; cited causal results of different designs are refused; a whitespace design is unrecognized.
# test_claim_strength_follows_cited_results_and_records: a slide citing several results takes the weakest claim; one citing none takes the weakest represented; with no causal finding the Answer slide fails too; a missing Claim, a missing results list, and a missing or differing methodology Claim strength line each fail.
# test_numbers_skip_a_claim_strength_line_the_claims_check_accepts: numbers on a causal Claim strength line that repeats its result's Claim cell give no numbers row, while a line continuing its paragraph is read; a line the claims check refuses, another design or no experiment named, keeps its numbers; check_numbers skips only the claim_lines it is given.
# test_numbers_count_lines_as_the_claims_check_does_after_a_comment: a comment holding a line break that str.splitlines() sees (U+2028, form feed, NEL) keeps the numbers check's line numbers on the claims check's, so the accepted-claim skip cannot land on the next line.
# test_numbers_check_drops_only_the_comments_the_draft_renders: a number after a <!-- in a code span (after an escaped backslash or backtick too), escaped, in fenced code, in a link's target or title, or written <!-->, with a later -->, is read, as the rendered view shows it, and so is one between escaped backticks; with no <!--, or one code span holding a whole comment, it is read; one in a comment, a block, within its paragraph or a link's text, across a list item's lines, after tabs, or in a heading, is skipped and the text after --> is read; a comment starting at column 0 and never closed hides the rest of the file from both, an empty last line included, and a comment may end the file without a line break; the numbers check reads exactly the view's lines outside fenced code.
# test_a_comment_marker_written_as_text_is_no_comment_never_closed: a <!-- in a link's target or title, a code span after an escaped backslash or backtick, or escaped is no markdown row; one in text that no --> closes within its paragraph is.
# test_check_draft_reads_numbers_after_a_comment_marker_written_as_text: the issue's code span shape in methodology.md fails check-draft in both modes with its numbers row, and release refuses.
# test_numbers_check_and_rendered_view_drop_the_same_comments: across a seeded corpus of 2,000 random narratives, link targets and escaped code spans among their pieces, the words the rendered view drops as comment are exactly those the numbers check's source lines blank, code spans aside, which it blanks by design, and the numbers check reads exactly the view's lines outside fenced code.
# test_numbers_check_pairs_code_spans_across_the_paragraph: a number after a code span wrapped across lines, a span on a later line after it, is read, as the draft shows it; one inside a wrapped span is skipped; a span on one line keeps its result. A line opening with a span, all code, or ending a wrapped span still leaves a numbered line after it wrapping the paragraph, in a quote too, so its number is read.
# test_an_allowed_text_quoting_a_code_span_covers_its_number: an allowed text holding a code span matches the line as written and covers its number.
# test_negated_causal_phrases_are_no_claims: a causal phrase in a negated clause, under the closed grammar _NEGATOR, _CLAUSE_END, and _UNKNOWN declare, is skipped; a negator outside the clause or window, in a relative clause, or an intensifier such as not only leaves it a row.
# test_check_draft_skips_negated_causal_wording: does not test what caused them passes check-draft's claims; drove the increase on the same slide is still a row.
# test_methodology_note_limitations_section_is_not_read_for_claims: causal wording under the note's ## Limitations, its ### sections included, gives no claims row; the same sentence under another section does.
# test_methodology_note_is_checked_with_rows_naming_it: a clean methodology-note.md passes and joins the inventory; an internal name, an untraced number, causal wording above the strongest represented claim, and an HTML block in it fail check-draft and release with rows naming the file; without it check-draft reports exactly what it did before.
# test_check_draft_counts_main_and_appendix_slides: slides counts the main sequence, title included, and the appendix apart; How we know under ## Appendix passes.
# test_appendix_slides_are_checked_like_main_slides: How we know under ## Appendix needs no methodology section; an appendix finding slide is held to its claim strength.
# test_appendix_how_we_know_and_limitations_wording_is_not_read: with only an association result represented, causal wording on How we know and Limitations under ## Appendix gives no claims row, and the same wording on an appendix finding slide is refused.
# test_presentation_order_decides_finding_order_when_set: absent or none leaves the ledger order; a non-ledger order the slides follow passes, inline markup read as the heading is; an order missing a finding, listing one twice, naming a heading no slide has, out of the slides' order, not a list, holding a blank entry, or recorded as JSON null fails storyline in both modes.
# test_export_keeps_presentation_order: export keeps the hand-recorded presentation_order.
# test_presentation_order_is_no_provenance_gap: a presentation_order heading that starts with Unknown is no release provenance gap, as allowed_numbers is not.
# test_storyline_orders_main_and_appendix_findings_each_by_the_ledger: main and appendix finding slides are ranked separately, the appendix numbering on.
# test_open_questions_follows_how_we_know_when_limitations_is_in_the_appendix: with Limitations under ## Appendix, Open questions passes after How we know and fails before it.
# test_copy_releases_copies_compares_and_never_overwrites: existing releases copy to newly recorded storage at <location>/<investigation>/<package>/<n>/; a rerun reports already copied; a differing copy is a conflict; an unknown package fails; no audit directory is written.

import hashlib
import importlib.util
import json
import random
import re
import shutil
import subprocess
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest

if shutil.which("git") is None:
    pytest.skip("git is required", allow_module_level=True)

SKILLS = Path(__file__).resolve().parents[1] / ".agents/skills"
ASSETS = {
    "src/awb.py": SKILLS / "awb-init/assets/awb_cli.py",
    "src/provenance.py": SKILLS / "awb-init/assets/awb_provenance.py",
    "src/packaging/draft.py": SKILLS / "awb-package/assets/awb_draft.py",
}
VIEW = b"""-- orders_comment_name stays out
CREATE OR REPLACE VIEW orders_view AS
WITH recent AS (SELECT * FROM read_parquet('data/parquet/orders/p1/*.parquet'))
SELECT r.*, EXTRACT(year FROM r.ordered_at) AS y FROM recent r JOIN main.regions_table g USING (region);
"""
SETTINGS = (b"[parameters]\nminimum_count = 5\nstart = 2026-01-01\n\n"
            b'[results.r-001]\nquestion = "How many claims closed late?"\n\n'
            b'[results.r-002]\nquestion = "Which regions close claims late?"\n')
STALE_SETTINGS = SETTINGS.replace(b"minimum_count = 5", b"minimum_count = 6")
RESULT = "region,late_rate,n\nW,21.349,10\nE,2.675,8\n"
CHART_SPEC = "**Chart 1.** Horizontal bar: late share by region\n- **Data:** category: Region; value: Closed late (%)\n"
# The fixture's chart file as export records it: r-001's first row, its region labeled and its rate rounded whole.
CHART_ENTRY = {"path": "charts/chart-1.csv", "result_id": "r-001", "columns": ["region", "late_rate"],
               "selection": {"first": 1}, "headers": ["Region", "Closed late (%)"],
               "values": {"region": {"W": "West"}}, "percent": [], "scale": {}, "round": {"late_rate": 0}}
# The display names and value labels CHART_ENTRY records.
CHART_DISPLAY = '[columns]\nregion = "Region"\nlate_rate = "Closed late (%)"\n\n[values.region]\nW = "West"\n'
# The required slides around the finding slides: the title and Answer open the deck, How we know and
# Limitations and open caveats follow the findings.
OPENING = ("# Order quality\nOperations leads, all regions\n\n## Answer\n\n**Headline:** The west has the most late orders\n\n"
           "**Notes:** The west leads the regions.\n\n## Findings\n\n")
HOW_WE_KNOW = "\n## How we know\n\n**Headline:** Totals reconcile to the order ledger\n\n**Notes:** Orders are counted once.\n"
LIMITATIONS = ("\n## Limitations and open caveats\n\n**Headline:** Coverage remains limited\n\n"
               "**Notes:** Interpret with care.\n")


def deck(slides, closing=HOW_WE_KNOW + LIMITATIONS):
    """A findings.md around the given finding slides."""
    return OPENING + slides + closing


BASE = deck("### Late orders rose in the west\n\n" + CHART_SPEC + "\n**Notes:** The west leads the regions.\n",
            HOW_WE_KNOW)
FINDINGS = BASE + LIMITATIONS
QUESTIONS = {"r-001": "How many claims closed late?", "r-002": "Which regions close claims late?"}
METHODOLOGY = ("# Methodology\n\n## Findings\n\n### Late orders rose in the west\n\n"
               "**Claim strength:** association\n\n"
               "Question (r-001): How many claims closed late?\nQuestion (r-002): Which regions close\nclaims late?\n")
STATE = """# Current investigation state

Last updated: 2026-10-01

## Current findings

| Finding | Evidence | Status | Claim | Revalidation reason or caveat |
| --- | --- | --- | --- | --- |
| Late orders rose in the west | [r-009](evidence/r-009.json) | {status} | association | {reason} |
| West volume is stable | [r-001](evidence/r-001.json) | supported | association | |
| Discounts cut late orders | [r-002](evidence/r-002.json) | supported | causal (experiment: randomized discount test) | |

## Next steps
"""
FLAGGED = STATE.format(status="revalidation-needed (was supported)", reason="Q-3 corrected west dates")
FLAG = {"finding": "Late orders rose in the west", "reason": "Q-3 corrected west dates"}
PLACES_PROBLEM = "represented_in is not none or a list of places; list them or record none"


def git(root, *args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", *args],
                          cwd=root, check=True, capture_output=True, text=True).stdout.strip()


def write(root, path, content):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content if isinstance(content, bytes) else content.encode())
    if path.endswith("/state.md") and isinstance(content, str):
        findings_for(target, content)


def findings_for(state, text):
    """Write the findings.json a state.md's rows render from, as run.py and `state` would have."""
    entries = []
    for line in text.splitlines():
        match = re.fullmatch(r"\| (.*) \| \[(.+)\]\(evidence/\2\.json\) \| (.*) \| (.*) \| ?(.*?) ?\|", line)
        if match:
            finding, result, status, claim, reason = (part.strip() for part in match.groups())
            claim, _, basis = claim.partition(" (")
            flagged = re.fullmatch(r"revalidation-needed(?: \(was (.+)\))?", status)
            entries.append({"result": result, "text": finding, "status": "revalidation-needed" if flagged else status,
                            "prior_status": flagged[1] if flagged else None,
                            "flag_reason": reason if flagged else "", "notes": [] if flagged or not reason else [reason],
                            "checks_caveat": "", "notes_checks": "", "claim": claim, "claim_basis": basis[:-1]})
    path = state.with_name("findings.json")
    if entries:
        path.write_text(json.dumps({"schema": "awb-findings/1", "findings": entries}, indent=2) + "\n")
    else:
        path.unlink(missing_ok=True)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def project(tmp_path):
    for target, source in ASSETS.items():
        write(tmp_path, target, source.read_bytes())
    write(tmp_path, ".gitignore", "deliveries/\n")
    write(tmp_path, "README.md", "Active investigation: inv\n\nReleased packages are kept at: not yet recorded\n")
    write(tmp_path, "foundation/views/01_orders.sql", VIEW)
    write(tmp_path, "investigations/inv/settings.toml", SETTINGS)
    write(tmp_path, "investigations/inv/run.py", "x = 1\n")
    write(tmp_path, "investigations/inv/state.md", STATE.format(status="supported", reason=""))
    write(tmp_path, "data/parquet/orders/p1/part-0.parquet", b"parquet bytes")
    write(tmp_path, "data/parquet/orders/p1/publication.json", json.dumps({
        "inputs": [], "conversion_commit": "c1",
        "files": [{"path": "part-0.parquet", "bytes": 13,
                   "sha256": hashlib.sha256(b"parquet bytes").hexdigest()}]}))
    git(tmp_path, "init")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-m", "fixture")
    provenance = load(tmp_path / "src/provenance.py", "provenance_fixture")
    for result_id in ("r-001", "r-002"):
        provenance.record_evidence(
            tmp_path, "inv", result_id, views=["foundation/views/01_orders.sql"],
            publications=["data/parquet/orders/p1"], acquisitions=[],
            settings_path="investigations/inv/settings.toml",
            checks=[{"name": "rows", "outcome": "pass", "detail": "3 rows"}])
    write(tmp_path, "investigations/inv/evidence/r-001-export-checks.json", "[]\n")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-m", "evidence")
    draft = tmp_path / "deliveries/inv/pkg/draft"
    write(draft, "findings.md", FINDINGS)
    write(draft, "methodology.md", METHODOLOGY)
    write(draft, "charts/chart-1.csv", "Region,Closed late (%)\nWest,21\n")
    write(tmp_path, "investigations/inv/results/r-001.csv", RESULT)
    write(tmp_path, "investigations/inv/results/r-002.csv", "region\nW\n")
    write(tmp_path, "foundation/display.toml", CHART_DISPLAY)
    write(draft, "manifest.json", json.dumps({
        "investigation": "inv", "package": "pkg", "status": "draft",
        "revalidation_flags": "none", "inventory": [], "charts": [CHART_ENTRY],
        "results": [{"result_id": r, "evidence": f"investigations/inv/evidence/{r}.json", "question": q}
                    for r, q in QUESTIONS.items()]}))
    return tmp_path


def run(project, capsys, *argv):
    cli = load(project / "src/awb.py", "awb_cli_fixture")
    code = cli.main(list(argv))
    return code, json.loads(capsys.readouterr().out)


def manifest(project, where="draft"):
    return json.loads((project / "deliveries/inv/pkg" / where / "manifest.json").read_text())


def test_names_cover_project_records(project):
    draft = load(project / "src/packaging/draft.py", "draft_fixture")
    names, problems = draft.project_names(project, "inv", "pkg")
    assert problems == []
    assert {"orders_view", "regions_table", "main.regions_table", "parameters.minimum_count",
            "parameters.start", "results.r-001", "r-001", "r-002", "r-009"} <= set(names)
    assert not {"inv", "pkg", "parameters", "results", "start", "minimum_count", "recent", "read_parquet",
                "ordered_at", "orders_comment_name", "r-001-export-checks"} & set(names)
    hyphenated, _ = draft.project_names(project, "inv-2026", "churn-q3")
    assert {"inv-2026", "churn-q3"} <= set(hyphenated)


def test_toml_keys_fall_back_to_tomli_then_key_lines(project, monkeypatch):
    tomllib = pytest.importorskip("tomllib")
    draft = load(project / "src/packaging/draft.py", "draft_toml")
    text = SETTINGS.decode()
    monkeypatch.setitem(sys.modules, "tomllib", None)
    monkeypatch.setitem(sys.modules, "tomli", tomllib)
    assert draft._toml_keys(text) == {"parameters", "parameters.minimum_count", "parameters.start",
                                      "results", "results.r-001", "results.r-001.question",
                                      "results.r-002", "results.r-002.question"}
    monkeypatch.setitem(sys.modules, "tomli", None)
    assert {"parameters", "results.r-001", "minimum_count"} <= draft._toml_keys(text)
    write(project, "foundation/display.toml", "[columns]\n")
    with pytest.raises(ImportError, match="tomli"):
        draft.display_names(project)


def test_check_draft_rewrites_inventory_and_passes(project, capsys):
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0 and report["passed"] and "record" not in report
    assert (report["findings"], report["charts"], report["verify"], report["errors"]) == ([], [], [], [])
    assert report["questions"] == []  # r-002's question is wrapped across two lines and still matches
    assert report["inventory"] == {"rows": 5, "source": "rewritten"}
    assert report["start_here"] == "deliveries/inv/pkg/draft/START-HERE.md"
    record = manifest(project)
    assert [row["path"] for row in record["inventory"]] == [
        "START-HERE.md", "charts/chart-1.csv", "findings.md", "manifest.json", "methodology.md"]
    assert record["revalidation_flags"] == "none"
    assert datetime.fromisoformat(record["revised_at"]).utcoffset() is not None
    path = project / "deliveries/inv/pkg/draft/manifest.json"
    path.write_text(json.dumps({**record, "revised_at": "2026-01-01T00:00:00+00:00"}))
    run(project, capsys, "check-draft", "inv", "pkg")
    assert manifest(project)["revised_at"] == "2026-01-01T00:00:00+00:00"
    write(project / "deliveries/inv/pkg/draft", "methodology.md", METHODOLOGY + "Revised.\n")
    run(project, capsys, "check-draft", "inv", "pkg")
    assert manifest(project)["revised_at"] != "2026-01-01T00:00:00+00:00"
    assert sorted(p.name for p in (project / "deliveries/inv/pkg").iterdir()) == ["draft"]


def test_check_draft_reports_each_helper_problem(project, capsys):
    draft = project / "deliveries/inv/pkg/draft"
    write(draft, "findings.md", FINDINGS + "\nCounts come from orders_view, as inv/notes says.\n\n**Chart 2.** Line: cases\n"
          "\n### East held steady\n")
    (project / "investigations/inv/settings.toml").unlink()
    for path in (project / "investigations/inv/evidence").glob("r-00?.json"):
        path.unlink()
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and not report["passed"]
    assert report["findings"] == [{"line": 31, "kind": "name", "text": "orders_view"},
                                  {"line": 31, "kind": "path", "text": "inv/notes"}]
    assert report["charts"] == [{"chart": "Chart 2", "problem": "no chart file for this specification"},
                                {"chart": "Chart 2", "problem": "no **Data:** line under the specification"}]
    assert report["headings"] == [
        {"heading": "East held steady", "problem": "methodology.md has no ### section with this exact heading"}]
    assert report["markdown"] == []
    assert report["names_problems"] == [
        "no settings found: investigations/inv/settings.toml is absent and no evidence records a settings file"]
    assert report["verify"] == []


def test_check_draft_reports_outline_and_chart_spec_rows(project, capsys):
    draft = project / "deliveries/inv/pkg/draft"
    long = "Late orders rose in the west, the region with the most stores and the busiest carrier"
    write(draft, "findings.md", FINDINGS.replace("Horizontal bar", "Pie").replace("Closed late (%)", "Late share"))
    write(draft, "methodology.md", METHODOLOGY.replace("Late orders rose in the west", long))
    write(draft, "findings.md", (draft / "findings.md").read_text().replace("Late orders rose in the west", long))
    for argv in (("check-draft", "inv", "pkg"), ("check-draft", "inv", "pkg", "--verify-only")):
        code, report = run(project, capsys, *argv)
        assert code == 1 and not report["passed"]
        assert report["outline"] == [{"slide": long, "line": 12, "problem": "the headline has 16 words; keep it to 15"}]
        assert report["charts"] == [
            {"chart": "Chart 1", "problem": "names no chart form (Pie); open the specification with one of: "
                                            "Horizontal bar, Bar with intervals, Line, Column, Stacked bar, Scatter, "
                                            "Table"},
            {"chart": "Chart 1", "problem": "chart-1.csv has no column 'Late share', which **Data:** names"},
            {"chart": "Chart 1", "problem": "chart-1.csv column 'Closed late (%)' is named by no **Data:** role; "
                                            "name it, or export the chart without it"}]
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 1 and report["refused"] == "check-draft --verify-only does not pass"
    assert len(report["check"]["outline"]) == 1 and len(report["check"]["charts"]) == 3


def set_results(project, results):
    path = project / "deliveries/inv/pkg/draft/manifest.json"
    record = json.loads(path.read_text())
    if results is None:
        record.pop("results")
    else:
        record["results"] = results
    path.write_text(json.dumps(record))


NOT_REPEATED = ("methodology.md does not repeat this question verbatim in text that renders, within one paragraph "
                "or heading")


def test_check_draft_requires_each_question_in_methodology(project, capsys):
    draft = project / "deliveries/inv/pkg/draft"
    write(draft, "methodology.md", METHODOLOGY.split("Question (r-002)")[0])
    code, report = run(project, capsys, "export", "inv", "pkg", "--result", "r-001")
    assert code == 0 and report["questions"] == {"r-001": QUESTIONS["r-001"]}
    assert run(project, capsys, "check-draft", "inv", "pkg")[1]["passed"]
    assert run(project, capsys, "export", "inv", "pkg", "--result", "r-001", "--result", "r-002")[1]["written"]
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and not report["passed"] and report["questions"] == [
        {"result_id": "r-002", "question": QUESTIONS["r-002"],
         "problem": NOT_REPEATED}]
    write(draft, "methodology.md", METHODOLOGY.replace("Which regions close", "Which regions closed"))
    assert run(project, capsys, "check-draft", "inv", "pkg")[1]["questions"][0]["result_id"] == "r-002"
    write(draft, "methodology.md", METHODOLOGY)
    run(project, capsys, "check-draft", "inv", "pkg")
    no_question = "the manifest records no question for this result; run export, or copy its question " \
                  "from settings into a hand-added entry"
    for results, problems in (
            ([{"result_id": "r-001", "evidence": "investigations/inv/evidence/r-001.json"}],
             [{"result_id": "r-001", "problem": no_question}]),
            ([{"result_id": "r-001", "question": {"unknown": "evidence lacks question"}}],
             [{"result_id": "r-001", "problem": no_question}]),
            (None, [{"result_id": None, "problem": "the manifest records no results list; run export"}])):
        set_results(project, results)
        code, report = run(project, capsys, "release", "inv", "pkg")
        assert code == 1 and report["refused"] == "check-draft --verify-only does not pass"
        assert report["check"]["questions"] == problems
    assert not (project / "deliveries/inv/pkg/released").exists()


# Where methodology.md writes r-002's question, and whether the questions check finds it there.
QUESTION_PLACES = {
    "only in a comment block": ("<!-- Which regions close claims late? -->", False),
    "in a comment within a paragraph": ("Question (r-002): <!-- Which regions close claims late? --> to come.", False),
    "in a comment opened in a stray ](...)": ("Intro ](x<!--) Which regions close claims late? -->", False),
    "in a comment opened in what a \\ before a space keeps from being a target": (
        "See [a](x\\ <!--) Which regions close claims late? -->", False),
    "in fenced code": ("```\nWhich regions close claims late?\n```", False),
    "split over two paragraphs": ("Which regions close\n\nclaims late?", False),
    "reworded": ("Which regions closed claims late?", False),
    "wrapped": ("Question (r-002): Which regions\nclose claims\nlate?", True),
    "emphasized": ("Question (r-002): **Which regions** close _claims_ late?", True),
    "linked": ("Question (r-002): [Which regions](https://example.com/r-002) close claims late?", True),
    "escaped and referenced": ("Question (r-002): Which regions close claims late\\? See&#32;notes.", True),
    "in a code span": ("Question (r-002): `Which regions close claims late?`", True),
    "in a heading": ("#### Which regions close claims late?", True),
    "in a list item": ("- r-002: Which regions close\n  claims late?", True),
    "after a comment block on its line": ("<!-- r-002 --> Which regions close claims late?", True),
}


@pytest.mark.parametrize("place", QUESTION_PLACES)
def test_questions_check_reads_methodology_as_it_renders(project, place):
    draft = load(project / "src/packaging/draft.py", "draft_questions")
    directory = project / "deliveries/inv/pkg/draft"
    body, found = QUESTION_PLACES[place]
    write(directory, "methodology.md", METHODOLOGY.split("Question (r-002)")[0] + "\n" + body + "\n")
    record = json.loads((directory / "manifest.json").read_text())
    assert draft.question_problems(directory, record) == ([] if found else [
        {"result_id": "r-002", "question": QUESTIONS["r-002"],
         "problem": NOT_REPEATED}])


# A question holding a markup character, written exactly inside a code span, which shows it as written.
MARKUP_QUESTIONS = (
    "Which regions [excluding test] close late?",
    "Did ~5% of orders close late?",
    "Which _id values repeat?",
    "Is churn above 5*baseline?",
    "Which AT&amp;T orders close late?",
    "Which regions close late\\?",
)


@pytest.mark.parametrize("question", MARKUP_QUESTIONS)
def test_questions_check_matches_a_code_span_as_written(project, question):
    draft = load(project / "src/packaging/draft.py", "draft_markup_questions")
    directory = project / "deliveries/inv/pkg/draft"
    before = METHODOLOGY.split("Question (r-002)")[0]
    write(directory, "methodology.md", before + f"\nQuestion (r-002): `{question}`\n")
    record = json.loads((directory / "manifest.json").read_text())
    for entry in record["results"]:
        if entry["result_id"] == "r-002":
            entry["question"] = question
    assert draft.question_problems(directory, record) == []
    # Without the code span r-002 fails, so the pass above is the code span's.
    write(directory, "methodology.md", before + "\nQuestion (r-002): to come.\n")
    assert [row["result_id"] for row in draft.question_problems(directory, record)] == ["r-002"]


def test_questions_check_refuses_a_commented_question(project, capsys):
    # The issue's probe: a question only inside an HTML comment never renders, so check-draft fails.
    draft = project / "deliveries/inv/pkg/draft"
    write(draft, "methodology.md", METHODOLOGY.replace("Question (r-002): Which regions close\nclaims late?",
                                                      "<!-- Which regions close claims late? -->"))
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and [row["result_id"] for row in report["questions"]] == ["r-002"]
    # A question the manifest records with inline markup is compared as it renders, as methodology.md is.
    record = json.loads((draft / "manifest.json").read_text())
    record["results"][1]["question"] = "Which **regions** close claims late?"
    (draft / "manifest.json").write_text(json.dumps(record))
    write(draft, "methodology.md", METHODOLOGY)
    assert run(project, capsys, "check-draft", "inv", "pkg")[1]["questions"] == []


# Where methodology.md writes r-002's question beside an image, and whether the questions check finds it there.
# An image shows a picture: its text shows only when the image fails to load, or to a screen reader.
QUESTION_IMAGES = {
    "only in an image's text": ("![{q}](charts/renewals.png)", False),
    "only in the text of an image inside a link": ("[![{q}](charts/renewals.png)](https://example.com)", False),
    "split by an image": ("Which regions ![map](charts/map.png) close claims late?", False),
    "split by an image without text": ("Which regions ![](charts/map.png) close claims late?", False),
    "in a link's text": ("[{q}](charts/renewals.png)", True),
    "in prose": ("Question (r-002): {q}", True),
    "in prose beside an image": ("![Renewals by quarter](charts/renewals.png) Question (r-002): {q}", True),
    "in an image's text and in prose": ("![{q}](charts/renewals.png)\n\nQuestion (r-002): {q}", True),
    "in an image's text and in prose after it": ("![{q}](charts/renewals.png) Question (r-002): {q}", True),
    # A bracket in an autolink, or in a code span after an escaped backslash or backtick, closes nothing.
    "only in an image's text holding an autolink with ]": ("![{q} <https://example.com/a]>](charts/r.png)", False),
    "only in an image's text holding an autolink with [": ("![{q} <https://example.com/[>](charts/r.png)", False),
    "only in an image's text holding \\\\ and a code span with ]": ("![{q} C:\\\\`]`](charts/r.png)", False),
    "only in an image's text holding \\` and a code span with ]": ("![{q} \\``]`](charts/r.png)", False),
    "only in an image's text after an escaped backslash": ("\\\\![{q}](charts/renewals.png)", False),
    "only in an image's text holding an email autolink with `": ("![{q} <a`b@example.com>](charts/r.png) `", False),
    "only in an image's text holding a link whose target has ]": ("![{q} [source](https://e.com/a]) b](charts/r.png)", False),
    "only in an image's text holding a link whose title has ]": ("![{q} [source](https://e.com \"]\")](charts/r.png)", False),
    "only in the text of an image whose target nests parentheses": ("![{q}](charts/renewals(q3(final)).png)", False),
    "only in the text of an image whose target escapes a parenthesis": ("![{q}](charts/renewals\\(q3.png)", False),
    "only in the text of an image whose title escapes a quote": ("![{q}](charts/r.png \"the \\\"Q3\\\" view\")", False),
    "only in an image's text, after an autolink holding `": ("<https://example.com/`> ![{q}](charts/r.png) `", False),
    "in a code span showing an image's syntax, after an escaped `": ("\\``![{q}](charts/renewals.png)`", True),
    "beside an unclosed ![ and a link whose text holds a code span with ]": ("Intro ![ {q} [\\``]`](charts/r.png) tail.",
                                                                            True),
    "in a code span after an escaped backslash": ("C:\\\\`![{q}](charts/renewals.png)`", True),
    "in a code span showing an image's syntax": ("`![{q}](charts/renewals.png)`", True),
    "after an escaped !, which makes a link": ("\\![{q}](charts/renewals.png)", True),
    "in a reference image, which never resolves": ("![{q}][renewals]", True),
}


@pytest.mark.parametrize("place", QUESTION_IMAGES)
def test_questions_check_leaves_out_image_text(project, place):
    draft = load(project / "src/packaging/draft.py", "draft_image_questions")
    directory = project / "deliveries/inv/pkg/draft"
    body, found = QUESTION_IMAGES[place]
    write(directory, "methodology.md", METHODOLOGY.split("Question (r-002)")[0] + "\n"
          + body.format(q=QUESTIONS["r-002"]) + "\n")
    record = json.loads((directory / "manifest.json").read_text())
    assert draft.question_problems(directory, record) == ([] if found else [
        {"result_id": "r-002", "question": QUESTIONS["r-002"], "problem": NOT_REPEATED}])


def test_other_checks_still_read_image_text(tmp_path):
    # Only the questions check leaves an image's text out; for the names scan, reading it is the stricter choice.
    draft = load(ASSETS["src/packaging/draft.py"], "draft_image_names")
    path = tmp_path / "findings.md"
    path.write_text("![Late orders in orders_view by region](charts/chart-1.csv)\n")
    assert [(row["kind"], row["text"]) for row in draft.check_findings(path)] == [("identifier", "orders_view")]
    assert "orders_view" in draft._read_view(path)[0][0].plain


def test_check_draft_help_and_references_agree_on_the_rendered_reading(project, capsys):
    cli = load(project / "src/awb.py", "awb_cli_help")
    with pytest.raises(SystemExit):
        cli.main(["check-draft", "--help"])
    help_text = " ".join(capsys.readouterr().out.split())
    assert "Every check but numbers reads the narratives as they render." in help_text
    assert "a question in a comment, fenced code, or an image's text does not count, nor does one running across an " \
           "image" in help_text
    assert "without the comments and fenced code the rendered reading drops" in help_text
    helpers = (SKILLS / "awb-package/references/helpers.md").read_text()
    assert "Every draft check but `numbers` reads" in helpers and "`questions` rows" in helpers
    assert "A question only in a comment, in fenced code, or in an image's text does not count" in helpers
    assert "a question cannot run across an image" in helpers
    assert "A comment is what the reading above drops" in helpers
    source = ASSETS["src/packaging/draft.py"].read_text()
    assert "# Every draft check but numbers reads the narratives (findings.md, methodology.md, and methodology-note.md" in source


def set_flags(project, flags):
    path = project / "deliveries/inv/pkg/draft/manifest.json"
    record = json.loads(path.read_text())
    record["revalidation_flags"] = flags
    path.write_text(json.dumps(record))


def test_check_draft_reports_unmatched_flags(project, capsys):
    write(project, "investigations/inv/state.md", FLAGGED)
    for argv in ((), ("--verify-only",)):
        code, report = run(project, capsys, "check-draft", "inv", "pkg", *argv)
        assert code == 1 and not report["passed"] and report["unmatched_flags"] == [FLAG]
        assert report["errors"] == [] and report["verify"] == []
    set_flags(project, [{**FLAG, "reason": "an older reason", "represented_in": "none"}])
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and report["unmatched_flags"] == [FLAG]
    set_flags(project, [{**FLAG, "represented_in": ["findings: Late orders"], "disposition": "none"}])
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0 and report["passed"] and report["unmatched_flags"] == []
    write(project, "investigations/inv/state.md", "# Current investigation state\n")
    code, report = run(project, capsys, "check-draft", "inv", "pkg", "--verify-only")
    assert code == 1 and report["unmatched_flags"] is None
    assert any("no Current findings table" in error for error in report["errors"])


def test_check_draft_and_release_refuse_malformed_flag_entries(project, capsys):
    path = project / "deliveries/inv/pkg/draft/manifest.json"
    record = json.loads(path.read_text())
    del record["revalidation_flags"]
    path.write_text(json.dumps(record))
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and report["unmatched_flags"] == [] and report["flag_entries"] == [
        {"finding": None, "problem": "revalidation_flags is missing; rerun export"}]
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 1 and report["refused"] == "check-draft --verify-only does not pass"
    assert report["check"]["flag_entries"][0]["problem"] == "revalidation_flags is missing; rerun export"
    write(project, "investigations/inv/state.md", FLAGGED)
    entry_problem = "entry is not an object with a text finding and reason; rerun export"
    for flags, rows in [
            ({"finding": "x"}, [{"finding": None,
                                 "problem": "revalidation_flags is not none or a list; rerun export"}]),
            (["x", {"finding": "F2", "represented_in": "none"}],
             [{"finding": None, "problem": entry_problem}, {"finding": "F2", "problem": entry_problem}]),
            ([{**FLAG, "represented_in": [], "disposition": "none"}],
             [{"finding": FLAG["finding"], "problem": PLACES_PROBLEM}]),
            # A non-text reason or finding is reported, never hashed into a crash.
            ([{"finding": FLAG["finding"], "reason": [], "represented_in": "none"},
              {"finding": {"a": 1}, "reason": FLAG["reason"], "represented_in": "none"}],
             [{"finding": FLAG["finding"], "problem": entry_problem}, {"finding": None, "problem": entry_problem}]),
            ([{**FLAG, "represented_in": [" "], "disposition": "omit"}],
             [{"finding": FLAG["finding"], "problem": PLACES_PROBLEM}])]:
        set_flags(project, flags)
        for command in ("check-draft", "release"):
            code, report = run(project, capsys, command, "inv", "pkg")
            check = report if command == "check-draft" else report["check"]
            assert code == 1 and not check["passed"] and check["flag_entries"] == rows
    set_flags(project, [{**FLAG, "represented_in": ["chart 1"], "disposition": "revalidate"}])
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0 and report["flag_entries"] == []
    assert not (project / "deliveries/inv/pkg/released").exists()


def set_manifest(project, **fields):
    path = project / "deliveries/inv/pkg/draft/manifest.json"
    path.write_text(json.dumps({**json.loads(path.read_text()), **fields}))


TRACED = deck("""### Late orders rose in the west

- West closed 21.3% of orders late, against 2.7% in the east.
- Ten checks covered 3 rows; regions needed at least 5 orders.
- Missing regions were 0.0% of rows, and 1,240 orders were reviewed.

""" + CHART_SPEC + """
**Notes:** The west leads the regions.
""").replace("# Order quality\n", "# Order quality, January to June 2026\n")


# The problem a numbers row gives for each rule that leaves its number untraced.
ALLOW = "or list its text in the manifest's allowed_numbers with the reason"
NOT_RECORDED = f"no represented result records this number at its written precision; correct it, {ALLOW}"
YEAR_COUNT = ("read as a count: a year is skipped only after a month name, alone in parentheses, or after a word "
              f"such as in or since where its period ends; reword it, such as ending the date with a comma, {ALLOW}")
JOINED = ("digits joined by dots, commas, slashes, or colons read as one number with no single value, so it never "
          f"traces; write each number apart, {ALLOW}")
ON_EDGE = ("a recorded value lies exactly on the edge of this number's rounding, as when a value the query rounded "
           f"is rounded again, so it does not trace; save the result at full precision, {ALLOW}")


def test_check_draft_traces_narrative_numbers(project, capsys):
    draft = project / "deliveries/inv/pkg/draft"
    write(project, "investigations/inv/results/r-001.profile.json", json.dumps(
        {"row_count": 2, "columns": {"region": {"dtype": "object", "null_rate": 0.0, "distinct_count": 2}}}))
    write(project, "investigations/inv/results/r-002.csv", "orders\n1240\n")
    set_manifest(project, results=[{"result_id": r, "evidence": f"investigations/inv/evidence/{r}.json",
                                    "question": QUESTIONS[r]} for r in ("r-001", "r-002")])
    # Table cells rounded, a check detail, a setting, a profile rate as a percent, a thousands separator.
    write(draft, "findings.md", TRACED)
    write(draft, "methodology.md", METHODOLOGY + "\nSettings `minimum_count = 7` (r-001), release 002, as of "
          "2026-06-30.\n\n- West closed 21.3% late.\n")
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0 and report["passed"] and report["numbers"] == [] and report["numbers_problems"] == []
    # A number no represented result produced fails with its file and line, in both modes and at release.
    write(draft, "findings.md", TRACED.replace("21.3%", "23.1%"))
    write(draft, "methodology.md", METHODOLOGY + "\nAbout 40 stores.\n")
    rows = [{"file": "findings.md", "line": 14, "text": "23.1%", "problem": NOT_RECORDED},
            {"file": "methodology.md", "line": 13, "text": "40", "problem": NOT_RECORDED}]
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and not report["passed"] and report["numbers"] == rows
    code, report = run(project, capsys, "check-draft", "inv", "pkg", "--verify-only")
    assert code == 1 and report["numbers"] == rows and report["verify"] == []
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 1 and report["refused"] == "check-draft --verify-only does not pass"
    assert report["check"]["numbers"] == rows and not (project / "deliveries/inv/pkg/released").exists()
    # An allowed number passes with its reason; a represented result's table is what makes a number trace.
    set_manifest(project, allowed_numbers=[{"text": "23.1%", "reason": "the prior release's figure"},
                                           {"text": "40", "reason": "store count from the owner"}])
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0 and report["passed"] and report["numbers"] == []
    allowed = manifest(project)["allowed_numbers"]
    set_manifest(project, charts="none")  # so r-001, which the chart file serializes, can leave the represented set
    code, _ = run(project, capsys, "export", "inv", "pkg", "--result", "r-002")
    assert code == 0 and manifest(project)["allowed_numbers"] == allowed  # export keeps the hand-recorded field
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and {"file": "findings.md", "line": 14, "text": "2.7%", "problem": NOT_RECORDED} in report["numbers"]


def test_check_draft_reports_number_problems(project, capsys):
    (project / "investigations/inv/results/r-002.csv").unlink()
    for fields, problems in [
            ({"allowed_numbers": [{"text": "40", "reason": " "}, "40"]},
             ["allowed_numbers entry 1 is not {text, reason} with both filled in",
              "allowed_numbers entry 2 is not {text, reason} with both filled in"]),
            ({"allowed_numbers": {"text": "40"}}, ["allowed_numbers is not none or a list of {text, reason}"]),
            ({"results": [{"result_id": "../r-001"}]}, ["manifest.json results is not a list of result_id entries; "
                                                         "rerun export"]),
            ({"results": "none"}, ["manifest.json results is not a list of result_id entries; rerun export"]),
            ({"results": [{"result_id": "r-002"}]},
             ["investigations/inv/results/r-002.csv is missing; numbers from r-002 cannot be traced"])]:
        set_manifest(project, allowed_numbers="none",
                     results=[{"result_id": "r-001", "evidence": "investigations/inv/evidence/r-001.json"}])
        set_manifest(project, **fields)
        code, report = run(project, capsys, "check-draft", "inv", "pkg")
        assert code == 1 and report["numbers"] == [] and report["numbers_problems"] == problems
    write(project, "investigations/inv/results/r-002.profile.json", "{not json")
    write(project, "investigations/inv/results/r-002.csv", "n\n1\n")
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and report["numbers_problems"][0].startswith(
        "investigations/inv/results/r-002.profile.json: unreadable")


def test_check_numbers_reads_formats(tmp_path):
    draft = load(ASSETS["src/packaging/draft.py"], "draft_numbers")
    values = sorted({Decimal(v) for v in ("21.349", "0.1", "0.15", "3", "4213000", "12480", "1240", "0.5")})
    path = tmp_path / "findings.md"
    path.write_text("""# Orders, January to June 2026

- n = 1,240 as of June 30, 2026, 30 June 2026, 2026-06-30T14:05:00-04:00, 6/30/2026, and 14:05:30.
- West 21% and 21.35; between 10-15% or 10 and 15%; 3x the east; $4.2M and 12.5 thousand; 0.5 percentage points.
- Release 002, Q-3, chart-1, v1.2.3, COVID-19, FY2026, and Charts 1.
1. A list marker[^2], `code 77`, and [the 7 guide](notes/88.md).
<!-- 66 -->
```
44
```
- Untraced: 21.4%, 1,250, 4.3M, 16%, 2, 3/4 of stores, and 9:30.
- Skipped: in 2026, Q3 2026, Charts 2 and 3, 9:30am, 9:30 a.m., June 5, June 5-7, 2026, Monday, June 5, 14:05, (2025).
- Traced: 1.24e3, 4.213e6, 1.5e-1 and 5e-1. Untraced: a hash 12345e6, 1e-5, 1.5e6, June 77 orders, 1950 orders.
""")
    rule = {"9:30": JOINED, "1950": YEAR_COUNT}
    assert draft.check_numbers(path, values) == [
        {"file": "findings.md", "line": 6, "text": "7", "problem": NOT_RECORDED},
        *({"file": "findings.md", "line": 11, "text": t, "problem": rule.get(t, NOT_RECORDED)}
          for t in ("21.4%", "1,250", "4.3M", "16%", "2", "4", "9:30")),
        *({"file": "findings.md", "line": 13, "text": t, "problem": rule.get(t, NOT_RECORDED)}
          for t in ("12345e6", "1e-5", "1.5e6", "77", "1950"))]
    assert draft.check_numbers(path, values, allowed={"7", "2", "16%", "1,250", "4.3M", "21.4%", "4", "9:30",
                                                      "12345e6", "1e-5", "1.5e6", "77", "1950"}) == []


# Each narrative a review probed in rounds 1 to 4, and each case the fail-safe reading settles, with the numbers
# check_numbers reports for it ([] is all skipped or traced), against recorded values [0.5] unless a row gives its own values or allowed texts.
# Reading fails safe, so a number in a doubtful context is reported, never skipped.
SHARE, FIXTURE, SCALED = {"values": ["0.213"]}, {"values": ["21.349", "2.675", "10", "8"]}, \
    {"values": ["4.2", "4.2e6", "0.00001", "1.2e9"]}
REVIEWED_PROBES = [
    ("Probability is 1e-5.", ["1e-5"]), ("Revenue is 1.5e6.", ["1.5e6"]), ("Revenue is 1.5E+06.", ["1.5E+06"]),
    ("12e3 orders", ["12e3"]), ("12.5e3", ["12.5e3"]),  # any mantissa: a hash such as 12345e6 is reported too
    ("Failure probability was .5e-3.", [".5e-3"], {"values": ["0.5", "3"]}),  # one number, never its pieces
    ("Failure probability was 5.e-3.", ["5.e-3"], {"values": ["5", "3"]}),
    ("Failure rate was .5e-3.", [], {"values": ["0.0005"]}), ("Failure rate was 5.e-3.", [], {"values": ["0.005"]}),
    ("In June 77 orders were lost.", ["77"]), ("in June 31 orders", ["31"]), ("June 5, 77 orders", ["77"]),
    ("on June 5 77 orders", ["5", "77"]), ("5 June 77 orders", ["5", "77"]),  # a date ends at punctuation
    ("June 5 we met", ["5"]), ("On June 5, 2026 we met", ["2026"]), ("From June 1, 2026 to June 30, 2026.", []),
    ("As shown in Chart 1, 77 orders were late.", ["77"]), ("As shown in Chart 1; 77 orders were late.", ["77"]),
    ("Chart 1, 2 regions led.", ["2"]), ("See Chart 2 and 40 stores.", ["40"]), ("Chart 3 - 12 regions", ["12"]),
    ("Chart 1: 77 orders", ["77"]), ("Charts 1 and 4 show 77 orders", ["4", "77"]), ("Charts 1 and 4 show it", ["4"]),
    ("Charts 1, 2, and 3 show it", ["2", "3"]), ("Charts 2-3 show it", ["3"]), ("Charts 2-3", []),
    ("Charts 1 and 4.", []), ("Charts 1, 40 stores", ["40"]), ("Charts 1 and 2, 40 stores", ["40"]),
    ("Charts 4,5 show it", ["4,5"]),
    ("in 2025, 2030 orders shipped", ["2030"]), ("since 2019, and 2020", []), ("between 2023 and 2024", []),
    ("in 2023, 2024 and 2025", []), ("We reviewed 1950 orders and 2,000 stores", ["1950", "2,000"]),
    ("an increase in 2000 orders", ["2000"]), ("between 1950 and 2000 stores were affected", ["1950", "2000"]),
    ("late 2000 orders were found", ["2000"]), ("in 2025 and 2026 orders", ["2025", "2026"]), ("mid-2025.", []),
    ("In June 2026 orders were lost", []), ("Q3 2025 revenue", ["2025"]), ("In Q3 2000 orders were late", ["2000"]),
    ("Revenue fell in Q3 2025.", []), ("FY 2024 and 2025 orders", ["2024", "2025"]), ("FY 2024 and 2025.", []),
    ("Late orders (2025) exceeded the target.", []),
    ("in 2000\norders were lost", ["2000"]),  # a line wrap continues the sentence
    ("Late orders rose 3 points over 2025.", ["3", "2025"]), ("compared with 2024", ["2024"]),
    ("the 2025 baseline", ["2025"]), ("2026 H1", ["2026"]), ("Week 23", ["23"]),
    ("Python 3.12 and DuckDB 1.1.3", ["3.12"]), ("Python 3.11", ["3.11"]), ("Python 3.12.1", []), ("3.12", ["3.12"]),
    ("host 10.0.0.1", []), ("1.234.567 orders", ["1.234.567"]), ("1.234,5 orders", ["1.234,5"]),
    ("?id=42", ["42"]), ("## 2. Sources", []), ("1. 77 orders", ["77"]),
    ("The count rose to\n77. Orders then fell.", ["77"]),  # 77. continues a paragraph; only 1. starts a list
    # Inside a list item or a quote, an indented number wraps the item's text unless a list item above has its indent.
    ("- Orders in the West rose to\n  77. Returns fell.", ["77"]), ("* Orders rose to\n  77. Then fell.", ["77"]),
    ("1. Orders in the West rose to\n   77. Returns fell.", ["77"]), ("> - The count rose to\n>   77. Orders then fell.", ["77"]),
    ("- Orders rose\n  steadily to\n  77. Then fell.", ["77"]), ("- Orders rose to\n77. Then fell.", []),
    ("  1. Orders rose\n  2. Orders fell", []), ("- Orders\n  - rose\n  77. Then fell.", []), ("- Orders\n  1. rose", []),
    ("1. Orders rose\n   steadily\n2. Orders fell", []),
    ("opened at 9:30am", []), ("opened at 14:05", []), ("a 1:20 ratio", ["1:20"]),
    ("-21.3%", ["21.3%"]), ("10–15 percent", ["10", "15 percent"]),
    ("values 1,2,3 and 4, 5", ["1,2,3", "4", "5"]), ("21,3%", ["21,3%"]), ("3/4 of stores", ["3", "4"]),
    ("Total,77 orders were late.", ["77"]), ("Total, 77 orders were late.", ["77"]), ("Total;77", ["77"]),
    ("Total:77", ["77"]), ("(77 orders)", ["77"]), ("Rates: West,21.3%; East,2.7%.", ["21.3%", "2.7%"]),
    ("West/21.3%", ["21.3%"]), ("sentence.5 stores", ["5"]), ("_77 orders_", ["77"]), ("late_77", []),
    ("Source: results/r-001-77.csv.", []), ("file data/run-2-45.parquet", []), ("**results/r-001-77.csv**", []),
    ("./run-2-45.csv and results/12-45.csv", []), ("ORD-123-45 and ORD-123", []), ("COVID-19", []),
    ("COVID-19-related 77 orders", ["77"]), ("top-10 stores", ["10"]), ("45/day", ["45"]),
    ("1st place", ["1st"], {"values": []}), ("77th percentile", ["77th"]), ("100ms", ["100ms"]),
    ("1 000 000 orders", ["1 000 000"], {"values": ["1", "0", "1000000"]}), ("5½", ["5½"], {"values": ["5"]}), ("30d window", [], {"values": ["30"]}),
    ("USD4.2M", [], {"values": ["4.2e6"]}),
    ("Late rate (%) <- r-001.late_rate", []), ("chart-1: Late rate (%) <- r-001.late_rate", []),
    ("Share was 21.3 percent.", [], SHARE), ("Share was 21.3  percent.", [], SHARE),
    ("Share was 21.3\npercent.", [], SHARE), ("Share was 21.3 %.", [], SHARE), ("> Share was 21.3\n> percent.", [], SHARE),
    ("> Orders rose in 2025\n> orders 77", ["2025", "77"]), ("> The count rose to\n> 77. Orders fell.", ["77"]),
    ("Revenue was 4.2  million.", [], SCALED), ("Revenue was 1.2 bn.", [], SCALED),
    ("Revenue is 4,200,000.", [], SCALED), ("The threshold is 0.00001.", [], SCALED),
    # Both narratives' numbers are recorded, so the check passes them; whether they agree is the manual item.
    ("### Late orders rose in the west\n\n- West closed 21.3% of orders late.", [], FIXTURE),
    ("### Late orders rose in the west\n\nWest closed 2.7% of orders late (r-001).", [], FIXTURE),
    ("Late orders rose 3 points over 2025; 2025 orders. Week 23 and 23 stores.", ["2025", "23"],
     {"values": ["3"], "allowed": {"over 2025", "Week 23"}}),
    ("Week 23 ran on Python 3.12, up 3 points over 2025; 23 stores and 2025 orders.", ["3", "23", "2025"],
     {"values": [], "allowed": {"Week 23", "Python 3.12", "over 2025"}}),
    ("compared with 2024, the 2025 baseline, 2026 H1", [],
     {"values": [], "allowed": {"compared with 2024", "the 2025 baseline", "2026 H1"}}),
    ("140 and 40%", ["140", "40%"], {"allowed": {"40"}}), ("Week 230", ["230"], {"allowed": {"Week 23"}}),
    # A row's text copied exactly covers its number across extra spaces or a wrap; a bare number does not cover its unit.
    ("Share was 18.2\npercent last year.", [], {"values": [], "allowed": {"18.2 percent"}}),
    ("Share was 18.2  percent last year.", [], {"values": [], "allowed": {"18.2 percent"}}),
    ("> Share was 18.2\n> percent.", [], {"values": [], "allowed": {"18.2 percent"}}),
    ("- Share was 18.2\n  percent.", [], {"values": [], "allowed": {"18.2 percent"}}),
    ("Share was 18.2\npercent this year.", ["18.2 percent"], {"values": [], "allowed": {"18.2"}}),
    ("Ran in Week\n23 of the year.", [], {"values": [], "allowed": {"Week 23"}}),
    # Ordinary notation (issue #88): two numbers joined by one slash are two numbers, each traced; a 24-hour time;
    # a year right after a month name, full or three letters, or alone in parentheses.
    ("Zones 264/265 led.", [], {"values": ["264", "265"]}), ("Zones 264/266 led.", ["266"], {"values": ["264", "265"]}),
    ("368/53.5% of orders", [], {"values": ["368", "0.535"]}), ("53.5%/368 of orders", ["53.5"], {"values": ["368", "0.535"]}),
    ("1/2/3 of orders", ["1/2/3"]), ("1,240/1,300 orders", [], {"values": ["1240", "1300"]}),
    ("at 00:00, 09:15, and 23:59", []), ("at 24:00", ["24:00"]), ("at 18:60", ["18:60"]), ("at 9:30 daily", ["9:30"]),
    ("3,18:00", ["3,18:00"]), ("a 12:20 ratio", []),  # a ratio written as a 24-hour time reads as one
    ("Dec 2011 sales", []), ("Dec. 2011 sales", []), ("September 2011 sales", []), ("Sept 2011 sales", ["2011"]),
    ("december 2011 sales", ["2011"]), ("(2019)", []), ("(Smith, 2019)", ["2019"]), ("(2019 orders)", ["2019"]),
    ("orders(2019)", ["2019"]), ("Dec 2011/2012 sales", ["2011", "2012"]),
    # A recorded value on the edge of a number's rounding does not trace: 0.5245 rounds to 52.5% only once rounded again.
    ("Share was 52.5%.", ["52.5%"], {"values": ["0.5245"]}), ("Share was 52.4%.", ["52.4%"], {"values": ["0.5245"]}),
    ("Share was 52.45%.", [], {"values": ["0.5245"]}), ("Share was 52%.", [], {"values": ["0.5245"]}),
]


def test_check_numbers_reviewed_probes(tmp_path):
    draft = load(ASSETS["src/packaging/draft.py"], "draft_probes")
    path = tmp_path / "findings.md"
    found = {}
    for line, _, *options in REVIEWED_PROBES:
        option = options[0] if options else {}
        path.write_text(line + "\n")
        values = sorted(Decimal(value) for value in option.get("values", ["0.5"]))
        found[line] = [row["text"] for row in draft.check_numbers(path, values, allowed=option.get("allowed", ()))]
    assert found == {line: expected for line, expected, *_ in REVIEWED_PROBES}


# Each recorded text a review probed, with the magnitudes it records.
REVIEWED_RECORDED = [
    ("Revenue is $4.2M.", ["4.2", "4.2e6"]), ("threshold = 1e-5", ["0.00001"]), ("results/r-001-77.csv", []),
    ("ORD-123", []), ("1e999999999999999999", ["1e999999999999999999"]), ("9e9999999999999999999", []),
    ("sNaN", []), ("Infinity", []), ("-0", ["0"]), ("1,5", []), ("Total,77", ["77"]),
    ("threshold = .5e-3", ["0.0005"]), ("rate 5.e-3", ["0.005"]),
]


def test_recorded_text_reviewed_probes():
    draft = load(ASSETS["src/packaging/draft.py"], "draft_recorded_probes")
    for text, expected in REVIEWED_RECORDED:
        found = set()
        draft._magnitudes(text, found)
        assert sorted(found) == sorted(Decimal(value) for value in expected), text


def test_check_numbers_skips_a_doi(tmp_path):
    draft = load(ASSETS["src/packaging/draft.py"], "draft_doi")
    path = tmp_path / "methodology.md"
    path.write_text("Data: UCI repository (DOI 10.24432/C5CG6D), doi:10.1000.10/182-x and "
                    "https://doi.org/10.24432/C5CG6D; 10.24432/C5CG6D.\n"
                    "Not a DOI: 10.123/abc, 10.24432 alone, and 1.24432/C5.\n"
                    "Fuel cost 10.2500/litre in March; doi: 10.1000/xyz is a paper.\n"
                    "Cost was 10.2500/1000 litres; ratio 10.12345/67.8 held.\n"
                    "See DOI 10.24432/C5CG6D,478 rows, and 10.24432/C5CG6D;12 more; cell 10.1016/j.cell.2009.01.002.\n")
    assert [(row["line"], row["text"]) for row in draft.check_numbers(path, [])] == [
        (2, "10.123"), (2, "10.24432"), (2, "1.24432"), (3, "10.2500"), (4, "10.2500"), (4, "1000"), (4, "10.12345"),
        (4, "67.8"), (5, "478"), (5, "12")]


def test_provenance_gaps_are_unknown_objects_and_unread_requirements():
    draft = load(ASSETS["src/packaging/draft.py"], "draft_gaps")
    record = {
        "analytical_settings": {"path": "investigations/inv/settings.toml", "content": {
            "parameters": {"pickup": "unknown_pickup", "label": "Unknown region"},
            "results": {"r-001": {"question": "Unknown pickups?",
                                  "validation": {"required_columns": ["unknown_pickup"]}}}}},
        "producing_commit": {"unknown": "not a git repository"},
        "results": [{"result_id": "r-001", "runtime": {"packages": {"duckdb": "unknown"},
                                                       "unread_requirements": ["requirements.txt:2: -e ."]}}],
        "inventory": [{"unknown": "skipped field"}]}
    assert draft.provenance_gaps(record) == [
        {"field": "producing_commit", "reason": "not a git repository"},
        {"field": "results[0].runtime.unread_requirements[0]",
         "reason": "requirements not read, packages unrecorded: requirements.txt:2: -e ."}]


def test_check_numbers_reads_ordinary_notation(tmp_path):
    draft = load(ASSETS["src/packaging/draft.py"], "draft_notation")
    path = tmp_path / "findings.md"
    path.write_text("- Mean fares were 54.8/57.6 at 18:00 and 18:59.\n- December 2011 is the last month; 41 trips.\n")
    values = sorted(Decimal(v) for v in ("54.8", "57.6"))
    assert draft.check_numbers(path, values) == [
        {"file": "findings.md", "line": 2, "text": "41", "problem": NOT_RECORDED}]
    # Each half is traced alone, so a half no result records is still a row.
    assert [(row["line"], row["text"]) for row in draft.check_numbers(path, values[:1])] == [(1, "57.6"), (2, "41")]


def test_numbers_rows_name_the_rule_that_applied(tmp_path):
    draft = load(ASSETS["src/packaging/draft.py"], "draft_rules")
    path = tmp_path / "methodology.md"
    path.write_text("About 40 stores.\nOpened at 9:30 daily.\nShare was 52.5%.\nWe reviewed 1950 orders.\n")
    assert [(row["text"], row["problem"]) for row in draft.check_numbers(path, [Decimal("0.5245")])] == [
        ("40", NOT_RECORDED), ("9:30", JOINED), ("52.5%", ON_EDGE), ("1950", YEAR_COUNT)]
    assert all("allowed_numbers" in problem for problem in draft._UNTRACED.values())


def test_check_numbers_allowed_phrases_and_precision(tmp_path):
    draft = load(ASSETS["src/packaging/draft.py"], "draft_phrases")
    path = tmp_path / "methodology.md"
    path.write_text("Week 23 ran on Python 3.12, up 3 points over 2025; 23 stores and 2025 orders.\n")
    assert [row["text"] for row in draft.check_numbers(path, [], allowed={"Week 23", "Python 3.12", "over 2025"})] \
        == ["3", "23", "2025"]
    assert [row["text"] for row in draft.check_numbers(path, [], allowed={"23", "3.12", "3", "2025"})] == []
    for text in ("Share was 23.1\npercent.\n", "Share was 23.1  percent.\n", "Share was 23.1 \n  percent.\n"):
        path.write_text(text)  # the row's text, copied exactly, covers it after a wrap or extra spaces
        assert [row["text"] for row in draft.check_numbers(path, [])] == ["23.1 percent"]
        assert draft.check_numbers(path, [], allowed={"23.1 percent"}) == []
    path.write_text("Share 0.12345678901234567890123456789, or 1.2345678901234567890123456789e-1.\n")
    assert draft.check_numbers(path, [Decimal("0.12345678901234567890123456789")]) == []
    assert [row["text"] for row in draft.check_numbers(path, [Decimal("0.1234567890123456789012345679")])] == [
        "0.12345678901234567890123456789", "1.2345678901234567890123456789e-1"]  # 1E-29 away: outside the rounding


def test_recorded_values_reads_whole_cells_and_quantities(tmp_path):
    draft = load(ASSETS["src/packaging/draft.py"], "draft_recorded")
    write(tmp_path, "investigations/inv/results/r-001.csv",
          "customer_hash,orders,label,source\n4e1234567,3,ORD-123,results/r-001-77.csv\n")
    # settings content is parsed TOML, as awb_provenance records it.
    write(tmp_path, "investigations/inv/evidence/r-001.json", json.dumps(
        {"checks": [{"detail": "Revenue is $4.2M on 2026-06-30"}], "producing_commit": "1234567", "notes": "run 9",
         "settings": {"path": "settings.toml", "bytes": 120, "content": {
             "parameters": {"threshold": 1e-5, "start": "2026-01-01", "flag": True},
             "results": {"r-001": {"window_days": 30}}}}}))
    values, problems = draft.recorded_values(tmp_path, "inv", [{"result_id": "r-001"}])
    assert problems == [] and values == sorted(  # no 123 from ORD-123, no 77 from the path, no overflow
        Decimal(v) for v in ("3", "4e1234567", "4.2", "4.2e6", "0.00001", "30"))
    path = tmp_path / "findings.md"
    path.write_text("Revenue was 4,200,000 against a threshold of 0.00001.\n")
    assert draft.check_numbers(path, values) == []


def test_recorded_values_keep_every_json_digit(tmp_path):
    # Profile and evidence fractions are read as written, not through a binary float.
    draft = load(ASSETS["src/packaging/draft.py"], "draft_exact_json")
    write(tmp_path, "investigations/inv/results/r-001.csv", "label\nwest\n")
    write(tmp_path, "investigations/inv/results/r-001.profile.json",
          '{"value": 0.12345678901234567890123456789, "rate": 0.21300000000000001, "rows": 12345678901234567890}')
    write(tmp_path, "investigations/inv/evidence/r-001.json",
          '{"checks": [{"detail": {"share": 0.30000000000000004}}], "settings": {"content": {"cut": 1e-30}}}')
    values, problems = draft.recorded_values(tmp_path, "inv", [{"result_id": "r-001"}])
    assert problems == [] and values == sorted(Decimal(v) for v in (
        "0.12345678901234567890123456789", "0.21300000000000001", "12345678901234567890", "0.30000000000000004",
        "1e-30"))
    path = tmp_path / "findings.md"
    path.write_text("Shares 0.12345678901234567890123456789 and 0.21300000000000001.\n")
    assert draft.check_numbers(path, values) == []
    path.write_text("Shares 0.12345678901234568000000000000 and 0.21300000000000002.\n")
    assert [row["text"] for row in draft.check_numbers(path, values)] == [
        "0.12345678901234568000000000000", "0.21300000000000002"]


def test_verify_only_never_writes(project, capsys):
    run(project, capsys, "check-draft", "inv", "pkg")
    before = (project / "deliveries/inv/pkg/draft/manifest.json").read_bytes()
    write(project / "deliveries/inv/pkg/draft", "methodology.md", METHODOLOGY + "Revised.\n")
    code, report = run(project, capsys, "check-draft", "inv", "pkg", "--verify-only")
    assert code == 1 and report["inventory"]["source"] == "recorded"
    assert [(d["path"], d["kind"]) for d in report["verify"]] == [
        ("methodology.md", "size"), ("methodology.md", "checksum")]
    assert (project / "deliveries/inv/pkg/draft/manifest.json").read_bytes() == before
    assert sorted(p.name for p in (project / "deliveries/inv/pkg").iterdir()) == ["draft"]


def test_missing_manifest_runs_other_checks(project, capsys):
    draft = project / "deliveries/inv/pkg/draft"
    (draft / "manifest.json").rename(draft / "manifest.yaml")
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and "manifest" not in report
    assert report["findings"] == [] and report["charts"] == [] and report["verify"] is None
    assert report["errors"] == ["manifest: no manifest at deliveries/inv/pkg/draft/manifest.json; run export first"]


def test_export_results_records_provenance_only(project, capsys):
    head = git(project, "rev-parse", "HEAD")
    producing = json.loads((project / "investigations/inv/evidence/r-001.json").read_text())["producing_commit"]
    (project / "deliveries/inv/pkg/draft/manifest.json").unlink()
    chart = (project / "deliveries/inv/pkg/draft/charts/chart-1.csv").read_bytes()
    write(project, "investigations/inv/settings.toml", STALE_SETTINGS)
    code, report = run(project, capsys, "export", "inv", "pkg", "--result", "r-001", "--result", "r-002")
    assert code == 0 and report["written"] and report["created"] and report["export_checks"]["results"] == 0
    record = manifest(project)
    assert (record["investigation"], record["package"], record["status"]) == ("inv", "pkg", "draft")
    assert record["producing_commit"] == producing != head
    assert record["producing_uncommitted_changes"] == "none"
    assert [v["results"] for v in record["inputs"]["views"]] == [["r-001", "r-002"]]
    assert record["inputs"]["publications"][0]["path"] == "data/parquet/orders/p1"
    # Scoped settings differ by result table, so each result keeps its own value.
    assert [(s["results"], s["value"]["content"]["parameters"]) for s in record["analytical_settings"]] == [
        (["r-001"], {"minimum_count": 5, "start": "2026-01-01"}),
        (["r-002"], {"minimum_count": 5, "start": "2026-01-01"})]
    assert record["packaging_commit"] == head and record["packaging_uncommitted_changes"] == "none"
    assert record["export_checks"] == "none" and "charts" not in record and "dataset_selection" not in record
    # A result represented without serialization is still listed with its evidence, for status, the
    # question its evidence recorded, verbatim, for methodology.md, and the runtime it recorded.
    assert record["results"] == [
        {"result_id": r, "evidence": f"investigations/inv/evidence/{r}.json", "question": QUESTIONS[r],
         "runtime": json.loads((project / f"investigations/inv/evidence/{r}.json").read_text())["runtime"]}
        for r in ("r-001", "r-002")]
    assert report["questions"] == QUESTIONS
    assert (project / "deliveries/inv/pkg/draft/charts/chart-1.csv").read_bytes() == chart


def state_rows(*rows):
    """A state.md whose Current findings table holds (finding, status, reason) rows."""
    lines = "".join(f"| {finding} | [r-001](evidence/r-001.json) | {status} | association | {reason} |\n"
                    for finding, status, reason in rows)
    return STATE.split("| Late orders")[0] + lines + "\n## Next steps\n"


LONG_REASON = ("Q-3 corrected west dates after the vendor re-sent the March file; the late share was computed "
               "on the uncorrected dates, so the rise in the west may be an artifact of the correction (`Q-3`)")
SECOND = {"finding": "East held steady", "reason": "Q-5 dropped duplicate east rows"}


def test_export_creates_revalidation_flags_from_state(project, capsys):
    path = project / "deliveries/inv/pkg/draft/manifest.json"
    path.unlink()
    code, out = run(project, capsys, "export", "inv", "pkg", "--result", "r-001")
    assert code == 0 and out["created"] and out["flags_pending"] == [] and "flags_error" not in out
    assert manifest(project)["revalidation_flags"] == "none"
    set_manifest(project, charts=[CHART_ENTRY])  # --result alone records no chart; the fixture's file needs one
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0 and report["flag_entries"] == [] and report["unmatched_flags"] == []
    path.unlink()
    write(project, "investigations/inv/state.md", state_rows(
        (FLAG["finding"], "revalidation-needed (was supported)", LONG_REASON), ("Other finding", "supported", "")))
    code, out = run(project, capsys, "export", "inv", "pkg", "--result", "r-001")
    assert code == 0 and out["created"] and manifest(project)["revalidation_flags"] == [
        {"finding": FLAG["finding"], "reason": LONG_REASON, "represented_in": [], "disposition": "none"}]
    assert out["flags_pending"] == [{"finding": FLAG["finding"], "needs": "represented_in"}]
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and report["unmatched_flags"] == [] and report["flag_entries"] == [
        {"finding": FLAG["finding"], "problem": PLACES_PROBLEM}]


def test_export_replaces_malformed_flag_entries_before_writing(project, capsys):
    with_results(project)
    write(project, "investigations/inv/state.md", FLAGGED)
    set_flags(project, [{"finding": FLAG["finding"], "reason": [], "represented_in": ["chart 1"], "disposition": "omit"}])
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001:region,late_rate", "--no-datasets")
    assert code == 0 and out["written"]
    record = manifest(project)
    assert record["charts"] == [EXPORTED_CHART]
    assert record["revalidation_flags"] == [{**FLAG, "represented_in": [], "disposition": "none"}]


def test_export_syncs_revalidation_flags_with_state(project, capsys):
    write(project, "investigations/inv/state.md", state_rows(
        (FLAG["finding"], "revalidation-needed (was supported)", FLAG["reason"]),
        (SECOND["finding"], "revalidation-needed", SECOND["reason"]),
        ("Third finding", "revalidation-needed", "Q-6 new")))
    chosen = {**FLAG, "represented_in": ["chart 1"], "disposition": "release_with_caveat", "note": "kept"}
    waiting = {**SECOND, "represented_in": ["findings: East"], "disposition": "none"}
    cleared = {"finding": "Gone", "reason": "fixed", "represented_in": "none"}
    stale = {"finding": "Third finding", "reason": "Q-6 old", "represented_in": ["chart 1"], "disposition": "omit"}
    set_flags(project, [stale, waiting, cleared, chosen])
    code, out = run(project, capsys, "export", "inv", "pkg", "--result", "r-001")
    assert code == 0 and out["written"]
    # State row order; exact matches kept whole; a changed reason starts fresh; a cleared flag drops.
    assert manifest(project)["revalidation_flags"] == [
        chosen, waiting, {"finding": "Third finding", "reason": "Q-6 new", "represented_in": [], "disposition": "none"}]
    assert out["flags_pending"] == [{"finding": SECOND["finding"], "needs": "disposition"},
                                    {"finding": "Third finding", "needs": "represented_in"}]
    write(project, "investigations/inv/state.md", STATE.format(status="supported", reason=""))
    code, out = run(project, capsys, "export", "inv", "pkg", "--result", "r-001")
    assert code == 0 and manifest(project)["revalidation_flags"] == "none" and out["flags_pending"] == []


def test_export_keeps_flags_when_state_is_unreadable(project, capsys):
    prior = [{**FLAG, "represented_in": ["chart 1"], "disposition": "none"}]
    set_flags(project, prior)
    write(project, "investigations/inv/state.md", b"\xff\xfe not text")
    code, out = run(project, capsys, "export", "inv", "pkg", "--result", "r-001")
    assert code == 0 and out["written"]
    assert out["flags_error"].startswith("investigations/inv/state.md: unreadable")
    record = manifest(project)
    assert record["revalidation_flags"] == prior and "producing_commit" in record
    assert out["flags_pending"] == [{"finding": FLAG["finding"], "needs": "disposition"}]


def test_flag_raised_after_none_fails_until_export_records_it(project, capsys):
    code, out = run(project, capsys, "export", "inv", "pkg", "--result", "r-001")
    assert code == 0 and manifest(project)["revalidation_flags"] == "none"
    run(project, capsys, "check-draft", "inv", "pkg")
    write(project, "investigations/inv/state.md", FLAGGED)
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and report["flag_entries"] == [] and report["unmatched_flags"] == [FLAG]
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 1 and report["refused"] == "flagged findings without a release disposition"
    assert report["unmatched_flags"] == [FLAG]
    code, out = run(project, capsys, "export", "inv", "pkg", "--result", "r-001")
    assert out["flags_pending"] == [{"finding": FLAG["finding"], "needs": "represented_in"}]
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert report["unmatched_flags"] == [] and report["flag_entries"] == [
        {"finding": FLAG["finding"], "problem": PLACES_PROBLEM}]


def test_export_keeps_differences_and_unknowns(project, capsys):
    evidence = project / "investigations/inv/evidence"
    second = json.loads((evidence / "r-002.json").read_text())
    second.update(producing_commit={"unknown": "not a git repository"},
                  producing_uncommitted_changes=[{"path": "src/x.py", "status": "no-vcs", "bytes": None, "sha256": None}])
    (evidence / "r-002.json").write_text(json.dumps(second))
    code, report = run(project, capsys, "export", "inv", "pkg", "--result", "r-001", "--result", "r-002")
    assert code == 0 and report["producing_commit"] == "differs by result"
    record = manifest(project)
    first = json.loads((evidence / "r-001.json").read_text())["producing_commit"]
    assert record["producing_commit"] == [
        {"results": ["r-001"], "value": first},
        {"results": ["r-002"], "value": {"unknown": "not a git repository"}}]
    assert record["producing_uncommitted_changes"] == [
        {"path": "src/x.py", "status": "no-vcs", "bytes": None, "sha256": None, "results": ["r-002"]}]


def test_export_refuses_missing_evidence_or_unnamed_chart_result(project, capsys):
    path = project / "deliveries/inv/pkg/draft/manifest.json"
    before = path.read_text()
    code, report = run(project, capsys, "export", "inv", "pkg", "--result", "r-001", "--result", "r-404")
    assert code == 1 and not report["written"]
    assert report["errors"][0].startswith("missing evidence: investigations/inv/evidence/r-404.json")
    assert path.read_text() == before
    path.write_text(json.dumps({**json.loads(before), "charts": [{"path": "charts/chart-1.csv", "result_id": "r-001"}]}))
    before = path.read_text()
    code, report = run(project, capsys, "export", "inv", "pkg", "--result", "r-002")
    assert code == 1 and report["errors"] == [
        "charts/chart-1.csv serializes r-001, which this call does not name; pass it with --result"]
    assert path.read_text() == before


DISPLAY = """[columns]
region = "Region"
late_rate = "Closed late (%)"
n = "Cases"

[values.region]
W = "West"
E = "East"

[round]
late_rate = 1
"""


def with_results(project):
    write(project, "foundation/display.toml", DISPLAY)


# What export records for --chart r-001:region,late_rate under DISPLAY.
EXPORTED_CHART = {"path": "charts/chart-1.csv", "result_id": "r-001", "columns": ["region", "late_rate"],
                  "selection": "all", "headers": ["Region", "Closed late (%)"],
                  "values": {"region": {"W": "West", "E": "East"}}, "percent": [], "scale": {},
                  "round": {"late_rate": 1}}


def test_export_writes_charts_datasets_and_manifest(project, capsys):
    with_results(project)
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001:region,late_rate",
                    "--dataset", "late-closures=r-001", "--result", "r-002")
    assert code == 0 and out["written"] and out["export_checks"] == {"results": 1, "failed": []}
    draft = project / "deliveries/inv/pkg/draft"
    assert (draft / "charts/chart-1.csv").read_text() == "Region,Closed late (%)\nWest,21.3\nEast,2.7\n"
    assert (draft / "datasets/late-closures.csv").read_text() == \
        "Region,Closed late (%),Cases\nWest,21.3,10\nEast,2.7,8\n"
    record = manifest(project)
    assert record["charts"] == [EXPORTED_CHART]
    assert record["dataset_selection"] == [{"path": "datasets/late-closures.csv", "result_id": "r-001",
                                            "columns": ["region", "late_rate", "n"], "percent": [], "scale": {},
                                            "round": {"late_rate": 1}}]
    assert [c["result_id"] for c in record["export_checks"]] == ["r-001"]
    assert all(len(c["comparisons"]) == 5 for c in record["export_checks"])
    assert [v["results"] for v in record["inputs"]["views"]] == [["r-001", "r-002"]]
    assert out["results"] == ["r-001", "r-002"] and record["revalidation_flags"] == "none"
    # Each source line states the shaping methodology.md repeats: here the rounding.
    assert "chart-1: Closed late (%) <- r-001.late_rate, rounded to 1 decimal place" in out["methodology_lines"]
    assert "late-closures: Cases <- r-001.n" in out["methodology_lines"]
    assert out["check_charts"] == []


def test_export_checks_follow_the_represented_set(project, capsys):
    with_results(project)
    run(project, capsys, "export", "inv", "pkg", "--chart", "r-001:region,late_rate", "--no-datasets")
    checks = manifest(project)["export_checks"]
    write(project, "investigations/inv/settings.toml", STALE_SETTINGS)
    code, out = run(project, capsys, "export", "inv", "pkg", "--result", "r-001", "--result", "r-002")
    assert code == 0 and manifest(project)["export_checks"] == checks
    write(project, "investigations/inv/settings.toml", SETTINGS)
    write(project / "deliveries/inv/pkg/draft", "findings.md", FINDINGS.replace(CHART_SPEC, ""))
    code, out = run(project, capsys, "export", "inv", "pkg", "--no-datasets", "--result", "r-002")
    assert code == 0 and out["charts"] == [] and out["check_charts"] == []
    record = manifest(project)
    assert (record["charts"], record["dataset_selection"], record["export_checks"]) == ("none", "none", "none")
    assert not (project / "deliveries/inv/pkg/draft/charts").exists()


def test_export_names_every_gap_and_blocks_stale_results(project, capsys):
    (project / "investigations/inv/results/r-002.csv").unlink()
    with_results(project)
    write(project, "foundation/display.toml", DISPLAY.replace('n = "Cases"\n', ""))
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001", "--chart", "r-002", "--no-datasets")
    assert code == 1 and not out["written"]
    assert out["errors"] == [
        "r-001: column 'n' has no display name in foundation/display.toml [columns]",
        "investigations/inv/results/r-002.csv is missing. Stop: saving a result table needs separately "
        "authorized analytical work"]
    with_results(project)
    before = (project / "deliveries/inv/pkg/draft/charts/chart-1.csv").read_bytes()
    write(project, "investigations/inv/settings.toml", STALE_SETTINGS)
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001", "--no-datasets")
    assert code == 1 and out["export_checks"]["failed"]
    assert out["exports_blocked"].endswith("Stop: changed results need separately authorized analytical work")
    assert (project / "deliveries/inv/pkg/draft/charts/chart-1.csv").read_bytes() == before
    write(project, "investigations/inv/settings.toml", SETTINGS)
    write(project, "deliveries/inv/pkg/draft/datasets/old.csv", "a\n1\n")
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001:region,late_rate", "--no-datasets")
    assert code == 0 and manifest(project)["dataset_selection"] == "none"
    assert not (project / "deliveries/inv/pkg/draft/datasets").exists()
    with pytest.raises(SystemExit):
        run(project, capsys, "export", "inv", "pkg", "--chart", "r-001")


def test_export_display_stub_names_each_gap_once(project, capsys):
    tomllib = pytest.importorskip("tomllib")
    write(project, "investigations/inv/results/r-001.csv", "region,late_rate,n,share.west\nW,21.3,10,0.5\n")
    write(project, "investigations/inv/results/r-002.csv", "region,n\nW,10\n")
    write(project, "foundation/display.toml", '[columns]\nregion = "Region"\nlate_rate = "  "\n')
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001:region,late_rate",
                    "--chart", "r-002", "--dataset", "wide=r-001")
    assert code == 1 and not out["written"]
    assert out["errors"][0] == "r-001: column 'late_rate' has a blank display name in foundation/display.toml [columns]"
    # Deduplicated across the chart and dataset paths; the dotted column stays one quoted key; the
    # blank late_rate already has its key, so the stub leaves it out and pasting it stays valid TOML.
    assert out["display_stub"] == '"n" = ""\n"share.west" = ""'
    assert tomllib.loads('[columns]\nregion = "Region"\nlate_rate = "  "\n' + out["display_stub"])["columns"] == {
        "region": "Region", "late_rate": "  ", "n": "", "share.west": ""}
    write(project, "foundation/display.toml", '[columns]\nregion = "Region"\nlate_rate = "Late"\nn = "Cases"\n')
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-002", "--dataset", "wide=r-001")
    assert code == 1 and out["display_stub"] == '"share.west" = ""'
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-002", "--dataset", "wide=r-001:region,n")
    assert out["written"] and "display_stub" not in out


# mean_age carries 14 decimal places; share's 4 and cases' 21.3500, 21.35 once its trailing zeros go, are display-ready.
UNROUNDED = "region,mean_age,share,cases\nW,366.89000039169395,0.2135,21.3500\nE,12.5,0.0268,8\n"
UNROUNDED_DISPLAY = '[columns]\nregion = "Region"\nmean_age = "Mean age"\nshare = "Share"\ncases = "Cases"\n'
ROUND_GAP = ("r-001: column 'mean_age' has values with more than 4 decimal places, trailing zeros aside, such as "
             "366.89000039169395, and no places under [round] in foundation/display.toml")


def test_export_gives_an_unrounded_float_column_a_round_gap_and_stub(project, capsys):
    tomllib = pytest.importorskip("tomllib")
    write(project, "investigations/inv/results/r-001.csv", UNROUNDED)
    write(project, "foundation/display.toml", UNROUNDED_DISPLAY)
    chart = (project / "deliveries/inv/pkg/draft/charts/chart-1.csv").read_bytes()
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001", "--dataset", "ages=r-001")
    assert code == 1 and not out["written"] and out["errors"] == [ROUND_GAP, ROUND_GAP]
    # One line per column, ready to paste under [round] once each is filled from the slide's number format.
    assert out["round_stub"] == '"mean_age" = ""' and "display_stub" not in out
    assert tomllib.loads(UNROUNDED_DISPLAY + "\n[round]\n" + out["round_stub"])["round"] == {"mean_age": ""}
    assert (project / "deliveries/inv/pkg/draft/charts/chart-1.csv").read_bytes() == chart
    # Only the cells a file holds count: the east row alone is display-ready.
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001:region,mean_age@where=region=E",
                    "--no-datasets")
    assert out["written"] and "round_stub" not in out
    # A pasted stub left blank is fixed in place from its own error, as a blank display name is.
    write(project, "foundation/display.toml", UNROUNDED_DISPLAY + '\n[round]\nmean_age = ""\n')
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001", "--no-datasets")
    assert code == 1 and "round_stub" not in out and out["errors"] == [
        "r-001: column 'mean_age' has [round] places '' in foundation/display.toml; give a whole number from 0 to 20"]
    write(project, "foundation/display.toml", UNROUNDED_DISPLAY + "\n[round]\nmean_age = 1\n")
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001", "--no-datasets")
    assert out["written"] and (project / "deliveries/inv/pkg/draft/charts/chart-1.csv").read_text() == (
        "Region,Mean age,Share,Cases\nW,366.9,0.2135,21.3500\nE,12.5,0.0268,8\n")
    # --round covers a column as [round] does.
    write(project, "foundation/display.toml", UNROUNDED_DISPLAY)
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001", "--no-datasets",
                    "--round", "mean_age=0")
    assert out["written"] and manifest(project)["charts"][0]["round"] == {"mean_age": 0}
    assert "chart-1: Mean age <- r-001.mean_age, rounded to whole numbers" in out["methodology_lines"]


@pytest.mark.parametrize("cell, percent, unrounded", [
    ("366.89000039169395", False, True), ("0.30000000000000004", False, True), ("1.23456", False, True),
    ("1e-05", False, True), ("-2.000001", False, True), ("0.1234567", True, True),
    ("1.2345", False, False), ("21.3500", False, False), ("1.5e3", False, False), ("100.0", False, False),
    ("0.123456", True, False), ("12", False, False), ("W", False, False), ("", False, False),
    ("nan", False, False), ("inf", False, False), ("1e999", False, False), ("1,234.56789", False, False),
    ("1_000.123456", False, False), (" 1.23456", False, False),
    # The file shows the saved text, so digits beyond a float's precision count, as does a tiny exponent.
    ("21.35000000000000142", False, True), ("0.1000000000000000055511151231257827", False, True),
    ("1e-999", False, True), ("12.50000000", True, False), ("-0.00", False, False),
    # An exponent too large for a decimal to hold is no number cell, as an overflowing one is not.
    ("1e-9999999999999999999", False, False), ("-1e-9999999999999999999", True, False)])
def test_unrounded_cells_follow_the_stated_threshold(cell, percent, unrounded):
    # A number cell is unrounded when its saved text, trailing zeros aside, any exponent applied, and a percent
    # column's 100-fold scaling applied, has more than four decimal places, so a percent column's saved fraction
    # may carry six; text that is not a finite plain number never is.
    draft = load(ASSETS["src/packaging/draft.py"], "draft_unrounded")
    assert draft._unrounded(cell, percent) is unrounded


def test_export_writes_a_cell_no_decimal_holds_as_saved(project, capsys):
    # A saved exponent too large for a decimal to hold is written as saved, not a crash.
    write(project, "investigations/inv/results/r-001.csv", "region,late_rate\nW,1e-9999999999999999999\n")
    write(project, "foundation/display.toml", '[columns]\nregion = "Region"\nlate_rate = "Closed late (%)"\n\n'
                                              '[percent]\ncolumns = ["late_rate"]\n')
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001", "--no-datasets")
    assert code == 0 and out["written"], out
    assert (project / "deliveries/inv/pkg/draft/charts/chart-1.csv").read_text() == \
        "Region,Closed late (%)\nW,1e-9999999999999999999\n"


def test_export_percent_scales_fractions_and_records_them(project, capsys):
    write(project, "investigations/inv/results/r-001.csv", "region,share\nW,0.21349\nE,0.0268\n")
    display = '[columns]\nregion = "Region"\nshare = "Share (%)"\n\n[percent]\ncolumns = ["share"]\n'
    write(project, "foundation/display.toml", display + "\n[round]\nshare = 1\n")
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001", "--dataset", "shares=r-001")
    assert out["written"], out
    draft = project / "deliveries/inv/pkg/draft"
    assert (draft / "charts/chart-1.csv").read_text() == "Region,Share (%)\nW,21.3\nE,2.7\n"
    assert (draft / "datasets/shares.csv").read_text() == "Region,Share (%)\nW,21.3\nE,2.7\n"
    record = manifest(project)
    assert (record["charts"][0]["percent"], record["charts"][0]["round"]) == (["share"], {"share": 1})
    assert "shares: Share (%) <- r-001.share, times 100, rounded to 1 decimal place" in out["methodology_lines"]
    assert record["dataset_selection"] == [{"path": "datasets/shares.csv", "result_id": "r-001",
                                            "columns": ["region", "share"], "percent": ["share"], "scale": {},
                                            "round": {"share": 1}}]
    # Scaled exactly from the saved text: 0.21349 shows as 21.349, three places, so it needs no [round].
    write(project, "foundation/display.toml", display)
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001", "--no-datasets")
    assert out["written"] and (draft / "charts/chart-1.csv").read_text() == "Region,Share (%)\nW,21.349\nE,2.68\n"
    assert "chart-1: Share (%) <- r-001.share, times 100" in out["methodology_lines"]
    for text in ('percent = ["share"]\n' + display.split("\n[percent]")[0],
                 display.replace('columns = ["share"]', 'columns = "share"'),
                 display.replace('columns = ["share"]', 'share = true')):
        write(project, "foundation/display.toml", text)
        code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001", "--no-datasets")
        assert code == 1 and not out["written"] and out["errors"] == [
            "foundation/display.toml: [percent] holds one key, columns, a list of column names"]
    # A key outside the file's tables, such as a misspelled one, is refused rather than ignored.
    write(project, "foundation/display.toml", display.replace("[percent]", "[percents]"))
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001", "--no-datasets")
    assert code == 1 and out["errors"] == [
        "foundation/display.toml: unknown key 'percents'; the file holds only [columns], [values.<column>], "
        "[round], [percent], [scale], [confirmed], and [results.\"<result>\"]"]


def test_per_result_display_names_override_the_global_ones(project, capsys):
    write(project, "investigations/inv/results/r-002.csv", "region,n\nW,4\n")
    override = ('\n[results."r-002".columns]\nregion = "Sales region"\n\n'
                '[results."r-002".values.region]\nW = "Wales"\n')
    write(project, "foundation/display.toml", DISPLAY + override)
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001:region,late_rate",
                    "--dataset", "wales=r-002")
    assert code == 0 and out["written"] and out["label_warnings"] == []
    draft = project / "deliveries/inv/pkg/draft"
    assert (draft / "charts/chart-1.csv").read_text() == "Region,Closed late (%)\nWest,21.3\nEast,2.7\n"
    assert (draft / "datasets/wales.csv").read_text() == "Sales region,Cases\nWales,4\n"
    assert "wales: Sales region <- r-002.region" in out["methodology_lines"]
    # A per-result value table replaces the global one for that column, so a code it lacks stays as written.
    write(project, "investigations/inv/results/r-002.csv", "region,n\nW,4\nE,5\n")
    run(project, capsys, "export", "inv", "pkg", "--chart", "r-001:region,late_rate", "--dataset", "wales=r-002")
    assert (draft / "datasets/wales.csv").read_text() == "Sales region,Cases\nWales,4\nE,5\n"
    write(project, "foundation/display.toml", DISPLAY + '\n[results."r-002".labels]\nregion = "Sales region"\n')
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001:region,late_rate", "--no-datasets")
    assert code == 1 and out["errors"] == [
        'foundation/display.toml: [results."r-002"] holds only a columns table, a values table, and a percent '
        'table']
    write(project, "foundation/display.toml", DISPLAY + '\n[results."r-002".percent]\ncolumns = "n"\n')
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001:region,late_rate", "--no-datasets")
    assert code == 1 and out["errors"] == [
        'foundation/display.toml: [results."r-002".percent] holds one key, columns, a list of column names']


def test_a_per_result_percent_list_replaces_the_global_one(project, capsys):
    # share holds fractions in r-001 and percents already in r-002: a global [percent] would scale r-002's
    # 21.35 to 2135, so r-002 takes its own list, here empty, and keeps its values as saved.
    write(project, "investigations/inv/results/r-001.csv", "region,share\nW,0.2135\n")
    write(project, "investigations/inv/results/r-002.csv", "region,share\nW,21.35\nE,2.68\n")
    display = ('[columns]\nregion = "Region"\nshare = "Share of claims (%)"\n\n[percent]\ncolumns = ["share"]\n\n'
               '[results."r-002".percent]\ncolumns = []\n')
    write(project, "foundation/display.toml", display)
    argv = ("export", "inv", "pkg", "--chart", "r-002", "--dataset", "fractions=r-001")
    code, out = run(project, capsys, *argv)
    assert out["written"], out
    draft = project / "deliveries/inv/pkg/draft"
    assert (draft / "charts/chart-1.csv").read_text() == "Region,Share of claims (%)\nW,21.35\nE,2.68\n"
    assert (draft / "datasets/fractions.csv").read_text() == "Region,Share of claims (%)\nW,21.35\n"
    record = manifest(project)
    assert record["charts"][0]["percent"] == [] and record["dataset_selection"][0]["percent"] == ["share"]
    assert "chart-1: Share of claims (%) <- r-002.share" in out["methodology_lines"]
    # check-draft reapplies the list the entry records, so the chart file matches its result.
    _, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert not [row for row in report["charts"] if "differs" in row["problem"]], report["charts"]
    # A result's own list names its percent columns whole: one naming the column scales it again.
    write(project, "foundation/display.toml", display.replace("columns = []", 'columns = ["share"]'))
    run(project, capsys, *argv)
    assert (draft / "charts/chart-1.csv").read_text() == "Region,Share of claims (%)\nW,2135\nE,268\n"
    # Without a global list, only the result that lists the column scales it.
    write(project, "foundation/display.toml", display.replace('[percent]\ncolumns = ["share"]', "[round]")
          .replace('[results."r-002".percent]\ncolumns = []', '[results."r-001".percent]\ncolumns = ["share"]'))
    run(project, capsys, *argv)
    assert (draft / "charts/chart-1.csv").read_text() == "Region,Share of claims (%)\nW,21.35\nE,2.68\n"
    assert (draft / "datasets/fractions.csv").read_text() == "Region,Share of claims (%)\nW,21.35\n"


COLLISION = ("results answering different questions share this [columns] name; confirm it fits each and list "
             "the column under [confirmed] columns, or name the column for one result under "
             "[results.\"<result>\".columns]")


def test_export_scale_divides_records_and_traces(project, capsys):
    draft = project / "deliveries/inv/pkg/draft"
    write(project, "foundation/display.toml", DISPLAY + "\n[scale]\nn = { divide = 4 }\n")
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001:region,n", "--dataset", "cases=r-001")
    assert out["written"], out
    assert (draft / "charts/chart-1.csv").read_text() == "Region,Cases\nWest,2.5\nEast,2\n"
    assert (draft / "datasets/cases.csv").read_text() == "Region,Closed late (%),Cases\nWest,21.3,2.5\nEast,2.7,2\n"
    record = manifest(project)
    assert record["charts"][0]["scale"] == {"n": 4} and record["dataset_selection"][0]["scale"] == {"n": 4}
    assert "chart-1: Cases <- r-001.n, divided by 4" in out["methodology_lines"]
    # A narrative number written in the scaled unit traces to the recorded value divided by the recorded divisor.
    write(draft, "methodology.md", METHODOLOGY + "\nWest averaged 2.5 cases a week.\n")
    _, report = run(project, capsys, "check-draft", "inv", "pkg")
    # The fixture's findings.md specifies another chart, so only the manifest rows of charts are compared below.
    recorded = [row for row in report["charts"] if "manifest" in row["problem"]]
    assert report["numbers"] == [] and recorded == [], report
    draft_module = load(ASSETS["src/packaging/draft.py"], "draft_scale")
    values, problems = draft_module.recorded_values(project, "inv", [{"result_id": "r-001"}], [("r-001", "n", 4)])
    assert problems == [] and {Decimal("2.5"), Decimal("2")} <= set(values)
    assert draft_module.recorded_scales(record) == [("r-001", "n", 4)]
    # Without the divisor the same number traces to nothing.
    write(project, "foundation/display.toml", DISPLAY)
    run(project, capsys, "export", "inv", "pkg", "--chart", "r-001:region,n", "--dataset", "cases=r-001")
    _, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert [row["text"] for row in report["numbers"]] == ["2.5"]
    # A divisor display.toml no longer gives is refused, as a header or label would be.
    set_manifest(project, charts=[{**record["charts"][0], "scale": {"n": 5}}])
    write(draft, "charts/chart-1.csv", "Region,Cases\nWest,2\nEast,1.6\n")
    _, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert [row for row in report["charts"] if "manifest" in row["problem"]] == [{
        "chart": "Chart 1", "problem": "the manifest's charts entry for chart-1.csv records "
                                 "scale divisors other than foundation/display.toml gives; rerun export, which "
                                 "records them"}]
    for scale in ("n = 4", "n = { divide = 0 }", "n = { divide = true }", "n = { divide = -2 }",
                  "n = { multiply = 4 }", 'n = { divide = "4" }'):
        write(project, "foundation/display.toml", DISPLAY + f"\n[scale]\n{scale}\n")
        code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001", "--no-datasets")
        assert code == 1 and out["errors"] == [
            "foundation/display.toml: [scale] n is not { divide = <a positive number> }"], scale
    write(project, "foundation/display.toml", "scale = 4\n" + DISPLAY)
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001", "--no-datasets")
    assert code == 1 and out["errors"] == [
        "foundation/display.toml: [scale] maps each column to { divide = <a positive number> }"]


def test_export_scale_needs_places_when_its_quotient_is_unrounded(project, capsys):
    write(project, "foundation/display.toml", DISPLAY + "\n[scale]\nn = { divide = 3 }\n")
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001:region,n", "--no-datasets")
    assert code == 1 and not out["written"] and out["round_stub"] == '"n" = ""'
    write(project, "foundation/display.toml", DISPLAY.replace("late_rate = 1", "late_rate = 1\nn = 1")
          + "\n[scale]\nn = { divide = 3 }\n")
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001:region,n", "--no-datasets")
    assert (project / "deliveries/inv/pkg/draft/charts/chart-1.csv").read_text() == \
        "Region,Cases\nWest,3.3\nEast,2.7\n"
    assert "chart-1: Cases <- r-001.n, divided by 3, rounded to 1 decimal place" in out["methodology_lines"]


PRECISION = ("its fractions are saved to exactly four decimal places, a sign the query rounded them, and shown as a "
             "percent to 1 places they are rounded a second time, which can move the last digit; save the result at "
             "full precision and round only under [round]")


def test_export_warns_on_a_fraction_rounded_in_its_query(project, capsys):
    # The issue's probe: 0.6315 saved by round(x, 4) shows as 63.2%, where the full value may give 63.1%.
    write(project, "investigations/inv/results/r-001.csv", "region,share\nW,0.6315\nE,0.0268\n")
    display = '[columns]\nregion = "Region"\nshare = "Share (%)"\n\n[percent]\ncolumns = ["share"]\n'
    write(project, "foundation/display.toml", display + "\n[round]\nshare = 1\n")
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001", "--dataset", "shares=r-001")
    assert out["written"] and out["precision_warnings"] == [  # a warning: the files are written
        {"result_id": "r-001", "column": "share", "example": "0.6315", "warning": PRECISION}]
    assert (project / "deliveries/inv/pkg/draft/charts/chart-1.csv").read_text() == "Region,Share (%)\nW,63.2\nE,2.7\n"
    # Shown to two places nothing is rounded again, and fractions saved at full precision raise nothing.
    write(project, "foundation/display.toml", display + "\n[round]\nshare = 2\n")
    _, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001", "--no-datasets")
    assert out["written"] and out["precision_warnings"] == []
    write(project, "investigations/inv/results/r-001.csv", "region,share\nW,0.63149999\nE,0.02680005\n")
    write(project, "foundation/display.toml", display + "\n[round]\nshare = 1\n")
    _, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001", "--no-datasets")
    assert out["written"] and out["precision_warnings"] == []


def test_export_warns_on_a_value_code_no_cell_holds(project, capsys):
    # The issue's probe: pandas saves a boolean as True, so a key true matches nothing.
    write(project, "investigations/inv/results/r-001.csv", "region,large\nW,True\nE,False\n")
    display = ('[columns]\nregion = "Region"\nlarge = "Large store"\n\n[values.region]\nW = "West"\nE = "East"\n'
               'N = "North"\n\n[values.large]\ntrue = "Yes"\nFalse = "No"\n')
    write(project, "foundation/display.toml", display)
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001", "--no-datasets")
    unmatched = "no cell of the saved tables it labels holds this code; a code matches the saved text exactly"
    assert out["written"] and out["value_warnings"] == [
        {"table": "[values.region]", "code": "N", "warning": unmatched},
        {"table": "[values.large]", "code": "true", "warning": unmatched + "; the table writes 'True'"}]
    assert (project / "deliveries/inv/pkg/draft/charts/chart-1.csv").read_text() == \
        "Region,Large store\nWest,True\nEast,No\n"
    # A code another exported table holds is matched, even when this chart's rows leave it out.
    write(project, "foundation/display.toml", display.replace("true", '"True"').replace('N = "North"\n', ""))
    _, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001@first=1", "--no-datasets")
    assert out["written"] and out["value_warnings"] == []


def test_confirmed_columns_silence_their_label_warning(project, capsys):
    with_results(project)
    write(project, "investigations/inv/results/r-002.csv", "region,n\nW,4\n")
    write(project, "foundation/display.toml", DISPLAY + '\n[confirmed]\ncolumns = ["region"]\n')
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001:region,n", "--dataset", "counts=r-002")
    assert out["written"] and out["label_warnings"] == [
        {"column": "n", "name": "Cases", "results": ["r-001", "r-002"], "warning": COLLISION}]
    write(project, "foundation/display.toml", DISPLAY + '\n[confirmed]\ncolumns = ["region", "n"]\n')
    _, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001:region,n", "--dataset", "counts=r-002")
    assert out["written"] and out["label_warnings"] == []
    write(project, "foundation/display.toml", DISPLAY + '\n[confirmed]\nregion = true\n')
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001:region,n", "--dataset", "counts=r-002")
    assert code == 1 and out["errors"] == [
        "foundation/display.toml: [confirmed] holds one key, columns, a list of column names"]


def test_export_warns_when_one_name_labels_results_with_different_questions(project, capsys):
    with_results(project)
    write(project, "investigations/inv/results/r-002.csv", "region,n\nW,4\n")
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001:region,late_rate",
                    "--dataset", "counts=r-002")
    # A warning, not a refusal: the files are written.
    assert code == 0 and out["written"] and out["label_warnings"] == [
        {"column": "region", "name": "Region", "results": ["r-001", "r-002"], "warning": COLLISION}]
    draft = load(ASSETS["src/packaging/draft.py"], "draft_collisions")
    display = draft.display_names(project)
    files = [("r-001", ["region", "late_rate"]), ("r-002", ["region", "n"])]
    assert draft.label_collisions(display, files, {"r-001": "Which?", "r-002": "Which?"}) == []
    assert draft.label_collisions(display, files, {"r-001": "Which?", "r-002": "How many?"}) == [
        {"column": "region", "name": "Region", "results": ["r-001", "r-002"], "warning": COLLISION}]
    display["results"] = {"r-002": {"columns": {"region": "Sales region"}, "values": {}}}
    assert draft.label_collisions(display, files, {"r-001": "Which?", "r-002": "How many?"}) == []


@pytest.mark.parametrize("text, parsed", [
    ("r-001", ("r-001", None, "all")),
    ("r-001:region,late_rate", ("r-001", ["region", "late_rate"], "all")),
    ("r-001: region , late_rate@first=10", ("r-001", ["region", "late_rate"], {"first": 10})),
    ("r-001@first=1", ("r-001", None, {"first": 1})),
    ("r-001@first=999999999", ("r-001", None, {"first": 999999999})),
    ("r-001:store,sales@where=region=W,E", ("r-001", ["store", "sales"],
                                            {"where": {"column": "region", "values": ["W", "E"]}})),
    ("r-001@where=contact=ops@example.com", ("r-001", None,
                                             {"where": {"column": "contact", "values": ["ops@example.com"]}})),
    ("r-001@where= region =West coast", ("r-001", None, {"where": {"column": "region", "values": ["West coast"]}})),
    # The '@' splits first, so a ':' in a value belongs to the selection, not the columns.
    ("r-001@where=slot=10:30", ("r-001", None, {"where": {"column": "slot", "values": ["10:30"]}})),
    # The @where column runs to the first '=', so it may hold the '@' or ',' a COLUMNS name cannot.
    ("r-001@where=e@mail=x", ("r-001", None, {"where": {"column": "e@mail", "values": ["x"]}})),
    ("r-001@where=a,b=x", ("r-001", None, {"where": {"column": "a,b", "values": ["x"]}})),
])
def test_chart_selection_grammar_accepts(text, parsed):
    draft = load(ASSETS["src/packaging/draft.py"], "draft_chart_grammar")
    assert draft.parse_chart(text) == parsed


@pytest.mark.parametrize("text, reason", [
    ("", "the result ID is not a simple name"), (":region", "the result ID is not a simple name"),
    ("r 001", "the result ID is not a simple name"), ("r-001:", "a column name is empty"),
    ("r-001:region,,n", "a column name is empty"),
    ("r-001@", "the row selection is not @first=<n> or @where=<column>=<value>[,<value>]"),
    ("r-001@last=3", "the row selection is not @first=<n> or @where=<column>=<value>[,<value>]"),
    ("r-001@first=0", "@first takes a whole number of rows from 1 to 999999999, without leading zeros"),
    ("r-001@first=007", "@first takes a whole number of rows from 1 to 999999999, without leading zeros"),
    ("r-001@first=-1", "@first takes a whole number of rows from 1 to 999999999, without leading zeros"),
    ("r-001@first=ten", "@first takes a whole number of rows from 1 to 999999999, without leading zeros"),
    ("r-001@first=1e3", "@first takes a whole number of rows from 1 to 999999999, without leading zeros"),
    ("r-001@first=1234567890", "@first takes a whole number of rows from 1 to 999999999, without leading zeros"),
    ("r-001@first=10@where=region=W", "@first takes a whole number of rows from 1 to 999999999, without leading zeros"),
    ("r-001@where=region", "@where needs a column, =, and values separated by commas, none empty"),
    ("r-001@where==W", "@where needs a column, =, and values separated by commas, none empty"),
    ("r-001@where=region=", "@where needs a column, =, and values separated by commas, none empty"),
    ("r-001@where=region=W,,E", "@where needs a column, =, and values separated by commas, none empty"),
    ("r-001@where=region=W,", "@where needs a column, =, and values separated by commas, none empty"),
])
def test_chart_selection_grammar_refuses(text, reason):
    draft = load(ASSETS["src/packaging/draft.py"], "draft_chart_grammar")
    with pytest.raises(ValueError) as error:
        draft.parse_chart(text)
    assert str(error.value) == (f"--chart {text!r}: {reason}; write "
                                "RESULT[:COLUMNS][@first=<n>|@where=<column>=<value>[,<value>]]")


MANY = "rank,store,sales\n" + "".join(f"{i},S{i:02d},{100 - i}\n" for i in range(1, 13))
MANY_DISPLAY = '[columns]\nrank = "Rank"\nstore = "Store"\nsales = "Sales"\n'


def test_export_selects_chart_rows_and_records_the_selection(project, capsys):
    write(project, "investigations/inv/results/r-001.csv", MANY)
    write(project, "foundation/display.toml", MANY_DISPLAY)
    draft = project / "deliveries/inv/pkg/draft"
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001:store,sales@first=10",
                    "--no-datasets")
    assert out["written"], out
    lines = (draft / "charts/chart-1.csv").read_text().splitlines()
    assert lines[0] == "Store,Sales" and lines[1:] == [f"S{i:02d},{100 - i}" for i in range(1, 11)]
    entry = manifest(project)["charts"][0]
    assert (entry["selection"], entry["columns"], entry["headers"]) == (
        {"first": 10}, ["store", "sales"], ["Store", "Sales"])
    assert out["methodology_lines"] == ["chart-1: rows <- the first 10 rows of r-001",
                                        "chart-1: Store <- r-001.store", "chart-1: Sales <- r-001.sales"]
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001:store,sales@where=store=S12,S03",
                    "--no-datasets")
    # Table order, not the order the values are listed in.
    assert out["written"] and (draft / "charts/chart-1.csv").read_text() == "Store,Sales\nS03,97\nS12,88\n"
    assert manifest(project)["charts"][0]["selection"] == {"where": {"column": "store", "values": ["S12", "S03"]}}
    assert out["methodology_lines"][0] == "chart-1: rows <- the rows of r-001 whose store is S12 or S03"
    before = (draft / "charts/chart-1.csv").read_bytes()
    for spec, error in [
            ("r-001:store,sales@where=region=W", "r-001: @where names no column 'region' (has rank, store, sales)"),
            ("r-001@where=store=S03,S99", "r-001: no row has store = 'S99'; @where compares values as the saved "
                                          "table writes them"),
            ("r-001@first=13", "r-001: @first=13 asks for more rows than the table's 12")]:
        code, out = run(project, capsys, "export", "inv", "pkg", "--chart", spec, "--no-datasets")
        assert code == 1 and not out["written"] and out["errors"] == [error]
    for argv, error in [
            (("--chart", "r-001@top=3", "--no-datasets"),
             "--chart 'r-001@top=3': the row selection is not @first=<n> or @where=<column>=<value>[,<value>]; "
             "write RESULT[:COLUMNS][@first=<n>|@where=<column>=<value>[,<value>]]"),
            (("--chart", "r-001", "--dataset", "top=r-001@first=3"),
             "--dataset 'top=r-001@first=3': a dataset takes no row selection; select rows only in a --chart")]:
        code, out = run(project, capsys, "export", "inv", "pkg", *argv)
        assert code == 2 and not out["written"] and out["errors"] == [error]
    assert (draft / "charts/chart-1.csv").read_bytes() == before


def test_check_draft_refuses_a_chart_file_that_differs_from_its_selection(project, capsys):
    with_results(project)
    draft = project / "deliveries/inv/pkg/draft"
    code, out = run(project, capsys, "export", "inv", "pkg", "--chart", "r-001:region,late_rate@first=1",
                    "--no-datasets", "--result", "r-002")
    assert code == 0 and (draft / "charts/chart-1.csv").read_text() == "Region,Closed late (%)\nWest,21.3\n"
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0 and report["charts"] == [], report
    # A hand-edited value, an extra row, and a renamed header each differ, in both modes and at release.
    differs = ("chart-1.csv differs from r-001 under its recorded selection, rounding, and labels ({}); rerun "
               "export, and select rows with --chart rather than editing the file")
    for text, detail in [("Region,Closed late (%)\nWest,21\n", "row 1"),
                         ("Region,Closed late (%)\nWest,21.3\nEast,2.7\n", "2 rows where the selection gives 1"),
                         ("Area,Closed late (%)\nWest,21.3\n", "its header")]:
        write(draft, "charts/chart-1.csv", text)
        for argv in ((), ("--verify-only",)):
            code, report = run(project, capsys, "check-draft", "inv", "pkg", *argv)
            assert code == 1 and {"chart": "Chart 1", "problem": differs.format(detail)} in report["charts"]
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 1 and report["refused"] == "check-draft --verify-only does not pass"
    assert not (project / "deliveries/inv/pkg/released").exists()
    # A rerun result whose saved table changed differs too.
    write(draft, "charts/chart-1.csv", "Region,Closed late (%)\nWest,21.3\n")
    write(project, "investigations/inv/results/r-001.csv", RESULT.replace("21.349", "19.2"))
    _, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert report["charts"] == [{"chart": "Chart 1", "problem": differs.format("row 1")}]
    write(project, "investigations/inv/results/r-001.csv", RESULT)
    # An entry edited to match an edited file differs from display.toml, so the falsified value never passes.
    entry = manifest(project)["charts"][0]
    write(draft, "charts/chart-1.csv", "Region,Closed late (%)\nWest,35\n")
    for edit, part in [({"values": {"region": {"W": "West"}, "late_rate": {"21.349": "35"}}}, "value labels"),
                       ({"percent": ["late_rate"], "round": {"late_rate": 0}}, "percent columns"),
                       ({"scale": {"late_rate": 10}}, "scale divisors"),
                       ({"headers": ["Region", "Closed late"]}, "headers")]:
        set_manifest(project, charts=[{**entry, **edit}])
        for argv in ((), ("--verify-only",)):
            code, report = run(project, capsys, "check-draft", "inv", "pkg", *argv)
            assert code == 1 and report["charts"] == [{"chart": "Chart 1", "problem": (
                f"the manifest's charts entry for chart-1.csv records {part} other than foundation/display.toml "
                "gives; rerun export, which records them")}], report
    write(draft, "charts/chart-1.csv", "Region,Closed late (%)\nWest,21.3\n")
    # Every chart file is one export recorded, with the shaping it applied.
    set_manifest(project, charts=[{"path": "charts/chart-1.csv", "result_id": "r-001"}])
    _, report = run(project, capsys, "check-draft", "inv", "pkg")
    old_entry = [{"chart": "Chart 1", "problem": "the manifest's charts entry for chart-1.csv records no selection, "
                  "columns, headers, value labels, percent, scale, or rounding; rerun export with every --chart to "
                  "record them (a --result-only export keeps this entry)"}]
    assert report["charts"] == old_entry
    # A --result-only export, as a revision that only adds caveats runs, keeps the entry, so the row names the
    # full export that records it.
    code, out = run(project, capsys, "export", "inv", "pkg", "--result", "r-001", "--result", "r-002")
    assert out["written"] and manifest(project)["charts"] == [{"path": "charts/chart-1.csv", "result_id": "r-001"}]
    _, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert report["charts"] == old_entry
    for charts in ("none", [], None):
        set_manifest(project, charts=charts)
        _, report = run(project, capsys, "check-draft", "inv", "pkg")
        assert report["charts"] == [{"chart": "Chart 1", "problem": "chart-1.csv is not in the manifest's charts; "
                                     "export writes every chart file, so rerun export with its --chart"}]
    set_manifest(project, charts=[{**EXPORTED_CHART, "selection": {"first": 1}, "values": {"region": {"W": "West"}}},
                                  {**EXPORTED_CHART, "path": "charts/chart-2.csv"}])
    _, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert report["charts"] == [{"chart": "Chart 2", "problem": "the manifest's charts lists charts/chart-2.csv, "
                                 "which the draft lacks; rerun export"}]
    set_manifest(project, charts={"path": "charts/chart-1.csv"})
    _, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert report["charts"] == [{"chart": None, "problem": "the manifest's charts is not none or a list of the "
                                 "entries export writes; rerun export"}]


# Plain text that reads the same where a viewer renders Markdown: a blank line ends each list, so no line
# after one joins its last item.
START_HERE = """Start here

This folder is the pkg package of the inv investigation. Its files fall into three parts.

1. Send these to your audience

- the deck, once you build it as part 2 says
{audience}
2. To build the deck

In a Microsoft 365 Copilot app chat, add the PowerPoint agent and attach these files:

- findings.md
- charts/chart-1.csv
- methodology.md
- deck-rules.md
- assembly/m365.md

Then send this prompt:

Build a PowerPoint deck from findings.md and the chart files, following deck-rules.md and m365.md.

3. Internal: keep these, and do not send them

- methodology.md, the full account of the analysis
- manifest.json, the record of what this package holds and what produced it
- deck-rules.md, the rules the deck is built by

The other files in part 2 are the deck's source; your audience gets the deck instead.
"""


def test_check_draft_writes_start_here_before_the_inventory(project, capsys):
    draft = project / "deliveries/inv/pkg/draft"
    note = draft / "START-HERE.md"
    code, report = run(project, capsys, "check-draft", "inv", "pkg", "--verify-only")
    assert not note.exists() and report["start_here"] is None  # --verify-only writes nothing
    lacks = ("START-HERE.md: the draft lacks it; run check-draft without --verify-only, which writes it and "
             "records it in the inventory")
    assert code == 1 and lacks in report["errors"]
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0 and report["start_here"] == "deliveries/inv/pkg/draft/START-HERE.md"
    assert note.read_text() == START_HERE.format(audience="")
    assert "START-HERE.md" in [row["path"] for row in manifest(project)["inventory"]]
    # The audience part lists the methodology note and each dataset the draft holds.
    write(draft, "methodology-note.md", "# How we did it\n\nWe counted orders.\n")
    write(draft, "datasets/late.csv", "Region\nWest\n")
    write(draft, "datasets/.DS_Store", "")
    set_manifest(project, dataset_selection=["datasets/late.csv"])
    run(project, capsys, "check-draft", "inv", "pkg")
    assert note.read_text() == START_HERE.format(audience="- methodology-note.md, a plain account of how the "
                                                          "analysis was done\n- datasets/late.csv\n")
    # --verify-only verifies it like any other file.
    note.write_text(note.read_text() + "Also send the manifest.\n")
    code, report = run(project, capsys, "check-draft", "inv", "pkg", "--verify-only")
    assert code == 1 and [(row["path"], row["kind"]) for row in report["verify"]] == [
        ("START-HERE.md", "size"), ("START-HERE.md", "checksum")]
    # Every release includes it: removed with its inventory row, it is still refused, at release too.
    note.unlink()
    record = manifest(project)
    set_manifest(project, inventory=[row for row in record["inventory"] if row["path"] != "START-HERE.md"])
    code, report = run(project, capsys, "check-draft", "inv", "pkg", "--verify-only")
    assert code == 1 and report["verify"] == [] and report["errors"] == [lacks] and report["start_here"] is None
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 1 and report["refused"] == "check-draft --verify-only does not pass"
    assert not (project / "deliveries/inv/pkg/released").exists()
    # The prompt is the one assembly/m365.md gives.
    m365 = (SKILLS / "awb-package/assets/package-format/assembly/m365.md").read_text()
    assert ("> Build a PowerPoint deck from findings.md and the chart files, following deck-rules.md and m365.md.\n"
            in m365)


@pytest.mark.parametrize("old, new, rows", [
    ("# Order quality\n", "# Order quality: board review DRAFT\n",
     [{"where": "title", "line": 1, "marker": "DRAFT", "text": "Order quality: board review DRAFT"}]),
    ("Operations leads, all regions\n", "Operations leads, all regions (working copy)\n",
     [{"where": "subtitle", "line": 2, "marker": "working copy", "text": "Operations leads, all regions (working copy)"}]),
    ("Operations leads, all regions\n", "Operations leads, all regions\n\n**Notes:** Not a numbered release yet.\n",
     [{"where": "title notes", "line": 4, "marker": "Not a numbered release", "text": "Not a numbered release yet."}]),
    ("### Late orders rose in the west", "### Draft: late orders rose in the west",
     [{"where": "heading", "line": 12, "marker": "Draft", "text": "Draft: late orders rose in the west"}]),
    ("**Headline:** The west has", "**Headline:** Draft answer: the west has",
     [{"where": "headline", "line": 6, "marker": "Draft",
       "text": "Draft answer: the west has the most late orders"}]),
    # Read only where a deck names its status; other words holding "draft" are not markers.
    ("# Order quality\n", "# Order quality, drafted by the operations team\n", []),
    ("# Order quality\n", "# Order quality after the redraft\n", []),
    ("Operations leads, all regions\n", "Operations leads, all regions, working copies\n", []),
    ("**Notes:** The west leads the regions.\n\n## How", "**Notes:** Draft numbers.\n\n## How", []),
    ("- **Data:**", "- The draft budget is set.\n- **Data:**", []),
])
def test_check_draft_reports_draft_markers_as_information(project, capsys, old, new, rows):
    draft = project / "deliveries/inv/pkg/draft"
    assert old in FINDINGS
    write(draft, "findings.md", FINDINGS.replace(old, new, 1))
    _, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert report["draft_markers"] == rows
    _, verified = run(project, capsys, "check-draft", "inv", "pkg", "--verify-only")
    assert verified["draft_markers"] == rows
    if old == "# Order quality\n" and rows:
        assert report["passed"]  # informational: a marker never fails the check


def test_release_refuses_failed_check_or_pending_disposition(project, capsys):
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 1 and report["refused"] == "check-draft --verify-only does not pass"
    run(project, capsys, "check-draft", "inv", "pkg")
    write(project, "investigations/inv/state.md", FLAGGED)
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 1 and report["refused"] == "flagged findings without a release disposition"
    assert report["unmatched_flags"] == [FLAG]
    unrelated = {"finding": "F2", "reason": "unrelated", "represented_in": "none"}
    places = ["findings: Late orders", "chart 1"]
    for flag, problem in [({"disposition": "none"}, "no disposition"),
                          ({"disposition": "revalidate"}, "revalidation pending")]:
        set_flags(project, [{**FLAG, "represented_in": places, **flag}, unrelated])
        code, report = run(project, capsys, "release", "inv", "pkg")
        assert code == 1 and report["unmatched_flags"] == [] and report["dispositions"] == [
            {"finding": FLAG["finding"], "problem": problem}]
    # Malformed entries fail check-draft itself, so release refuses on the check with its flag_entries.
    unknown = "unknown disposition {!r}; record none, revalidate, omit, or release_with_caveat"
    for flag, problem in [({}, unknown.format(None)), ({"disposition": "later"}, unknown.format("later")),
                          ({"represented_in": [], "disposition": "omit"}, PLACES_PROBLEM),
                          ({"represented_in": [{"place": "chart 1"}], "disposition": "omit"}, PLACES_PROBLEM)]:
        set_flags(project, [{**FLAG, "represented_in": places, **flag}, unrelated])
        code, report = run(project, capsys, "release", "inv", "pkg")
        assert code == 1 and report["refused"] == "check-draft --verify-only does not pass"
        assert report["check"]["flag_entries"] == [{"finding": FLAG["finding"], "problem": problem}]
    assert not (project / "deliveries/inv/pkg/released").exists()


SOURCES = """# Source register

## Acquisitions

| Acquisition ID | Source ID | Acquired at | Source version, query, or request | Landed directory | Retained copy | Integrity or completeness check | Restrictions | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| a1 | crm | 2026-01-02 | export | data/raw/crm/a1 | this checkout only | rows | none | |
| a2 | crm | 2026-01-03 | export | data/raw/crm/a2 | `/backup/raw` | rows | none | |
"""


def test_release_reports_fields_for_the_report(project, capsys):
    write(project, "investigations/inv/state.md", FLAGGED)
    write(project, "foundation/sources.md", SOURCES)
    path = project / "deliveries/inv/pkg/draft/manifest.json"
    record = json.loads(path.read_text())
    record.update(dataset_selection=["datasets/late.csv"], producing_commit={"unknown": "not a git repository"},
                  inputs={"acquisitions": [{"path": f"data/raw/crm/{a}", "results": ["r-001"]}
                                           for a in ("a1", "a2", "a3")]},
                  revalidation_flags=[{**FLAG, "represented_in": ["chart 1"], "disposition": "release_with_caveat"},
                                      {"finding": "F2", "reason": "unrelated", "represented_in": "none"}])
    path.write_text(json.dumps(record))
    write(project, "deliveries/inv/pkg/draft/datasets/late.csv", "Region\nWest\n")
    # The deck states its open caveats on its Limitations and open caveats slide, flagged findings among them.
    findings = BASE + LIMITATIONS.replace("**Notes:**", "- Prices are as recorded; VAT treatment is unconfirmed\n"
                                          "- Late orders in the west await revalidation\n"
                                          "  - Their dates are being corrected\n\n**Notes:**")
    write(project, "deliveries/inv/pkg/draft/findings.md", findings)
    line = findings.splitlines().index("- Prices are as recorded; VAT treatment is unconfirmed") + 1
    # The slide's headline states the limitation that matters most, so it is the first caveat listed.
    slide = [{"slide": "Limitations and open caveats",
              "line": findings.splitlines().index("**Headline:** Coverage remains limited") + 1,
              "text": "Coverage remains limited", "sub": []},
             {"slide": "Limitations and open caveats", "line": line,
              "text": "Prices are as recorded; VAT treatment is unconfirmed", "sub": []},
             {"slide": "Limitations and open caveats", "line": line + 1,
              "text": "Late orders in the west await revalidation", "sub": ["Their dates are being corrected"]}]
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0, report
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 0 and report["verify"] == [] and report["datasets"] == ["datasets/late.csv"]
    assert report["dispositions"] == [{**FLAG, "represented_in": ["chart 1"],
                                       "disposition": "release_with_caveat", "new": True}]
    # The open caveats the release carries, new or carried forward, so the report never calls it clean.
    assert report["open_caveats"] == slide + [{**FLAG, "represented_in": ["chart 1"]}]
    assert report["provenance_gaps"] == [{"field": "producing_commit", "reason": "not a git repository"}]
    assert report["checkout_only_acquisitions"] == [
        {"acquisition": "data/raw/crm/a1", "retained_copy": "this checkout only"},
        {"acquisition": "data/raw/crm/a3", "retained_copy": "no Acquisitions row"}]
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 0 and report["release_number"] == "002" and report["dispositions"][0]["new"] is False
    assert report["open_caveats"] == slide + [{**FLAG, "represented_in": ["chart 1"]}]
    set_flags(project, [{**FLAG, "represented_in": ["chart 1"], "disposition": "omit"}])
    code, report = run(project, capsys, "release", "inv", "pkg")
    # An omitted flag is no caveat, but the slide's caveats remain open.
    assert code == 0 and report["dispositions"][0]["new"] is True and report["open_caveats"] == slide
    (project / "deliveries/inv/pkg/released/003/manifest.json").write_text("not json")
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 0 and report["release_number"] == "004" and report["dispositions"][0]["new"] is None


def test_open_caveats_read_the_deck_wherever_its_caveat_slides_stand(tmp_path):
    draft = load(ASSETS["src/packaging/draft.py"], "draft_open_caveats")
    findings = deck("### Late orders rose in the west\n\n- The open caveat here is a finding's bullet\n\n"
                    "**Notes:** The west leads.\n",
                    HOW_WE_KNOW + "\n## Open questions\n\n**Headline:** One question remains\n\n"
                    "- Are prices net of VAT?\n\n**Notes:** Finance owns it.\n\n## Appendix\n\n"
                    "### Limitations and open caveats\n\n**Headline:** Coverage remains limited\n\n"
                    "- History before 2009 is not visible\n  - Earlier orders were archived\n\n"
                    "**Notes:** Interpret with care.\n")
    write(tmp_path, "findings.md", findings)
    lines = findings.splitlines()
    flags = [{**FLAG, "represented_in": ["chart 1"], "disposition": "release_with_caveat"},
             {"finding": "F2", "reason": "dropped", "represented_in": ["chart 2"], "disposition": "omit"},
             {"finding": "F3", "reason": "unrelated", "represented_in": "none"}]
    assert draft.open_caveats(tmp_path, {"revalidation_flags": flags}) == [
        {"slide": "Open questions", "line": lines.index("**Headline:** One question remains") + 1,
         "text": "One question remains", "sub": []},
        {"slide": "Open questions", "line": lines.index("- Are prices net of VAT?") + 1,
         "text": "Are prices net of VAT?", "sub": []},
        {"slide": "Limitations and open caveats", "line": lines.index("**Headline:** Coverage remains limited") + 1,
         "text": "Coverage remains limited", "sub": []},
        {"slide": "Limitations and open caveats", "line": lines.index("- History before 2009 is not visible") + 1,
         "text": "History before 2009 is not visible", "sub": ["Earlier orders were archived"]},
        {**FLAG, "represented_in": ["chart 1"]}]
    assert draft.open_caveats(tmp_path, {"revalidation_flags": "none"})[-1]["slide"] == "Limitations and open caveats"
    # A Limitations slide holding only its headline and notes passes every check, and its headline is the
    # deck's main open caveat, so the release still lists it.
    findings = BASE + LIMITATIONS.replace("Coverage remains limited", "VAT treatment of retail B is unconfirmed")
    write(tmp_path, "findings.md", findings)
    assert draft.outline_problems(tmp_path / "findings.md") == []
    assert draft.open_caveats(tmp_path, {"revalidation_flags": "none"}) == [
        {"slide": "Limitations and open caveats",
         "line": findings.splitlines().index("**Headline:** VAT treatment of retail B is unconfirmed") + 1,
         "text": "VAT treatment of retail B is unconfirmed", "sub": []}]


def test_release_manifest_lists_runtime_per_result(project, capsys):
    evidence = project / "investigations/inv/evidence"
    first = json.loads((evidence / "r-001.json").read_text())["runtime"]
    assert set(first) == {"python", "platform", "packages", "unread_requirements"}
    second = json.loads((evidence / "r-002.json").read_text())
    second["runtime"]["packages"]["duckdb"] = "0.0.1-fixture"
    (evidence / "r-002.json").write_text(json.dumps(second))
    code, report = run(project, capsys, "export", "inv", "pkg", "--result", "r-001", "--result", "r-002")
    assert code == 0 and report["written"]
    run(project, capsys, "check-draft", "inv", "pkg")
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 0 and report["released"] and report["provenance_gaps"] == []
    assert [(r["result_id"], r["runtime"]) for r in manifest(project, "released/001")["results"]] == [
        ("r-001", first), ("r-002", second["runtime"])]
    second["runtime"]["unread_requirements"] = ["requirements.txt:2: -e ."]
    (evidence / "r-002.json").write_text(json.dumps(second))
    run(project, capsys, "export", "inv", "pkg", "--result", "r-001", "--result", "r-002")
    run(project, capsys, "check-draft", "inv", "pkg")
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 0 and report["released"] and report["provenance_gaps"] == [
        {"field": "results[1].runtime.unread_requirements[0]",
         "reason": "requirements not read, packages unrecorded: requirements.txt:2: -e ."}]
    del second["runtime"]
    (evidence / "r-002.json").write_text(json.dumps(second))
    run(project, capsys, "export", "inv", "pkg", "--result", "r-001", "--result", "r-002")
    run(project, capsys, "check-draft", "inv", "pkg")
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 0 and report["provenance_gaps"] == [
        {"field": "results[1].runtime", "reason": "evidence lacks runtime"}]
    assert manifest(project, "released/003")["results"][1]["runtime"] == {"unknown": "evidence lacks runtime"}
    second["runtime"] = None
    (evidence / "r-002.json").write_text(json.dumps(second))
    run(project, capsys, "export", "inv", "pkg", "--result", "r-001", "--result", "r-002")
    assert manifest(project, "draft")["results"][1]["runtime"] == {"unknown": "evidence lacks runtime"}


def test_release_numbers_stamps_and_copies_to_storage(project, capsys, tmp_path_factory):
    store = tmp_path_factory.mktemp("store")
    readme = project / "README.md"
    readme.write_text(readme.read_text().replace("not yet recorded", f"`{store}`"))
    run(project, capsys, "check-draft", "inv", "pkg")
    for number in ("001", "003"):
        (project / f"deliveries/inv/pkg/released/{number}").mkdir(parents=True)
    (project / "deliveries/inv/pkg/released/notes").mkdir()
    draft_before = manifest(project)
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 0 and report["released"] and report["release_number"] == "004"
    record = manifest(project, "released/004")
    assert (record["status"], record["release_number"], record["prior_release"]) == ("release", "004", "released/003")
    assert record["released_at"] == report["released_at"]
    assert record["revised_at"] == draft_before["revised_at"]
    assert datetime.fromisoformat(record["released_at"]).utcoffset() is not None
    assert record["inventory"] == draft_before["inventory"] and manifest(project) == draft_before
    # Storage holds <location>/<investigation>/<package>/<n>/, without the checkout's released/ folder.
    assert report["storage"] == {"status": "copied", "copy": str(store / "inv/pkg/004"), "compare_trees": []}
    assert (store / "inv/pkg/004/findings.md").read_text() == FINDINGS
    assert not (store / "inv/pkg/released").exists()


def test_release_storage_conflict_and_instructions(project, capsys, tmp_path_factory):
    store = tmp_path_factory.mktemp("store")
    (store / "inv/pkg/001").mkdir(parents=True)
    readme = project / "README.md"
    original = readme.read_text()
    run(project, capsys, "check-draft", "inv", "pkg")
    readme.write_text(original.replace("not yet recorded", str(store)))
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 1 and report["released"] and report["storage"]["status"] == "conflict"
    assert {row["kind"] for row in report["storage"]["compare_trees"]} == {"missing"}
    assert list((store / "inv/pkg/001").iterdir()) == []

    cases = {"none chosen": "none chosen", "not yet recorded": "unrecorded",
             "https://example.invalid/sites/team": "unreachable"}
    for number, (location, status) in enumerate(cases.items(), start=2):
        readme.write_text(original.replace("not yet recorded", location))
        code, report = run(project, capsys, "release", "inv", "pkg")
        assert code == 0 and report["release_number"] == f"{number:03d}"
        assert report["storage"]["status"] == status
        if status == "none chosen":
            assert "only copy" in report["storage"]["warning"]
        if status == "unrecorded":
            assert report["storage"]["instruction"] == (
                "record where released packages are kept, then copy deliveries/inv/pkg/released/003/ "
                "there as <location>/inv/pkg/003/")
    assert report["storage"]["instruction"] == (
        "copy deliveries/inv/pkg/released/004/ to https://example.invalid/sites/team/inv/pkg/004/")


def test_copy_releases_copies_compares_and_never_overwrites(project, capsys, tmp_path_factory):
    run(project, capsys, "check-draft", "inv", "pkg")
    for _ in range(2):
        code, report = run(project, capsys, "release", "inv", "pkg")
        assert code == 0 and report["storage"]["status"] == "unrecorded"
    store = tmp_path_factory.mktemp("store")
    readme = project / "README.md"
    readme.write_text(readme.read_text().replace("not yet recorded", str(store)))
    code, report = run(project, capsys, "copy-releases", "inv")
    assert code == 0 and report["location"] == str(store) and report["errors"] == []
    assert [(r["release"], r["storage"]["status"], r["storage"]["compare_trees"]) for r in report["releases"]] == [
        ("deliveries/inv/pkg/released/001", "copied", []), ("deliveries/inv/pkg/released/002", "copied", [])]
    assert (store / "inv/pkg/002/findings.md").read_text() == FINDINGS
    assert not (store / "inv/pkg/released").exists()
    assert not (project / "deliveries/inv/pkg/audit").exists()
    (store / "inv/pkg/001/findings.md").write_text("changed\n")
    code, report = run(project, capsys, "copy-releases", "inv", "pkg")
    assert code == 1 and [r["storage"]["status"] for r in report["releases"]] == ["conflict", "already copied"]
    assert (store / "inv/pkg/001/findings.md").read_text() == "changed\n"
    code, report = run(project, capsys, "copy-releases", "inv", "other")
    assert code == 1 and report["errors"] == ["no package at deliveries/inv/other"]


@pytest.mark.parametrize("verify_only", [False, True])
def test_check_draft_checks_findings_drift(project, verify_only):
    draft = load(project / "src/packaging/draft.py", "draft_findings_drift")
    assert draft.check_draft(project, "inv", "pkg")["passed"]
    write(project, "investigations/inv/state.md", STATE.format(status="supported", reason=""))
    path = project / "investigations/inv/findings.json"
    content = json.loads(path.read_text())
    assert content["findings"][0] == {
        "result": "r-009", "text": "Late orders rose in the west", "status": "supported", "prior_status": None,
        "flag_reason": "", "notes": [], "checks_caveat": "", "notes_checks": "", "claim": "association",
        "claim_basis": ""}
    report = draft.check_draft(project, "inv", "pkg", verify_only=verify_only)
    assert report["passed"] and report["errors"] == []
    del content["findings"][0]["claim"]  # an absent claim strength fails, never defaulted
    path.write_text(json.dumps(content))
    report = draft.check_draft(project, "inv", "pkg", verify_only=verify_only)
    assert not report["passed"] and "no valid claim strength" in " ".join(report["errors"])
    write(project, "investigations/inv/state.md", STATE.format(status="supported", reason=""))
    state = project / "investigations/inv/state.md"
    state.write_text(state.read_text().replace("Late orders rose in the west", "Hand edited finding"))
    report = draft.check_draft(project, "inv", "pkg", verify_only=verify_only)
    assert not report["passed"]
    assert "Hand edited finding" in " ".join(report["errors"])
    assert "state render --investigation inv" in " ".join(report["errors"])
    write(project, "src/provenance.py", "# old provenance helper\n")
    report = draft.check_draft(project, "inv", "pkg", verify_only=verify_only)
    assert not report["passed"] and "install_helpers.py --upgrade" in " ".join(report["errors"])
    write(project, "src/provenance.py", ASSETS["src/provenance.py"].read_bytes())
    (project / "investigations/inv/findings.json").unlink()  # with no findings.json, any row is drift
    report = draft.check_draft(project, "inv", "pkg", verify_only=verify_only)
    assert not report["passed"] and "state render --investigation inv" in " ".join(report["errors"])


@pytest.mark.parametrize("unusable", ["schema", "unscoped"])
def test_evidence_older_than_scoped_3_is_reported_for_rerun(project, capsys, unusable):
    path = project / "investigations/inv/evidence/r-001.json"
    evidence = json.loads(path.read_text())
    if unusable == "schema":
        evidence["schema"] = "awb-evidence/1"
    else:
        evidence["settings"].pop("result")
    path.write_text(json.dumps(evidence))
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and not report["passed"]
    assert ("investigations/inv/evidence/r-001.json: not awb-evidence/3 with result-scoped settings; rerun the result"
            in report["names_problems"])
    code, out = run(project, capsys, "export", "inv", "pkg", "--result", "r-001")
    assert code == 1 and any("rerun the result" in e for e in out["errors"])


CLAIM_FINDINGS = """# Order quality for the operations team
Operations leads, all regions, January to June 2026

## Answer

**Headline:** Discounts drive 4 points fewer late orders

## Findings

### Late orders rose in the west

- The new carrier drives the rise to 21%, a data-driven view.
- West volume, <!-- causes --> its comment unread, is flat.

**Chart 1.** Bar: late share by region

### Discounts cut late orders by 4 points

- Randomized discounts led to 4 points fewer late orders.

## How we know

**Headline:** Totals reconcile to the ledger

- June is short due to a feed outage.

## Limitations and open caveats

- Late orders may rise because of holiday volume.
"""
CLAIM_METHODOLOGY = """# Methodology

## Findings

### Late orders rose in the west

**Claim strength:** association

Result `r-009`, evidence [r-009](../../../../investigations/inv/evidence/r-009.json).

### Discounts cut late orders by 4 points

**Claim strength:** causal (experiment: randomized discount test)

Result `r-002`.
"""


def claim_draft(project, findings=CLAIM_FINDINGS, methodology=CLAIM_METHODOLOGY, results=("r-009", "r-002")):
    draft = project / "deliveries/inv/pkg/draft"
    # Each represented result's question, repeated in a section of its own so it cites no result, and the
    # table the findings' numbers trace to: the questions and numbers checks pass, leaving claims to judge.
    questions = {r: {**QUESTIONS, "r-009": "Did west late orders rise?"}.get(r, "What did this result record?")
                 for r in results}
    write(draft, "findings.md", findings)
    write(draft, "methodology.md", methodology + "\n## Result questions\n\n" + "\n\n".join(questions.values()) + "\n")
    write(project, "investigations/inv/results/r-009.csv", "region,late_rate,change\nW,21,4\n")
    path = draft / "manifest.json"
    record = json.loads(path.read_text())
    record["results"] = [{"result_id": r, "evidence": f"investigations/inv/evidence/{r}.json", "question": questions[r]}
                         for r in results]
    path.write_text(json.dumps(record))


def test_check_draft_refuses_causal_wording_above_claim_strength(project, capsys):
    claim_draft(project)
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and not report["passed"]
    assert report["claims"] == [{
        "line": 12, "section": "Late orders rose in the west", "phrase": "drives", "claim": "association",
        "results": ["r-009"], "problem": "causal wording above the association claim strength; reword it, since "
        "only an experiment or an identified natural experiment supports a causal claim"}]
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 1 and report["refused"] == "check-draft --verify-only does not pass"
    assert [row["phrase"] for row in report["check"]["claims"]] == ["drives"]
    claim_draft(project, DECK_FINDINGS)
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0 and report["passed"] and report["claims"] == [] and report["outline"] == []


# Sentences on an Answer slide, and the causal phrases the claims check reads in them: a phrase in a negated clause
# is skipped, under the closed grammar the helper declares above _CLAUSE_END.
NEGATED_PROBES = [
    ("The design does not test what caused them.", []), ("Discounts drove the increase.", ["drove"]),
    ("The effect on repeat rates is unknown.", []), ("The data show patterns, not trends or causes.", []),
    ("The impact of the change remains unclear.", []), ("The causes of the drop are not established.", []),
    ("The rise is not due to weather.", []), ("The rise isn't attributable to price.", []),
    ("We cannot say whether discounts drove sales.", []), ("There is no evidence that discounts drove sales.", []),
    ("Without testing what caused them, we report shares.", []), ("Neither region drove it.", []),
    ("Sales did not\nfall due to weather.", []),  # a wrapped line continues its clause
    # Outside the grammar the phrase is still read: another clause, a relative clause, a negator five words back,
    # an intensifier, a determiner, a noun phrase's relative clause, a verb's predicate, or another bullet.
    ("The rise was not due to weather, but due to pricing.", ["due to"]),
    ("The rise was not seasonal; discounts drove it.", ["drove"]),
    ("Sales did not fall and discounts drove returns.", ["drove"]),
    ("Customers who did not renew drove the drop.", ["drove"]),
    ("Stores that never discounted drove the rise.", ["drove"]),
    ("We did not see that the large western stores drove it.", ["drove"]),
    ("Not only did discounts drive sales.", ["drive"]), ("Not just price drove it.", ["drove"]),
    ("Stores with no discount drove the rise.", ["drove"]), ("Stores without a discount drove the rise.", ["drove"]),
    ("Weather causes delays whose length is unknown.", ["causes"]), ("Discounts drove sales that are unknown.", ["drove"]),
    ("- Sales did not fall\n- Discounts drove returns", ["drove"]),
]


def test_negated_causal_phrases_are_no_claims():
    draft = load(ASSETS["src/packaging/draft.py"], "draft_negated")
    found = {}
    for text, _ in NEGATED_PROBES:
        view = draft._view("## Answer\n\n" + text + "\n")[0]
        found[text] = [phrase for _, phrase, _ in draft._phrases(view, "prose", 2)]
    assert found == dict(NEGATED_PROBES)


def test_check_draft_skips_negated_causal_wording(project, capsys):
    bullet = "- Late orders rose to 21%, a data-driven view."
    claim_draft(project, DECK_FINDINGS.replace(bullet, "- The scan does not test what caused them."))
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0 and report["claims"] == [], report
    claim_draft(project, DECK_FINDINGS.replace(bullet, "- The scan does not test what caused them.\n"
                                                       "- The new carrier drove the increase."))
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and [(row["line"], row["phrase"]) for row in report["claims"]] == [(15, "drove")]


CLEAN_FINDINGS = CLAIM_FINDINGS.replace("The new carrier drives the rise", "Late orders rose")
# CLEAN_FINDINGS with every slide's notes and the chart's Data line, so the whole draft passes.
DECK_FINDINGS = """# Order quality for the operations team
Operations leads, all regions, January to June 2026

## Answer

**Headline:** Discounts drive 4 points fewer late orders

**Notes:** The discount test is the answer.

## Findings

### Late orders rose in the west

- Late orders rose to 21%, a data-driven view.
- West volume, <!-- causes --> its comment unread, is flat.

""" + CHART_SPEC + """
**Notes:** The west leads the regions.

### Discounts cut late orders by 4 points

- Randomized discounts led to 4 points fewer late orders.

**Notes:** Stores were assigned at random.

## How we know

**Headline:** Totals reconcile to the ledger

- June is short due to a feed outage.

**Notes:** The ledger is the finance team's.

## Limitations and open caveats

**Headline:** Holiday volume may move late orders

- Late orders may rise because of holiday volume.

**Notes:** Holiday weeks are in the period.
"""
WEST = "### Late orders rose in the west"
HEADLINE = "The new carrier drives late orders up in the west"
WEST_BULLET = "- Late orders rose to 21%, a data-driven view."
WEST_CLAIM = "**Claim strength:** association"
DISCOUNT_CLAIM = "**Claim strength:** causal (experiment: randomized discount test)"
DISCOUNT_RESULT = "Result `r-002`."
WEST_DISCOUNT = "Late orders rose in the west"
DISCOUNT = "Discounts cut late orders by 4 points"
NO_LINE = ("methodology.md's section has no **Claim strength:** line opening a top-level paragraph; its results "
           "support association")
UNRECOGNIZED = ("methodology.md's **Claim strength:** line is not descriptive, association, or causal with its "
                "design basis; its results support association")
NO_SECTION = ("methodology.md has no ### section with this heading, so no **Claim strength:** line; its results "
              "support association")
STATES_CAUSAL = "methodology.md states causal on its **Claim strength:** line; its results support association"
# What a markdown row refuses, as `unsupported Markdown: <what> at line N; rewrite as <how>` names it.
HEADING_IN_LIST = "a heading inside a list item or block quote"
INDENTED_CODE = "text indented four or more spaces, which renders as code"
SETEXT = "text underlined with = or -, which renders as a heading"
FENCE_IN_LIST = "a code fence inside a list item or block quote"
FENCE_INDENTED = "a code fence indented from the start of its line"
FENCE_OPEN = "a code fence never closed"
COMMENT_IN_LIST = "a comment inside a list item or block quote"
COMMENT_INDENTED = "a comment indented from the start of its line"
COMMENT_OPEN = "a comment never closed"
HTML_BLOCK = "an HTML block"
INLINE_TAG = "an inline HTML tag"
DEFINITION = "a link reference or footnote definition"
CLAIM_IN_LIST = "a **Claim strength:** line inside a list item or block quote"
CLAIM_INDENTED = "a **Claim strength:** line indented from the start of its line"
CLAIM_IN_PARAGRAPH = "a **Claim strength:** line inside a paragraph"
CHART = "**Chart 1.** Bar: late share by region"
# Round 2: emphasis and other inline markup do not hide a phrase (Codex 1).
EMPHASIS = ["Price **leads** to sales", "Price **leads to** sales", "Price _leads_ to sales", "Price le**ad**s to sales",
            "Price ~~leads~~ to sales", "Price &#108;eads to sales", "Price lea​ds to sales",
            "Price lea<!-- -->ds to sales", "Price leads<br>to sales",
            "Price \\*leads\\* to sales", "Price \\_leads\\_ to sales", "Price ｌｅａｄｓ ｔｏ sales"]
# Round 3: a link's text joins the words around it, and a backslash hard break is whitespace (both reviews).
LINKS_AND_BREAKS = {"Price leads [to](https://example.com) sales": "leads to",
                    "Price due [to the outage](https://x.io)": "due to",
                    "This [lea](https://x.io)ds to churn": "leads to",
                    "The carrier [dri](https://x.io)ves late orders": "drives",
                    "Price [leads to](https://example.com) sales": "leads to",
                    "Price leads\\\n  to sales": "leads to",
                    "Price led\\\n  to churn": "led to",
                    # Round 4: a reference link never resolves, so its label shows; the phrase is found with the
                    # label read (Codex 2 nit in the Opus review) and with it dropped.
                    "See [a][drives] sales": "drives",
                    "Price [leads][x] to sales": "leads to"}

# Every probe a reviewer ran against the claim check in rounds 1 to 3, and each Markdown form the shared
# reader refuses or reads with them: (findings edits, methodology edits, represented results, claims rows,
# headings rows, markdown rows). A claims row is (phrase, line) or its section and problem; a headings row
# is (heading, problem); a markdown row is (file:line, what it refuses).
PROBES = {
    # Round 1: a ### headline is read with its slide (Opus 1, Codex 1).
    "headline": ([(WEST, f"### {HEADLINE}")], [(WEST, f"### {HEADLINE}")], ("r-009", "r-002"), [("drives", 10)], [],
                 []),
    "headline on the only result": ([(WEST, "### Discounts drive fewer late orders")],
                                    [(WEST, "### Discounts drive fewer late orders")], ("r-009",),
                                    [("drive", 6), ("drive", 10), (DISCOUNT, STATES_CAUSAL), ("led to", 19)], [], []),
    # Round 1: "contribute to" is causal; the noun "result in" and "affected" are not (Opus 2).
    "contribute to": ([(WEST_BULLET, "- The carrier contribute to late orders.\n- The result in June affected "
                                     "stores.")], [], ("r-009", "r-002"), [("contribute to", 12)], [], []),
    # Round 1: a **Caveat:** bullet on a finding slide is read (Opus 3).
    "caveat bullet": ([(WEST_BULLET, "- **Caveat:** the rise is due to holiday volume.")], [], ("r-009", "r-002"),
                      [("due to", 12)], [], []),
    # Round 1: a ~~~ line inside a backtick fence does not close it (Opus 4).
    "tilde in a backtick fence": ([("**Chart 1.**", "```\n~~~\n```\n- The carrier contribute to late orders.\n\n"
                                                    "**Chart 1.**")], [], ("r-009", "r-002"),
                                  [("contribute to", 18)], [], []),
    # Round 1: only a rendered declaration counts, and it names one strength (Codex 2, 4).
    "declaration in a comment": ([], [(WEST_CLAIM, f"<!--\n{WEST_CLAIM}\n-->")], ("r-009", "r-002"),
                                 [(WEST_DISCOUNT, NO_LINE)], [], []),
    "declaration in a fence": ([], [(WEST_CLAIM, f"```markdown\n{WEST_CLAIM}\n```")], ("r-009", "r-002"),
                               [(WEST_DISCOUNT, NO_LINE)], [], []),
    "declaration indented as code": ([], [(WEST_CLAIM, f"    {WEST_CLAIM}")], ("r-009", "r-002"),
                                     [(WEST_DISCOUNT, NO_LINE)], [], [("methodology.md:7", INDENTED_CODE)]),
    "two strengths on one line": ([], [(WEST_CLAIM, "**Claim strength:** association / causal")],
                                  ("r-009", "r-002"), [(WEST_DISCOUNT, UNRECOGNIZED)], [], []),
    "whitespace design": ([], [(WEST_CLAIM, "**Claim strength:** causal (experiment:  )")], ("r-009", "r-002"),
                          [(WEST_DISCOUNT, UNRECOGNIZED)], [], []),
    "two declarations": ([], [(WEST_CLAIM, f"{WEST_CLAIM}\n\n**Claim strength:** causal (experiment: a test)")],
                         ("r-009", "r-002"), [(WEST_DISCOUNT, "methodology.md's section has 2 **Claim strength:** "
                                                              "lines; its results support association")], [], []),
    # Round 1: a result ID in a comment is not a citation (Codex 3); a comment left open is refused (round 2
    # closure), and so is one inside a list item or quote, whose end CommonMark ties to the container (round 3
    # closure). A refused form is read as text, so the check fails on the markdown row.
    "citation in a comment": ([("Randomized discounts led to", "Randomized discounts drive")],
                              [(DISCOUNT_RESULT, "<!-- TODO: compare with r-002 -->")], ("r-009", "r-002"),
                              [(DISCOUNT, STATES_CAUSAL), ("drive", 19)], [], []),
    "citation in an unclosed comment": ([("Randomized discounts led to", "Randomized discounts drive")],
                                        [(DISCOUNT_RESULT, "<!-- TODO: compare with r-002")], ("r-009", "r-002"),
                                        [(DISCOUNT, STATES_CAUSAL), ("drive", 19)], [],
                                        [("methodology.md:15", COMMENT_OPEN)]),
    # Round 4: a reference link renders as written, since its definition is refused, so its label is a
    # citation (both closures); a plain citation is the control.
    "citation in a reference label": ([("Randomized discounts led to", "Randomized discounts drive")],
                                      [(DISCOUNT_RESULT, "Result r-002; also see [carrier comparison][r-009].")],
                                      ("r-009", "r-002"), [(DISCOUNT, STATES_CAUSAL), ("drive", 19)], [], []),
    "citation in plain text": ([("Randomized discounts led to", "Randomized discounts drive")],
                               [(DISCOUNT_RESULT, "Result r-002; also see carrier comparison r-009.")],
                               ("r-009", "r-002"), [(DISCOUNT, STATES_CAUSAL), ("drive", 19)], [], []),
    "citation in a comment in a list item": ([("Randomized discounts led to", "Randomized discounts drive")],
                                             [(DISCOUNT_RESULT, "- <!-- TODO: compare with r-002")], ("r-009", "r-002"),
                                             [], [], [("methodology.md:15", COMMENT_IN_LIST)]),
    "citation in a comment in a quote": ([("Randomized discounts led to", "Randomized discounts drive")],
                                         [(DISCOUNT_RESULT, "> <!-- TODO: compare with r-002")], ("r-009", "r-002"),
                                         [], [], [("methodology.md:15", COMMENT_IN_LIST)]),
    # Round 2: the declared design must be the one state.md records (Opus 1).
    "other design": ([], [(DISCOUNT_CLAIM, "**Claim strength:** causal (experiment: some unrelated survey)")],
                     ("r-009", "r-002"),
                     [(DISCOUNT, "methodology.md states causal (experiment: some unrelated survey) on its **Claim "
                                 "strength:** line; state.md records causal (experiment: randomized discount test) "
                                 "for r-002; its results support causal")], [], []),
    "same design, other spacing and emphasis": ([], [(DISCOUNT_CLAIM, "**Claim strength:** *causal (experiment:  "
                                                                      "randomized discount test)*")],
                                                ("r-009", "r-002"), [], [], []),
    # Round 2: verbs of change with an agent are a known limit of the list, stated in the contract (Opus 2).
    "verb of change": ([(WEST_BULLET, "- The carrier raised late orders 4 points.")], [], ("r-009", "r-002"), [], [],
                       []),
    # Round 2: a value in a code span reads as the value (Opus 3).
    "value in a code span": ([], [(WEST_CLAIM, "**Claim strength:** `association`")], ("r-009", "r-002"), [], [], []),
    **{f"inline markup: {text}": ([(WEST_BULLET, f"- {text}.")], [], ("r-009", "r-002"), [("leads to", 12)], [], [])
       for text in EMPHASIS},
    # An inline tag other than <br> is refused, since its attributes can hide text; its words are still read.
    "inline markup: Price <b>leads</b> to sales": ([(WEST_BULLET, "- Price <b>leads</b> to sales.")], [],
                                                   ("r-009", "r-002"), [("leads to", 12)], [],
                                                   [("findings.md:12", INLINE_TAG)]),
    "citation in a hidden span": ([], [(DISCOUNT_RESULT, '<span hidden>Result `r-002`.</span>')], ("r-009", "r-002"),
                                  [], [], [("methodology.md:15", INLINE_TAG)]),
    **{f"link or break: {text}": ([(WEST_BULLET, f"- {text}.")], [], ("r-009", "r-002"), [(phrase, 12)], [], [])
       for text, phrase in LINKS_AND_BREAKS.items()},
    # Round 2: a section commented out whole is no section (Codex 2, both closures).
    "methodology section commented out": (
        [], [(f"{WEST}\n", f"<!--\n{WEST}\n"), ("../../../../investigations/inv/evidence/r-009.json).",
                                                "../../../../investigations/inv/evidence/r-009.json).\n-->")],
        ("r-009", "r-002"), [(WEST_DISCOUNT, NO_SECTION)],
        [(WEST_DISCOUNT, "methodology.md has no ### section with this exact heading")], []),
    # Round 2: sections sharing a heading pool their evidence and are refused (Codex 3), compared as they
    # render, so a link in one heading does not set it apart (round 3 Codex closure).
    "duplicate methodology heading": (
        [], [(DISCOUNT_RESULT, f"{DISCOUNT_RESULT}\n\n### {DISCOUNT}\n\n{WEST_CLAIM}\n\nResult `r-009`.")],
        ("r-009", "r-002"),
        [(DISCOUNT, "methodology.md's section has 2 **Claim strength:** lines; its results support association"),
         ("led to", 19)],
        [(DISCOUNT, "methodology.md has 2 ### sections with this exact heading; merge them into one")], []),
    "duplicate methodology heading with a link": (
        [], [(DISCOUNT_RESULT, f"{DISCOUNT_RESULT}\n\n### Discounts cut late orders [by 4 points](https://example.com)"
                               f"\n\n{WEST_CLAIM}\n\nResult `r-009`.")],
        ("r-009", "r-002"),
        [(DISCOUNT, "methodology.md's section has 2 **Claim strength:** lines; its results support association"),
         ("led to", 19)],
        [(DISCOUNT, "methodology.md has 2 ### sections with this exact heading; merge them into one")], []),
    # Round 4: a code span in one heading does not set it apart either (Codex closure).
    "duplicate methodology heading with a code span": (
        [], [(DISCOUNT_RESULT, f"{DISCOUNT_RESULT}\n\n### Discounts cut late orders by `4` points"
                               f"\n\n{WEST_CLAIM}\n\nResult `r-009`.")],
        ("r-009", "r-002"),
        [(DISCOUNT, "methodology.md's section has 2 **Claim strength:** lines; its results support association"),
         ("led to", 19)],
        [(DISCOUNT, "methodology.md has 2 ### sections with this exact heading; merge them into one")], []),
    "duplicate findings heading": ([("## How we know", f"### {DISCOUNT}\n\n- Discounts led to it.\n\n## How we know")],
                                   [], ("r-009", "r-002"), [],
                                   [(DISCOUNT, "findings.md has 2 ### slides with this heading; give each finding "
                                               "its own")], []),
    # Round 2: a heading indented up to three spaces is a heading in both files (Codex 4, both closures).
    "indented headline": ([(WEST, f"   ### {HEADLINE}")], [(WEST, f"  ### {HEADLINE}")], ("r-009", "r-002"),
                          [("drives", 10)], [], []),
    # Round 3: a heading continuing a list item is refused and starts no slide, so an unchecked title cannot
    # switch the check off and the wording below it is read on the finding slide (both closures).
    "heading continuing a list item": ([(WEST_BULLET, "- Context\n\n  ## How we know\n\n  The carrier drives late "
                                                      "orders.")], [], ("r-009", "r-002"), [("drives", 16)], [],
                                       [("findings.md:14", HEADING_IN_LIST)]),
    "heading continuing a list item, other title": ([(WEST_BULLET, "- Context\n\n  ## Details\n\n  The carrier drives "
                                                                   "late orders.")], [], ("r-009", "r-002"),
                                                    [("drives", 16)], [], [("findings.md:14", HEADING_IN_LIST)]),
    "heading in a quote or list": ([(WEST_BULLET, f"> ### {HEADLINE}\n- # of stores rose")], [],
                                   ("r-009", "r-002"), [("drives", 12)], [],
                                   [("findings.md:12", HEADING_IN_LIST), ("findings.md:13", HEADING_IN_LIST)]),
    "heading indented as code": ([(WEST_BULLET, "\n    ### The carrier rose")], [], ("r-009", "r-002"), [], [],
                                 [("findings.md:13", INDENTED_CODE)]),
    "setext heading after an unchecked slide": ([("- June is short", "The carrier drives late orders\n---\n\n"
                                                                     "- June is short")], [], ("r-009", "r-002"), [],
                                                [], [("findings.md:26", SETEXT)]),
    "title heading after an unchecked slide": ([("## Limitations", "# The carrier drives late orders\n\n"
                                                                   "## Limitations")], [], ("r-009", "r-001"),
                                               [("drive", 6), (DISCOUNT, STATES_CAUSAL), ("led to", 19),
                                                ("drives", 27)], [], []),
    # Round 3: a declaration counts only as its own top-level paragraph at column 0; elsewhere it is refused
    # (Opus 3, and the fence in a list item of the Codex closure).
    "declaration in a fence in a list item": ([], [(WEST_CLAIM, f"- ```markdown\n  {WEST_CLAIM}\n  ```")],
                                              ("r-009", "r-002"), [(WEST_DISCOUNT, NO_LINE)], [],
                                              [("methodology.md:7", FENCE_IN_LIST), ("methodology.md:8", CLAIM_IN_LIST),
                                               ("methodology.md:9", FENCE_IN_LIST)]),
    "declaration as a list item": ([], [(WEST_CLAIM, f"- {WEST_CLAIM}")], ("r-009", "r-002"),
                                   [(WEST_DISCOUNT, NO_LINE)], [], [("methodology.md:7", CLAIM_IN_LIST)]),
    "declaration in a quote": ([], [(WEST_CLAIM, f"> {WEST_CLAIM}")], ("r-009", "r-002"),
                               [(WEST_DISCOUNT, NO_LINE)], [], [("methodology.md:7", CLAIM_IN_LIST)]),
    "declaration indented two spaces": ([], [(WEST_CLAIM, f"  {WEST_CLAIM}")], ("r-009", "r-002"),
                                        [(WEST_DISCOUNT, NO_LINE)], [], [("methodology.md:7", CLAIM_INDENTED)]),
    # Round 4: a declaration opening a paragraph counts, with text continuing it (Opus 3).
    "declaration opening a paragraph": ([], [(WEST_CLAIM, f"{WEST_CLAIM}\nResult `r-009` shows it.")],
                                        ("r-009", "r-002"), [], [], []),
    "declaration inside a paragraph": ([], [(WEST_CLAIM, f"The claim follows.\n{WEST_CLAIM}")], ("r-009", "r-002"),
                                       [(WEST_DISCOUNT, NO_LINE)], [], [("methodology.md:8", CLAIM_IN_PARAGRAPH)]),
    # The other forms outside the subset: indented code, an indented or unclosed fence, an indented comment,
    # and an HTML block are refused and read as text.
    "citation in indented code": ([], [(DISCOUNT_RESULT, f"    {DISCOUNT_RESULT}")], ("r-009", "r-002"), [], [],
                                  [("methodology.md:15", INDENTED_CODE)]),
    "fence never closed": ([(CHART, f"```\n{CHART}")], [], ("r-009", "r-002"), [], [],
                           [("findings.md:15", FENCE_OPEN)]),
    "fence indented two spaces": ([(CHART, f"{CHART}\n\n  ~~~\n  The carrier drives them.\n  ~~~")], [],
                                  ("r-009", "r-002"), [("drives", 18)], [],
                                  [("findings.md:17", FENCE_INDENTED), ("findings.md:19", FENCE_INDENTED)]),
    "comment indented two spaces": ([(CHART, f"{CHART}\n\n  <!-- The carrier drives them. -->")], [],
                                    ("r-009", "r-002"), [], [], [("findings.md:17", COMMENT_INDENTED)]),
    "citation in a link reference definition": ([], [(DISCOUNT_RESULT, "[r-002]: ../evidence/r-002.json")],
                                                ("r-009", "r-002"), [], [], [("methodology.md:15", DEFINITION)]),
    "HTML block": ([(CHART, f"<details>\nThe carrier drives late orders.\n</details>\n\n{CHART}")], [],
                   ("r-009", "r-002"), [("drives", 16)], [],
                   [("findings.md:15", HTML_BLOCK), ("findings.md:17", HTML_BLOCK)]),
    # Forms a differential run against a CommonMark parser turned up: an unmatched marker or an escaped
    # backtick or `<` shows as a character, so the word beside it is read; a numbered item ends the one
    # before it; an item opened empty ends at a blank line, so what follows indented four spaces is code.
    "unmatched marker": ([(WEST_BULLET, "- The carrier*drives late orders.")], [], ("r-009", "r-002"),
                         [("drives", 12)], [], []),
    "escaped backtick": ([(WEST_BULLET, "- See \\`the carrier drives them\\`.")], [], ("r-009", "r-002"),
                         [("drives", 12)], [], []),
    "escaped comment opener": ([(WEST_BULLET, "- The carrier \\<!-- x -->drives them.")], [], ("r-009", "r-002"),
                               [("drives", 12)], [], []),
    "heading in a second numbered item": ([(WEST_BULLET, "1. Late orders rose.\n2. ### The carrier drives late "
                                                         "orders")], [], ("r-009", "r-002"), [("drives", 13)], [],
                                          [("findings.md:13", HEADING_IN_LIST)]),
    "indented code after an empty item": ([(WEST_BULLET, "-\n\n    The carrier drives them.")], [],
                                          ("r-009", "r-002"), [("drives", 14)], [], [("findings.md:14", INDENTED_CODE)]),
    # Comments as CommonMark scopes them.
    "comment open across a blank line": ([(WEST_BULLET, "- Late orders rose <!-- note\n\n- The carrier drives "
                                                        "them -->")], [], ("r-009", "r-002"), [("drives", 14)], [],
                                         [("findings.md:12", COMMENT_OPEN)]),
    "comment opener in a code span": ([(WEST_BULLET, "- See `<!--`, the carrier drives them `-->`.")], [],
                                      ("r-009", "r-002"), [("drives", 12)], [], []),
    "text after a comment block": ([(WEST_BULLET, "<!-- note --> The carrier drives them.")], [],
                                   ("r-009", "r-002"), [("drives", 12)], [], []),
}


@pytest.mark.parametrize("probe", PROBES)
def test_review_probes_read_markdown_as_it_renders(project, probe):
    findings_edits, methodology_edits, results, claims_rows, headings_rows, markdown_rows = PROBES[probe]
    findings, methodology = CLEAN_FINDINGS, CLAIM_METHODOLOGY
    for old, new in findings_edits:
        assert old in findings, old
        findings = findings.replace(old, new, 1)
    for old, new in methodology_edits:
        assert old in methodology, old
        methodology = methodology.replace(old, new, 1)
    claim_draft(project, findings, methodology, results)
    draft = load(project / "src/packaging/draft.py", "draft_probes")
    directory = project / "deliveries/inv/pkg/draft"
    rows = draft.claim_problems(directory, list(results), draft.state_claims(project, "inv"))
    assert [(r["phrase"], r["line"]) if "phrase" in r else (r["section"], r["problem"]) for r in rows] == claims_rows
    assert [(r["heading"], r["problem"]) for r in draft.heading_problems(directory)] == headings_rows
    refused = draft.markdown_problems(directory)
    assert [(f"{r['file']}:{r['line']}", r["problem"].split(" at line ")[0]) for r in refused] == [
        (place, f"unsupported Markdown: {what}") for place, what in markdown_rows]
    assert all(r["problem"].startswith(f"unsupported Markdown: {r['problem'][22:].split(' at line ')[0]} at line "
                                       f"{r['line']}; rewrite as ") for r in refused)


def test_unsupported_markdown_fails_check_draft(project, capsys):
    # The round-3 list-continuation heading: refused, and its wording read on the finding slide.
    claim_draft(project, CLEAN_FINDINGS.replace(WEST_BULLET, "- Context\n\n  ## How we know\n\n  Price drives sales."))
    code, report = run(project, capsys, "check-draft", "inv", "pkg", "--verify-only")
    assert code == 1 and not report["passed"]
    assert report["markdown"] == [{"file": "findings.md", "line": 14, "problem": (
        "unsupported Markdown: a heading inside a list item or block quote at line 14; rewrite as a heading at the "
        "start of its own line, outside lists and quotes")}]
    assert [(row["phrase"], row["line"]) for row in report["claims"]] == [("drives", 16)]
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 1 and report["check"]["markdown"] == [{"file": "findings.md", "line": 14, "problem": (
        "unsupported Markdown: a heading inside a list item or block quote at line 14; rewrite as a heading at the "
        "start of its own line, outside lists and quotes")}]


def test_names_and_charts_read_the_same_rendered_text(project):
    draft = load(project / "src/packaging/draft.py", "draft_rendered")
    path = project / "deliveries/inv/pkg/draft/findings.md"
    # A comment opened mid-paragraph ends with the paragraph, so its text shows; one opening a line runs to
    # its -->, here the end of the file, hiding the chart specification.
    path.write_text("# T\n\nSee orders_view <!-- open\n\nThen regions_table -->\n\n<!-- orders_view\n\n"
                    "**Chart 1.** Bar\n")
    assert draft.check_findings(path, names=["orders_view", "regions_table"]) == [
        {"line": 3, "kind": "name", "text": "orders_view"}, {"line": 5, "kind": "name", "text": "regions_table"}]
    assert draft.check_charts(path, path.parent / "charts") == [
        {"chart": "Chart 1", "problem": "chart file has no specification in findings"}]
    # Escapes, character references, zero-width characters, and emphasis render a name or a chart number
    # whole, so the names scan and the chart check read it as the claims check does (round 3, both reviews):
    # chart-1.csv now has its specification.
    path.write_text("Read from orders\\_view, orders&#95;view, orders​_view, and orders_**view**.\n"
                    "Result r\\-009, r&#45;009, and [r-009](../evidence/r-009.json).\n\n"
                    + CHART_SPEC.replace("Chart 1.", "Chart &#49;."))
    assert draft.check_findings(path, names=["orders_view", "r-009"]) == (
        [{"line": 1, "kind": "name", "text": "orders_view"}] * 4 + [{"line": 2, "kind": "name", "text": "r-009"}] * 3)
    assert draft.check_charts(path, path.parent / "charts") == []
    # A reference link renders as written, since its definition is refused, so its label is visible (round 4,
    # both reviews); a code span crossing a line break is code, reported at its opening line (round 4, Codex 2).
    path.write_text("See [the view][orders_view] and [calculation][orders_view].\n\n"
                    "The calculation `COUNT(*)\nFILTER (WHERE late)` rose, and so did `x`.\n")
    assert draft.check_findings(path, names=["orders_view"]) == [
        {"line": 1, "kind": "name", "text": "orders_view"}, {"line": 1, "kind": "name", "text": "orders_view"},
        {"line": 3, "kind": "code", "text": "`COUNT(*) FILTER (WHERE late)`"}, {"line": 4, "kind": "code", "text": "`x`"}]
    path.write_text("The calculation `COUNT(*) FILTER (WHERE late)` rose.\n")
    assert draft.check_findings(path) == [{"line": 1, "kind": "code", "text": "`COUNT(*) FILTER (WHERE late)`"}]


def test_claim_check_reads_headlines_and_cited_designs(project, capsys):
    draft = load(project / "src/packaging/draft.py", "draft_headlines")
    claims = draft.state_claims(project, "inv")
    directory = project / "deliveries/inv/pkg/draft"
    # A finding slide's ### heading is its headline, read with the slide; the row says to reword both files.
    claim_draft(project, CLEAN_FINDINGS.replace(WEST, f"### {HEADLINE}"), CLAIM_METHODOLOGY.replace(WEST, f"### {HEADLINE}"))
    code, report = run(project, capsys, "check-draft", "inv", "pkg", "--verify-only")
    assert code == 1 and not report["passed"]
    assert report["claims"] == [{
        "line": 10, "section": HEADLINE, "phrase": "drives", "claim": "association", "results": ["r-009"],
        "problem": "causal wording above the association claim strength; reword it, since only an experiment or an "
                   "identified natural experiment supports a causal claim; reword the methodology.md heading to match"}]
    # Causal results recorded with different designs cannot share one causal finding.
    claim_draft(project, CLEAN_FINDINGS, CLAIM_METHODOLOGY.replace(DISCOUNT_RESULT, "Results `r-002` and `r-003`."),
                results=("r-009", "r-002", "r-003"))
    rows = draft.claim_problems(directory, ["r-009", "r-002", "r-003"],
                                {**claims, "r-003": "causal (natural experiment: border policy change)"})
    assert rows == [{"section": DISCOUNT, "problem": (
        "the results it cites record different causal designs (causal (experiment: randomized discount test) for "
        "r-002; causal (natural experiment: border policy change) for r-003); give each design its own finding; its "
        "results support causal")}]
    # A causal Claim cell needs design text, not just spaces.
    state = project / "investigations/inv/state.md"
    state.write_text(state.read_text().replace("(experiment: randomized discount test)", "(experiment:  )"))
    assert draft.state_claims(project, "inv")["r-002"] is None


def test_claim_strength_follows_cited_results_and_records(project, capsys):
    draft = load(project / "src/packaging/draft.py", "draft_claims")
    claims = draft.state_claims(project, "inv")
    assert claims == {"r-009": "association", "r-001": "association",
                      "r-002": "causal (experiment: randomized discount test)"}
    directory = project / "deliveries/inv/pkg/draft"
    clean = CLAIM_FINDINGS.replace("The new carrier drives the rise", "Late orders rose")
    # Citing r-009 too holds the discount slide to the weaker association claim.
    claim_draft(project, clean, CLAIM_METHODOLOGY.replace("Result `r-002`.", "Results `r-002` and `r-009`."))
    rows = draft.claim_problems(directory, ["r-009", "r-002"], claims)
    assert [(r.get("section"), r.get("phrase")) for r in rows] == [
        ("Discounts cut late orders by 4 points", None), ("Discounts cut late orders by 4 points", "led to")]
    assert rows[0]["problem"] == ("methodology.md states causal on its **Claim strength:** line; its results "
                                  "support association")
    # Without a causal represented finding, the Answer slide is held to association as well.
    claim_draft(project, clean, CLAIM_METHODOLOGY, results=("r-009", "r-001"))
    rows = draft.claim_problems(directory, ["r-009", "r-001"], claims)
    assert [(r.get("section"), r.get("phrase"), r.get("line")) for r in rows] == [
        ("Answer", "drive", 6), ("Discounts cut late orders by 4 points", None, None),
        ("Discounts cut late orders by 4 points", "led to", 19)]
    # A phrase across a line break is found at its first line.
    split = clean.replace("Randomized discounts led to", "Late orders fell\nbecause of discounts, by")
    claim_draft(project, split)
    rows = draft.claim_problems(directory, ["r-009", "r-002"], {**claims, "r-002": "association"})
    assert [(r.get("phrase"), r.get("line")) for r in rows if r.get("phrase")] == [("drive", 6), ("because of", 20)]
    # Code spans, fenced blocks, and link text targets are not wording.
    claim_draft(project, clean.replace("Late orders rose to 21%", "Late orders rose to 21% (`drives`)")
                + "\n```\ndrives\n```\n[link](drives.md)\n")
    assert draft.claim_problems(directory, ["r-009", "r-002"], claims) == []
    # A represented result without a recognized Claim, or with no row, fails.
    rows = draft.claim_problems(directory, ["r-009", "r-002", "r-003"], {**claims, "r-002": None})
    assert rows[:2] == [
        {"result": "r-002", "problem": "state.md's Claim cell is not descriptive, association, or causal with its "
                                       "design basis"},
        {"result": "r-003", "problem": "state.md has no findings row with a claim strength for this result"}]
    claim_draft(project, clean, CLAIM_METHODOLOGY.replace("**Claim strength:** association\n", ""))
    rows = draft.claim_problems(directory, ["r-009", "r-002"], claims)
    assert rows == [{"section": "Late orders rose in the west",
                     "problem": "methodology.md's section has no **Claim strength:** line opening a top-level "
                                "paragraph; its results support association"}]
    # The rendered table without a Claim column, and a manifest without results, are errors.
    state = project / "investigations/inv/state.md"
    state.write_text(state.read_text().replace("| Claim |", "| Strength |"))
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and any(e.startswith("claims: investigations/inv/state.md has no Current findings table with "
                                          "Evidence and Claim columns") for e in report["errors"])
    write(project, "investigations/inv/state.md", STATE.format(status="supported", reason=""))
    record = json.loads((directory / "manifest.json").read_text())
    del record["results"]
    (directory / "manifest.json").write_text(json.dumps(record))
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and "manifest: manifest.json records no results list; rerun export" in report["errors"]


HOLDOUT = "causal (experiment: randomized holdout of 2024 Q3, 50/50 split)"


def test_numbers_skip_a_claim_strength_line_the_claims_check_accepts(project, capsys):
    # A causal **Claim strength:** line repeats state.md's Claim cell, design basis included, so once the claims
    # check accepts it its numbers trace to the record and the numbers check skips that line.
    write(project, "investigations/inv/state.md", STATE.format(status="supported", reason="").replace(
        "causal (experiment: randomized discount test)", HOLDOUT))
    claim_draft(project, DECK_FINDINGS, CLAIM_METHODOLOGY.replace(DISCOUNT_CLAIM, f"**Claim strength:** {HOLDOUT}"))
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert report["claims"] == [] and report["numbers"] == [] and code == 0 and report["passed"]
    # Only that source line is skipped: a number on the line continuing its paragraph is read.
    claim_draft(project, DECK_FINDINGS, CLAIM_METHODOLOGY.replace(
        DISCOUNT_CLAIM, f"**Claim strength:** {HOLDOUT}\nacross 77 stores"))
    report = run(project, capsys, "check-draft", "inv", "pkg")[1]
    assert report["claims"] == [] and report["numbers"] == [
        {"file": "methodology.md", "line": 14, "text": "77", "problem": NOT_RECORDED}]
    # A line the claims check refuses keeps its numbers: another design, or the issue's line, which names no
    # experiment or natural experiment.
    for declared in (HOLDOUT.replace("Q3", "Q4"), "causal (randomized holdout of 2024 Q3, 50/50 split)"):
        claim_draft(project, DECK_FINDINGS, CLAIM_METHODOLOGY.replace(DISCOUNT_CLAIM, f"**Claim strength:** {declared}"))
        code, report = run(project, capsys, "check-draft", "inv", "pkg")
        assert code == 1 and [row["section"] for row in report["claims"]] == [DISCOUNT]
        assert report["numbers"] == [{"file": "methodology.md", "line": 13, "text": text, "problem": problem}
                                     for text, problem in (("2024", YEAR_COUNT), ("50", NOT_RECORDED),
                                                           ("50", NOT_RECORDED))]
    # Without the claims check's accepted lines, check_numbers reads every line.
    draft = load(project / "src/packaging/draft.py", "draft_claim_numbers")
    path = project / "deliveries/inv/pkg/draft/methodology.md"
    assert [row["text"] for row in draft.check_numbers(path, [Decimal(4)])] == ["2024", "50", "50"]
    assert draft.check_numbers(path, [Decimal(4)], claim_lines={13}) == []


@pytest.mark.parametrize("brk", ["\u2028", "\x0c", "\x85"])
def test_numbers_count_lines_as_the_claims_check_does_after_a_comment(project, capsys, brk):
    # A comment holding a line break that str.splitlines() sees but "\n" does not must not shift the numbers
    # check's line numbers off the claims check's, or the skip lands on the line after the accepted claim.
    comment = f"## Findings\n<!-- note{brk}more -->"
    claim_draft(project, DECK_FINDINGS, CLAIM_METHODOLOGY.replace("## Findings", comment)
                .replace(DISCOUNT_CLAIM, f"{DISCOUNT_CLAIM}\nacross 77 stores"))
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and report["claims"] == []
    assert report["numbers"] == [{"file": "methodology.md", "line": 16, "text": "77", "problem": NOT_RECORDED}]
    write(project, "investigations/inv/state.md", STATE.format(status="supported", reason="").replace(
        "causal (experiment: randomized discount test)", HOLDOUT))
    claim_draft(project, DECK_FINDINGS, CLAIM_METHODOLOGY.replace("## Findings", comment)
                .replace(DISCOUNT_CLAIM, f"**Claim strength:** {HOLDOUT}\nacross 77 stores"))
    report = run(project, capsys, "check-draft", "inv", "pkg")[1]
    assert report["claims"] == [] and report["numbers"] == [
        {"file": "methodology.md", "line": 16, "text": "77", "problem": NOT_RECORDED}]


# Where a <!-- stands around "Renewals fell 37% in Q3.", and the numbers check_numbers reports with no recorded value
# tracing 37 or 40: a <!-- that opens no comment as the draft renders hides nothing, and a comment hides what it holds.
UNTRACED = "Renewals fell 37% in Q3."
COMMENT_SHAPES = {
    # The issue's three shapes, and an empty comment, each with a later --> that once closed a comment.
    "a code span holding <!-- before it, and one holding --> after it": (
        f"A note opens with `<!--`.\n\n{UNTRACED}\n\nIt closes with `-->`.\n", ["37%"]),
    "an escaped <!-- before it, and a bare --> after it": (
        f"A note opens with \\<!--.\n\n{UNTRACED}\n\nIt closes with -->.\n", ["37%"]),
    "a fenced block holding <!-- before it, and a bare --> in later prose": (
        f"```\n<!--\n```\n\n{UNTRACED}\n\nIt closes with -->.\n", ["37%"]),
    "an empty comment <!--> before it, and a bare --> after it": (
        f"Notes <!--> go here.\n\n{UNTRACED}\n\nIt closes with -->.\n", ["37%"]),
    # The same within one paragraph, where the reading once took the <!-- for a comment's start.
    "a code span holding <!-- after an escaped backslash": (f"Write C:\\\\`<!--` then {UNTRACED} Then `-->` ends it.\n",
                                                           ["37%"]),
    "a code span holding <!-- after an escaped backtick": (f"A tick \\``<!--` then {UNTRACED} Then `-->` ends it.\n",
                                                          ["37%"]),
    "a link's title holding <!--": (f"See [the note](x.png \"<!--\"). {UNTRACED} It closes with -->.\n", ["37%"]),
    "a link's target holding <!--": (f"See [the note](<!--x>). {UNTRACED} It closes with -->.\n", ["37%"]),
    "escaped backticks around it, which open no code span": ("Renewals fell \\` then 37% in Q3 \\` end.\n", ["37%"]),
    # Controls, and comments where a column or a line of the source differs from the rendered text's.
    "no <!--": (f"{UNTRACED}\n", ["37%"]),
    "one code span holding <!-- x -->": (f"A note is written `<!-- x -->`.\n\n{UNTRACED}\n", ["37%"]),
    "a comment holding it": (f"<!--\n{UNTRACED}\n-->\n", []),
    "a comment within its paragraph": (f"Notes <!-- {UNTRACED} --> go here.\n", []),
    "a comment within a link's text": (f"See [the note <!-- {UNTRACED} -->](x.png).\n", []),
    "a comment opened in a stray ](...), which no [ makes a target": (f"Intro ](x<!--) {UNTRACED} -->\n", []),
    "a comment opened after a \\ before a space, which ends a target": (f"See [a](x\\ <!--) {UNTRACED} -->\n", []),
    "a comment across lines of a list item": (f"- Notes <!-- a\n  {UNTRACED} --> about 40 stores\n", ["40"]),
    "a comment after tabs": (f"Notes\t\t<!-- {UNTRACED} -->\t40 stores.\n", ["40"]),
    "a comment in a heading": (f"## Notes <!-- {UNTRACED} --> 40 ##\n", ["40"]),
    "a comment never closed, which the markdown check refuses": (f"<!--\n{UNTRACED}\n", []),
    "a comment never closed, before an empty last line": (f"<!--\n{UNTRACED}\n\n", []),
    "a comment never closed, ending the file without a line break": (f"<!--\n{UNTRACED}", []),
    "a comment ending the file without a line break": (f"{UNTRACED}\n<!--\nnote\n-->", ["37%"]),
}


@pytest.mark.parametrize("shape", COMMENT_SHAPES)
def test_numbers_check_drops_only_the_comments_the_draft_renders(tmp_path, shape):
    draft = load(ASSETS["src/packaging/draft.py"], "draft_comment_shapes")
    text, rows = COMMENT_SHAPES[shape]
    path = tmp_path / "methodology.md"
    path.write_text(text)
    assert [row["text"] for row in draft.check_numbers(path, [Decimal(12)])] == rows
    # The rendered view the other checks read shows the sentence exactly when the numbers check reads it, and the
    # numbers check reads every line the view holds outside fenced code, so their line numbers agree.
    view = draft._read_view(path)[0]
    assert any("37%" in line.plain for line in view) == ("37%" in rows)
    assert [number for number, _, _ in draft._unfenced(path)] == [line.number for line in view if line.kind != "code"]


@pytest.mark.parametrize("text, refused", [
    ("See [the note](x.png \"<!--\") here.\n", False),
    ("See [the note](<!--x>) here.\n", False),
    ("Write C:\\\\`<!--` here.\n", False),
    ("A tick \\``<!--` here.\n", False),
    ("Write \\<!-- here.\n", False),
    ("Notes <!-- here.\n", True),
    ("Notes `x` <!-- here.\n", True),
])
def test_a_comment_marker_written_as_text_is_no_comment_never_closed(text, refused):
    # A <!-- in a link's target or title, a code span, or an escape opens no comment, so it is no comment left
    # open either; one in plain text that no --> closes within its paragraph is still refused.
    draft = load(ASSETS["src/packaging/draft.py"], "draft_comment_open")
    assert [problem for _, problem in draft._view(text)[1]] == (
        ["unsupported Markdown: a comment never closed at line 1; rewrite as a comment closed with --> in the same "
         "paragraph, or delete it"] if refused else [])


def test_check_draft_reads_numbers_after_a_comment_marker_written_as_text(project, capsys):
    # The issue's first shape in methodology.md: release's mechanical check reports the untraced number.
    draft = project / "deliveries/inv/pkg/draft"
    write(draft, "methodology.md", METHODOLOGY + f"\nA note opens with `<!--`.\n\n{UNTRACED}\n\nIt closes with `-->`.\n")
    rows = [{"file": "methodology.md", "line": 15, "text": "37%", "problem": NOT_RECORDED}]
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and report["numbers"] == rows
    code, report = run(project, capsys, "check-draft", "inv", "pkg", "--verify-only")
    assert code == 1 and report["numbers"] == rows and report["verify"] == []
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 1 and report["check"]["numbers"] == rows
    assert not (project / "deliveries/inv/pkg/released").exists()


# Pieces of the random narratives the agreement check reads: comment markers, code spans, escapes, fences, containers,
# tabs, and the line breaks str.splitlines() sees. Its words are unique markers, zq1x, zq2x, ..., which no markup changes.
CORPUS_INLINE = ("fell", "37%", "<!--", "-->", "<!-->", "<!--->", "\\<!--", "\\\\<!--", "`", "``", "`<!--`", "`-->`",
                 "\\", "\\\\`", "\\``", " ", "\t", "[", "]", "![", "*", "_", "##", "](x.png \"<!--\")", "](<!--x>)",
                 "](x(<!--(y)).png)", "](x\\(<!--.png)", "](x \"a\\\"<!--\")", "<a`b@e.com>")
CORPUS_STARTS = ("", "", "", "- ", "> ", "# ", "1. ", "```", "~~~", "    ", "  ", "\t", "> - ", "<!-- ", "---")
CORPUS_BREAKS = ("\n", "\n", "\n\n", "\r\n", "\u2028", "\x0c", "\x85", "")


def test_numbers_check_and_rendered_view_drop_the_same_comments(tmp_path):
    # Across a random corpus, the words the rendered view drops as comment are exactly the words the numbers check's
    # source lines blank. Fenced code, which both skip, is set aside, so a marker missing from the view was in a comment.
    draft = load(ASSETS["src/packaging/draft.py"], "draft_comment_agreement")
    rng, path, hidden = random.Random(79), tmp_path / "methodology.md", 0
    for _ in range(2000):
        pieces, markers = [], []
        for _ in range(rng.randint(1, 12)):
            pieces.append(rng.choice(CORPUS_STARTS))
            for _ in range(rng.randint(0, 6)):
                if rng.random() < 0.35:
                    markers.append(f"zq{len(markers)}x")
                    pieces.append(f" {markers[-1]} ")
                else:
                    pieces.append(rng.choice(CORPUS_INLINE))
            pieces.append(rng.choice(CORPUS_BREAKS))
        path.write_bytes("".join(pieces).encode())
        view, _, _, spans = draft._read_view(path)
        text = path.read_text(encoding="utf-8")
        code = " ".join(text.splitlines()[line.number - 1] for line in view if line.kind == "code")
        shown = " ".join(line.plain for line in view if line.kind != "code") + " " + code
        # The numbers check also blanks code spans, by design, so their words are kept, not dropped as comment.
        kept = " ".join(line for _, line, _ in draft._unfenced(path)) + " " + code + " " + " ".join(
            text[start:end] for start, end in spans)
        dropped = [marker for marker in markers if marker not in shown]
        assert dropped == [marker for marker in markers if marker not in kept], "".join(pieces)
        assert [number for number, _, _ in draft._unfenced(path)] == [line.number for line in view
                                                                       if line.kind != "code"], "".join(pieces)
        hidden += len(dropped)
    assert hidden > 1000  # the corpus puts many words in comments, so it tests agreement rather than assuming it


# Code spans in hard-wrapped prose, and the rows check_numbers gives with no recorded value tracing 37 or 40: a code
# span pairs its own backticks across the whole paragraph, as the draft renders it, never within a line's window.
WRAPPED_CODE = {
    "a span closing on the line above another span": (
        "We kept rows where `status =\n'active'` held.\nThat left 37% of accounts, per `orders`.\n", [(3, "37%")]),
    "a span closing two lines above another span": (
        "We filtered on `status =\n'active'` rows.\nThat left 37% of accounts.\nSee `orders` for details.\n", [(3, "37%")]),
    "a span over three lines before one over two": ("Run `a\nb\nc` and renewals fell 37% in Q3 `x\nd`.\n", [(3, "37%")]),
    "control: the first span on one line": (
        "We kept rows where `status = 'active'` held.\nThat left 37% of accounts, per `orders`.\n", [(2, "37%")]),
    "a number inside a span wrapped across lines": ("We kept rows where `status =\n40 'active'` held.\n", []),
    # A span opening a line, or a line all code, leaves the next line wrapping it, so 377. starts no list.
    "a line opening with a span before a numbered line": (
        "Monthly orders per account in\n`orders_view` rose to\n377. Orders per account fell 12%.\n", [(3, "377")]),
    "the same in a quote": (
        "> Monthly orders per account in\n> `orders_view` rose to\n> 377. Orders per account fell 12%.\n", [(3, "377")]),
    "a line all code before a numbered line": (
        "We counted the accounts matching\n`status = 'active'`\n377. Of those, 341% renewed.\n", [(3, "377"), (3, "341%")]),
    "a wrapped span's end opening the line before a numbered line": (
        "We filtered `status =\n'active'` and got\n377. Done.\n", [(3, "377")]),
}


@pytest.mark.parametrize("shape", WRAPPED_CODE)
def test_numbers_check_pairs_code_spans_across_the_paragraph(tmp_path, shape):
    draft = load(ASSETS["src/packaging/draft.py"], "draft_wrapped_code")
    text, rows = WRAPPED_CODE[shape]
    path = tmp_path / "methodology.md"
    path.write_text(text)
    assert [(row["line"], row["text"]) for row in draft.check_numbers(path, [Decimal(12)])] == rows


def test_an_allowed_text_quoting_a_code_span_covers_its_number(tmp_path):
    # Allowed texts match the line as written, code spans included, though numbers are read with them blanked.
    draft = load(ASSETS["src/packaging/draft.py"], "draft_allowed_code")
    path = tmp_path / "methodology.md"
    path.write_text("Per `orders` 40 stores.\n")
    assert [row["text"] for row in draft.check_numbers(path, [])] == ["40"]
    assert draft.check_numbers(path, [], allowed={"`orders` 40"}) == []


def storyline_fixture(project):
    state = project / "investigations/inv/state.md"
    write(project, "investigations/inv/state.md", state.read_text().replace("causal (experiment: randomized discount test)", "association"))
    provenance = load(project / "src/provenance.py", "ledger_story_fixture")
    for text, parent, priority in [
        ("How large is the change?", "", "should"),
        ("Where is the change?", "Q-001", "must"),
        ("Which customers changed?", "", "must"),
        ("Which detail helps?", "", "could"),
    ]:
        provenance.add_question(project, "inv", text, kind="analytical", answerer="data", origin="scope",
                                parent=parent, priority=priority)
    settings = project / "investigations/inv/settings.toml"
    settings.write_text(settings.read_text().replace('[results.r-001]', '[results.r-001]\nanswers = ["Q-001", "Q-002"]')
                        .replace('[results.r-002]', '[results.r-002]\nanswers = ["Q-003"]'))
    for question, result in (("Q-001", "r-001"), ("Q-002", "r-001"), ("Q-003", "r-002")):
        provenance.answer_question(project, "inv", question, results=[result])
    draft = project / "deliveries/inv/pkg/draft"
    shutil.rmtree(draft / "charts")
    set_manifest(project, charts="none")
    write(draft, "methodology.md", "# Methodology\n\n## Findings\n\n"
          "### Customer rates differ\n\n**Claim strength:** association\n\n[r-002](../../../../investigations/inv/evidence/r-002.json)\n\n"
          "### Regional rates differ\n\n**Claim strength:** association\n\nResult: r-001\n\n"
          "### Coverage remains limited\n\n**Claim strength:** association\n\nNo recorded answer is claimed here.\n\n"
          "How many claims closed late?\n\nWhich regions close claims late?\n")
    return draft


# Only slides outside the longest run already in order are reported, so one moved slide is one row.
@pytest.mark.parametrize("headlines, misplaced", [
    (["Customer rates differ", "Regional rates differ", "Coverage remains limited"], []),
    (["Regional rates differ", "Customer rates differ", "Coverage remains limited"],
     [("Regional rates differ", "Q-002", 2)]),
    (["Coverage remains limited", "Customer rates differ", "Regional rates differ"],
     [("Coverage remains limited", None, 3)]),
    (["Coverage remains limited", "Regional rates differ", "Customer rates differ"],
     [("Coverage remains limited", None, 3), ("Regional rates differ", "Q-002", 2)]),
])
def test_check_draft_orders_findings_from_priority_then_tree(project, capsys, headlines, misplaced):
    draft = storyline_fixture(project)
    write(draft, "findings.md", deck("".join(f"### {headline}\n\n- Rates vary across groups.\n\n**Notes:** Compare the "
                                             "groups.\n\n" for headline in headlines)))
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert [(row["slide"], row["question"], row["expected_position"]) for row in report["storyline"]] == misplaced
    assert report["unlinked_findings"] == ["Coverage remains limited"]
    assert report["passed"] is (not misplaced), report
    assert code == (1 if misplaced else 0)
    # Read-only verification uses the same checks and reports the same rows.
    _, verified = run(project, capsys, "check-draft", "inv", "pkg", "--verify-only")
    assert verified["storyline"] == report["storyline"]


@pytest.mark.parametrize("required, body, placement, problem, text, audience", [
    (*case, "What caused the delay?", "") for case in [
    (False, None, "after", None),
    (False, "- What caused the delay?", "after", "no unanswered must"),
    (True, None, "after", "missing Open questions"),
    (True, "- What caused the delay?", "after", None),
    (True, "* What **caused** the delay?", "after", None),
    (True, "1. What [caused](https://example.invalid) the delay?", "after", None),
    (True, "- What caused\n  the delay?", "after", None),
    (True, "- Why were orders late?", "after", "missing question"),
    (True, "- Q-001: What caused the delay?", "after", "unexpected question"),
    (True, "- What caused the delay?\n- What caused the delay?", "after", "repeated question"),
    (True, "- What caused the delay?\n  - Ask the owner", "after", "nested bullets"),
    (True, "- What caused the delay?", "before", "after Limitations"),
    (True, "- What caused the delay?", "late", "before What changed"),
    (True, "- What caused the delay?", "twice", "exactly one"),
    (True, "What caused the delay?", "after", "missing question"),
    (True, "- What caused the delay?\n\n**Chart 2.** Table: supporting rates\n- **Data:** column: Rate", "after", "takes no chart"),
]] + [
    (True, "- Why were orders late?", "after", None, "What caused the delay?", "Why were orders late?"),
    (True, "- Why were orders late?", "after", None, "What caused the delay?", "Why were **orders** late?"),
    (True, "- What caused the delay?", "after", "missing question", "What caused the delay?", "Why were orders late?"),
    (True, "- Does late_rate differ?", "after", 'questions edit Q-001 --audience "<wording>"', "Does late_rate differ?", ""),
    (True, "- Does performance differ?", "after", 'questions edit Q-001 --audience "<wording>"', "Does late_rate differ?", ""),
    (True, "- Do orders differ?", "after", None, "Does orders_view differ?", "Do orders differ?"),
    (True, "- Does orders_view differ?", "after", 'questions edit Q-001 --audience "<wording>"', "Does orders_view differ?", ""),
])
def test_check_draft_open_questions_rows(project, capsys, required, body, placement, problem, text, audience):
    provenance = load(project / "src/provenance.py", "ledger_open_fixture")
    provenance.add_question(project, "inv", text, kind="context", answerer="user",
                            origin="scope", priority="must" if required else "could", audience=audience)
    # A parked must remains unresolved; set-aside and settled questions are excluded.
    for text, state in (("Which period?", "declined"), ("Which definition?", "superseded"), ("Which scope?", "answered")):
        entry = provenance.add_question(project, "inv", text, kind="context", answerer="user", origin="scope", priority="must")
        if state == "answered":
            provenance.answer_question(project, "inv", entry["id"], text="Current scope", by="user")
        else:
            provenance.set_question(project, "inv", [entry["id"]], state, reason="Set aside")
    draft = project / "deliveries/inv/pkg/draft"
    limitations = "\n## Limitations and open caveats\n\n**Headline:** Coverage remains limited\n\n**Notes:** Interpret with care.\n"
    changed = "\n## What changed since the last version\n\n**Headline:** Coverage is clearer\n\n**Notes:** Definitions are clearer.\n"
    opened = ("\n## Open questions\n\n**Headline:** Some questions remain\n\n" + body +
              "\n\n**Notes:** These answers matter.\n") if body is not None else ""
    parts = {"after": limitations + opened + changed, "before": opened + limitations + changed,
             "late": limitations + changed + opened, "twice": limitations + opened + opened + changed}
    write(draft, "findings.md", BASE + parts[placement])
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    if problem:
        assert code == 1 and any(problem in row["problem"] for row in report["open_questions"]), report
    else:
        assert report["open_questions"] == [] and code == 0 and report["passed"], report
    _, verified = run(project, capsys, "check-draft", "inv", "pkg", "--verify-only")
    assert verified["open_questions"] == report["open_questions"]


def test_open_questions_includes_parked_and_recheck_without_truncation(project, capsys):
    provenance = load(project / "src/provenance.py", "ledger_complete_fixture")
    questions = ["Which regions need review?", "Which period applies?", "Which owner decides?",
                 "Which population matters?", "Which definition applies?", "Which caveat matters?"]
    for index, text in enumerate(questions):
        provenance.add_question(project, "inv", "Which regions in orders_view need review?" if index == 0 else text, kind="context", answerer="data" if index == 0 else "user",
                                origin="scope", priority="must")
    settings = project / "investigations/inv/settings.toml"
    settings.write_text(settings.read_text().replace('[results.r-001]', '[results.r-001]\nanswers = ["Q-001"]'))
    provenance.answer_question(project, "inv", "Q-001", results=["r-001"])
    provenance.set_question(project, "inv", ["Q-002"], "parked", reason="Waiting on owner")
    provenance.flag_findings(project, "inv", [{"result": "r-001", "reason": "Changed input"}])
    assert provenance.question_tree(project, "inv")[0]["display_status"] == "answered (awaiting recheck)"
    provenance.edit_question(project, "inv", "Q-001", audience="Which regions need review?")
    draft = project / "deliveries/inv/pkg/draft"
    record = manifest(project)
    record["revalidation_flags"] = [{"finding": "West volume is stable", "reason": "Changed input", "represented_in": "none", "disposition": "none"}]
    write(draft, "manifest.json", json.dumps(record))
    before_open = BASE + "\n## Limitations and open caveats\n\n**Headline:** Coverage remains limited\n\n**Notes:** Interpret carefully.\n"
    opened = "\n## Open questions\n\n**Headline:** These answers still matter\n\n" + "\n".join("- " + text for text in questions) + "\n\n**Notes:** Confirm the unanswered questions.\n"
    write(draft, "findings.md", before_open + opened)
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert report["open_questions_count"] == 6
    assert report["open_questions"] == [] and report["outline"] == [] and code == 0, report
    assert report["findings"] == [] and report["passed"], report
    entry = provenance.question_tree(project, "inv")[0]
    assert entry["text"] == "Which regions in orders_view need review?" and entry["priority"] == "must"
    assert entry["status"] == "answered"
    write(draft, "findings.md", before_open + opened.replace("- Which regions need review?\n", ""))
    _, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert any(row.get("question") == "Which regions need review?" and row["problem"] == "missing question"
               for row in report["open_questions"])


@pytest.mark.parametrize("citation, unlinked", [
    ("Result: r-001", ["Coverage remains limited"]),
    ("Result: `r-001`", ["Coverage remains limited"]),
    ("[Evidence](../../../../investigations/inv/evidence/r-001.json)", ["Coverage remains limited"]),
    ("Result (r-001).", ["Coverage remains limited"]),
    ("Result: r-001-extra", ["Regional rates differ", "Coverage remains limited"]),
    ("<!-- Result: r-001 -->", ["Regional rates differ", "Coverage remains limited"]),
    ("The regional result", ["Regional rates differ", "Coverage remains limited"]),
    (None, ["Regional rates differ", "Coverage remains limited"]),
])
def test_storyline_citation_grammar_reports_unlinked_text(project, capsys, citation, unlinked):
    draft = storyline_fixture(project)
    write(draft, "findings.md", deck("### Customer rates differ\n\n**Notes:** Compare customers.\n\n"
                                     "### Regional rates differ\n\n**Notes:** Compare regions.\n\n"
                                     "### Coverage remains limited\n\n**Notes:** Interpret carefully.\n"))
    path = draft / "methodology.md"
    if citation is None:
        (project / "investigations/inv/evidence/r-001.json").unlink()
    else:
        path.write_text(path.read_text().replace("Result: r-001", citation))
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert report["unlinked_findings"] == unlinked and report["storyline"] == []
    assert code == 0, report


@pytest.mark.parametrize("settings_text, empty_ledger, expected", [
    ('[results.r-001]\nquestion = "Which regions?"\nanswers = "Q-001"\n', False, "answers must be a list"),
    ('[results.r-001]\nquestion = "Which regions?"\nanswers = ["Q-999"]\n', False, "questions.json does not hold"),
    ('[results.r-001]\nquestion = "Which regions?"\nanswers = ["Q-999"]\n', True, "questions.json does not hold"),
    ('[parameters]\nscope = "current"\n', False, "settings"),
    ('[results.r-001\n', False, "settings"),
])
def test_storyline_refuses_unreadable_or_invalid_declared_answers(project, capsys, settings_text, empty_ledger, expected):
    draft = storyline_fixture(project)
    write(draft, "findings.md", deck("### Regional rates differ\n\n**Notes:** Compare the regions.\n"))
    # Use the alternative settings file named in the evidence, rather than assume settings.toml.
    evidence = project / "investigations/inv/evidence/r-001.json"
    recorded = json.loads(evidence.read_text())
    recorded["settings"]["path"] = "investigations/inv/analysis.toml"
    evidence.write_text(json.dumps(recorded))
    write(project, "investigations/inv/analysis.toml", settings_text)
    if empty_ledger:
        write(project, "investigations/inv/questions.json", '{"schema": "awb-questions/1", "questions": []}')
        (project / "investigations/inv/questions.md").unlink()
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and any("storyline check:" in error and expected in error for error in report["errors"]), report


def test_storyline_should_precedes_could_and_ties_keep_order(project, capsys):
    draft = storyline_fixture(project)
    path = project / "investigations/inv/settings.toml"
    path.write_text(path.read_text().replace('answers = ["Q-001", "Q-002"]', 'answers = ["Q-001"]')
                    .replace('answers = ["Q-003"]', 'answers = ["Q-004"]'))
    write(draft, "findings.md", deck("### Customer rates differ\n\n**Notes:** Compare customers.\n\n"
                                     "### Regional rates differ\n\n**Notes:** Compare regions.\n"))
    _, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert [(row["slide"], row["question"], row["expected_position"]) for row in report["storyline"]] == [
        ("Customer rates differ", "Q-004", 2)]
    # Equal question priority and position leave the author's ordering intact.
    path.write_text(path.read_text().replace('answers = ["Q-004"]', 'answers = ["Q-001"]'))
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert report["storyline"] == [] and code == 0, report


NOTE = """# How the analysis was done

Operations leads, all regions, January to June 2026.

## Sources

- The order extract from the operations team.

## Method

- Orders are counted once.
"""
NOTE_ADDITIONS = ("\n- Counts come from orders_view.\n- About 40 stores took part.\n"
                  "- Discounts drive fewer late orders.\n\n<div>Draft only.</div>\n")


def test_methodology_note_is_checked_with_rows_naming_it(project, capsys):
    draft = project / "deliveries/inv/pkg/draft"
    # One association result is represented, so causal wording anywhere in the note is above its strength.
    set_manifest(project, results=[{"result_id": "r-001", "evidence": "investigations/inv/evidence/r-001.json",
                                    "question": QUESTIONS["r-001"]}])
    code, before = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0 and before["passed"]
    write(draft, "methodology-note.md", NOTE)
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0 and report["passed"], report
    assert "methodology-note.md" in [row["path"] for row in manifest(project)["inventory"]]
    write(draft, "methodology-note.md", NOTE + NOTE_ADDITIONS)
    first = len(NOTE.splitlines()) + 2
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and not report["passed"]
    assert report["findings"] == [{"file": "methodology-note.md", "line": first, "kind": "name", "text": "orders_view"}]
    assert report["numbers"] == [{"file": "methodology-note.md", "line": first + 1, "text": "40", "problem": NOT_RECORDED}]
    assert report["claims"] == [{
        "file": "methodology-note.md", "line": first + 2, "section": "Method", "phrase": "drive",
        "claim": "association", "results": ["r-001"], "problem": "causal wording above the association claim "
        "strength; reword it, since only an experiment or an identified natural experiment supports a causal claim"}]
    assert report["markdown"] == [{"file": "methodology-note.md", "line": first + 4, "problem":
                                   f"unsupported Markdown: an HTML block at line {first + 4}; rewrite as Markdown text"}]
    code, report = run(project, capsys, "release", "inv", "pkg")
    assert code == 1 and report["refused"] == "check-draft --verify-only does not pass"
    # Without the note, check-draft reports exactly what it did before the note was written.
    (draft / "methodology-note.md").unlink()
    code, after = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0 and after == before


def test_methodology_note_limitations_section_is_not_read_for_claims(project, capsys):
    draft = project / "deliveries/inv/pkg/draft"
    set_manifest(project, results=[{"result_id": "r-001", "evidence": "investigations/inv/evidence/r-001.json",
                                    "question": QUESTIONS["r-001"]}])
    caveats = ("\n## Limitations\n\n- Part of the rise is attributable to holiday volume.\n\n### Coverage\n\n"
               "- June is short due to a feed outage.\n")
    write(draft, "methodology-note.md", NOTE + caveats)
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0 and report["claims"] == [], report
    # The same sentence under another section is read, and so is a section after Limitations.
    write(draft, "methodology-note.md", NOTE + caveats.replace("## Limitations", "## Exclusions")
          + "\n## Limitations\n\n- Holiday weeks are in the period.\n\n## Contacts\n\n- Volume drives staffing.\n")
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and [(row["section"], row["phrase"]) for row in report["claims"]] == [
        ("Exclusions", "attributable to"), ("Coverage", "due to"), ("Contacts", "drives")]


def test_check_draft_counts_main_and_appendix_slides(project, capsys):
    _, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert report["slides"] == {"main": 5, "appendix": 0}
    draft = project / "deliveries/inv/pkg/draft"
    write(draft, "findings.md", BASE.replace(HOW_WE_KNOW, "") + LIMITATIONS + "\n## Appendix\n"
          + HOW_WE_KNOW.replace("## How we know", "### How we know"))
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0 and report["slides"] == {"main": 4, "appendix": 1} and report["outline"] == [], report


def appendix_deck(findings, slide, closing):
    """findings with `slide` cut from ## Findings and placed, with `closing`, under ## Appendix."""
    return findings.replace(slide, "") + "\n## Appendix\n\n" + slide + closing


def test_appendix_slides_are_checked_like_main_slides(project, capsys):
    west = DECK_FINDINGS[DECK_FINDINGS.index(WEST):DECK_FINDINGS.index("### Discounts")]
    how = DECK_FINDINGS[DECK_FINDINGS.index("## How we know"):DECK_FINDINGS.index("## Limitations")]
    moved = appendix_deck(DECK_FINDINGS.replace(how, ""), west, "\n" + how.replace("## How", "### How"))
    # How we know needs no methodology section from the appendix too.
    claim_draft(project, moved)
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0 and report["passed"] and report["headings"] == [] and report["claims"] == [], report
    # An appendix finding slide is still held to its claim strength.
    claim_draft(project, moved.replace(WEST_BULLET, "- The new carrier drives the rise to 21%."))
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    text = moved.replace(WEST_BULLET, "- The new carrier drives the rise to 21%.")
    assert code == 1 and [(row["section"], row["phrase"], row["line"]) for row in report["claims"]] == [
        (WEST_DISCOUNT, "drives", text[:text.index("drives")].count("\n") + 1)]


def test_appendix_how_we_know_and_limitations_wording_is_not_read(project, capsys):
    # Only the association result is represented, so causal wording on a read slide is refused.
    discount = DECK_FINDINGS[DECK_FINDINGS.index("### Discounts"):DECK_FINDINGS.index("## How we know")]
    closing = DECK_FINDINGS[DECK_FINDINGS.index("## How we know"):]
    findings = (DECK_FINDINGS.replace(discount, "").replace(closing, "")
                .replace("Discounts drive 4 points fewer late orders", "Late orders rose in the west"))
    methodology = CLAIM_METHODOLOGY[:CLAIM_METHODOLOGY.index("### Discounts")]
    moved = findings + "## Appendix\n\n" + closing.replace("## ", "### ")
    claim_draft(project, moved, methodology, results=("r-009",))
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0 and report["passed"] and report["claims"] == [], report
    assert report["slides"] == {"main": 3, "appendix": 2}, report
    # The same wording on an appendix finding slide is read.
    slide = closing.replace("## How we know", "### Feed outage").replace("**Headline:** Totals reconcile to the "
                                                                          "ledger\n\n", "")
    slide = slide[:slide.index("## Limitations")]
    claim_draft(project, moved + "\n" + slide, methodology + "\n### Feed outage\n\n" + WEST_CLAIM
                + "\n\nResult `r-009`.\n", results=("r-009",))
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 1 and [(row["section"], row["phrase"]) for row in report["claims"]] == [
        ("Feed outage", "due to")], report


ORDER = ["Regional rates differ", "Coverage remains limited", "Customer rates differ"]
NULL = object()  # presentation_order recorded as JSON null, which is malformed rather than absent


def ordered_deck(project, headlines, order):
    draft = storyline_fixture(project)
    write(draft, "findings.md", deck("".join(f"### {headline}\n\n- Rates vary across groups.\n\n**Notes:** Compare "
                                             "the groups.\n\n" for headline in headlines)))
    if order is not None:
        set_manifest(project, presentation_order=None if order is NULL else order)
    return draft


@pytest.mark.parametrize("order, rows", [
    # Without an order the ledger decides: Customer answers the must root, so it leads.
    (None, [("Customer rates differ", 1, "finding slide is out of place; move it to finding position 1")]),
    ("none", [("Customer rates differ", 1, "finding slide is out of place; move it to finding position 1")]),
    (ORDER, []),
    (["Regional rates differ", "Coverage remains limited"],
     [("Customer rates differ", None, "presentation_order does not list this finding slide; add its heading where "
                                      "the user placed it")]),
    (ORDER + ["Regional rates differ"],
     [("Regional rates differ", None, "presentation_order lists this heading 2 times; keep it once")]),
    (ORDER + ["West volume is flat"],
     [("West volume is flat", None, "presentation_order names no finding slide with this heading; give the "
                                    "slide's current heading or remove it")]),
    (["Customer rates differ", "Regional rates differ", "Coverage remains limited"],
     [("Customer rates differ", 1, "finding slide is out of place in presentation_order; move it to finding "
                                   "position 1")]),
    (["Regional rates differ", "Coverage remains limited", "Customer rates **differ**"], []),
    ("Regional rates differ",
     [(None, None, "presentation_order is not none or a list of finding headings; record the approved order, "
                   "or none")]),
    ([ORDER[0], ORDER[1], ""],
     [(None, None, "presentation_order is not none or a list of finding headings; record the approved order, "
                   "or none")]),
    (NULL,
     [(None, None, "presentation_order is not none or a list of finding headings; record the approved order, "
                   "or none")]),
], ids=["absent", "none", "followed", "missing", "repeated", "unknown", "moved", "markup", "not a list", "blank",
        "null"])
def test_presentation_order_decides_finding_order_when_set(project, capsys, order, rows):
    ordered_deck(project, ORDER, order)
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert [(row["slide"], row.get("expected_position"), row["problem"]) for row in report["storyline"]] == rows
    assert report["unlinked_findings"] == ["Coverage remains limited"]
    assert code == (1 if rows else 0) and report["passed"] is (not rows), report
    _, verified = run(project, capsys, "check-draft", "inv", "pkg", "--verify-only")
    assert verified["storyline"] == report["storyline"]


def test_export_keeps_presentation_order(project, capsys):
    ordered_deck(project, ORDER, ORDER)
    code, report = run(project, capsys, "export", "inv", "pkg", "--result", "r-001", "--result", "r-002")
    assert code == 0 and report["written"] and manifest(project)["presentation_order"] == ORDER


def test_presentation_order_is_no_provenance_gap():
    draft = load(ASSETS["src/packaging/draft.py"], "draft_order_gaps")
    record = {"presentation_order": ["Unknown regions hold few late orders"],
              "producing_commit": {"unknown": "no Git history"}}
    assert draft.provenance_gaps(record) == [{"field": "producing_commit", "reason": "no Git history"}]


def test_storyline_orders_main_and_appendix_findings_each_by_the_ledger(project, capsys):
    draft = storyline_fixture(project)
    slides = {headline: f"### {headline}\n\n- Rates vary across groups.\n\n**Notes:** Compare the groups.\n\n"
              for headline in ORDER}
    text = deck(slides["Regional rates differ"]) + "\n## Appendix\n\n" + slides["Customer rates differ"] \
        + slides["Coverage remains limited"]
    write(draft, "findings.md", text)
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0 and report["storyline"] == [] and report["outline"] == [], report
    # Within the appendix the ledger order still applies.
    write(draft, "findings.md", deck(slides["Regional rates differ"]) + "\n## Appendix\n\n"
          + slides["Coverage remains limited"] + slides["Customer rates differ"])
    _, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert [(row["slide"], row["expected_position"]) for row in report["storyline"]] == [("Coverage remains limited", 3)]


def test_open_questions_follows_how_we_know_when_limitations_is_in_the_appendix(project, capsys):
    provenance = load(project / "src/provenance.py", "ledger_appendix_fixture")
    provenance.add_question(project, "inv", "What caused the delay?", kind="context", answerer="user",
                            origin="scope", priority="must")
    opened = "\n## Open questions\n\n**Headline:** Some questions remain\n\n- What caused the delay?\n\n" \
             "**Notes:** These answers matter.\n"
    appendix = "\n## Appendix\n" + LIMITATIONS.replace("## Limitations", "### Limitations")
    draft = project / "deliveries/inv/pkg/draft"
    write(draft, "findings.md", BASE + opened + appendix)
    code, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert code == 0 and report["open_questions"] == [] and report["outline"] == [], report
    write(draft, "findings.md", BASE.replace(HOW_WE_KNOW, opened + HOW_WE_KNOW) + appendix)
    _, report = run(project, capsys, "check-draft", "inv", "pkg")
    assert [row["problem"] for row in report["open_questions"]] == [
        "place Open questions immediately after Limitations and open caveats, or, with that slide in the appendix, "
        "immediately after the last finding, Implications, or How we know slide"]
