# Friction log: Priya Natarajan (retail-A)

## Pre-session: reading the README

- README is very install-heavy and technical (MCP config, symlinks, AGENTS.md precedence, Copilot reviewer agent). As a non-programmer I skimmed most of it; I could not tell which parts I personally need to do versus the agent. The brief says skills are already installed, so I skipped Install.
- The "Use" section is the useful part: suggested phrasings for awb-init, awb-scope, awb-status, awb-package, awb-release. Good.
- Jargon I don't understand: "canonical views", "validated Parquet datasets", "DuckDB views", "question ledger", "receipt", "M365 assembly file". Not clear whether the deliverable is actual PowerPoint slides or an outline that someone else (Copilot PowerPoint agent) has to build. I need "about 8 slides"; README suggests I'd get an outline plus chart data files, not a finished deck. Mild worry.
- README says the agent will ask where landed originals and releases are kept. I know these paths from the brief, so I will give them up front to save a round trip.

## Turn 1

- Asked: awb-init with the business question, the five questions, data source link, audience/deadline, storage locations.
- Expected: project set up, then a scoping interview.
- Happened: project initialized and investigation "scoped" in one go. No actual interview happened; it recorded open decisions instead of asking me. Fine for speed, but README promised an interview.
- Reply is jargon-heavy for me: "MCP writes were unavailable, so setup used the local CLI", "filesystem policy prevented Git initialization". I don't know if those are problems I need to act on. Nothing said whether I should worry.
- "Questions: opened 10 (3 need your context)" but it did not tell me WHICH 3 questions it needs from me. I have to infer from the "open decisions" bullet list. Friction: I'd have to open a file to find out.
- Good: it confirmed my storage paths and the five questions, and gave a clear next step.

## Turn 2

- Asked: answered the open decisions I could infer (meaningful sales threshold, repeat-purchase definition, no spend/margin data, no constraints), told it what I know about the data (C invoices, non-product codes, missing customer IDs, Dec 2011 incomplete), asked which 3 questions it actually needs from me, and told it to go ahead and get the data in.
- Expected: it downloads, lands, and validates the workbook.
- Happened: data downloaded and landed (1,067,371 lines), originals copied to my landed folder with checksums. Clear revenue recommendation (include merchandise, delivery, discounts; show fees/bad debt/adjustments separately with reconciliation). Good, that is the kind of recommendation I wanted.
- Clear answer that MCP/Git need no action from me. Good.
- Friction: it linked me to an agent instruction file (awb-clean SKILL.md) as justification for asking. I declined to open it; I don't need to read the tool's rules, just the decision. Exposing internal file paths to a business user is noise.
- Friction: "22,523 identical lines repeated across both sheets" - it didn't say WHY they repeat (I assume the two sheets overlap around the year boundary in early Dec 2010). I'd want that one sentence of explanation to feel confident.
- "keeping the second-sheet copy" - irrelevant detail to me if they're identical.

## Turn 3

- Asked: yes, count once; asked to confirm whether it's the boundary overlap; asked it to proceed to the analysis.
- Expected: cleaning done, then exploration and answers.
- Happened: big jump - it went straight from cleaning to answering all five questions in one reply, with tables and a headline recommendation. Very useful. I didn't see an explicit "explore" step; fine by me.
- Confirmed the 22,523 repeats are all 1-9 Dec 2010. Good, exactly what I wanted. Also flagged 11,491 other repeated-looking lines kept as not proven errors - reasonable.
- Spot checks (by hand, in my head/Excel-style): monthly figures sum to the annual totals (9,335.3 / 9,602.2); Sep-Nov share 36.0% checks; top-10% 54.0% and no-ID 14.5% of £18.94m both check. Numbers are internally consistent. Good.
- Concerns:
  - April 2011 (£492k) is down 24% on April 2010 with no comment. I'd get asked about that in the room.
  - Q4 list is dominated by one-off order reversals (storage jar: one order = 94.8% of sales). It flagged this itself (good), but as-is the list is not something I can show leadership. Also unclear which period Q4 covers.
  - Q3 December cohort only 76 customers / 15.8% - unexplained.
- Methodology note link points to a file inside the project; it's offered as something for me to review. I'll read it at package stage.
- Jargon fairly light this turn. "Questions: answered 8" counter is a bit opaque (I have 5 questions; it counts its own ledger).

## Turn 4

- Asked: explain April 2011 dip; redo Q4 with a more robust "meaningful" definition that excludes single-order reversals, and state the period; explain December cohort size.
- Expected: revised Q4 table and short explanations.
- Happened: thorough answers to all three follow-ups. April dip decomposed (fewer trading dates, lower daily sales, more cancellations), April+May combined only -2% - that's a line I can say in the room. Revised Q4 with recommended cut-offs and a clean top 10, plus caveats (credits may relate to older purchases; 6 of 10 not sold in 2011). December cohort explained (short month, returning buyers, more anonymous sales).
- Good: it gave specific questions for IT and Finance, and kept the raw ranking in the methodology.
- Minor: cited a district council committee PDF as the source for 2011 bank holidays - odd choice for a leadership-facing note; gov.uk would be the obvious source.
- Minor: replies are long; the "Customers*" footnote definition ("positive product spend after subtracting credits") took a re-read.
- Q4 top 10 is 7 variants of the same Cherry Lights range - for slides it should be grouped as one range-level finding.
- I now accept answers to Q1-Q5.

## Turn 5

- Asked: awb-status (where are we), and stated I accept the answers, with a note to group Cherry Lights for the deck.
- Expected: a plain status summary and suggested next step (package).
- Happened: concise, plain-language status. Done / open / package not created / storage ready, plus the exact next request phrasing. Good - this is what I wanted.
- Mild confusion: "19 supported findings" - I asked 5 questions; not clear what the 19 are or whether all go in the deck. "choosing supporting data exports - including none" is unclear: what are my options?

## Turn 6

- Asked: awb-package for the eight-slide leadership package; asked for monthly revenue and country tables as spreadsheet-friendly exports; asked what the 19 findings are relative to the 8 slides.
- Expected: a draft deck outline + methodology note to review.
- Happened: headline checkpoint before full draft. Opened findings.md (just the headings so far) and the two CSVs. Listed 13 of 19 findings in/out with reasons - clear.
- Friction: again cited the awb-package SKILL.md to justify the checkpoint. I don't need that; "I'll wait for your OK on headlines before writing the slides" is enough.
- Friction: findings.md is only headings with "Answer / Findings / Supporting datasets" section labels - it's hard to picture slides 1-8 from it; the table in chat was clearer than the file.
- Headline wording has analyst jargon unsuited for leadership: "screened cancellation-value rates", "first observed", "use two tables to check the evidence". Slide 8 headline reads like a note to analysts.
- CSVs: values carry 9+ decimal places (e.g. 366.89000039169395%, 100.00000000000001). Works in Excel but looks sloppy if anyone opens them; I want rounding. Country file has blank cells where there are no identified buyers - OK.
- The 14.5% unidentified revenue and Ireland's £91k decline aren't in any headline; I want them visible.

## Turn 7

- Asked: reworded headlines 5-8, add unidentified-revenue and Ireland mentions, round the CSVs; otherwise approve.
- Expected: full draft (outline + methodology note) ready for review.
- Happened: full draft ready. Opened findings.md (8 slides: title, answer, 5 findings, next steps), methodology.md, CSVs. All my headline changes and rounding were made. Agent narrowed two claims to match evidence (Australia, Cherry Lights) - appreciated, and it told me.
- Surprise / friction: there is no actual PowerPoint. The deliverable is a slide-by-slide text outline + chart data files; building the deck requires the Microsoft 365 Copilot PowerPoint agent. README hinted at this but I hadn't fully registered it. If I didn't have M365 Copilot I'd be stuck building slides by hand. This is the biggest expectation gap so far.
- Friction: methodology note is ~4,300 words and full of internal jargon: "immutable publication", "canonical correction", "exact overlap multisets", question IDs (Q-008, Q-016), JSON evidence file paths, check names in backticks. Fine as an audit trail, but I can't send that to leadership or Finance as "the methodology note". I need a short plain-English summary up front.
- Slides: only two charts across eight slides; the country slide has none, and that's the one people will argue about. Slide notes are long and caveat-heavy but usable as speaker notes.
- "Supporting datasets" section heading holds slide 8 "Next steps" - odd label but harmless.
- The draft folder also has assembly/, charts/, deck-rules.md, manifest.json - not explained to me; I assume they're for the PowerPoint builder.
- Good: reconciliation table is clear and exactly what Finance would want.

## Turn 8

- Asked: add a country growth bar chart on slide 6; add a one-page plain-English summary at the top of the methodology note; confirm what I hand to Copilot to build the deck.
- Expected: revised draft, then I release.
- Happened: chart 3 (country change bar incl. Ireland) added; plain-English one-page summary at top of methodology with reconciliation table and open checks - exactly what I asked. Clear list of 7 files to give Copilot plus a copy-paste instruction. Very helpful; this should be in the README or offered unprompted.
- Minor: the summary still uses "signed cancellations" and "proven copies" - slightly technical but acceptable.
- Minor: having to attach 7 specific files (not the folder) to another tool is a fiddly manual handoff.

## Turn 9

- Asked: awb-release to mark it delivered (release 001), copy to releases folder.
- Expected: frozen release 001 and a copy in storage/releases/.
- Happened: release 001 created and copied to storage/releases/marketing-budget-priorities/leadership-budget/released/001/. I checked the folder: findings, methodology, 3 chart CSVs, 2 data CSVs, deck rules, assembly file, plus a new build-powerpoint.md (presumably the Copilot instructions). No decisions asked of me. Smooth.
- Minor: the release folder path is deep (4 levels) - I'd have to dig to find it in Finder. "Git-history gap remains documented" is noise to me.
- Reached end point: all 5 questions answered and accepted; asked awb-status once; draft reviewed with corrections; release 001 delivered and copied.

## Overall summary

What went well: fast, numerically consistent answers; agent volunteered caveats (one-off reversals, Australia concentration, first-observed vs new); clear decision asks; storage handled without fuss; awb-status was clear and actionable; headline checkpoint before full draft was useful.
Main friction: (1) no actual PowerPoint - an outline for M365 Copilot to build, which a first-time user may not expect or have access to; (2) agent repeatedly linked internal SKILL.md files to justify its asks; (3) jargon in early replies and in the methodology note (fixed on request with a summary); (4) "N questions need your context" without listing them; (5) CSV exports first had unrounded floats; (6) README install section is impenetrable for a non-programmer; (7) no real scoping interview despite README promising one.
