# Feedback from Dana Ortiz (taxi-A simulation)

## 1. Did I get what I needed?

Yes. All five questions got specific answers I would put in front of the board. I got a status check, a headline preview, a full draft that I reviewed and corrected, and release 001 copied to my releases folder. It took 9 exchanges from my first message to the release, plus a closing message.

**Satisfaction: 9/10.** I would use this again. The analysis was more careful than I would have managed myself. It caught that the zero-tip pattern sits in one provider's "fare code 99" records, which changes what the board can say about tipping. The point I took off is for internal process and jargon leaking into the chat.

## 2. Top pain points, ranked

1. **Agent instruction files linked and quoted to me (minor-to-major).** This happened in the scoping turn (awb-init SKILL.md, quoted twice) and again at the headline preview (awb-package SKILL.md). It reads as the agent justifying itself to its own rulebook. A non-technical user might think they're supposed to open those files. *Would have helped:* never link or quote skill files to the user. Just state the next step.
2. **Jargon in reports I was pointed to (minor).** Examples: cleaning-report.md ("canonical views", "primary_eligible", "Q-008", "strict⊆primary⊆relaxed", links to .sql files), analysis-report.md ("deadheading", "run.py", "single-thread analytical session"), and the methods note ("with zero-record tolerance", which I had to ask to remove). *Would have helped:* write the user-facing reports in plain terms and move the internals to a separate file.
3. **Review rules saved without asking (minor).** After both draft reviews the agent saved review rules (R-tipping-001, R-question-coverage-001, and others). The README says one-off edits shouldn't become rules. I was never asked whether my corrections were general or one-off. *Would have helped:* one line asking "Keep this as a rule for future drafts?"
4. **Unexplained counts and status (minor).** After cleaning, the footer said "1 answered" without naming which question. I had to ask, and it was Q4. Status said "nine findings" when I had asked five questions. *Would have helped:* always name the question number, and explain how findings map to questions.
5. **Commit hashes and rule IDs in chat (minor).** Noise for a non-programmer.
6. **The ranking support floor was flagged but not asked (minor).** The agent noticed that top zones had only one trip each but didn't propose a minimum or ask me for one. I had to raise the 1,000-trip floor myself. *Would have helped:* a recommended floor offered as a scoping question.

## 3. The README

- The quick-start was good. "What to say first" gave me a template, and putting everything in my first message (questions, audience, storage folders, preview mode) clearly saved turns.
- Too much of it isn't for me. "How it works", "Install and administer", MCP, and receipts are heavy, and they're mixed into the same document as the analyst guide. A separate analyst-only page would help.
- It didn't tell me what "commit" means for me, or whether I should care. The agent recommended committing, and I only knew to say "commit as you go" because the README happened to mention the phrase.
- It doesn't say that the agent may fetch documentation from the web itself. The agent read the TLC dictionary that I couldn't download, which was great, but I didn't know that was possible.
- It doesn't explain that findings ≠ questions (one question can produce several findings).
- It says the agent asks before moving slides to the appendix. In practice the agent proposed an appendix and I volunteered my agreement, and the moment to agree wasn't clearly signposted.

## 4. Agent communication

- The scoping interview was excellent: four concrete questions, each with a recommendation and an alternative, and the definitions written out so I could accept or change them. It didn't ask about things the data could settle.
- Messages were long. The first reply repeated the four questions twice, and progress narration ("I'm finishing…") preceded each final summary. The final summaries themselves were clear.
- The footer line ("Your five questions: … · next: …") was very helpful.
- In most turns, the numbers in chat were enough to judge the results without opening files.

## 5. Trust

- **Trusted:** exclusion counts, which reconciled exactly to input records and were broken down by vendor; the airport shares and fares, with an upper bound for unknown locations; the tipping medians, with the sensitivity check and the code-99 diagnostic; and the zone ranking after the floor, because it was stable under the alternative cutoffs and tested against single large fares.
- **Trusted with caution:** the weekday changes (Tuesday +16%, Saturday −10%). They're large and unexplained. The agent added a holiday caveat when I asked but didn't analyze it, which I accept for the board.
- **Not settled by the data, and labeled as such:** what the code-99 zero tips mean, and Vendor 6's identity in 2024. Both were handled honestly as TLC questions.

## 6. Deck package review and release

- Preview-and-wait was honored. The headline preview made it easy to redirect the emphasis (airport money in the headline, not overstating a 0.6-point tip change, tying the zone ranking to the airport decision).
- The full draft applied every change faithfully. The second round of corrections was shown inline as changed slides, which was great. The agent also used good judgment on ranges (27–28%) instead of my single-month numbers.
- One gap in the first draft: the hour and borough tip variation (explicitly part of Q3) was only in the speaker notes. I had to catch it. The package check apparently doesn't verify that every part of a question appears on a slide.
- START-HERE.md was clear about what to send and what to keep.
- The release was smooth: no unnecessary questions, the exact path was given, the copy was verified, and the closing list of caveats was handy.

## 7. Wasted turns or time

Very little. The one turn spent on "which question is answered / what is Vendor 6 / zone floor" could have been avoided if the cleaning turn had named Q4 and proposed a floor. One draft revision round was needed for wording and Q3 coverage, which is reasonable.

## 8. What worked well

- Naming the storage folders up front meant no storage questions later. The originals were preserved and verified in the first turn.
- I asked for broken records to be counted rather than silently dropped. That was done thoroughly, by month, vendor, and reason, with overlaps.
- The agent found the cash-tip answer in the TLC dictionary itself.
- The code-99 discovery protected the Lab from taking a tipping position on misleading data.
- The status report was short and gave me the exact next request to type.
- Release 001 landed in my shared folder with everything needed to build the deck.
