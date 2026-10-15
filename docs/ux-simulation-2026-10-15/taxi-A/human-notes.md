# Friction log: Dana Ortiz (taxi-A)

## Pre-session: reading the README
- README is long and mostly install/host plumbing (MCP config, VS Code Local, Claude Code AGENTS.md vs CLAUDE.md). As a non-programmer I skimmed most of it; hard to tell which parts I need as a user vs. which are for whoever sets up the machine.
- The "Use" section is the useful part: start with "Use awb-init to initialize this analytics project. The question is ...". Clear enough.
- Jargon I did not understand from the README alone: "canonical views", "foundation level", "question ledger", "flagged finding disposition", "M365 assembly file", "R-<area>-NNN". I gather the deliverable is a deck outline + chart data files that PowerPoint Copilot builds, not an actual .pptx. That is a surprise; I wanted a deck. Will see.
- Good: README says the agent will ask where landed originals and releases are kept, so I know to have those paths ready.

## Turn 1
- Asked: awb-init with my business question, summary of the five questions, data location, storage folders.
- Expect: project set up, then a scoping interview.
- Happened: project initialized, investigation "yellow-taxi-monthly-patterns" created, deadline and storage paths recorded. 12 questions opened, 1 "needs your context" but it did not say which one or ask it. No scoping interview happened, even though the README said awb-init hands off to awb-scope which interviews me. Surprising.
- Confusing/jargon: "Git creation was blocked by the environment. MCP reads work; writes require the CLI fallback." I don't know what this means for me or whether it is a problem. "Board decision thresholds remain open" - unclear what is expected of me. "Data, cache, and delivery directories are deferred" - irrelevant detail to me.
- Good: short summary, correct deadline computed, storage paths captured without being asked again.

## Turn 2
- Asked: which question needs my input, what "thresholds" means, whether git/MCP thing matters; go ahead and land the data.
- Expect: the one question surfaced, then data landed and validated.
- Happened: agent clarified the pending question (what would persuade the board) and that tooling issues don't need me. Landed all 3 files to my shared drive (verified: storage/landed/data/raw/tlc-yellow/supplied-20261015/... plus provenance.json; folder nesting "data/raw/..." is a bit deep but fine). Ran a screening: ~3.6-3.75% flagged overall, by vendor table. Good: concrete numbers fast, invalid rate by vendor already partly answers Q4. Cited the TLC dictionary.
- Gaps: no breakdown of which rule flags how many records; "Vendor 1/2" not named; unclear whether flagged rows will be excluded but counted (my requirement). "Opened 1 for provider clarification" - didn't say what. Scoping interview still never really happened (just one question).

## Turn 3
- Answered the board-threshold question (nothing decided; gave a sensible bar). Asked for rule-by-rule breakdown, confirmation that flagged rows are excluded-but-counted, vendor names, and what the provider-clarification question is. Told it to proceed with Q1.
- Happened: rule-by-rule table with counts and %, vendor names (CMT, Curb) with sources, provider question explained (one duplicate record; TLC owns it). Q1 answered with weekday per-day table and hourly highlights; links to PDFs and CSV. Opened volume-hourly.csv: readable, includes baseline/lenient rule sets (sensitivity), though column names are technical.
- Good: specific, sourced, sensitivity check, explicit exclusions. Exactly what I asked for.
- Concern: weekday swings (Thu -3.9%, Sat -10.3%, Tue +16%) are big; I suspect holidays (Jan 1 & MLK Day are Mondays; July 4 is Thursday). Agent didn't mention holidays. Also the "identical weekday counts" correction referred to an earlier note I never saw - a little confusing.
- Minor: links are relative paths in a chat; as a user I had to figure out the project folder.

## Turn 4
- Asked about holiday effects on weekday comparison and for one board-friendly sentence; proceed to Q2 airports.
- Happened: holiday sensitivity done properly (Thursday flips from -3.9% to +9.1%), board sentence given. Q2 airports answered in the same turn: share of trips 9.8%->11.3%, ~30-32% of fare revenue, median fare ~4.5x, duration ~3x, per-airport shares, caveats (fare excludes tips/surcharges/tolls, unknown geography, Newark mostly dropoffs).
- Good: agent proactively moved on and answered Q2 completely; revenue definition stated explicitly as I asked. Q1 and Q2 accepted.
- Small gap: "unknown geography can conceal airport trips" - no number for how much. Asked for it.

## Turn 5
- Accepted Q1/Q2, asked for the unknown-zone count, proceed to Q3 tipping.
- Happened: unknown geography quantified (~0.5-0.6%; ~1% incl. outside NYC). Q3: tip% defined (tip/fare, median incl. zeros), cash caveat explicit. Medians ~26%; by borough Manhattan 26%, Queens 23%, Brooklyn/Bronx 0%(!), Staten Island tiny n. Agent itself flagged that Brooklyn/Bronx zeros are concentrated in CMT records (91-94% zero-tip for CMT vs 6-9% for Curb) and recommended TLC/CMT clarification. Hourly range 23.6%-28%.
- Good: agent caught a vendor artifact that would have embarrassed us with the board. Strong.
- Need: a borough comparison that isn't distorted by the CMT issue (Curb-only). Also July has fewer card trips than Jan despite more trips overall - wanted to know card share.

## Turn 6
- Asked for Curb-only borough medians and card-payment share per month; then Q5.
- Happened: Curb-only borough medians (Bronx 16-21%, Brooklyn ~23%, Manhattan ~26%, Queens ~23%) with n's; hourly ranges; footnote wording drafted. Card share 80%->75% explained as growth in payment code 0, not a switch to cash. Q5: unrestricted top 10 dominated by 1-5-trip zones (Rikers Island, 1 trip!); offered 100-trip/10-hour and 500/50 thresholds; said no threshold-independent answer. Opened the summary .md the agent linked: well organized, readable, though it mentions internal IDs like "Q-017" and "seven declared validation categories" that mean nothing to me.
- Good: agent refused to give a misleading ranking and showed sensitivity. Q3 accepted.
- Friction: Q5 left the definition decision to me implicitly (didn't explicitly ask me to pick). Flushing Meadows-Corona Park at $177/occupied hour in January looks odd to me (no US Open in Jan) - want sanity check.
- Asked for status for the first time.

## Turn 7
- Chose 100 trips/10 hours as the board definition for Q5; asked for Flushing Meadows sanity check; "Use awb-status — where are we?"
- Happened: Flushing sanity check found $70 JFK-rate records with no JFK endpoint (205/221) - suspicious coding; agent recommended setting it aside pending TLC verification and gave the alternative top 10. Status report given: Q1-3 accepted, 39 findings, 5 open questions (all TLC-side), no deck yet, deadline Oct 29, storage reachable, Git unavailable.
- Good: status was readable and short, told me the next request to make. Sanity check was thorough and plain.
- Friction: "39 supported findings" - way more than I can put in 8 slides; unclear how they'll be boiled down. Status didn't list Q4 as accepted (I never explicitly said so). Status mentions Git again - still don't know if I should care. Link this time was an absolute path, earlier ones relative - inconsistent.

## Turn 8
- Accepted Q4 and Q5 (Flushing set aside, footnoted). Requested awb-package with guidance on storyline for board.
- Happened: agent produced storyline (8 headlines) and a one-page methodology PDF; full deck held for headline approval and a "datasets" choice ("no separate datasets" vs "summarized comparison tables") I didn't understand the purpose of.
- FRICTION: agent linked me to the awb-package SKILL.md ("instructions explicitly require...") as justification. That's an agent instruction file; I didn't open it. A user shouldn't be pointed at tool internals to explain why they're being asked something.
- FRICTION: "separate audience-facing datasets" - unclear what that is or why the board would want one. No recommendation given.
- Methodology PDF: good, genuinely one page, clear. Surprise: a third vendor "Myle" (260 Jan records, 35.8% flagged) appears for the first time - never mentioned in chat, where only vendors 1 and 2 were shown.
- Storyline: decision framing good. Weak spots: tipping headline (slide 4) and timing headline (slide 5) have no numbers; slide 7 says "Fund broader airport research" - a recommendation; I'd rather "evidence supports" framing since the board decides. Slide 8 doesn't mention the vendor difference.

## Turn 9
- Approved storyline with edits; chose no separate datasets; asked about Myle.
- Happened: full draft delivered as PDF + editable PPTX + methodology note; Myle explained. Opened the deck PDF.
- Surprise (positive): I got an actual .pptx, not just an outline for M365 Copilot as the README implied. README set the wrong expectation (or this is a different path).
- Deck is solid and decision-framed; my headline edits were applied. Issues I found reviewing:
  - Slide 2 (airports) has a stray tipping bullet.
  - Slide 3 fares missing $ signs in bullets; no "4.5x / 3x" takeaway.
  - Every data label carries an asterisk (9.8%*, 117.01* ...) - noisy and meaningless to a board reader.
  - Slide 5 chart shows holiday-excluded per-weekday averages but the chart legend doesn't say so; y-axis lacks thousands separators.
  - Slide 6: "Maspeth" and "Elmhurst/Maspeth" as the two leaders will confuse the board; need a note they're separate zones.
- Agent said "Independent review and final package checks passed" yet these issues remained - the review checks rules, not readability.

## Turn 10
- Requested the corrections; flagged asterisks as a general rule for future drafts.
- Happened: all five corrections applied in one pass; asterisk rule saved for future drafts. Checked slides 2-6: tipping bullet gone, 4.5x/3x added, $ signs in, no per-value asterisks, slide 5 axis labeled "holidays set aside" with commas, Maspeth note in slide 6 footnote (small, but acceptable).
- Good: fast, accurate revision; no regressions noticed.

## Turn 11
- Asked to release (awb-release) as release 001 to the shared drive.
- Happened: release 001 delivered and copied; verified storage/releases/yellow-taxi-monthly-patterns/board-decisions/released/001/ contains board-deck.pdf/.pptx, methodology-note.pdf, chart CSVs.
- Friction: release folder is cluttered for a shared drive - ~20 files incl. many JSON check/report files (artifact-checks.json, serialization-checks.json, review-state.json...) next to the 3 files a colleague actually wants. Path is 5 levels deep. "Release log records existing provenance gaps: ... two geography-validation metadata entries" - unexplained jargon; I don't know whether to worry. No disposition question was asked despite README saying I'd choose a disposition for each flagged finding (fine for me, but README expectation mismatch).

## Wrap-up
- All five questions answered with specific numbers and sensible caveats; status asked once; deck reviewed, corrected, released as 001 to my releases folder. End point reached.
- Biggest positives: agent caught real data problems (CMT zero tips, Flushing JFK-rate coding, holiday effect once prompted) and refused misleading rankings; answers were quantitative and sourced; revisions accurate and fast; produced a real .pptx.
- Biggest frictions: README is mostly installer plumbing and jargon, and mis-set expectations (M365-outline deliverable, scoping interview that never really happened, disposition step that didn't occur); agent pointed me to its SKILL.md to justify a question; tooling notes (Git/MCP/CLI fallback, provenance gaps) surfaced to me without saying whether I need to act; the "datasets" choice came with no explanation or recommendation; holiday effect only checked because I asked; internal IDs (Q-017) leak into user-facing files; release folder clutter.
