# Friction log — Dana Ortiz, taxi-A

## Turn 1 — first message (awb-init)
- Read README first. The quick-start ("What to say first") was clear and gave a good template; I copied its shape.
- Asked: set up project, gave all 5 questions, audience (board, non-technical, ~8 slides + one-page methods note), decisions, deadline, data location, landed + releases folders, preview-and-wait headline mode.
- Expected: setup, then a scoping round of up to four questions.
- README notes: lots of internal jargon (canonical view, receipt, disposition, MCP) — the "Install and administer" and "How it works" sections are not for me and feel heavy, but the quick-start was readable. Unclear whether I need to do anything about "Python 3.10" or Git — I just assumed it's installed.
- Mentioned that I couldn't get the data dictionary and what I remember of it, including my uncertainty about cash tips.

## Turn 2 — scoping round
- What happened: setup done, landed files preserved and verified (good, it told me plainly). Agent read the TLC dictionary through its web tool and confirmed cash tips aren't recorded. That was helpful because it resolved my uncertainty.
- Four scope questions, each with a recommendation and an alternative, as the README promised. They were good, concrete questions.
- Friction: the reply linked an agent instruction file (awb-init SKILL.md) twice and quoted it ("first interview round before it creates the investigation"). As a user I don't care about that and didn't open it; it reads like internal process leaking into my chat. The four questions also appeared twice (once in detail, once as a summary), so the reply was long.
- "occupied trip hours" is jargon-ish but they explained it.
- Footer line "Your five questions: captured, none analyzed · next: settle scope" — nice and clear.
- My answers: board decides, describe tipping patterns first, accept definitions (fare_amount only for revenue, also want zero-tip share), accept exclusion rules.

## Turn 3 — bring in + clean
- Asked: bring data in and clean it. Expected: counts of excluded records.
- Got: a clear table by month and vendor (3.56% Jan, 3.75% Jul), and the vendor flip (V1 down, V2 up). Sensitivity check said medians are stable and zone rankings less so. Very good, concrete.
- Opened cleaning-report.md as pointed to. It's useful but dense: "canonical views", "primary_eligible", "Q-008", "strict⊆primary⊆relaxed", links to .sql files I won't open. It's half written for me and half for the agent.
- Surprise: "1 answered" in the footer. I think that's Q4 (invalid records), but it didn't say which. Vendor 6 appears (260 records, 36% excluded). It wasn't explained and I don't know who it is.
- Zone ranking includes zones with 1 trip, so it's useless for the board as is. I need a minimum-volume rule. The agent flagged this but didn't ask me; I'm deciding now.
- "I recommend committing this preparation checkpoint": I'm not sure what committing means for me. Told it to commit as you go (README mentioned that phrase).

## Turn 4 — analysis of Q1, Q2, Q3, Q5
- Asked: confirm Q4, Vendor 6, a 1,000-trip floor for the zone ranking, commit as you go, analyze the rest.
- Got: everything in one turn, with specific numbers in chat plus a full analysis-report.md. Excellent. The chat summary alone was enough to see the headline numbers.
- Big value: it caught that the high Bronx/Brooklyn zero-tip shares come from Vendor 1 "fare code 99" records, which are all zero tips. That matters a lot for the tipping-position decision, and I would never have found it myself. It's labeled as a TLC question.
- Vendor 6 = Myle Technologies according to the 2025 dictionary, with a caveat. Fine.
- Report is long but readable. Some jargon remains ("deadheading", "Q-009", "run.py", "single-thread analytical session"). Commit hash in chat means nothing to me.
- I accept all five answers. Next: status (I want to try it), then package.

## Turn 5 — awb-status + holiday caveat
- Got: a short, readable status with the analysis, open TLC questions, deliverables, storage, and a suggested next request I can copy. Good. It was shorter than the README's "one screen" and that was fine.
- Holiday caveat added with dates and no overclaiming. Good.
- "Nine findings are supported": I asked five questions, so the jump to nine findings is a little confusing (presumably several per question). It wasn't explained.
- Next: package, answering datasets = none and methods note = yes up front.

## Turn 6 — headline preview
- Got: 8 main headlines plus 4 appendix headlines, and a methods-note plan. Preview-and-wait was honored. Good.
- Friction: it linked and quoted the awb-package SKILL.md again. That's not for me and I didn't open it; it's the second time this has happened.
- Also unclear: the numbered list includes the title as slide 1, yet the agent said "the deck opens with the title, then the answer slide". Took a second to map.
- My edits: the tip headline overstates a 0.6-point change for a lay board, so round it to "about a quarter"; the exclusions headline omits the vendor difference (the interesting part of Q4); the zone ranking headline should tie to the airport decision (airport zones dominate); slides 4 and 8 repeat the TLC point; and I want fare numbers in the airport headline.
- I agreed to put How we know and Limitations in the appendix. The agent didn't explicitly ask me, but the README says it needs my agreement, so I gave it.

## Turn 7 — full draft review
- Got: findings.md (8 main + 4 appendix), methodology-note.md (~400 words), START-HERE.md, and 6 chart files. All my headline edits were applied faithfully. Review rules were saved (I didn't ask for that, but OK).
- Links in chat were relative paths this time (earlier they were absolute). Minor inconsistency.
- START-HERE is clear. Surprise: it tells me to attach methodology.md (internal) to Copilot but not send it to the board. That's fine and the README explained it.
- My review issues:
  - The tipping slide dropped the hour and borough variation (it's only in speaker notes). Q3 explicitly asked for that, so it needs a bullet.
  - Some bullets are awkward or jargon-y for the board: "other located trips", "One provider and unspecified-fare group records almost all card tips as zero", "with zero-record tolerance" (in the methods note), "occupied hour".
  - Zone chart uses two-decimal dollar labels ($106.28). Too precise for the board; use whole dollars.
  - The exclusions headline with arrows reads like a spreadsheet.
- Overall: draft quality is high. Mostly wording.

## Turn 8 — revisions
- All six corrections were applied and the changed slides shown inline in chat, so I didn't have to reopen files. Very convenient.
- It sensibly used ranges (27–28%, 26–27%) instead of my single numbers, to cover both months. Good judgment.
- It saved two more review rules (R-question-coverage-001, R-zone-display-001) without asking. Not harmful, but I'm unsure I agreed that these are general rules rather than one-off edits.
- Commit hashes keep appearing in chat; they're noise to me.
- Next: release.

## Turn 9 — release
- Release 001 frozen and copied. I checked the releases folder myself and all files are there (findings, methods note, 6 charts, START-HERE, deck rules, assembly, methodology, manifest).
- No release questions were asked: there was no DRAFT label and no warnings, so nothing to ask. Smooth.
- The report repeated all the open caveats. That was useful as a final checklist.

## Summary
- 9 exchanges from first message to release, plus this closing one. That matches the README's 6–11 estimate.
- Went well: concrete numbers every turn, the code-99 tipping catch, exclusions counted by vendor, my edits applied faithfully, the changed slides shown inline, and storage handled without extra questions because I named the folders up front.
- Friction: agent instruction files (SKILL.md) were linked and quoted to me twice; jargon in the reports (canonical views, Q-numbers, run.py, deadheading, tolerance); commit hashes and review-rule IDs in chat; review rules saved without asking whether each correction was general; "nine findings" vs my five questions wasn't explained; the cleaning step counted Q4 as answered without saying so explicitly.
