# User feedback: Dana Ortiz (taxi-A)

## 1. Outcome

- **Did I get what I needed?** Yes. All five questions have specific, quantitative answers with caveats I'd put in front of the board. I have an 8-slide deck as a PDF and an editable .pptx, plus a one-page methodology note. All of it was released as 001 to our shared drive.
- **Satisfaction:** 8/10.
- **Would I use it again?** Yes. The analysis quality was well above what I'd have produced alone in two weeks. The agent caught two data problems that would have embarrassed us: CMT's zero tips in Brooklyn and the Bronx, and Flushing Meadows records coded at the JFK rate. I lost points to a jargon-heavy README, tooling chatter, and a few expectations the README set that didn't happen.
- Session length: 11 turns from init to release. That's reasonable.

## 2. Top pain points (ranked)

1. **The README is written for the installer, not for me (major).** When: before my first message. About 80% of it is MCP config, VS Code targets, AGENTS.md vs CLAUDE.md, and symlinks. Words like "canonical views", "foundation level", "flagged finding disposition", "M365 assembly file" and "R-<area>-NNN" mean nothing to a policy analyst. *What would have helped:* a separate one-page "For analysts" section. It should cover what to say, what you'll be asked (storage locations, audience, deadline), what you get at the end, and the 6 typical requests in order.
2. **The agent pointed me at its own instruction file (major).** When: turn 9, at the first package checkpoint. It linked the awb-package SKILL.md to explain why it needed headline approval and a datasets choice. I shouldn't have to read tool internals to understand a question. *What would have helped:* "Before I build the slides, approve these 8 headlines" was enough on its own.
3. **Tooling status reached me with no "do I need to act?" (minor to major).** When: turn 1 ("Git creation was blocked… MCP reads work; writes require the CLI fallback"), status in turn 7 (Git again), and release in turn 11 ("provenance gaps: … two geography-validation metadata entries"). Each one made me wonder whether something was broken. The agent only clarified in turn 2 because I asked. *What would have helped:* leave it out, or say in one line "no action needed; doesn't affect results."
4. **The "datasets" choice had no explanation and no recommendation (minor).** When: turn 9. "No separate datasets or summarized comparison tables". I didn't know what either would contain or who they're for. *What would have helped:* one sentence on what each option is, plus the agent's recommendation.
5. **The pending question was announced but not asked (minor).** When: turn 1. "Opened 12 (1 needs your context)", without saying which one. That cost me a turn. *What would have helped:* ask the question inline.
6. **The holiday effect was only checked because I raised it (minor, but a trust issue).** When: turn 4. The weekday table showed Thursday −3.9% and Saturday −10.3% with no mention of New Year's Day, MLK Day or July 4. Setting the holidays aside flipped Thursday to +9.1%. If I hadn't spotted it, the board would have seen a misleading slide. *What would have helped:* calendar effects checked by default for any weekday comparison.
7. **The package review passed, but readability problems remained (minor).** When: turn 10. The "independent review and final package checks passed" draft still had a tipping bullet on the airport slide and an asterisk on every data label. It also had fares without $ signs, an unlabeled holiday-adjusted chart, and the Maspeth vs Elmhurst/Maspeth confusion. The checks seem to test rules, not whether a board member can read the slide.
8. **The release folder is cluttered (minor).** When: turn 11. The release sits 5 folders deep on the shared drive, with about 20 files: artifact-checks.json, serialization-checks.json, review-state.json, build-report.json and so on. They surround the 3 files a colleague actually wants. *What would have helped:* put the deliverables at the top and the audit files in a subfolder.
9. **A third vendor appeared without warning (minor).** When: turn 9. "Myle" (260 records, 36% flagged) first showed up in the methodology PDF, though the chat vendor table had shown only vendors 1 and 2.

## 3. The README

- **Missing:** what the user experience looks like end to end. That means how many back-and-forths to expect, what decisions I'll be asked to make, and what the final deliverable files are.
- **Wrong or misleading expectations:**
  - It says awb-init "hands the question to awb-scope, which interviews you." No real interview happened: I got one question about decision thresholds, asked indirectly.
  - It describes the deliverable as an outline plus chart data for the Microsoft 365 PowerPoint agent to build. I actually got a finished .pptx and PDF, which was better, but the README made me expect to build the deck myself in M365.
  - It says release happens "once you have chosen a disposition for each flagged finding." I was never asked, and I still don't know what a "flagged finding" is in this sense.
- **Unclear:** the difference between "findings", "questions", "quality rows" and "catalog cells". Who the "reviewer subagent" is and whether I need to install it. What `awb-brainstorm` would have given me.
- **Helpful:** it warned that the agent would ask where landed data and releases go, so I had those paths ready. The example phrasings ("Use awb-status — where are we?") worked.

## 4. Agent communication

- **Length:** mostly right. Messages were tables plus a few bullets, and dense but scannable. A couple of turns combined two answers (holidays plus airports, Curb plus card share plus zones), which was efficient.
- **Jargon:** "retained", "screening rules", "occupied hours", "ratio of sums" and "date exposure" were fine for me. Not fine: "MCP", "CLI fallback", "provenance gaps", "geography-validation metadata entries", "canonical", and internal IDs like "Q-017" in files it pointed me to.
- **Quality of questions:** few questions, but the ones asked were good. Examples: what would persuade the board, and the threshold for zone rankings, which it framed as a sensitivity rather than forcing a choice. It should have asked me directly to choose the Q5 threshold instead of leaving the choice implicit.
- **Scoping interview:** effectively absent. It took my first message and ran. That worked because my brief was detailed. A vaguer user would have needed the interview the README promised.
- **Links:** sometimes relative paths, sometimes absolute. That's inconsistent, and the relative ones made me hunt for the project folder.

## 5. Trust

- **Trusted:** volume and airport numbers, with internal consistency checks (per-day totals reconcile with month totals and day counts). The rule-by-rule flag table had counts and an overlap note. The Curb-only tipping figures came with sample sizes. The Flushing sanity check showed robustness tests (removing the top 10 trips, removing trips under 5 minutes). Sources were cited (TLC dictionary, OPM holidays, Curb history).
- **Trusted after a follow-up:** the weekday comparison, once holidays were handled. Tipping by borough, after the agent itself flagged that all-vendor medians of 0% were a CMT artifact. That self-flagging raised my trust a lot.
- **Less sure:** the zone ranking. The agent was honest that there's no threshold-independent answer, and the leader depends on my 100-trip choice. I'd caveat it heavily or demote it in the deck. Payment code 0 doubling (4% to 9%) is also unexplained, so I wouldn't say anything about cash vs card trends.

## 6. Deck package review and release

- **Headline-first checkpoint:** useful. Reviewing 8 headlines before slide bodies let me fix vague headlines cheaply.
- **First full draft:** good structure and decision framing, and my edits were applied faithfully. It needed one round of readability fixes (listed in pain point 7). All five corrections came back correct in one pass, and the agent saved "no per-value asterisks" as a rule for future drafts.
- **Methodology note:** excellent. Truly one page, and complete enough for a skeptical board member.
- **Release:** one request, no questions, copied and verified to the shared drive. The only issues were folder clutter and the unexplained "provenance gaps" line.

## 7. Wasted turns and time

- Turn 2 existed only to learn which question needed me and whether the tooling messages mattered. Both could have been in turn 1.
- Turn 4 (holidays) and turn 10 (readability fixes) were needed, but default checks could have avoided them.
- Otherwise the pacing was efficient. The agent proactively ran the next question when I hadn't explicitly asked.

## 8. What worked well

- Concrete, quantitative answers every turn, with counts as well as percentages, and definitions stated (revenue = fare only; tip % = tip/fare median including zeros).
- My requirement to exclude bad records but count and report them was honored and visible everywhere.
- The agent caught data problems unprompted: CMT zero tips, Flushing JFK-rate coding, payment code 0 growth, and Staten Island's tiny sample. It also refused to overclaim, for example "no switch-to-cash claim is supported."
- Sensitivity checks came by default: strict and lenient screens, and zone thresholds.
- Original data was landed to my shared drive with checksums, and the release was copied there automatically.
- awb-status was short, readable, and told me the next request to make.
- I got a real editable .pptx.
