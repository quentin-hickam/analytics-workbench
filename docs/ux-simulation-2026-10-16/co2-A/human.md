# Feedback: Sam Whitfield, research lead (co2-A)

## 1. Did I get what I needed?

Yes. All five questions have specific, checked answers that I would put in front of donors. I got an 8-slide outline with two appendix slides, six chart data files, and a methodology note that donors can read. Release 001 is frozen and copied to my releases folder. It took 5 exchanges from the first message to the release, plus a closing message.

**Satisfaction: 8/10.** Yes, I would use this again, especially for a recurring donor brief where the frozen releases and the question ledger pay off.

## 2. Pain points, ranked

1. **"All five answered" came before the answers were shown** (turn 3, major). The chat said every question was answered, but it gave only the #1 country for Q1 and Q5. The top-10 lists for Q1 weren't even in the preview file, and the Q2 and Q3 numbers were only in a file I had to open. I had to spend a whole turn asking for the tables. *Would have helped:* when an answer is a ranking or list, show the full table in chat the first time it's reported as answered.
2. **The Answer headline was weakened without asking** (turn 4/5, minor-to-major). I had approved a two-clause Answer headline (growth in China, India and Indonesia; cuts with growth in the US, Japan and Germany). The draft dropped the second clause. Later I learned this was because of a "template word limit" I had never heard of. It took a correction turn. *Would have helped:* when an approved headline breaks a rule, say so at the checkpoint and ask, rather than silently trimming it.
3. **Review rules were created without telling me** (turns 3 and 5, minor). My headline preferences became "R-headlines-001" and my definition request became "R-metric-definitions-001". It's probably the right behaviour, but I only found out after the fact, and it isn't clear what I've committed future drafts to. *Would have helped:* one line such as "I'll treat this as a standing rule for future drafts. OK?"
4. **Skill internals leaked into chat** (turn 2, minor). The scoping message linked to a SKILL.md and quoted its rule text. Later messages mentioned "template word limit", finding counts ("11 findings", "two required supporting questions") and record IDs (Q-001, territorial-change). None of that was for me.
5. **The status report's next step was ambiguous** (turn 5, minor). It said "assemble PowerPoint, then mark delivered". The README presents the package as the deliverable, so I wasn't sure whether I was supposed to build the deck before releasing. I released anyway, and that was fine.
6. **"Ready for an initial commit"** (turn 2, minor). It wasn't clear whether that was a request for me to act.

## 3. The README

- **Good:** the quick-start, the example first message, the "What you will be asked" list and the glossary. Giving everything up front in the first message really did cut the number of questions.
- **Unclear:** whether data at a web address is fetched during setup or needs a separate "bring in" request. It was fetched automatically, which was great, but I didn't know that in advance.
- **Unclear:** preview-and-wait vs draft-then-review took two reads.
- **Missing:** that headlines have a word limit, and that my corrections may turn into standing review rules automatically. The glossary describes review rules but not that they get created without asking.
- **Missing:** whether to build the PowerPoint before or after releasing.
- **Too much for me:** "How it works" and the install sections (Parquet, DuckDB, receipts, MCP). These should be clearly fenced off as admin-only. Mostly they are, but "How it works" sits in the middle.
- START-HERE listed methodology.md as both "attach to the builder" and "internal". The README's explanation of this is easy to miss. The agent fixed the wording when I asked.

## 4. Agent communication

- **Scoping interview:** good. There were four focused questions, each with a recommendation. It flagged the cumulative-since-1850 subtlety unprompted. It didn't ask what "countries" meant, so I volunteered it, and the agent then checked my ISO assumption and found Kosovo. That was excellent.
- **Jargon:** the analysis language was mostly plain. The workbench internals (rule IDs, record names, skill quotes) were the jargon.
- **Length:** the replies were long, especially turn 3. That was justified by what I asked for, but the progress narration ("I'm checking…", "I'm fixing the remaining mechanical issues…") could be cut. I only need the result.

## 5. Trust

- **Trusted:** the Q1 rankings (2000 and 2024 values shown, plausible magnitudes) and Q2 (strict endpoint rule stated, Australia's −0.3% flagged). I also trusted Q3, because the matched-year numbers are consistent with what I know, and Q5, because both points and points/year are shown and the China counterexample was kept.
- **Q4 trusted after follow-up:** the first answer only said "label as recorded". After I asked, it checked GCP's documentation on how World is built and ran a transparent sensitivity test (China +0.05 points), honestly labelled "not an upper bound". That made me confident.
- **The EU-27 check** against the member sum and the Ukraine before/after-2022 split both increased my trust.
- I did not independently verify the numbers against OWID's browser charts. The README's warning that checks don't redo the analysis is fair.

## 6. Package review and release

- The outline was well structured, with caveats on the slides they qualify, and the chart CSVs were clean and labelled. The methods note is something I can send donors as-is.
- Corrections were applied precisely in one turn, and I verified them in the file.
- The release was one exchange. It was copied to my folder and the report listed its caveats. A minor issue: headline-preview.md travels in the release folder, but START-HERE doesn't mention it.

## 7. Wasted turns and time

- One turn (turn 3) went on getting the full answers that the "answered" claim implied I already had.
- About half a turn went on restoring the headline wording I had already approved.
- Otherwise it was efficient: setup, scoping, landing, analysis and the headline preview all happened in about two turns.

## 8. What worked well

- A fast path from an empty folder to a frozen release.
- Careful data handling: Kosovo's missing ISO code, EU-27 reconciliation, the pinned dataset version, matched comparison years stated per question.
- Honest caveats: Ukraine war timing, Australia's tiny decline, coal share vs absolute coal, historical gaps.
- The headline checkpoint (preview-and-wait) worked as the README described.
- The storage folders were used exactly as I specified, and the copies were verified.
