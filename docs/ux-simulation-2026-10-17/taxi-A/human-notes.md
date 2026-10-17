# Friction log — Dana Ortiz (taxi-A)

## Turn 1 — first message (awb-init)
- Read the README first. Asked: awb-init setup with business question, 5 sub-questions, audience/decisions, ~8 slides + one-page methods note, data location, landed/releases folders. Mentioned what I remember from the data dictionary (and that I couldn't download the PDF).
- Expected: project setup, then a scoping round of up to four questions at a time.
- README notes: Quick-start is clear and the example first message is very helpful. The "What you will be asked" section is long and dense (review rules, flagged findings, draft-then-review vs preview-and-wait) — a lot to absorb as a first-time user. Unclear whether I need to choose a headline checkpoint mode up front; I picked preview-and-wait since it sounds safer. "Install and administer" section irrelevant to me but easy to skip.
- Not sure whether to mention excluding bad records now or wait to be asked; mentioned it up front.

## Turn 2 — scoping questions
- Agent set up project, landed files (hash-checked), got the dictionary itself (nice — it could download what I couldn't), confirmed cash tips excluded. Good.
- Asked two decision-criteria questions with recommendations. Reasonable and plain.
- Friction: it linked me to a SKILL.md file and quoted its instructions to justify why it's asking — I don't need to see agent internals; didn't open it. Slightly odd/defensive tone ("That is why the investigation remains pending").
- Note: "dictionary dated March 2025, postdates files" caveat is thoughtful.
- "Investigation remains pending" — jargon; unclear what an investigation is vs. the project.

## Turn 3 — investigation created
- Answered both; agent created "trip-pattern-comparison" investigation. Quick, clear closing line.
- (see turn 4 below)
- Confusion: originals already "preserved" in landed/ at setup — but README says setup brings no data in. Is the data "in" or not? Not sure if I need to say "bring in the files". Asked for it explicitly anyway, plus cleaning, and asked it to propose exclusion thresholds to me before applying (README says it should).

## Turn 4 — cleaning proposal
- Agent answered my "is the data in?" question directly — good. Loaded 6.04M trips, proposed thresholds in a clear table with rationale, held for signoff. Exactly what I wanted. ~3.3–3.4% would be excluded.
- Opened quality-proposal.md: thorough and useful (vendor table, high-value examples), but dense — column names (`fare_amount`), file paths, "Q-011", "publication.json", "canonical view" are agent jargon. Fine for me, not something I'd hand anyone.
- Approved all rules as proposed, review-flag treatment for >$500/>100mi, keep duplicates. Asked for sensitivity check on the 127 high-value records in the results.
- Noticed vendor 6 (260 records, Jan only) — good that agent flagged it.

## Turn 5 — all five answers
- Big turn, all five answered with numbers in chat; sensitivity check done as asked. Great.
- Q1, Q2, Q4 look board-ready. Q1: Thursday decline in July — July 4 2024 was a Thursday; agent didn't mention holidays. Asked.
- Q3: Bronx/Brooklyn 0% medians explained by "rate-code 99" — agent never said what code 99 means; I don't know either. Need standard-rate medians and share of 99s before I can put this in front of the board.
- Q5: ranking dominated by zones with 1–13 trips (Rikers Island, 1 trip!). Not usable. Agent flagged it but didn't propose a fix. README says thresholds should be proposed before seeing leaders — here it showed leaders first, then flagged. Asked for a minimum-trip threshold proposal.
- Status line says "5 provisional answers" — README explains provisional, fine.

## Turn 6 — refinements
- All three follow-ups handled well: 300-trip minimum with reasoning; code 99 = Null/unknown, Bronx 92–95% code 99 all vendor 1 zero tips; July 4 explains Thursday dip. Newark pickup caveat (yellow cabs can't pick up there) — great catch I wouldn't have known.
- Minor: agent said it would propose and wait for signoff, then applied in the same turn (I had said "rerun" so OK, but the message contradicts itself).
- Suspicious: standard-rate overall median (26.61% / 26.25%) is identical to the earlier Manhattan all-card medians. Asked whether coincidence. Also hourly tip variation wasn't restated for the standard-rate population.
- Ready to move to headlines. Accepted Q1, Q5 (pending nothing), Q2, Q4.

## Turn 7 — headline preview
- Agent verified the median coincidence (bunching) and gave standard-rate hourly range. Then headline preview: 8 slides, clear list. preview-and-wait respected. Good.
- Preview file lives in a hidden ".preview" folder — a real user on Finder wouldn't see it; luckily headlines were in chat.
- My edits: slide 2 reads like the Lab is making the funding recommendation — board decides, want it softer/factual. Slide 5 should carry the cash-tip/missing-tip gap, the thing the board most needs. Slide 6 "leads named zones" dodges that Outside NYC is #1 in July; noticed all 9 named zones in both months are in Queens — better headline (asked agent to confirm). Slide 7 drops the vendor part of Q4.

## Turn 8 — full draft review
- Agent made all four headline changes, verified the Queens claim, ran review, fixed reviewer gaps itself. Gave clickable links. Package passes checks; 521-word note, on target.
- Read findings.md, methodology-note.md, START-HERE.md. Overall strong, caveats where they belong, honest about limits. START-HERE is clear and short — nice.
- Problems I want fixed: (a) tipping slide has a bullet "Independent checks confirm the equal standard-rate and Manhattan all-card medians come from different populations" — internal QA chatter, the board never saw the Manhattan figure; reviewer pushed it onto the slide. (b) 24-hour times (18:00) — board would prefer 6 p.m. (c) Answer headline "over fourfold median fares" is clunky.
- findings.md is long/dense for "speaker notes" — fine for builder but heavy to review as a non-programmer. Not clear what the deck will look like until built.
- Combined awb-status + corrections + release in one message, per README's "other requests in same message" note. Asked to see changed slides before release.

## Turn 9 — status + corrections
- awb-status delivered as prose paragraphs, not the "one screen" with per-question list and suggested next requests the README promised. Useful content, though. "Nine supported findings and two provisional reference calculations" — I asked 5 questions; mapping of 11 results to my 5 unclear.
- Corrections applied as asked; 12-hour rule saved. Changed slides shown in chat (good, didn't need the hidden .preview file).
- Again quoted a SKILL.md at me to explain why it waited — unnecessary; I asked for that myself.
- Approved release.

## Turn 10 — release 001
- Released 001, full path given, caveats listed. Checked the releases folder: all package files present (findings, methodology note, charts 1–5, START-HERE, manifest, deck rules, assembly).
- Done. 9 exchanges + closing. All five questions answered with board-usable numbers; status asked once; draft reviewed, corrected and released.

## Overall
- Went well: scoping was short; agent fetched the data dictionary I couldn't; thresholds proposed and held for signoff; caught things I didn't know (Newark pickup ban, code 99 = unknown); honest caveats; 521-word note on target; release copy verified.
- Friction: agent repeatedly linked/quoted its own SKILL.md files at me; hidden ".preview" folder for headlines; awb-status came as prose, not the promised one-screen list with next-step suggestions; jargon in review files (Q-011, publication, canonical view, column names); Q5 first shown with tiny-sample leaders before any minimum was proposed (README implies thresholds come before seeing leaders); "data is landed" vs "brought in" distinction confusing after setup; findings.md is long and hard to picture as slides.
