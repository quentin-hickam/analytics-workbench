# User feedback: Sam Whitfield (co2-A)

## 1. Did I get what I needed?

Yes. All five questions got specific, sourced answers with the year each one used. I asked for status once, reviewed a draft, asked for corrections, and release 001 ended up in my releases folder. It took 9 message turns from setup to delivery, and none of them were wasted loops.

- **Satisfaction: 8/10.** The analysis was careful and honest. I lost points because internal bookkeeping kept leaking into the conversation, the methodology note I got first was written for internal use, and there is no actual deck file.
- **Would I use it again?** Yes, for a data-driven brief like this. Next time I would ask for the donor-readable methodology note up front and expect to build the slides myself.

## 2. Top pain points, ranked

1. **The default methodology note was internal, not something I could give donors.** (Major) This was turn 7, my first package review. The draft was full of result IDs (r-010), file names (settings.toml, run.py), parameter names (`baseline_year=2000`), evidence JSON links and the same "Recorded question" line repeated several times. I had asked for a methodology note for donors. I had to ask again for a donor version, and once I did it was excellent. *What would have helped:* when the audience is external, produce the audience-facing note by default and keep the internal record as a backing file. At minimum, ask which one I want.
2. **No deck file at the end.** (Major) This was at release. The "deck package" is a markdown outline, chart CSVs and assembly guides. I still have to build 8 slides by hand, because I may not have a Microsoft 365 Copilot licence. *What would have helped:* the README saying plainly that the package is an outline plus data, not slides. Better still, a basic .pptx or a rendered preview, so I could check the storyline visually and not by reading a long markdown file.
3. **Internal bookkeeping in the conversation.** (Minor to major) This ran across turns 1, 4, 6 and 7. Two separate "Q-" numbering systems appeared: question-ledger Q-003/Q-004 and quality records Q-001–Q-013. "17 questions answered, 10 findings" came up when I had asked 5, and I needed a whole turn to find out what they were. r-IDs appeared in drafts. *What would have helped:* talk in terms of my five questions. Keep the ledger counts behind the scenes, or explain them in one clause when they first appear.
4. **The agent linked me to its own skill instruction file** (awb-package SKILL.md) and quoted its rules as the reason for a checkpoint. (Minor) This was turn 7. I did not open it. It reads as process leaking into the conversation. *What would have helped:* just "I'd like your OK on the headlines before I write the full slides."
5. **Environment errors reported with no indication of impact.** (Minor) In turn 1 I was told "Git initialization was denied" and "connector writes were blocked". I had no idea whether I needed to act and had to ask. The answer was no. *What would have helped:* say "no action needed" in the same sentence.
6. **Links were inconsistent.** (Minor) Some were absolute paths and some relative (`deliveries/...`). I had to work out where the relative ones pointed. The release path also nests deeply (`releases/emissions-accounting-shifts/donor-roundtable/released/001/`, with "released" sitting inside "releases").
7. **No guide in the release to what goes to donors.** (Minor) The release mixes donor files with internal ones (deck-rules, manifest, m365.md, internal methodology), and I had to ask which to send. A short "send these" note in the release would fix it.
8. **A small wording change made silently.** (Minor) At release, the agent reworded my slide-8 headline. The new wording was better, but it didn't tell me.

## 3. The README

- **Too much of it is for installers and IT,** not users: symlinks, MCP registration, VS Code Session Targets and allowlists. The part I needed ("Use") is about a quarter of the page.
- **Jargon with no explanation:** Parquet, DuckDB views, canonical views, saved queries, question ledger, "disposition for each flagged finding", the M365 assembly file, `R-<area>-NNN` rules.
- **Unclear what the package actually is.** It describes an outline that Microsoft 365 Copilot's PowerPoint agent turns into a deck. It doesn't say whether M365 Copilot is required, or that without it you build the slides yourself. The agent confirmed that manual assembly works, but the README never says so.
- **It doesn't say the default methodology output is internal.** "An internal methodology reference" is mentioned, but nothing says how to get an audience-facing note.
- **The workflow it describes differs from what happened.** It reads as init → scope interview → clean → explore → package. In practice there was no real scoping interview, and no separate explore step: the agent went from cleaning straight to answers. That was fine, but I couldn't tell whether something had been skipped.
- **Useful parts:** the example request phrasings, the warning that I'd be asked for storage locations (so I gave them up front), and the awb-status phrasing.
- **What I needed and didn't get:** how long a typical run takes, what I'll actually receive at the end, and which files are for my audience.

## 4. The agent's communication

- **Length:** usually right. Summaries were short with bold key facts. Tables made the answers and the cleaning decisions easy to scan.
- **Jargon:** mostly plain in chat. The drafts and status reports were heavier (IDs, "supported findings", "superseded", "recorded results"). Speaker notes repeat "does not establish policy causality" on almost every slide.
- **Questions to me:** good when it asked. The cleaning decisions came as three items in a table, each with a recommended option and an alternative, which is ideal. The coal-measure sensitivity was framed well with a recommendation, and the headline checkpoint was reasonable.
- **Scoping interview:** there wasn't really one. Init recorded my question and listed open items (eligibility, measures, selection criteria, endpoint) in a ledger, then waited for my five questions. Because I volunteered definitions up front, it didn't matter much. A user who gave less up front might have missed the interview the README promises.
- **Pushback:** when it disagreed with me (slide 8 overgeneralizing "wealthy countries"), it said so plainly and gave the reason. I appreciated that.

## 5. Which answers I trusted, and why

- **Trusted all five, after review.** Q4's cumulative shares (US ~24%, EU-27 ~16%, China ~15%) match what I know from OWID's own charts. Q3's direction (consumption accounting raises the US and EU, lowers China and India) matches the literature. Q1's top increases and decreases are plausible.
- Trust went up because:
  - It checked my ISO-code assumption rather than following it, and found Kosovo would be dropped.
  - It corrected its own earlier "2024" claim for consumption data to 2023, without being asked.
  - It disclosed China's and India's early gaps instead of filling them with zeros.
  - It answered "is a top-20 emitter missing GDP?" with a specific number (Sudan, rank 95).
  - It was honest that OWID's documentation doesn't specify the USSR allocation weights.
- **Less sure at first:** Q5. The agent chose the coal metric (percentage points) without asking me, although it did state the choice. The sensitivity check showed the ranking changes a lot depending on the metric. I'm comfortable now that both views are disclosed.
- The "68.7% of combined increases" figure on slide 2 is correct, but the denominator is awkward for donors. It is footnoted.

## 6. Deck package review and release

- **Headline checkpoint:** useful. It let me fix headlines that named one country on slides showing ten.
- **Full outline:** thorough, with chart specs, alt text, footnotes and speaker notes. But reviewing a long markdown file is not the same as seeing slides, and I couldn't judge the visual storyline.
- **Donor methodology note:** two readable pages, the right content. The best single item in the package.
- **Chart CSVs:** the first version had floating-point noise (0.42541799999999996) and a label that didn't match the slides ("European Union (27)" vs "EU-27"). Both were fixed in one round.
- **Release:** smooth. No extra questions, because I had given the storage path at the start. It verified both the local copy and the copy in my folder. I checked, and the corrections were all in.

## 7. Wasted turns or time

- One turn went on asking what "17 questions / 10 findings" meant.
- One turn went on getting a donor methodology note after receiving the internal one, although I bundled it with the headline review, so it cost little.
- Half a turn went on asking whether the git and connector errors mattered.
- Nothing looped, and the agent never asked me the same thing twice.

## 8. What worked well

- Fast, clean data landing, pinned to a specific OWID commit, with checksums and a copy in my storage folder.
- Cleaning that verified my assumptions and turned up a real issue (Kosovo, Antarctica).
- Specific, quantitative answers that state the year each one used, with ready-to-use slide footnotes.
- Candid self-correction and honest limits on what the documentation supports.
- Decisions offered as a recommendation plus an alternative.
- awb-status was short and plain, and gave me the exact phrase for the next request.
- A one-shot "fix these three things and release" worked first time.
