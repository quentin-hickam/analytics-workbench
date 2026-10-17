# Friction log — Sam Whitfield (co2-A)

## Turn 1 — setup request
- Asked: awb-init with full business question, 5 questions, audience, length (~8 slides + methods note), data URLs, landed + releases folders, preview-and-wait headlines.
- Expected: project set up, then a scoping round of up to four questions.
- README notes before starting:
  - README is long; the analyst quick-start is useful, but "How it works" is dense with internals (Parquet, DuckDB, receipts) a research lead doesn't need.
  - Unclear whether data at a web address gets downloaded by awb-init or needs a separate "bring in" request. Asked for it in the first message anyway.
  - "Canonical view", "disposition", "review rule" are jargon; the glossary helps.
  - Picked preview-and-wait since I want to see headlines before full slides; the two-mode explanation took a couple of reads.
- Happened: setup done; agent built a project-local Python env because a package was missing (reported in one line, fine). Four scoping questions, each with a recommendation, as the README promised. Good.
- Friction: reply links to a SKILL.md and quotes the skill's rule ("Before writing the records, ask...") — internal detail I don't need and shouldn't be pointed to. Didn't open it.
- Friction: "ready for an initial commit" — not sure whether I'm supposed to act. README says it commits only when asked.
- Nice: flagged the cumulative-since-1850 subtlety unprompted.
- Q3 on comparison years was slightly abstract; recommendation made it easy.
- Not yet: whether "countries" excludes aggregates wasn't asked; I'll say it.

## Turn 2 — answering scoping
- Answered all 4, plus added country definition and "latest year per variable, state the year".
- Happened: one long turn did scope + landing + all analysis + headline preview. Fast. Good catch: Kosovo has no ISO code (my assumption was wrong). EU-27 checked against member sum.
- Friction: chat claimed "all five answered" but only gave the #1 country for Q1 and Q5; top-10 lists and Q2's largest countries only visible in the preview file (Q1 lists not even there). Had to open the file to find Q2/Q3 numbers.
- Preview file mentions "Q-001", "recorded results" IDs like territorial-change: mild jargon but OK.
- Slide 2 answer headline is vague ("other measures reveal different priorities") — not a donor-ready answer.
- Q4 caveat: China series starts 1907 — want to know how much that might understate China's share.

## Turn 3 — review headlines, ask for missing numbers
- Asked: full Q1/Q5 tables, Ukraine war timing, size of Q4 gap effect, headline rewrites.
- Happened: excellent, thorough tables in chat; Ukraine split before/after 2022; Q4 sensitivity (China +0.05 pts) with honest "not an upper bound" framing; checked GCP docs for how World is built. All five questions now have answers I'd put in front of donors.
- Surprise: my headline wording preferences got turned into a review rule "R-headlines-001" without asking. Probably fine, but I didn't know what I'd signed up for.
- Friction: revised answer headline uses slashes ("China/India/Indonesia") and is long — reads like a note, not a slide headline.
- Answer was long (lots of scrolling) but that's what I asked for.

## Turn 4 — approve headlines with small tweaks, go to full draft
- Happened: full draft, methods note, 6 chart CSVs, START-HERE, all checks passed. Links were relative paths (fine in an IDE, awkward in a terminal).
- Reviewed findings.md, methodology-note.md, START-HERE.md, chart-3/6 CSVs. Quality is high; caveats are where I asked for them; the methods note is readable for donors.
- Friction: the Answer headline dropped the second clause I'd suggested ("while US, Japan, Germany cut CO2 as economies grew"); the agent explained this mid-stream, but it left the answer slide weaker.
- "Territorial" is never defined in plain words on the main slides; donors will trip on it.
- Chart spec lines ("Interval: none", "Highlight") are builder-facing; OK since the builder reads them.
- START-HERE says to attach methodology.md to the Copilot builder but also lists it as internal — slightly confusing (README explains the builder may consult it).
- The headline-preview mode worked as described.

## Turn 5 — small corrections + status
- Happened: all four corrections made; verified answer headline, territorial definition, UK bullet in findings.md. awb-status gave a clear one-screen summary.
- Friction: "Your exact headline exceeds the template's word limit... record it as an explicit exception" — fine, but I didn't know there was a word limit.
- Another review rule (R-metric-definitions-001) created without asking — reasonable, but it's happening silently.
- Slightly confusing: status says "next: assemble PowerPoint, then mark delivered". README implies the package itself is the deliverable; I don't have Copilot handy and don't want to wait to freeze. Releasing now.
- Status report said "11 findings" and "two required supporting questions" — I didn't know about those; minor.

## Turn 6 — release
- Happened: release 001 frozen and copied to storage/releases/co2-country-priorities/donor-roundtable/001/; I confirmed the files are there. Caveats listed in the report.
- Minor: headline-preview.md is included in the release folder, which START-HERE doesn't mention; harmless but clutter.
- Minor: release path nests investigation/package names I never chose explicitly.

## Overall
- 5 exchanges from first message to release, plus a closing one; matches the README's estimate.
- Strengths: careful data checks (Kosovo ISO, EU-27 sum, Ukraine timing, historical gap sensitivity), caveats placed where they qualify, headline checkpoint worked.
- Friction: the first "all answered" claim came before full answers were shown in chat; skill internals (SKILL.md link, review-rule IDs, word-limit "template") leaked into chat; review rules created silently; long replies.
