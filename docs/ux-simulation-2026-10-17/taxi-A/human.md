# Feedback: Dana Ortiz (taxi-A), first-time workbench user

## 1. Did I get what I needed?

Yes. All five questions have specific, board-usable answers with caveats. Release 001 is in my releases folder, and the methodology note is 521 words, which fits the one page I asked for. It took 9 exchanges plus a closing message.

**Satisfaction: 8/10.** Would I use it again? Yes. The rigor shows: thresholds were held for my signoff, exclusions were reconciled, and it caught things I didn't know. What keeps it from a 9–10 is the agent showing me its own internals, a few dense files, and a Q5 ranking I couldn't use on the first pass.

## 2. Top pain points, ranked

1. **The first Q5 ranking was led by zones with 1–13 trips (Rikers Island on 1 trip).** Turn 5. Severity: **major**. It cost a full extra round, and I had to ask for a minimum myself. The agent flagged the tiny samples but didn't propose a fix. The README says thresholds are "proposed before the agent sees which rows lead", but this one only came after the leaders were shown. What would have helped: propose a minimum-sample rule for any ranking question during the threshold signoff in turn 4, alongside the other cutoffs.
2. **The first tipping answer led with "0%" for Bronx and Brooklyn.** Turn 5. The explanation was "rate-code 99" with no definition. Severity: **major**. I couldn't have put it in front of the board. One follow-up fixed it: code 99 means Null/unknown, and the standard-rate population became the basis. What would have helped: define any code the first time it's cited, and offer the cleaner population up front.
3. **The agent quoted or linked its own SKILL.md files to justify itself.** This happened in turns 2 and 9 ("The awb-scope instructions require…"). Severity: **minor**, but it was jarring. I don't need to see the agent's rulebook, and it read as defensive. What would have helped: just say "I'll wait for your OK before releasing."
4. **awb-status came back as prose paragraphs.** Turn 9. The README promised "one screen: each of your questions with its findings… and up to five requests you can type next." Severity: **minor**. It also said "nine supported findings and two provisional reference calculations", and I couldn't map 11 results onto my 5 questions. What would have helped: a per-question table and the suggested next requests.
5. **Previews were saved in a hidden `.preview` folder.** Turns 7 and 9. Severity: **minor**. Finder doesn't show it. The headlines were also in chat, so I didn't need the file.
6. **The quality-proposal file was full of jargon:** column names (`fare_amount`), "Q-011", "publication.json", "canonical view", file paths. Turn 4. Severity: **minor**. The chat summary was clean; the file reads like an internal log.
7. **"Landed" vs. "brought in" was confusing.** Setup copied my files to storage, but the README says setup brings no data in. I had to ask whether the data was "in". Turn 3. Severity: **minor**. The agent answered clearly once I asked.

## 3. The README

- **Missing:** the difference between "landed" (copied), "published" (queryable), and "cleaned/screened". I needed to know which state the data was in.
- **Unclear:** "investigation" vs. "project". I didn't know an investigation was a separate thing to create until the agent said it was pending.
- **Wrong, or not honored:** the awb-status "one screen" description doesn't match what I got. The promise that thresholds come before seeing leaders wasn't kept for the ranking minimum.
- **Too dense:** "What you will be asked", especially items 6–8 (review rules, flagged findings, draft-then-review vs. preview-and-wait). That's a lot to absorb on day one. A shorter "what to expect, in order" list would help, with details linked below.
- **Good:** the example first message. Copying its shape meant very few scoping questions. The "How many exchanges to expect" section set realistic expectations, and my run fell inside its range.
- **Would have liked:** a note that findings.md is long and builder-oriented, and roughly what the finished slide will look like, so I know what I'm reviewing.

## 4. The agent's communication

- **Scoping interview:** excellent. There were only two questions, both plain and each with a recommendation. It looked up the facts it could (it fetched the data dictionary I couldn't download) rather than asking me.
- **Questions overall:** well judged. The threshold proposal was a clear table with rationale and alternatives, and it waited for my signoff.
- **Message length:** some turns were long (turns 5 and 6), but they were structured with tables, and the closing line ("Your five questions: … · next: …") was very useful.
- **Jargon:** "provisional", "investigation pending", "supported findings / reference calculations", "eligible view", "publication". Plus the SKILL.md quotes. Chat was mostly plain; the files less so.
- **One self-contradiction:** in turn 6 it said it would propose the 300-trip minimum and wait, then applied it in the same message. I had said "rerun", so the outcome was fine, but the message was confusing.

## 5. Trust

- **Trusted:** Q1 volume, especially after the July 4 check. Q2 airport share, fares, and durations, with the sensitivity check on high-value records. Q4 exclusions: they reconcile by month and vendor, and the counts are given. The final Q3 and Q5 answers: the standard-rate tip medians were independently re-verified when I spotted a suspicious match, and the 300-trip ranking shows trip counts.
- **Didn't trust at first:** the first-pass Q3 (0% medians, undefined code) and Q5 (tiny-sample leaders). Neither was board-safe until I pushed.
- **Mild unease:** the standard-rate median exactly matching the earlier Manhattan figure. The agent explained it (tips bunch at preset percentages) and confirmed it with independent calculations, so I accepted it. I'd prefer the agent catch that kind of coincidence itself.
- **Big trust boosters:** the Newark caveat (yellow cabs can't pick up there) and the note that the dictionary postdates the 2024 files. The agent knew things I didn't and said so.

## 6. Package review and release

- The headline preview was clear, and the agent made my four changes, including verifying the "all Queens" claim before using it. The reviewer caught real gaps (fare spread, occupied hours) and the agent fixed them without bothering me.
- **But** the reviewer also pushed an internal QA bullet onto the tipping slide ("independent checks confirm… different populations"). The board would never understand it, so I had to ask for it to be removed.
- 24-hour times (18:00) were a poor fit for a non-technical board. They became a saved rule after I asked. 12-hour times should be the default for lay audiences.
- findings.md is long and hard to picture as slides. START-HERE.md is excellent: short, and clear about what to send to whom.
- **Release:** smooth. The changed slides were shown before release, the full path was given, the caveats were listed, and the copy was verified in my folder.

## 7. Wasted turns or time

- Turn 6 existed mainly to fix Q5 sample size and the Q3 code-99 framing. Both could have been anticipated in turn 4 or 5.
- Turn 3 was partly spent asking whether the data was "in".
- One cleanup request in turn 9 (the QA bullet) came from the reviewer, not from me.
- Everything else was productive.

## 8. What worked well

- A short scoping round, with recommendations on every question.
- The agent fetched documentation itself and was careful about which facts were verified and which I only remembered.
- Thresholds were proposed with rationale and held for signoff. Exclusions were counted and reported, never silently dropped, which is exactly what I asked for.
- It caught real-world context I lacked: the Newark pickup restriction, code 99 = unknown, July 4 on a Thursday (confirmed once I raised it).
- The sensitivity checks on the 127 high-value records were done without fuss.
- Honest, well-placed caveats; it was careful not to make the board's decisions for it.
- The one-line status at the end of each turn.
- The release was copied and verified, and the full path was reported.
